from datetime import date
import tempfile
import json
from importlib.resources import files
from pathlib import Path

import pytest

from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.day_pillar import day_pillar_for_date
from destiny_saju.diagnostics import DiagnosticCode
from destiny_saju.branches import EarthlyBranch
from destiny_saju.stems import HeavenlyStem


def test_day_pillar_fails_closed_without_a_verified_anchor() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        with pytest.raises(DatasetError) as error:
            day_pillar_for_date(date(2019, 1, 27), RuleRegistry(Path(temporary), allow_unverified=True))

    assert error.value.code is DiagnosticCode.DAY_PILLAR_ANCHOR_UNAVAILABLE


def test_verified_anchor_covers_a_complete_sexagenary_cycle() -> None:
    registry = RuleRegistry(allow_unverified=True)
    start = date(2019, 1, 27)

    pillars = [day_pillar_for_date(start.fromordinal(start.toordinal() + offset), registry) for offset in range(61)]

    assert pillars[0].stem is HeavenlyStem.GAP
    assert pillars[0].branch is EarthlyBranch.JA
    assert pillars[60] == pillars[0]
    assert len(set(pillars[:60])) == 60
    assert {pillar.stem for pillar in pillars[:60]} == set(HeavenlyStem)
    assert {pillar.branch for pillar in pillars[:60]} == set(EarthlyBranch)


def test_anchor_jdn_or_sexagenary_value_corruption_is_rejected() -> None:
    source = files("destiny_saju.data.saju")
    for field, value in (("julian_day_number_at_noon", 1), ("day_branch", "branch:chuk")):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            for resource in source.iterdir():
                if resource.name.endswith(".json"):
                    (target / resource.name).write_bytes(resource.read_bytes())
            path = target / "day_pillar_anchor_v1.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["data"][field] = value
            path.write_text(json.dumps(payload), encoding="utf-8")

            with pytest.raises(DatasetError) as error:
                RuleRegistry(target, allow_unverified=True).load("day_pillar_anchor_v1")
            assert error.value.code is DiagnosticCode.DATASET_SCHEMA_INVALID


def test_day_pillar_rejects_non_date_input_before_loading_data() -> None:
    with pytest.raises(TypeError, match="civil_date"):
        day_pillar_for_date("2019-01-27", RuleRegistry(allow_unverified=True))  # type: ignore[arg-type]
