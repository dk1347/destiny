"""Compose a complete Saju result from a normalized birth profile.

This is the engine layer described by ``docs/04_SAJU_CALCULATION_SPEC.md``. It
does not re-derive any calendar fact: the birth profile already resolved civil
time, and the rule datasets already hold every verified table. What this module
owns is the *composition* — which timeline each pillar is decided on, which
day-boundary doctrine is the default, and which uncertainties must be stated
rather than silently resolved.

Three uncertainties are deliberately surfaced instead of hidden:

* A birth within ±15 minutes of a 절입 instant is flagged, because a recorded
  clock time is not accurate enough to settle the month pillar there.
* A birth in the 23:00 hour produces a second, classical-doctrine result so the
  UI can show both readings side by side.
* An unknown birth time never becomes an hour pillar, and on a 절입 day it does
  not become a single year/month pillar either.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from ..birth.profile import AnalysisMode, Gender, NormalizedBirthProfile
from ..calculation_profile import KR_STANDARD_V1, MIDNIGHT_V1, CalculationProfile, DayBoundary
from ..data_registry import RuleRegistry
from ..day_pillar import DayPillar, day_pillar_for_date
from ..four_pillars import FourPillars, HourPillar, ThreePillars
from ..hour_branch import hour_branch_for_time
from ..hour_stem import hour_stem_for
from ..month_pillar import MonthPillar, month_pillar_for_datetime
from ..ten_gods import TenGod, ten_god_for
from ..year_pillar import YearPillar, year_pillar_for_datetime
from .daewun import DEFAULT_CYCLE_COUNT, Daewun, daewun_for
from .display import pillar_hanja, stem_hanja, ten_god_label
from .timeline import (
    CalculationTimeline,
    is_season_boundary_adjacent,
    major_term_on_date,
    timeline_for_profile,
)

RESULT_VERSION = "1.0"


class DayBoundaryDoctrine(StrEnum):
    """Which school decides the day pillar inside the 23:00 hour."""

    MODERN_MAJORITY = "modern_majority_ya_ja_si"
    CLASSICAL = "classical_jeong_ja_si"


DOCTRINE_LABELS: dict[DayBoundaryDoctrine, str] = {
    DayBoundaryDoctrine.MODERN_MAJORITY: "현대 다수설(야자시·조자시설) 기준 산출",
    DayBoundaryDoctrine.CLASSICAL: "고전 원칙론(정자시설) 기준 산출",
}

DOCTRINE_PROFILES: dict[DayBoundaryDoctrine, CalculationProfile] = {
    DayBoundaryDoctrine.MODERN_MAJORITY: MIDNIGHT_V1,
    DayBoundaryDoctrine.CLASSICAL: KR_STANDARD_V1,
}

#: The corrected-time hour whose day pillar depends on the chosen doctrine.
ZI_HOUR_DUAL_VIEW_HOUR = 23


class CalculationNotice(StrEnum):
    """Flags a result carries so a caller never has to infer uncertainty."""

    SEASON_BOUNDARY_ADJACENT = "SEASON_BOUNDARY_ADJACENT"
    SEASON_BOUNDARY_CANDIDATE_BRANCH = "SEASON_BOUNDARY_CANDIDATE_BRANCH"
    ZI_HOUR_DUAL_VIEW = "ZI_HOUR_DUAL_VIEW"
    TIME_PRECISION_APPROXIMATE = "TIME_PRECISION_APPROXIMATE"
    DAEWUN_EXCHANGE_PRECISION = "DAEWUN_EXCHANGE_PRECISION"
    DAEWUN_GENDER_REQUIRED = "DAEWUN_GENDER_REQUIRED"


NOTICE_MESSAGES: dict[CalculationNotice, str] = {
    CalculationNotice.SEASON_BOUNDARY_ADJACENT: (
        "출생 시각이 절기 절입 시각(입춘/경칩 등)과 매우 인접합니다. 출생 당시의 시계 기록 오차 및 "
        "자연시차 요인으로 인해 월주(또는 연주)가 이전/이후 절기 기준으로 다르게 해석될 가능성이 있습니다."
    ),
    CalculationNotice.SEASON_BOUNDARY_CANDIDATE_BRANCH: (
        "출생일이 절기 절입일과 겹치는데 출생 시각이 확인되지 않아 연주·월주를 하나로 확정하지 "
        "않았습니다. 절입 전후 두 가지 후보를 모두 제시하니 출생 시각을 확인해 주세요."
    ),
    CalculationNotice.ZI_HOUR_DUAL_VIEW: (
        "밤 11시~12시 구간은 명리학 전통 학설(야자시설 vs 정자시설)에 따라 일진(태어난 날)의 기운이 "
        "다르게 적용될 수 있습니다. 본 시스템은 현대 다수설을 기본으로 산출하며, 고전 원칙론 기준의 "
        "명식도 함께 비교해 보실 수 있습니다."
    ),
    CalculationNotice.TIME_PRECISION_APPROXIMATE: (
        "정확한 분 단위 출생 기록이 확인되지 않아 시주(말년·자녀궁)를 임의 추정하지 않고 제외한 "
        "삼주(6자) 체계로 정밀 분석합니다. 대운수 및 교운기는 관례에 따라 정오 기준으로 산출되었으므로 "
        "약 ±1세의 차이가 발생할 수 있습니다."
    ),
    CalculationNotice.DAEWUN_EXCHANGE_PRECISION: (
        "출생 분 및 균시차 등의 요인으로 교운 시점의 정확도가 다소 떨어질 수 있습니다."
    ),
    CalculationNotice.DAEWUN_GENDER_REQUIRED: (
        "대운은 성별에 따라 순행·역행이 달라져 성별 기록 없이는 산출하지 않았습니다."
    ),
}


@dataclass(frozen=True)
class SeasonCandidate:
    """One of the two readings available when a 절입 day has no birth time."""

    label: str
    term_id: str
    term_occurs_at: datetime
    year: YearPillar
    month: MonthPillar
    applies_when: str


@dataclass(frozen=True)
class SajuCalculation:
    """An immutable, provenance-bearing result for one birth profile."""

    result_version: str
    birth_profile_id: str
    status: str
    analysis_mode: AnalysisMode
    calculation_profile_id: str
    day_boundary_doctrine: DayBoundaryDoctrine
    day_boundary_doctrine_label: str
    timeline_policy_id: str
    civil_time_policy_id: str
    season_basis_datetime: datetime
    pillar_basis_datetime: datetime
    day_pillar: DayPillar
    pillars: FourPillars | ThreePillars | None
    ten_gods: tuple[tuple[str, TenGod], ...]
    daewun: Daewun | None
    season_candidates: tuple[SeasonCandidate, ...]
    alternative_candidate: "SajuCalculation | None"
    notices: tuple[CalculationNotice, ...]
    warnings: tuple[str, ...]
    dataset_versions: tuple[tuple[str, str], ...]

    def as_dict(self, registry: RuleRegistry) -> dict[str, object]:
        """Return a JSON-ready result using the project's notation standard."""

        return {
            "result_version": self.result_version,
            "birth_profile_id": self.birth_profile_id,
            "status": self.status,
            "analysis_mode": str(self.analysis_mode),
            "calculation_profile_id": self.calculation_profile_id,
            "day_boundary_doctrine": str(self.day_boundary_doctrine),
            "day_boundary_doctrine_label": self.day_boundary_doctrine_label,
            "timeline_policy_id": self.timeline_policy_id,
            "civil_time_policy_id": self.civil_time_policy_id,
            "season_basis_datetime": self.season_basis_datetime.isoformat(),
            "pillar_basis_datetime": self.pillar_basis_datetime.isoformat(),
            "pillars": self._pillars_dict(registry),
            "ten_gods": {
                position: ten_god_label(ten_god, registry) for position, ten_god in self.ten_gods
            },
            "daewun": self._daewun_dict(registry),
            "season_candidates": [
                {
                    "label": candidate.label,
                    "term_id": candidate.term_id,
                    "term_occurs_at": candidate.term_occurs_at.isoformat(),
                    "year": pillar_hanja(candidate.year.stem, candidate.year.branch, registry),
                    "month": pillar_hanja(candidate.month.stem, candidate.month.branch, registry),
                    "applies_when": candidate.applies_when,
                }
                for candidate in self.season_candidates
            ],
            "alternative_candidate": (
                None if self.alternative_candidate is None
                else self.alternative_candidate.as_dict(registry)
            ),
            "notices": [str(notice) for notice in self.notices],
            "warnings": list(self.warnings),
            "provenance": {dataset_id: version for dataset_id, version in self.dataset_versions},
        }

    def _pillars_dict(self, registry: RuleRegistry) -> dict[str, str | None]:
        def rendered(pillar: object | None) -> str | None:
            if pillar is None:
                return None
            return pillar_hanja(pillar.stem, pillar.branch, registry)  # type: ignore[attr-defined]

        pillars = self.pillars
        return {
            "year": rendered(getattr(pillars, "year", None)),
            "month": rendered(getattr(pillars, "month", None)),
            "day": rendered(self.day_pillar),
            "hour": rendered(getattr(pillars, "hour", None)),
            "day_master": stem_hanja(self.day_pillar.stem, registry),
        }

    def _daewun_dict(self, registry: RuleRegistry) -> dict[str, object] | None:
        if self.daewun is None:
            return None
        return {
            "method_id": self.daewun.method_id,
            "direction": str(self.daewun.direction),
            "boundary_term_id": self.daewun.boundary_term_id,
            "boundary_instant": self.daewun.boundary_instant.isoformat(),
            "source_day_difference": self.daewun.source_day_difference,
            "daewun_raw_float": self.daewun.daewun_raw_float,
            "daewun_number": self.daewun.daewun_number,
            "first_exchange_at": self.daewun.first_exchange_at.isoformat(),
            "is_anchor_approximate": self.daewun.is_anchor_approximate,
            "cycles": [
                {
                    "sequence": cycle.sequence,
                    "pillar": pillar_hanja(cycle.stem, cycle.branch, registry),
                    "starts_at": cycle.starts_at.isoformat(),
                    "exchange_year_month": f"{cycle.starts_at.year:04d}-{cycle.starts_at.month:02d}",
                    "start_age_display": cycle.start_age_display,
                    "start_age_years": cycle.start_age_years,
                }
                for cycle in self.daewun.cycles
            ],
        }


