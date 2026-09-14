# Destiny — 사주 계산 스펙/구현 리뷰

> 검토 대상: `docs/03_BIRTH_PROFILE_SPEC.md` (v1.1), `docs/04_SAJU_CALCULATION_SPEC.md` (v0.1), `docs/05_CALCULATION_DATA_SOURCES.md` (v0.1), `tests/fixtures/saju/*`, 및 현재 구현 상태(`src/destiny_saju/hour_branch.py`, `data/saju/*.json`)
> 코드 변경 없음 — 리뷰 전용 문서
> 작성일: 2026-09-14

---

## 0. 검토 범위 요약

3개 스펙 문서와 fixture 폴더, 그리고 현재 유일하게 구현된 모듈(`hour_branch.py`)과 데이터 파일 2종(`core_tables_v1.json`, `day_pillar_anchor_candidates_v1.json`)을 함께 대조했다. 스펙 자체의 원칙(계산/해석 분리, unknown 보존, 재현 가능성)은 명확하고 일관성이 높다. 다만 "원칙 문서"와 "구현 가능한 규칙" 사이에는 아직 간극이 있고, 문서 간 교차 참조에서 몇 가지 실제 충돌이 발견됐다.

---

## 1. 구현 관점에서 빠진 규칙

### 1.1 월간(月干)·시간(時干) 생성 테이블이 존재하지 않음 — 핵심 기능 공백
`04_SAJU_CALCULATION_SPEC.md` §7.3, §7.5는 "월간은 연간과 월지의 관계를 이용해 고정 공식 또는 검증 테이블로 산출", "시간간은 일간과 시지의 관계 테이블로 정한다"고만 서술한다. 그러나 `data/saju/core_tables_v1.json`에는 월지→절기 매핑과 시지→시간대만 있고, 실제 오호둔(五虎遁, 연간→월두법)이나 오서둔(五鼠遁, 일간→시두법) 테이블/공식이 어디에도 없다. 현재 상태로는 지지(년/월/일/시)까지만 계산 가능하고 천간의 절반(월간·시간)은 계산 불가능하다. MVP 출시 전 반드시 추가해야 할 데이터/규칙.

### 1.2 십신(十神) 산출 알고리즘 부재
§6.2는 "십신은 일간을 기준으로 산출"이라고 원칙만 제시하고, 오행 생극(상생/상극) 관계에서 10개 십신 명칭(비견·겁재·식신·상관·편재·정재·편관·정관·편인·정인)을 도출하는 규칙표가 없다. 오행 상생상극 순환 테이블 자체도 `core_tables_v1.json`에 없다(각 stem에 `element`만 있고 生剋 관계는 별도 정의되지 않음).

### 1.3 지장간(藏干) 테이블 부재
§8.1에서 "지장간은 versioned lookup table에서 가져온다"고 하지만 그런 테이블이 레포에 없다. 여기/중기/정기 구분과 (있다면) 절입 이후 경과일에 따른 비중까지 포함할지 여부도 스펙에 없다.

### 1.4 합·충·형·파·해 탐지 알고리즘의 구체 규칙 미정
§8.2는 예시 JSON만 보여주고, 실제로 "어떤 조합이 관계로 인정되는가"의 판정 규칙(예: 삼합은 3개 지지가 모두 있어야 하는지, 2개만 있어도 반합으로 인정하는지, 한 지지가 여러 관계에 동시에 참여할 때 전부 보고하는지)이 없다. 이건 해석이 아니라 "발견"의 문제이므로 계산 엔진 책임인데 규칙이 없다.

### 1.5 대운 기산일수→나이 환산 공식 부재
§9.2는 필요한 결정 항목 리스트만 나열("일수와 시작 연령의 환산 방식" 등)하고 `defer_until_v1`로 명시적으로 미룬 상태다. 구현 관점에서는 "빠진 것"이라기보다 "의도적으로 열어둔 것"이지만, `02_KOREA_MVP_SCOPE.md` §2에서는 대운·세운을 Korea MVP V1 핵심 서비스에 포함시키고 있어 실제로는 출시 전 반드시 채워야 하는 공백이다(§3의 충돌 항목 참조).

