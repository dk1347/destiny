"""Fortune-cycle (대운) count, direction and exchange instants.

The conventional count divides the distance between birth and the neighbouring
절입 by three. This module keeps the *whole* derivation — the raw day
difference and the undivided float — next to the rounded integer that is shown
to a user, so a later change in convention can be re-derived from stored data
instead of being recalculated from the birth record.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum

from ..branches import EarthlyBranch
from ..data_registry import DatasetError, RuleRegistry
from ..diagnostics import DiagnosticCode
from ..month_pillar import MonthPillar
from ..stems import HeavenlyStem
from ..tables import ordered_branches, ordered_stems, stem_attributes
from ..year_pillar import YearPillar
from .timeline import major_solar_terms

DAEWUN_METHOD_ID = "daewun_three_day_one_year_v1"

#: Days per year used to turn the fractional count into an exchange instant.
#: The Gregorian mean year is used so the conversion is exactly reproducible.
MEAN_YEAR_DAYS = 365.2425

#: Days of separation that the convention treats as one year of age.
DAYS_PER_FORTUNE_YEAR = 3

DEFAULT_CYCLE_COUNT = 9
SEXAGENARY_CYCLE_LENGTH = 60


class DaewunDirection(StrEnum):
    FORWARD = "forward"
    BACKWARD = "backward"


@dataclass(frozen=True)
class DaewunCycle:
    """One ten-year fortune cycle and the instant it takes over."""

    sequence: int
    stem: HeavenlyStem
    branch: EarthlyBranch
    starts_at: datetime
    start_age_display: int
    start_age_years: float


@dataclass(frozen=True)
class Daewun:
    """A complete fortune-cycle derivation with its inputs preserved."""

    method_id: str
    direction: DaewunDirection
    boundary_term_id: str
    boundary_instant: datetime
    source_day_difference: float
    daewun_raw_float: float
    daewun_number: int
    first_exchange_at: datetime
    cycles: tuple[DaewunCycle, ...]
    is_anchor_approximate: bool


def daewun_direction_for(year_stem: HeavenlyStem, gender: str, registry: RuleRegistry) -> DaewunDirection:
    """Apply 양남음녀 순행 / 음남양녀 역행 to the year stem's polarity."""

    if gender not in {"male", "female"}:
        raise ValueError("daewun direction needs a recorded gender of 'male' or 'female'")
    is_yang = stem_attributes(year_stem, registry).yin_yang == "yang"
    forward = is_yang == (gender == "male")
    return DaewunDirection.FORWARD if forward else DaewunDirection.BACKWARD


def daewun_for(
    birth_instant: datetime,
    year_pillar: YearPillar,
    month_pillar: MonthPillar,
    gender: str,
    registry: RuleRegistry,
    *,
    is_anchor_approximate: bool = False,
    cycle_count: int = DEFAULT_CYCLE_COUNT,
) -> Daewun:
    """Derive the fortune-cycle count and every cycle's exchange instant."""

    if type(birth_instant) is not datetime or birth_instant.tzinfo is None:
        raise TypeError("birth_instant must be a timezone-aware datetime")
    if cycle_count < 1:
        raise ValueError("cycle_count must be at least 1")

    direction = daewun_direction_for(year_pillar.stem, gender, registry)
    boundary = _boundary_term(birth_instant, direction, registry)

    source_day_difference = abs(boundary.occurs_at - birth_instant).total_seconds() / 86400
    raw_float = source_day_difference / DAYS_PER_FORTUNE_YEAR
    number = round_daewun_number(raw_float)

    first_exchange_at = birth_instant + timedelta(days=raw_float * MEAN_YEAR_DAYS)
    start_index = _sexagenary_index(month_pillar.stem, month_pillar.branch, registry)
    step = 1 if direction is DaewunDirection.FORWARD else -1
    stems = ordered_stems(registry)
    branches = ordered_branches(registry)

    cycles = tuple(
        DaewunCycle(
            sequence=sequence,
            stem=stems[(start_index + step * sequence) % 10],
            branch=branches[(start_index + step * sequence) % 12],
            starts_at=birth_instant + timedelta(
                days=(raw_float + 10 * (sequence - 1)) * MEAN_YEAR_DAYS
            ),
            start_age_display=number + 10 * (sequence - 1),
            start_age_years=raw_float + 10 * (sequence - 1),
        )
        for sequence in range(1, cycle_count + 1)
    )

    return Daewun(
        method_id=DAEWUN_METHOD_ID,
        direction=direction,
        boundary_term_id=boundary.id,
        boundary_instant=boundary.occurs_at,
        source_day_difference=source_day_difference,
        daewun_raw_float=raw_float,
        daewun_number=number,
        first_exchange_at=first_exchange_at,
        cycles=cycles,
        is_anchor_approximate=is_anchor_approximate,
    )


def _boundary_term(birth_instant: datetime, direction: DaewunDirection, registry: RuleRegistry):
    terms = major_solar_terms(registry)
    if direction is DaewunDirection.FORWARD:
        candidates = [term for term in terms if term.occurs_at > birth_instant]
        boundary = candidates[0] if candidates else None
    else:
        candidates = [term for term in terms if term.occurs_at <= birth_instant]
        boundary = candidates[-1] if candidates else None
    if boundary is None:
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            f"대운수 계산에 필요한 {direction.value} 방향 절입 시각이 검증 범위 밖이에요.",
        )
    return boundary


def round_daewun_number(value: float) -> int:
    """Round with 사사오입 and clamp to the 1..10 range shown to users."""

    rounded = int(Decimal(repr(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return min(10, max(1, rounded))


def _sexagenary_index(stem: HeavenlyStem, branch: EarthlyBranch, registry: RuleRegistry) -> int:
    stems = ordered_stems(registry)
    branches = ordered_branches(registry)
    stem_index = stems.index(stem)
    for index in range(SEXAGENARY_CYCLE_LENGTH):
        if index % 10 == stem_index and branches[index % 12] is branch:
            return index
    raise ValueError("stem and branch do not form a sexagenary pair")