def saju_calculation_for_profile(
    profile: NormalizedBirthProfile,
    registry: RuleRegistry,
    *,
    doctrine: DayBoundaryDoctrine = DayBoundaryDoctrine.MODERN_MAJORITY,
    cycle_count: int = DEFAULT_CYCLE_COUNT,
) -> SajuCalculation:
    """Calculate one birth profile under the default modern-majority doctrine."""

    return _calculate(profile, registry, doctrine, cycle_count, with_alternative=True)


def _calculate(
    profile: NormalizedBirthProfile,
    registry: RuleRegistry,
    doctrine: DayBoundaryDoctrine,
    cycle_count: int,
    *,
    with_alternative: bool,
) -> SajuCalculation:
    if not isinstance(profile, NormalizedBirthProfile):
        raise TypeError("profile must be a NormalizedBirthProfile instance")
    if doctrine not in DOCTRINE_PROFILES:
        raise ValueError("doctrine must be a DayBoundaryDoctrine member")

    timeline = timeline_for_profile(profile)
    calculation_profile = DOCTRINE_PROFILES[doctrine]
    day_pillar = day_pillar_for_date(_pillar_date(timeline, calculation_profile), registry)

    notices: list[CalculationNotice] = []
    boundary_term = (
        major_term_on_date(timeline.season_basis.date(), registry)
        if timeline.is_anchor_approximate else None
    )

    if timeline.is_anchor_approximate:
        notices.append(CalculationNotice.TIME_PRECISION_APPROXIMATE)
    elif is_season_boundary_adjacent(timeline.season_basis, registry):
        notices.append(CalculationNotice.SEASON_BOUNDARY_ADJACENT)

    if boundary_term is not None:
        notices.append(CalculationNotice.SEASON_BOUNDARY_CANDIDATE_BRANCH)
        candidates = _season_candidates(boundary_term, registry)
        pillars: FourPillars | ThreePillars | None = None
        status = "candidate_branch"
        daewun = None
    else:
        candidates = ()
        year = year_pillar_for_datetime(timeline.season_basis, registry)
        month = month_pillar_for_datetime(timeline.season_basis, registry)
        if profile.analysis_mode is AnalysisMode.FOUR_PILLARS:
            branch = hour_branch_for_time(timeline.pillar_basis.timetz())
            pillars = FourPillars(
                year, month, day_pillar, HourPillar(hour_stem_for(day_pillar.stem, branch, registry), branch)
            )
            status = "complete"
        else:
            pillars = ThreePillars(year, month, day_pillar)
            status = "partial"
        daewun = _daewun_or_none(profile, timeline, year, month, registry, cycle_count, notices)

    alternative = None
    if timeline.pillar_basis.hour == ZI_HOUR_DUAL_VIEW_HOUR:
        notices.append(CalculationNotice.ZI_HOUR_DUAL_VIEW)
        if with_alternative:
            alternative = _calculate(
                profile, registry, _opposite(doctrine), cycle_count, with_alternative=False
            )

    return SajuCalculation(
        result_version=RESULT_VERSION,
        birth_profile_id=profile.profile_id,
        status=status,
        analysis_mode=profile.analysis_mode,
        calculation_profile_id=calculation_profile.profile_id,
        day_boundary_doctrine=doctrine,
        day_boundary_doctrine_label=DOCTRINE_LABELS[doctrine],
        timeline_policy_id=timeline.policy_id,
        civil_time_policy_id=profile.civil_time_policy_id,
        season_basis_datetime=timeline.season_basis,
        pillar_basis_datetime=timeline.pillar_basis,
        day_pillar=day_pillar,
        pillars=pillars,
        ten_gods=_ten_gods_for(pillars, day_pillar, registry),
        daewun=daewun,
        season_candidates=candidates,
        alternative_candidate=alternative,
        notices=tuple(notices),
        warnings=tuple(NOTICE_MESSAGES[notice] for notice in notices),
        dataset_versions=registry.loaded_dataset_versions(),
    )


