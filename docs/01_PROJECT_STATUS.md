\# Destiny — Project Status



> Version: 1.0  

> Status: Phase 1 — Project Diagnosis \& Architecture  

> Principle: Computer calculates, AI interprets.



\---



\## 1. Project Vision



Destiny는 전통적인 운명·점술 체계와 현대적인 AI 기술을 결합한 글로벌 분석 플랫폼을 목표로 한다.



초기에는 한국의 사주·명리학을 중심으로 MVP를 구축하고, 검증과 서비스 경험을 축적하면서 국가 및 점술 체계를 단계적으로 확장한다.



예상 확장 순서:



Korea → Japan → China → India / Thailand / Vietnam / Southeast Asia → USA → Europe → Global



장기적으로 다음 체계를 통합할 수 있다.



\- 사주 / 명리학

\- 궁합

\- 택일

\- 토정비결

\- 주역

\- 서양 점성술

\- 타로

\- Twin Flames

\- 수비학

\- 국가별 전통 점술 체계



\---



\## 2. Core Architecture Principle



Destiny의 핵심 원칙:



> 계산 가능한 사실을 LLM에게 계산시키지 않는다.



기본 구조:



Birth Data  

↓  

Birth Engine  

↓  

Deterministic Destiny Engine  

↓  

Knowledge / RAG  

↓  

Interpretation LLM  

↓  

User Experience



역할을 다음과 같이 분리한다.



\### Birth Engine



사용자의 출생정보를 보존하고 표준화한다.



\- 양력 / 음력

\- 윤달

\- 생년월일

\- 출생시간

\- 시간 정밀도

\- 출생지역

\- 좌표

\- 시간대

\- 입력 신뢰도



\### Destiny Engine



규칙에 따라 계산 가능한 결과를 생성한다.



LLM이 계산 결과를 임의로 생성하지 않는다.



\### Knowledge Engine



전통 문헌, 허가된 자료, Public Domain 자료 및 자체 구축 지식을 검색·제공한다.



\### Interpretation Engine



계산 결과와 Knowledge Engine의 근거를 받아 사용자에게 이해하기 쉬운 형태로 해석한다.



\---



\## 3. Current Development Tracks



\### Production Track



현재 최우선 개발 대상:



\*\*Korea MVP — Traditional Four Pillars / 사주팔자\*\*



우선 정확하고 검증 가능한 전통 사주 계산 체계를 구축한다.



\### Research Track



Production MVP와 분리하여 연구한다.



\- 5주10자

\- 분주(分柱) 규칙

\- 명궁

\- 출생 공간 좌표

\- 천문학적 계산

\- 혼천의 기반 시각화

\- 고해상도 출생시간 연구



실험적 방법을 전통 명리학의 확립된 방법인 것처럼 표현하지 않는다.



\---



\## 4. Project Status Dashboard



Legend:



\- 🟢 Good / Defined

\- 🟡 In Progress / Needs Validation

\- 🔴 Not Ready / Major Work Required



| # | Area | Status | Notes |

|---|---|---|---|

| 1 | Service Vision | 🟢 | Global AI destiny platform |

| 2 | Korea MVP | 🟡 | Scope specification required |

| 3 | Divination Systems | 🟡 | Long-term systems identified |

| 4 | Calculation Engine | 🔴 | Production engine not implemented |

| 5 | Knowledge Sources | 🔴 | Inventory and rights classification underway |

| 6 | AI Interpretation | 🟡 | Architecture direction defined |

| 7 | Multi-System Integration | 🔴 | Future phase |

| 8 | Database | 🔴 | Schema not finalized |

| 9 | System Architecture | 🔴 | Design phase |

| 10 | Development Environment | 🟡 | GitHub repository initialized |

| 11 | Validation | 🔴 | Test corpus required |

| 12 | UX/UI | 🔴 | Production UX not designed |

| 13 | Monetization | 🟡 | Direction exists, not finalized |

| 14 | Marketing | 🟢 | Country-specific hook strategy established |

