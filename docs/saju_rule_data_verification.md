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

`core_tables_v1` was promoted to `production_verified` on 2026-09-16 for its
calculation scope. Its status history and source links are recorded in the
dataset metadata; display-only animal labels remain outside the approval.

`month_stem_rules_v1` and `hour_stem_rules_v1` were promoted to
`production_verified` on 2026-09-16. Their source links and status histories
are recorded in their respective dataset metadata.

`hidden_stems_v1` was promoted to `production_verified` on 2026-09-16 for
the compact hidden-stem convention only; the seasonal model remains separate.

`ten_gods_v1` was promoted to `production_verified` on 2026-09-16 for
structural day-master-to-target mapping only; interpretation remains outside
the dataset.

`relations_v1` was promoted to `production_verified` on 2026-09-16 for
observed structural relations only; priority, interpretation, and fortune
claims remain outside the dataset.

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
