"""Abstract base class for the 6 courtroom agents.

Each concrete agent:
  1. Builds (system_prompt, user_prompt) from the current CaseFile.
  2. Calls `backend.llm.client.call_agent` with its Pydantic output schema.
  3. Merges the validated output back into the CaseFile.
  4. Returns the CaseFile with one AgentActivity entry appended (COMPLETED
     on success, FAILED on a backend validation error after retry).

The orchestrator owns ordering; the base class owns timing + bookkeeping.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from backend.exceptions import BackendValidationError
from backend.llm.client import DEFAULT_MAX_TOKENS, call_agent
from shared.schema import (
    AgentActivity, AgentName, AgentStatus, CaseFile,
)

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class BaseAgent(ABC):
    """Template-method base — subclasses implement build_prompt + merge."""

    # Subclasses set these as class attributes.
    agent_name: AgentName
    output_schema: type[BaseModel]
    prompt_filename: str          # e.g. "detective.txt"
    action_summary: str           # one-liner for AgentActivity.action
    max_tokens: int = DEFAULT_MAX_TOKENS

    def run(self, case: CaseFile) -> CaseFile:
        """Execute this agent and append exactly one AgentActivity entry."""
        started_at = datetime.now()
        try:
            system_prompt, user_prompt = self.build_prompt(case)
            output = call_agent(
                system_prompt, user_prompt, self.output_schema,
                max_tokens=self.max_tokens,
            )
            self.merge(case, output)
        except BackendValidationError:
            case.agent_activity.append(
                AgentActivity(
                    agent=self.agent_name,
                    action=self.action_summary,
                    status=AgentStatus.FAILED,
                    started_at=started_at,
                    completed_at=datetime.now(),
                    output_summary="Validation failed after retry.",
                )
            )
            raise

        case.agent_activity.append(
            AgentActivity(
                agent=self.agent_name,
                action=self.action_summary,
                status=AgentStatus.COMPLETED,
                started_at=started_at,
                completed_at=datetime.now(),
                output_summary=self.summarise(output),
            )
        )
        return case

    def load_prompt(self) -> str:
        """Read this agent's system prompt template from backend/prompts/."""
        return (PROMPTS_DIR / self.prompt_filename).read_text(encoding="utf-8")

    @abstractmethod
    def build_prompt(self, case: CaseFile) -> tuple[str, str]:
        """Return `(system_prompt, user_prompt)` for this agent's call."""

    @abstractmethod
    def merge(self, case: CaseFile, output: BaseModel) -> None:
        """Apply the validated LLM output back onto the CaseFile in place."""

    def summarise(self, output: BaseModel) -> str:
        """Short one-line summary shown in the AgentActivity timeline."""
        return ""


__all__ = ["BaseAgent", "PROMPTS_DIR"]
