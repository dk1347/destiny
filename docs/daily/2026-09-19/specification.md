# Module Specification: JDN Calculator (`src/engine/jdn.py`)

## 1. Function Specs
- `date_to_jdn(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> float`
  - 입력받은 양력 연/월/일/시/분을 율리우스일(JDN) 플로트 값으로 변환한다.
  - 음수 연도(B.C.) 및 윤년 처리를 정밀하게 포함한다.

- `jdn_to_date(jdn: float) -> dict`
  - JDN 값을 입력받아 `{ "year": int, "month": int, "day": int, "hour": int, "minute": int }` 형태로 복원한다.

## 2. Test Cases (`tests/test_jdn.py`)
- Standard Date Test: `2026-09-19 00:00:00` ➔ 계산된 JDN 값 검증
- Historical Date Test: 윤년 포함 과거 일자 검증
- Round-trip Test: `date_to_jdn` 후 `jdn_to_date` 실행 시 원본 날짜와 일치 여부 확인
