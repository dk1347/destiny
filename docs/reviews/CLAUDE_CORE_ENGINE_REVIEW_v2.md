# Destiny — Core Engine Implementation Review (670dd45 → fbf9c2b), 재검토판

> 검토 범위: `src/destiny_saju/*`, `data/saju/*.json`, `tests/*`, `pyproject.toml`, `.github/workflows/test.yml`
> 대조 문서: `docs/06_ENGINE_CONTRACTS_AND_CORE_RULES.md`, `docs/07_VERSIONED_RULE_DATA_SPEC.md`
> 검토 방식: GitHub 저장소(main, HEAD `e907deb`)에서 소스를 직접 받아 로컬에 재구성 → `pip install -e '.[dev]'` + `pytest`로 실제 실행 → `python -m build --sdist`로 배포 패키징 실제 검증 → 오호둔/오서둔/십신/지장간 표를 손으로 재계산해 대조 → Element enum 재배치, 데이터 참조 누락 등 결함 주입(fault injection) 실험으로 취약점을 직접 재현. 코드는 수정하지 않음.
> 작성일: 2026-09-15

---

## 확인 사항: 이번 재검토의 대상 커밋에 대해

GitHub(`dk1347/destiny`, 브랜치 `main`)를 확인한 결과, 직전 리뷰 대상이었던 `fbf9c2b`("Enforce verified rule data across Saju calculators") 이후 저장소에 추가된 커밋은 `e907deb`("Add Claude core engine review v1") 하나뿐이며, 이 커밋은 `docs/reviews/CLAUDE_CORE_ENGINE_REVIEW_v1.md` 문서 파일을 추가한 것 외에 **소스 코드 변경을 포함하지 않습니다**. 즉 `src/destiny_saju/*`, `data/saju/*.json`, `tests/*`는 `fbf9c2b` 시점과 완전히 동일합니다.

말씀하신 "다시 소스 수정해서 커밋"이 아직 이 저장소(main)에는 반영되지 않은 것으로 보입니다. 로컬에만 있고 push 전이거나, 다른 브랜치/포크에 있을 가능성도 있습니다(브랜치 목록에는 `main` 하나만 확인됨). 이 재검토는 부득이 **현재 push되어 있는 최신 상태(`fbf9c2b`와 동일한 소스)**를 기준으로, 새로운 방법(실제 빌드/실행/결함 주입)으로 다시 독립 검증한 결과입니다. 추가로 push하신 커밋이 있다면 알려주시면 그 기준으로 다시 검토하겠습니다.

참고로 이번에 함께 확인해보니, 말씀하신 `docs/reviews/CLAUDE_IMPLEMENTATION_REVIEW_v1.md`는 `670dd45` 커밋의 코드 리뷰가 아니라, `670dd45`보다 먼저 작성된 스펙/문서 리뷰(`docs/03~05` 대상)입니다. `670dd45`를 대상으로 한 코드 리뷰는 `docs/reviews/CLAUDE_CORE_ENGINE_REVIEW_v1.md`이고, `docs/06`의 헤더에도 "Incorporates: CLAUDE_IMPLEMENTATION_REVIEW_v1.md"라고 명시되어 있어 두 문서가 서로 다른 단계에서 쓰인 것을 확인했습니다. 아래 재검토는 원래 6개 중점 항목(= `CLAUDE_CORE_ENGINE_REVIEW_v1.md`가 `670dd45`에 대해 사용한 항목)을 그대로 이어받아 진행했습니다.

---

## 요약

| 구분 | 이전 재검토(fbf9c2b, v2 초안) | 이번 재검토 |
|---|---|---|
| Critical | 0 | 0 |
| Major | 2 | 1 |
| Minor | 4 | 6 |
| Suggestion | 3 | 4 |

로컬 재현: `pip install -e '.[dev]'` → `pytest -v` **12/12 통과**. `pip uninstall` 후 `pythonpath` fallback으로도 **12/12 통과**. 여기까지는 이전 리뷰와 같은 결론입니다.

