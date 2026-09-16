# Destiny — 2026 Solar-term Verification Audit

> Decision: retain `solar_term_instants_v1` version `1.0.0` as
> `production_verified` for its explicitly bounded 2026 KST coverage only.

## Scope and result

On 2026-09-16, all 24 2026 solar-term IDs and KST minute-level instants in
`solar_term_instants_v1` were compared with the Korea Astronomy and Space
Science Institute (KASI) calendar-data table. Every entry matched exactly.

An independent comparison was also made against the National Astronomical
Observatory of Japan (NAOJ) Calendar and Ephemeris Computation output with
its local standard time set to UTC+9. Its 2026 sequence also matched all 24
IDs and minute-level instants.

## Sources

| Role | Source | Time basis | Result |
| --- | --- | --- | --- |
| Primary | KASI, [Calendar Data (Monthly Almanac)](https://astro.kasi.re.kr/kor/life/post/calendarData) | KST | Exact 24/24 match. The site identifies this material as the basis for calendar production; the 2026 values are published as official calendar data. |
| Independent comparison | NAOJ, [Calendar and Ephemeris Computation: 24 solar terms](https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_sy_en.cgi) | UTC+9 | Exact 24/24 match. This is a comparison source, not a replacement for KASI. |

## Reproducibility and limits

- `tests/test_solar_terms.py` fixes the 24 published 2026 ID/timestamp pairs
  in a regression test, so an accidental data edit is visible in local CI.
- This decision does **not** expand the supported birth-year range. Lookups
  before 2026-01-01 or after 2026-12-31 KST continue to fail closed.
- KASI and NAOJ may revise future material or calculation parameters. A new
  annual table must receive a new dataset version, a fresh source capture,
  an independent comparison, and its own audit before promotion.
- The exact prior-boundary records in the file are required only to identify
  the active term at the beginning of the 2026 coverage; they are not a claim
  of supported 2025 birth-date coverage.
