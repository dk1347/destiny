# Destiny — Core Engine Implementation Review (670dd45)

> 대상 커밋: `670dd45` "Implement core Saju rule modules and datasets"
> 검토 범위: `src/destiny_saju/*`, `data/saju/*_rules_v1.json`, `data/saju/hidden_stems_v1.json`, `data/saju/ten_gods_v1.json`, `tests/*`, `pyproject.toml`
> 대조 문서: `docs/06_ENGINE_CONTRACTS_AND_CORE_RULES.md`, `docs/07_VERSIONED_RULE_DATA_SPEC.md`
> 검토 방식: 코드 수기 대조 + 로컬에서 `pip install -e .` 및 `pytest` 실제 실행으로 재현 확인 (코드는 수정하지 않음)
> 작성일: 2026-09-15

---

## 요약

| 구분 | 개수 |
|---|---|
| Critical | 4 |
| Major | 9 |
| Minor | 5 |
| Suggestion | 4 |

가장 중요한 결론부터: **오호둔·오서둔·십신·지장간 계산 값과 공식 자체에는 오류를 찾지 못했다.** 표 값, offset 공식, 오행 상생상극 방향, 십신 델타 매핑을 `docs/06`과 하나씩 대조했고 모두 일치한다. 문제의 중심은 계산 결과가 아니라 **아키텍처(데이터셋 미사용)와 안전장치(production 게이트 우회)와 테스트의 실효성**이다.

---

## 1. docs/06, docs/07 명세와 구현 일치 여부

**[Critical]** `month_stem.py`, `hour_stem.py`, `ten_gods.py` 세 모듈 모두 `docs/07_VERSIONED_RULE_DATA_SPEC.md`가 정의한 "규칙은 versioned JSON 데이터셋으로 관리하고 엔진이 이를 로드한다"는 아키텍처를 따르지 않는다. `data/saju/month_stem_rules_v1.json`, `hour_stem_rules_v1.json`, `ten_gods_v1.json`이 이번 커밋에서 함께 추가됐지만, 이 세 모듈 중 어느 것도 `data_registry.load_dataset()`을 호출하지 않는다. 대신 완전히 동일한 표를 Python 딕셔너리로 다시 타이핑해 하드코딩했다(`month_stem.py`의 `_IN_MONTH_START`, `hour_stem.py`의 `_START`, `ten_gods.py`의 `_TEN_GODS`). 결과적으로 세 JSON 데이터셋은 지금 시점에는 코드에서 전혀 소비되지 않는 죽은 파일이며, 코드와 데이터라는 두 개의 독립된 진실 소스(source of truth)가 생겼다 — 둘 중 하나만 수정되면 조용히 어긋난다. `docs/07` §1이 "이 규칙들을 데이터로 옮긴다"고 명시한 목적 자체가 아직 달성되지 않았다.

**[Critical]** 위 문제의 직접적 결과로, `docs/06` §7·§8과 `docs/07` §3이 요구하는 "production 경로는 `status: production_verified` 데이터셋만 로드하고, 아니면 `DATASET_NOT_PRODUCTION_VERIFIED`로 차단한다"는 안전장치가 월간·시간·십신 계산에는 **아예 존재하지 않는다**(§4에서 상세).

**[Major]** `docs/06` §7이 요구하는 "코드와 fixture가 공유하는 단일 진단 코드 registry(`errors.py` 등)"가 구현되어 있지 않다. 현재 코드베이스 전체에서 진단 코드가 등장하는 곳은 `data_registry.py` 안에 raw 문자열로 박힌 `"DATASET_NOT_PRODUCTION_VERIFIED"` 하나뿐이고, `INVALID_DATE`, `UNKNOWN_BIRTH_TIME` 등 `docs/06` §7의 나머지 코드는 코드베이스 어디에도 상수로 존재하지 않는다.