이번 재검토에서 새로 확인한 것은 두 가지입니다. (1) `python -m build --sdist`를 실제로 실행해, "data_dir을 필수 인자로 위임했지만 배포 시나리오는 미정"이라는 이전의 우려가 실제로 어떻게 나타나는지 직접 재현했습니다 — 결과는 **완전히 빈 데이터 디렉터리로 배포됨**(Major로 유지/구체화). (2) 이전 리뷰가 "해결됨"으로 정리한 부분(enum 선언 순서 의존 제거) 중 하나가 **다른 위치(오행 생극 순환의 `Element` enum)에 형태를 바꿔 남아 있음**을 결함 주입 실험으로 실증했습니다 — 다만 실제로 재배치를 가해 보니 golden fixture가 상당 부분(12건 중 4건) 이를 우연히 잡아낸다는 것도 함께 확인했습니다(Minor로 분류, 근거 첨부).

---

## 1. docs/06, docs/07 명세와 구현 일치 여부

**[확인 — 이전 결론 유지]** `month_stem.py`, `hour_stem.py`, `ten_gods.py`, `hidden_stems.py` 네 모듈 모두 `RuleRegistry.load()`를 통해 해당 JSON 데이터셋을 실제로 읽어 계산합니다. 소스를 직접 받아 로컬에서 실행해도 동일하게 동작함을 확인했고, 하드코딩된 중복 표는 남아 있지 않습니다. `docs/07`의 핵심 목표(규칙의 JSON 데이터셋화)가 달성된 상태가 이어지고 있습니다.

**[확인 — 이전 결론 유지]** `tables.py`의 `ordered_stems()`/`stem_attributes()`가 `core_tables_v1.json`의 `order`/`yin_yang`/`element` 필드를 직접 참조하므로, `month_stem_for`/`hour_stem_for`의 순환 계산은 더 이상 `HeavenlyStem` enum의 "선언 순서"에 의존하지 않습니다. 이를 직접 테스트했습니다: `HeavenlyStem`을 알파벳 순으로 재선언해도(실험) `ordered_stems()`가 반환하는 순서는 JSON의 `order` 필드만으로 결정되므로 결과가 바뀌지 않는 구조임을 코드 경로 추적으로 확인했습니다.

**[Minor — 신규 발견, §2에서 상세]** 다만 위와 별개로 `ten_gods.py`의 오행 생극 방향 판정은 여전히 **Python 코드에 하드코딩된 `Element` StrEnum의 선언 순서**(`WOOD, FIRE, EARTH, METAL, WATER`)에 의존합니다. `docs/06` §5.1의 생(生) 순환 자체가 `core_tables_v1.json`에 명시적 필드로 존재하지 않고, 오직 이 enum의 나열 순서로만 코드에 인코딩되어 있습니다. 즉 "enum 선언 순서 의존"이라는 이전 리뷰의 핵심 지적이 `HeavenlyStem`에서는 해소됐지만, 같은 종류의 의존이 `Element`에서는 형태를 바꿔 남아 있습니다. 상세 근거는 §2.

**[해결됨 — 이전 Major, 재확인]** `EarthlyBranch` 타입이 `docs/06` §2가 요구하는 이름으로 존재하고, `HourBranch = EarthlyBranch`는 하위 호환 별칭으로 유지됩니다.

**[Minor — 이전과 동일 판단]** `DiagnosticCode`(`diagnostics.py`)는 `DATASET_NOT_PRODUCTION_VERIFIED`, `DATASET_STATUS_INVALID`, `DATASET_SCHEMA_INVALID`, `INVALID_STEM`, `INVALID_BRANCH` 5개만 정의합니다. `docs/06` §7이 정의한 17개 코드 중 나머지(`INVALID_DATE`, `UNKNOWN_BIRTH_TIME`, `AMBIGUOUS_LOCAL_TIME` 등 출생정보·시간복원 계층)는 아직 없습니다. 이 계층 자체가 구현되지 않은 상태이므로 지금 시점에는 공백이 자연스럽지만, 그 계층을 구현할 때 diagnostics.py를 확장하는 작업이 반드시 뒤따라야 한다는 점을 다시 표시해 둡니다.

**[범위 밖, 변화 없음]** `relations_v1`(합·충·형·파·해)은 여전히 구현되지 않았습니다. 이번 재검토 대상 소스에도 포함되어 있지 않으므로 회귀는 아닙니다.

---