### 1.6 후보(candidate) 폭발 제어 규칙 없음
윤달 unknown + 출생시간 unknown + DST ambiguous local time이 동시에 발생할 수 있는데, 이런 축(axis)들이 몇 개까지 동시에 존재할 수 있고 어떻게 조합(교차곱 vs 개별 목록)해서 `candidates` 배열을 구성할지, 그리고 candidate 개수 상한이나 사용자 노출 정책이 스펙에 없다.

### 1.7 통합 에러/경고 코드 레지스트리 없음
`03_BIRTH_PROFILE_SPEC.md` §27과 `04_SAJU_CALCULATION_SPEC.md` §12가 각자 다른 에러 코드 집합을 정의한다(예: `04`의 `MISSING_REQUIRED_TIME_BASIS`, `SOLAR_TERM_DATA_UNAVAILABLE`, `DAY_PILLAR_ANCHOR_UNAVAILABLE`, `DAEWOON_RULE_NOT_CONFIGURED`는 `03`에 없음; `03`의 `LOCATION_NOT_FOUND`, `TIMEZONE_NOT_FOUND` 등은 `04`에 없음). BirthProfile 계층과 Saju 계산 계층을 아우르는 단일 코드 레지스트리(파일/enum)가 없어 계층 간 에러 전파 규칙이 불명확하다.

### 1.8 `candidates` 원소의 스키마 미정의
`SajuResult`의 `"candidates": []`가 어떤 객체 형태를 가지는지(연/월/일/시 중 어느 필드가 후보별로 달라지는지, 각 candidate에도 자체 `warnings`/`provenance`가 있는지) 예시가 없다.

### 1.9 버전 증가 정책 미정의
§13은 "규칙이 바뀌면 재계산 표시"라고만 하고, dataset version / calculation profile version / engine version 중 무엇을 언제 올려야 하는지(semver 규칙, 호환성 매트릭스)는 정의돼 있지 않다.

---

## 2. 모호하거나 충돌할 수 있는 부분

### 2.1 ⚠️ 실제 데이터 충돌: stem/branch id 네임스페이스 충돌
`data/saju/core_tables_v1.json`을 직접 확인한 결과, **천간 "신"(辛, 금)의 id가 `"sin"`이고, 지지 "신"(申, 원숭이, 금)의 id도 `"sin"`이다.** 두 테이블을 분리된 dict로 유지하면 문제없지만, 코드에서 stem/branch를 하나의 이름 공간(단일 dict, 단일 enum)으로 합쳐 조회하면 조용히 잘못된 값을 반환할 위험이 있다. **출시 전 필수 수정 대상**이며, 아래 4장 코드 구조 제안에서 이를 원천 차단하는 타입 설계를 제시한다.

### 2.2 ⚠️ 문서 간 충돌: 대운/세운의 MVP 포함 여부
`docs/02_KOREA_MVP_SCOPE.md` §2는 "대운, 세운"을 Korea MVP V1 핵심 서비스 목록에 명시한다. 반면 `docs/04_SAJU_CALCULATION_SPEC.md` §5, §9.2는 `daewoon_direction_rule`/`daewoon_start_rule`을 `"defer_until_v1"`로 명시적으로 유보한다. 즉 제품 스코프 문서와 계산 스펙 문서가 서로 다른 약속을 하고 있다. 세운(연간 사이클)은 §9.1에 계산 규칙이 있어 구현 가능하지만, 대운(시작 연령 포함)은 구현 불가능한 상태다. **출시 커뮤니케이션 전에 반드시 조율 필요** — 대운을 MVP에서 뺄지, 04의 유보를 풀지 결정해야 한다.

### 2.3 일주 계산 기준(자정)과 anchor 기준(정오 JDN)의 변환 규칙 모호
`kr_standard_v1`의 `day_boundary`는 자정(00:00)이지만, day pillar anchor는 `civil_time_basis: local_civil_date_at_noon`(정오 기준 JDN)을 쓴다. `05_CALCULATION_DATA_SOURCES.md` §2.3은 "혼동되지 않도록 명시한다"고만 하고 실제 변환 규칙(예: 로컬 민간일의 날짜를 그대로 그 날 정오의 JDN에 매핑하면 되는지, 혹은 별도 보정이 필요한지)을 제공하지 않는다. 구현자가 임의로 해석할 여지가 있다.

