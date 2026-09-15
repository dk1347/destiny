"""Month pillar calculation from verified major solar-term boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .branches import EarthlyBranch
from .data_registry import DatasetError, RuleRegistry
from .diagnostics import DiagnosticCode
from .month_stem import month_stem_for
from .solar_terms import solar_term_for_datetime
from .stems import HeavenlyStem
from .year_pillar import year_pillar_for_datetime


@dataclass(frozen=True)
class MonthPillar:
    stem: HeavenlyStem
    branch: EarthlyBranch


def month_pillar_for_datetime(resolved_local_datetime: datetime, registry: RuleRegistry) -> MonthPillar:
    """Return the solar-term-bounded month pillar for a verified local instant."""

    solar_term_for_datetime(resolved_local_datetime, registry)
    data = registry.load("solar_term_instants_v1")["data"]
    major_terms = {
        row["term"]: EarthlyBranch(row["branch"])
        for row in registry.load("core_tables_v1")["data"]["month_branch_by_major_solar_term"]
    }
    active_major = next(
        (
            row["id"]
            for row in reversed(data["terms"])
            if datetime.fromisoformat(row["occurs_at"]) <= resolved_local_datetime and row["id"] in major_terms
        ),
        None,
    )
    if active_major is None:
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            "no production-verified major solar-term boundary covers this datetime",
        )
    branch = major_terms[active_major]
    stem = month_stem_for(year_pillar_for_datetime(resolved_local_datetime, registry).stem, branch, registry)
    return MonthPillar(stem, branch)