def _pillar_date(timeline: CalculationTimeline, calculation_profile: CalculationProfile):
    """Advance the day pillar at 23:00 only under the classical doctrine."""

    pillar_date = timeline.pillar_basis.date()
    if (calculation_profile.day_boundary is DayBoundary.ZI_HOUR_START
            and timeline.pillar_basis.hour >= ZI_HOUR_DUAL_VIEW_HOUR):
        pillar_date += timedelta(days=1)
    return pillar_date


def _season_candidates(boundary_term, registry: RuleRegistry) -> tuple[SeasonCandidate, ...]:
    before_instant = boundary_term.occurs_at - timedelta(minutes=1)
    clock = f"{boundary_term.occurs_at:%H:%M}"
    return (
        SeasonCandidate(
            label="before_term",
            term_id=boundary_term.id,
            term_occurs_at=boundary_term.occurs_at,
            year=year_pillar_for_datetime(before_instant, registry),
            month=month_pillar_for_datetime(before_instant, registry),
            applies_when=f"{clock} 이전 출생인 경우",
        ),
        SeasonCandidate(
            label="after_term",
            term_id=boundary_term.id,
            term_occurs_at=boundary_term.occurs_at,
            year=year_pillar_for_datetime(boundary_term.occurs_at, registry),
            month=month_pillar_for_datetime(boundary_term.occurs_at, registry),
            applies_when=f"{clock} 이후 출생인 경우",
        ),
    )


