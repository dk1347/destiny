"""Immutable, provenance-bearing result for a resolved Four Pillars calculation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .calculation_profile import CalculationProfile, KR_STANDARD_V1
from .data_registry import RuleRegistry
from .four_pillars import FourPillars, ThreePillars, four_pillars_for_datetime, three_pillars_for_date


@dataclass(frozen=True)
class SajuResult:
    result_version: str
    calculation_profile_id: str
    status: str
    pillars: FourPillars | ThreePillars
    dataset_versions: tuple[tuple[str, str], ...]
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-ready public result without exposing runtime objects."""

        def pillar(value: object | None) -> dict[str, str] | None:
            if value is None:
                return None
            return {"stem": value.stem.value, "branch": value.branch.value}  # type: ignore[attr-defined]

        return {
            "result_version": self.result_version,
            "calculation_profile_id": self.calculation_profile_id,
            "status": self.status,
            "pillars": {
                "year": pillar(self.pillars.year), "month": pillar(self.pillars.month),
                "day": pillar(self.pillars.day), "hour": pillar(getattr(self.pillars, "hour", None)),
            },
            "warnings": list(self.warnings),
            "provenance": {dataset_id: version for dataset_id, version in self.dataset_versions},
        }


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


def saju_result_for_date(local_date: date, registry: RuleRegistry) -> SajuResult:
    """Create a verified three-pillar result for a date with unknown birth time."""

    pillars = three_pillars_for_date(local_date, registry)
    return SajuResult(
        result_version="1.0",
        calculation_profile_id="kr_standard_v1",
        status="partial",
        pillars=pillars,
        dataset_versions=registry.loaded_dataset_versions(),
        warnings=("출생시간이 없어 시주는 포함하지 않았어요.",),
    )
