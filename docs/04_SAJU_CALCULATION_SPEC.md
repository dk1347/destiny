# Destiny — Saju Calculation Specification

> Version: 0.1  
> Phase: Core Calculation Engine  
> Status: Draft for Architecture Review  
> Depends on: `03_BIRTH_PROFILE_SPEC.md`

---

## 1. Purpose

이 문서는 Destiny의 사주(Four Pillars) 계산 엔진이 동일한 출생정보에서 언제나 동일한 결과를 만들기 위한 규칙을 정의한다.

이 문서의 범위는 **계산**이다. 고전 문헌·RAG·LLM은 계산 결과를 해석할 수 있지만, 간지·오행·십신 등을 임의로 추정하거나 변경할 수 없다.

```text
BirthProfile + Resolved Time Set + Calculation Profile + Engine Version
                              ↓
                    Saju Calculation Engine
                              ↓
               Structured SajuResult (facts/rules/evidence)
                              ↓
                      Knowledge + Interpretation
```

---

## 2. Scope and Non-goals

### In scope

- 연주·월주·일주·시주
- 24절기 및 입춘·절입 경계
- 천간·지지·오행·음양
- 지장간·십신·12운성(후속 확장 가능)
- 합·충·형·파·해 등 관계 데이터
- 대운·세운의 계산 규칙과 버전 관리
- 누락·모호한 출생정보에 대한 부분 계산 및 후보 결과

### Out of scope

- 출생지 좌표, 역사적 시간대, DST, 평균/진태양시의 산출 자체
- 문헌 기반 길흉 해석·상담 문장 생성
- 성명학, 관상, 타로, 점성술 계산

위 현실 시간 복원은 Time Resolution Engine이 담당한다. 이 엔진은 그 결과 중 어떤 값을 사주 계산에 적용할지를 결정한다.

---

## 3. Immutable Principles

1. **계산과 해석을 분리한다.** 계산 엔진의 출력은 구조화된 사실이며 LLM이 수정할 수 없다.
2. **원본 입력을 보존한다.** BirthProfile의 원시 입력은 덮어쓰지 않는다.
3. **unknown은 유효한 값이다.** 출생시간·윤달 등이 없을 때 임의의 값으로 채우지 않는다.
4. **모호성은 결과로 드러낸다.** 단일 답이 보장되지 않으면 후보와 차이를 표시한다.
5. **같은 프로필과 규칙은 같은 결과를 낸다.** 사용한 데이터·규칙·엔진 버전을 모두 결과에 기록한다.

---

## 4. Calculation Inputs

엔진은 BirthProfile을 직접 수정하지 않고 아래의 확정 또는 후보 입력을 받는다.

```text
BirthProfile
Resolved Time Set
Calculation Profile
Engine Version
```

### 4.1 Resolved Time Set

Time Resolution Engine이 제공하는 값의 예:

```json
{
  "recorded_local_datetime": "1990-06-02T23:35:00",
  "legal_local_datetime": "1990-06-02T23:35:00",
  "utc_datetime": "1990-06-02T14:35:00Z",
  "local_mean_solar_datetime": null,
  "true_solar_datetime": null,
  "timezone_id": "Asia/Seoul",
  "resolution_status": "resolved"
}
```

`null`은 계산 실패가 아니라 해당 시간 기준을 아직 산출하지 않았다는 뜻일 수 있다. Calculation Profile이 요구하는 시간 기준이 없다면 그 프로필의 계산은 `blocked`로 처리한다.

### 4.2 Minimum input requirements

| 계산 항목 | 필요한 정보 | 부족할 때 |
|---|---|---|
| 연주·월주·일주 | 확정된 양력 날짜 | 계산 불가 또는 날짜 후보별 결과 |
| 시주 | 확정된 계산 기준 시각 | 3주6자 결과만 제공 |
| 대운 시작 나이 | 성별 규칙값, 절입시각, 출생시각 | 계산 보류 또는 범위로 표시 |

---

## 5. Calculation Profile

전통 및 서비스 정책의 차이를 코드 곳곳에 흩어 두지 않고 하나의 명시적 프로필로 관리한다.

MVP 기본 프로필은 `kr_standard_v1`이다. 이 명칭은 유일한 정통성을 주장하지 않으며, 서비스의 기본 계산 약속을 뜻한다.

