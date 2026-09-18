# Korean Historical Civil-Time Policy

> Status: policy and test plan only. The current calculation profile has not
> been changed by this document.

## Decision

Birth time means the civil clock time recorded at the birth place. For Korean
MVP calculations, resolve that clock time using a **pinned** `Asia/Seoul`
timezone-data release rather than treating every historical input as an
unchanging UTC+09:00 offset.

The user does not need to know timezone mechanics. The result instead states
the applied civil-time profile and warns only when a submitted local time was
ambiguous or did not exist because a clock changed.

## Evidence to preserve

| Fact | Evidence | Product implication |
| --- | --- | --- |
| Korea returned to the 135°E standard meridian on 1961-08-10. | [National Archives: summer-time history](https://theme.archives.go.kr/next/koreaOfRecord/summerTime.do) | Do not apply pre-1961 offset assumptions to later dates. |
| Summer time was used again in 1987 and 1988. | [National Archives daily record](https://theme.archives.go.kr/next/daily/viewMain.do?selectDay=20140510) and [IANA TZ Database documentation](https://data.iana.org/time-zones/tzdb-2017c/tz-link.htm) | A local clock time in these years needs transition-aware handling. |
| A 1948 daylight-saving proclamation set clocks forward one hour and later returned them. | [Korean History Database primary record](https://db.history.go.kr/contemp/gb/level.do?levelId=gbmg_1948_05_20_a0014&viewTab=compare) | Earlier support requires documentary checks, not a blanket UTC+09 rule. |

IANA timezone data is the technical distribution used by many systems, but its
maintainers note that government time rules can change and historical records
may be incomplete. Treat it as the versioned implementation dataset; retain
the cited historical evidence for review.

## Implementation contract

1. Add a `civil_time_policy_id` to every datetime calculation response.
2. Parse a birth time as a local `Asia/Seoul` wall-clock value, then resolve it
   under the repository-pinned timezone-data version.
3. If the local time is skipped during a spring transition, return
   `NONEXISTENT_LOCAL_TIME` and ask for a birth record correction.
4. If the local time occurs twice during an autumn transition, return
   `AMBIGUOUS_LOCAL_TIME` and ask which recorded offset applied; never select
   one silently.
5. Persist the original local date/time and the resolved UTC offset in a
   calculation trace. Do not expose a false precision claim beyond the input.

## Test matrix before enabling historical-time support

| Case | Expected result |
| --- | --- |
| 1963-10-31 12:30 in Seoul | Resolves as an ordinary Korean civil time; independent solar-term coverage remains a separate gate. |
| Immediately before/after the 1961 standard-time transition | Recorded offset changes only as specified by the pinned dataset. |
| 1987 and 1988 DST start | Skipped local-time interval is rejected. |
| 1987 and 1988 DST end | Repeated local-time interval requires disambiguation. |
| Contemporary Korean date | Continues to resolve as KST without DST. |
| Pre-1961 date | Remains unavailable until its historical timezone evidence and solar-term coverage are both approved. |

## Scope boundaries

- This policy concerns legal civil time only; it does not implement true solar
  time.
- Birthplace outside Korea is out of scope for the Korean MVP.
- A complete solar-term record is still required after a civil-time input is
  resolved.
- Do not rely on the operating system's unpinned tzdata as production evidence.
