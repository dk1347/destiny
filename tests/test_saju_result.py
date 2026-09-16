from datetime import date, datetime, timedelta, timezone

from destiny_saju.data_registry import RuleRegistry
from destiny_saju.saju_result import saju_result_for_date, saju_result_for_datetime


def test_result_preserves_profile_and_loaded_rule_versions() -> None:
    result = saju_result_for_datetime(
        datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9))),
        RuleRegistry(allow_unverified=True),
    )
    assert result.status == "complete"
    assert result.calculation_profile_id == "kr_standard_v1"
    assert ("core_tables_v1", "1.0.0") in result.dataset_versions
    assert ("solar_term_instants_v1", "1.0.0") in result.dataset_versions
    assert result.as_dict()["pillars"]["year"] == {"stem": "byeong", "branch": "o"}
    assert result.as_dict()["provenance"]["solar_term_instants_v1"] == "1.0.0"


def test_date_only_result_omits_hour_without_inventing_a_time() -> None:
    result = saju_result_for_date(date(2026, 2, 5), RuleRegistry(allow_unverified=True))
    assert result.status == "partial"
    assert result.as_dict()["pillars"]["hour"] is None
    assert result.as_dict()["warnings"] == ["출생시간이 없어 시주는 포함하지 않았어요."]