### 2.4 `zi_hour_policy`가 `kr_standard_v1`에서 실제로 무엇을 하는지 불명확
프로필에 `zi_hour_policy: "same_civil_day"`가 있고 `day_boundary: "midnight"`도 별도로 있다. 이미 자정 기준으로 일주가 정해지는데 `zi_hour_policy`가 추가로 관여하는 계산이 무엇인지(현재는 no-op처럼 보임, 향후 대안 프로필에서만 의미가 생기는 필드인지) 스펙에 명시가 없다. `hour_branch.py`의 docstring도 "day-boundary는 여기서 결정하지 않는다"고만 하고 어느 모듈이 실제로 결정하는지 연결점이 없다.

### 2.5 "계산 기준 시각"이 모든 주(pillar)에서 동일한 시간 기준을 가리키는지 불명확
§7.2(연주), §7.3(월주), §7.5(시주)가 각각 "출생 계산 기준 시각"이라는 표현을 반복 사용하는데, 이것이 매번 Calculation Profile의 `time_basis`(현재 `legal_local_time`)로 고정된 동일한 값을 가리키는 것인지, 혹은 연/월주는 다른 시간 기준을 쓸 수 있는 여지가 있는지 명시적으로 재확인되지 않는다.

### 2.6 상태(status) 어휘가 3곳에서 서로 다름
- `tests/fixtures/saju/README.md`의 카테고리 테이블: "데이터 출처 확정 대기", "준비 가능" 등 한국어 프로즈
- 실제 fixture JSON의 `status` 필드: `"ready"`, `"pending_independent_verification"`
- `day_pillar_anchor_candidates_v1.json`의 `verification_status` 필드: `"single_source_only"`

세 어휘 체계가 1:1로 매핑되지 않는다. 자동화(예: "ready가 아닌 fixture는 CI에서 스킵")를 만들려면 하나의 canonical enum으로 수렴시켜야 한다.

### 2.7 `resolved_time_set.resolution_status`의 전체 값 집합 미정의
예시에는 `"resolved"`만 나오는데, `AMBIGUOUS_LOCAL_TIME`/`HISTORICAL_TIMEZONE_UNCERTAIN` 같은 에러 코드가 존재하는 걸 보면 `"ambiguous"`, `"failed"`, `"historical_uncertain"` 등의 상태도 있어야 할 것 같다. 이 필드의 enum이 명시되지 않아 Saju 엔진이 `resolution_status`를 보고 분기해야 하는 로직을 스펙만으로는 구현할 수 없다.

### 2.8 README.md 인코딩 손상
저장소 최상위 `README.md`가 인코딩이 깨져 있다(한글이 mojibake로 표시됨). 내용상 문제는 아니지만 리뷰 중 발견된 사항이라 기록한다.

---

## 3. 권장 코드 구조 (Python 기준)

현재 `pyproject.toml`은 `destiny-saju` 패키지(Python ≥3.11, `StrEnum` 사용 확인됨)를 정의하고 있으므로 이를 기준으로 제안한다.