| 15 | Privacy / Security | 🔴 | Formal specification required |

| 16 | Legal / Policy | 🔴 | Rights investigation underway |

| 17 | Multilingual | 🔴 | Future architecture required |

| 18 | Japan Expansion | 🟡 | Long-term plan |

| 19 | China Expansion | 🟡 | Long-term plan |

| 20 | Southeast Asia Expansion | 🟡 | Long-term plan |

| 21 | US / Western Expansion | 🟡 | Astrology / Tarot candidates |

| 22 | Global Platform | 🟡 | Long-term vision |

| 23 | AI Collaboration | 🟢 | Product Owner + ChatGPT + Claude model |



\---



\## 5. Birth Data Policy



사용자의 원래 입력값을 절대로 잃지 않는다.



처리 구조:



Raw Input  

↓  

Normalized Birth Profile  

↓  

Calendar / Astronomy Calculation  

↓  

Divination-specific Calculation



예:



사용자가 음력 생일을 입력했다면 처음부터 양력으로 덮어쓰지 않는다.



다음 정보를 각각 보존한다.



\- raw calendar type

\- raw date

\- leap month status

\- raw birth time

\- normalized datetime

\- birthplace label

\- normalized location

\- latitude / longitude

\- timezone

\- precision

\- confidence

\- conversion source



핵심 원칙:



> 모르는 것을 AI가 채워 넣지 않는다.



정보가 불확실하면 `unknown`, 후보값 또는 confidence 형태로 보존한다.



\---



\## 6. Time Precision Model



출생정보 정밀도에 따라 제공 가능한 분석을 구분한다.



\### Date only



부분적인 사주 분석.



\### Traditional birth hour / 시진



전통적인 4주8자 분석.



\### Minute-level birth time



실험적인 5주10자 연구 가능.



\### Minute + Birthplace



5주10자 연구와 별도의 공간/천문학적 명궁 연구 가능.



더 높은 입력 정밀도가 반드시 더 높은 점술적 정확성을 의미한다고 주장하지 않는다.



\---



\## 7. Day Boundary / Zi Hour



야자시·조자시 문제는 단일 정답으로 고정하지 않는다.



예상 Calculation Profile:



\- `midnight`

\- `zi\_hour\_23`



향후 학파 또는 계산 프로파일에 따라 선택 가능하도록 설계한다.



Raw birth time과 계산에 사용된 시간, day-boundary rule을 모두 기록한다.



\---



\## 8. Existing Software Assets



\### Byeolha



Current status:



\*\*🟡 Reference Prototype / Rights confirmation pending\*\*



Byeolha는 Production Core가 아니다.



활용 가능 영역:



\- 기능 아이디어

\- Prototype 분석

\- UX 참고

\- 비교 테스트



현재 확인된 주의사항:



\- Byeolha 브랜드는 사용하지 않는다.

\- 기존 GPT prompt는 Production에서 재사용하지 않는다.

\- 고유 loading message 및 설명 문구는 재작성한다.

\- 기존 계산 로직은 Production 정답으로 간주하지 않는다.

\- 외부 라이브러리의 라이선스는 별도로 확인한다.



특히 기존 계산에는 단순화된 규칙이 존재하므로 독립적인 검증이 필요하다.



Production Core는 Destiny specification을 기준으로 독립 구현한다.



\---



\## 9. Byeolha Code Provenance Audit



Status:



\*\*🟡 Open\*\*



확인 대상:



\- 브랜드 문자열

\- GPT prompt

\- UI 문구

\- 일간 설명

\- 대운 및 조언 문구

\- HTML / CSS

\- 함수 구조

\- 계산 코드

\- 데이터 테이블

\- 외부 라이브러리



Byeolha 배포자에게 다음 이용범위를 문의한 상태다.



\- 수정

\- 소스코드 활용

\- 상업적 이용

\- 출처표시

\- 재배포

\- 기타 라이선스 조건



답변을 증빙자료로 보관한다.



