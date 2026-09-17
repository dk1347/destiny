from datetime import datetime, timedelta, timezone

import pytest

from destiny_saju.data_registry import RuleRegistry
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
    serialized = annual.as_dict()
    assert serialized["pillar"] == {"stem": "byeong", "branch": "o"}
    assert any("seun_branch" in relation["participants"] for relation in serialized["relations"])
    assert serialized["provenance"]["solar_term_instants_v1"] == "2.0.0"
    assert serialized["provenance"]["relations_v1"] == "1.0.0"


def test_seun_is_available_when_all_required_production_data_is_verified() -> None:
    registry = RuleRegistry()
    natal = four_pillars_for_datetime(datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)

    annual = seun_for_datetime(natal, datetime(2026, 2, 4, 5, 2, tzinfo=KST), registry)

    assert annual.pillar.branch.value == "o"
