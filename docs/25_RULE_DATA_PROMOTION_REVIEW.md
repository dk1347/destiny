# Destiny — Rule-data Promotion Review Pack

> Status: prepared for human review on 2026-09-16. This is evidence assembly,
> not approval. No dataset status changes through this document.

Use this pack with `docs/saju_rule_data_verification.md` before any
`pending_verification` dataset becomes `production_verified`.

## Review records

| Dataset | Version | Evidence and scope | Regression coverage | Decision |
| --- | --- | --- | --- | --- |
| `core_tables_v1` | `1.0.0` | `docs/24_CORE_TABLES_SOURCE_AUDIT.md`: canonical orders, calculation element/polarity, five-element cycles, hour windows, and major-term/month mapping. | `tests/test_data_and_hidden_stems.py` locks cycles, 12 windows, 12 major-term mappings, and 22 calculation attributes. | **Approved 2026-09-16** for calculation scope; display-only animal labels excluded. |
| `hidden_stems_v1` | `1.0.0` | `docs/22_HIDDEN_STEMS_SCOPE_AUDIT.md`: selected compact-only convention and two complete-table comparisons. | `tests/test_data_and_hidden_stems.py` locks every compact row and role order. | **Pending** — compact convention/reuse approval; seasonal model remains separate. |
| `month_stem_rules_v1` | `1.0.0` | `docs/21_MONTH_AND_HOUR_STEM_SOURCE_AUDIT.md`: Five Tigers start groups and canonical In-origin cycle. | `tests/test_month_stem.py` plus data-registry canonical-cycle checks. | **Pending** — retrieval detail, row review, and release decision. |
| `hour_stem_rules_v1` | `1.0.0` | `docs/21_MONTH_AND_HOUR_STEM_SOURCE_AUDIT.md`: two direct five-group Rat-hour tables and Korean sequence support. | `tests/test_hour_stem.py` plus data-registry canonical-cycle checks. | **Pending** — retrieval detail, row review, and release decision. |
| `ten_gods_v1` | `1.0.0` | `docs/23_TEN_GODS_SOURCE_AUDIT.md`: five-relationship model and full 乙 day-master row. | `tests/test_ten_gods.py` locks the 乙 row and all 100 combinations. | **Pending** — reviewer approval after dependent core-table decision. |
| `relations_v1` | `1.0.0` | `docs/17_RELATIONS_V1_SOURCE_AUDIT.md`: stem combinations, branch combinations, three-harmony groups/candidates, and clashes. | `tests/test_relations.py` locks every candidate row and detection boundary. | **Pending** — edition/page and reuse record; no interpretation policy here. |

## Approval checklist

For each row, a reviewer must explicitly confirm all of the following before
changing JSON metadata:

1. Source edition or stable source location, access date, and reuse assessment
   are preserved.
2. The listed regression tests passed against the reviewed row values.
3. The dataset's scope is understood, including exclusions and dependencies.
4. The release decision, reviewer, and date are written into the dataset
   source metadata or a linked immutable review record.
5. The production API and library tests still reject every dataset that has
   not received this explicit approval.

## Deliberate non-decisions

- This pack does not approve a status change or alter a dataset version.
- It does not create a universal interpretation of relations or hidden stems.
- It does not extend the 2026 KST solar-term coverage. That dataset has its
  own bounded production approval in `docs/20_SOLAR_TERM_2026_VERIFICATION_AUDIT.md`.
