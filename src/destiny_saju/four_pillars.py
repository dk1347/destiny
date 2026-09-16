"""Compose the four Saju pillars from one resolved local datetime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .day_pillar import DayPillar, day_pillar_for_date
from .data_registry import RuleRegistry
from .hour_branch import hour_branch_for_time
from .hour_stem import hour_stem_for
from .month_pillar import MonthPillar, month_pillar_for_datetime
from .stems import HeavenlyStem
from .branches import EarthlyBranch
from .year_pillar import YearPillar, year_pillar_for_datetime


@dataclass(frozen=True)
class HourPillar:
    stem: HeavenlyStem
    branch: EarthlyBranch


@dataclass(frozen=True)
class FourPillars:
    year: YearPillar
    month: MonthPillar
    day: DayPillar
    hour: HourPillar


def four_pillars_for_datetime(resolved_local_datetime: datetime, registry: RuleRegistry) -> FourPillars:
    """Calculate every pillar from one already-resolved Asia/Seoul datetime."""

    if type(resolved_local_datetime) is not datetime:
        raise TypeError("resolved_local_datetime must be a datetime.datetime instance")
    year = year_pillar_for_datetime(resolved_local_datetime, registry)
    month = month_pillar_for_datetime(resolved_local_datetime, registry)
    # Saju day pillars change at the beginning of ja hour (23:00), not at
    # civil midnight.  Year and month continue to use the resolved civil
    # instant, while the day and hour stem use this adjusted date.
    pillar_date = resolved_local_datetime.date()
    if resolved_local_datetime.hour >= 23:
        pillar_date += timedelta(days=1)
    day = day_pillar_for_date(pillar_date, registry)
    hour_branch = hour_branch_for_time(resolved_local_datetime.timetz())
    hour = HourPillar(hour_stem_for(day.stem, hour_branch, registry), hour_branch)
    return FourPillars(year, month, day, hour)
