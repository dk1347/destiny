# Solar-Term Source Acquisition Ledger

> Status: research record only. This document does not approve any additional
> birth-year coverage or change production data.

## Objective

Extend `solar_term_instants_v1` only in small, auditable year batches. Every
added year must pass the release gate in
`docs/16_SOLAR_TERM_DATA_RELEASE_GATE.md` and the implementation rules in
`docs/39_SOLAR_TERM_COVERAGE_EXPANSION_SPEC.md`.

## Confirmed official-source starting point

| Source | What it establishes | Usable scope | Role |
| --- | --- | --- | --- |
| [KASI Calendar Data](https://astro.kasi.re.kr/kor/life/post/calendarData) | KASI publishes calendar data from 2021 onward and directs earlier lookups to its almanac material. | 2021 onward | Primary source when the annual table is available. |
| [KASI Monthly Almanac](https://astro.kasi.re.kr/life/post/almanac) | KASI provides officially announced monthly almanac material from 2004 onward, including 24-term dates and times. | 2004 onward | Primary source for historical annual collection. |
| [NAOJ Calendar and Ephemeris Computation](https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_sy_en.cgi) | Can produce a separately checked 24-term sequence with UTC+9 selected. | Per-year comparison | Independent comparison only. |

The KASI pages establish a practical official-source route for 2004 onward.
They do **not** establish a production source for 1963. A 1963 record stays
unavailable until a separately captured primary source and an independent
comparison are reviewed.

## Per-year evidence record

Create one completed row for each candidate year before editing the dataset.

| Year | KASI publication/reference | Retrieved (KST) | 24 entries captured | KST minute precision | NAOJ comparison | Differences investigated | Licence/reuse reviewed | Reviewer | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026 | Calendar Data; existing audit `docs/20_SOLAR_TERM_2026_VERIFICATION_AUDIT.md` | 2026-09-16 | Yes | Yes | Exact 24/24 | N/A | Existing review | Recorded | Approved, already bundled |
| 2004–2025 | Not yet captured | — | No | — | No | — | No | — | Not approved |
| 2027 onward | Not yet captured | — | No | — | No | — | No | — | Not approved |
| Before 2004, including 1963 | Primary source not yet selected | — | No | — | No | — | No | — | Not approved |

## Safe import sequence

1. Select one contiguous pilot year from the available KASI range; do not
   infer values from a neighbouring year.
2. Save the primary-source reference and capture all 24 term IDs, KST
   timestamps, and published precision.
3. Independently compare all 24 entries with NAOJ configured to UTC+9. Record
   even a one-minute mismatch rather than rounding it away.
4. Add the year as its own explicit coverage range with provenance in the
   dataset, then run the boundary and gap tests specified in `docs/39`.
5. Obtain review, run the complete test/build checks, and only then widen the
   supported-year message or public documentation.

## Non-negotiable guardrails

- Never use a web lookup during a user calculation.
- Never generate missing historical term instants from an LLM or an
  undocumented library and label them verified.
- Preserve the current fail-closed response for every year not in an approved
  range.
- Do not touch the legacy RAG database as part of this work.
