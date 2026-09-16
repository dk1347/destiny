"""Annual-cycle facts built from the verified year-pillar boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .calculation_profile import CalculationProfile, KR_STANDARD_V1
from .data_registry import RuleRegistry
from .four_pillars import FourPillars
from .relations import RelationFinding, relations_for_values
from .year_pillar import YearPillar, year_pillar_for_datetime


@dataclass(frozen=True)
class Seun:
    """The annual pillar at one target local instant and structural relations."""

    calendar_year: int
    calculation_profile_id: str
    pillar: YearPillar
    relations: tuple[RelationFinding, ...]


def seun_for_datetime(
    natal_pillars: FourPillars,
    target_local_datetime: datetime,
    registry: RuleRegistry,
    profile: CalculationProfile = KR_STANDARD_V1,
) -> Seun:
    """Return a target instant's annual pillar and facts relative to natal pillars.

    The annual boundary is the same verified Ipchun boundary used for a year
    pillar. This function does not assign luck, priority, or an interpretation.
    """

    if not isinstance(natal_pillars, FourPillars):
        raise TypeError("natal_pillars must be a FourPillars instance")
    if type(target_local_datetime) is not datetime:
        raise TypeError("target_local_datetime must be a datetime.datetime instance")
    if not isinstance(profile, CalculationProfile):
        raise TypeError("profile must be a CalculationProfile instance")

    pillar = year_pillar_for_datetime(target_local_datetime, registry)
    relations = relations_for_values(
        (("year_stem", natal_pillars.year.stem.value), ("month_stem", natal_pillars.month.stem.value),
         ("day_stem", natal_pillars.day.stem.value), ("hour_stem", natal_pillars.hour.stem.value),
         ("seun_stem", pillar.stem.value)),
        (("year_branch", natal_pillars.year.branch.value), ("month_branch", natal_pillars.month.branch.value),
         ("day_branch", natal_pillars.day.branch.value), ("hour_branch", natal_pillars.hour.branch.value),
         ("seun_branch", pillar.branch.value)),
        registry,
    )
    return Seun(target_local_datetime.year, profile.profile_id, pillar, relations)
