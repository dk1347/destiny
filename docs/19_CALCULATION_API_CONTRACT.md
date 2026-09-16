# Destiny — Calculation API Contract

> Status: framework-neutral MVP contract. No public endpoint exists yet.

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

## Error response

```json
{"code":"SOLAR_TERM_DATA_UNAVAILABLE","message":"This birth datetime is outside the verified supported range."}
```

Messages are plain language and do not claim that an unavailable result was
calculated. Diagnostic codes remain stable for clients; implementation traces
stay server-side.

## Production gate

The public endpoint uses `RuleRegistry()` only. It must never enable
`allow_unverified=True`; that flag is limited to tests and explicit internal
verification jobs. The endpoint does not invoke an LLM.