```json
{
  "profile_id": "kr_standard_v1",
  "time_basis": "legal_local_time",
  "year_boundary": "ipchun",
  "month_boundary": "major_solar_term",
  "day_boundary": "zi_hour_start",
  "zi_hour_policy": "next_civil_day",
  "hour_branch_boundary": "two_hour_blocks",
  "daewoon_direction_rule": "defer_until_v1",
  "daewoon_start_rule": "defer_until_v1"
}
```

### 5.1 MVP policy decisions

| 항목 | `kr_standard_v1` 기본값 | 이유 |
|---|---|---|
| 계산 시각 | 법정 현지시 | 출생기록과 가장 직접적으로 대응하며 설명이 쉽다. |
| 연주 경계 | 입춘 순간 | 사주 서비스에서 널리 쓰이는 기준으로 명시한다. |
| 월주 경계 | 절기(12 절입) 순간 | 음력 월이 아니라 절기월을 사용한다. |
| 일주 경계 | 23:00 | 현재 적용된 기본값. 자정 기준은 별도 프로필로 제공한다. |
| 23:00–23:59 | 다음 민간 날짜의 일주 | 자시 시작과 동시에 일주를 변경한다. |
| 시지 | 2시간 단위 | 자시 23:00–00:59, 축시 01:00–02:59 등의 표준 구간. |

`true_solar_time`, 자정 일주 경계, 대운 세부 규칙은 검증이 끝난 뒤 별도 프로필로 추가한다. 기본 결과와 다른 프로필 결과를 섞어 보여주지 않는다.

### 5.2 자동 계산과 의미 있는 선택 정책

제품은 사용자가 결과를 받기 전에 야자시·진태양시 같은 전문 용어를
이해하도록 요구하지 않는다. 기록된 출생 사실과 확정된 법정 현지시를
바탕으로 기본 `kr_standard_v1` 프로필을 자동 계산한다.

필요한 데이터가 확보된 경우 엔진은 명시적으로 버전이 부여된 대안
프로필을 계산할 수 있다. 대안은 기본값과 구조화된 주 결과가 실제로
달라질 때에만 사용자에게 제시한다. 결과가 같으면 불필요한 선택을
만들지 않는다.

| 상황 | 자동 동작 | 결과가 다를 때의 사용자 선택 |
| --- | --- | --- |
| 23:00–00:59 자시 구간 출생 | 기본 23:00 경계 프로필을 계산하고, 제공 가능한 자정 경계 프로필도 비교 계산한다. | "밤 11시 날짜 변경 기준" / "기록된 날짜 기준" |
| 확정된 진태양시가 관련 주 경계를 넘는 경우 | 법정 현지시 결과와 진태양시 프로필을 계산한다. | "기록된 시각 기준" / "출생지 태양시 보정" |
| 시간 정밀도·위치·시간 복원 근거가 부족한 경우 | 보정을 만들어 내거나 비교 결과를 단정하지 않는다. | 한계를 설명하고 `unknown` 또는 후보 상태를 보존한다. |

초기 구현은 선택을 미리 강요하지 않고 쉬운 설명을 사용해야 한다. 고급
설정에서만 전문 용어와 프로필 식별자를 노출할 수 있다. 경계 근접
임계값을 도입할 경우 반드시 버전과 테스트를 갖춰야 하며, 막연한
“경계 근처” 표시는 계산 규칙이 아니다.

모든 결과는 선택된 프로필 식별자, 기본 프로필 식별자, 실제로 평가한
대안 프로필, 각 프로필에 적용한 확정 시각 기준, 구조화된 주 결과의
차이 여부를 보존해야 한다. 사용자의 이후 선택은 해당 결과 요청에만
적용하며 원래 BirthProfile을 덮어쓰거나 이전에 저장된 결과를 조용히
바꾸지 않는다.

---

## 6. Fundamental Tables

### 6.1 Heavenly Stems and Earthly Branches

계산 엔진은 고정된 순서와 속성 테이블을 사용한다.

```text
천간: 갑 을 병 정 무 기 경 신 임 계
지지: 자 축 인 묘 진 사 오 미 신 유 술 해
```

각 항목에는 최소한 다음 속성을 둔다.

```text
id, korean_name, hanja, order, yin_yang, element
```

간지 순환은 60갑자이며, stem index는 10, branch index는 12로 순환한다. 모든 테이블은 데이터 파일의 버전으로 관리한다.

### 6.2 Five elements and Ten Gods

