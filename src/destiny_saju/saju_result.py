"""Immutable, provenance-bearing result for a resolved Four Pillars calculation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .calculation_profile import CalculationProfile, KR_STANDARD_V1
from .data_registry import RuleRegistry
from .four_pillars import FourPillars, four_pillars_for_datetime


@dataclass(frozen=True)
class SajuResult:
    result_version: str
    calculation_profile_id: str
    status: str
    pillars: FourPillars
    dataset_versions: tuple[tuple[str, str], ...]
    warnings: tuple[str, ...] = ()


def saju_result_for_datetime(
    resolved_local_datetime: datetime,
    registry: RuleRegistry,
    profile: CalculationProfile = KR_STANDARD_V1,
) -> SajuResult:
    """Create a complete result for one already-resolved local datetime."""

    pillars = four_pillars_for_datetime(resolved_local_datetime, registry, profile)
    return SajuResult(
        result_version="1.0",
        calculation_profile_id=profile.profile_id,
        status="complete",
        pillars=pillars,
        dataset_versions=registry.loaded_dataset_versions(),
    )