```
src/destiny_saju/
  core/
    stems.py          # HeavenlyStem enum — StemId만 다루는 별도 타입
    branches.py        # EarthlyBranch enum — BranchId만 다루는 별도 타입 (2.1 문제 원천 차단)
    tables.py           # core_tables_v1.json 로더 → 위 enum에 매핑, dataset_version 검증
  profile/
    calculation_profile.py   # CalculationProfile 모델(불변, profile_id로 식별), kr_standard_v1.json 로더
    birth_profile.py          # BirthProfile/RawBirthInput 데이터 모델 (03 스펙 6장 구조)
  time_resolution/
    resolved_time.py    # ResolvedTimeSet 모델 (04 §4.1 계약과 동일한 필드) — 실제 시간대/DST 계산은 별도 엔진(범위 밖)이므로 여기는 계약(인터페이스)만
  pillars/
    year_pillar.py
    month_pillar.py     # 절입 경계 + 오호둔 테이블 필요 (1.1)
    day_pillar.py         # JDN 기반 60갑자 순환; anchor 로더는 status=="production_verified" 데이터만 허용
    hour_branch.py        # 기존 구현 유지
    hour_stem.py           # 오서둔 테이블 필요 (1.1)
  derived/
    elements.py
    ten_gods.py           # 오행 생극 테이블 + 십신 산출 (1.2)
    hidden_stems.py        # 지장간 테이블 (1.3)
    relations.py            # 합충형파해 탐지 (1.4)
  fortune_cycles/
    seun.py
    daewoon.py              # v1에서는 DAEWOON_RULE_NOT_CONFIGURED 반환만 구현 (04 §15 순서 준수)
  result/
    saju_result.py           # SajuResult 모델, status enum, candidates 스키마 명시 (1.8)
  validation/
    errors.py                  # 03+04 통합 에러/경고 코드 레지스트리 (1.7)
  data_registry.py            # 모든 versioned JSON 데이터셋의 단일 로드/검증 지점; status가 not_for_production/pending_verification인 데이터셋은 프로덕션 경로에서 로드 자체를 거부
  engine.py                     # BirthProfile + ResolvedTimeSet + CalculationProfile + EngineVersion → SajuResult 오케스트레이션
```

핵심 설계 원칙 제안:

1. **stem/branch 타입 분리**: `HeavenlyStem`과 `EarthlyBranch`를 서로 다른 `StrEnum`(또는 `NewType`)으로 만들어 "sin" 충돌이 타입 시스템에서 원천적으로 불가능하게 한다. 두 값을 같은 dict/enum에 섞지 않는다.
2. **불변 값 객체**: `CalculationProfile`, `SajuResult`, `ResolvedTimeSet` 등은 `frozen=True` dataclass 또는 pydantic 모델로 — 계산 도중 어디서도 수정되지 않아야 한다는 스펙 원칙(§3 Immutable Principles)을 타입으로 강제.
3. **데이터셋 상태 게이트**: `data_registry.py`가 모든 JSON 자산을 로드할 때 `status`/`verification_status` 필드를 검사해서, `not_for_production`/`pending_verification`/`pending_independent_verification` 상태인 데이터는 프로덕션 엔진 경로에서 예외를 던지고 테스트 전용 경로에서만 허용한다. 이렇게 하면 `day_pillar_anchor_candidates_v1.json` 같은 미검증 데이터가 실수로 프로덕션에 흘러들어가는 걸 코드 레벨에서 막는다.
4. **provenance 자동 생성**: 각 pillar 모듈이 개별적으로 `provenance` 필드를 채우지 말고, `data_registry`가 로드한 데이터셋의 `dataset_id`/`version`을 자동 수집해 `engine.py`가 최종 `SajuResult.provenance`를 조립한다(수기 기입으로 인한 버전 drift 방지, 1.9 관련).
5. **순수 함수 우선**: `hour_branch_for_time`처럼 부작용 없는 순수 함수 스타일을 다른 pillar 모듈에도 동일하게 적용해 property-based 테스트가 쉬워지도록 한다.

---

## 4. 자동 테스트 계획

### 4.1 단위/경계 테스트 (기존 `test_hour_branch.py` 패턴 확장)
- 연주: 입춘 순간 직전(−1s)/정각/직후(+1s) 3케이스 × 여러 연도
- 월주: 12절입 각각 직전/정각/직후 (§11 요구사항 그대로)
- 일주: JDN 모듈러 순환의 순수 수학적 정합성(anchor 값과 무관하게 60일 주기 및 index%10/index%12 매핑이 항상 일관되는지) — property-based(hypothesis)로 임의의 anchor_index/offset에 대해 검증
- 시지: 기존 테스트를 24시간 전체 슬롯에 대해 빠짐/겹침 없이 커버하는지로 확장(현재는 표본 케이스만 체크)
- 시간: 오서둔 테이블 추가 후 일간×시지 전체 조합(10×12=120) 커버리지 테스트

