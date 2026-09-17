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


def test_2026_solar_term_table_matches_the_recorded_official_kst_audit() -> None:
    registry = RuleRegistry(allow_unverified=True)
    terms = registry.load("solar_term_instants_v1")["data"]["terms"]
    published_2026_terms = (
        ("sohan", "2026-01-05T17:23:00+09:00"),
        ("daehan", "2026-01-20T10:45:00+09:00"),
        ("ipchun", "2026-02-04T05:02:00+09:00"),
        ("usu", "2026-02-19T00:52:00+09:00"),
        ("gyeongchip", "2026-03-05T22:59:00+09:00"),
        ("chunbun", "2026-03-20T23:46:00+09:00"),
        ("cheongmyeong", "2026-04-05T03:40:00+09:00"),
        ("gogu", "2026-04-20T10:39:00+09:00"),
        ("ipha", "2026-05-05T20:49:00+09:00"),
        ("soman", "2026-05-21T09:37:00+09:00"),
        ("mangjong", "2026-06-06T00:48:00+09:00"),
        ("haji", "2026-06-21T17:25:00+09:00"),
        ("soseo", "2026-07-07T10:57:00+09:00"),
        ("daeseo", "2026-07-23T04:13:00+09:00"),
        ("ipchu", "2026-08-07T20:43:00+09:00"),
        ("cheoseo", "2026-08-23T11:19:00+09:00"),
        ("baengno", "2026-09-07T23:41:00+09:00"),
        ("chubun", "2026-09-23T09:05:00+09:00"),
        ("hallo", "2026-10-08T15:29:00+09:00"),
        ("sanggang", "2026-10-23T18:38:00+09:00"),
        ("ipdong", "2026-11-07T18:52:00+09:00"),
        ("soseol", "2026-11-22T16:23:00+09:00"),
        ("daeseol", "2026-12-07T11:53:00+09:00"),
        ("dongji", "2026-12-22T05:50:00+09:00"),
    )

    recorded_2026_terms = tuple(
        (term["id"], term["occurs_at"])
        for term in terms
        if term["occurs_at"].startswith("2026-")
    )

    assert recorded_2026_terms == published_2026_terms


