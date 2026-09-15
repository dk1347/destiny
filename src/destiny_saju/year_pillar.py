"""Year pillar calculation using the verified ipchun boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .branches import EarthlyBranch
from .data_registry import RuleRegistry
from .solar_terms import solar_term_for_datetime
from .stems import HeavenlyStem


_JIA_ZI_YEAR = 1984


@dataclass(frozen=True)
class YearPillar:
    stem: HeavenlyStem
    branch: EarthlyBranch


def year_pillar_for_datetime(resolved_local_datetime: datetime, registry: RuleRegistry) -> YearPillar:
    """Return the ipchun-bounded year pillar for a verified local instant."""

    active_term = solar_term_for_datetime(resolved_local_datetime, registry)
    sexagenary_year = resolved_local_datetime.year
    if active_term.id in {"dongji", "sohan", "daehan"}:
        sexagenary_year -= 1
    offset = sexagenary_year - _JIA_ZI_YEAR
    return YearPillar(list(HeavenlyStem)[offset % 10], list(EarthlyBranch)[offset % 12])