오행은 목·화·토·금·수, 음양은 양·음으로 표현한다. 십신은 일간을 기준으로 산출하며, 결과에는 일간과의 관계 및 음양 일치 여부를 함께 기록한다.

십신 이름만 저장하지 않고 다음을 구조화한다.

```text
target_stem, relation_element, polarity_match, ten_god
```

---

## 7. Four Pillars Calculation

### 7.1 Solar calendar normalization

연·월·일·시 계산 전에 입력 달력은 검증된 Calendar Engine으로 proleptic Gregorian 날짜 또는 지원 범위의 양력 날짜로 정규화한다.

음력·윤달이 모호하면 가능한 양력 날짜마다 후보 계산을 생성한다.

### 7.2 Year pillar

연주는 Gregorian 1월 1일이 아니라 Calculation Profile의 `year_boundary`를 사용한다.

`ipchun` 프로필에서는 출생 계산 기준 시각이 해당 해 입춘 이전이면 전년의 간지를, 입춘 순간 이후면 해당 연도의 간지를 적용한다.

절입 순간과 정확히 같은 시각은 **새 경계에 포함**한다 (`>= boundary`).

### 7.3 Month pillar

월주는 음력 월이 아니라 12 절입에 따라 결정한다. 월지 순서는 인월에서 시작한다.

```text
입춘→인, 경칩→묘, 청명→진, 입하→사, 망종→오, 소서→미,
입추→신, 백로→유, 한로→술, 입동→해, 대설→자, 소한→축
```

월간은 연간과 월지의 관계를 이용해 고정 공식 또는 동등한 검증 테이블로 산출한다. 절입 천문 데이터의 출처·버전·정확도는 결과에 남긴다.

### 7.4 Day pillar

일주는 검증된 기준일(anchor)과 Julian Day Number 기반의 60갑자 순환으로 계산한다.

```text
sexagenary_index = modulo(anchor_index + days_between(anchor_date, target_date), 60)
```

anchor date와 index는 테스트 가능한 데이터 자산으로 버전 관리한다. 구현자는 온라인 음양력 결과를 런타임에 호출해 일주를 결정하지 않는다.

### 7.5 Hour pillar

출생시각이 확정된 경우에만 시주를 계산한다.

1. Calculation Profile의 `time_basis`로 계산 기준 시각을 선택한다.
2. `hour_branch_boundary` 규칙으로 시지를 정한다.
3. 일간과 시지의 관계 테이블로 시간간을 정한다.

시각이 2시간 구간 경계와 일주 경계에 걸릴 수 있으나 분 단위 정보가 없다면 후보 시주를 생성하거나 사용자에게 정밀도를 안내한다.

---

## 8. Hidden Stems and Derived Relations

### 8.1 Hidden stems

각 지지의 지장간은 versioned lookup table에서 가져온다. 본기·중기·여기의 역할 구분은 데이터에 보존하되, 가중치나 강약 판단은 해석 규칙으로 분리한다.

### 8.2 Relations

천간합·지지 육합·삼합·충·형·파·해 등은 "발견된 관계"로만 우선 산출한다.

```json
{
  "relation_type": "branch_clash",
  "participants": ["year_branch", "day_branch"],
  "values": ["자", "오"],
  "rule_set_version": "relations_v1"
}
```

관계의 길흉·우선순위·해소 여부는 Calculation Engine의 사실 계산이 아니라 Interpretation Rule Layer의 책임이다.

---

## 9. Fortune Cycles

대운·세운은 원국과 분리된 계산 모듈로 구현한다.

### 9.1 Seun (annual cycle)

세운은 각 대상 연도의 간지와 원국과의 관계를 구조화해 제공한다. 세운의 연도 경계도 Calculation Profile의 연주 경계를 명시적으로 따른다.

### 9.2 Daewoon (major cycle)

대운에는 전통별 차이가 크므로 `kr_standard_v1`에서는 계산 결과를 확정하지 않는다. v1 구현 전 다음을 단일 프로필로 확정해야 한다.

- 성별 및 연간 음양에 따른 순행/역행 규칙
- 출생 시점에서 이전·다음 절입 중 어떤 기준을 쓰는지
- 일수와 시작 연령의 환산 방식
- 절입 순간 데이터의 정밀도와 출처
- 출생시간 unknown일 때의 후보/범위 정책

대운을 제공할 때에는 반드시 적용 프로필과 시작 시점 산출 근거를 결과에 포함한다.

---

## 10. Result Contract

