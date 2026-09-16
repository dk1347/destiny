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
| `hidden_stems_v1` | Compact-only MVP scope, two compact-table comparisons, role/order mapping, and 12-row regression table are recorded in `docs/22_HIDDEN_STEMS_SCOPE_AUDIT.md`. | Preserve the compact-convention source and reuse decision in the promotion record; do not mix it with the separate seasonal model. |
| `ten_gods_v1` | The five-relationship model and a full 乙 day-master reference row are recorded in `docs/23_TEN_GODS_SOURCE_AUDIT.md` and regression tests. | Complete an approved promotion record after the dependent core-table release decision. |
| `relations_v1` | Candidate participant sets/elements are cross-checked and locked in `docs/17_RELATIONS_V1_SOURCE_AUDIT.md` and relation tests. | Preserve edition/page-level and reuse evidence; keep interpretation policy out of this dataset; record reviewer decision. |

`core_tables_v1` was promoted to `production_verified` on 2026-09-16 for its
calculation scope. Its status history and source links are recorded in the
dataset metadata; display-only animal labels remain outside the approval.

`month_stem_rules_v1` and `hour_stem_rules_v1` were promoted to
`production_verified` on 2026-09-16. Their source links and status histories
are recorded in their respective dataset metadata.

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
