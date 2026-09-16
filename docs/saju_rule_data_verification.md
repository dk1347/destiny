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

| Dataset | Evidence still required before promotion |
| --- | --- |
| `core_tables_v1` | Independent confirmation of vocabulary order, five-element generation/control cycles, polarity, time windows, and major-term month mapping. |
| `hidden_stems_v1` | Source decision for each branch's main/middle/residual stems and display ordering. |
| `month_stem_rules_v1` | Independent confirmation of each year-stem group, In-month start stem, and full canonical branch cycle. |
| `hour_stem_rules_v1` | Independent confirmation of each day-stem group, Ja-hour start stem, and full canonical branch cycle. |
| `ten_gods_v1` | Independent confirmation of the relation-to-ten-god mapping and same/different-polarity rule. |

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
