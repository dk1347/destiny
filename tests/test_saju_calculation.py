import json
from datetime import datetime, timedelta, timezone

import pytest

from destiny_saju.birth import AnalysisMode, RawBirthInput, normalize_birth_input
from destiny_saju.calculator import (
    DEFAULT_CYCLE_COUNT,
    MEAN_YEAR_DAYS,
    NOTICE_MESSAGES,
    SEASON_BOUNDARY_WINDOW,
    TIMELINE_POLICY_ID,
    CalculationNotice,
    DaewunDirection,
    DayBoundaryDoctrine,
    branch_hanja,
    daewun_direction_for,
    daewun_for,
    format_korean_with_hanja,
    pillar_hanja,
    round_daewun_number,
    saju_calculation_for_profile,
    stem_hanja,
    ten_god_label,
    timeline_for_profile,
)
from destiny_saju.data_registry import DatasetError, RuleRegistry
from destiny_saju.four_pillars import FourPillars, ThreePillars
from destiny_saju.stems import HeavenlyStem
from destiny_saju.ten_gods import TenGod


KST = timezone(timedelta(hours=9))

#: The only verified solar-term coverage is 2026, so every fixture lives there.


@pytest.fixture
def registry() -> RuleRegistry:
    return RuleRegistry()


def calculate(registry: RuleRegistry, birth_time_str: str | None, *, gender: str = "male",
              year: int = 2026, month: int = 6, day: int = 15, **kwargs: object):
    profile = normalize_birth_input(
        RawBirthInput("solar", year, month, day, birth_time_str, gender=gender)
    )[0]
    return saju_calculation_for_profile(profile, registry, **kwargs)  # type: ignore[arg-type]


def rendered(calculation, registry: RuleRegistry) -> dict[str, str | None]:
    return calculation.as_dict(registry)["pillars"]


# --- 1. One timeline for every comparison -----------------------------------

def test_year_and_month_are_decided_on_the_uncorrected_instant_timeline(registry: RuleRegistry) -> None:
    """A 05:20 civil birth is after 입춘 05:02 even though its basis time is 04:50.

    Comparing the −30 minute basis time against the published KST term instant
    would double-correct and wrongly return the previous year's 乙巳/己丑.
    """

    calculation = calculate(registry, "05:20", year=2026, month=2, day=4)

    assert calculation.season_basis_datetime == datetime(2026, 2, 4, 5, 20, tzinfo=KST)
    assert calculation.pillar_basis_datetime == datetime(2026, 2, 4, 4, 50, tzinfo=KST)
    assert rendered(calculation, registry)["year"] == "丙午"
    assert rendered(calculation, registry)["month"] == "庚寅"


def test_day_and_hour_are_decided_on_the_corrected_basis_time(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "05:20", year=2026, month=2, day=4)

    # 04:50 falls in the 寅 window (03:00–04:59); the uncorrected 05:20 would be 卯.
    assert rendered(calculation, registry)["hour"] == "丙寅"
    assert rendered(calculation, registry)["day"] == "己酉"


def test_a_birth_before_ipchun_keeps_the_previous_year_pillar(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "04:47", year=2026, month=2, day=4)

    assert rendered(calculation, registry)["year"] == "乙巳"
    assert rendered(calculation, registry)["month"] == "己丑"


