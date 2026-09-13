# Destiny — Birth Profile Specification

> Version: 1.1  
> Phase: Core Data Model  
> Status: Draft for Architecture Review

---

## 1. Purpose

BirthProfile은 Destiny 전체 시스템에서 사용하는 공통 출생정보 표준이다.

다음 시스템의 공통 입력 기반으로 사용할 수 있어야 한다.

- Saju / Four Pillars
- Compatibility
- Date Selection
- Astrology
- 5 Pillars Research
- Myung-Gung Research
- Future Global Divination Systems

핵심 원칙:

> Preserve what the user entered.  
> Normalize without destroying the original.  
> Never invent unknown birth information.

---

## 2. Data Processing Flow

```text
User Input
   ↓
RawBirthInput
   ↓
Validation
   ↓
Normalization
   ↓
BirthProfile
   ↓
Time / Calendar / Location Resolution
   ↓
Calculation Engines
```

Raw input과 normalized data는 반드시 분리한다.

---

## 3. Birth Information Requirement Policy

사주 계산의 기본 필수 출생정보:

- 출생년도
- 출생월
- 출생일
- Calendar Type (양력 / 음력)

다음은 선택 입력값이며 사용자가 모를 수 있다.

- 출생시
- 출생분
- 출생초
- 출생지

사용자가 모르는 값을 현재 시각, 00분, 정오, 현재 거주지 등의 임의 기본값으로 대체하지 않는다.

정보가 일부 없더라도 계산 가능한 범위까지 계산한다.

예:

```text
생년월일 확인 + 출생시간 unknown
        ↓
연주 + 월주 + 일주 계산
        ↓
3주6자 기반 분석
        ↓
시주 관련 분석 제외
```

출생 시진을 알지만 정확한 분을 모르는 경우 전통 4주8자 계산에는 사용할 수 있다.
정확한 분을 요구하는 실험적 계산에는 사용하지 않는다.

---

## 4. Automatic Resolution Policy

사용자가 알아야 하는 사실만 묻는다.

시스템이 달력, 역사적 시간대 자료, 위치 자료, 천문 계산 등으로 확정할 수 있는 값은 자동으로 계산한다.

예:

- 해당 연도의 윤달 존재 여부
- 양력/음력 변환
- 출생 당시 법정 표준시
- 당시 UTC offset
- 서머타임(DST) 적용 여부
- 출생지의 위도/경도
- 평균태양시 계산
- 진태양시 계산에 필요한 천문 보정값

원칙:

> 계산으로 확정할 수 있는 것은 자동 계산한다.  
> 계산으로 확정할 수 없는 사실은 사용자에게 묻고, 그래도 알 수 없으면 unknown으로 남긴다.

자동 계산값에는 가능한 경우 source, engine version, confidence를 기록한다.

---

## 5. RawBirthInput

사용자가 실제로 입력한 값은 수정하지 않고 보존한다.

예:

```json
{
  "display_name": "홍길동",
  "calendar_type": "lunar",
  "year": 1990,
  "month": 5,
  "day": 10,
  "leap_month": "unknown",
  "hour": 23,
  "minute": 35,
  "birth_place": "서울",
  "time_precision": "minute"
}
```

Raw input은 오류 분석, 재계산, 사용자 확인 및 계산 재현에 사용할 수 있다.

---

## 6. Core BirthProfile

개념적 구조:

```json
{
  "profile_version": "1.1",
  "raw_input": {},
  "calendar": {},
  "date_time": {},
  "location": {},
  "timezone": {},
  "precision": {},
  "normalization": {},
  "confidence": {},
  "metadata": {}
}
```

이 JSON은 구현 파일이 아니라 데이터 구조 명세 예시다.

---

## 7. Calendar Data

Calendar layer는 사용자가 입력한 달력 체계와 정규화된 날짜를 분리한다.

필요 정보:

- input_calendar
- input_year / month / day
- lunar_leap_month
- normalized_calendar
- normalized_date
- conversion_source
- conversion_engine_version

양력 입력은 Gregorian 기준으로 정규화한다.

음력 입력은 검증된 Calendar Engine을 사용한다.

---

## 8. Leap Month Handling

윤달 상태:

```text
yes
no
unknown
not_applicable
```

해당 연도/월에 윤달이 존재하지 않는 것이 달력 계산으로 확인되면 시스템이 자동으로 `no`를 확정할 수 있다.

