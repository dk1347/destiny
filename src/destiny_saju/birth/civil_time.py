"""Korean historical civil-time rules applied to a recorded birth clock time.

Scope follows ``docs/53_KOREAN_HISTORICAL_CIVIL_TIME_POLICY.md``: this module
resolves the *legal civil time* that a Korean clock showed on a given date, and
the fixed standard-meridian correction used by the Saju convention. It does not
implement true solar time (``docs/54_TRUE_SOLAR_TIME_OPTION_SPEC.md``).

Two distinct numbers are produced for one date:

``utc_offset_minutes``
    What the wall clock was actually offset from UTC on that date, used to
    reconstruct the absolute instant of birth.
``meridian_offset_minutes``
    The signed correction from the civil clock to the Saju calculation basis
    (``-30`` while Korea used the 135°E meridian, ``0`` while it used 127.5°E).

Every period boundary below is **inclusive of both its start and end date**;
the tables are deliberately date-granular, so a clock change that happened at
an intraday hour is reported through ``DST_BOUNDARY_DATE_APPROXIMATE`` instead
of being silently resolved.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import StrEnum

UTC = timezone.utc
KST = timezone(timedelta(hours=9))

CIVIL_TIME_POLICY_ID = "kr_civil_time_v1"

MERIDIAN_127_5_UTC_OFFSET_MINUTES = 8 * 60 + 30
MERIDIAN_135_UTC_OFFSET_MINUTES = 9 * 60
MERIDIAN_135_CORRECTION_MINUTES = -30
MERIDIAN_127_5_CORRECTION_MINUTES = 0
DST_CORRECTION_MINUTES = -60

#: Korea's first documented standard time. Anything earlier is out of range.
FIRST_DOCUMENTED_STANDARD_TIME_DATE = date(1908, 4, 1)


class CivilTimeRuleId(StrEnum):
    """Traceable ids recorded in ``NormalizedBirthProfile.applied_rule_ids``."""

    MERIDIAN_127_5_NO_OFFSET = "MERIDIAN_127_5_NO_OFFSET"
    MERIDIAN_135_OFFSET_MINUS_30 = "MERIDIAN_135_OFFSET_MINUS_30"
    MERIDIAN_OUT_OF_RANGE_NO_OFFSET = "MERIDIAN_OUT_OF_RANGE_NO_OFFSET"
    DST_APPLIED_MINUS_60 = "DST_APPLIED_MINUS_60"
    DST_BOUNDARY_DATE_APPROXIMATE = "DST_BOUNDARY_DATE_APPROXIMATE"
    SOLAR_DATE_SHIFTED_PREV = "SOLAR_DATE_SHIFTED_PREV"
    SOLAR_DATE_SHIFTED_NEXT = "SOLAR_DATE_SHIFTED_NEXT"


@dataclass(frozen=True)
class MeridianSegment:
    """One period during which a single standard meridian was in legal use."""

    start_date: date | None
    end_date: date | None
    utc_offset_minutes: int
    meridian_offset_minutes: int
    rule_id: CivilTimeRuleId

    def covers(self, civil_date: date) -> bool:
        if self.start_date is not None and civil_date < self.start_date:
            return False
        if self.end_date is not None and civil_date > self.end_date:
            return False
        return True


@dataclass(frozen=True)
class DstPeriod:
    """One Korean summer-time period, inclusive of both dates.

    ``end_date`` is the last date treated as summer time, not the date on which
    the clock returned. ``intraday_transition`` marks the 1987/1988 periods,
    whose clocks changed at 02:00 and 03:00 rather than at midnight; for those
    the date-granular table cannot be exact near the boundary.
    """

    start_date: date
    end_date: date
    intraday_transition: bool = False

    def covers(self, civil_date: date) -> bool:
        return self.start_date <= civil_date <= self.end_date

    def is_boundary_date(self, civil_date: date) -> bool:
        """Report a date whose exact summer-time status is not date-decidable."""

        if not self.intraday_transition:
            return False
        return civil_date in {self.start_date, self.end_date + timedelta(days=1)}


# Sources: National Archives summer-time history and the IANA `Asia/Seoul` zone
# (docs/53_KOREAN_HISTORICAL_CIVIL_TIME_POLICY.md). 127.5°E = UTC+08:30,
# 135°E = UTC+09:00.
MERIDIAN_SEGMENTS: tuple[MeridianSegment, ...] = (
    MeridianSegment(
        date(1908, 4, 1), date(1911, 12, 31),
        MERIDIAN_127_5_UTC_OFFSET_MINUTES, MERIDIAN_127_5_CORRECTION_MINUTES,
        CivilTimeRuleId.MERIDIAN_127_5_NO_OFFSET,
    ),
    MeridianSegment(
        date(1912, 1, 1), date(1954, 3, 20),
        MERIDIAN_135_UTC_OFFSET_MINUTES, MERIDIAN_135_CORRECTION_MINUTES,
        CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30,
    ),
    MeridianSegment(
        date(1954, 3, 21), date(1961, 8, 9),
        MERIDIAN_127_5_UTC_OFFSET_MINUTES, MERIDIAN_127_5_CORRECTION_MINUTES,
        CivilTimeRuleId.MERIDIAN_127_5_NO_OFFSET,
    ),
    MeridianSegment(
        date(1961, 8, 10), None,
        MERIDIAN_135_UTC_OFFSET_MINUTES, MERIDIAN_135_CORRECTION_MINUTES,
        CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30,
    ),
)

# Before 1908-04-01 Seoul kept local mean time (UTC+08:27:52 in the IANA zone).
# No meridian correction is claimed for that range; UTC+08:30 is used only as
# the nearest documented civil offset so an instant can still be reconstructed.
OUT_OF_RANGE_SEGMENT = MeridianSegment(
    None, date(1908, 3, 31),
    MERIDIAN_127_5_UTC_OFFSET_MINUTES, 0,
    CivilTimeRuleId.MERIDIAN_OUT_OF_RANGE_NO_OFFSET,
)

# Summer time ran 1948–1951 and 1987–1988 on the 135°E basis, and 1955–1960 on
# the 127.5°E basis. Each `end_date` is the last full day under summer time.
DST_PERIODS: tuple[DstPeriod, ...] = (
    DstPeriod(date(1948, 6, 1), date(1948, 9, 12)),
    DstPeriod(date(1949, 4, 3), date(1949, 9, 10)),
    DstPeriod(date(1950, 4, 1), date(1950, 9, 9)),
    DstPeriod(date(1951, 5, 6), date(1951, 9, 8)),
    DstPeriod(date(1955, 5, 5), date(1955, 9, 8)),
    DstPeriod(date(1956, 5, 20), date(1956, 9, 29)),
    DstPeriod(date(1957, 5, 5), date(1957, 9, 21)),
    DstPeriod(date(1958, 5, 4), date(1958, 9, 20)),
    DstPeriod(date(1959, 5, 3), date(1959, 9, 19)),
    DstPeriod(date(1960, 5, 1), date(1960, 9, 17)),
    DstPeriod(date(1987, 5, 10), date(1987, 10, 10), intraday_transition=True),
    DstPeriod(date(1988, 5, 8), date(1988, 10, 8), intraday_transition=True),
)


@dataclass(frozen=True)
class CivilTimeResolution:
    """The civil-time facts that apply to one Korean calendar date."""

    civil_date: date
    utc_offset_minutes: int
    dst_offset_minutes: int
    meridian_offset_minutes: int
    historical_dst_applied: bool
    applied_rule_ids: tuple[str, ...]
    policy_id: str = CIVIL_TIME_POLICY_ID

    @property
    def total_correction_minutes(self) -> int:
        """The signed minutes added to the civil clock to reach the basis time."""

        return self.dst_offset_minutes + self.meridian_offset_minutes


def meridian_segment_for(civil_date: date) -> MeridianSegment:
    """Return the standard-meridian segment in force on ``civil_date``."""

    _require_date(civil_date)
    for segment in MERIDIAN_SEGMENTS:
        if segment.covers(civil_date):
            return segment
    return OUT_OF_RANGE_SEGMENT


def dst_period_for(civil_date: date) -> DstPeriod | None:
    """Return the summer-time period covering ``civil_date``, if any."""

    _require_date(civil_date)
    for period in DST_PERIODS:
        if period.covers(civil_date):
            return period
    return None


def resolve_civil_time(civil_date: date) -> CivilTimeResolution:
    """Resolve UTC offset, summer time and meridian correction for one date."""

    _require_date(civil_date)
    segment = meridian_segment_for(civil_date)
    rule_ids: list[str] = [segment.rule_id.value]

    period = dst_period_for(civil_date)
    dst_offset_minutes = 0
    utc_offset_minutes = segment.utc_offset_minutes
    if period is not None:
        dst_offset_minutes = DST_CORRECTION_MINUTES
        utc_offset_minutes -= DST_CORRECTION_MINUTES
        rule_ids.append(CivilTimeRuleId.DST_APPLIED_MINUS_60.value)
    if _is_dst_boundary_date(civil_date):
        rule_ids.append(CivilTimeRuleId.DST_BOUNDARY_DATE_APPROXIMATE.value)

    return CivilTimeResolution(
        civil_date=civil_date,
        utc_offset_minutes=utc_offset_minutes,
        dst_offset_minutes=dst_offset_minutes,
        meridian_offset_minutes=segment.meridian_offset_minutes,
        historical_dst_applied=period is not None,
        applied_rule_ids=tuple(rule_ids),
    )


def adjusted_solar_datetime(
    civil_datetime: datetime, resolution: CivilTimeResolution
) -> datetime:
    """Apply summer-time and meridian corrections to a naive civil datetime.

    The result is naive on purpose: it is a calculation basis, not a civil
    clock reading, so labelling it with a UTC offset would assert an instant
    that ``normalized_utc_timestamp`` already records correctly.
    """

    _require_naive_datetime(civil_datetime)
    return civil_datetime + timedelta(minutes=resolution.total_correction_minutes)


def utc_timestamp_for(
    civil_datetime: datetime, resolution: CivilTimeResolution
) -> datetime:
    """Reconstruct the absolute UTC instant from the civil clock reading."""

    _require_naive_datetime(civil_datetime)
    return (civil_datetime - timedelta(minutes=resolution.utc_offset_minutes)).replace(tzinfo=UTC)


def _is_dst_boundary_date(civil_date: date) -> bool:
    return any(period.is_boundary_date(civil_date) for period in DST_PERIODS)


def _require_date(value: date) -> None:
    if not isinstance(value, date) or isinstance(value, datetime):
        raise TypeError("civil_date must be a datetime.date instance")


def _require_naive_datetime(value: datetime) -> None:
    if type(value) is not datetime:
        raise TypeError("civil_datetime must be a datetime.datetime instance")
    if value.tzinfo is not None:
        raise ValueError("civil_datetime must be a naive Korean civil clock reading")
