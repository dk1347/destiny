import json
from dataclasses import FrozenInstanceError
from datetime import date, datetime, time, timedelta, timezone

import pytest

from destiny_saju.birth import (
    AnalysisMode,
    BirthDiagnosticCode,
    BirthRuleId,
    CalendarType,
    CivilTimeRuleId,
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
    dst_period_for,
    meridian_segment_for,
    normalize_birth_input,
    parse_birth_time,
    resolve_civil_time,
)
from destiny_saju.data_registry import RuleRegistry
from destiny_saju.four_pillars import four_pillars_for_datetime
from destiny_saju.branches import EarthlyBranch
from destiny_saju.stems import HeavenlyStem


UTC = timezone.utc
KST = timezone(timedelta(hours=9))


class FakeLunarCalendar:
    """An in-memory stand-in for the verified KASI conversion dataset.

    Its numbers are fixtures for the branching rules, not an astronomical
    claim; the real adapter will read the reviewed snapshot instead.
    """

    dataset_id = "fake_lunar_v0"

    _LEAP_MONTHS = {(2025, 6)}
    _CONVERSIONS = {
        (2026, 8, 8, False): date(2026, 9, 18),
        (2025, 6, 10, False): date(2025, 7, 4),
        (2025, 6, 10, True): date(2025, 8, 3),
        (1988, 8, 4, False): date(1988, 9, 14),
    }

    def has_leap_month(self, lunar_year: int, lunar_month: int) -> bool:
        return (lunar_year, lunar_month) in self._LEAP_MONTHS

    def to_solar_date(
        self, lunar_year: int, lunar_month: int, lunar_day: int, is_leap_month: bool
    ) -> date:
        try:
            return self._CONVERSIONS[(lunar_year, lunar_month, lunar_day, is_leap_month)]
        except KeyError as error:
            raise InvalidLunarDateError(
                BirthDiagnosticCode.INVALID_LUNAR_DATE, "no such lunar date"
            ) from error


def solar_input(**overrides: object) -> RawBirthInput:
    values: dict[str, object] = {
        "calendar_type": "solar",
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_time_str": "14:30",
        "gender": "female",
        "location_text": "서울특별시",
    }
    values.update(overrides)
    return RawBirthInput(**values)  # type: ignore[arg-type]


def normalize_one(raw_input: RawBirthInput, lunar_calendar: object | None = None) -> NormalizedBirthProfile:
    profiles = normalize_birth_input(raw_input, lunar_calendar)  # type: ignore[arg-type]
    assert len(profiles) == 1
    return profiles[0]


# --- Modern solar input -----------------------------------------------------

def test_modern_solar_birth_applies_only_the_meridian_correction() -> None:
    profile = normalize_one(solar_input())

    assert profile.meridian_offset_minutes == -30
    assert profile.dst_offset_minutes == 0
    assert profile.historical_dst_applied is False
    assert profile.adjusted_solar_time == datetime(1990, 5, 15, 14, 0)
    assert profile.civil_solar_date == date(1990, 5, 15)
    assert profile.solar_birth_date == date(1990, 5, 15)
    assert profile.normalized_utc_timestamp == datetime(1990, 5, 15, 5, 30, tzinfo=UTC)
    assert profile.civil_utc_offset_minutes == 540
    assert profile.time_precision == TimePrecision.MINUTE
    assert profile.analysis_mode == AnalysisMode.FOUR_PILLARS
    assert profile.resolution_status == ResolutionStatus.RESOLVED
    assert profile.base_timezone == "Asia/Seoul"
    assert profile.civil_time_policy_id == "kr_civil_time_v1"
    assert profile.applied_rule_ids == (CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30,)


def test_raw_input_is_preserved_unchanged() -> None:
    raw_input = solar_input()

    profile = normalize_one(raw_input)

    assert profile.raw_input is raw_input
    assert profile.raw_input.birth_time_str == "14:30"
    assert profile.raw_input.calendar_type == CalendarType.SOLAR
    assert profile.raw_input.gender == Gender.FEMALE