## 2. 오호둔·오서둔·십신·지장간 계산 오류

계산값 자체를 `docs/06` §3.1/§3.2/§5.1~§5.3 표와 다시 손으로 대조했고, 아래 항목은 모두 일치를 확인했습니다(첫 리뷰 이후 데이터 변경 없음).

- `month_stem_rules_v1.json`의 5개 그룹(갑기→병, 을경→무, 병신→경, 정임→임, 무계→갑)과 `month_branch_order_from_in`(인묘진사오미신유술해자축) — **일치**.
- `hour_stem_rules_v1.json`의 5개 그룹(갑기→갑, 을경→병, 병신→무, 정임→경, 무계→임)과 `hour_branch_order_from_ja`(자축인묘진사오미신유술해) — **일치**.
- `hidden_stems_v1.json`의 12개 지지 지장간 구성 — **일치**.
- `ten_gods_v1.json`의 관계표(비견/겁재…정인) — **일치**.

코드 로직도 직접 재유도해 검증했습니다. `ten_gods.py`의 델타 매핑

```
delta = (index(target_element) - index(day_element)) % 5
0→same_element, 1→day_master_generates_target, 2→day_master_controls_target,
3→target_controls_day_master, 4→target_generates_day_master
```

이 `docs/06` §5.1의 생 순환(`wood→fire→earth→metal→water→wood`, +1 오프셋)과 극 순환(`wood→earth→water→fire→metal→wood`, +2 오프셋)에서 수학적으로 정확히 도출된다는 것을 직접 재유도해 확인했습니다(예: 극 관계는 매번 순환에서 두 칸씩 건너뛰므로 delta=2가 "생성" 아닌 "극"에 대응하는 것이 항등식으로 성립).

로컬에서 golden fixture(`core-rule-golden-v1.json`) 12+13+12건을 모두 재계산해 기대값과 완전히 일치함을 확인했고, 추가로 다음을 손으로 검산해 교차 확인했습니다: `("gap","myo","jeong")`, `("gap","chuk","eul")`(오서둔), `("gye","gap","sangwan")`(역방향 십신, 계수→갑목은 생 관계이자 음양이 달라 상관) 등. 모두 일치.

**[Minor — 신규 발견, 결함 주입으로 실증]** `Element` enum의 선언 순서를 알파벳순(`EARTH, FIRE, METAL, WATER, WOOD`)으로 바꾸는 실험을 로컬에서 실제로 수행했습니다. 결과: 100개 일간×대상 쌍 중 **56쌍의 십신 결과가 조용히 달라짐**(예: 갑목 일간·병화 대상이 식신→편재로 바뀜). 이 재배치를 감지할 `isinstance`/assert 가드는 코드에 없습니다. 다만 같은 실험에서 `core-rule-golden-v1.json`의 십신 golden case 12건 중 4건이 실제로 실패로 바뀌는 것도 확인했습니다 — 즉 지금 있는 golden 테스트가 이런 유형의 회귀를 **부분적으로는** 잡아냅니다(전수는 아님, 갑목 기준 케이스만 있으므로). 결론: 실제 버그는 아니지만, "오행 생극 순환의 유일한 소스가 코드 파일 안의 enum 나열 순서"라는 구조적 취약점이 남아 있고, 이는 데이터 소스 하나로 계산을 통일한다는 이번 커밋의 목적과 정확히 같은 종류의 위험입니다. `core_tables_v1.json`에 오행 생/극 순환 자체를 명시적 필드로 추가하고 `ten_gods.py`가 그 필드를 읽도록 바꾸면 근본적으로 해소됩니다.

**[Minor — 신규 발견, 실증]** `HeavenlyStem`과 `EarthlyBranch`는 둘 다 `StrEnum`이라 문자열 값이 같으면(`"sin"`) 서로 다른 타입인데도 `==`와 해시가 같다고 판정됩니다. 직접 확인:

```python
>>> HeavenlyStem.SIN == EarthlyBranch.SIN
True
>>> {HeavenlyStem.SIN: "x"}.get(EarthlyBranch.SIN)
'x'
```