평달과 윤달이 모두 가능한 월인데 사용자가 어느 쪽인지 모르면:

```text
leap_month = unknown
```

으로 유지한다.

이 경우:

- 임의 선택 금지
- 사용자 확인 요청 가능
- 가능한 날짜 후보 생성 가능
- 후보별 계산 결과 분리 가능

---

## 9. Date and Time Data

출생기록의 현지 날짜와 시각을 사실 데이터로 보존한다.

시간을 모르면:

```text
time_known = false
hour = null
minute = null
second = null
```

임의로 00:00 또는 12:00을 넣지 않는다.

---

## 10. Time Precision

시간 정밀도 예:

```text
unknown
date_only
hour_block
hour
minute
second
```

- `date_only`: 날짜만 확인
- `hour_block`: 전통 시진 정도 확인
- `hour`: 시간 단위 확인
- `minute`: 시·분 확인
- `second`: 초 단위까지 확인

정밀도가 높다고 운세의 예측 정확성이 자동으로 높아진다고 주장하지 않는다.

---

## 11. Location Data

사용자는 일반적으로 위도/경도를 직접 입력하지 않는다.

사용자 입력 예:

```text
서울
부산
도쿄
뉴욕
```

시스템은 가능한 경우 이를 다음과 같이 정규화한다.

- raw/input place label
- normalized place
- country/region
- latitude
- longitude
- location precision
- location source

사용자가 입력한 원래 지명은 정규화된 지명으로 덮어쓰지 않는다.

---

## 12. Location Precision

예:

```text
unknown
country
region
city
district
exact
```

MVP에서는 일반적으로 city-level이면 충분하다.

정밀 주소 입력을 요구하지 않는다.

---

## 13. Historical Place Preservation

과거 지명, 행정구역 변경 전 지명, 사용자가 기억하는 장소 표현을 raw data로 보존한다.

Location Resolution Layer가 현대 좌표 또는 적절한 역사적 위치로 정규화하더라도 원본 지명을 삭제하지 않는다.

---

## 14. Global Time Resolution Layer

Destiny는 한국 전용 시간 처리 로직을 Core에 하드코딩하지 않는다.

시간 복원은 지역/국가/시대별 규칙을 적용할 수 있는 Global Time Resolution Layer에서 수행한다.

개념:

```text
Recorded Birth Date/Time
        ↓
Birth Location Resolution
        ↓
Historical Time Rules
        ↓
Legal Time / UTC Resolution
        ↓
Astronomical Time Calculations
        ↓
Resolved Time Set
```

국가 하나만으로 시간대를 결정하지 않는다.

한 국가 안에 여러 시간대가 존재할 수 있고 동일 지역도 역사적으로 표준시가 변경될 수 있다.

---

## 15. Historical Time Rules

지역 및 시대별로 다음 요소를 해결할 수 있어야 한다.

- timezone identifier
- historical UTC offset
- standard time changes
- daylight saving time (DST)
- DST start/end rules
- exceptional historical changes
- valid_from / valid_to
- source
- confidence

개념적 Rule:

```text
region
timezone_id
valid_from
valid_to
rule_type
offset
source
confidence
```

실제 구현에서는 검증된 시간대 데이터베이스를 우선 활용하고, 별도 Destiny rule은 보완·검증이 필요한 경우에 사용한다.

---

## 16. Recorded Time, Legal Time and UTC

다음 값을 개념적으로 구분한다.

```text
Recorded Local Time
Legal / Civil Time
UTC
Local Mean Solar Time
True Solar Time
```

사용자가 입력한 출생기록 시각은 원본으로 유지한다.

역사적 표준시나 DST를 적용해 계산된 값이 원본 입력을 덮어쓰지 않는다.

---

## 17. Local Mean Solar Time

출생지의 경도와 해당 법정 시간대의 기준을 이용하여 평균태양시(Local Mean Solar Time)를 계산할 수 있도록 한다.

대략적인 천문 개념:

```text
경도 15° ≈ 1시간
경도 1° ≈ 4분
```

정확한 구현 공식과 기준은 별도 계산 명세에서 정의한다.

---

## 18. True Solar Time

진태양시(True Solar Time)는 평균태양시에 실제 태양 운동에 따른 균시차(Equation of Time) 등을 고려한 시간 표현이다.

개념:

