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
    with pytest.raises(DatasetError, match="DATASET_NOT_PRODUCTION_VERIFIED"):
        relations_for_pillars(pillars, RuleRegistry())


def test_pending_relations_dataset_is_available_only_in_explicit_test_mode() -> None:
    pillars = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), RuleRegistry(allow_unverified=True))
    findings = relations_for_pillars(pillars, RuleRegistry(allow_unverified=True))
    assert {finding.relation_id for finding in findings} == {"branch-half-in-o", "branch-clash-myo-yu"}


def test_bundled_relations_candidate_rows_match_the_audited_structural_tables() -> None:
    data = RuleRegistry(allow_unverified=True).load("relations_v1")["data"]

    assert {
        (row["participants"][0], row["participants"][1], row["resulting_element"])
        for row in data["stem_combinations"]
    } == {
        ("stem:gap", "stem:gi", "earth"),
        ("stem:eul", "stem:gyeong", "metal"),
        ("stem:byeong", "stem:sin", "water"),
        ("stem:jeong", "stem:im", "wood"),
        ("stem:mu", "stem:gye", "fire"),
    }

    complete_three_harmonies = {
        tuple(row["participants"]): row["resulting_element"]
        for row in data["branch_relations"]
        if row["relation_type"] == "branch_three_harmony"
    }
    assert complete_three_harmonies == {
        ("branch:sin", "branch:ja", "branch:jin"): "water",
        ("branch:sa", "branch:yu", "branch:chuk"): "metal",
        ("branch:in", "branch:o", "branch:sul"): "fire",
        ("branch:hae", "branch:myo", "branch:mi"): "wood",
    }
    assert {
        frozenset(row["participants"]): row["resulting_element"]
        for row in data["branch_relations"]
        if row["relation_type"] == "branch_six_combination"
    } == {
        frozenset(("branch:ja", "branch:chuk")): "earth",
        frozenset(("branch:in", "branch:hae")): "wood",
        frozenset(("branch:myo", "branch:sul")): "fire",
        frozenset(("branch:jin", "branch:yu")): "metal",
        frozenset(("branch:sa", "branch:sin")): "water",
        frozenset(("branch:o", "branch:mi")): "earth",
    }
    assert {
        frozenset(row["participants"]): row["resulting_element"]
        for row in data["branch_relations"]
        if row["relation_type"] == "branch_half_three_harmony_candidate"
    } == {
        frozenset(("branch:sin", "branch:ja")): "water",
        frozenset(("branch:ja", "branch:jin")): "water",
        frozenset(("branch:sin", "branch:jin")): "water",
        frozenset(("branch:sa", "branch:yu")): "metal",
        frozenset(("branch:yu", "branch:chuk")): "metal",
        frozenset(("branch:sa", "branch:chuk")): "metal",
        frozenset(("branch:in", "branch:o")): "fire",
        frozenset(("branch:o", "branch:sul")): "fire",
        frozenset(("branch:in", "branch:sul")): "fire",
        frozenset(("branch:hae", "branch:myo")): "wood",
        frozenset(("branch:myo", "branch:mi")): "wood",
        frozenset(("branch:hae", "branch:mi")): "wood",
    }
    assert {
        frozenset(row["participants"])
        for row in data["branch_relations"]
        if row["relation_type"] == "branch_clash"
    } == {
        frozenset(pair)
        for pair in (
            ("branch:ja", "branch:o"),
            ("branch:chuk", "branch:mi"),
            ("branch:in", "branch:sin"),
            ("branch:myo", "branch:yu"),
            ("branch:jin", "branch:sul"),
            ("branch:sa", "branch:hae"),
        )
    }


def test_relation_lookup_returns_detected_facts_only() -> None:
    registry = _registry_with_relations()
    pillars = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)
    assert relations_for_pillars(pillars, registry)[0].relation_id == "branch-in-o"
    assert relations_for_pillars(pillars, registry)[0].participants == ("year_branch", "month_branch")
    assert relations_for_pillars(pillars, registry)[0].values == ("in", "o")
    assert relations_for_pillars(pillars, registry)[0].resulting_element == "fire"
    assert relations_for_pillars(pillars, registry)[0].rule_set_version == "relations_v1@1.0.0"


def test_relation_values_reject_malformed_named_values() -> None:
    from destiny_saju.relations import relations_for_values

    with pytest.raises(TypeError, match="tuples"):
        relations_for_values([], (), RuleRegistry(allow_unverified=True))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="position/value"):
        relations_for_values((("year_stem",),), (), RuleRegistry(allow_unverified=True))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unique"):
        relations_for_values(
            (("year_stem", "gap"), ("year_stem", "gi")),
            (),
            RuleRegistry(allow_unverified=True),
        )


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
