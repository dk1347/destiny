"""Normalize a raw birth input into an auditable ``NormalizedBirthProfile``.

Implements ``docs/03_BIRTH_PROFILE_SPEC.md`` under three standing rules:

1. The raw input is preserved unchanged on the profile.
2. Nothing is guessed. An unknown birth time never becomes a made-up clock
   time, and an unresolvable leap month becomes explicit candidate profiles
   instead of a silent default.
3. Every applied decision leaves a rule id behind in ``applied_rule_ids``.

Lunar input is converted through the :class:`LunarCalendarPort` protocol so the
verified KASI conversion dataset (``docs/52_LUNAR_INPUT_AND_CONVERSION_SPEC.md``)
can be attached later without changing this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from enum import StrEnum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from .civil_time import (
    CIVIL_TIME_POLICY_ID,
    KST,
    CivilTimeRuleId,
    adjusted_solar_datetime,
    resolve_civil_time,
    utc_timestamp_for,
)

BASE_TIMEZONE = "Asia/Seoul"

#: Accepted spellings for "the birth time was never recorded".
UNKNOWN_TIME_TOKENS = frozenset({"", "unknown", "모름", "미상", "시간모름", "시간미상"})


class BirthDiagnosticCode(StrEnum):
    """Stable codes carried by every birth-normalization error."""

    INVALID_CALENDAR_TYPE = "INVALID_CALENDAR_TYPE"
    INVALID_GENDER = "INVALID_GENDER"
    INVALID_BIRTH_DATE = "INVALID_BIRTH_DATE"
    INVALID_BIRTH_TIME = "INVALID_BIRTH_TIME"
    INVALID_LEAP_MONTH = "INVALID_LEAP_MONTH"
    LEAP_MONTH_NOT_APPLICABLE = "LEAP_MONTH_NOT_APPLICABLE"
    INVALID_LUNAR_DATE = "INVALID_LUNAR_DATE"
    LUNAR_CALENDAR_DATA_UNAVAILABLE = "LUNAR_CALENDAR_DATA_UNAVAILABLE"


class BirthRuleId(StrEnum):
    """Normalization rule ids that are not civil-time rules."""

    LEAP_MONTH_USER_SELECTED = "LEAP_MONTH_USER_SELECTED"
    LEAP_MONTH_AUTO_FALSE = "LEAP_MONTH_AUTO_FALSE"
    LEAP_MONTH_CANDIDATE_BRANCH = "LEAP_MONTH_CANDIDATE_BRANCH"
    LEAP_MONTH_CANDIDATE_ORDINARY = "LEAP_MONTH_CANDIDATE_ORDINARY"
    LEAP_MONTH_CANDIDATE_LEAP = "LEAP_MONTH_CANDIDATE_LEAP"
    LUNAR_CONVERTED_TO_SOLAR = "LUNAR_CONVERTED_TO_SOLAR"
    TIME_UNKNOWN_NO_ADJUSTMENT = "TIME_UNKNOWN_NO_ADJUSTMENT"
    TIME_UNKNOWN_THREE_PILLARS = "TIME_UNKNOWN_THREE_PILLARS"


class CalendarType(StrEnum):
    SOLAR = "solar"
    LUNAR = "lunar"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class TimePrecision(StrEnum):
    MINUTE = "minute"
    UNKNOWN = "unknown"


class AnalysisMode(StrEnum):
    FOUR_PILLARS = "FOUR_PILLARS"
    THREE_PILLARS = "THREE_PILLARS"


class ResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    CANDIDATE_BRANCH = "CANDIDATE_BRANCH"


class BirthProfileError(ValueError):
    """Base class for every rejected birth input."""

    def __init__(self, code: BirthDiagnosticCode, message: str) -> None:
        super().__init__(f"{code.value}: {message}")
        self.code = code


class InvalidCalendarTypeError(BirthProfileError):
    pass


class InvalidGenderError(BirthProfileError):
    pass


class InvalidBirthDateError(BirthProfileError):
    pass


class InvalidBirthTimeError(BirthProfileError):
    pass


class InvalidLeapMonthException(BirthProfileError):
    """A leap month was claimed for a month that has none, or for a solar date."""


class InvalidLunarDateError(BirthProfileError):
    """The lunar date does not exist in the conversion dataset."""


class LunarCalendarUnavailableError(BirthProfileError):
    """No verified conversion dataset is available for the requested date."""


@runtime_checkable
class LunarCalendarPort(Protocol):
    """The conversion dataset this module needs, and nothing more.

    Implementations must be offline datasets. A live request to KASI during a
    user's calculation is explicitly excluded by the lunar conversion spec.
    """

    @property
    def dataset_id(self) -> str:
        """Versioned id of the conversion dataset, recorded for provenance."""

    def has_leap_month(self, lunar_year: int, lunar_month: int) -> bool:
        """Report whether the given lunar month also exists as a leap month."""

    def to_solar_date(
        self, lunar_year: int, lunar_month: int, lunar_day: int, is_leap_month: bool
    ) -> date:
        """Convert one lunar date, raising ``InvalidLunarDateError`` if absent."""


@dataclass(frozen=True)
class RawBirthInput:
    """Exactly what the user submitted, validated but never rewritten."""

    calendar_type: CalendarType
    birth_year: int
    birth_month: int
    birth_day: int
    birth_time_str: str | None = None
    is_leap_month: bool | None = None
    gender: Gender = Gender.UNKNOWN
    location_text: str = ""

    def __post_init__(self) -> None:
        try:
            calendar_type = CalendarType(self.calendar_type)
        except ValueError as error:
            raise InvalidCalendarTypeError(
                BirthDiagnosticCode.INVALID_CALENDAR_TYPE,
                "calendar_type must be 'solar' or 'lunar'",
            ) from error
        try:
            gender = Gender(self.gender)
        except ValueError as error:
            raise InvalidGenderError(
                BirthDiagnosticCode.INVALID_GENDER,
                "gender must be 'male', 'female' or 'unknown'",
            ) from error
        object.__setattr__(self, "calendar_type", calendar_type)
        object.__setattr__(self, "gender", gender)

        for name in ("birth_year", "birth_month", "birth_day"):
            value = getattr(self, name)
            if type(value) is not int:
                raise InvalidBirthDateError(
                    BirthDiagnosticCode.INVALID_BIRTH_DATE, f"{name} must be an int"
                )
        if not 1 <= self.birth_month <= 12:
            raise InvalidBirthDateError(
                BirthDiagnosticCode.INVALID_BIRTH_DATE, "birth_month must be 1..12"
            )
        if not 1 <= self.birth_day <= 31:
            raise InvalidBirthDateError(
                BirthDiagnosticCode.INVALID_BIRTH_DATE, "birth_day must be 1..31"
            )
        if self.is_leap_month is not None and type(self.is_leap_month) is not bool:
            raise InvalidLeapMonthException(
                BirthDiagnosticCode.INVALID_LEAP_MONTH,
                "is_leap_month must be True, False or None",
            )
        if calendar_type is CalendarType.SOLAR and self.is_leap_month:
            raise InvalidLeapMonthException(
                BirthDiagnosticCode.LEAP_MONTH_NOT_APPLICABLE,
                "a solar date has no leap month",
            )
        parse_birth_time(self.birth_time_str)

    @property
    def time_is_unknown(self) -> bool:
        return parse_birth_time(self.birth_time_str) is None


@dataclass(frozen=True)
class NormalizedBirthProfile:
    """One fully resolved birth interpretation, ready for the calculator."""

    profile_id: str
    raw_input: RawBirthInput
    civil_solar_date: date
    solar_birth_date: date
    normalized_utc_timestamp: datetime | None
    adjusted_solar_time: datetime | None
    base_timezone: str
    civil_utc_offset_minutes: int | None
    historical_dst_applied: bool
    dst_offset_minutes: int
    meridian_offset_minutes: int
    time_precision: TimePrecision
    analysis_mode: AnalysisMode
    resolution_status: ResolutionStatus
    applied_rule_ids: tuple[str, ...]
    civil_time_policy_id: str = CIVIL_TIME_POLICY_ID
    resolved_is_leap_month: bool | None = None
    lunar_dataset_id: str | None = None

    def calculation_basis_datetime(self) -> datetime | None:
        """Return the basis time labelled ``+09:00`` for the pillar engine.

        The label is a calculation convention required by the engine's input
        contract, not a claim about the historical civil offset; that offset
        stays in ``civil_utc_offset_minutes`` and the true instant stays in
        ``normalized_utc_timestamp``.
        """

        if self.adjusted_solar_time is None:
            return None
        return self.adjusted_solar_time.replace(tzinfo=KST)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-ready view without exposing runtime objects."""

        return {
            "profile_id": self.profile_id,
            "raw_input": {
                "calendar_type": str(self.raw_input.calendar_type),
                "birth_year": self.raw_input.birth_year,
                "birth_month": self.raw_input.birth_month,
                "birth_day": self.raw_input.birth_day,
                "birth_time_str": self.raw_input.birth_time_str,
                "is_leap_month": self.raw_input.is_leap_month,
                "gender": str(self.raw_input.gender),
                "location_text": self.raw_input.location_text,
            },
            "civil_solar_date": self.civil_solar_date.isoformat(),
            "solar_birth_date": self.solar_birth_date.isoformat(),
            "normalized_utc_timestamp": (
                None if self.normalized_utc_timestamp is None
                else self.normalized_utc_timestamp.isoformat()
            ),
            "adjusted_solar_time": (
                None if self.adjusted_solar_time is None
                else self.adjusted_solar_time.isoformat()
            ),
            "base_timezone": self.base_timezone,
            "civil_utc_offset_minutes": self.civil_utc_offset_minutes,
            "civil_time_policy_id": self.civil_time_policy_id,
            "historical_dst_applied": self.historical_dst_applied,
            "dst_offset_minutes": self.dst_offset_minutes,
            "meridian_offset_minutes": self.meridian_offset_minutes,
            "time_precision": str(self.time_precision),
            "analysis_mode": str(self.analysis_mode),
            "resolution_status": str(self.resolution_status),
            "resolved_is_leap_month": self.resolved_is_leap_month,
            "lunar_dataset_id": self.lunar_dataset_id,
            "applied_rule_ids": list(self.applied_rule_ids),
        }