def test_normalized_profile_is_immutable() -> None:
    profile = normalize_one(solar_input())

    with pytest.raises(FrozenInstanceError):
        profile.solar_birth_date = date(2000, 1, 1)  # type: ignore[misc]


# --- Solar date shift across midnight ---------------------------------------

def test_correction_before_midnight_moves_the_solar_birth_date_back() -> None:
    profile = normalize_one(solar_input(birth_year=2000, birth_month=1, birth_day=1, birth_time_str="00:10"))

    assert profile.civil_solar_date == date(2000, 1, 1)
    assert profile.solar_birth_date == date(1999, 12, 31)
    assert profile.adjusted_solar_time == datetime(1999, 12, 31, 23, 40)
    assert profile.normalized_utc_timestamp == datetime(1999, 12, 31, 15, 10, tzinfo=UTC)
    assert CivilTimeRuleId.SOLAR_DATE_SHIFTED_PREV in profile.applied_rule_ids


def test_a_summer_time_birth_just_after_midnight_shifts_back_once() -> None:
    profile = normalize_one(solar_input(birth_year=1988, birth_month=8, birth_day=15, birth_time_str="01:15"))

    assert profile.adjusted_solar_time == datetime(1988, 8, 14, 23, 45)
    assert profile.solar_birth_date == date(1988, 8, 14)
    assert profile.applied_rule_ids == (
        CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30,
        CivilTimeRuleId.DST_APPLIED_MINUS_60,
        CivilTimeRuleId.SOLAR_DATE_SHIFTED_PREV,
    )


def test_no_shift_rule_is_recorded_when_the_date_does_not_move() -> None:
    profile = normalize_one(solar_input())

    assert CivilTimeRuleId.SOLAR_DATE_SHIFTED_PREV not in profile.applied_rule_ids
    assert CivilTimeRuleId.SOLAR_DATE_SHIFTED_NEXT not in profile.applied_rule_ids


# --- Historical civil time --------------------------------------------------

def test_127_5_meridian_period_applies_no_correction() -> None:
    profile = normalize_one(solar_input(birth_year=1958, birth_month=3, birth_day=1, birth_time_str="09:00"))

    assert profile.meridian_offset_minutes == 0
    assert profile.adjusted_solar_time == datetime(1958, 3, 1, 9, 0)
    assert profile.civil_utc_offset_minutes == 510
    assert profile.normalized_utc_timestamp == datetime(1958, 3, 1, 0, 30, tzinfo=UTC)
    assert profile.applied_rule_ids == (CivilTimeRuleId.MERIDIAN_127_5_NO_OFFSET,)


def test_summer_time_on_the_127_5_meridian_subtracts_only_one_hour() -> None:
    profile = normalize_one(solar_input(birth_year=1958, birth_month=6, birth_day=10, birth_time_str="09:00"))

    assert (profile.dst_offset_minutes, profile.meridian_offset_minutes) == (-60, 0)
    assert profile.historical_dst_applied is True
    assert profile.adjusted_solar_time == datetime(1958, 6, 10, 8, 0)
    assert profile.civil_utc_offset_minutes == 570
    assert profile.normalized_utc_timestamp == datetime(1958, 6, 9, 23, 30, tzinfo=UTC)


