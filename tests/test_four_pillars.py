from datetime import datetime, timedelta, timezone

import pytest

from destiny_saju.branches import EarthlyBranch
from destiny_saju.calculation_profile import CalculationProfile, KR_STANDARD_V1, MIDNIGHT_V1
from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.four_pillars import four_pillars_for_datetime
from destiny_saju.stems import HeavenlyStem


KST = timezone(timedelta(hours=9))


def test_four_pillars_composes_a_verified_boundary_instant() -> None:
    result = four_pillars_for_datetime(
        datetime(2026, 2, 4, 5, 2, tzinfo=KST), RuleRegistry(allow_unverified=True)
    )

    assert (result.year.stem, result.year.branch) == (HeavenlyStem.BYEONG, EarthlyBranch.O)
    assert (result.month.stem, result.month.branch) == (HeavenlyStem.GYEONG, EarthlyBranch.IN)
    assert (result.day.stem, result.day.branch) == (HeavenlyStem.GI, EarthlyBranch.YU)
    assert (result.hour.stem, result.hour.branch) == (HeavenlyStem.JEONG, EarthlyBranch.MYO)


def test_four_pillars_preserves_the_solar_term_coverage_gate() -> None:
    with pytest.raises(DatasetError, match="SOLAR_TERM_DATA_UNAVAILABLE"):
        four_pillars_for_datetime(
            datetime(2027, 1, 1, 0, 0, tzinfo=KST), RuleRegistry(allow_unverified=True)
        )


@pytest.mark.parametrize("minute", [0, 30, 59])
def test_four_pillars_uses_the_next_day_pillar_at_ja_hour(minute: int) -> None:
    result = four_pillars_for_datetime(
        datetime(2026, 2, 4, 23, minute, tzinfo=KST), RuleRegistry(allow_unverified=True)
    )

    assert (result.day.stem, result.day.branch) == (HeavenlyStem.GYEONG, EarthlyBranch.SUL)
    assert result.hour.branch is EarthlyBranch.JA


def test_four_pillars_supports_a_midnight_day_boundary_profile() -> None:
    instant = datetime(2026, 2, 4, 23, 30, tzinfo=KST)
    registry = RuleRegistry(allow_unverified=True)

    default_result = four_pillars_for_datetime(instant, registry)
    explicit_default_result = four_pillars_for_datetime(instant, registry, KR_STANDARD_V1)
    midnight_result = four_pillars_for_datetime(instant, registry, MIDNIGHT_V1)

    assert explicit_default_result == default_result
    assert (default_result.day.stem, default_result.day.branch) == (HeavenlyStem.GYEONG, EarthlyBranch.SUL)
    assert (midnight_result.day.stem, midnight_result.day.branch) == (HeavenlyStem.GI, EarthlyBranch.YU)
    assert midnight_result.hour.branch is EarthlyBranch.JA


def test_calculation_profile_rejects_unknown_day_boundary() -> None:
    with pytest.raises(TypeError, match="day_boundary"):
        CalculationProfile("invalid", "midnight")  # type: ignore[arg-type]