`isinstance(HeavenlyStem.SIN, EarthlyBranch)`는 `False`이므로, 현재 코드 전체가 타입 검증에 `isinstance`만 쓰고 있어(모든 계산 함수 진입점에서 확인) 실제로 이 값이 섞여 들어가는 경로는 없습니다. 다만 애초에(첫 스펙 리뷰 2.1 항목) 이 문제를 "타입 시스템에서 원천적으로 불가능하게 한다"는 설계 목표로 제시했었는데, `StrEnum`을 쓰는 한 그 목표는 엄밀히는 달성되지 않고 "지금까지 짜인 호출 경로가 우연히 안전할 뿐"이라는 점을 명확히 해 둘 필요가 있습니다. 향후 두 타입의 멤버를 같은 dict/set/list에 섞어 넣는 코드(예: 로깅, 직렬화, 캐시 키)가 추가되면 재발할 수 있는 위험입니다.

---

## 3. 테스트가 구현을 그대로 반복하는 자기검증 문제

**[확인 — 이전 결론 유지]** `test_month_stem.py`, `test_hour_stem.py`, `test_ten_gods.py`는 모두 별도 파일 `core-rule-golden-v1.json`에서 기대값을 읽어와 비교하며, 구현 코드 내부 표를 다시 타이핑하는 구조는 남아 있지 않습니다. 로컬에서 golden 파일을 그대로 로드해 재실행해도 12/12 통과를 확인했습니다.

같은 한계도 이전과 동일하게 남아 있습니다: golden case 값 자체가 `docs/06`이라는 단일 출처에서 나왔으므로 완전한 제3자 검증은 아직 아닙니다(파일이 스스로 `status: pending_independent_verification`이라고 표시하는 점은 정직한 태도로 평가). **Suggestion으로 유지**.

**[Minor — 이전 지적 재확인, 근거 보강]** `test_all_one_hundred_pairs_produce_a_ten_god`는 완전성(coverage)만 검증합니다. 다만 이번에 직접 100쌍을 전수 계산해 보니, golden case가 GAP(갑)을 일간으로 한 10쌍 전부(5개 관계×2개 극성)를 다루고 있어 **오행/음양 데이터 자체의 정확성**은 사실상 간접적으로 이미 검증되고 있음을 확인했습니다(다른 9개 일간에 대해 별도 분기 로직이 없고 동일한 함수 경로를 타기 때문). 그러나 "다른 9개 일간 기준의 90쌍"에 대해 엄밀한 의미의 정답 assertion은 여전히 없으므로, 코드가 나중에 일간별 특수 처리를 추가하는 방향으로 바뀌면 이 커버리지 공백이 실질적 위험이 됩니다. 분류는 Minor로 유지합니다.

**[확인 — 이전 결론 유지]** `hour-boundary-001.json`이 `test_fixtures.py`에서 실제로 로드되어 사용됩니다. `day-anchor-2019-01-27-candidate.json`은 여전히 미사용이지만 일주 anchor 자체가 스코프 밖이라 문제는 아닙니다.

**[Minor — 이전 지적 유지]** golden case 커버리지가 월간 60개 조합 중 13개, 시간 60개 조합 중 12개만 샘플링되어 있습니다(전수 아님). 순환식 자체의 정합성 확인 용도로는 충분하지만, GAP·GI 그룹 외 offset 2~9 구간은 값 대조가 비어 있습니다.

---

## 4. 데이터 로더의 production 상태 차단 안전성

**[확인 — 이전 결론 유지]** `hidden_stems_for`, `hour_stem_for`, `month_stem_for`, `ten_god_for` 네 함수 모두 `registry: RuleRegistry`를 인자로 받고, 하드코딩된 `allow_unverified=True` 우회는 소스 어디에도 없습니다(grep으로 재확인). `test_every_calculator_obeys_production_gate`를 로컬에서 재실행해, 기본 `RuleRegistry(DATA_DIR)`(=`allow_unverified=False`)로 네 함수를 호출하면 예외 없이 전부 `DATASET_NOT_PRODUCTION_VERIFIED`를 던지는 것을 확인했습니다.

**[확인 — 이전 결론 유지]** `_VALID_STATUSES`가 `draft`/`pending_verification`/`production_verified`/`deprecated`만 허용하고, `core_tables_v1.json`의 `status`는 `pending_verification`으로 정상 표기되어 있습니다(이전 리뷰가 지적했던 `draft_for_validation` 오탈자성 값은 남아 있지 않음).

