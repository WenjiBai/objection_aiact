"""CaseFile schema — single source of truth for OBJECTION! AI ACT.

Implements documents/CaseFile_Schema_Spec.md v2 (A-approved).
Backend agents write to this; UI renders from this.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ================================================================ enums

class RiskTier(str, Enum):
    PROHIBITED = "prohibited"
    HIGH_RISK = "high_risk"
    POTENTIAL_HIGH_RISK = "potential_high_risk"  # symbolic gate default
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"
    UNKNOWN = "unknown"


class ConfidenceLabel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class EvidenceCategory(str, Enum):
    PURPOSE = "purpose"
    USERS = "users"
    AFFECTED_PERSONS = "affected_persons"
    SECTOR = "sector"
    INPUT_DATA = "input_data"
    OUTPUT = "output"
    AUTOMATION_LEVEL = "automation_level"
    HUMAN_OVERSIGHT = "human_oversight"
    DEPLOYMENT_CONTEXT = "deployment_context"
    AI_GENERATED_CONTENT = "ai_generated_content"
    GPAI_USAGE = "gpai_usage"
    DECISION_IMPACT = "decision_impact"
    OTHER = "other"


class OutputType(str, Enum):
    """Symbolic gate matching — Detective normalises extracted facts to one of these."""
    RANKING = "ranking"
    SCREENING = "screening"
    RECOMMENDATION = "recommendation"
    SCORING = "scoring"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    FORECAST = "forecast"
    DECISION = "decision"
    DETECTION = "detection"
    OTHER = "other"


class Sector(str, Enum):
    """Annex III eight categories + common non-high-risk sectors."""
    EMPLOYMENT = "employment"
    EDUCATION = "education"
    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    BIOMETRICS = "biometrics"
    LAW_ENFORCEMENT = "law_enforcement"
    MIGRATION_BORDER = "migration_border"
    JUSTICE_DEMOCRACY = "justice_democracy"
    ESSENTIAL_SERVICES = "essential_services"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    LOGISTICS = "logistics"
    RETAIL = "retail"
    GENERAL_BUSINESS = "general_business"
    OTHER = "other"


class SourceType(str, Enum):
    LEGISLATION = "legislation"
    GUIDANCE = "guidance"
    NATIONAL = "national"
    COMMENTARY = "commentary"
    UPLOADED = "uploaded"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CaseStatus(str, Enum):
    NEW = "new"
    INGESTING = "ingesting"
    RETRIEVING = "retrieving"
    DELIBERATING = "deliberating"
    VERDICT_READY = "verdict_ready"
    RE_EXAMINING = "re_examining"
    ERROR = "error"


class AgentName(str, Enum):
    DETECTIVE = "detective"
    LEGAL_CLERK = "legal_clerk"
    PROSECUTOR = "prosecutor"
    DEFENSE = "defense"
    CRITIQUE = "critique"
    JUDGE = "judge"


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# =============================================================== models

class _Base(BaseModel):
    # extra=forbid catches LLM hallucinated keys at parse time → backend retry.
    model_config = ConfigDict(extra="forbid", use_enum_values=False)


# --- documents & atomic evidence ----------------------------------------

class Document(_Base):
    doc_id: str
    filename: str
    mime_type: str
    content: str
    page_count: Optional[int] = None
    uploaded_at: datetime = Field(default_factory=datetime.now)


class Evidence(_Base):
    """E-code — facts extracted from uploaded docs. Code format: `E-{n:02d}`."""
    code: str
    source_doc_id: str
    source_locator: Optional[str] = None
    text: str
    structured_value: Optional[str] = None
    category: EvidenceCategory
    relevance: Severity

    @model_validator(mode="after")
    def _check_structured_value(self) -> "Evidence":
        # Sync v1 §2.1.4 — structured_value required for these categories.
        if self.category == EvidenceCategory.SECTOR:
            allowed = {s.value for s in Sector}
            if self.structured_value not in allowed:
                raise ValueError(
                    f"Evidence {self.code} category=sector requires structured_value "
                    f"in {sorted(allowed)}, got {self.structured_value!r}"
                )
        elif self.category == EvidenceCategory.OUTPUT:
            allowed = {o.value for o in OutputType}
            if self.structured_value not in allowed:
                raise ValueError(
                    f"Evidence {self.code} category=output requires structured_value "
                    f"in {sorted(allowed)}, got {self.structured_value!r}"
                )
        elif self.category == EvidenceCategory.GPAI_USAGE:
            if self.structured_value not in {"true", "false", "unknown"}:
                raise ValueError(
                    f"Evidence {self.code} category=gpai_usage requires structured_value "
                    f"in 'true'/'false'/'unknown', got {self.structured_value!r}"
                )
        return self


class Reference(_Base):
    """R-code — citations from the AI Act corpus.

    Code formats: `R-Art-{n}` / `R-Annex-{n}-{item}` / `R-Recital-{n}`
    / `R-Guide-{slug}` / `R-FI-{slug}`.
    """
    code: str
    article_no: str
    title: str
    snippet: str
    full_text: str
    source_type: SourceType
    source_label: str
    url: Optional[str] = None
    relevance_score: Optional[float] = None


class Assumption(_Base):
    """A-code — system-generated assumptions, must be confirmable. Code: `A-{n:02d}`."""
    code: str
    text: str
    reasoning: str
    needs_confirmation: bool = True


# --- workflow types -----------------------------------------------------

class RuleFiring(_Base):
    """Symbolic Rules Panel reads this directly."""
    rule_id: str
    description: str
    fired: bool
    when_conditions: dict
    evaluated_against: dict
    then_actions: dict
    supporting_evidence_codes: list[str] = Field(default_factory=list)
    maps_to_refs: list[str] = Field(default_factory=list)
    yaml_source: str  # injected by A on loading rules.yaml — UI shows verbatim


class Allegation(_Base):
    """Prosecutor's claim."""
    allegation_id: str
    tier: RiskTier
    claim: str
    basis_evidence_codes: list[str] = Field(default_factory=list)
    basis_ref_codes: list[str] = Field(default_factory=list)
    strength: Severity


