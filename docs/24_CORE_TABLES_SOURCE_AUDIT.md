# Destiny — Core Tables Source Audit

> Decision: lock the reviewed lookup values in regression tests, while keeping
> `core_tables_v1` as `pending_verification` until every field has an approved
> source record.

## Reviewed slices

| Slice | Evidence | Result |
| --- | --- | --- |
| Stem and branch order | [Encyclopedia of Korean Culture, *Iljin*](https://encykorea.aks.ac.kr/Article/E0047325) | Supports the stored standard `gap…gye` and `ja…hae` order. |
| Five-element generation/control cycles | [Korea District Heating Corporation magazine reference](https://www.kdnavien.co.kr/upload/pr/magazine/20201013064145839.pdf) depicts the wood→fire→earth→metal→water generation cycle and its control cycle. | Matches both five-entry maps in `element_relations`. |
| Legal-local hour branches | [Encyclopedia of Korean Culture, *Saju*](https://encykorea.aks.ac.kr/Article/E0025957) describes the Ja-to-Hae two-hour sequence; the existing boundary tests verify the exact 23:00–00:59 through 21:00–22:59 partition. | Matches the 12 stored windows. |
| Major solar-term to month branch | [Korean Naming Research Institute FAQ](https://www.irum.com/Support/Faq/12815) prints the twelve pairings from Ipchun→In through Sohan→Chuk. | Exact 12/12 match. |

`tests/test_data_and_hidden_stems.py` records these cycles, all 12 hour
windows, and all 12 major-term/month-branch pairs as explicit regression
values. Existing structural tests still protect canonical ordering and Enum
vocabulary integrity.

## Still deliberately unapproved

- Per-stem and per-branch element/polarity assignments have not yet received a
  full second-source row-by-row audit in this record.
- English animal labels are display vocabulary and have not received a source
  decision.
- This audit does not decide true-solar time, a day boundary, or interpretive
  meaning.

Accordingly, no core-table value, version, or status changes here.