### 4.2 데이터 무결성 테스트 (`core_tables_v1.json` 등)
- 천간 10개/지지 12개 id가 서로 다른 네임스페이스에서도 **전체적으로 유일**한지 검사(2.1 재발 방지 회귀 테스트)
- 시지 24시간 윈도우가 gap/overlap 없이 24시간을 정확히 커버하는지
- 월지-절기 매핑이 12절기 전부에 대해 1:1 전단사인지
- 신규 데이터셋 추가 시 `schema_version`/`dataset_id`/`status` 필수 필드 존재 검사(간단한 JSON Schema lint)

### 4.3 계약(schema) 테스트
- 모든 fixture 기반 테스트 실행 시 엔진 출력이 `SajuResult` JSON Schema(2.7/1.8에서 확정할 스키마)를 항상 만족하는지 검증
- `status` enum(`complete/partial/ambiguous/blocked/invalid`)과 `warnings` 코드가 실제 통합 레지스트리(1.7)에 정의된 값만 사용하는지 검증

### 4.4 Fixture 기반 회귀 테스트
- `tests/fixtures/saju/*.json`을 로더가 읽어 `status` 필드로 파라미터화(pytest `parametrize`)
- `status != "ready"`(또는 승격된 상태)인 fixture는 프로덕션 assertion에서 자동 스킵/xfail 처리하고, "아직 몇 개 pending인지"를 리포트하는 별도 체크(예: `pytest --collect-only` 요약 또는 CI 단계)를 둔다 — README의 "First implementation gate"를 자동으로 강제
- 새 fixture 추가 시 `case_id`, `status`, `evidence`(또는 `evidence_ref`) 필드 존재를 검사하는 lint 스크립트

### 4.5 통합/일관성 테스트
- 동일 BirthProfile + ResolvedTimeSet을 서로 다른 두 CalculationProfile로 실행해 의도적으로 다른 결과가 나오는지(§11 요구사항)
- 결정론성(determinism) 테스트: 동일 입력을 N회 반복 실행해 완전히 동일한 출력(딕셔너리 순서까지 포함해 직렬화 결과)이 나오는지
- 음력/윤달 unknown, 출생시간 unknown, DST ambiguous 케이스별 "부분 계산" 결과(§28 disclosure)가 실제로 어떤 필드를 `null`/제외 처리하는지, 그리고 그 사유가 `warnings`에 정확히 기록되는지
- 최종 anchor 승격 후: anchor 전후 60일 연속성을 독립 출처와 자동 대조하는 회귀 스위트(§11의 "기준일 전후 60일" 요구사항)

### 4.6 부정 경로(negative path) 테스트
- 존재하지 않는 날짜(2월 30일), 유효하지 않은 음력 날짜, 알 수 없는 timezone, ambiguous local time, 필수 필드 누락 등에서 정확한 에러 코드가 발생하는지 — 그리고 **어떤 경우에도 시간/분/장소가 임의 기본값(00:00, 정오, 현재 위치)으로 대체되지 않는지**를 명시적으로 assert하는 회귀 테스트(스펙의 핵심 원칙이므로 코드 레벨 가드레일 필요)

### 4.7 CI 구성 제안
- 현재 `pyproject.toml`에 테스트 러너/린터 설정이 없음 — `pytest`, `hypothesis`, `jsonschema`(또는 `pydantic`)를 dev dependency로 추가하고 `ruff`/`mypy` 같은 정적 검사 도입 권장
- "not_for_production" 데이터셋이 프로덕션 코드 경로에서 import되지 않는지 검사하는 정적 체크(예: `data_registry` 외부에서 `data/saju/*.json`을 직접 여는 코드가 없는지 grep 기반 lint)

---

## 5. 출시 전 반드시 검증할 위험 항목

우선순위 순으로 정리했다.

