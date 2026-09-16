"""Sexagenary day-pillar calculation from a verified civil-date anchor."""

from __future__ import annotations

from datetime import date
from dataclasses import dataclass

from .branches import EarthlyBranch
from .data_registry import DatasetError, RuleRegistry
from .diagnostics import DiagnosticCode
from .stems import HeavenlyStem
from .tables import ordered_branches, ordered_stems


_ANCHOR_DATASET_ID = "day_pillar_anchor_v1"


@dataclass(frozen=True)
class DayPillar:
    stem: HeavenlyStem
    branch: EarthlyBranch


def day_pillar_for_date(civil_date: date, registry: RuleRegistry) -> DayPillar:
    """Return the sexagenary day for an already-resolved local civil date."""

    if type(civil_date) is not date:
        raise TypeError("civil_date must be a datetime.date instance")
    try:
        anchor = registry.load(_ANCHOR_DATASET_ID)["data"]
    except DatasetError as error:
        raise DatasetError(
            DiagnosticCode.DAY_PILLAR_ANCHOR_UNAVAILABLE,
            "a production-verified day-pillar anchor is required",
        ) from error

    anchor_date = date.fromisoformat(anchor["anchor_date"])
    offset = (civil_date - anchor_date).days
    index = anchor["sexagenary_index_1_based"] - 1 + offset
    stems = ordered_stems(registry)
    branches = ordered_branches(registry)
    return DayPillar(stems[index % 10], branches[index % 12])
