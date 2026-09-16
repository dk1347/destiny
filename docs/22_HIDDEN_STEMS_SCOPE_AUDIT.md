# Destiny — Hidden-stems Scope Audit

> Product decision (2026-09-16): use the compact hidden-stem convention for
> the MVP. Keep `hidden_stems_v1` as `pending_verification`; do not promote or
> silently replace rows until its compact row set has dedicated source review.

## What the current dataset means

`hidden_stems_v1` records a compact role list in this order:

1. `main` (정기 / 본기)
2. `middle` (중기), when adopted
3. `residual` (여기), when adopted

For example, the current `branch:in` row is `甲(main), 丙(middle), 戊(residual)`.
It intentionally stores only `癸` for 子, only `乙` for 卯, only `辛` for 酉,
and `壬(main), 甲(middle)` for 亥.

## External comparison and material divergence

The [Learning Institute course material](https://www.lei.or.kr/upfiledata/board/%EB%AA%85%EB%A6%AC%EC%8B%AC%EB%A6%AC%EC%83%81%EB%8B%B4%EC%82%AC_%EC%A0%84%EC%A0%95%ED%9B%88_%EA%B5%90%EC%95%88%EB%AA%A8%EC%9D%8C.pdf)
describes a seasonal/`사령` table in `여기 → 중기 → 정기` order. It explicitly
lists, for example, 子 as 壬/癸, 卯 as 甲/乙, 酉 as 庚/辛, and 亥 as 戊/甲/壬.
Its ordering is the reverse of Destiny's role order, but after reversal it
also retains more stems than the current compact rows.

This is not a formatting issue. It reflects two possible dataset scopes:

| Candidate convention | Use | Consequence |
| --- | --- | --- |
| Compact branch hidden-stem list | General structural display or a rule set that uses only adopted hidden components | Matches the present JSON shape, but needs a source defining exactly which components are omitted. |
| Seasonal `여기/중기/정기` table with `사령` durations | Month-branch timing and interpretation tied to days since a solar term | Requires every branch's full ordered set and duration model; it cannot be represented faithfully by the present JSON alone. |

## Release decision

The calculator must not claim that the compact list implements the seasonal
`사령` model. The two models should be separate versioned datasets if both are
needed. Until product chooses the supported semantics and a source supports
every row under that semantics, production loading remains blocked.

## Required next decision

The MVP selection is option 1 below. The other options remain future design
paths, not current implementation work.

1. **Compact-only MVP (selected):** name the chosen convention and obtain a full
   row-by-row source for its omissions.
2. **Seasonal model:** add a new dataset containing `residual/middle/main`
   roles plus each interval or duration, with its solar-term linkage.
3. **Both:** retain the compact dataset for structural output and introduce a
   separately named seasonal dataset; never overload one API field to mean
   both.
