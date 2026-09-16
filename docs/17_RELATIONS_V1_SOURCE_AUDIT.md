# Destiny — Relations V1 Source Audit

> Status: source-audit and staged-scope decision. This document does not
> approve a `production_verified` relations dataset.

## 1. Decision

`relations_v1` must report only **observed structural relationships** between
the stems and branches present in a result. It must never turn a relationship
into a lucky/unlucky outcome, health, legal, financial, or relationship claim.

The engine will not implement a rule merely because it is common in online
fortune content. Every production row needs two independently reviewable
sources and a preserved source reference.

## 2. What the current evidence supports

The academic paper below explicitly states the six branch clashes as
`ja-o`, `chuk-mi`, `in-sin`, `myo-yu`, `jin-sul`, and `sa-hae`. It also makes
an important product point: the outcome of a clash or punishment depends on
the whole configuration, and historical sources disagree on some downstream
interpretations. That supports detecting a relation as a fact but not making
a deterministic interpretation from it.

The existing versioned-data specification already defines the schema and
completeness conditions for:

- five stem combinations;
- six branch combinations;
- four complete three-harmony groups and their two-branch candidates; and
- six branch clashes.

Those four categories are the first candidate implementation batch, but they
remain `pending_verification` until every row has two reviewed sources.

## 3. Explicitly deferred relation types

`branch_punishment`, `branch_self_punishment`, `branch_break`, and
`branch_harm` remain out of the first data batch. Their membership, grouping,
and downstream meaning are more likely to differ by source or school.

Do not hide those omissions: a result must either omit unsupported types or
show a structured availability warning. It must not silently label a partial
relation set as “complete 합충형파해 analysis.”

## 4. Data and test gate

Before a first `relations_v1` dataset is enabled for production:

1. Record source identifiers, editions/pages or stable URLs, access dates, and
   licensing/reuse assessment for every row.
2. Independently verify all batch-one rows; resolve any mismatch before
   setting `production_verified`.
3. Add schema tests for unique IDs, canonical stem/branch references,
   participant cardinality, unordered-pair canonicalization, and correct
   resulting-element presence.
4. Add synthetic four-pillar fixtures for: a single pair, overlapping
   relations, a complete three-harmony, a two-member candidate, repeated
   branches for any future self-punishment rule, and no relationship.
5. Verify that calculation output remains the same regardless of input pillar
   enumeration order, while each returned finding retains its actual pillar
   locations.
6. Keep all interpretation and priority policy outside this dataset and
   outside the deterministic calculator.

## 5. Sources reviewed

- Kim Man-tae, “A Study on the Origin of Clash and Punishment as Interaction
  Relationships of the Twelve Earthly Branches,” *Journal of Koreanology*
  36(3), 2013. The paper lists the six clashes and discusses disagreement about
  downstream readings:
  https://www.accesson.kr/ksq/assets/pdf/40880/journal-36-3-134.pdf
- Existing Destiny schema and completeness requirements:
  `docs/07_VERSIONED_RULE_DATA_SPEC.md` §5.5.
- Existing engine boundary between relation detection and interpretation:
  `docs/06_ENGINE_CONTRACTS_AND_CORE_RULES.md` §5.4.

## 6. Non-decision

This audit does not choose a commercial Manse Ryeok site, a blog, an LLM, or
a single modern textbook as the production authority. It also does not add
celebrity charts or personally identifying birth data as fixtures.
