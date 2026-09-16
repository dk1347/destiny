# Destiny — Calculation API Contract

> Status: guarded MVP implementation. `src/destiny_saju/api.py` exposes this
> contract for internal integration; it is not a deployed public service.

## Request

`POST /v1/saju/calculate` accepts exactly one of a resolved local civil
datetime or a local civil date, plus an optional supported calculation-profile
ID. A date-only request never invents an unknown birth time.

```json
{"birth_local_datetime":"2026-02-04T05:02:00+09:00","calculation_profile_id":"kr_standard_v1"}
```

```json
{"birth_local_date":"2026-02-05"}
```

A datetime must use the Korea Standard Time UTC+09:00 offset. The API rejects
naive or non-KST datetimes, unknown profiles, requests containing both input
forms, and input outside verified solar-term coverage. A stable date-only
request returns year, month, and day pillars with `hour: null` and a warning.
If the date crosses a solar-term boundary, it returns `BIRTH_TIME_NEEDED`
rather than guessing which side applies. Lunar conversion, historical timezone
recovery, and true-solar-time choices enter only after their own resolver
contracts exist.

## Success response

The response body is `SajuResult.as_dict()`. It contains canonical IDs, not
interpretive prose. The server returns provenance and warnings, but never API
keys, host paths, raw request logs, or other users' data. Date-only results
have `status: "partial"`; a complete four-pillar result has `status:
"complete"`.

## Annual-cycle request

`POST /v1/seun/calculate` accepts the resolved birth local datetime and a
resolved target local datetime, plus the optional calculation-profile ID.

```json
{
  "birth_local_datetime":"2026-02-04T05:02:00+09:00",
  "target_local_datetime":"2026-03-01T12:00:00+09:00",
  "calculation_profile_id":"kr_standard_v1"
}
```

Both datetimes must use the Asia/Seoul UTC+09:00 offset. This endpoint needs a
known birth time and is not available for a date-only result. A successful
response contains the target calendar year, the annual pillar, and structural
stem/branch findings relative to the natal four pillars. `participants` marks
the annual locations as `seun_stem` or `seun_branch`. It does not return luck,
priority, health, relationship, financial, or other interpretive claims. The
response also includes provenance for every rule dataset used to calculate the
result.

## Error response

```json
{"code":"BIRTH_TIME_NEEDED","message":"이 날짜는 절기 전환일이라 검증된 결과를 위해 출생시간이 필요해요."}
```

Messages are plain Korean and do not claim that an unavailable result was
calculated. Diagnostic codes remain stable for clients; implementation traces
stay server-side.

## Production gate

Both public endpoints use `RuleRegistry()` only. They must never enable
`allow_unverified=True`; that flag is limited to tests and explicit internal
verification jobs. The endpoints do not invoke an LLM.