SajuResult는 표시용 문장이 아닌 계산 사실과 근거를 담는다.

```json
{
  "result_version": "1.0",
  "engine_version": "saju-engine/0.1.0",
  "calculation_profile_id": "kr_standard_v1",
  "status": "complete",
  "resolved_time_reference": "resolved-time-set-id",
  "pillars": {
    "year": {"stem": "경", "branch": "오"},
    "month": {"stem": "신", "branch": "사"},
    "day": {"stem": "갑", "branch": "자"},
    "hour": null
  },
  "derived": {"day_master": "갑", "elements": {}, "ten_gods": [], "relations": []},
  "candidates": [],
  "warnings": ["UNKNOWN_BIRTH_TIME"],
  "provenance": {"solar_term_dataset": "...", "calendar_engine": "..."}
}
```

`status` 값:

```text
complete       모든 요청된 주 계산 완료
partial        일부 계산만 완료
ambiguous      복수 후보 존재
blocked        필수 입력 또는 요구 시간 기준 없음
invalid        유효하지 않은 입력
```

---

## 11. Validation and Boundary Tests

엔진 릴리스 전 최소 다음 테스트를 통과해야 한다.

- 입춘 직전·정각·직후의 연주
- 12개 절입 직전·정각·직후의 월주
- 00:00 및 23:00 경계의 일주·시주
- 출생시간 unknown인 3주6자 결과
- 음력 평달/윤달 및 윤달 unknown 후보
- 역사적 표준시 변경과 DST의 ambiguous/nonexistent local time
- 서로 다른 Calculation Profile에서 의도적으로 달라지는 결과
- 기준일 전후 60일의 일주 연속성
- 독립적으로 검증된 신뢰 사례집과의 비교

테스트 케이스에는 개인정보를 쓰지 않고 합성 데이터 또는 사용 허가된 공개 예시를 사용한다.

---

## 12. Error and Disclosure Policy

사용자에게는 계산 상태와 제외 사유를 평이하게 보여 준다.

예:

```text
출생시간이 확인되지 않아 시주와 시주를 전제로 하는 해석은 포함하지 않았습니다.
```

가능한 오류/경고 코드:

```text
UNKNOWN_BIRTH_TIME
AMBIGUOUS_LUNAR_DATE
AMBIGUOUS_LOCAL_TIME
MISSING_REQUIRED_TIME_BASIS
SOLAR_TERM_DATA_UNAVAILABLE
DAY_PILLAR_ANCHOR_UNAVAILABLE
DAEWOON_RULE_NOT_CONFIGURED
```

---

## 13. Versioning and Audit Trail

결과마다 최소한 다음을 보존한다.

- BirthProfile version 및 식별자
- Resolved Time Set의 source/version
- calendar conversion 및 solar-term dataset version
- Calculation Profile ID와 전체 rule-set version
- Saju Engine version
- 계산 시각 및 status/warnings

규칙을 개선해 결과가 달라질 수 있다. 이 경우 과거 결과를 조용히 덮어쓰지 않고, 새 엔진 버전으로 재계산되었음을 표시한다.

---

## 14. Architecture Review Decisions Remaining

`kr_standard_v1`의 원국 계산은 위 기본값으로 진행할 수 있다. 프로덕션 구현 전에 아래 항목은 반드시 확정·검증한다.

1. 달력 변환, 절입시각, 역사적 시간대 데이터셋의 공급원과 라이선스
2. 일주 anchor date의 독립 검증 방식
3. 태양시 프로필을 출시할지와 공식·정확도 정책
4. 자시 일주 경계 대안 프로필의 명칭과 표시 방식
5. 대운 순역·기산 규칙 및 성별 데이터 처리 정책
6. 기준 사례집과 자동 회귀 테스트의 책임자·갱신 절차

---

## 15. Delivery Sequence

1. `kr_standard_v1`으로 연·월·일주 및 시간 확정 시 시주를 구현한다.
2. 고정 테이블과 기준 사례집을 versioned data asset으로 분리한다.
3. 지장간·십신·관계 데이터를 추가한다.
4. 대운 명세를 별도 검토·확정한 뒤 구현한다.
5. 이후 `true_solar_time` 및 자정 일주 경계 대안 프로필을 추가한다.

이 순서를 지키면 한국 MVP는 이해하기 쉬운 하나의 기본 결과를 제공하면서도, 후속 전통·해외 확장에 필요한 차이를 투명하게 수용할 수 있다.