def test_the_timeline_policy_is_recorded_on_every_result(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30")

    assert calculation.timeline_policy_id == TIMELINE_POLICY_ID == "unified_instant_v1"
    assert calculation.civil_time_policy_id == "kr_civil_time_v1"


def test_the_timeline_exposes_both_bases_as_kst_instants(registry: RuleRegistry) -> None:
    profile = normalize_birth_input(RawBirthInput("solar", 2026, 6, 15, "10:30", gender="male"))[0]

    timeline = timeline_for_profile(profile)

    assert timeline.season_basis.utcoffset() == timedelta(hours=9)
    assert timeline.pillar_basis.utcoffset() == timedelta(hours=9)
    assert timeline.season_basis - timeline.pillar_basis == timedelta(minutes=30)
    assert timeline.is_anchor_approximate is False


@pytest.mark.parametrize("birth_time_str", ["05:10", "05:17", "04:47", "05:02"])
def test_a_birth_within_fifteen_minutes_of_a_term_is_flagged(
    registry: RuleRegistry, birth_time_str: str
) -> None:
    calculation = calculate(registry, birth_time_str, year=2026, month=2, day=4)

    assert CalculationNotice.SEASON_BOUNDARY_ADJACENT in calculation.notices
    assert NOTICE_MESSAGES[CalculationNotice.SEASON_BOUNDARY_ADJACENT] in calculation.warnings


@pytest.mark.parametrize("birth_time_str", ["05:18", "06:00", "04:46"])
def test_a_birth_outside_the_window_is_not_flagged(
    registry: RuleRegistry, birth_time_str: str
) -> None:
    calculation = calculate(registry, birth_time_str, year=2026, month=2, day=4)

    assert CalculationNotice.SEASON_BOUNDARY_ADJACENT not in calculation.notices


def test_the_boundary_window_is_fifteen_minutes() -> None:
    assert SEASON_BOUNDARY_WINDOW == timedelta(minutes=15)


def test_the_boundary_message_states_the_clock_and_natural_time_causes() -> None:
    message = NOTICE_MESSAGES[CalculationNotice.SEASON_BOUNDARY_ADJACENT]

    assert "절입 시각" in message
    assert "시계 기록 오차" in message and "자연시차" in message
    assert "월주(또는 연주)" in message


# --- 2. Zi hour dual view ---------------------------------------------------

def test_the_zi_hour_default_follows_the_modern_majority_doctrine(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "23:45")

    assert calculation.pillar_basis_datetime.hour == 23
    assert calculation.day_boundary_doctrine is DayBoundaryDoctrine.MODERN_MAJORITY
    assert calculation.day_boundary_doctrine_label == "현대 다수설(야자시·조자시설) 기준 산출"
    assert calculation.calculation_profile_id == "midnight_v1"
    # Same-day 일진 with a 子 hour.
    assert rendered(calculation, registry)["day"] == "庚申"
    assert rendered(calculation, registry)["hour"] == "丙子"


def test_the_zi_hour_also_produces_the_classical_candidate(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "23:45")
    alternative = calculation.alternative_candidate

    assert alternative is not None
    assert alternative.day_boundary_doctrine is DayBoundaryDoctrine.CLASSICAL
    assert alternative.day_boundary_doctrine_label == "고전 원칙론(정자시설) 기준 산출"
    assert alternative.calculation_profile_id == "kr_standard_v1"
    # 23:00 already belongs to the next day under 정자시설.
    assert rendered(alternative, registry)["day"] == "辛酉"
    assert rendered(alternative, registry)["hour"] == "戊子"


def test_both_doctrines_agree_on_the_year_and_month_pillars(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "23:45")
    alternative = calculation.alternative_candidate

    assert alternative is not None
    assert rendered(alternative, registry)["year"] == rendered(calculation, registry)["year"]
    assert rendered(alternative, registry)["month"] == rendered(calculation, registry)["month"]


def test_the_dual_view_notice_names_both_schools(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "23:45")
    message = NOTICE_MESSAGES[CalculationNotice.ZI_HOUR_DUAL_VIEW]

    assert CalculationNotice.ZI_HOUR_DUAL_VIEW in calculation.notices
    assert message in calculation.warnings
    assert "야자시설" in message and "정자시설" in message
    assert "현대 다수설" in message


def test_the_alternative_candidate_does_not_nest_further(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "23:45")

    assert calculation.alternative_candidate is not None
    assert calculation.alternative_candidate.alternative_candidate is None


@pytest.mark.parametrize("birth_time_str", ["10:30", "01:20", "22:45"])
def test_no_alternative_is_produced_outside_the_zi_hour(
    registry: RuleRegistry, birth_time_str: str
) -> None:
    calculation = calculate(registry, birth_time_str)

    assert calculation.alternative_candidate is None
    assert CalculationNotice.ZI_HOUR_DUAL_VIEW not in calculation.notices


def test_a_just_after_midnight_birth_falls_into_the_zi_hour_once_corrected(
    registry: RuleRegistry
) -> None:
    """00:20 civil becomes 23:50 on the previous day after the −30 correction."""

    calculation = calculate(registry, "00:20")

    assert calculation.pillar_basis_datetime == datetime(2026, 6, 14, 23, 50, tzinfo=KST)
    assert CalculationNotice.ZI_HOUR_DUAL_VIEW in calculation.notices
    assert calculation.alternative_candidate is not None
    # 야자시: the 14th keeps its own 일진; 정자시: the 15th already began.
    assert rendered(calculation, registry)["day"] == "己未"
    assert rendered(calculation.alternative_candidate, registry)["day"] == "庚申"


def test_requesting_the_classical_doctrine_flips_the_pair(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "23:45", doctrine=DayBoundaryDoctrine.CLASSICAL)

    assert rendered(calculation, registry)["day"] == "辛酉"
    assert calculation.alternative_candidate is not None
    assert calculation.alternative_candidate.day_boundary_doctrine is DayBoundaryDoctrine.MODERN_MAJORITY
    assert rendered(calculation.alternative_candidate, registry)["day"] == "庚申"


# --- 3. Fortune cycle precision ---------------------------------------------

def test_the_raw_day_difference_and_float_are_preserved(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30")
    daewun = calculation.daewun

    assert daewun is not None
    # 2026-06-15 10:30 → 소서 2026-07-07 10:57 is 22 days 27 minutes away.
    assert daewun.boundary_term_id == "soseo"
    assert daewun.source_day_difference == pytest.approx(22 + 27 / 1440)
    assert daewun.daewun_raw_float == pytest.approx(daewun.source_day_difference / 3)
    assert daewun.daewun_number == 7
    assert daewun.method_id == "daewun_three_day_one_year_v1"


def test_the_displayed_number_uses_round_half_up_not_bankers_rounding() -> None:
    assert round_daewun_number(6.5) == 7
    assert round_daewun_number(7.5) == 8
    assert round_daewun_number(7.4999) == 7


def test_the_displayed_number_is_clamped_to_the_one_to_ten_range() -> None:
    assert round_daewun_number(0.1) == 1
    assert round_daewun_number(12.0) == 10


@pytest.mark.parametrize(
    "year_stem, gender, expected",
    [
        (HeavenlyStem.BYEONG, "male", DaewunDirection.FORWARD),
        (HeavenlyStem.BYEONG, "female", DaewunDirection.BACKWARD),
        (HeavenlyStem.EUL, "male", DaewunDirection.BACKWARD),
        (HeavenlyStem.EUL, "female", DaewunDirection.FORWARD),
    ],
)
def test_direction_follows_yang_male_yin_female_forward(
    registry: RuleRegistry, year_stem: HeavenlyStem, gender: str, expected: DaewunDirection
) -> None:
    assert daewun_direction_for(year_stem, gender, registry) is expected


def test_a_forward_cycle_advances_from_the_month_pillar(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30", gender="male")
    daewun = calculation.daewun

    assert daewun is not None and daewun.direction is DaewunDirection.FORWARD
    assert rendered(calculation, registry)["month"] == "甲午"
    assert [pillar_hanja(cycle.stem, cycle.branch, registry) for cycle in daewun.cycles[:3]] == [
        "乙未", "丙申", "丁酉",
    ]


def test_a_backward_cycle_retreats_from_the_month_pillar(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30", gender="female")
    daewun = calculation.daewun

    assert daewun is not None and daewun.direction is DaewunDirection.BACKWARD
    assert daewun.boundary_term_id == "mangjong"
    assert [pillar_hanja(cycle.stem, cycle.branch, registry) for cycle in daewun.cycles[:3]] == [
        "癸巳", "壬辰", "辛卯",
    ]


def test_every_exchange_instant_is_ten_years_after_the_previous_one(registry: RuleRegistry) -> None:
    daewun = calculate(registry, "10:30").daewun

    assert daewun is not None
    assert len(daewun.cycles) == DEFAULT_CYCLE_COUNT
    assert daewun.cycles[0].starts_at == daewun.first_exchange_at
    for earlier, later in zip(daewun.cycles, daewun.cycles[1:]):
        assert later.starts_at - earlier.starts_at == timedelta(days=10 * MEAN_YEAR_DAYS)
        assert later.start_age_display == earlier.start_age_display + 10


def test_the_exchange_year_and_month_are_reported(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30")
    first = calculation.as_dict(registry)["daewun"]["cycles"][0]

    assert first["exchange_year_month"] == "2033-10"
    assert first["start_age_display"] == 7
    assert first["start_age_years"] == pytest.approx(7.339583, abs=1e-5)


def test_the_exchange_precision_notice_is_always_attached(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30")
    message = NOTICE_MESSAGES[CalculationNotice.DAEWUN_EXCHANGE_PRECISION]

    assert CalculationNotice.DAEWUN_EXCHANGE_PRECISION in calculation.notices
    assert message in calculation.warnings
    assert "균시차" in message and "교운" in message


def test_the_fortune_cycle_fails_closed_outside_verified_term_coverage(registry: RuleRegistry) -> None:
    with pytest.raises(DatasetError, match="SOLAR_TERM_DATA_UNAVAILABLE"):
        calculate(registry, "10:00", gender="male", month=12, day=20)


def test_the_same_date_still_resolves_in_the_covered_direction(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:00", gender="female", month=12, day=20)

    assert calculation.daewun is not None
    assert calculation.daewun.boundary_term_id == "daeseol"


def test_an_unrecorded_gender_never_guesses_a_direction(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30", gender="unknown")

    assert calculation.daewun is None
    assert CalculationNotice.DAEWUN_GENDER_REQUIRED in calculation.notices


def test_daewun_rejects_a_naive_instant_and_an_empty_cycle_count(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30")
    pillars = calculation.pillars
    assert isinstance(pillars, FourPillars)

    with pytest.raises(TypeError):
        daewun_for(datetime(2026, 6, 15, 10, 30), pillars.year, pillars.month, "male", registry)
    with pytest.raises(ValueError):
        daewun_for(
            calculation.season_basis_datetime, pillars.year, pillars.month, "male", registry,
            cycle_count=0,
        )


# --- 4. Three-pillar mode ---------------------------------------------------

def test_an_unknown_time_produces_three_pillars_without_an_hour(registry: RuleRegistry) -> None:
    calculation = calculate(registry, None)

    assert calculation.analysis_mode is AnalysisMode.THREE_PILLARS
    assert calculation.status == "partial"
    assert isinstance(calculation.pillars, ThreePillars)
    assert rendered(calculation, registry)["hour"] is None
    assert rendered(calculation, registry)["day"] == "庚申"


def test_an_unknown_time_anchors_the_fortune_cycle_at_noon(registry: RuleRegistry) -> None:
    calculation = calculate(registry, None)

    assert calculation.season_basis_datetime == datetime(2026, 6, 15, 12, 0, tzinfo=KST)
    assert calculation.pillar_basis_datetime == datetime(2026, 6, 15, 11, 30, tzinfo=KST)
    assert calculation.daewun is not None
    assert calculation.daewun.is_anchor_approximate is True
    assert calculation.daewun.daewun_number == 7


def test_the_three_pillar_notice_explains_the_noon_anchor(registry: RuleRegistry) -> None:
    calculation = calculate(registry, None)
    message = NOTICE_MESSAGES[CalculationNotice.TIME_PRECISION_APPROXIMATE]

    assert CalculationNotice.TIME_PRECISION_APPROXIMATE in calculation.notices
    assert message in calculation.warnings
    assert "삼주(6자)" in message and "정오 기준" in message and "±1세" in message


def test_a_known_time_is_never_marked_approximate(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30")

    assert CalculationNotice.TIME_PRECISION_APPROXIMATE not in calculation.notices
    assert calculation.daewun is not None and calculation.daewun.is_anchor_approximate is False


def test_an_unknown_time_on_a_term_day_branches_instead_of_choosing(registry: RuleRegistry) -> None:
    calculation = calculate(registry, None, year=2026, month=2, day=4)

    assert calculation.status == "candidate_branch"
    assert calculation.pillars is None
    assert calculation.daewun is None
    assert CalculationNotice.SEASON_BOUNDARY_CANDIDATE_BRANCH in calculation.notices
    assert [candidate.label for candidate in calculation.season_candidates] == [
        "before_term", "after_term",
    ]


def test_both_season_candidates_carry_their_own_pillars(registry: RuleRegistry) -> None:
    calculation = calculate(registry, None, year=2026, month=2, day=4)
    before, after = calculation.as_dict(registry)["season_candidates"]

    assert (before["year"], before["month"]) == ("乙巳", "己丑")
    assert (after["year"], after["month"]) == ("丙午", "庚寅")
    assert before["term_id"] == after["term_id"] == "ipchun"
    assert before["applies_when"] == "05:02 이전 출생인 경우"
    assert after["applies_when"] == "05:02 이후 출생인 경우"


def test_the_day_pillar_stays_certain_while_year_and_month_branch(registry: RuleRegistry) -> None:
    calculation = calculate(registry, None, year=2026, month=2, day=4)

    assert rendered(calculation, registry)["day"] == "己酉"
    assert rendered(calculation, registry)["year"] is None
    assert rendered(calculation, registry)["month"] is None


# --- 5. Naming and notation standard ----------------------------------------

def test_stems_and_branches_are_written_as_bare_hanja(registry: RuleRegistry) -> None:
    assert stem_hanja(HeavenlyStem.GAP, registry) == "甲"
    assert branch_hanja(calculate(registry, "23:45").pillars.hour.branch, registry) == "子"


def test_a_pillar_is_two_hanja_characters(registry: RuleRegistry) -> None:
    calculation = calculate(registry, "10:30")

    assert pillar_hanja(calculation.day_pillar.stem, calculation.day_pillar.branch, registry) == "庚申"
    assert calculation.as_dict(registry)["pillars"]["day_master"] == "庚"


def test_ten_gods_are_written_korean_with_hanja(registry: RuleRegistry) -> None:
    assert ten_god_label(TenGod.BIGYEON, registry) == "비견(比肩)"
    assert ten_god_label(TenGod.JEONGGWAN, registry) == "정관(正官)"


def test_the_result_labels_every_ten_god_position(registry: RuleRegistry) -> None:
    ten_gods = calculate(registry, "10:30").as_dict(registry)["ten_gods"]

    assert set(ten_gods) == {"year", "month", "hour"}
    assert ten_gods["year"] == "편관(偏官)"
    assert ten_gods["month"] == "편재(偏財)"


def test_the_same_formatter_covers_twelve_stage_names() -> None:
    assert format_korean_with_hanja("건록", "建祿") == "건록(建祿)"


def test_the_formatter_refuses_a_missing_reading() -> None:
    with pytest.raises(ValueError):
        format_korean_with_hanja("건록", "")


# --- Serialization ----------------------------------------------------------

def test_the_result_is_json_serializable_with_its_alternative(registry: RuleRegistry) -> None:
    payload = json.loads(json.dumps(calculate(registry, "23:45").as_dict(registry), ensure_ascii=False))

    assert payload["status"] == "complete"
    assert payload["pillars"] == {
        "year": "丙午", "month": "甲午", "day": "庚申", "hour": "丙子", "day_master": "庚",
    }
    assert payload["alternative_candidate"]["pillars"]["day"] == "辛酉"
    assert payload["provenance"]["solar_term_instants_v1"] == "2.0.0"
    assert CalculationNotice.ZI_HOUR_DUAL_VIEW in payload["notices"]


def test_the_result_records_the_birth_profile_it_came_from(registry: RuleRegistry) -> None:
    profile = normalize_birth_input(RawBirthInput("solar", 2026, 6, 15, "10:30", gender="male"))[0]

    calculation = saju_calculation_for_profile(profile, registry)

    assert calculation.birth_profile_id == profile.profile_id
    assert calculation.result_version == "1.0"


def test_the_calculator_rejects_a_raw_input_instead_of_a_profile(registry: RuleRegistry) -> None:
    with pytest.raises(TypeError):
        saju_calculation_for_profile(RawBirthInput("solar", 2026, 6, 15, "10:30"), registry)  # type: ignore[arg-type]