```text
Legal Time
   ↓
Longitude Correction
   ↓
Local Mean Solar Time
   ↓
Equation of Time
   ↓
True Solar Time
```

진태양시를 계산할 수 있다는 사실과, 그것을 사주 계산의 기본 시각으로 채택한다는 것은 서로 다른 결정이다.

사주에서 어떤 시간 기준을 사용할지는 Calculation Profile에서 결정한다.

---

## 19. Time Resolution Rules vs Saju Rules

두 종류의 규칙을 명확히 분리한다.

### Time Resolution Rules

현실 세계의 시각을 복원·계산하는 규칙:

- historical timezone
- UTC offset
- DST
- location/longitude
- Local Mean Solar Time
- True Solar Time

### Saju Calculation Rules

복원된 시간 중 무엇을 명리 계산에 적용할지 결정하는 규칙:

- time basis
- day boundary
- Zi hour treatment
- 야자시 / 조자시
- solar-term boundary
- Daewoon rules

원칙:

> 현실의 시간 복원은 Time Resolution Engine이 담당하고,  
> 명리학적 시간 해석은 Saju Calculation Engine이 담당한다.

---

## 20. Day Boundary and Zi Hour

BirthProfile은 사용자가 입력한 실제 날짜와 시간을 보존한다.

다음과 같은 규칙은 BirthProfile에 하드코딩하지 않는다.

```text
midnight
zi_hour_23
```

23:00~01:00 출생자에 대한 야자시/조자시 및 일주 변경 판단은 Saju Calculation Profile에서 수행한다.

---

## 21. BirthProfile and QueryContext Separation

BirthProfile과 운세를 의뢰한 시점은 서로 다른 데이터다.

```text
BirthProfile
├─ birth_date
├─ birth_time
└─ birth_location

QueryContext
├─ query_datetime
├─ query_location
└─ question
```

출생시간을 모른다고 의뢰 시각을 출생시간으로 대체하지 않는다.

출생지를 모른다고 현재 거주지를 출생지로 대체하지 않는다.

QueryContext는 향후 질문 시점을 사용하는 별도 분석/점술 Engine에서 활용할 수 있지만 Saju Natal Calculation과 구분한다.

---

## 22. Confidence Model

각 데이터에 신뢰 수준을 기록할 수 있다.

예:

```text
confirmed
high
medium
low
unknown
```

신뢰도는 출생정보뿐 아니라 역사적 위치/시간대 자동 해결 결과에도 적용할 수 있다.

---

## 23. Source Metadata

가능한 출생정보 출처 예:

```text
official_record
hospital_record
family_record
user_memory
estimated
unknown
```

자동 계산 데이터에는 별도의 calculation/resolution source를 기록할 수 있다.

---

## 24. Unknown Data Policy

Destiny의 핵심 원칙:

> Unknown is a valid value.

정보가 없다는 사실 자체가 데이터다.

LLM이나 프로그램이 편의를 위해 누락된 출생정보를 만들어내지 않는다.

---

## 25. Candidate Resolution

입력만으로 하나의 사실을 확정할 수 없는 경우 candidate를 생성할 수 있다.

예:

```text
음력 5월
윤달 여부 unknown
```

실제로 평5월과 윤5월이 모두 존재한다면 두 후보를 유지할 수 있다.

후보는 명확하게 구분하며 하나를 임의로 정답으로 선택하지 않는다.

---

## 26. Validation

입력 및 정규화 단계에서 다음을 검증한다.

- 존재하지 않는 날짜
- 음력 날짜 유효성
- 윤달 가능 여부
- 시간 범위
- 지역 식별 가능 여부
- timezone resolution 여부
- ambiguous local time
- historical timezone data availability
- calendar conversion success

---

## 27. Error / Warning Policy

잘못된 입력은 조용히 수정하지 않는다.

개념적 오류 코드 예:

```text
INVALID_DATE
INVALID_TIME
INVALID_LUNAR_DATE
INVALID_LEAP_MONTH
AMBIGUOUS_LEAP_MONTH
UNKNOWN_TIME
UNKNOWN_LOCATION
LOCATION_NOT_FOUND
TIMEZONE_NOT_FOUND
AMBIGUOUS_LOCAL_TIME
HISTORICAL_TIMEZONE_UNCERTAIN
CALENDAR_CONVERSION_FAILED
```

