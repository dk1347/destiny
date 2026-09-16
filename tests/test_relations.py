from datetime import datetime, timedelta, timezone
import json
import tempfile
from importlib.resources import files
from pathlib import Path

import pytest

from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.four_pillars import four_pillars_for_datetime
from destiny_saju.relations import relations_for_pillars


KST = timezone(timedelta(hours=9))


def _registry_with_relations() -> RuleRegistry:
    source = files("destiny_saju.data.saju")
    temporary = tempfile.TemporaryDirectory()
    target = Path(temporary.name)
    for resource in source.iterdir():
        if resource.name.endswith(".json"):
            (target / resource.name).write_bytes(resource.read_bytes())
    payload = {
        "schema_version": "1.0.0", "dataset_id": "relations_v1", "dataset_version": "1.0.0",
        "status": "pending_verification", "source": {"kind": "test"}, "license": {"kind": "test"},
        "generated_at": "2026-01-01T00:00:00+09:00",
        "data": {
            "stem_combinations": [{"relation_id": "stem-gap-gi", "relation_type": "stem_combination", "participants": ["stem:gap", "stem:gi"], "resulting_element": "earth"}],
            "branch_relations": [{"relation_id": "branch-in-o", "relation_type": "branch_half_three_harmony_candidate", "participants": ["branch:in", "branch:o"], "resulting_element": "fire"}],
        },
    }
    (target / "relations_v1.json").write_text(json.dumps(payload), encoding="utf-8")
    registry = RuleRegistry(target, allow_unverified=True)
    registry._temporary_directory = temporary  # type: ignore[attr-defined]
    return registry


def test_relation_lookup_requires_a_dataset() -> None:
    pillars = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), RuleRegistry(allow_unverified=True))
    with pytest.raises(DatasetError):
        relations_for_pillars(pillars, RuleRegistry(allow_unverified=True))


def test_relation_lookup_returns_detected_facts_only() -> None:
    registry = _registry_with_relations()
    pillars = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)
    assert relations_for_pillars(pillars, registry)[0].relation_id == "branch-in-o"
    assert relations_for_pillars(pillars, registry)[0].participants == ("year_branch", "month_branch")
    assert relations_for_pillars(pillars, registry)[0].values == ("in", "o")
    assert relations_for_pillars(pillars, registry)[0].resulting_element == "fire"
    assert relations_for_pillars(pillars, registry)[0].rule_set_version == "relations_v1@1.0.0"


def test_relations_dataset_rejects_unknown_reference() -> None:
    registry = _registry_with_relations()
    data = registry.load("relations_v1")
    data["data"]["branch_relations"][0]["participants"][1] = "branch:unknown"
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary)
        for resource in registry.data_dir.iterdir():
            if resource.name.endswith(".json"):
                (target / resource.name).write_bytes(resource.read_bytes())
        path = target / "relations_v1.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(DatasetError, match="DATASET_SCHEMA_INVALID"):
            RuleRegistry(target, allow_unverified=True).load("relations_v1")
