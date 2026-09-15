"""Solar-term data availability gate.

Year and month pillars depend on versioned, production-verified solar-term
instants. Until that dataset exists, callers receive a specific diagnostic
instead of a guessed term boundary.
"""

from __future__ import annotations

from datetime import datetime

from .data_registry import DatasetError, RuleRegistry
from .diagnostics import DiagnosticCode


_SOLAR_TERM_DATASET_ID = "solar_term_instants_v1"


def solar_term_for_datetime(resolved_local_datetime: datetime, registry: RuleRegistry) -> None:
    """Refuse solar-term lookup until production-verified term instants exist."""

    if type(resolved_local_datetime) is not datetime:
        raise TypeError("resolved_local_datetime must be a datetime.datetime instance")
    try:
        registry.load(_SOLAR_TERM_DATASET_ID)
    except DatasetError as error:
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            "production-verified solar-term instants are required",
        ) from error
    raise DatasetError(
        DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
        "solar-term calculation is not implemented",
    )
