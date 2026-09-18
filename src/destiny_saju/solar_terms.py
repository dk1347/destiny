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
    """Return the most recent solar term at an Asia/Seoul local instant.

    Raises
    ------
    TypeError
        If *resolved_local_datetime* is not a timezone-aware datetime in KST (+09:00).
    DatasetError(SOLAR_TERM_DATA_UNAVAILABLE)
        If the instant falls outside every verified coverage range, or in a gap
        between two ranges, or if no production-verified dataset is loaded.
        The error message includes the queried year so callers can surface it.
    """
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
    ranges = [
        (
            datetime.fromisoformat(rng["coverage_start"]),
            datetime.fromisoformat(rng["coverage_end"]),
        )
        for rng in data["coverage_ranges"]
    ]

    # fail-closed: datetime must fall inside at least one declared range.
    # Include the queried year in the error so callers can surface it to users.
    if not any(rs <= resolved_local_datetime <= re for rs, re in ranges):
        queried_year = resolved_local_datetime.year
        raise DatasetError(
            DiagnosticCode.SOLAR_TERM_DATA_UNAVAILABLE,
            f"{queried_year}년의 절기 데이터가 아직 준비되지 않았어요.",
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
