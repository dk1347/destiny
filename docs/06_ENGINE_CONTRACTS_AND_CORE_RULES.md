# Destiny — Engine Contracts and Core Rules

> Version: 0.1  
> Phase: Core Calculation Engine  
> Status: Draft for Architecture Review  
> Depends on: `03_BIRTH_PROFILE_SPEC.md`, `04_SAJU_CALCULATION_SPEC.md`, `05_CALCULATION_DATA_SOURCES.md`  
> Incorporates: `docs/reviews/CLAUDE_IMPLEMENTATION_REVIEW_v1.md`

---

## 1. Purpose and precedence

이 문서는 기존 계산 명세에서 구현 규칙으로 충분히 고정되지 않았던 항목을 정한다. 목적은 해석 규칙을 늘리는 것이 아니라, 동일 입력이 언제나 같은 구조화된 계산 결과를 내도록 하는 것이다.

문서의 우선순위는 다음과 같다.

1. `03_BIRTH_PROFILE_SPEC.md`: 원본 입력, 시간 복원, unknown 보존
2. `04_SAJU_CALCULATION_SPEC.md`: 원국 계산 범위와 Calculation Profile
3. **본 문서**: 원국의 세부 계산 규칙과 공통 결과 계약
4. 버전 데이터셋: 본 문서에서 정의한 lookup table의 값

규칙과 해석은 분리한다. 예를 들어 합·충의 존재는 계산 결과이나 길흉, 강약, 우선순위는 Interpretation Rule Layer의 책임이다.

---

## 2. Canonical identifiers and data boundaries

천간과 지지는 서로 다른 타입과 이름공간이다. 한글 “신”에 대응하는 천간 `stem:sin`(辛)과 지지 `branch:sin`(申)은 같은 ID가 아니다.

```text
StemId   = gap | eul | byeong | jeong | mu | gi | gyeong | sin | im | gye
BranchId = ja | chuk | in | myo | jin | sa | o | mi | sin | yu | sul | hae
```

- 모든 코드 모델은 `HeavenlyStem`과 `EarthlyBranch`를 별도 타입/enum으로 둔다.
- ID의 유일성은 각 타입 안에서 검사한다. 타입을 넘는 전역 유일성을 요구하지 않는다.
- 로그·관계 데이터·외부 키에는 `stem:` 또는 `branch:` 접두어를 붙인다.
- `core_tables_v1.json`은 어휘 데이터다. 아래 계산 규칙은 별도 버전 데이터셋으로 추가한다.

---

## 3. Pillar stem rules

### 3.1 Month stem — Five Tigers Escape (오호둔)

월지는 절입으로 이미 결정되어 있어야 한다. 연간별 인월(寅月)의 월간 시작값은 다음과 같다.

| Year stem group | 寅月 month stem |
|---|---|
| 갑·기 | 병 |
| 을·경 | 무 |
| 병·신 | 경 |
| 정·임 | 임 |
| 무·계 | 갑 |

월간은 인월을 offset `0`으로 하여 월지 순서 `인→묘→…→축`만큼 천간을 순환시킨다.

```text
month_stem_index = modulo(tiger_start_stem_index(year_stem) + month_branch_offset_from_in, 10)
```

이 규칙은 `month_stem_rules_v1` 데이터셋으로 제공한다. 절입 순간은 이 규칙이 아니라 Solar-term dataset이 결정한다.

### 3.2 Hour stem — Five Rats Escape (오서둔)

시지는 법정 현지시와 Calculation Profile로 먼저 결정한다. 일간별 자시(子時)의 시간 시작값은 다음과 같다.

| Day stem group | 子時 hour stem |
|---|---|
| 갑·기 | 갑 |
| 을·경 | 병 |
| 병·신 | 무 |
| 정·임 | 경 |
| 무·계 | 임 |

시간간은 자시를 offset `0`으로 하여 시지 순서 `자→축→…→해`만큼 천간을 순환시킨다.

