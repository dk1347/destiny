"""Explicit calculation-profile choices supported by the Saju core."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DayBoundary(Enum):
    """The instant at which the day pillar advances."""

    MIDNIGHT = "midnight"
    ZI_HOUR_START = "zi_hour_start"


@dataclass(frozen=True)
class CalculationProfile:
    """A versioned, deterministic set of calculation choices.

    The core currently supports only legal local time. True-solar-time profiles
    require the separate time-resolution evidence gate before implementation.
    """

    profile_id: str
    day_boundary: DayBoundary

    def __post_init__(self) -> None:
        if not self.profile_id:
            raise ValueError("profile_id must not be empty")
        if not isinstance(self.day_boundary, DayBoundary):
            raise TypeError("day_boundary must be a DayBoundary instance")


KR_STANDARD_V1 = CalculationProfile(
    profile_id="kr_standard_v1",
    day_boundary=DayBoundary.ZI_HOUR_START,
)

MIDNIGHT_V1 = CalculationProfile(
    profile_id="midnight_v1",
    day_boundary=DayBoundary.MIDNIGHT,
)