1. **일주(日柱) anchor 미검증** — `day_pillar_anchor_candidates_v1.json`이 단일 출처(`ytliu0.github.io`)만으로 `single_source_only` 상태이며 데이터셋 자체가 `"not_for_production"`으로 표시돼 있다. 모든 사주 계산이 일주에 의존하므로, 독립된 두 번째 출처 확인 + 전후 60일 회귀 세트 없이는 **출시 불가**.
2. **24절기(節氣) 데이터셋 부재** — 연주·월주 계산 자체가 이 데이터셋 없이는 완전히 블록된 상태(`SOLAR_TERM_DATA_UNAVAILABLE`). 천문 모델/에페머리스 소스 선정, 라이선스 확인, 지원 연도 범위(예: 1900–2100) 결정이 출시 전 필수.
3. **한국 역사적 표준시/DST 데이터 검증** — 한국은 1908~1961년 사이 UTC offset이 여러 번 바뀌었고(UTC+8:30 시기 포함), 1948–1960년 및 1987–1988년 DST 적용 이력이 있다. `05_CALCULATION_DATA_SOURCES.md`가 이미 "1988년 DST 사례"를 필수 통합 테스트로 지정했는데, 이 항목이 실제로 검증됐는지 확인 필요. 이 데이터가 틀리면 시주뿐 아니라 연/월주 경계 판정까지 잘못될 수 있다.
4. **월간/시간 생성 테이블 부재로 인한 기능 공백** (1.1) — 이 상태로는 "완전한 사주팔자"를 제공할 수 없다. `02_KOREA_MVP_SCOPE.md`가 사주팔자를 MVP 핵심으로 명시하므로, 출시 전 반드시 채워야 하는 최우선 구현 항목.
5. **stem/branch id 네임스페이스 충돌** (2.1) — 코드에 반영되기 전에 데이터/타입 설계로 반드시 수정. 조용히 틀린 결과를 낼 수 있는 가장 위험한 유형의 버그(예외 없이 잘못된 값 반환).
6. **대운 스코프 문서 충돌** (2.2) — 제품 스코프(`02`)와 계산 스펙(`04`)이 대운의 MVP 포함 여부에서 불일치. 출시 마케팅/기능 목록과 실제 계산 가능 여부가 어긋나면 사용자 신뢰 문제로 이어질 수 있어 조기에 조율 필요.
7. **십신·지장간·관계(합충형파해) 규칙 부재** (1.2–1.4) — `02_KOREA_MVP_SCOPE.md`가 이 모두를 MVP 핵심 서비스로 명시하고 있으나 계산 규칙 자체가 스펙에 없다. 규칙 확정과 데이터 구축이 출시 일정의 실질적 병목이 될 가능성이 높다.
8. **재현성 보증의 실제 구현 여부** — 에페머리스/천문 라이브러리 버전이 올라가면서 절입 순간이 초 단위로 미세하게 바뀌면 경계 부근 결과가 조용히 달라질 수 있다. 라이브러리 버전 고정 정책과, 업그레이드 시 경계 케이스 재검증을 강제하는 프로세스가 필요.
9. **외부 데이터/코드 출처의 라이선스 확인** — `05` 문서가 `rath/orrery`를 "참고용으로만 사용, 프로덕션 의존성 아님"이라 명시했지만 이를 코드/CI에서 강제하는 장치가 없다. `ytliu0.github.io` 자료의 재사용 범위(데이터 자체를 파생 데이터셋에 포함해도 되는지)도 명확히 확인 필요.
10. **개인정보 처리 실제 검증** — `03` 스펙의 최소수집·"외부 LLM에 불필요한 개인정보 전송 금지" 원칙(§29)이 실제 RAG/LLM 연동 코드에서 지켜지는지(원본 출생지·이름이 외부 LLM 프롬프트에 그대로 들어가지 않는지) 출생 데이터라는 민감한 입력의 특성상 출시 전 별도 데이터 흐름 감사가 필요.
11. **README 인코딩 손상** — 사소하지만 공개 저장소로 전환하거나 신규 기여자를 받기 전에 수정 권장.

---

## 부록: 참고한 파일 목록
- `docs/03_BIRTH_PROFILE_SPEC.md`
- `docs/04_SAJU_CALCULATION_SPEC.md`
- `docs/05_CALCULATION_DATA_SOURCES.md`
- `docs/02_KOREA_MVP_SCOPE.md` (스코프 충돌 확인용 교차 참조)
- `tests/fixtures/saju/README.md`, `hour-boundary-001.json`, `day-anchor-2019-01-27-candidate.json`
- `tests/test_hour_branch.py`
- `src/destiny_saju/hour_branch.py`
- `data/saju/core_tables_v1.json`, `data/saju/day_pillar_anchor_candidates_v1.json`
- `pyproject.toml`, `README.md`
