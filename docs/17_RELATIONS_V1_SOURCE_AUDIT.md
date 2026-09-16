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

Those four categories are the first candidate implementation batch. A
2026-09-16 row-level cross-check found that the bundled participant sets and
resulting elements agree with the independently presented table in *Mingli
Tanyuan* (which itself identifies its historical attributions):

- five stem combinations and their elements;
- six branch combinations and their elements (with `o`/`mi` retained as the
  traditional sun/moon pairing and represented in this dataset as earth);
- the four three-harmony groups and their elements; and
- the six branch clashes.

The bundled two-member three-harmony candidates are a mechanical subset of
those four reviewed complete groups. This establishes a useful regression
baseline, but the dataset remains `pending_verification`: the review record
must still preserve edition/page-level evidence and complete reuse assessment
before it may become `production_verified`.

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
- Kim Man-tae, “A Study on Clues for the Combination of the Ten Celestial
  Stems in Their Relations of Mutual Changes and Actions,” *Sogang Journal of
  Philosophy* 30 (2012), 97–128, DOI: 10.17325/sgjp.2012.30..97:
  https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001690465
- Kim Man-tae, “A Study on Clues for Jiji Combinations as Relations of Mutual
  Changing Actions among Jijis,” *Sogang Journal of Philosophy* 31 (2012),
  205–241, DOI: 10.17325/sgjp.2012.31..205:
  https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART001716658
- *Mingli Tanyuan*, vol. 1, sections “Five-combination five elements”,
  “Six-combination five elements”, “Three-harmony five elements”, and “Six
  clashes”. It gives all four candidate categories row by row and attributes
  the traditional material it quotes:
  https://libokang.com/zh-hant/guji/bazi/%E5%91%BD%E7%90%86%E6%8E%A2%E6%BA%90/
- *Sanming Tonghui*, vol. 2, preserved primary-text reference for the existing
  data source:
  https://zh.wikisource.org/zh-hant/%E4%B8%89%E5%91%BD%E9%80%9A%E6%9C%83/%E5%8D%B7%E4%BA%8C
- Existing Destiny schema and completeness requirements:
  `docs/07_VERSIONED_RULE_DATA_SPEC.md` §5.5.
- Existing engine boundary between relation detection and interpretation:
  `docs/06_ENGINE_CONTRACTS_AND_CORE_RULES.md` §5.4.

## 6. Non-decision

This audit does not choose a commercial Manse Ryeok site, a blog, an LLM, or
a single modern textbook as the production authority. It also does not add
celebrity charts or personally identifying birth data as fixtures.

The two KCI records establish useful independent academic provenance for the
existence and historical discussion of stem and branch combinations. The
row-level cross-check above is deliberately narrower than a release approval:
it does not resolve source-edition, licensing, or all-school-variation review.
Do not enable a production dataset until those release records are complete.
