"""Day-pillar calculation gate.

The calculation contract requires a production-verified sexagenary-day anchor.
No such anchor is packaged yet, so this public entry point intentionally fails
closed instead of deriving a day pillar from an unverified candidate fixture.
"""

from __future__ import annotations

from datetime import date

from .data_registry import DatasetError, RuleRegistry
from .diagnostics import DiagnosticCode


_ANCHOR_DATASET_ID = "day_pillar_anchor_v1"


def day_pillar_for_date(civil_date: date, registry: RuleRegistry) -> None:
    """Refuse day-pillar calculation until a verified anchor is supplied.

    ``civil_date`` is deliberately accepted now to establish the public
    calculation boundary: callers must resolve the local civil date before
    reaching this module. The future implementation will consume the same
    value with a production-verified anchor under this dataset id.
    """

    if type(civil_date) is not date:
        raise TypeError("civil_date must be a datetime.date instance")
    try:
        registry.load(_ANCHOR_DATASET_ID)
    except DatasetError as error:
        raise DatasetError(
            DiagnosticCode.DAY_PILLAR_ANCHOR_UNAVAILABLE,
            "a production-verified day-pillar anchor is required",
        ) from error
    raise DatasetError(
        DiagnosticCode.DAY_PILLAR_ANCHOR_UNAVAILABLE,
        "day-pillar anchor calculation is not implemented",
    )
