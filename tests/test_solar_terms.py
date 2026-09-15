from datetime import datetime

import pytest

from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.diagnostics import DiagnosticCode
from destiny_saju.solar_terms import solar_term_for_datetime


def test_solar_term_lookup_fails_closed_without_verified_instants() -> None:
    with pytest.raises(DatasetError) as error:
        solar_term_for_datetime(datetime(2026, 2, 4, 0, 0), RuleRegistry(allow_unverified=True))

    assert error.value.code is DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE


def test_solar_term_lookup_rejects_non_datetime_input() -> None:
    with pytest.raises(TypeError, match="resolved_local_datetime"):
        solar_term_for_datetime("2026-02-04T00:00:00", RuleRegistry(allow_unverified=True))  # type: ignore[arg-type]
