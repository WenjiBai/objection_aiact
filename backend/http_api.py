"""Tiny HTTP adapter for the React frontend.

Run from the project root:

    python -m backend.http_api

The core backend contract remains `backend.api.run_courtroom` /
`backend.api.handle_chat`; this module only translates browser JSON requests
into `CaseFile` objects and serializes the result back to JSON.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import json
import mimetypes
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urlparse

from backend.api import BackendValidationError, handle_chat, run_courtroom
from shared.document_parser import extract_text
from shared.pdf_export import case_pdf_filename, case_to_pdf_bytes
from shared.schema import CaseFile, CaseStatus, Document

HOST = "127.0.0.1"
PORT = 8787
MAX_BODY_BYTES = 25 * 1024 * 1024
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


@dataclass
class BrowserUpload:
    name: str
    type: str
    data: bytes

    def getvalue(self) -> bytes:
        return self.data


def _json_case(case: CaseFile) -> dict[str, Any]:
    return case.model_dump(mode="json")


def _normalize_case_payload(raw: Any) -> dict[str, Any]:
    """Accept older React demo CaseFile snapshots at the HTTP boundary."""
    if not isinstance(raw, dict):
        raise ValueError("case_file is required.")

    payload = deepcopy(raw)

    for ref in payload.get("refs") or []:
        if isinstance(ref, dict) and not ref.get("full_text"):
            ref["full_text"] = ref.get("snippet") or ref.get("title") or ""

    verdict = payload.get("verdict")
    if isinstance(verdict, dict):
        label = verdict.get("confidence_label")
        if isinstance(label, str):
            normalized = {
                "low": "Low",
                "medium": "Medium",
                "high": "High",
            }.get(label.strip().lower())
            if normalized:
                verdict["confidence_label"] = normalized

    return payload


def _case_from_payload(payload: dict[str, Any]) -> CaseFile:
    return CaseFile.model_validate(_normalize_case_payload(payload.get("case_file")))


def _build_new_case(payload: dict[str, Any]) -> tuple[CaseFile, list[str]]:
    docs: list[Document] = []
    warnings: list[str] = []

    for i, item in enumerate(payload.get("files") or [], start=1):
        name = str(item.get("name") or f"upload_{i}.txt")
        mime = str(item.get("type") or "text/plain")
        encoded = str(item.get("data_base64") or "")
        try:
            data = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise ValueError(f"Could not decode {name}: {exc}") from exc

        upload = BrowserUpload(name=name, type=mime, data=data)
        parsed = extract_text(upload)
        if parsed.parser == "fallback":
            warnings.append(f"Could not parse {name}; sent placeholder text to the courtroom.")
        elif parsed.truncated:
            warnings.append(
                f"{name} was {parsed.original_chars:,} chars; truncated to 30,000 to stay under the LLM rate limit."
            )
        docs.append(
            Document(
                doc_id=f"doc_{i:02d}",
                filename=name,
                mime_type=mime,
                content=parsed.text,
            )
        )

    pasted = str(payload.get("pasted_text") or "").strip()
    if pasted:
        docs.append(
            Document(
                doc_id=f"doc_{len(docs) + 1:02d}",
                filename="pasted_use_case.md",
                mime_type="text/markdown",
                content=pasted,
            )
        )

    if not docs:
        raise ValueError("At least one uploaded file or pasted use-case description is required.")

    return (
        CaseFile(
            case_id=f"case_{uuid.uuid4().hex[:8]}",
            status=CaseStatus.NEW,
            documents=docs,
        ),
        warnings,
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "ObjectionAIActHTTP/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")

    def do_OPTIONS(self) -> None:
        self._send_json({}, HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._send_json({"ok": True})
            return
        self._serve_static()

    def do_POST(self) -> None:
        try:
            payload = self._read_json()
            if self.path == "/api/run-courtroom":
                case, warnings = _build_new_case(payload)
                result = run_courtroom(case)
                self._send_json({"case_file": _json_case(result), "warnings": warnings})
                return
            if self.path == "/api/chat":
                case = _case_from_payload(payload)
                text = str(payload.get("user_text") or "").strip()
                if not text:
                    raise ValueError("user_text is required.")
                result = handle_chat(case, text)
                self._send_json({"case_file": _json_case(result)})
                return
            if self.path == "/api/export-pdf":
                case = _case_from_payload(payload)
                pdf_bytes = case_to_pdf_bytes(case)
                self._send_binary(
                    pdf_bytes,
                    "application/pdf",
                    case_pdf_filename(case),
                )
                return
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
        except BackendValidationError as exc:
            self._send_json(
                {
                    "error": str(exc),
                    "agent": exc.agent,
                    "details": exc.errors,
                    "raw_output": exc.raw_output,
                },
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
        except Exception as exc:
            status = HTTPStatus.BAD_REQUEST
            text = str(exc)
            if type(exc).__name__ == "RateLimitError" or "rate_limit" in text.lower() or "429" in text:
                status = HTTPStatus.TOO_MANY_REQUESTS
                text = "Rate limit hit; wait about 1 minute and try again, or upload fewer / smaller documents."
            self._send_json({"error": text or type(exc).__name__}, status)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_BODY_BYTES:
            raise ValueError("Request body is too large.")
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = b"" if status == HTTPStatus.NO_CONTENT else json.dumps(payload).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Expose-Headers", "Content-Disposition")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _send_binary(self, data: bytes, content_type: str, filename: str) -> None:
        fallback_name = "".join(
            c if c.isascii() and (c.isalnum() or c in "-_.") else "_"
            for c in filename
        ) or "objection_verdict.pdf"
        encoded_name = quote(filename, safe="")
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Expose-Headers", "Content-Disposition")
        self.send_header("Content-Type", content_type)
        self.send_header(
            "Content-Disposition",
            f"attachment; filename=\"{fallback_name}\"; filename*=UTF-8''{encoded_name}",
        )
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_static(self) -> None:
        if not FRONTEND_DIST.exists():
            self._send_text(
                "Frontend build not found. Run `cd frontend && npm.cmd run build`, then restart this server.",
                HTTPStatus.NOT_FOUND,
                "text/plain; charset=utf-8",
            )
            return

        route = unquote(urlparse(self.path).path).lstrip("/")
        target = (FRONTEND_DIST / route).resolve() if route else FRONTEND_DIST / "index.html"
        dist_root = FRONTEND_DIST.resolve()
        if not str(target).startswith(str(dist_root)):
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        if not target.is_file():
            target = FRONTEND_DIST / "index.html"

        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_text(self, text: str, status: HTTPStatus, content_type: str) -> None:
        body = text.encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"OBJECTION! AI ACT API listening on http://{HOST}:{PORT}")
    print("Serving React frontend from frontend/dist when present.")
    print("Endpoints: POST /api/run-courtroom, POST /api/chat, POST /api/export-pdf, GET /api/health")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
