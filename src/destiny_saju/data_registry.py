from __future__ import annotations

import copy
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from .diagnostics import DiagnosticCode


class DatasetError(ValueError):
    def __init__(self, code: DiagnosticCode, message: str) -> None:
        super().__init__(f"{code.value}: {message}")
        self.code = code


_VALID_STATUSES = {"draft", "pending_verification", "production_verified", "deprecated"}
_ELEMENTS = {"wood", "fire", "earth", "metal", "water"}
_RELATIONS = {
    "same_element",
    "day_master_generates_target",
    "day_master_controls_target",
    "target_controls_day_master",
    "target_generates_day_master",
}
_TEN_GODS = {
    "bigyeon", "geopjae", "siksin", "sangwan", "pyeonjae",
    "jeongjae", "pyeongwan", "jeonggwan", "pyeonin", "jeongin",
}


class RuleRegistry:
    """Load and validate rules from package resources or an override directory."""

    def __init__(self, data_dir: Path | None = None, *, allow_unverified: bool = False) -> None:
        self.data_dir = Path(data_dir) if data_dir is not None else files("destiny_saju.data.saju")
        self.allow_unverified = allow_unverified
        self._cache: dict[str, dict[str, Any]] = {}

    def load(self, dataset_id: str) -> dict[str, Any]:
        if dataset_id not in self._cache:
            payload = self._read(dataset_id)
            _validate_envelope(payload, dataset_id, self.allow_unverified)
            core = payload if dataset_id == "core_tables_v1" else self._load_core()
            _validate_data(payload, core)
            self._cache[dataset_id] = payload
        return copy.deepcopy(self._cache[dataset_id])

    def _read(self, dataset_id: str) -> dict[str, Any]:
        path = self.data_dir.joinpath(f"{dataset_id}.json")
        try:
            with path.open(encoding="utf-8") as stream:
                payload = json.load(stream)
        except (FileNotFoundError, OSError, json.JSONDecodeError) as error:
            raise DatasetError(DiagnosticCode.DATASET_SCHEMA_INVALID, f"{dataset_id}: {error}") from error
        if not isinstance(payload, dict):
            raise DatasetError(DiagnosticCode.DATASET_SCHEMA_INVALID, f"{dataset_id}: root must be an object")
        return payload

    def _load_core(self) -> dict[str, Any]:
        if "core_tables_v1" not in self._cache:
            core = self._read("core_tables_v1")
            _validate_envelope(core, "core_tables_v1", self.allow_unverified)
            _validate_data(core, core)
            self._cache["core_tables_v1"] = core
        return self._cache["core_tables_v1"]


def load_dataset(
    dataset_id: str, *, allow_unverified: bool = False, data_dir: Path | None = None
) -> dict[str, Any]:
    return RuleRegistry(data_dir, allow_unverified=allow_unverified).load(dataset_id)


def _invalid(dataset_id: str, message: str) -> None:
    raise DatasetError(DiagnosticCode.DATASET_SCHEMA_INVALID, f"{dataset_id}: {message}")


def _validate_envelope(payload: dict[str, Any], dataset_id: str, allow_unverified: bool) -> None:
    required = {"schema_version", "dataset_id", "dataset_version", "status", "source", "license", "generated_at", "data"}
    missing = required - payload.keys()
    if missing:
        _invalid(dataset_id, f"missing fields: {sorted(missing)}")
    if payload["dataset_id"] != dataset_id:
        _invalid(dataset_id, "dataset_id does not match filename")
    if payload["status"] not in _VALID_STATUSES:
        raise DatasetError(DiagnosticCode.DATASET_STATUS_INVALID, f"unknown status: {payload['status']}")
    if payload["status"] != "production_verified" and not allow_unverified:
        raise DatasetError(DiagnosticCode.DATASET_NOT_PRODUCTION_VERIFIED, dataset_id)
    if not isinstance(payload["data"], dict):
        _invalid(dataset_id, "data must be an object")


def _validate_data(payload: dict[str, Any], core: dict[str, Any]) -> None:
    dataset_id = payload["dataset_id"]
    try:
        if dataset_id == "core_tables_v1":
            _validate_core(payload["data"], dataset_id)
            return
        stem_refs, branch_refs = _vocabulary(core)
        data = payload["data"]
        if dataset_id == "month_stem_rules_v1":
            _validate_stem_start_rules(data, dataset_id, "tiger_start_by_year_stem_group", "year_stems", "in_month_start_stem", "month_branch_order_from_in", "branch:in", stem_refs, branch_refs)
        elif dataset_id == "hour_stem_rules_v1":
            _validate_stem_start_rules(data, dataset_id, "rat_start_by_day_stem_group", "day_stems", "ja_hour_start_stem", "hour_branch_order_from_ja", "branch:ja", stem_refs, branch_refs)
        elif dataset_id == "hidden_stems_v1":
            _validate_hidden_stems(data, dataset_id, stem_refs, branch_refs)
        elif dataset_id == "ten_gods_v1":
            _validate_ten_gods(data, dataset_id)
    except DatasetError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        _invalid(dataset_id, str(error))