def test_summer_time_on_the_135_meridian_subtracts_ninety_minutes() -> None:
    profile = normalize_one(solar_input(birth_year=1988, birth_month=8, birth_day=15, birth_time_str="10:00"))

    assert (profile.dst_offset_minutes, profile.meridian_offset_minutes) == (-60, -30)
    assert profile.adjusted_solar_time == datetime(1988, 8, 15, 8, 30)
    assert profile.civil_utc_offset_minutes == 600
    assert profile.normalized_utc_timestamp == datetime(1988, 8, 15, 0, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    "civil_date, utc_offset_minutes, meridian_offset_minutes, rule_id",
    [
        (date(1908, 3, 31), 510, 0, CivilTimeRuleId.MERIDIAN_OUT_OF_RANGE_NO_OFFSET),
        (date(1908, 4, 1), 510, 0, CivilTimeRuleId.MERIDIAN_127_5_NO_OFFSET),
        (date(1911, 12, 31), 510, 0, CivilTimeRuleId.MERIDIAN_127_5_NO_OFFSET),
        (date(1912, 1, 1), 540, -30, CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30),
        (date(1954, 3, 20), 540, -30, CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30),
        (date(1954, 3, 21), 510, 0, CivilTimeRuleId.MERIDIAN_127_5_NO_OFFSET),
        (date(1961, 8, 9), 510, 0, CivilTimeRuleId.MERIDIAN_127_5_NO_OFFSET),
        (date(1961, 8, 10), 540, -30, CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30),
        (date(2026, 9, 20), 540, -30, CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30),
    ],
)
def test_meridian_segments_include_both_boundary_dates(
    civil_date: date, utc_offset_minutes: int, meridian_offset_minutes: int, rule_id: str
) -> None:
    resolution = resolve_civil_time(civil_date)

    assert resolution.utc_offset_minutes == utc_offset_minutes
    assert resolution.meridian_offset_minutes == meridian_offset_minutes
    assert meridian_segment_for(civil_date).rule_id == rule_id
    assert rule_id in resolution.applied_rule_ids


def test_a_pre_1908_birth_records_the_out_of_range_rule_without_correction() -> None:
    profile = normalize_one(solar_input(birth_year=1900, birth_month=1, birth_day=1, birth_time_str="12:00"))

    assert profile.meridian_offset_minutes == 0
    assert profile.adjusted_solar_time == datetime(1900, 1, 1, 12, 0)
    assert profile.applied_rule_ids == (CivilTimeRuleId.MERIDIAN_OUT_OF_RANGE_NO_OFFSET,)


@pytest.mark.parametrize(
    "civil_date, in_summer_time",
    [
        (date(1948, 5, 31), False),
        (date(1948, 6, 1), True),
        (date(1948, 9, 12), True),
        (date(1948, 9, 13), False),
        (date(1960, 5, 1), True),
        (date(1960, 9, 17), True),
        (date(1960, 9, 18), False),
        (date(1961, 5, 1), False),
        (date(1987, 5, 9), False),
        (date(1987, 5, 10), True),
        (date(1987, 10, 10), True),
        (date(1987, 10, 11), False),
        (date(1988, 5, 8), True),
        (date(1988, 10, 8), True),
        (date(1988, 10, 9), False),
        (date(1989, 7, 1), False),
    ],
)
def test_summer_time_periods_include_both_boundary_dates(civil_date: date, in_summer_time: bool) -> None:
    resolution = resolve_civil_time(civil_date)

    assert resolution.historical_dst_applied is in_summer_time
    assert resolution.dst_offset_minutes == (-60 if in_summer_time else 0)
    assert (dst_period_for(civil_date) is not None) is in_summer_time


@pytest.mark.parametrize(
    "civil_date",
    [date(1987, 5, 10), date(1987, 10, 11), date(1988, 5, 8), date(1988, 10, 9)],
)
def test_intraday_summer_time_transitions_are_marked_approximate(civil_date: date) -> None:
    assert CivilTimeRuleId.DST_BOUNDARY_DATE_APPROXIMATE in resolve_civil_time(civil_date).applied_rule_ids


@pytest.mark.parametrize(
    "civil_date",
    [date(1948, 6, 1), date(1948, 9, 13), date(1960, 5, 1), date(1987, 7, 1), date(1990, 5, 15)],
)
def test_midnight_transitions_are_not_marked_approximate(civil_date: date) -> None:
    assert CivilTimeRuleId.DST_BOUNDARY_DATE_APPROXIMATE not in resolve_civil_time(civil_date).applied_rule_ids


