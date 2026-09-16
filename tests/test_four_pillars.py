from datetime import datetime, timedelta, timezone

import pytest

from destiny_saju.branches import EarthlyBranch
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


def test_four_pillars_uses_the_next_day_pillar_at_ja_hour() -> None:
    result = four_pillars_for_datetime(
        datetime(2026, 2, 4, 23, 30, tzinfo=KST), RuleRegistry(allow_unverified=True)
    )

    assert (result.day.stem, result.day.branch) == (HeavenlyStem.GYEONG, EarthlyBranch.SUL)
    assert result.hour.branch is EarthlyBranch.JA
