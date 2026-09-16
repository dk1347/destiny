# Destiny — Ten Gods Source Audit

> Decision (2026-09-16): approve `ten_gods_v1` as `production_verified` for
> structural ten-god mapping only. Interpretation and fortune claims remain
> outside this dataset.

## What is verified

The relation table encodes five relationships to the day master: same element,
day master generates target, day master controls target, target controls day
master, and target generates day master. Each splits into the same- and
different-polarity cases.

| Source | Direct support | Comparison result |
| --- | --- | --- |
| [Hakka Affairs Council research material](https://sign.hakka.gov.tw/File/Get?filename=%5CAttach%5C1990%5C1%5C322010382571.pdf) | Explains the five day-master relationships and that adding yin/yang creates the ten categories. It names the five paired groups: 印, 食傷, 官殺, 財, and 比劫. | Supports the model underlying every `relation_table` row. |
| [*Exploration of Fate Theory*, volume 3](https://libokang.com/zh-hant/guji/bazi/%E5%91%BD%E7%90%86%E6%8E%A2%E6%BA%90/3/) | Its explicit 乙-day-master example gives all ten target-stem outcomes: 乙=比肩, 甲=劫財, 丁=食神, 丙=傷官, 己=偏財, 戊=正財, 辛=偏官, 庚=正官, 癸=偏印, 壬=正印. | Exact match for an opposite-polarity day-master row, including every same/different polarity selection. |

`tests/test_ten_gods.py` now fixes that complete 乙 reference row in addition
to the existing 100-pair totality test and 甲 golden cases.

## Limits

- The evidence validates the ten-god naming/mapping rule, not any
  interpretation or fortune claim.
- The computation relies on `core_tables_v1` five-element cycles and stem
  polarity. That calculation scope was independently promoted on 2026-09-16.
- The linked dataset metadata records the source locations, approved scope,
  status history, review date, and promotion decision.