**[Major]** `docs/06` §2는 "모든 코드 모델은 `HeavenlyStem`과 `EarthlyBranch`를 별도 타입으로 둔다"고 명시하지만, 실제 지지 타입 이름은 여전히 `HourBranch`(`hour_branch.py`)다. 이 타입이 `hidden_stems_for(branch: HourBranch)`, `hour_stem_for(..., branch: HourBranch)`처럼 "시간"과 무관한 문맥(지장간 조회 등 모든 지지 12개 전체를 대표하는 자리)에서도 재사용되고 있어, 타입 이름과 실제 역할이 어긋난다. 기능적 오류는 아니지만 문서 용어와 코드 용어가 불일치한다.

**[Minor]** 4개 데이터셋(`month_stem_rules_v1`, `hour_stem_rules_v1`, `ten_gods_v1`, `hidden_stems_v1`) 모두 `status: "pending_verification"`으로 정확히 등록되어 있고 내용도 `docs/06` 표와 정확히 일치한다(양호). 다만 앞서 지적한 대로 실제로 로더를 거쳐 소비되는 것은 `hidden_stems_v1` 하나뿐이라, 나머지 세 데이터셋의 상태 표기는 지금은 장식에 가깝다.

---

## 2. 오호둔·오서둔·십신·지장간 계산 오류

계산 로직 자체를 `docs/06` §3.1(오호둔), §3.2(오서둔), §5.1(오행 생극), §5.2(십신), §5.3(지장간) 표와 하나씩 수기로 대조한 결과는 다음과 같다.

- 오호둔 `_IN_MONTH_START` 5개 그룹 값 — **일치**.
- 오서둔 `_START` 5개 그룹 값 — **일치**.
- `ten_gods.py`의 `_ELEMENTS` (오행 배정)와 오행 생성 순환(`Element` enum 순서 wood→fire→earth→metal→water) — `docs/06` §5.1의 생(生) 순환과 **일치**. delta 기반 관계 판정(`same/generates/controls/controlled_by/generated_by`)도 상생·상극의 "X는 X+2를 극한다"는 항등식을 정확히 이용하고 있으며, 5개 관계 × same/different polarity = 10개 십신 매핑도 `docs/06` 표와 **정확히 일치**한다.
- 지장간 JSON 데이터(`hidden_stems_v1.json`)의 12개 지지 값 — `docs/06` §5.3 표와 **일치**.

이 부분은 긍정적으로 평가할 만하다. 다만 계산 로직의 "구현 방식"에는 아래 문제가 있다.

**[Major]** `ten_gods.py`의 `same_polarity = day_index % 2 == target_index % 2`는 `HeavenlyStem` enum이 "정확히 양-음이 번갈아 선언되어 있다"는 사실에 전적으로 의존한다. 이 가정을 강제하는 assert나 테스트가 전혀 없다. `_ELEMENTS` 튜플도 `stems.py`의 선언 순서에 위치 인덱스로만 연결되어 있다. `core_tables_v1.json`에는 이미 각 천간의 `yin_yang`, `element`가 명시적으로 들어 있는데도, 코드는 그 데이터를 참조하지 않고 "선언 순서"라는 암묵 규칙을 별도로 재구현했다. 누군가 가독성을 이유로 `HeavenlyStem`의 멤버 순서를 바꾸면 십신 계산이 조용히 깨진다.

**[Major]** `month_stem_for(year_stem, month_branch_offset_from_in)`은 월지를 나타내는 정수 offset(0~11)을 그대로 받는다. 이 offset이 실제로 어떤 지지(예: 인월=0, 묘월=1…)를 가리키는지 함수 스스로 검증하거나 연결할 방법이 없다. 절입 판정 로직(아직 미구현)이 나중에 이 함수를 호출할 때 오프셋 계산을 한 칸이라도 잘못하면, `month_stem_for`는 이를 감지하지 못하고 틀린 월간을 조용히 반환한다.

**[Minor]** `hour_stem_for`에는 입력 검증이 전혀 없다(5번 항목에서 상세).

---

## 3. 테스트가 구현을 그대로 반복하는 자기검증 문제

이 부분이 이번 커밋에서 가장 구조적으로 취약한 지점이다.

