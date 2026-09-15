# Claude Core Engine Review v2 — 조치 결과

> 대상 리뷰: `CLAUDE_CORE_ENGINE_REVIEW_v2.md`
> 조치일: 2026-09-15
> 범위: 리뷰에서 확인된 Major 1건과 즉시 처리 가능한 구조적 Minor 항목

## 완료한 조치

1. **배포 패키지 데이터 누락 해결**
   - 엔진이 사용하는 JSON 5개를 `src/destiny_saju/data/saju/`로 이동했다.
   - setuptools package data와 `importlib.resources`를 적용했다.
   - sdist와 wheel에 JSON이 포함되는지, wheel만 설치한 새 환경에서 기본 `RuleRegistry`가 데이터를 읽는지 검증한다.

2. **오행 enum 선언 순서 의존 제거**
   - 생·극 관계를 `core_tables_v1.json`의 `element_relations`에 명시했다.
   - 십신 계산은 enum 순서가 아니라 이 데이터만 참조한다.

3. **천간·지지 교차 동등성 제거**
   - `HeavenlyStem`, `EarthlyBranch`를 문자열 기반 enum에서 일반 `Enum`으로 변경했다.
   - 같은 로마자 ID인 `stem:sin`과 `branch:sin`은 더 이상 같다고 비교되지 않는다.

4. **데이터 참조 무결성 검사 추가**
   - 천간·지지 전수성, 시작 천간 참조, 지장간 참조, 십신 표, 오행 관계를 로드 시점에 검사한다.
   - 깨진 참조는 raw `ValueError`/`StopIteration` 대신 `DATASET_SCHEMA_INVALID`로 통일한다.

5. **캐시·공개 API·CI 보강**
   - `RuleRegistry`에 캐시와 방어적 복사를 적용했다.
   - 계산기의 공개 API를 패키지 최상위에서 export한다.
   - CI를 Python 3.11·3.12·3.13으로 확장하고 wheel 설치 검증을 추가했다.

## 의도적으로 남긴 항목

- 데이터 상태는 독립 검증 전이므로 계속 `pending_verification`으로 유지한다.
- 절입시각, 일주 기준일, 출생시간 복원 진단 코드는 해당 계산 계층 구현 시 추가한다.
- 합·충·형·파·해(`relations_v1`)는 다음 계산 규칙 구현 단계에서 다룬다.
- golden fixture의 외부 독립 검증은 별도 검증 작업으로 유지한다.