답변을 기다리는 동안 Destiny 개발은 중단하지 않는다.



\---



\## 10. Orrery



Project:



Orrery — 혼천의



Current status:



\*\*🟢 Research / Validation Reference\*\*



License:



\*\*AGPL-3.0-only\*\*



Policy:



Orrery를 proprietary Production Core에 직접 포함하지 않는다.



주요 활용 목적:



\- 사주 결과 비교

\- 절기 검증

\- 야자시 / 조자시 비교

\- 대운 비교

\- edge case 탐색

\- 테스트 oracle 후보 비교



Validation concept:



BirthProfile Test Dataset  

↓  

Destiny Engine ↔ Orrery  

↓  

Comparator  

↓  

Difference Analysis



Orrery와 결과가 다르다고 해서 Orrery를 자동으로 정답으로 간주하지 않는다.



차이가 발생한 계산 규칙의 근거를 조사한다.



\---



\## 11. Knowledge Architecture



Knowledge 자료를 두 영역으로 분리한다.



\### Research Library



연구·비교·개념 조사 목적으로 사용할 수 있는 자료.



저작권이 불명확한 자료도 연구 목적으로 분류될 수 있으나 Production RAG에는 자동으로 들어가지 않는다.



\### Production Knowledge Base



다음 조건을 만족하는 자료만 후보가 된다.



\- Public Domain

\- 명확한 Open License

\- 저작권자의 명시적 허가

\- 공공·공개 데이터

\- 자체 작성한 구조화 지식



\---



\## 12. Current Knowledge Assets



\### 명리학 Archive



Status:



\*\*🟡 Research Library\*\*



출처 중 하나:



동의명리학 東醫命理學(대한동의명학회)



포함 가능 영역:



\- 명리학

\- 주역

\- 역학

\- 고전

\- 기타 관련 자료



현재 카페 운영자에게 DB / AI / RAG / 상업적 이용 가능 범위를 문의 중이다.



운영자의 허가가 있더라도 외부 저자·출판사의 자료는 별도 권리 검토가 필요하다.



\---



\### Western Astrology / Tarot Archive



Status:



\*\*🟡 Research Library\*\*



자료별 출처와 저작권을 확인한 뒤 Production 후보를 분리한다.



\---



\## 13. Public Domain / Production Candidates



\### A. E. Waite — The Pictorial Key to the Tarot



Source:



Internet Archive



Status:



\*\*🟢 Production Knowledge candidate\*\*



Use cases:



\- Rider-Waite-Smith tarot knowledge

\- card meanings

\- symbolism

\- structured tarot knowledge



현대 한국어 번역이나 현대 해설 자료가 추가될 경우 별도의 저작권을 확인한다.



\---



\### Ptolemy — Tetrabiblos



Source:



Project Gutenberg



Gutenberg eBook #70850



English translation:



J. M. Ashmand



Status:



\*\*🟢 Production Knowledge candidate\*\*



Use cases:



\- classical Western astrology

\- historical astrology concepts

\- astrology knowledge genealogy



Production 적용 전 서비스 대상 국가별 권리 상태를 최종 확인한다.



\---



\## 14. Knowledge Provenance



각 Knowledge Asset에 다음 metadata를 기록한다.



\- title

\- author

\- translator

\- edition

\- publication year

\- source

\- source URL

\- acquisition source

\- language

\- category

\- copyright status

\- license

\- permission evidence

\- reliability

\- calculation relevance

\- Research usability

\- Production RAG usability



Knowledge Asset Registry를 별도로 관리한다.



\---



\## 15. Legal \& IP



Destiny는 저작권 및 라이선스를 개발 초기부터 관리한다.



확인 대상:



\- source code

\- books

\- translations

\- commentaries

\- images

\- tarot artwork

\- datasets

\- prompts

\- UI content

\- third-party libraries



Public availability를 자유로운 상업적 이용 허가로 간주하지 않는다.



\---



\## 16. Privacy



