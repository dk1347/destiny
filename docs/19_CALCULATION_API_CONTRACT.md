# Destiny — Calculation API Contract

> Status: guarded MVP implementation. `src/destiny_saju/api.py` exposes this
> contract for internal integration; it is not a deployed public service.

## Request

`POST /v1/saju/calculate` accepts only a resolved local civil datetime and an
optional supported calculation-profile ID in the first API iteration.

```json
{"birth_local_datetime":"2026-02-04T05:02:00+09:00","calculation_profile_id":"kr_standard_v1"}
```

The API must reject naive datetimes, non-Asia/Seoul offsets, unknown profiles,
and input outside the verified solar-term coverage. Lunar conversion, unknown
birth time, historical timezone recovery, and true-solar-time choices enter
only after their own resolver contracts exist.

## Success response

The response body is `SajuResult.as_dict()`. It contains canonical IDs, not
interpretive prose. The server returns provenance and warnings, but never API
keys, host paths, raw request logs, or other users' data.

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

Both datetimes must use the Asia/Seoul UTC+09:00 offset. A successful response
contains the target calendar year, the annual pillar, and structural
stem/branch findings relative to the natal four pillars. `participants` marks
the annual locations as `seun_stem` or `seun_branch`. It does not return luck,
priority, health, relationship, financial, or other interpretive claims.

## Error response

```json
{"code":"SOLAR_TERM_DATA_UNAVAILABLE","message":"This birth datetime is outside the verified supported range."}
```

Messages are plain language and do not claim that an unavailable result was
calculated. Diagnostic codes remain stable for clients; implementation traces
stay server-side.

## Production gate

Both public endpoints use `RuleRegistry()` only. They must never enable
`allow_unverified=True`; that flag is limited to tests and explicit internal
verification jobs. The endpoints do not invoke an LLM.
