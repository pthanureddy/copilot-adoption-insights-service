from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from copilot_insights.models import TeamMembership, UsageRecord

T = TypeVar("T", bound=BaseModel)


class InputFormatError(ValueError):
    pass


def _read_ndjson(path: Path, model: type[T]) -> list[T]:
    records: list[T] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            records.append(model.model_validate_json(raw_line))
        except (ValidationError, ValueError) as exc:
            raise InputFormatError(f"{path}:{line_number}: {exc}") from exc
    if not records:
        raise InputFormatError(f"{path}: no records found")
    return records


def read_usage(path: Path) -> list[UsageRecord]:
    return _read_ndjson(path, UsageRecord)


def read_memberships(path: Path) -> list[TeamMembership]:
    return _read_ndjson(path, TeamMembership)


def write_json(path: Path, value: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8")
