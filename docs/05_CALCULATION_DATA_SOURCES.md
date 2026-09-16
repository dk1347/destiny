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

## 5. Future true-solar-time profile gate

진태양시 보정은 법정시의 대체 사실이 아니라 별도 Calculation Profile의
계산값이다. 따라서 `true_solar_time` 프로필은 아래 근거를 결과와 함께
버전 고정할 수 있을 때만 제공한다.

| 입력 또는 계산 단계 | 필수 provenance | 제공 불가 조건 |
| --- | --- | --- |
| 법정 현지시 → UTC | IANA time-zone identifier와 사용한 tzdb release | 역사적 표준시 또는 DST 근거가 불충분함 |
| 출생지 → 경도 | 지오코딩 출처, 좌표, 위치 정밀도 | 도시 수준에서도 위치를 확정할 수 없음 |
| 경도 보정 | 기준 자오선, 부호 규칙, 알고리즘 버전 | 알고리즘 또는 기준 시간대가 기록되지 않음 |
| 평균태양시 → 진태양시 | 균시차 모델, 입력 천문 시각, 알고리즘 버전과 오차 정책 | 모델의 지원 범위·오차 정책이 없음 |

균시차는 겉보기 태양시와 평균태양시의 차이이며, 경도 보정과 별개의
성분이다. 두 보정을 하나의 불투명한 “태양시 보정” 값으로 저장하거나,
법정시만으로 자동 추정해서는 안 된다.

`true_solar_time` 프로필의 검증에는 최소한 다음을 포함한다.

- timezone/DST 전환과 역사적 표준시 변경 사례
- 시지·일주·절기 경계를 실제로 넘는 합성 사례와 넘지 않는 대조 사례
- 기본 법정시 프로필과 구조화된 주 결과가 같은 경우 선택지를 노출하지
  않는 사례
- 위치·시간 근거가 부족한 경우 보정 결과를 만들지 않고 `unknown` 또는
  후보 상태를 보존하는 사례

IANA tzdb는 현실 법정시 이력의 실용적인 입력 데이터이며, 스스로도 모든
역사 기록에 대해 절대적 권위를 주장하지 않는다. 따라서 프로필 결과에는
tzdb release와 불확실성 상태를 남기고, 지원 근거가 약한 기간·지역은
기본 법정시 결과로 조용히 대체하지 않고 명시적으로 보류한다.

## References for validation

- 24 Solar Terms definition and algorithms: https://ytliu0.github.io/ChineseCalendar/solarTerms.html
- Sexagenary-day/JDN derivation: https://ytliu0.github.io/ChineseCalendar/sexagenary.html
- JPL development ephemerides: https://ssd.jpl.nasa.gov/planets/eph_export.html
- IANA Time Zone Database: https://www.iana.org/time-zones
- U.S. Naval Observatory, Equation of Time: https://aa.usno.navy.mil/faq/eqtime
- NOAA, General Solar Position Calculations: https://gml.noaa.gov/grad/solcalc/solareqns.PDF
- Reference implementation only: https://github.com/rath/orrery

## Open implementation decision

절입 데이터 생성기는 backend language와 deployment target을 확정할 때 선택한다. 선택 전에는 고정된 테스트 데이터셋을 검증 용도로만 추가하며, 정확도·지원 연도·라이선스가 확인되지 않은 패키지는 production dependency로 채택하지 않는다.