class Defense(_Base):
    """Mitigation / exemption argument."""
    defense_id: str
    targets_allegation_id: Optional[str] = None
    type: str  # "narrow_procedural" | "human_oversight" | "exemption_documented" | …
    claim: str
    basis_evidence_codes: list[str] = Field(default_factory=list)
    basis_ref_codes: list[str] = Field(default_factory=list)
    requires_documentation: bool


class Objection(_Base):
    """Critique agent's challenge."""
    objection_id: str
    target_type: str  # "allegation" | "defense" | "verdict" | "fact"
    target_id: str
    reason: str
    severity: Severity
    challenging_evidence_codes: list[str] = Field(default_factory=list)
    resolution: Optional[str] = None  # None → not yet handled


# --- agent visualisation -----------------------------------------------

class AgentActivity(_Base):
    """One row in the 6-agent timeline."""
    agent: AgentName
    action: str
    status: AgentStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_summary: Optional[str] = None


# --- result types -------------------------------------------------------

class Verdict(_Base):
    tier: RiskTier
    confidence_score: int = Field(ge=0, le=10)
    confidence_label: ConfidenceLabel
    reasoning_trail: str
    caveats: list[str] = Field(default_factory=lambda: [
        "Preliminary assessment only — not legal advice.",
        "Human legal review is recommended before deployment.",
    ])

    @model_validator(mode="after")
    def _check_label_matches_score(self) -> "Verdict":
        # Sync v1 §2.1.6 — confidence_label must agree with score.
        if 0 <= self.confidence_score <= 3:
            expected = ConfidenceLabel.LOW
        elif 4 <= self.confidence_score <= 6:
            expected = ConfidenceLabel.MEDIUM
        else:
            expected = ConfidenceLabel.HIGH
        if self.confidence_label != expected:
            raise ValueError(
                f"confidence_label={self.confidence_label.value} disagrees with "
                f"score={self.confidence_score} (expected {expected.value})"
            )
        return self


class MissingEvidenceItem(_Base):
    description: str
    severity: Severity
    blocks_verdict: bool = False
    suggested_questions: list[str] = Field(default_factory=list)


class ChecklistItem(_Base):
    item: str
    applies: bool
    ai_act_reference: Optional[str] = None
    evidence_codes: list[str] = Field(default_factory=list)
    note: Optional[str] = None


class ChatTurn(_Base):
    role: str  # "user" | "judge" | "system"
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    triggered_updates: list[str] = Field(default_factory=list)


# --- root --------------------------------------------------------------

class CaseFile(_Base):
    case_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    status: CaseStatus = CaseStatus.NEW

    documents: list[Document] = Field(default_factory=list)

    facts: list[Evidence] = Field(default_factory=list)
    refs: list[Reference] = Field(default_factory=list)
    assumptions: list[Assumption] = Field(default_factory=list)

    rule_firings: list[RuleFiring] = Field(default_factory=list)
    allegations: list[Allegation] = Field(default_factory=list)
    defenses: list[Defense] = Field(default_factory=list)
    objections: list[Objection] = Field(default_factory=list)

    verdict: Optional[Verdict] = None
    missing_evidence: list[MissingEvidenceItem] = Field(default_factory=list)
    governance_checklist: list[ChecklistItem] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)

    agent_activity: list[AgentActivity] = Field(default_factory=list)

    chat_history: list[ChatTurn] = Field(default_factory=list)

    snapshot_id: Optional[str] = None  # rollback handle


__all__ = [
    # enums
    "RiskTier", "ConfidenceLabel", "EvidenceCategory", "OutputType", "Sector",
    "SourceType", "Severity", "CaseStatus", "AgentName", "AgentStatus",
    # atomic
    "Document", "Evidence", "Reference", "Assumption",
    # workflow
    "RuleFiring", "Allegation", "Defense", "Objection",
    # viz
    "AgentActivity",
    # result
    "Verdict", "MissingEvidenceItem", "ChecklistItem", "ChatTurn",
    # root
    "CaseFile",
]
