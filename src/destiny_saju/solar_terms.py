"""Solar-term lookup from production-verified local instants."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .data_registry import DatasetError, RuleRegistry
from .diagnostics import DiagnosticCode


_SOLAR_TERM_DATASET_ID = "solar_term_instants_v1"


@dataclass(frozen=True)
class SolarTerm:
    id: str
    occurs_at: datetime


def solar_term_for_datetime(resolved_local_datetime: datetime, registry: RuleRegistry) -> SolarTerm:
    """Return the most recent solar term at an Asia/Seoul local instant."""

    if type(resolved_local_datetime) is not datetime:
        raise TypeError("resolved_local_datetime must be a datetime.datetime instance")
    if resolved_local_datetime.tzinfo is None:
        raise TypeError("resolved_local_datetime must be timezone-aware")
    if resolved_local_datetime.utcoffset() != timedelta(hours=9):
        raise TypeError("resolved_local_datetime must use the Asia/Seoul UTC offset")
    try:
        registry.load(_SOLAR_TERM_DATASET_ID)
    except DatasetError as error:
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            "production-verified solar-term instants are required",
        ) from error
    data = registry.load(_SOLAR_TERM_DATASET_ID)["data"]
    coverage_ranges = [
        (datetime.fromisoformat(row["coverage_start"]), datetime.fromisoformat(row["coverage_end"]))
        for row in data["coverage_ranges"]
    ]
    if not any(start <= resolved_local_datetime <= end for start, end in coverage_ranges):
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            "no production-verified solar-term instant covers this datetime",
        )
    terms = [
        SolarTerm(row["id"], datetime.fromisoformat(row["occurs_at"]))
        for row in data["terms"]
    ]
    active = [term for term in terms if term.occurs_at <= resolved_local_datetime]
    if not active:
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            "no production-verified solar-term instant covers this datetime",
        )
    return active[-1]
