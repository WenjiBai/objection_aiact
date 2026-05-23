"""Load `rules.yaml` into typed `RuleSpec` objects with raw YAML text captured.

Spec: Backend_Architecture_v1.md §2.4 / Frontend_Backend_Sync_v1.md §4.

Each rule's original YAML text is injected as `RuleSpec.yaml_source` so the
Symbolic Rules Panel in the UI can render it verbatim without re-parsing
or hitting the disk.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_RULES_PATH = Path(__file__).resolve().parent / "rules.yaml"


class RuleSpec(BaseModel):
    """One loaded rule from `rules.yaml`. `yaml_source` is injected on load."""
    model_config = ConfigDict(extra="forbid")

    id: str
    description: str
    when: dict[str, Any]
    then: dict[str, Any] = Field(default_factory=dict)
    maps_to_refs: list[str] = Field(default_factory=list)
    severity: str = "medium"
    yaml_source: str


def load_rules(path: Path | str = DEFAULT_RULES_PATH) -> list[RuleSpec]:
    """Parse `rules.yaml` into a list of `RuleSpec`s with per-rule yaml_source."""
    p = Path(path)
    parsed = yaml.safe_load(p.read_text(encoding="utf-8"))

    if not isinstance(parsed, list):
        raise ValueError(
            f"{p.name} root must be a list of rule mappings, "
            f"got {type(parsed).__name__}"
        )

    rules: list[RuleSpec] = []
    for item in parsed:
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError(f"rule entry missing 'id': {item!r}")
        yaml_source = yaml.dump([item], sort_keys=False, allow_unicode=True)
        rules.append(RuleSpec(yaml_source=yaml_source, **item))
    return rules


__all__ = ["RuleSpec", "load_rules", "DEFAULT_RULES_PATH"]