def _daewun_or_none(
    profile: NormalizedBirthProfile,
    timeline: CalculationTimeline,
    year: YearPillar,
    month: MonthPillar,
    registry: RuleRegistry,
    cycle_count: int,
    notices: list[CalculationNotice],
) -> Daewun | None:
    if profile.raw_input.gender is Gender.UNKNOWN:
        notices.append(CalculationNotice.DAEWUN_GENDER_REQUIRED)
        return None
    daewun = daewun_for(
        timeline.season_basis,
        year,
        month,
        str(profile.raw_input.gender),
        registry,
        is_anchor_approximate=timeline.is_anchor_approximate,
        cycle_count=cycle_count,
    )
    notices.append(CalculationNotice.DAEWUN_EXCHANGE_PRECISION)
    return daewun


def _ten_gods_for(
    pillars: FourPillars | ThreePillars | None, day_pillar: DayPillar, registry: RuleRegistry
) -> tuple[tuple[str, TenGod], ...]:
    if pillars is None:
        return ()
    positions = [("year", pillars.year.stem), ("month", pillars.month.stem)]
    hour = getattr(pillars, "hour", None)
    if hour is not None:
        positions.append(("hour", hour.stem))
    return tuple(
        (position, ten_god_for(day_pillar.stem, stem, registry)) for position, stem in positions
    )


def _opposite(doctrine: DayBoundaryDoctrine) -> DayBoundaryDoctrine:
    if doctrine is DayBoundaryDoctrine.MODERN_MAJORITY:
        return DayBoundaryDoctrine.CLASSICAL
    return DayBoundaryDoctrine.MODERN_MAJORITY
