from datetime import datetime, timedelta, timezone
import json
import tempfile
from importlib.resources import files
from pathlib import Path

import pytest

from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.diagnostics import DiagnosticCode
from destiny_saju.solar_terms import solar_term_for_datetime


def test_solar_term_lookup_fails_closed_without_verified_instants() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        with pytest.raises(DatasetError) as error:
            solar_term_for_datetime(
                datetime(2026, 2, 4, 0, 0, tzinfo=timezone(timedelta(hours=9))),
                RuleRegistry(Path(temporary), allow_unverified=True),
            )

    assert error.value.code is DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE


def test_solar_term_boundary_uses_the_verified_kst_instant() -> None:
    registry = RuleRegistry(allow_unverified=True)
    ipchun = datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9)))

    assert solar_term_for_datetime(ipchun - timedelta(minutes=1), registry).id == "daehan"
    assert solar_term_for_datetime(ipchun, registry).id == "ipchun"
    assert solar_term_for_datetime(ipchun + timedelta(minutes=1), registry).id == "ipchun"


def test_every_verified_solar_term_observes_its_boundary() -> None:
    registry = RuleRegistry(allow_unverified=True)
    data = registry.load("solar_term_instants_v1")["data"]
    terms = data["terms"]
    coverage_start = datetime.fromisoformat(data["coverage_start"])

    for index, row in enumerate(terms):
        instant = datetime.fromisoformat(row["occurs_at"])
        if instant < coverage_start:
            continue
        assert solar_term_for_datetime(instant, registry).id == row["id"]
        assert solar_term_for_datetime(instant + timedelta(minutes=1), registry).id == row["id"]
        if index:
            assert solar_term_for_datetime(instant - timedelta(minutes=1), registry).id == terms[index - 1]["id"]


def test_solar_term_lookup_rejects_naive_datetime() -> None:
    with pytest.raises(TypeError, match="timezone-aware"):
        solar_term_for_datetime(datetime(2026, 2, 4, 5, 2), RuleRegistry(allow_unverified=True))


def test_solar_term_lookup_rejects_non_kst_datetime() -> None:
    with pytest.raises(TypeError, match="Asia/Seoul"):
        solar_term_for_datetime(
            datetime(2026, 2, 4, 5, 2, tzinfo=timezone.utc),
            RuleRegistry(allow_unverified=True),
        )


def test_solar_term_lookup_fails_closed_outside_its_verified_coverage() -> None:
    registry = RuleRegistry(allow_unverified=True)
    with pytest.raises(DatasetError, match="SOLAR_TERM_DATA_UNAVAILABLE"):
        solar_term_for_datetime(
            datetime(2025, 12, 31, 23, 59, tzinfo=timezone(timedelta(hours=9))),
            registry,
        )
    assert solar_term_for_datetime(
        datetime(2026, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=9))),
        registry,
    ).id == "dongji"


def test_solar_term_dataset_rejects_out_of_order_or_wrong_offset_instant() -> None:
    source = files("destiny_saju.data.saju")
    for field, value in (("occurs_at", "2026-02-04T05:02:00+00:00"), ("id", "ipchun")):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            for resource in source.iterdir():
                if resource.name.endswith(".json"):
                    (target / resource.name).write_bytes(resource.read_bytes())
            path = target / "solar_term_instants_v1.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["data"]["terms"][0][field] = value
            path.write_text(json.dumps(payload), encoding="utf-8")

            with pytest.raises(DatasetError) as error:
                RuleRegistry(target, allow_unverified=True).load("solar_term_instants_v1")
            assert error.value.code is DiagnosticCode.DATASET_SCHEMA_INVALID


def test_solar_term_lookup_rejects_non_datetime_input() -> None:
    with pytest.raises(TypeError, match="resolved_local_datetime"):
        solar_term_for_datetime("2026-02-04T00:00:00", RuleRegistry(allow_unverified=True))  # type: ignore[arg-type]