# --- Unknown birth time -----------------------------------------------------

@pytest.mark.parametrize("birth_time_str", [None, "", "  ", "모름", "미상", "unknown", "UNKNOWN"])
def test_unknown_birth_time_never_invents_a_clock_time(birth_time_str: str | None) -> None:
    profile = normalize_one(solar_input(birth_time_str=birth_time_str))

    assert profile.time_precision == TimePrecision.UNKNOWN
    assert profile.analysis_mode == AnalysisMode.THREE_PILLARS
    assert profile.normalized_utc_timestamp is None
    assert profile.adjusted_solar_time is None
    assert profile.calculation_basis_datetime() is None
    assert profile.civil_utc_offset_minutes is None


def test_unknown_birth_time_does_not_move_the_solar_birth_date() -> None:
    profile = normalize_one(solar_input(birth_year=2000, birth_month=1, birth_day=1, birth_time_str=None))

    assert profile.solar_birth_date == date(2000, 1, 1)
    assert profile.civil_solar_date == date(2000, 1, 1)
    assert CivilTimeRuleId.SOLAR_DATE_SHIFTED_PREV not in profile.applied_rule_ids


def test_unknown_birth_time_applies_no_summer_time_correction() -> None:
    profile = normalize_one(solar_input(birth_year=1988, birth_month=8, birth_day=15, birth_time_str=None))

    assert (profile.dst_offset_minutes, profile.meridian_offset_minutes) == (0, 0)
    assert profile.historical_dst_applied is False
    assert profile.applied_rule_ids == (
        BirthRuleId.TIME_UNKNOWN_NO_ADJUSTMENT,
        BirthRuleId.TIME_UNKNOWN_THREE_PILLARS,
    )


@pytest.mark.parametrize("birth_time_str", ["14:30", "00:00", "23:59", " 09:05 "])
def test_valid_times_parse_to_minute_precision(birth_time_str: str) -> None:
    parsed = parse_birth_time(birth_time_str)

    assert isinstance(parsed, time)
    assert parsed.second == 0


@pytest.mark.parametrize("birth_time_str", ["24:00", "9시 30분", "14:30:00", "2:70", "abc", "1430"])
def test_unparsable_times_are_rejected_instead_of_guessed(birth_time_str: str) -> None:
    with pytest.raises(InvalidBirthTimeError) as error:
        solar_input(birth_time_str=birth_time_str)

    assert error.value.code == BirthDiagnosticCode.INVALID_BIRTH_TIME


# --- Lunar input ------------------------------------------------------------

def test_lunar_month_without_a_leap_counterpart_resolves_automatically() -> None:
    raw_input = RawBirthInput("lunar", 2026, 8, 8, "10:00", None, "male")

    profile = normalize_one(raw_input, FakeLunarCalendar())

    assert profile.resolved_is_leap_month is False
    assert profile.resolution_status == ResolutionStatus.RESOLVED
    assert profile.civil_solar_date == date(2026, 9, 18)
    assert profile.solar_birth_date == date(2026, 9, 18)
    assert profile.lunar_dataset_id == "fake_lunar_v0"
    assert profile.applied_rule_ids == (
        BirthRuleId.LEAP_MONTH_AUTO_FALSE,
        BirthRuleId.LUNAR_CONVERTED_TO_SOLAR,
        CivilTimeRuleId.MERIDIAN_135_OFFSET_MINUS_30,
    )