```text
hour_stem_index = modulo(rat_start_stem_index(day_stem) + hour_branch_offset_from_ja, 10)
```

`kr_standard_v1`에서 `day_boundary: midnight`와 `zi_hour_policy: same_civil_day`는 자시에도 민간 날짜의 일간을 사용한다. 즉 이 프로필에서 `zi_hour_policy`는 23:00에 일주를 앞당기지 않는다는 명시적 정책이며, 별도 보정을 수행하지 않는다.

---

## 4. Day-pillar date/JDN mapping

일주 계산은 먼저 Calculation Profile의 시간 기준으로 **현지 민간 날짜**를 결정한 뒤 수행한다.

```text
chosen local datetime
  → local civil date (day boundary: 00:00)
  → Gregorian JDN for noon of that local civil date
  → anchor offset modulo 60
```

JDN의 정오 시작 관례는 날짜 번호를 정의하기 위한 것이며, 출생 순간을 UTC 정오로 변환하라는 뜻이 아니다. 같은 현지 민간 날짜에 속하는 모든 시각은 그 날짜의 정오 JDN에 대응한다.

`kr_standard_v1`에서는 다음을 적용한다.

- 00:00 이상은 새 민간 날짜의 일주를 사용한다.
- 23:00–23:59는 그 민간 날짜의 일주를 유지한다.
- UTC 날짜, JDN 정오 경계, 야자시 규칙을 서로 섞어 날짜를 한 번 더 보정하지 않는다.

production anchor는 `05_CALCULATION_DATA_SOURCES.md`의 검증 게이트를 모두 통과한 데이터셋만 사용할 수 있다.

---

## 5. Derived-fact rules

### 5.1 Five-element relations

오행의 방향은 다음으로 고정한다.

```text
생(creates): wood → fire → earth → metal → water → wood
극(controls): wood → earth → water → fire → metal → wood
```

### 5.2 Ten Gods (십신)

십신은 일간과 대상 **천간**의 오행 관계 및 음양 일치 여부로만 산출한다. 지지 자체의 십신을 임의로 만들지 않으며, 지장간에는 각 지장간 천간을 대상으로 별도 계산한다.

| Day-master relation to target | Polarity same | Polarity different |
|---|---|---|
| 같은 오행 | 비견 | 겁재 |
| 일간이 대상을 생함 | 식신 | 상관 |
| 일간이 대상을 극함 | 편재 | 정재 |
| 대상이 일간을 극함 | 편관 | 정관 |
| 대상이 일간을 생함 | 편인 | 정인 |

결과 원소는 다음 형식을 사용한다.

```json
{
  "target": "stem:gyeong",
  "source": "month_stem",
  "relation_element": "controls_day_master",
  "polarity_match": true,
  "ten_god": "pyeongwan"
}
```

표시명은 별도 locale 테이블에서 `pyeongwan → 편관`으로 렌더링한다.

### 5.3 Hidden stems (지장간)

`hidden_stems_v1`은 강약·가중치를 포함하지 않는 원국 사실 데이터다. `role`은 `main`, `middle`, `residual`만 사용한다.

| Branch | Hidden stems in role order |
|---|---|
| 자 | 계(main) |
| 축 | 기(main), 계(middle), 신(residual) |
| 인 | 갑(main), 병(middle), 무(residual) |
| 묘 | 을(main) |
| 진 | 무(main), 을(middle), 계(residual) |
| 사 | 병(main), 경(middle), 무(residual) |
| 오 | 정(main), 기(middle) |
| 미 | 기(main), 정(middle), 을(residual) |
| 신 | 경(main), 임(middle), 무(residual) |
| 유 | 신(main) |
| 술 | 무(main), 신(middle), 정(residual) |
| 해 | 임(main), 갑(middle) |

이 표의 항목에는 `stem_id`, `role`, `display_order`를 저장한다. 가중치, 투간, 계절 강약은 본 데이터셋에 넣지 않는다.

