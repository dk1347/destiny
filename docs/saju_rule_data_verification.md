# Saju rule-data verification checklist

This checklist governs promotion of a bundled Saju rule dataset from
`pending_verification` to `production_verified`. Completing a checklist does
not itself approve a promotion; it records the evidence needed for a
reproducible approval.

## Required for every dataset

- [ ] Keep the current `dataset_id`; publish a new `dataset_version` for a
  corrected value rather than rewriting a verified version.
- [ ] Record a primary source, its edition or publication date, and the exact
  rule scope that it supports.
- [ ] Record an independent second source or a documented independent review.
- [ ] Verify the JSON schema, vocabulary, ordering, and all semantic
  invariants through `RuleRegistry` tests.
- [ ] Add a regression case that would fail if each corrected or newly
  verified rule were changed.
- [ ] Record reviewer, review date, and decision in the dataset's source
  metadata or a linked review record.
- [ ] Confirm the production path rejects the dataset until its status is
  explicitly promoted.

## Current pending datasets

The listed audit documents and regression tests record evidence progress; they
are not promotion approvals. Every row below remains unavailable to production
until the common checklist and the explicit promotion record are complete.

| Dataset | Evidence already recorded | Remaining release condition |
| --- | --- | --- |
| `core_tables_v1` | Order, calculation element/polarity attributes, element cycles, hour windows, and major-term mapping are recorded in `docs/24_CORE_TABLES_SOURCE_AUDIT.md` and regression tests. | Preserve an approved field-level source/reuse record, resolve the display-label scope, and record reviewer decision. |
| `hidden_stems_v1` | Compact-only MVP scope, two compact-table comparisons, role/order mapping, and 12-row regression table are recorded in `docs/22_HIDDEN_STEMS_SCOPE_AUDIT.md`. | Preserve the compact-convention source and reuse decision in the promotion record; do not mix it with the separate seasonal model. |
| `month_stem_rules_v1` | Two source families and all five Tiger-start groups are recorded in `docs/21_MONTH_AND_HOUR_STEM_SOURCE_AUDIT.md`; canonical ordering is schema-tested. | Record retrieval details, row-by-row reviewer sign-off, and release decision. |
| `hour_stem_rules_v1` | Two direct historical tables cover all five Rat-hour start groups; canonical ordering is schema-tested. See `docs/21_MONTH_AND_HOUR_STEM_SOURCE_AUDIT.md`. | Record retrieval details, row-by-row reviewer sign-off, and release decision. |
| `ten_gods_v1` | The five-relationship model and a full 乙 day-master reference row are recorded in `docs/23_TEN_GODS_SOURCE_AUDIT.md` and regression tests. | Complete an approved promotion record after the dependent core-table release decision. |
| `relations_v1` | Candidate participant sets/elements are cross-checked and locked in `docs/17_RELATIONS_V1_SOURCE_AUDIT.md` and relation tests. | Preserve edition/page-level and reuse evidence; keep interpretation policy out of this dataset; record reviewer decision. |

## Promotion record template

For each promotion, add a record with this information before changing
`status`:

```text
dataset_id:
dataset_version:
primary source:
independent source or reviewer:
verified scope:
regression tests:
review date:
review decision:
```

If any item is absent, retain `pending_verification`. Do not use
`allow_unverified=True` as a production substitute.
