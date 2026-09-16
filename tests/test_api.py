from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from destiny_saju.api import CalculationRequest, SeunRequest, calculate, calculate_seun


def test_api_rejects_non_kst_datetime() -> None:
    with pytest.raises(HTTPException) as error:
        calculate(CalculationRequest(birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone.utc)))
    assert error.value.status_code == 422


def test_api_rejects_unknown_profile() -> None:
    with pytest.raises(HTTPException) as error:
        calculate(CalculationRequest(birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9))), calculation_profile_id="unknown"))
    assert error.value.status_code == 422


def test_api_returns_a_production_result_when_required_pillar_data_is_verified() -> None:
    result = calculate(CalculationRequest(
        birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9))),
    ))
    assert result["status"] == "complete"
    assert result["pillars"]["year"] == {"stem": "byeong", "branch": "o"}
    assert result["provenance"]["month_stem_rules_v1"] == "1.0.0"


def test_seun_api_rejects_a_non_kst_target_datetime() -> None:
    with pytest.raises(HTTPException) as error:
        calculate_seun(SeunRequest(
            birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9))),
            target_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone.utc),
        ))
    assert error.value.status_code == 422
    assert error.value.detail["code"] == "INVALID_LOCAL_DATETIME"


def test_seun_api_rejects_an_unknown_profile() -> None:
    with pytest.raises(HTTPException) as error:
        calculate_seun(SeunRequest(
            birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9))),
            target_local_datetime=datetime(2026, 3, 1, 12, 0, tzinfo=timezone(timedelta(hours=9))),
            calculation_profile_id="unknown",
        ))
    assert error.value.status_code == 422
    assert error.value.detail["code"] == "UNKNOWN_CALCULATION_PROFILE"


def test_seun_api_returns_structural_production_result() -> None:
    result = calculate_seun(SeunRequest(
        birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9))),
        target_local_datetime=datetime(2026, 3, 1, 12, 0, tzinfo=timezone(timedelta(hours=9))),
    ))
    assert result["pillar"] == {"stem": "byeong", "branch": "o"}
    assert result["calculation_profile_id"] == "kr_standard_v1"
    assert result["provenance"]["relations_v1"] == "1.0.0"
