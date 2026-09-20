"""One timeline for every instant comparison made during a calculation.

The engine compares two kinds of time that are easy to mix up:

``season_basis``
    The **absolute instant** of birth, expressed on the KST wall clock that the
    verified solar-term table itself is published on. Year and month pillars are
    decided here.
``pillar_basis``
    The **corrected local time** from the birth profile (standard-meridian and
    historical summer-time corrections already applied). Day and hour pillars —
    the ones that depend on where the sun actually is — are decided here.

Keeping them apart is what prevents the double correction described in
``docs/54_TRUE_SOLAR_TIME_OPTION_SPEC.md``. A solar-term instant and a birth
instant are both points on the same absolute timeline, so a −30 minute meridian
shift moves *both* by the same amount and cancels out of the comparison;
applying it to only the birth side would silently move a pillar across a term
boundary. ``season_basis`` therefore never carries the meridian correction, and
``pillar_basis`` always does.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from ..birth.civil_time import KST, adjusted_solar_datetime, resolve_civil_time, utc_timestamp_for
from ..birth.profile import NormalizedBirthProfile
from ..data_registry import RuleRegistry
from ..solar_terms import SolarTerm

TIMELINE_POLICY_ID = "unified_instant_v1"

#: A birth this close to a major term is reported as boundary-adjacent.
SEASON_BOUNDARY_WINDOW = timedelta(minutes=15)

#: The clock time used as an anchor when the birth time was never recorded.
UNKNOWN_TIME_ANCHOR = time(12, 0)


@dataclass(frozen=True)
class CalculationTimeline:
    """The two resolved instants a calculation is allowed to compare against."""

    season_basis: datetime
    pillar_basis: datetime
    is_anchor_approximate: bool
    policy_id: str = TIMELINE_POLICY_ID

    def __post_init__(self) -> None:
        for value in (self.season_basis, self.pillar_basis):
            if value.tzinfo is None or value.utcoffset() != timedelta(hours=9):
                raise TypeError("timeline instants must be KST (+09:00) datetimes")


def timeline_for_profile(profile: NormalizedBirthProfile) -> CalculationTimeline:
    """Resolve both calculation bases from a normalized birth profile.

    When the birth time is unknown the profile deliberately holds no instant, so
    a 12:00 anchor is built here instead. The anchor is used only to place the
    birth between two solar terms for the fortune-cycle count; it never becomes
    an hour pillar, and it is reported through ``is_anchor_approximate``.
    """

    if not isinstance(profile, NormalizedBirthProfile):
        raise TypeError("profile must be a NormalizedBirthProfile instance")

    if profile.normalized_utc_timestamp is not None:
        pillar_basis = profile.calculation_basis_datetime()
        assert pillar_basis is not None  # guaranteed together by the profile
        return CalculationTimeline(
            season_basis=profile.normalized_utc_timestamp.astimezone(KST),
            pillar_basis=pillar_basis,
            is_anchor_approximate=False,
        )

    civil_anchor = datetime.combine(profile.civil_solar_date, UNKNOWN_TIME_ANCHOR)
    resolution = resolve_civil_time(profile.civil_solar_date)
    return CalculationTimeline(
        season_basis=utc_timestamp_for(civil_anchor, resolution).astimezone(KST),
        pillar_basis=adjusted_solar_datetime(civil_anchor, resolution).replace(tzinfo=KST),
        is_anchor_approximate=True,
    )


def major_solar_terms(registry: RuleRegistry) -> tuple[SolarTerm, ...]:
    """Return the verified 절입 instants that move a month or year pillar."""

    major_ids = {
        row["term"]
        for row in registry.load("core_tables_v1")["data"]["month_branch_by_major_solar_term"]
    }
    terms = registry.load("solar_term_instants_v1")["data"]["terms"]
    return tuple(sorted(
        (
            SolarTerm(row["id"], datetime.fromisoformat(row["occurs_at"]))
            for row in terms
            if row["id"] in major_ids
        ),
        key=lambda term: term.occurs_at,
    ))


def nearest_major_term(instant: datetime, registry: RuleRegistry) -> tuple[SolarTerm, timedelta] | None:
    """Return the closest 절입 to an instant and the unsigned gap to it."""

    terms = major_solar_terms(registry)
    if not terms:
        return None
    term = min(terms, key=lambda candidate: abs(candidate.occurs_at - instant))
    return term, abs(term.occurs_at - instant)


def is_season_boundary_adjacent(instant: datetime, registry: RuleRegistry) -> bool:
    """Report a birth within ±15 minutes of a verified 절입 instant."""

    nearest = nearest_major_term(instant, registry)
    return nearest is not None and nearest[1] <= SEASON_BOUNDARY_WINDOW


def major_term_on_date(civil_date: date, registry: RuleRegistry) -> SolarTerm | None:
    """Return the 절입 falling on a KST calendar date, if one does."""

    for term in major_solar_terms(registry):
        if term.occurs_at.date() == civil_date:
            return term
    return None
