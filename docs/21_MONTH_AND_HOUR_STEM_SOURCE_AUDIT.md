# Destiny — Month/Hour Stem Rule Source Audit

> Decision: record the currently available source evidence; retain both
> `month_stem_rules_v1` and `hour_stem_rules_v1` as `pending_verification`.

## Scope

This audit covers only the five start-stem groups and the canonical branch
progression used by the month-stem and hour-stem datasets. It does not approve
solar-term boundaries, day-boundary policy, hidden stems, or Ten Gods.

## Evidence found on 2026-09-16

| Dataset | Source | What it directly supports | Result |
| --- | --- | --- | --- |
| `month_stem_rules_v1` | Cheng Pei and Hu Sumin, [*Origin and Interpretation of the Ten Stems to Mark the Five Motions in Traditional Chinese Medicine*](https://yizhe.dmu.edu.cn/data/article/yxyzx/preview/pdf/2018-2A-22.pdf), *Medicine and Philosophy*, 2018 | It reproduces the five-group `Five Tigers` month-start formula, explains that it selects the In-month stem from the year stem, and describes continuing the stems through the following months. | Matches all five `tiger_start_by_year_stem_group` rows and the In-origin month cycle. |
| `month_stem_rules_v1` | Ming source, [*Newly Published Geographic Outline…*](https://www.shidianguji.com/zh/mid-page/7556734501952077834) | Its `起月訣` gives the same five start groups: 甲己→丙, 乙庚→戊, 丙辛→庚, 丁壬→壬, 戊癸→甲. | Independent textual agreement with the dataset's five start stems. |
| `hour_stem_rules_v1` | Ming source, [*Newly Published Geographic Outline…*](https://www.shidianguji.com/zh/mid-page/7556734501952077834) | Its `起時訣` gives the five Rat-hour start groups: 甲己→甲, 乙庚→丙, 丙辛→戊, 丁壬→庚, 戊癸→壬. | Matches all five `rat_start_by_day_stem_group` rows. |
| `hour_stem_rules_v1` | Ming source, [*Leijing* (十干起子歌)](https://www.shidianguji.com/zh/mid-page/7504041099071242267) | It independently prints the same five Rat-hour start groups and explains advancing two positions from Zi to derive the In-month stem. | Independent textual agreement with all five hour-start rows. |
| `hour_stem_rules_v1` | [Encyclopedia of Korean Culture, *Saju*](https://encykorea.aks.ac.kr/Article/E0025957) | Confirms the canonical 10-stem and 12-branch orders, the Ja-through-Hae time sequence, and demonstrates the 乙/庚 day-stem path from 丙子 through 己卯. | Supports one concrete group and the sequential progression; it is not a full independent five-group table. |

## Why the status does not change yet

- For month stems, the evidence is strong enough to justify a separate human
  approval review, but no promotion record has been approved and no dataset
  version change is made here.
- For hour stems, two independent historical-text sources now print every
  group directly; the Korean reference adds a modern Korean explanation of
  one concrete progression. This is sufficient to prepare a human promotion
  review, but it is not itself an approval.
- A source record is not a substitute for a controlled release decision.
  Production code continues to reject these pending datasets.

## Next verification action

Prepare the promotion record required by `docs/saju_rule_data_verification.md`
for both datasets. It must explicitly list the source retrieval dates,
row-by-row comparison, reviewer, and release decision before any status field
can be changed.