**[Critical]** `tests/test_hour_stem.py`의 `starts` 딕셔너리는 `hour_stem.py`의 `_START` 딕셔너리를 값 표현만 바꿔(정수 인덱스 → enum 멤버) 그대로 다시 타이핑한 것이다. 테스트는 `hour_stem_for`가 자기 자신의 offset 공식과 일관되는지만 확인할 뿐, `docs/06`의 원본 표나 별도 fixture 등 독립적인 근거와는 전혀 대조하지 않는다. `06` 문서의 오서둔 표 자체에 오탈자가 있었다면 코드와 테스트가 같은 오탈자를 공유한 채로 계속 통과한다.

**[Critical]** `tests/test_month_stem.py`도 동일한 유형이다. `test_five_tigers_start_stems`는 `month_stem_for`가 만들어내는 결과값(BYEONG, MU, GYEONG, IM, GAP)을 그대로 기대값으로 다시 적어놓은 것에 가깝고, `test_offsets_cycle_through_stems`는 "10번 이동한 결과가 다른 offset의 결과와 같다"는 **자기 자신과의 순환 일관성**만 확인할 뿐 실제 정답 여부를 독립적으로 검증하지 않는다. offset 1~9(2월~10월 월간)에 대한 개별 검증 케이스가 하나도 없다.

**[Major]** `tests/test_ten_gods.py`는 10개 일간 중 GAP 한 행만 "`TenGod` enum 선언 순서와 일치하는지"로 검증하고, 나머지 9개 행(90쌍)은 "100개 쌍이 전부 어떤 `TenGod` 값이든 반환하고 그 집합이 10개 십신 전체를 커버하는지"만 확인한다. 이는 완전성(coverage)만 검증할 뿐 개별 쌍의 정오답을 검증하지 않는다 — 예컨대 두 관계가 서로 뒤바뀌어도(예: 편재↔정관처럼 다른 열로 잘못 매핑) 커버리지 테스트는 여전히 통과할 수 있다.

**[Major]** `tests/fixtures/saju/`에 있는 두 fixture(`hour-boundary-001.json`, `day-anchor-2019-01-27-candidate.json`)가 이번 커밋의 어떤 테스트에서도 로드되지 않는다(`grep` 확인). `docs/06` §10 구현 게이트와 `tests/fixtures/saju/README.md`가 전제하는 "fixture 기반 회귀 테스트" 패턴이 아직 코드에 전혀 연결되어 있지 않다. 위에서 지적한 자기검증 문제를 막을 수 있는 유일한 장치(파일로 분리된 독립 fixture)가 이미 레포에 존재하는데도 활용되지 않고 있다.

**참고(자기검증 문제 아님)**: `tests/test_data_and_hidden_stems.py`의 `test_reference_values`는 자시(子)·인(寅) 지지의 지장간 값을 손으로 다시 타이핑해 비교한다. 이 값도 결국 같은 `06` 문서 표에서 나온 것이라 "완전히 독립적인 제3자 검증"은 아니지만, 이 테스트의 실제 목적(JSON 파일 파싱과 `hidden_stems_for`의 데이터 추출 로직이 맞는지)에는 부합하는 유효한 테스트다 — 나머지 세 모듈과 달리 실제 JSON을 거쳐서 검증하기 때문이다.

---

## 4. 데이터 로더의 production 상태 차단 안전성

**[Critical]** `hidden_stems.py`의 `hidden_stems_for()`가 `load_dataset("hidden_stems_v1", allow_unverified=True)`를 **하드코딩**으로 호출한다. 이건 테스트 코드가 아니라 `src/destiny_saju/hidden_stems.py`, 즉 production 라이브러리 코드다. 현재 `hidden_stems_v1.json`의 `status`는 `pending_verification`인데, 이 상태에서 어떤 상위 서비스 코드가 `hidden_stems_for()`를 호출하더라도 `DATASET_NOT_PRODUCTION_VERIFIED` 없이 조용히 값을 반환한다. `docs/06` §7·§8, `docs/07` §3.1이 요구하는 "production 계산 경로는 `production_verified`만 로드한다"는 핵심 원칙이 이 한 줄로 무력화되어 있다.