**참고**: 현재 `data/saju/*.json` 5개 파일이 전부 `pending_verification` 상태이므로, 기본 `RuleRegistry`(운영 경로 가정)로는 네 계산 함수 중 어느 것도 값을 반환하지 못하는 상태입니다. 이는 의도된 설계(검증 전 데이터는 운영에 흘려보내지 않음)이며 결함이 아닙니다.

**[Minor — 이전 지적 유지]** `RuleRegistry`는 호출마다 파일을 다시 읽습니다(캐시 없음). 지금 규모에서는 문제없습니다.

---

## 5. 누락된 입력 검증과 경계 사례

**[확인 — 이전 결론 유지]** `hidden_stems_for`, `hour_stem_for`, `month_stem_for`, `ten_god_for` 모두 `isinstance` 체크로 잘못된 타입에 `CalculationInputError(DiagnosticCode.INVALID_STEM/INVALID_BRANCH, ...)`를 던집니다.

**[Minor — 이전 지적 유지, 실증 재확인]** 타입은 맞지만 참조 무결성이 깨진 경우(데이터셋에 대응 행이 없는 경우)는 여전히 raw 예외가 새어 나갑니다. 실제로 결함을 주입해 확인했습니다: `month_stem_rules_v1`의 `month_branch_order_from_in`에서 `branch:chuk` 항목을 제거한 뒤 `month_stem_for(GAP, CHUK, ...)`를 호출하면

```
ValueError: 'branch:chuk' is not in list
```

가 `DiagnosticCode`로 감싸이지 않고 그대로 올라옵니다. 지금 데이터가 사람이 직접 작성한 소량이고 이미 `docs/06`과 대조 확인된 상태라 실제 발생 가능성은 낮지만, `docs/07` §6.4가 요구하는 참조 무결성 검사(lint)가 아직 없다는 근본 원인은 그대로입니다.

---

## 6. Python 패키징 및 테스트 실행 환경 문제

로컬 재현: `python3.11 -m venv` → `pip install -e '.[dev]'` → `pytest -v` **12/12 통과**. `pip uninstall destiny-saju` 후 `pythonpath` fallback만으로도 **12/12 통과**. 여기까지는 이전과 동일합니다.

**[Major — 이전 "완화됨"에서 재분류, 실측으로 구체화]** 이전 리뷰는 "`data_dir`를 필수 인자로 위임했지만 실제 배포 시나리오는 미정"이라고 정리했는데, 이번에 `python -m build --sdist`로 **실제 소스 배포판을 만들어 내용물을 확인**했습니다.

```
destiny_saju-0.1.0/src/destiny_saju/*.py   ← 포함됨
destiny_saju-0.1.0/tests/*.py              ← 포함됨
data/saju/*.json                           ← 포함되지 않음
```

`[tool.setuptools.packages.find] where = ["src"]` 설정상 `data/`가 `src/` 바깥에 있고 `package_data`/`MANIFEST.in`/`importlib.resources` 등 데이터 포함 설정이 전혀 없기 때문에, 이 sdist(또는 여기서 만든 wheel)를 설치한 환경에는 `data/saju/*.json`이 아예 존재하지 않습니다. `RuleRegistry(data_dir=...)`가 필수 인자를 요구하도록 바뀐 것은 "잘못된 경로를 스스로 계산하던 버그"는 제거했지만, "설치된 패키지가 필요한 데이터를 아예 갖고 있지 않다"는 더 근본적인 문제는 그대로이며 지금 처음으로 실측 확인됐습니다. 엔진 진입점을 만들기 전에 반드시 다음 중 하나를 결정해야 합니다: (a) `data/`를 `src/destiny_saju/data/`로 옮기고 `package_data`로 포함, (b) `importlib.resources`로 패키지 내부 리소스를 읽도록 전환, (c) 데이터를 별도 아티팩트/설정 경로로 배포하고 배포 파이프라인에서 명시적으로 주입. 지금처럼 "테스트가 레포 체크아웃 상대 경로로 직접 계산해서 넘긴다"는 사실만으로는 실제 배포 가능성을 보장하지 않습니다.

