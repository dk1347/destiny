from datetime import datetime, timedelta, timezone

import pytest

from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.four_pillars import four_pillars_for_datetime
from destiny_saju.seun import seun_for_datetime


KST = timezone(timedelta(hours=9))


def test_seun_uses_the_same_ipchun_boundary_as_the_year_pillar() -> None:
    registry = RuleRegistry(allow_unverified=True)
    natal = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)

    before_ipchun = seun_for_datetime(natal, datetime(2026, 2, 4, 5, 1, tzinfo=KST), registry)
    at_ipchun = seun_for_datetime(natal, datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)

    assert (before_ipchun.pillar.stem.value, before_ipchun.pillar.branch.value) == ("eul", "sa")
    assert (at_ipchun.pillar.stem.value, at_ipchun.pillar.branch.value) == ("byeong", "o")
    assert at_ipchun.calendar_year == 2026
    assert at_ipchun.calculation_profile_id == "kr_standard_v1"


def test_seun_relations_identify_the_annual_pillar_location_without_interpretation() -> None:
    registry = RuleRegistry(allow_unverified=True)
    natal = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)

    annual = seun_for_datetime(natal, datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)

    assert any(
        finding.relation_id == "branch-half-in-o" and "seun_branch" in finding.participants
        for finding in annual.relations
    )


def test_seun_fails_closed_when_required_production_data_is_unverified() -> None:
    registry = RuleRegistry(allow_unverified=True)
    natal = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)

    with pytest.raises(DatasetError, match="SOLAR_TERM_DATA_UNAVAILABLE"):
        seun_for_datetime(natal, datetime(2026, 2, 4, 5, 2, tzinfo=KST), RuleRegistry())
