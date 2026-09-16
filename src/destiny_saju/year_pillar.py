"""Year pillar calculation using the verified ipchun boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .branches import EarthlyBranch
from .data_registry import DatasetError, RuleRegistry
from .diagnostics import DiagnosticCode
from .solar_terms import solar_term_for_datetime
from .stems import HeavenlyStem
from .tables import ordered_branches, ordered_stems


_JIA_ZI_YEAR = 1984


@dataclass(frozen=True)
class YearPillar:
    stem: HeavenlyStem
    branch: EarthlyBranch


def year_pillar_for_datetime(resolved_local_datetime: datetime, registry: RuleRegistry) -> YearPillar:
    """Return the ipchun-bounded year pillar for a verified local instant."""

    # This call performs the strict local-time and coverage checks shared by
    # every solar-term-backed calculation.
    solar_term_for_datetime(resolved_local_datetime, registry)
    data = registry.load("solar_term_instants_v1")["data"]
    ipchun_instants = [
        datetime.fromisoformat(row["occurs_at"])
        for row in data["terms"]
        if row["id"] == "ipchun"
        and datetime.fromisoformat(row["occurs_at"]).year == resolved_local_datetime.year
    ]
    if len(ipchun_instants) != 1:
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            "no production-verified ipchun instant covers this datetime",
        )
    sexagenary_year = resolved_local_datetime.year
    if resolved_local_datetime < ipchun_instants[0]:
        sexagenary_year -= 1
    offset = sexagenary_year - _JIA_ZI_YEAR
    stems = ordered_stems(registry)
    branches = ordered_branches(registry)
    return YearPillar(stems[offset % 10], branches[offset % 12])
