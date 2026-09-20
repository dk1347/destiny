"""The calculation engine layer: a normalized birth profile becomes a result.

Read ``timeline`` first — it defines which instant each pillar is decided on,
and every other module in this package depends on that distinction.
"""

from .daewun import (
    DAEWUN_METHOD_ID,
    DAYS_PER_FORTUNE_YEAR,
    DEFAULT_CYCLE_COUNT,
    MEAN_YEAR_DAYS,
    Daewun,
    DaewunCycle,
    DaewunDirection,
    daewun_direction_for,
    daewun_for,
    round_daewun_number,
)
from .display import (
    branch_hanja,
    format_korean_with_hanja,
    pillar_hanja,
    stem_hanja,
    ten_god_label,
)
from .saju_calculation import (
    DOCTRINE_LABELS,
    DOCTRINE_PROFILES,
    NOTICE_MESSAGES,
    RESULT_VERSION,
    ZI_HOUR_DUAL_VIEW_HOUR,
    CalculationNotice,
    DayBoundaryDoctrine,
    SajuCalculation,
    SeasonCandidate,
    saju_calculation_for_profile,
)
from .timeline import (
    SEASON_BOUNDARY_WINDOW,
    TIMELINE_POLICY_ID,
    UNKNOWN_TIME_ANCHOR,
    CalculationTimeline,
    is_season_boundary_adjacent,
    major_solar_terms,
    major_term_on_date,
    nearest_major_term,
    timeline_for_profile,
)

__all__ = [
    "CalculationNotice", "CalculationTimeline", "DAEWUN_METHOD_ID", "DAYS_PER_FORTUNE_YEAR",
    "DEFAULT_CYCLE_COUNT", "DOCTRINE_LABELS", "DOCTRINE_PROFILES", "Daewun", "DaewunCycle",
    "DaewunDirection", "DayBoundaryDoctrine", "MEAN_YEAR_DAYS", "NOTICE_MESSAGES",
    "RESULT_VERSION", "SEASON_BOUNDARY_WINDOW", "SajuCalculation", "SeasonCandidate",
    "TIMELINE_POLICY_ID", "UNKNOWN_TIME_ANCHOR", "ZI_HOUR_DUAL_VIEW_HOUR", "branch_hanja",
    "daewun_direction_for", "daewun_for", "format_korean_with_hanja",
    "is_season_boundary_adjacent", "major_solar_terms", "major_term_on_date",
    "nearest_major_term", "pillar_hanja", "round_daewun_number", "saju_calculation_for_profile", "stem_hanja",
    "ten_god_label", "timeline_for_profile",
]
