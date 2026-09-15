from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .diagnostics import DiagnosticCode


class DatasetError(ValueError):
    def __init__(self, code: DiagnosticCode, message: str) -> None:
        super().__init__(f"{code.value}: {message}")
        self.code = code


_VALID_STATUSES = {"draft", "pending_verification", "production_verified", "deprecated"}


class RuleRegistry:
    def __init__(self, data_dir: Path, *, allow_unverified: bool = False) -> None:
        self.data_dir = Path(data_dir)
        self.allow_unverified = allow_unverified

    def load(self, dataset_id: str) -> dict[str, Any]:
        return load_dataset(dataset_id, allow_unverified=self.allow_unverified, data_dir=self.data_dir)


def load_dataset(dataset_id: str, *, allow_unverified: bool = False, data_dir: Path) -> dict[str, Any]:
    path = Path(data_dir) / f"{dataset_id}.json"
    with path.open(encoding="utf-8") as stream:
        payload: dict[str, Any] = json.load(stream)
    required = {"schema_version", "dataset_id", "dataset_version", "status", "source", "license", "generated_at", "data"}
    missing = required - payload.keys()
    if missing:
        raise DatasetError(DiagnosticCode.DATASET_SCHEMA_INVALID, f"missing fields: {sorted(missing)}")
    if payload["dataset_id"] != dataset_id:
        raise DatasetError(DiagnosticCode.DATASET_SCHEMA_INVALID, "dataset_id does not match filename")
    if payload["status"] not in _VALID_STATUSES:
        raise DatasetError(DiagnosticCode.DATASET_STATUS_INVALID, f"unknown status: {payload['status']}")
    if payload["status"] != "production_verified" and not allow_unverified:
        raise DatasetError(DiagnosticCode.DATASET_NOT_PRODUCTION_VERIFIED, dataset_id)
    return payload