### 5.4 Relations (합·충·형·파·해)

관계 엔진은 원국의 간·지 조합을 발견해 반환한다. 각 원소는 `relation_id`, `relation_type`, `participants`, `values`, `rule_set_version`을 가진다.

- 천간합, 지지 육합·충·형·파·해는 원자 관계표로 버전 관리한다.
- 삼합은 세 지지가 모두 존재할 때만 `three_harmony`로 반환한다.
- 두 지지만 존재하는 경우는 `half_three_harmony_candidate`로 별도 반환하며, 완성된 삼합으로 취급하지 않는다.
- 한 간지 쌍이 여러 관계에 참여해도 모든 사실 관계를 반환한다. 해석 계층이 우선순위를 정한다.
- 동일 지지의 자형은 서로 다른 pillar 위치에 같은 지지가 둘 이상 있을 때만 검사한다.

정확한 조합값은 `relations_v1` 데이터셋에 두며, 엔진에 하드코딩하지 않는다.

---

## 6. Result, candidate, and status contract

### 6.1 Resolved Time Set status

`resolution_status`의 canonical 값은 다음과 같다.

```text
resolved                 하나의 계산 기준 시각이 확정됨
ambiguous                둘 이상의 유효한 계산 기준 시각이 존재함
partial                  일부 시간 기준만 계산 가능함
historical_uncertain     역사 시간대 정보를 확정할 수 없음
failed                   시간 복원 실패
```

Calculation Profile이 요구하는 시간 기준이 없으면 사주 엔진은 추정하지 않고 `blocked` 결과를 낸다.

### 6.2 Candidate model and explosion control

날짜·시간 후보는 하나의 교차곱 후보 집합으로 계산한다. 각 후보는 독립적으로 완전한 원국 사실과 provenance를 가진다.

```json
{
  "candidate_id": "candidate-001",
  "input_variant": {
    "calendar_date": "1990-06-02",
    "resolved_time_reference": "resolved-time-set-001"
  },
  "pillars": {"year": {}, "month": {}, "day": {}, "hour": {}},
  "derived": {},
  "warnings": [],
  "provenance": {}
}
```

- 후보 수는 기본 상한 `16`이다.
- 상한을 넘으면 후보를 임의로 버리지 않는다. 결과는 `blocked`이고 `CANDIDATE_LIMIT_EXCEEDED`를 반환한다.
- 후보가 둘 이상이면 상위 결과 `status`는 `ambiguous`다. 후보별로 계산이 일부만 가능하면 각 후보의 `status`를 기록한다.
- 출생시간 unknown은 후보를 만들지 않는다. 연·월·일주 계산이 가능하면 상위 결과는 `partial`이며 시주는 `null`이다.

### 6.3 Overall status

```text
complete   요청된 원국 항목이 하나의 확정 결과로 계산됨
partial    확정 결과는 있으나 일부 항목을 계산하지 못함
ambiguous  둘 이상의 유효 후보 결과가 있음
blocked    유효한 결과를 만들 필수 데이터/규칙이 없음
invalid    입력 자체가 유효하지 않음
```

`invalid`는 입력 검증 실패에만 사용한다. 데이터셋 미검증, 시간 기준 부재, 대운 규칙 미설정은 `blocked`다.

---

## 7. Unified diagnostic registry

코드와 fixture는 아래의 canonical 코드를 사용한다. UI 문구는 코드와 분리한다.

