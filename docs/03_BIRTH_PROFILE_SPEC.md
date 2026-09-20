# 03. BirthProfile Specification (출생정보 정규화 규격서)
> **문서 버전**: 1.0.0  
> **작성 일자**: 2026 년 9 월 20 일  
> **상태**: 확정 (Approved)  
> **적용 모듈**: `src/destiny_saju/birth/`

---

## 1. 개요 및 설계 철학

본 규격서는 사용자로부터 입력받은 다양한 형태의 출생 정보를 표준화된 계산 데이터 (`NormalizedBirthProfile`) 로 정규화하는 규칙을 정의한다.

### 핵심 원칙
1. **원본 보존 (Raw Preservation)**: 사용자가 입력한 원래의 값 (Raw Input) 은 절대 수정하거나 유실하지 않는다.
2. **추측 금지 (No Hallucination/Guesswork)**: 불확실하거나 모르는 정보는 AI 나 시스템이 임의로 추정하여 채우지 않는다.
3. **자동화 우선 및 사용자 선택**:
   - 시스템이 역법/천문학적 사실로 100% 자동 판단 가능한 항목은 사용자 개입 없이 자동 보정한다.
   - 복수의 가능성이 존재하는 모호한 상태에서는 임의 판단을 배제하고 사용자에게 명시적 선택을 요청한다.

---

## 2. 데이터 모델 스키마

### 2.1 RawBirthInput (입력 원본)
```json
{
  "calendar_type": "solar | lunar",
  "birth_year": 1988,
  "birth_month": 7,
  "birth_day": 15,
  "birth_time_str": "14:30",
  "is_leap_month": null,
  "gender": "male | female",
  "location_text": "서울시 종로구"
}

### 2.2 NormalizedBirthProfile (정규화 결과)
{
  "profile_id": "uuid-v4",
  "raw_input": { ... },
  "normalized_utc_timestamp": "1988-07-15T04:30:00Z",
  "solar_birth_date": "1988-07-15",
  "base_timezone": "Asia/Seoul",
  "historical_dst_applied": true,
  "dst_offset_minutes": -60,
  "meridian_offset_minutes": -30,
  "adjusted_solar_time": "13:00:00",
  "time_precision": "minute | hour_shijin | unknown",
  "analysis_mode": "FOUR_PILLARS | THREE_PILLARS",
  "applied_rule_ids": ["KOREA_HISTORICAL_DST_1988", "MERIDIAN_135_TO_127_5"],
  "resolution_status": "RESOLVED | CANDIDATE_BRANCH"
}

##3. 핵심 정규화 정책

### 3.1 음력 및 윤달 (閏月) 자동 판정 정책
Case A (윤달 부존재 월): 입력된 연·월에 윤달이 없는 경우 시스템이 is_leap_month = false 로 자동 확정한다. (UI 에서 윤달 선택 비활성화)
Case B (윤달 공존 월): 해당 연·월에 실제 윤달이 존재하는 경우 사용자에게 명시적으로 선택을 요청한다 ([평달] / [윤달] / [모름]).
사용자가 모름을 선택한 경우: 임의 단일값을 부여하지 않고, 평달 후보 프로필과 윤달 후보 프로필 2 개를 분기 (Branching) 생성하여 보존한다.
Case C (유효성 오류): 윤달이 없는 달에 사용자가 강제로 윤달을 지정한 경우 검증 예외 (InvalidLeapMonthException) 를 반환한다.

### 3.2 역사적 서머타임 (DST) 및 표준 자오선 자동 보정
사용자에게 과거 표준시 변경에 대한 지식을 요구하지 않으며, 내장된 역사 테이블에 의해 자동 보정된다.
서머타임 (DST) 자동 판정 테이블:
1 차: 1948.06.01 ~ 1951.09.08
2 차: 1955.05.05 ~ 1960.09.18
3 차: 1987.05.10 ~ 1987.10.11 / 1988.05.08 ~ 1988.10.09
해당 구간 출생 시: 자동으로 -60 분 보정 적용 및 근거 기록.
역사적 표준 자오선 시차 보정:
1908.04.01 ~ 1911.12.31: 동경 127.5 도 (보정 0 분)
1912.01.01 ~ 1954.03.20: 동경 135.0 도 (자연시 오차 -30 분 보정)
1954.03.21 ~ 1961.08.09: 동경 127.5 도 (보정 0 분)
1961.08.10 ~ 현재: 동경 135.0 도 (자연시 오차 -30 분 보정)

### 3.3 출생 시간 미상 (Unknown Time) 처리 정책
사용자가 시간을 모르는 경우 임의의 시간 (예: 12:00 정오 등) 을 시주로 채택하지 않는다.
time_precision = "unknown"으로 기록하고, 시스템은 자동으로 3 주 (삼주 6 자: 년·월·일주) 분석 모드 (analysis_mode = "THREE_PILLARS") 로 전환한다.
시주 (Hour Pillar) 는 null 로 유지하며, 시주 기반의 해석 영역 (말년운, 자녀운 등) 은 해석 배제 대상으로 태깅한다.