def test_an_unchosen_leap_month_produces_two_explicit_candidates() -> None:
    raw_input = RawBirthInput("lunar", 2025, 6, 10, "10:00", None, "male")

    ordinary, leap = normalize_birth_input(raw_input, FakeLunarCalendar())

    assert ordinary.resolved_is_leap_month is False
    assert leap.resolved_is_leap_month is True
    assert ordinary.civil_solar_date == date(2025, 7, 4)
    assert leap.civil_solar_date == date(2025, 8, 3)
    assert ordinary.profile_id != leap.profile_id
    for profile in (ordinary, leap):
        assert profile.resolution_status == ResolutionStatus.CANDIDATE_BRANCH
        assert BirthRuleId.LEAP_MONTH_CANDIDATE_BRANCH in profile.applied_rule_ids
    assert BirthRuleId.LEAP_MONTH_CANDIDATE_ORDINARY in ordinary.applied_rule_ids
    assert BirthRuleId.LEAP_MONTH_CANDIDATE_LEAP in leap.applied_rule_ids


@pytest.mark.parametrize(
    "is_leap_month, expected_date",
    [(False, date(2025, 7, 4)), (True, date(2025, 8, 3))],
)
def test_an_explicit_leap_month_choice_is_used_as_given(is_leap_month: bool, expected_date: date) -> None:
    raw_input = RawBirthInput("lunar", 2025, 6, 10, "10:00", is_leap_month, "male")

    profile = normalize_one(raw_input, FakeLunarCalendar())

    assert profile.resolved_is_leap_month is is_leap_month
    assert profile.civil_solar_date == expected_date
    assert profile.resolution_status == ResolutionStatus.RESOLVED
    assert BirthRuleId.LEAP_MONTH_USER_SELECTED in profile.applied_rule_ids


def test_a_leap_month_claim_for_a_month_without_one_is_rejected() -> None:
    raw_input = RawBirthInput("lunar", 2026, 8, 8, "10:00", True, "male")

    with pytest.raises(InvalidLeapMonthException) as error:
        normalize_birth_input(raw_input, FakeLunarCalendar())

    assert error.value.code == BirthDiagnosticCode.INVALID_LEAP_MONTH


def test_a_solar_input_cannot_claim_a_leap_month() -> None:
    with pytest.raises(InvalidLeapMonthException) as error:
        solar_input(is_leap_month=True)

    assert error.value.code == BirthDiagnosticCode.LEAP_MONTH_NOT_APPLICABLE


def test_lunar_input_without_a_conversion_dataset_is_unavailable() -> None:
    raw_input = RawBirthInput("lunar", 2026, 8, 8, "10:00", False, "male")

    with pytest.raises(LunarCalendarUnavailableError) as error:
        normalize_birth_input(raw_input)

    assert error.value.code == BirthDiagnosticCode.LUNAR_CALENDAR_DATA_UNAVAILABLE


def test_an_unknown_lunar_date_is_rejected_by_the_dataset() -> None:
    raw_input = RawBirthInput("lunar", 2026, 8, 30, "10:00", False, "male")

    with pytest.raises(InvalidLunarDateError) as error:
        normalize_birth_input(raw_input, FakeLunarCalendar())

    assert error.value.code == BirthDiagnosticCode.INVALID_LUNAR_DATE


def test_lunar_conversion_applies_civil_time_rules_of_the_converted_date() -> None:
    raw_input = RawBirthInput("lunar", 1988, 8, 4, "10:00", None, "female")

    profile = normalize_one(raw_input, FakeLunarCalendar())

    assert profile.civil_solar_date == date(1988, 9, 14)
    assert profile.historical_dst_applied is True
    assert profile.adjusted_solar_time == datetime(1988, 9, 14, 8, 30)


def test_the_fake_dataset_satisfies_the_lunar_calendar_port() -> None:
    assert isinstance(FakeLunarCalendar(), LunarCalendarPort)


# --- Input validation -------------------------------------------------------

def test_an_impossible_solar_date_is_rejected() -> None:
    with pytest.raises(InvalidBirthDateError) as error:
        normalize_birth_input(solar_input(birth_year=2026, birth_month=2, birth_day=30))

    assert error.value.code == BirthDiagnosticCode.INVALID_BIRTH_DATE