| Code | Meaning | Default severity |
|---|---|---|
| `INVALID_DATE` | 유효하지 않은 양력 날짜 | error |
| `INVALID_TIME` | 유효하지 않은 시각 | error |
| `INVALID_LUNAR_DATE` | 유효하지 않은 음력 날짜 | error |
| `INVALID_LEAP_MONTH` | 윤달 지정이 유효하지 않음 | error |
| `AMBIGUOUS_LEAP_MONTH` | 윤달 여부로 날짜 후보가 복수임 | warning |
| `UNKNOWN_BIRTH_TIME` | 출생시간이 없음 | warning |
| `UNKNOWN_LOCATION` | 출생지가 없음 | warning |
| `LOCATION_NOT_FOUND` | 출생지 해석 실패 | error |
| `TIMEZONE_NOT_FOUND` | 시간대를 찾지 못함 | error |
| `AMBIGUOUS_LOCAL_TIME` | DST 등으로 현지 시각이 복수임 | warning |
| `HISTORICAL_TIMEZONE_UNCERTAIN` | 역사 시간대가 확정되지 않음 | warning |
| `CALENDAR_CONVERSION_FAILED` | 달력 변환 실패 | error |
| `MISSING_REQUIRED_TIME_BASIS` | 프로필이 요구하는 시간 기준 없음 | error |
| `SOLAR_TERM_DATA_UNAVAILABLE` | 절입 데이터가 없음 | error |
| `DAY_PILLAR_ANCHOR_UNAVAILABLE` | 검증된 일주 anchor가 없음 | error |
| `DAEWOON_RULE_NOT_CONFIGURED` | 대운 규칙이 아직 확정되지 않음 | warning |
| `CANDIDATE_LIMIT_EXCEEDED` | 후보 수가 안전 상한을 초과함 | error |
| `DATASET_NOT_PRODUCTION_VERIFIED` | 미검증 데이터셋이 production 경로에 요청됨 | error |

`errors.py` 또는 동등한 단일 registry가 이 목록의 소유자다. BirthProfile, Time Resolution, Saju Engine은 같은 코드를 재정의하지 않는다.

---

## 8. Dataset and version policy

모든 계산 데이터셋에는 최소한 다음을 둔다.

```text
schema_version, dataset_id, dataset_version, status, source, license, generated_at
```

`status`는 다음 enum으로 통일한다.

```text
draft | pending_verification | production_verified | deprecated
```

- `production_verified`만 production 계산 경로에서 로드할 수 있다.
- `draft`와 `pending_verification`은 fixture·개발 환경에서만 명시적으로 허용한다.
- 값·알고리즘·출처가 결과를 바꾸는 변경은 `dataset_version`의 major를 올린다.
- 결과 스키마의 호환되지 않는 변경은 `result_version`의 major를 올린다.
- 코드 구현만 바뀌어도 같은 입력 결과가 달라질 가능성이 있으면 `engine_version`을 올리고 경계 회귀 테스트를 재실행한다.

---

## 9. Fortune-cycle scope decision

`kr_standard_v1`에서 대운의 순역·기산 규칙은 아직 확정되지 않았다. 따라서 Core Calculation Engine V1은 원국·세운의 기반 계산에 집중하고, 대운 요청에는 계산값을 추정하지 않는다.

```json
{
  "daewoon": null,
  "warnings": ["DAEWOON_RULE_NOT_CONFIGURED"]
}
```

대운을 Korea MVP 공개 기능으로 포함하려면, 별도 `daewoon_rules_v1`과 성별 규칙, 순역 판정, 절입 기준, 기산 환산 규칙, 경계 fixture를 승인한 뒤에만 이 정책을 해제한다. 이에 맞춰 `02_KOREA_MVP_SCOPE.md`의 기능 목록은 다음 제품 스코프 정리에서 갱신한다.

---

## 10. Implementation gate

다음 순서 전에는 완전한 원국 결과를 production에 제공하지 않는다.

1. `month_stem_rules_v1`, `hour_stem_rules_v1`, `hidden_stems_v1`, `relations_v1`, `ten_gods_v1` 데이터셋과 schema lint 작성
2. 일주 anchor와 24절기 데이터셋을 `production_verified`로 승격
3. 입춘·12절입·00:00·23:00·DST·unknown 입력의 fixture 회귀 테스트 통과
4. 동일 입력의 결정론성 및 provenance 기록 테스트 통과
5. 한국 MVP 지원 연도 범위와 라이선스 기록 확정