def parse_birth_time(birth_time_str: str | None) -> time | None:
    """Parse ``HH:MM`` minute precision, or return ``None`` for an unknown time."""

    if birth_time_str is None:
        return None
    if not isinstance(birth_time_str, str):
        raise InvalidBirthTimeError(
            BirthDiagnosticCode.INVALID_BIRTH_TIME, "birth_time_str must be a string or None"
        )
    value = birth_time_str.strip()
    if value.casefold() in UNKNOWN_TIME_TOKENS:
        return None
    try:
        parsed = datetime.strptime(value, "%H:%M")
    except ValueError as error:
        raise InvalidBirthTimeError(
            BirthDiagnosticCode.INVALID_BIRTH_TIME,
            "birth_time_str must be a 24-hour 'HH:MM' value",
        ) from error
    return parsed.time()


def normalize_birth_input(
    raw_input: RawBirthInput, lunar_calendar: LunarCalendarPort | None = None
) -> tuple[NormalizedBirthProfile, ...]:
    """Normalize one raw input into one profile, or two explicit candidates.

    Two profiles are returned only when a lunar month exists both as an
    ordinary and a leap month and the user did not choose between them; both
    then carry ``resolution_status == CANDIDATE_BRANCH``.
    """

    if not isinstance(raw_input, RawBirthInput):
        raise TypeError("raw_input must be a RawBirthInput instance")

    birth_time = parse_birth_time(raw_input.birth_time_str)
    if raw_input.calendar_type is CalendarType.SOLAR:
        candidates = ((_solar_date_from(raw_input), None, ()),)
        dataset_id = None
        status = ResolutionStatus.RESOLVED
    else:
        candidates, dataset_id, status = _lunar_candidates(raw_input, lunar_calendar)

    return tuple(
        _build_profile(
            raw_input=raw_input,
            civil_solar_date=civil_solar_date,
            birth_time=birth_time,
            resolved_is_leap_month=resolved_is_leap_month,
            leading_rule_ids=leading_rule_ids,
            resolution_status=status,
            lunar_dataset_id=dataset_id,
        )
        for civil_solar_date, resolved_is_leap_month, leading_rule_ids in candidates
    )


