# Solar-Term Coverage Expansion — Implementation Specification

## Purpose

The current calculator deliberately fails closed outside the verified 2026 KST
solar-term coverage.  This work makes verified annual coverage extensible
without weakening that safety rule.

This specification does **not** authorize guessed, calculated, scraped without
provenance, or unreviewed solar-term instants in production data.

## First implementation unit

Build the data contract and validation required to add one or more separately
audited years.  Do not add a large historical range until every proposed year
has a reviewable official source record.

### Required behaviour

1. The dataset must declare verified coverage as one or more explicit KST date
   ranges, not merely a broad label or an inferred first/last timestamp.
2. Every coverage range must be continuous, chronological, and backed by an
   auditable source record that identifies the year, publisher, source URL or
   publication reference, access date, and precision.
3. Each term instant must be timezone-aware KST (`+09:00`), strictly ordered,
   and belong to an explicit verified coverage range.
4. Lookup must continue to raise `SOLAR_TERM_DATA_UNAVAILABLE` for every
   instant outside verified coverage, including gaps between ranges.
5. Existing 2026 lookup behaviour and its published boundary instants must not
   change.
6. The public API must expose no claim that an unavailable historical date was
   calculated successfully.

## Data migration and compatibility

- Preserve the dataset id `solar_term_instants_v1` unless a compatibility
  review demonstrates a new id is necessary.
- Bump the dataset version and update its `scope`, provenance, and generation
  notes whenever production coverage changes.
- Keep the current 2026 official-almanac attribution intact.
- Do not relax `RuleRegistry` integrity validation to accept malformed legacy
  data.

## Required regression tests

1. The existing 2026 boundary audit remains exact.
2. A valid additional audited range can be looked up at its first instant,
   final instant, and a major-term boundary.
3. An instant before/after coverage and inside a deliberately introduced gap is
   rejected with `SOLAR_TERM_DATA_UNAVAILABLE`.
4. Dataset loading rejects: overlapping ranges, ranges out of order, a term
   outside its declared range, missing provenance fields, a non-KST instant,
   and terms that are not strictly ordered.  These failures use
   `DATASET_SCHEMA_INVALID`.
5. Month-pillar behaviour crosses the additional range's `ipchun` boundary
   correctly.

## Source and review gate

Before adding a new year, provide a source table with: year, official
publisher, stable reference/URL, retrieval date, listed KST instant precision,
and a second independent cross-check where available.  Separate direct facts
from assumptions.  If a year cannot pass this gate, leave it unavailable.

## Completion criteria

- The implementation meets every required behaviour and regression case.
- `pytest` and `python -m build` pass locally.
- The change is independently reviewed for fail-closed behaviour.
- A final report lists exact added years, sources, tests run, build result, and
  remaining unavailable years.

## Explicit non-goals

- Do not implement Daewoon, AI interpretation, true-solar-time conversion, or
  an unverified all-years ephemeris in this unit.
- Do not alter `main`; work remains on `fix/v3-data-integrity`.