@pytest.mark.parametrize("birth_month, birth_day", [(0, 15), (13, 15), (5, 0), (5, 32)])
def test_out_of_range_month_and_day_are_rejected_at_input(birth_month: int, birth_day: int) -> None:
    with pytest.raises(InvalidBirthDateError):
        solar_input(birth_month=birth_month, birth_day=birth_day)


def test_an_unknown_calendar_type_is_rejected() -> None:
    with pytest.raises(InvalidCalendarTypeError) as error:
        solar_input(calendar_type="julian")

    assert error.value.code == BirthDiagnosticCode.INVALID_CALENDAR_TYPE


def test_an_unknown_gender_is_rejected() -> None:
    with pytest.raises(InvalidGenderError) as error:
        solar_input(gender="여성")

    assert error.value.code == BirthDiagnosticCode.INVALID_GENDER


def test_gender_defaults_to_unknown_rather_than_a_guess() -> None:
    raw_input = RawBirthInput("solar", 1990, 5, 15, "14:30")

    assert raw_input.gender == Gender.UNKNOWN


def test_normalize_rejects_a_non_profile_input() -> None:
    with pytest.raises(TypeError):
        normalize_birth_input({"calendar_type": "solar"})  # type: ignore[arg-type]


# --- Identity and serialization ---------------------------------------------

def test_profile_id_is_deterministic_for_the_same_input() -> None:
    first = normalize_one(solar_input())
    second = normalize_one(solar_input())

    assert first.profile_id == second.profile_id
    assert first == second


def test_profile_id_changes_when_the_input_changes() -> None:
    first = normalize_one(solar_input())
    second = normalize_one(solar_input(birth_time_str="14:31"))

    assert first.profile_id != second.profile_id


def test_as_dict_is_json_serializable_and_keeps_both_dates() -> None:
    profile = normalize_one(solar_input(birth_year=2000, birth_month=1, birth_day=1, birth_time_str="00:10"))

    payload = json.loads(json.dumps(profile.as_dict()))

    assert payload["civil_solar_date"] == "2000-01-01"
    assert payload["solar_birth_date"] == "1999-12-31"
    assert payload["adjusted_solar_time"] == "1999-12-31T23:40:00"
    assert payload["normalized_utc_timestamp"] == "1999-12-31T15:10:00+00:00"
    assert payload["time_precision"] == "minute"
    assert payload["analysis_mode"] == "FOUR_PILLARS"
    assert payload["resolution_status"] == "RESOLVED"
    assert payload["applied_rule_ids"] == [
        "MERIDIAN_135_OFFSET_MINUS_30", "SOLAR_DATE_SHIFTED_PREV",
    ]


def test_unknown_time_profile_serializes_null_timestamps() -> None:
    payload = json.loads(json.dumps(normalize_one(solar_input(birth_time_str="모름")).as_dict()))

    assert payload["normalized_utc_timestamp"] is None
    assert payload["adjusted_solar_time"] is None
    assert payload["analysis_mode"] == "THREE_PILLARS"


# --- Hand-off to the existing pillar engine ---------------------------------

def test_the_calculation_basis_feeds_the_existing_four_pillars_engine() -> None:
    profile = normalize_one(solar_input(birth_year=2026, birth_month=2, birth_day=4, birth_time_str="05:32"))
    basis = profile.calculation_basis_datetime()

    assert basis == datetime(2026, 2, 4, 5, 2, tzinfo=KST)

    pillars = four_pillars_for_datetime(basis, RuleRegistry(allow_unverified=True))

    assert (pillars.year.stem, pillars.year.branch) == (HeavenlyStem.BYEONG, EarthlyBranch.O)
    assert (pillars.day.stem, pillars.day.branch) == (HeavenlyStem.GI, EarthlyBranch.YU)
    assert (pillars.hour.stem, pillars.hour.branch) == (HeavenlyStem.JEONG, EarthlyBranch.MYO)
