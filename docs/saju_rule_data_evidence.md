# Saju rule-data evidence ledger

This ledger records source checks completed for bundled Saju data. It is not a
promotion approval and must be read together with
`saju_rule_data_verification.md`.

## Evidence recorded

| Scope | Source | Result | Promotion effect |
| --- | --- | --- | --- |
| 2026 Korea Standard Time solar-term instants | [Korea Astronomy and Space Science Institute, Monthly Almanac](https://astro.kasi.re.kr/life/post/calendardata) | The published 2026 sequence and minute-level times match the bundled `solar_term_instants_v1` values. | Supports the already production-verified, explicitly bounded 2026 table only. |
| Heavenly-stem and earthly-branch ordering | [Encyclopedia of Korean Culture, *Iljin*](https://encykorea.aks.ac.kr/Article/E0047325) | Records the standard `gap…gye` and `ja…hae` sequences and their 60-cycle pairing. | Supports vocabulary order; does not independently verify every core-table field. |
| Hour-branch windows and hour-stem progression | [Encyclopedia of Korean Culture, *Saju*](https://encykorea.aks.ac.kr/Article/E0025957) | Describes the 12 hour branches from Ja through Hae and gives a Ja-hour-to-Myo-hour stem progression example. | Supports the hour-boundary model; does not independently verify all hour-stem groups. |

## Evidence still missing

- A second independent source or reviewer for each core-table mapping.
- Source decisions for hidden-stem main/middle/residual roles.
- Complete independent checks of month-stem and hour-stem grouping rules.
- Complete independent check of ten-god relation and polarity mappings.

Accordingly, `core_tables_v1`, `hidden_stems_v1`, `month_stem_rules_v1`,
`hour_stem_rules_v1`, and `ten_gods_v1` remain `pending_verification`.