**[Critical]** 1번 항목에서 지적한 대로 `month_stem.py`, `hour_stem.py`, `ten_gods.py`는 애초에 `load_dataset`을 호출하지 않으므로, `hidden_stems`보다 더 근본적으로 상태 게이트 자체가 없다. 세 모듈의 계산 결과에는 "이 값이 검증됐는지 여부"에 대한 어떤 추적도 붙지 않는다.

**긍정적 평가**: `data_registry.load_dataset()` 자체의 기본 동작은 스펙과 일치한다 — `allow_unverified` 기본값은 `False`이고, `status`가 `production_verified`가 아니면 차단하며, 이를 검증하는 `test_unverified_dataset_is_blocked_by_default` 테스트도 실제로 통과한다(로컬 재현 확인). 문제는 로더 자체가 아니라, 유일하게 로더를 사용하는 콜사이트가 스스로 안전장치를 우회하고 있다는 점이다.

**[Minor]** `load_dataset()`은 `status` 필드가 `docs/07` §3의 4개 canonical 값(`draft`/`pending_verification`/`production_verified`/`deprecated`) 중 하나인지 자체는 검증하지 않는다. `"production_verified"` 문자열과의 단순 일치 비교라 fail-closed이긴 하지만(다른 값은 전부 차단으로 처리되므로 안전 방향의 실패), 오탈자로 잘못된 status 값이 들어가도 별도로 진단해주지 않아 디버깅이 어렵다.

---

## 5. 누락된 입력 검증과 경계 사례

**[Major]** `hour_stem_for(day_stem, branch)`에는 타입/값 검증이 전혀 없다. 기존 모듈 `hour_branch_for_time()`이 `isinstance` 체크로 명시적 `TypeError`를 던지는 것과 대조적으로, 이번 커밋에서 추가된 세 모듈(`month_stem`, `hour_stem`, `ten_gods`)에는 이런 방어 코드가 없거나 불완전하다.

**[Major]** `month_stem_for`는 `month_branch_offset_from_in` 범위(0~11)만 검증하고 `year_stem`의 타입은 검증하지 않는다. 잘못된 타입(예: 문자열 `"gap"`)을 넘기면 `_IN_MONTH_START[year_stem]`에서 unhelpful한 `KeyError`가 발생하며, 이는 `docs/06`의 통일 진단 코드 체계와 전혀 연결되지 않는다.

**[Major]** 이번에 추가된 4개 모듈 어디에도 `docs/06` §7의 진단 코드(`INVALID_DATE`, `UNKNOWN_BIRTH_TIME` 등)를 실제로 발생시키는 경로가 없다. 지금 구현 범위(월간/시간/십신/지장간)는 원시 출생정보를 직접 다루는 단계가 아니라서 당장 크게 문제되진 않지만, 상위 엔진이 이 모듈들을 호출할 때 어떤 예외/코드 계약을 기대해야 하는지가 전혀 정의되어 있지 않다 — 지금 정해두지 않으면 각 모듈이 서로 다른 방식(raw `KeyError`, `ValueError`, 혹은 무검증 통과)으로 실패하는 채로 굳어질 위험이 있다.

**[Minor]** 수치상 경계 커버리지(offset 0~11 전체, 시지 12개 전체, 십신 100쌍 전체)는 빠짐없이 순회하는 것처럼 보이지만, 3번 항목에서 지적했듯 "돌긴 도는데 정답 여부는 구조적으로 검증되지 않는다"는 문제가 있어 이 커버리지가 실제 정확성을 보장하지 않는다.

---

## 6. Python 패키징 및 테스트 실행 환경 문제

로컬에서 다음을 실제로 재현했다: `python3 -m venv`로 가상환경 생성 → `pip install -e .` → `pytest -v`. 결과: **11개 테스트, 126개 subtest 전부 정상 통과**. `pip uninstall` 후 `pyproject.toml`의 `pythonpath = ["src"]` 설정만으로 다시 실행해도 동일하게 전부 통과한다. 패키지 임포트 자체가 깨지는 수준의 문제는 없다.

