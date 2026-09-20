"""Birth-input normalization: raw user input to a calculator-ready profile.

This package owns every decision made *before* the pillar engine runs — lunar
conversion, historical Korean civil time, the standard-meridian correction and
the unknown-birth-time policy. The engine modules stay unaware of them and keep
receiving one already-resolved datetime.
"""

from .civil_time import (
    CIVIL_TIME_POLICY_ID,
    DST_PERIODS,
    FIRST_DOCUMENTED_STANDARD_TIME_DATE,
    MERIDIAN_SEGMENTS,
    CivilTimeResolution,
    CivilTimeRuleId,
    DstPeriod,
    MeridianSegment,
    adjusted_solar_datetime,
    dst_period_for,
    meridian_segment_for,
    resolve_civil_time,
    utc_timestamp_for,
)
from .profile import (
    BASE_TIMEZONE,
    AnalysisMode,
    BirthDiagnosticCode,
    BirthProfileError,
    BirthRuleId,
    CalendarType,
    Gender,
    InvalidBirthDateError,
    InvalidBirthTimeError,
    InvalidCalendarTypeError,
    InvalidGenderError,
    InvalidLeapMonthException,
    InvalidLunarDateError,
    LunarCalendarPort,
    LunarCalendarUnavailableError,
    NormalizedBirthProfile,
    RawBirthInput,
    ResolutionStatus,
    TimePrecision,
    normalize_birth_input,
    parse_birth_time,
)

__all__ = [
    "AnalysisMode", "BASE_TIMEZONE", "BirthDiagnosticCode", "BirthProfileError", "BirthRuleId",
    "CIVIL_TIME_POLICY_ID", "CalendarType", "CivilTimeResolution", "CivilTimeRuleId",
    "DST_PERIODS", "DstPeriod", "FIRST_DOCUMENTED_STANDARD_TIME_DATE", "Gender",
    "InvalidBirthDateError", "InvalidBirthTimeError", "InvalidCalendarTypeError",
    "InvalidGenderError", "InvalidLeapMonthException", "InvalidLunarDateError",
    "LunarCalendarPort", "LunarCalendarUnavailableError", "MERIDIAN_SEGMENTS",
    "MeridianSegment", "NormalizedBirthProfile", "RawBirthInput", "ResolutionStatus",
    "TimePrecision", "adjusted_solar_datetime", "dst_period_for", "meridian_segment_for",
    "normalize_birth_input", "parse_birth_time", "resolve_civil_time", "utc_timestamp_for",
]
