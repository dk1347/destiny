# Saju Calculation Validation Cases

> Status: Test-plan draft — expected astronomical values are intentionally not yet populated.

## Purpose

이 폴더는 Destiny 사주 엔진의 회귀 테스트 사례를 저장한다. 사례는 엔진의 계산 사실만 검증하며, 길흉 해석이나 LLM 출력은 포함하지 않는다.

## Rules

- 테스트 입력은 합성 데이터 또는 사용 허가된 공개 사례만 사용한다.
- 입력·시간 복원 결과·Calculation Profile·기대 결과를 모두 기록한다.
- 독립된 두 출처로 확인되지 않은 절입시각·일주 기준일은 `pending_verification`으로 둔다.
- 테스트를 통과시키기 위해 기대값을 맞추지 않는다. 근거가 바뀌면 dataset/engine version을 올린다.

## Case categories

| ID prefix | 검증 대상 | 상태 |
|---|---|---|
| `YEAR-IPCHUN` | 입춘 전·정각·후 연주 경계 | 데이터 출처 확정 대기 |
| `MONTH-TERM` | 12 절입 월주 경계 | 데이터 출처 확정 대기 |
| `DAY-ANCHOR` | 기준일 기반 일주 60일 순환 | anchor 검증 대기 |
| `HOUR-BOUNDARY` | 23:00, 00:00, 01:00 등 시지 경계 | 준비 가능 |
| `PARTIAL-UNKNOWN` | 출생시 unknown인 3주6자 | 준비 가능 |
| `AMBIGUOUS-LUNAR` | 윤달 모호성 후보 계산 | calendar dataset 확정 대기 |
| `TIME-AMBIGUOUS` | DST·역사적 시간대 모호성 | time-resolution engine 연동 대기 |

## Fixture contract

각 JSON fixture는 아래 형태를 사용한다.

```json
{
  "case_id": "HOUR-BOUNDARY-001",
  "status": "ready",
  "purpose": "23:00 is mapped to the Zi branch under kr_standard_v1.",
  "birth_profile": {"calendar_type":"solar","year":2000,"month":1,"day":2,"hour":23,"minute":0},
  "resolved_time": {"legal_local_datetime":"2000-01-02T23:00:00","resolution_status":"resolved"},
  "calculation_profile_id": "kr_standard_v1",
  "expected": {"hour_branch":"ja"},
  "evidence": {"source":"core_tables_v1","source_version":"1.0.0"}
}
```

## First implementation gate

연·월·일주 계산을 출시하기 전에 `YEAR-IPCHUN`, `MONTH-TERM`, `DAY-ANCHOR` 범주의 각 경계마다 직전·정각·직후 사례를 채우고, 독립 검증을 통과해야 한다.