def _solar_date_from(raw_input: RawBirthInput) -> date:
    try:
        return date(raw_input.birth_year, raw_input.birth_month, raw_input.birth_day)
    except ValueError as error:
        raise InvalidBirthDateError(
            BirthDiagnosticCode.INVALID_BIRTH_DATE,
            f"{raw_input.birth_year}-{raw_input.birth_month}-{raw_input.birth_day} is not a real date",
        ) from error


def _lunar_candidates(
    raw_input: RawBirthInput, lunar_calendar: LunarCalendarPort | None
) -> tuple[tuple[tuple[date, bool, tuple[str, ...]], ...], str, ResolutionStatus]:
    if lunar_calendar is None:
        raise LunarCalendarUnavailableError(
            BirthDiagnosticCode.LUNAR_CALENDAR_DATA_UNAVAILABLE,
            "a lunar birth date needs a verified conversion dataset",
        )

    has_leap_month = lunar_calendar.has_leap_month(raw_input.birth_year, raw_input.birth_month)
    if raw_input.is_leap_month is None:
        if has_leap_month:
            choices = (
                (False, (BirthRuleId.LEAP_MONTH_CANDIDATE_BRANCH.value,
                         BirthRuleId.LEAP_MONTH_CANDIDATE_ORDINARY.value)),
                (True, (BirthRuleId.LEAP_MONTH_CANDIDATE_BRANCH.value,
                        BirthRuleId.LEAP_MONTH_CANDIDATE_LEAP.value)),
            )
            status = ResolutionStatus.CANDIDATE_BRANCH
        else:
            choices = ((False, (BirthRuleId.LEAP_MONTH_AUTO_FALSE.value,)),)
            status = ResolutionStatus.RESOLVED
    else:
        if raw_input.is_leap_month and not has_leap_month:
            raise InvalidLeapMonthException(
                BirthDiagnosticCode.INVALID_LEAP_MONTH,
                f"음력 {raw_input.birth_year}년 {raw_input.birth_month}월에는 윤달이 없어요.",
            )
        choices = ((raw_input.is_leap_month, (BirthRuleId.LEAP_MONTH_USER_SELECTED.value,)),)
        status = ResolutionStatus.RESOLVED

    candidates = tuple(
        (
            lunar_calendar.to_solar_date(
                raw_input.birth_year, raw_input.birth_month, raw_input.birth_day, is_leap_month
            ),
            is_leap_month,
            rule_ids + (BirthRuleId.LUNAR_CONVERTED_TO_SOLAR.value,),
        )
        for is_leap_month, rule_ids in choices
    )
    return candidates, lunar_calendar.dataset_id, status


