# Destiny — Calculation Data Source Policy

> Version: 0.1  
> Status: Draft for Architecture Review

## Decision

Destiny는 사주 원국을 계산할 때 제3자 만세력 웹사이트를 런타임 의존성으로 사용하지 않는다. 입력·계산 프로필·데이터셋 버전을 저장해 동일한 결과를 재현한다.

## 1. Solar-term instants

### Production direction

24절입은 태양의 겉보기 지심 황경이 15° 간격의 경계에 도달하는 시각으로 계산하거나, 같은 정의와 명시적 버전을 가진 사전 생성 데이터셋으로 제공한다.

```text
astronomical model / ephemeris
        ↓
solar longitude solver
        ↓
UTC solar-term instant
        ↓
Time Resolution Engine
        ↓
Calculation Profile boundary decision
```

- 첫 출시 범위는 한국 MVP 지원 기간의 절입시각을 versioned dataset으로 빌드 시 포함한다.
- 원천 천문 모델·생성 스크립트·데이터 생성 일시·오차 정책을 함께 보관한다.
- API 장애나 제3자 서비스 변경이 원국 결과를 바꾸게 하지 않는다.
- `rath/orrery`는 결과 대조용 참고 구현으로만 사용하며 Destiny 제품 의존성으로 포함하지 않는다.

## 2. Day pillar anchor

일주는 하나의 검증된 기준일과 Julian Day Number의 60일 모듈러 순환으로 계산한다.

```text
sexagenary_index = modulo(anchor_index + days_between(anchor_date, target_date), 60)
```

Production anchor는 아래 조건을 모두 만족해야 한다.

1. 공개적으로 재현 가능한 날짜·시간대·60갑자 index를 가진다.
2. 독립된 두 출처와 대조한다.
3. 적용 Calculation Profile의 일주 경계와 혼동되지 않도록 JDN 기준과 local civil date 변환을 명시한다.
4. anchor와 검증 사례는 코드가 아닌 versioned data asset으로 저장한다.

## 3. Calendar and time data separation

| 데이터 | 담당 엔진 | 사주 엔진의 역할 |
|---|---|---|
| 음양력 변환·윤달 | Calendar Engine | 양력 날짜/후보 수신 |
| 시간대·DST·역사적 법정시 | Time Resolution Engine | 계산 기준 시각 선택 |
| 절입시각 | Solar-term dataset/generator | 연주·월주 경계 적용 |
| 60갑자·오행 표 | Saju core data | 원국 및 파생 데이터 계산 |

## 4. Validation gate

프로덕션 원국 계산 전 다음을 완료한다.

- 각 절입의 직전·정각·직후 테스트를 데이터셋 지원 기간 전체에 생성한다.
- 일주 anchor 전후 60일을 독립 출처와 대조한다.
- Korea 표준시 및 1988년 DST 사례를 Time Resolution Engine 통합 테스트에 포함한다.
- 서로 다른 Calculation Profile의 차이는 같은 입력에서 의도적으로 확인한다.

## References for validation

- 24 Solar Terms definition and algorithms: https://ytliu0.github.io/ChineseCalendar/solarTerms.html
- Sexagenary-day/JDN derivation: https://ytliu0.github.io/ChineseCalendar/sexagenary.html
- JPL development ephemerides: https://ssd.jpl.nasa.gov/planets/eph_export.html
- Reference implementation only: https://github.com/rath/orrery

## Open implementation decision

절입 데이터 생성기는 backend language와 deployment target을 확정할 때 선택한다. 선택 전에는 고정된 테스트 데이터셋을 검증 용도로만 추가하며, 정확도·지원 연도·라이선스가 확인되지 않은 패키지는 production dependency로 채택하지 않는다.