이 코드는 현재 별도 JSON 파일을 의미하지 않는다.
실제 코드 구조와 schema는 구현 단계에서 결정한다.

---

## 28. Partial Calculation and Disclosure

출생정보가 부족하더라도 가능한 계산은 수행한다.

단, 수행하지 못한 영역과 이유를 결과에 명확히 표시한다.

예:

> 출생시간을 알 수 없어 시주를 제외한 범위에서 분석했습니다.

정보 부족으로 수행하지 않은 계산을 AI가 추정하여 채우지 않는다.

---

## 29. Privacy Principle

BirthProfile은 개인정보가 될 수 있으므로 최소수집을 기본으로 한다.

- 실명 필수 아님
- 정밀 주소 필수 아님
- 도시 단위 위치 권장
- 외부 LLM에 불필요한 개인정보 전송 금지
- 사용자 계정 정보와 BirthProfile의 논리적 분리

---

## 30. Name Handling

이름은 기본 사주 계산 필수값이 아니다.

MVP에서는 `display_name` 정도로 취급하며 실명을 강제하지 않는다.

향후 성명학 기능을 추가할 경우 별도 NameProfile을 설계한다.

---

## 31. Profile Attributes

성별 등 일부 프로필 속성은 특정 전통 계산 규칙에 영향을 줄 수 있다.

BirthProfile에서는 가능한 한 사실 데이터로 저장하고, 어떤 계산에 어떻게 사용할지는 Calculation Profile에서 정의한다.

---

## 32. Versioning and Reproducibility

BirthProfile schema에는 version을 둔다.

같은 다음 입력 조합은 동일한 계산 결과를 재현할 수 있어야 한다.

```text
BirthProfile
+
Resolved Time Data
+
CalculationProfile
+
EngineVersion
=
Reproducible Result
```

적용된 시간 규칙과 데이터 source/version도 추적 가능해야 한다.

---

## 33. Engine Independence

BirthProfile은 특정 점술 Engine에 종속되지 않는다.

BirthProfile에는 출생 사실을 저장하고 사주 계산 결과는 별도 SajuResult에 저장한다.

예:

```text
BirthProfile.birth_date        → 허용
BirthProfile.saju_day_master   → 금지
```

---

## 34. Global Expansion Policy

BirthProfile과 Time Resolution Layer는 다음 지역 확장을 염두에 둔다.

```text
Korea
→ Japan
→ China
→ India / Thailand / Vietnam / Southeast Asia
→ United States
→ Europe
→ Global
```

새 국가가 추가될 때 Core BirthProfile 구조를 다시 설계하는 대신 해당 지역의 위치·시간·달력 규칙을 확장하는 방향을 우선한다.

---

## 35. Factual Integrity Principle

Destiny의 핵심 데이터 철학:

> 입력된 사실만 계산하고, 모르는 것은 모른다고 처리한다.

그리고:

> 사용자가 알아야 하는 사실만 묻고, 시스템이 신뢰성 있게 계산할 수 있는 것은 자동으로 처리한다.

전체 흐름:

```text
Raw Facts
↓
Validated / Normalized Facts
↓
Time / Calendar / Location Resolution
↓
Calculation
↓
Knowledge
↓
Interpretation
```

LLM이 출생정보나 계산값을 임의 생성하는 구조를 허용하지 않는다.

---

## 36. Architecture Review Items

다음 항목은 Saju Calculation Specification 및 Claude Architecture Review에서 검토한다.

- Production에서 사용할 calendar conversion source
- Historical timezone source와 fallback 정책
- DST ambiguous/nonexistent local time 처리
- 평균태양시 공식
- 균시차/진태양시 계산 방법
- 사주 기본 time basis
- 야자시/조자시 기본 정책
- 일주 변경 기준
- 절입시각 처리
- 대운 순역 및 기산 방식

---

## 37. Next Specification

Next:

`04_SAJU_CALCULATION_SPEC.md`

여기서 현실 시간 복원 결과를 실제 사주 계산에 어떻게 적용할지 정의한다.

주요 대상:

- 천간 / 지지
- 연주
- 월주
- 절기 / 입춘
- 일주
- 시주
- 야자시 / 조자시
- time basis
- 오행
- 십신
- 지장간
- 합 / 충 / 형 / 파 / 해
- 대운
- 세운
- Calculation Profile
- Engine Version
- Validation Rules