def _build_profile(
    *,
    raw_input: RawBirthInput,
    civil_solar_date: date,
    birth_time: time | None,
    resolved_is_leap_month: bool | None,
    leading_rule_ids: tuple[str, ...],
    resolution_status: ResolutionStatus,
    lunar_dataset_id: str | None,
) -> NormalizedBirthProfile:
    if not isinstance(civil_solar_date, date) or isinstance(civil_solar_date, datetime):
        raise InvalidLunarDateError(
            BirthDiagnosticCode.INVALID_LUNAR_DATE,
            "the conversion dataset must return a datetime.date",
        )

    if birth_time is None:
        rule_ids = leading_rule_ids + (
            BirthRuleId.TIME_UNKNOWN_NO_ADJUSTMENT.value,
            BirthRuleId.TIME_UNKNOWN_THREE_PILLARS.value,
        )
        return NormalizedBirthProfile(
            profile_id=_profile_id(raw_input, civil_solar_date, resolved_is_leap_month),
            raw_input=raw_input,
            civil_solar_date=civil_solar_date,
            solar_birth_date=civil_solar_date,
            normalized_utc_timestamp=None,
            adjusted_solar_time=None,
            base_timezone=BASE_TIMEZONE,
            civil_utc_offset_minutes=None,
            historical_dst_applied=False,
            dst_offset_minutes=0,
            meridian_offset_minutes=0,
            time_precision=TimePrecision.UNKNOWN,
            analysis_mode=AnalysisMode.THREE_PILLARS,
            resolution_status=resolution_status,
            applied_rule_ids=rule_ids,
            resolved_is_leap_month=resolved_is_leap_month,
            lunar_dataset_id=lunar_dataset_id,
        )

    civil_datetime = datetime.combine(civil_solar_date, birth_time)
    resolution = resolve_civil_time(civil_solar_date)
    adjusted = adjusted_solar_datetime(civil_datetime, resolution)
    rule_ids = leading_rule_ids + resolution.applied_rule_ids + _date_shift_rule_ids(
        civil_solar_date, adjusted.date()
    )

    return NormalizedBirthProfile(
        profile_id=_profile_id(raw_input, civil_solar_date, resolved_is_leap_month),
        raw_input=raw_input,
        civil_solar_date=civil_solar_date,
        solar_birth_date=adjusted.date(),
        normalized_utc_timestamp=utc_timestamp_for(civil_datetime, resolution),
        adjusted_solar_time=adjusted,
        base_timezone=BASE_TIMEZONE,
        civil_utc_offset_minutes=resolution.utc_offset_minutes,
        historical_dst_applied=resolution.historical_dst_applied,
        dst_offset_minutes=resolution.dst_offset_minutes,
        meridian_offset_minutes=resolution.meridian_offset_minutes,
        time_precision=TimePrecision.MINUTE,
        analysis_mode=AnalysisMode.FOUR_PILLARS,
        resolution_status=resolution_status,
        applied_rule_ids=rule_ids,
        resolved_is_leap_month=resolved_is_leap_month,
        lunar_dataset_id=lunar_dataset_id,
    )


def _date_shift_rule_ids(civil_solar_date: date, solar_birth_date: date) -> tuple[str, ...]:
    if solar_birth_date < civil_solar_date:
        return (CivilTimeRuleId.SOLAR_DATE_SHIFTED_PREV.value,)
    if solar_birth_date > civil_solar_date:
        return (CivilTimeRuleId.SOLAR_DATE_SHIFTED_NEXT.value,)
    return ()


def _profile_id(
    raw_input: RawBirthInput, civil_solar_date: date, resolved_is_leap_month: bool | None
) -> str:
    """Derive a stable id so the same input always normalizes to the same id."""

    canonical = "|".join((
        str(raw_input.calendar_type),
        f"{raw_input.birth_year:04d}-{raw_input.birth_month:02d}-{raw_input.birth_day:02d}",
        (raw_input.birth_time_str or "").strip(),
        str(raw_input.is_leap_month),
        str(resolved_is_leap_month),
        str(raw_input.gender),
        raw_input.location_text.strip(),
        civil_solar_date.isoformat(),
    ))
    return f"bp_{sha256(canonical.encode('utf-8')).hexdigest()[:16]}"
