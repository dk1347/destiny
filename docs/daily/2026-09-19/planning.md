# Daily Planning - 2026-09-19

## 1. Goal
`destiny` 메인 저장소의 백엔드 기초 모듈인 **Birth Engine(만세력/생년월일 변환 계산기)**의 핵심 기반 라이브러리 및 단위 테스트 환경 구축.

## 2. Tasks
1. Python 환경 기반 만세력 계산용 율리우스일(Julian Day Number, JDN) 변환 모듈 구현 (`src/engine/jdn.py`)
2. JDN 변환 정확도 검증을 위한 `pytest` 단위 테스트 작성 (`tests/test_jdn.py`)
3. 로컬 VM Runner 환경에서의 자동 빌드 및 테스트 수행 리포트 생성 (`docs/implementation/2026-09-19-report.md`)