**[확인 — 이전 결론 유지]** `[project.optional-dependencies] dev = ["pytest>=8,<9"]`, `[tool.setuptools.packages.find] where = ["src"]`, `.github/workflows/test.yml`(push/PR마다 `pip install -e '.[dev]'` + `pytest -q`) 모두 존재하고 로컬 재현에서 그대로 동작함을 확인했습니다.

**[Minor — 신규 발견]** `.github/workflows/test.yml`은 Python 3.11 한 버전만 테스트합니다. `pyproject.toml`의 `requires-python = ">=3.11"`이 상한을 두지 않으므로, 이후 Python 버전에서의 회귀를 CI가 잡지 못합니다. 지금은 우선순위가 낮습니다.

**[Minor — 신규 발견]** 패키지 최상위 `src/destiny_saju/__init__.py`는 여전히 `EarthlyBranch`, `HourBranch`, `hour_branch_for_time`만 export합니다. 이번 커밋(`fbf9c2b`)에서 추가된 `RuleRegistry`, `hidden_stems_for`, `hour_stem_for`, `month_stem_for`, `ten_god_for`, `TenGod`, `Element`, `DiagnosticCode`, `CalculationInputError` 등은 공개 API(`__all__`)에 없어, 외부에서 쓰려면 서브모듈 경로를 직접 알아야 합니다. 기능적 문제는 아니지만 패키지의 공개 표면이 실제 구현 범위를 반영하지 못하고 있습니다.

---

## 남은 항목 정리

| 심각도 | 항목 | 근거 |
|---|---|---|
| Major | `data/saju/*.json`이 sdist/wheel에 전혀 포함되지 않아, 배포된 패키지는 계산에 필요한 데이터를 아예 갖고 있지 않음 | `python -m build --sdist` 실측 |
| Minor | 참조 무결성 실패 시 `DiagnosticCode` 없이 raw `ValueError`/`StopIteration` 유출 | 결함 주입으로 재현 (`branch:chuk` 제거 후 확인) |
| Minor | `ten_gods.py`의 오행 생극 순환이 `Element` enum 선언 순서에 암묵 의존(코드가 유일한 소스) | 알파벳 재배치 실험 → 100쌍 중 56쌍 변경, golden 12건 중 4건 실패로 부분 감지 확인 |
| Minor | `HeavenlyStem`/`EarthlyBranch`가 `StrEnum`이라 값이 같으면(`"sin"`) `==`/hash가 교차 일치함(현재는 모든 진입점이 `isinstance`로 방어해 실제 버그 없음) | `HeavenlyStem.SIN == EarthlyBranch.SIN` 등 직접 실행 확인 |
| Minor | `DiagnosticCode`가 데이터셋 계층 5개만 있고 `docs/06` §7의 출생정보/시간복원 계층 코드 없음 | 그 계층이 아직 미구현이라 자연스러운 공백, 구현 시 함께 채울 것 |
| Minor | golden case 커버리지: 월간/시간 60개 조합 중 13/12개, 십신은 GAP 기준만 전수 | 파일 직접 확인 |
| Suggestion | `core-rule-golden-v1.json`이 `docs/06` 단일 출처(제3자 검증 전) | 파일 자체의 `status` 표기 |
| Suggestion | `RuleRegistry`에 파일 캐시 없음 | 코드 확인, 현재 규모에서 무해 |
| Suggestion | `relations_v1`(합충형파해) 미구현 | 범위 밖, 회귀 아님 |
| Suggestion | CI가 Python 3.11 단일 버전만 테스트 | `.github/workflows/test.yml` 확인 |

---

## 이 리뷰에서 확인하지 않은 것

- 절입시각, 일주 anchor, 대운 규칙 — 이번 소스에도 포함되지 않음(`docs/07` §8이 이미 보류로 명시).
- `relations_v1`(합·충·형·파·해) — 여전히 미구현.
- 코드 스타일/포맷팅 — 기능적 문제가 아니므로 범위에서 제외.
- 이번 재검토는 `fbf9c2b`와 동일한 소스를 대상으로 했습니다. 실제로 추가 수정을 push하셨다면 그 커밋 SHA를 알려주시면 diff 기준으로 다시 검토하겠습니다.