**[Major]** `data_registry.py`가 데이터 파일 경로를 `Path(__file__).resolve().parents[2] / "data" / "saju"`로 계산한다. 이는 "레포를 통째로 체크아웃한 개발 환경"에서만 유효한 상대 경로 가정이다. `data/`가 `src/` 패키지 바깥에 있고 `package_data`/`MANIFEST.in`/`importlib.resources` 등으로 패키징되어 있지 않으므로, `pip install`로 만든 wheel/sdist를 별도 환경(예: 프로덕션 컨테이너)에 설치하면 이 경로 계산이 깨진다. 지금 로컬 검증(editable install, pytest pythonpath fallback)이 둘 다 통과한 것은 두 경우 모두 "레포 루트 기준 상대 경로"가 우연히 유지되기 때문이지, 패키징이 올바르게 되어 있어서가 아니다.

**[Minor]** `pyproject.toml`에 `pytest`가 의존성으로 선언되어 있지 않다(`[project.optional-dependencies]` 같은 dev 그룹 없음). 새 기여자가 `pip install -e .`만 실행하면 테스트를 돌릴 수 없고, README에도 안내가 없다.

**[Minor]** `[tool.setuptools.packages.find]` 같은 명시적 패키지 탐색 설정이 없어 src-layout 자동 인식에 의존한다. 지금은 setuptools 자동 탐지로 문제없이 동작함을 확인했지만(직접 설치해 검증), 이는 암묵적 동작이라 `src/` 아래 구조가 조금만 복잡해지면(예: 비-패키지 보조 디렉터리 추가) 조용히 깨질 수 있다.

**[Suggestion]** CI 설정(`.github/workflows` 등)이 전혀 없다. 테스트가 사람이 로컬에서 직접 돌리지 않는 한 실행을 강제할 방법이 없고, 이번 리뷰에서 지적한 문제들(자기검증 테스트, 미사용 데이터셋, production 게이트 우회) 상당수는 "테스트는 통과하지만 실효성이 없다"는 유형이라 CI 로그만 봐서는 알아채기 어렵다. 커밋마다 pytest를 돌리는 최소한의 워크플로 추가를 권장한다.

---

## Suggestion (낮은 우선순위)

- **[Suggestion]** `HourBranch` 타입명을 `docs/06`이 쓰는 용어에 맞춰 `EarthlyBranch`(또는 별도 alias)로 정리하는 것을 고려. 현재도 기능상 문제는 없으나 문서·코드 간 용어 불일치가 커뮤니케이션 비용을 만든다.
- **[Suggestion]** `ten_gods.py`의 same_polarity/오행 판정을 `core_tables_v1.json`의 `yin_yang`/`element` 필드에서 유도하도록 바꾸면, `HeavenlyStem` 선언 순서에 대한 암묵적 의존을 제거하고 어휘 데이터(`core_tables_v1.json`)와 계산 로직 사이의 단일 진실 소스를 확보할 수 있다.
- **[Suggestion]** `data_registry.load_dataset()`에 `status` enum 자체의 유효성 검사(4개 값 외 다른 문자열이면 명시적으로 "unknown status" 에러)를 추가하면 오탈자 디버깅이 쉬워진다.
- **[Suggestion]** `tests/fixtures/saju/*.json`을 실제로 로드해서 검증하는 fixture 러너를 하나 만들고, 최소한 `hour-boundary-001.json` 하나만이라도 연결해 "fixture 기반 회귀 테스트"의 첫 사례를 만들어두면 이후 절입시각·일주 anchor 데이터가 들어올 때 같은 패턴을 바로 재사용할 수 있다.

---

## 참고: 이 리뷰에서 확인하지 않은 것

- 절입시각, 일주 anchor, 대운 규칙 — 이번 커밋에 포함되지 않았으므로 검토 대상에서 제외했다(`docs/07` §8이 이미 "실제 값 없이 보류"라고 명시한 영역과 동일).
- `relations_v1`(합·충·형·파·해) — 이번 커밋에 아직 구현되지 않았다.
- 코드 스타일/포맷팅(예: `hour_stem.py`의 한 줄 압축 스타일)은 기능적 문제가 아니므로 이 리뷰의 범위에서 제외했다.
