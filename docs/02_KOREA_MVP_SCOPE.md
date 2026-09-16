\# Destiny — Korea MVP Scope



> Version: 1.0  

> Phase: Korea MVP Definition  

> Status: Draft for Product Owner approval



\---



\## 1. MVP Objective



Destiny의 첫 번째 MVP는 한국 사용자를 대상으로 하는 사주·명리학 기반 분석 서비스다.



MVP의 최우선 목표는 다음 두 가지다.



1\. 출생정보를 정확하게 처리하여 신뢰할 수 있는 사주 계산 결과를 생성한다.

2\. 계산 결과와 검증된 Knowledge를 기반으로 AI가 이해하기 쉬운 해석을 제공한다.



MVP 단계에서는 결제, 회원가입, 고급 커머스 기능보다 계산 정확도와 해석 품질을 우선한다.



\---



\## 2. Core MVP Service



Korea MVP V1의 핵심 서비스는 다음으로 한정한다.



\- 사주팔자

\- 만세력 기반 계산

\- 오행

\- 십신

\- 지장간

\- 합 / 충 / 형 / 파 / 해 등 관계

\- 세운

\- 기본 사주 분석

\- AI 종합 해석



\---



\## 3. Deferred Features



다음 기능은 MVP 이후 단계로 보류한다.



\- 궁합

\- 택일

\- 토정비결

\- 주역 점

\- 타로

\- 서양 점성술

\- Twin Flames

\- 수비학

\- 국가별 전통 점술

\- 대운

\- 5주10자

\- 명궁 기반 공간 분석

\- 혼천의 시각화



5주10자 및 명궁은 별도의 Research Track에서 계속 연구할 수 있다.



\---



\## 4. User Flow



초기 MVP 사용자 흐름은 최대한 단순하게 구성한다.



Birth Information Input  

↓  

Birth Engine  

↓  

Saju Calculation Engine  

↓  

Basic Analysis  

↓  

Knowledge Retrieval  

↓  

AI Interpretation  

↓  

Result



\---



\## 5. Birth Information Input



MVP에서 기본적으로 받는 정보:



\- 이름 또는 표시용 별명

\- 성별 또는 분석에 필요한 프로필 정보

\- 양력 / 음력

\- 생년월일

\- 윤달 여부

\- 출생시간

\- 출생시간 정밀도

\- 출생지역



사용자가 모르는 정보는 임의로 생성하지 않는다.



\---



\## 6. Payment Policy



Payment 기능은 Korea MVP V1에서 구현하지 않는다.



현재 목표는 사주 계산 및 AI 해석 품질 검증이다.



다음 항목은 후속 단계로 연기한다.



\- 유료 / 무료 기능 구분

\- 가격 정책

\- PG 연동

\- 주문

\- 결제

\- 환불

\- 영수증

\- 결제 이력



필요한 경우 공개 베타 단계에서 다음과 같은 안내 문구를 사용할 수 있다.



> 현재 베타 기간 동안 무료로 제공됩니다.



향후 서비스 검증 후 유료 기능을 추가할 수 있다.



\---



\## 7. Account Policy



MVP V1에서는 회원가입을 필수 요구사항으로 두지 않는다.



다음 기능은 향후 필요성에 따라 추가한다.



\- 사용자 계정

\- 로그인

\- 소셜 로그인

\- 분석 결과 저장

\- 분석 이력

\- 결제 내역

\- 사용자 프로필



Core Calculation Engine은 계정 시스템과 독립적으로 동작해야 한다.



\---



\## 8. Architecture Requirement



결제 및 계정 기능을 나중에 추가해도 사주 계산 Core를 수정하지 않도록 설계한다.



Example:



Account / Payment / History  

↓  

Service Layer  

↓  

Birth Engine  

↓  

Saju Engine  

↓  

Knowledge / RAG  

↓  

Interpretation Engine



Core Engine은 사용자 인증 및 결제 시스템에 의존하지 않는다.



\---



\## 9. MVP Priority



\### P0



\- BirthProfile 정의

\- 양력 / 음력 처리

\- 윤달 처리

\- 시간 처리

\- 출생지역 처리

\- 사주 4주8자 계산

\- 절기 기반 월주 계산

\- 일주 계산

\- 시주 계산

\- 야자시 / 조자시 정책

\- 테스트 및 검증



\### P1



\- 오행 분석

\- 십신

\- 지장간

\- 합 / 충 / 형 / 파 / 해

\- 기본 사주 해석 구조



\### P2



\- Knowledge RAG

\- AI Interpretation

\- 사용자 결과 화면

\- 설명 품질 개선



\---



\## 10. Calculation Accuracy Policy



사주 계산 결과는 LLM이 생성하지 않는다.



LLM은 다음 자료만 해석한다.



\- 계산 Engine 결과

\- 구조화된 Knowledge

\- 검증된 Source Context



Principle:



> Computer calculates, AI interprets.



\---



\## 11. School / Rule Differences



명리학에는 학파별 계산 및 해석 차이가 존재할 수 있다.



예:



\- 야자시 / 조자시

\- 일자 변경 기준

\- 대운 계산 방식

\- 용신 판단

\- 신강 / 신약 판단



MVP에서는 계산 규칙을 명시적으로 기록하며, 가능한 경우 Calculation Profile로 분리한다.

대운은 Korea MVP V1 공개 범위에서 제외한다. 순역·기산·절입 기준·성별
처리·경계 사례가 별도 `daewoon_rules_v1`로 검증된 뒤 후속 기능으로
추가한다. 이 결정은 추정 계산값을 사용자에게 제공하지 않기 위한 것이다.



\---



\## 12. Interpretation Policy



AI는 사주 결과를 확정적 미래 예언으로 표현하지 않는다.



해석은 다음 방향을 기본으로 한다.



\- 성향

\- 경향

\- 가능성

\- 삶의 흐름

\- 자기성찰

\- 선택에 대한 참고



다음 영역은 전문적인 확정 판단으로 제공하지 않는다.



\- 의료

\- 법률

\- 투자

\- 생명 / 안전 관련 판단



\---



\## 13. Success Criteria



Korea MVP V1의 성공 기준:



1\. Birth input이 안정적으로 처리된다.

2\. 양력 / 음력 / 윤달 변환이 검증된다.

3\. 4주8자 계산 결과가 기준 데이터와 높은 일치도를 보인다.

4\. 절기 경계 사례가 검증된다.

5\. 야자시 / 조자시 규칙이 명확하다.

6\. AI가 계산 결과를 임의로 변경하지 않는다.

7\. 사용자에게 이해하기 쉬운 결과를 제공한다.

8\. 주요 테스트 케이스가 자동화된다.

9\. 저작권 및 개인정보 정책을 위반하지 않는다.



\---



\## 14. Out of Scope



Korea MVP V1에서 명확하게 제외:



\- 결제

\- 구독

\- 광고 시스템

\- 복잡한 회원관리

\- 모바일 Native App

\- 5주10자 Production 적용

\- 명궁 Production 적용

\- 글로벌 다국어 서비스

\- 타로 / 점성술 통합

\- 궁합 / 택일 / 토정비결 전체 구현



\---



\## 15. Next Specification



Next document:



`03\_BIRTH\_PROFILE\_SPEC.md`



목표:



사용자의 출생정보를 Destiny 전체 시스템에서 공통으로 사용할 수 있는 표준 데이터 모델로 정의한다.



BirthProfile은 이후 다음 Engine들의 공통 입력 기반이 된다.



\- Saju

\- Astrology

\- 5 Pillars Research

\- Myung-Gung Research

\- Compatibility

\- Date Selection