향후 다음 데이터가 개인정보 또는 민감한 사용자 데이터가 될 수 있음을 전제로 설계한다.



\- 생년월일

\- 출생시간

\- 출생지역

\- 계정정보

\- 상담내용

\- AI conversation

\- payment-related records



원칙:



\- Data minimization

\- Purpose limitation

\- Retention policy

\- User deletion

\- Access control

\- Auditability



\---



\## 17. AI Data Governance



외부 LLM에 불필요한 개인정보를 전달하지 않는다.



가능한 구조:



User Identity  

↓  

Internal User ID



Birth / Destiny Data  

↓  

Calculation Result



LLM에는 필요한 계산 결과와 최소한의 context만 전달한다.



사용자 identity와 점술 분석 데이터를 가능한 범위에서 분리한다.



\---



\## 18. Security



Production에서 요구되는 주요 영역:



\- TLS

\- secret management

\- password hashing

\- access control

\- admin RBAC

\- privacy-safe logging

\- backup

\- disaster recovery

\- incident response

\- dependency security

\- API rate limiting



API Key, password 및 secret은 Git repository에 저장하지 않는다.



\---



\## 19. Payment Security



Raw card information을 Destiny 서버에서 직접 저장하지 않는 방향을 기본으로 한다.



검증된 PG / payment provider의 hosted 또는 tokenized payment 방식을 우선 검토한다.



향후 확인 대상:



\- Korean PG requirements

\- Electronic Financial Transactions rules

\- E-commerce requirements

\- cancellation

\- refund

\- digital-content conditions

\- settlement protection



\---



\## 20. Service Safety Policy



운명·점술 결과를 다음 전문 영역의 확정적 판단으로 제공하지 않는다.



\- medical diagnosis

\- legal advice

\- investment advice



사용자에게 오락·자기성찰·문화적 콘텐츠의 성격을 명확하게 전달할 수 있는 UX 및 정책을 설계한다.



\---



\## 21. Experimental Five-Pillar Research



Traditional Four Pillars:



\*\*4주8자\*\*



Experimental concept:



\*\*5주10자\*\*



목적:



분 단위 출생시간을 활용한 고해상도 시간 좌표 연구.



주의:



5주10자는 전통적으로 확립된 표준 사주 체계로 표현하지 않는다.



연구 대상:



\- historical precedents

\- 分刻 / minute concepts

\- candidate formulas

\- consistency

\- twin birth cases

\- explanatory usefulness

\- empirical comparison



\---



\## 22. Myung-Gung / Spatial Research



출생지는 시간과 다른 공간 차원으로 취급한다.



Concept:



4주8자  

→ traditional temporal coordinates



5주10자  

→ experimental high-resolution temporal coordinates



명궁  

→ spatial / astronomical coordinates



Combined concept:



\*\*WHEN × WHERE\*\*



출생지 기반 계산에는 향후 다음 요소를 검토한다.



\- latitude

\- longitude

\- timezone

\- historical timezone

\- local solar time

\- true solar time

\- astronomical position



\---



\## 23. Development Environment



Official repository:



`dk1347/destiny`



Local workspace:



`D:\\Users\\dk134\\Documents\\git\\destiny`



Current structure:



destiny/  

├── docs/  

├── research/  

├── src/  

├── tests/  

├── .gitignore  

└── README.md



GitHub를 프로젝트의 공식 변경 이력 및 공통 기준 저장소로 사용한다.



\---



\## 24. AI Collaboration Model



\### Product Owner



Responsibilities:



\- vision

\- priorities

\- final decisions

\- business direction



\### ChatGPT



Responsibilities:



\- strategy

\- architecture

\- specifications

\- research

\- Knowledge / RAG design

\- validation design

\- project coordination

\- cross-review



\### Claude



Responsibilities:



\- implementation

\- code review

\- refactoring

\- testing

\- technical critique



Principle:



> AI outputs are cross-checked rather than treated as unquestioned authority.



\---



\## 25. Planned Documentation



The following documents will become the core project specification.



