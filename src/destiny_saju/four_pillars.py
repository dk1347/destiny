"""Compose the four Saju pillars from one resolved local datetime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from .calculation_profile import CalculationProfile, DayBoundary, KR_STANDARD_V1
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


@dataclass(frozen=True)
class ThreePillars:
    """A date-only result when year/month pillars are stable across the day."""

    year: YearPillar
    month: MonthPillar
    day: DayPillar


def four_pillars_for_datetime(
    resolved_local_datetime: datetime,
    registry: RuleRegistry,
    profile: CalculationProfile = KR_STANDARD_V1,
) -> FourPillars:
    """Calculate every pillar from one resolved Asia/Seoul datetime and profile."""

    if type(resolved_local_datetime) is not datetime:
        raise TypeError("resolved_local_datetime must be a datetime.datetime instance")
    if not isinstance(profile, CalculationProfile):
        raise TypeError("profile must be a CalculationProfile instance")
    year = year_pillar_for_datetime(resolved_local_datetime, registry)
    month = month_pillar_for_datetime(resolved_local_datetime, registry)
    pillar_date = resolved_local_datetime.date()
    if profile.day_boundary is DayBoundary.ZI_HOUR_START and resolved_local_datetime.hour >= 23:
        pillar_date += timedelta(days=1)
    day = day_pillar_for_date(pillar_date, registry)
    hour_branch = hour_branch_for_time(resolved_local_datetime.timetz())
    hour = HourPillar(hour_stem_for(day.stem, hour_branch, registry), hour_branch)
    return FourPillars(year, month, day, hour)


def three_pillars_for_date(local_date: date, registry: RuleRegistry) -> ThreePillars:
    """Return a safe date-only result, never inventing an unknown birth time."""

    if type(local_date) is not date:
        raise TypeError("local_date must be a datetime.date instance")
    kst = timezone(timedelta(hours=9))
    start = datetime.combine(local_date, time.min, kst)
    end = datetime.combine(local_date, time(23, 59), kst)
    start_year, end_year = year_pillar_for_datetime(start, registry), year_pillar_for_datetime(end, registry)
    start_month, end_month = month_pillar_for_datetime(start, registry), month_pillar_for_datetime(end, registry)
    if (start_year, start_month) != (end_year, end_month):
        raise ValueError("이 날짜는 절기 전환일이라 검증된 결과를 위해 출생시간이 필요해요.")
    return ThreePillars(start_year, start_month, day_pillar_for_date(local_date, registry))
