# 03. BirthProfile Specification (출생정보 정규화 규격서)

> **문서 버전**: 1.0.0
> **작성 일자**: 2026년 9월 20일
> **상태**: 확정 (Approved)
> **적용 모듈**: src/destiny_saju/birth/

## 1. 개요 및 설계 철학
사용자로부터 입력받은 출생 정보를 정규화 데이터(NormalizedBirthProfile)로 변환한다.
- 원본 보존: Raw input 불변
- 추측 금지: 모르는 정보는 AI가 임의 추정 금지
- 자동화 우선: 100% 자동 판단 가능한 항목은 보정, 모호하면 명시적 선택 요청

## 2. 데이터 스키마
- RawBirthInput: calendar_type(solar/lunar), birth_year, birth_month, birth_day, birth_time_str, is_leap_month, gender, location_text
- NormalizedBirthProfile: profile_id, raw_input, normalized_utc_timestamp, solar_birth_date, base_timezone, historical_dst_applied, dst_offset_minutes, meridian_offset_minutes, adjusted_solar_time, time_precision, analysis_mode, applied_rule_ids, resolution_status

## 3. 핵심 정규화 정책
1. 윤달 자동 판정: 윤달 없는 달은 false 자동화, 윤달 공존 시 선택 유도(모름 시 평달/윤달 후보 2개 분기)
2. 서머타임(DST) 자동 보정: 1948~1951, 1955~1960, 1987~1988 구간 -60분 자동 보정
3. 표준 자오선 시차 보정: 127.5도 구간(1908~1911, 1954~1961) 0분, 135도 구간(1912~1954, 1961~현재) -30분 자동 보정
4. 시간 미상(Unknown Time): 임의 시간 대입 금지, 3주 분석 모드(analysis_mode=THREE_PILLARS) 전환 및 시주 null 처리