1\. `01\_PROJECT\_STATUS.md`

2\. `02\_KOREA\_MVP\_SCOPE.md`

3\. `03\_BIRTH\_PROFILE\_SPEC.md`

4\. `04\_SAJU\_CALCULATION\_SPEC.md`

5\. `05\_KNOWLEDGE\_RAG\_DESIGN.md`

6\. `06\_SYSTEM\_ARCHITECTURE.md`

7\. `07\_TEST\_VALIDATION\_PLAN.md`

8\. `08\_BACKLOG\_PRIORITY.md`

9\. `09\_RND\_5PILLARS\_MYUNGGUNG.md`

10\. `10\_CLAUDE\_HANDOFF.md`



\---



\## 26. Immediate Priorities



\### P0 — Foundation



\- Korea MVP scope

\- BirthProfile specification

\- Korean Saju calculation specification

\- source / copyright inventory

\- validation methodology



\### P1 — Architecture



\- system architecture

\- API boundaries

\- database model

\- Knowledge / RAG architecture

\- LLM provider abstraction



\### P2 — Implementation



\- Birth Engine

\- Saju Calculation Engine

\- validation tests

\- Knowledge retrieval

\- Interpretation Engine

\- Web MVP



\### Research Track



\- 5주10자

\- 명궁

\- astronomy

\- 혼천의 visualization



Research Track은 Korea MVP 출시를 방해하지 않도록 Production Track과 분리한다.



\---



\## 27. Current Blocking Issues



현재 전체 프로젝트를 중단시키는 Blocking Issue는 없다.

### 2026-09-16 implementation snapshot

- Production-verified deterministic calculation is available for the core
  tables, verified solar-term coverage, month/hour stems, compact hidden
  stems, ten gods, and structural relations.
- The guarded internal API provides four-pillar calculation, a safe date-only
  three-pillar result, and structural annual-cycle facts.
- A React/TypeScript internal web MVP covers known-time and date-only input,
  calculated-result display, and annual-cycle display when birth time is known.
- The API has explicit browser-origin configuration and a non-sensitive
  `GET /healthz` liveness check. CI validates tests, builds, and an installed
  wheel on Python 3.11 through 3.13.
- Public-content assets are drafts only; no content has been published.



다음 항목은 병렬 확인 중이다.



\- Byeolha 이용 허가

\- 동의명리학 자료 이용 허가

\- Knowledge archive 출처 분류

\- Public Domain 자료의 국가별 Production 권리 확인



권리 확인이 끝나지 않은 자료는 Production에 포함하지 않는다.



\---



\## 28. Next Milestone



### Integration MVP hardening

1. Use the approved Render internal-preview shape only after the account and
   exact preview origin are supplied; configure that exact allowed origin then.
2. Run an end-to-end browser review against the non-local preview API,
   including known-time, date-only, and solar-term-boundary recovery paths.
3. Select the public custom domain and privacy-preserving CTA contract before
   a public calculator or waitlist is exposed.
4. Keep Daewoon and AI interpretation outside the first calculator release
   until their separate rule, safety, and evaluation gates are complete.



\---



\## Decision Log



\### D-001



Korea-first MVP 전략 채택.



\### D-002



계산 Engine과 LLM Interpretation을 분리한다.



\### D-003



Birth raw data를 보존하고 normalized data와 분리한다.



\### D-004



Byeolha를 Reference Prototype으로 분류한다.



\### D-005



Orrery를 AGPL Research / Validation Reference로 분류한다.



\### D-006



Research Library와 Production Knowledge Base를 분리한다.



\### D-007



5주10자 및 명궁은 Production MVP와 분리된 Research Track으로 관리한다.



\### D-008



GitHub `destiny`를 프로젝트의 공식 개발 저장소로 사용한다.



\### D-009



ChatGPT와 Claude의 결과를 상호 교차검증한다.



\### D-010



Copyright, Privacy, Security 및 Payment Compliance를 개발 후반 작업이 아니라 Architecture 단계부터 관리한다.

