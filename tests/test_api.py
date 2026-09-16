from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from destiny_saju.api import CalculationRequest, calculate


def test_api_rejects_non_kst_datetime() -> None:
    with pytest.raises(HTTPException) as error:
        calculate(CalculationRequest(birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone.utc)))
    assert error.value.status_code == 422


def test_api_rejects_unknown_profile() -> None:
    with pytest.raises(HTTPException) as error:
        calculate(CalculationRequest(birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9))), calculation_profile_id="unknown"))
    assert error.value.status_code == 422


def test_api_fails_closed_when_production_data_is_not_verified() -> None:
    with pytest.raises(HTTPException) as error:
        calculate(CalculationRequest(birth_local_datetime=datetime(2026, 2, 4, 5, 2, tzinfo=timezone(timedelta(hours=9)))) )
    assert error.value.status_code == 503
    assert error.value.detail["code"] == "SOLAR_TERM_DATA_UNAVAILABLE"
