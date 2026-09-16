# Destiny — Korea MVP Demand Claim Audit

> Research date: 2026-09-16  
> Input: *2026 Korea Saju, Fortune, Tarot Demand TOP 10 Research Report*
> Status: claim audit; this document does not assert a market ranking.

## 1. Purpose and decision rule

The earlier exploratory report is useful for generating MVP hypotheses, but
its numeric statements are not accepted as product facts until their source,
scope, and comparison method are independently inspectable.

In particular, Naver DataLab values are relative indices. A value normalised
against an anchor keyword in one comparison group cannot be safely compared
with a value produced from another group unless the exact groups, dates,
filters, and normalisation procedure are retained. An apparent multiplier is
therefore not a market-size or conversion claim.

The only current decision use is to choose experiments from a small list of
plausible entry points. No audited claim below authorises marketing language,
revenue forecasts, or a permanent MVP funnel choice.

## 2. Claim register

| ID | Earlier-report claim | Audited status | Safe interpretation | Evidence still needed |
| --- | --- | --- | --- | --- |
| MKT-01 | Daily fortune is the largest search topic, reported as `379.3x` the compatibility anchor. | **Unverified** | Daily fortune is a reasonable entry-point hypothesis only. | Saved DataLab comparison URL/export for every keyword group; date range, device/sex/age filters, keyword membership, and anchor normalisation calculation. |
| MKT-02 | Compatibility, romance, reunion, comprehensive Saju, and wealth form a numeric TOP 10 demand ranking. | **Unverified** | These are candidate content families, not a ranked demand list. | Same DataLab materials as MKT-01, plus a documented rule for combining/splitting overlapping keywords. |
| MKT-03 | Relationship/reunion content has very large cumulative view counts and stronger purchase potential than comprehensive Saju. | **Unverified** | Relationship follow-up is worth an experiment; no conversion advantage is established. | Dated source snapshots or export for the cited store metrics, whether views are free or paid, unique-user definition, tag-deduplication rule, and category-level purchase data. |
| MKT-04 | The free-to-relationship-to-paid-comprehensive funnel is the best product sequence. | **Needs experiment** | It is the current working funnel in `09_KOREA_MVP_DEMAND_HYPOTHESES.md`, not a conclusion from external data. | A controlled Destiny experiment with pre-defined acquisition, completion, voluntary return, purchase, and contact/refund metrics. |
| MKT-05 | A stated percentage of consumers is interested in wealth/financial fortune content. | **Partially corroborated** | Wealth is a candidate topic to test. This is stated interest, not purchase intent or a financial-product signal. | Retain the original survey wording and any weighting details; do not infer payment behavior. |
| MKT-06 | The Korean fortune-app market has the reported MAU, sales, paid-consultation, and demographic values. | **Partially corroborated / not accepted numerically** | A large, content-led fortune service demonstrably exists; the report's precise figures need source-specific verification. | A primary company statement or a directly inspectable report for each figure, including collection date and metric definition. |

## 3. What is independently corroborated

The report embeds its original source links, which makes a focused audit
possible. One of those sources is a 2025 ZDNet Korea interview with
Forceteller's founders. It supports the following narrow observations:

- The service offers themed readings including daily fortune, romance, career,
  health, and relationship-oriented content.
- The publisher describes broad content expansion and paid fortune sales.
- In that interview, the publisher says solo romance is its average popular
  theme and reunion is more used at year end and New Year.

These are publisher/interview statements, not independently measured topic
shares. The interview must not be transformed into a claim that romance or
reunion is the universally highest-demand category. See the
[ZDNet Korea interview](https://zdnet.co.kr/view/?no=20250203104315),
published 2025-02-06.

The app-store and service-page observations listed in
`09_KOREA_MVP_DEMAND_HYPOTHESES.md` remain valid only as evidence that the
categories are commercially offered. They do not corroborate the report's
search ranking, content-view totals, or conversion claims.

## 4. Evidence-quality findings

1. **Relative search data:** the report states a common compatibility anchor,
   but a numerical comparison across separate DataLab groups is not
   reproducible from the PDF alone. The original DataLab URLs are retained in
   the PDF and must be opened/exported with their group definitions before use.
2. **Platform content views:** a content-view count does not identify a unique
   user, purchase, retention, or causal demand. The report itself notes free
   versus paid visibility and multiple-tag duplication limits. Those limits
   are disqualifying for a conversion conclusion.
3. **Company and media figures:** app installs, sign-ups, revenue, MAU, and
   audience composition have different definitions and dates. Each must retain
   its exact primary or named secondary source; they cannot be summed or used
   as a single market-size figure.
4. **Survey percentages:** the PDF links to surveys, but a percentage is not
   reusable without the original question and respondent base. Survey attitude
   is also not equivalent to willingness to pay.

## 5. MVP consequence

Continue with two equally visible free entry candidates—daily reading and
compatibility/relationship reading—and evaluate them with Destiny's own
instrumentation. A relationship-oriented follow-up and a paid comprehensive
result remain test variants, not assumptions.

No claim from the earlier report may be used to say that a category is
“number one,” that it has a specific market size, or that it has a superior
payment conversion rate.

## 6. Independent cross-check outcome

A second researcher was asked to validate only MKT-01, MKT-03, and MKT-05
without producing a new ranking. Its outcome is consistent with this audit:

| Claim | Outcome | Audit consequence |
| --- | --- | --- |
| MKT-01: daily fortune has decisively greater search demand than compatibility | **Not found** | Retain as an entry-point experiment, not a demand conclusion. |
| MKT-03: relationship/reunion converts better than comprehensive Saju | **Not found** | Retain as a follow-up experiment, not a conversion conclusion. |
| MKT-05: wealth-related fortune interest has a measurable survey percentage | **Partially corroborated** | A current, inspectable source reports wealth fortune as an interest topic, but it is not payment behavior. |

The directly inspected source for MKT-05 is TrendMonitor's *2026 New Year
Plan and Fortune Service Usage Survey*. It reports that 58.7% of respondents
selected wealth fortune as a topic of interest when using fortune services
(multiple response). The page identifies a national sample of 1,000 adults
aged 19–59 and a field period of 2026-01-05 through 2026-01-07. The result
must always retain its survey-attitude and multiple-response qualifications.
See [TrendMonitor's survey page](https://www.trendmonitor.co.kr/tmweb/trend/allTrend/detail.do?bIdx=3318&code=0401&trendType=CKOREA).

## 7. Next independent cross-check

Ask a second researcher to verify only MKT-01, MKT-03, and MKT-05. It must:

1. Return a direct source URL for each accepted fact, its publication or
   collection date, and the metric definition.
2. Mark a claim **not found** when no direct source is available; it must not
   fill gaps with an estimate.
3. Preserve the distinction between provider statements, app-store offerings,
   search indices, survey attitudes, and observed purchase behavior.
4. Produce no TOP 10 ranking or product recommendation.

This narrow task will either corroborate a decision-relevant input or keep it
as an experiment hypothesis, which is a useful result in both cases.