def test_every_verified_solar_term_observes_its_boundary() -> None:
    registry = RuleRegistry(allow_unverified=True)
    data = registry.load("solar_term_instants_v1")["data"]
    terms = data["terms"]
    coverage_start = datetime.fromisoformat(data["coverage_ranges"][0]["coverage_start"])

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
    for outside_coverage in (
        datetime(2025, 12, 31, 23, 59, tzinfo=timezone(timedelta(hours=9))),
        datetime(2027, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=9))),
    ):
        with pytest.raises(DatasetError, match="SOLAR_TERM_DATA_UNAVAILABLE"):
            solar_term_for_datetime(outside_coverage, registry)
    assert solar_term_for_datetime(
        datetime(2026, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=9))),
        registry,
    ).id == "dongji"
    assert solar_term_for_datetime(
        datetime(2026, 12, 31, 23, 59, tzinfo=timezone(timedelta(hours=9))),
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


def test_solar_term_dataset_rejects_a_stale_pre_coverage_boundary() -> None:
    source = files("destiny_saju.data.saju")
    with tempfile.TemporaryDirectory() as temporary:
        target = Path(temporary)
        for resource in source.iterdir():
            if resource.name.endswith(".json"):
                (target / resource.name).write_bytes(resource.read_bytes())
        path = target / "solar_term_instants_v1.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["data"]["terms"][0]["occurs_at"] = "2024-12-07T06:05:00+09:00"
        payload["data"]["terms"][1]["occurs_at"] = "2024-12-22T00:03:00+09:00"
        path.write_text(json.dumps(payload), encoding="utf-8")

        with pytest.raises(DatasetError) as error:
            RuleRegistry(target, allow_unverified=True).load("solar_term_instants_v1")
        assert error.value.code is DiagnosticCode.DATASET_SCHEMA_INVALID


def test_solar_term_lookup_rejects_non_datetime_input() -> None:
    with pytest.raises(TypeError, match="resolved_local_datetime"):
        solar_term_for_datetime("2026-02-04T00:00:00", RuleRegistry(allow_unverified=True))  # type: ignore[arg-type]


def _payload_with_second_range() -> dict:
    source = files("destiny_saju.data.saju").joinpath("solar_term_instants_v1.json")
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["data"]["coverage_ranges"].append(
        {
            "coverage_start": "2028-01-01T00:00:00+09:00",
            "coverage_end": "2028-01-31T23:59:00+09:00",
            "provenance": {
                "publisher": "test fixture only",
                "reference": "non-production contract fixture",
                "retrieved_on": "2026-09-18",
                "precision": "minute",
            },
        }
    )
    payload["data"]["terms"].extend(
        [
            {"id": "sohan", "occurs_at": "2027-12-20T10:00:00+09:00"},
            {"id": "daehan", "occurs_at": "2028-01-05T10:00:00+09:00"},
            {"id": "ipchun", "occurs_at": "2028-01-20T10:00:00+09:00"},
        ]
    )
    return payload


def _registry_for_payload(payload: dict) -> RuleRegistry:
    source = files("destiny_saju.data.saju")
    temporary = tempfile.TemporaryDirectory()
    target = Path(temporary.name)
    for resource in source.iterdir():
        if resource.name.endswith(".json"):
            (target / resource.name).write_bytes(resource.read_bytes())
    (target / "solar_term_instants_v1.json").write_text(json.dumps(payload), encoding="utf-8")
    registry = RuleRegistry(target, allow_unverified=True)
    registry._test_temporary_directory = temporary  # type: ignore[attr-defined]
    return registry


def test_solar_term_dataset_rejects_missing_range_provenance() -> None:
    payload = _payload_with_second_range()
    del payload["data"]["coverage_ranges"][0]["provenance"]
    with pytest.raises(DatasetError) as error:
        _registry_for_payload(payload).load("solar_term_instants_v1")
    assert error.value.code is DiagnosticCode.DATASET_SCHEMA_INVALID


def test_solar_term_dataset_rejects_overlapping_ranges() -> None:
    payload = _payload_with_second_range()
    payload["data"]["coverage_ranges"][1]["coverage_start"] = "2026-12-31T23:59:00+09:00"
    with pytest.raises(DatasetError) as error:
        _registry_for_payload(payload).load("solar_term_instants_v1")
    assert error.value.code is DiagnosticCode.DATASET_SCHEMA_INVALID


def test_solar_term_dataset_rejects_non_kst_range_bounds() -> None:
    payload = _payload_with_second_range()
    payload["data"]["coverage_ranges"][1]["coverage_start"] = "2028-01-01T00:00:00+00:00"
    with pytest.raises(DatasetError) as error:
        _registry_for_payload(payload).load("solar_term_instants_v1")
    assert error.value.code is DiagnosticCode.DATASET_SCHEMA_INVALID


def test_solar_term_dataset_rejects_term_outside_declared_ranges() -> None:
    payload = _payload_with_second_range()
    payload["data"]["terms"].append({"id": "usu", "occurs_at": "2028-02-04T10:00:00+09:00"})
    with pytest.raises(DatasetError) as error:
        _registry_for_payload(payload).load("solar_term_instants_v1")
    assert error.value.code is DiagnosticCode.DATASET_SCHEMA_INVALID


def test_solar_term_lookup_fails_closed_in_a_verified_range_gap() -> None:
    registry = _registry_for_payload(_payload_with_second_range())
    with pytest.raises(DatasetError) as error:
        solar_term_for_datetime(datetime(2027, 6, 15, 12, 0, tzinfo=timezone(timedelta(hours=9))), registry)
    assert error.value.code is DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE


def test_second_range_ipchun_boundary_and_month_pillar() -> None:
    from destiny_saju.month_pillar import month_pillar_for_datetime

    registry = _registry_for_payload(_payload_with_second_range())
    ipchun = datetime(2028, 1, 20, 10, 0, tzinfo=timezone(timedelta(hours=9)))
    assert solar_term_for_datetime(ipchun - timedelta(minutes=1), registry).id == "daehan"
    assert solar_term_for_datetime(ipchun, registry).id == "ipchun"
    assert month_pillar_for_datetime(ipchun, registry).branch.value == "in"
