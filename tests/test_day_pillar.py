from datetime import date

import pytest

from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.day_pillar import day_pillar_for_date
from destiny_saju.diagnostics import DiagnosticCode


def test_day_pillar_fails_closed_without_a_verified_anchor() -> None:
    with pytest.raises(DatasetError) as error:
        day_pillar_for_date(date(2019, 1, 27), RuleRegistry(allow_unverified=True))

    assert error.value.code is DiagnosticCode.DAY_PILLAR_ANCHOR_UNAVAILABLE


def test_day_pillar_rejects_non_date_input_before_loading_data() -> None:
    with pytest.raises(TypeError, match="civil_date"):
        day_pillar_for_date("2019-01-27", RuleRegistry(allow_unverified=True))  # type: ignore[arg-type]
