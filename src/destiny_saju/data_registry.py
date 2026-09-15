from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class DatasetError(ValueError):
    pass


def load_dataset(dataset_id: str, *, allow_unverified: bool = False, data_dir: Path | None = None) -> dict[str, Any]:
    root = data_dir or Path(__file__).resolve().parents[2] / "data" / "saju"
    path = root / f"{dataset_id}.json"
    with path.open(encoding="utf-8") as stream:
        payload: dict[str, Any] = json.load(stream)
    required = {"schema_version", "dataset_id", "dataset_version", "status", "source", "license", "generated_at", "data"}
    missing = required - payload.keys()
    if missing:
        raise DatasetError(f"missing dataset fields: {sorted(missing)}")
    if payload["dataset_id"] != dataset_id:
        raise DatasetError("dataset_id does not match filename")
    if payload["status"] != "production_verified" and not allow_unverified:
        raise DatasetError("DATASET_NOT_PRODUCTION_VERIFIED")
    return payload