def _validate_core(data: dict[str, Any], dataset_id: str) -> None:
    try:
        stems = data["heavenly_stems"]
        branches = data["earthly_branches"]
        if len(stems) != 10 or len({row["id"] for row in stems}) != 10:
            _invalid(dataset_id, "heavenly_stems must contain 10 unique ids")
        if len(branches) != 12 or len({row["id"] for row in branches}) != 12:
            _invalid(dataset_id, "earthly_branches must contain 12 unique ids")
        if {row["order"] for row in stems} != set(range(1, 11)):
            _invalid(dataset_id, "heavenly_stems order must be 1..10")
        if {row["order"] for row in branches} != set(range(1, 13)):
            _invalid(dataset_id, "earthly_branches order must be 1..12")
        if {row["element"] for row in stems + branches} - _ELEMENTS:
            _invalid(dataset_id, "unknown element")
        relations = data["element_relations"]
        for name in ("generates", "controls"):
            mapping = relations[name]
            if set(mapping) != _ELEMENTS or set(mapping.values()) != _ELEMENTS:
                _invalid(dataset_id, f"element_relations.{name} must map every element exactly once")
            if any(source == target for source, target in mapping.items()):
                _invalid(dataset_id, f"element_relations.{name} cannot contain self-relations")
        for source in _ELEMENTS:
            for target in _ELEMENTS - {source}:
                matches = sum(
                    (
                        relations["generates"][source] == target,
                        relations["controls"][source] == target,
                        relations["controls"][target] == source,
                        relations["generates"][target] == source,
                    )
                )
                if matches != 1:
                    _invalid(dataset_id, f"element relation is ambiguous or missing: {source}->{target}")
    except DatasetError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        _invalid(dataset_id, str(error))


def _vocabulary(core: dict[str, Any]) -> tuple[set[str], set[str]]:
    data = core["data"]
    return (
        {f"stem:{row['id']}" for row in data["heavenly_stems"]},
        {f"branch:{row['id']}" for row in data["earthly_branches"]},
    )


def _validate_stem_start_rules(data: dict[str, Any], dataset_id: str, groups_key: str, members_key: str, start_key: str, order_key: str, first_branch: str, stem_refs: set[str], branch_refs: set[str]) -> None:
    groups = data[groups_key]
    members = [reference for group in groups for reference in group[members_key]]
    starts = [group[start_key] for group in groups]
    order = data[order_key]
    if len(groups) != 5 or len(members) != 10 or set(members) != stem_refs or len(set(members)) != 10:
        _invalid(dataset_id, f"{members_key} must cover every stem exactly once")
    if any(reference not in stem_refs for reference in starts):
        _invalid(dataset_id, f"{start_key} contains an unknown stem")
    if len(order) != 12 or set(order) != branch_refs or len(set(order)) != 12 or order[0] != first_branch:
        _invalid(dataset_id, f"{order_key} must cover every branch once and start with {first_branch}")


def _validate_hidden_stems(data: dict[str, Any], dataset_id: str, stem_refs: set[str], branch_refs: set[str]) -> None:
    mapping = data["branch_hidden_stems"]
    if set(mapping) != branch_refs:
        _invalid(dataset_id, "branch_hidden_stems must cover every branch exactly once")
    for branch, rows in mapping.items():
        if not 1 <= len(rows) <= 3:
            _invalid(dataset_id, f"{branch} must contain 1..3 hidden stems")
        if any(row["stem"] not in stem_refs for row in rows):
            _invalid(dataset_id, f"{branch} contains an unknown stem")
        if sum(row["role"] == "main" for row in rows) != 1:
            _invalid(dataset_id, f"{branch} must contain one main stem")
        if [row["display_order"] for row in rows] != list(range(1, len(rows) + 1)):
            _invalid(dataset_id, f"{branch} display_order must be contiguous")


def _validate_ten_gods(data: dict[str, Any], dataset_id: str) -> None:
    rows = data["relation_table"]
    if len(rows) != 5 or {row["relation_element"] for row in rows} != _RELATIONS:
        _invalid(dataset_id, "relation_table must cover all five relations exactly once")
    values = {row[key] for row in rows for key in ("same_polarity", "different_polarity")}
    if values != _TEN_GODS or set(data["display_names"]) != _TEN_GODS:
        _invalid(dataset_id, "relation_table and display_names must cover all ten gods")
    if data["polarity_rule"] != "same_yin_yang_selects_same_polarity_column":
        _invalid(dataset_id, "unknown polarity_rule")
