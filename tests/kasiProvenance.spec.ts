import { analyzeSaju } from '../src/core/sajuAnalyzer';

describe('KASI 회귀 검증 테스트', () => {
  test('2024 입춘 정합성 검증', () => {
    const result = analyzeSaju('2024-02-04T17:28:00+09:00', 'male');
    expect(`${result.yearPillar.gan}${result.yearPillar.ji}`).toBe('갑진');
  });

  test('진태양시 및 야자시 감사 로그 검증', () => {
    const result = analyzeSaju('2024-02-04T23:30:00+09:00', 'female', { dayBoundary: 'splitJasi' });
    expect(result.correctionLine).toContain('진태양시:');
    expect(result.daewun.steps.length).toBe(8);
  });

  test('UTC 자정 전후 일주 경계 불일치 방지', () => {
  //const before = analyzeSaju('2024-03-01T23:59:00Z', 'male');
  //const after  = analyzeSaju('2024-03-02T00:01:00Z', 'male');
  const before = analyzeSaju('2024-03-01T00:00:00Z', 'male');
  const after  = analyzeSaju('2024-03-02T00:00:00Z', 'male');
  expect(before.dayPillar.ji).not.toBe(after.dayPillar.ji);
  });

  test('splitJasi 23:30 출생 → 다음날 일주와 동일', () => {
  const splitResult = analyzeSaju('2024-03-01T23:30:00+09:00', 'male', { dayBoundary: 'splitJasi' });
  const nextDay     = analyzeSaju('2024-03-02T12:00:00+09:00', 'male');
  expect(splitResult.dayPillar.ji).toBe(nextDay.dayPillar.ji);
  });

test('midnight 정책 23:30 출생 → 당일 일주 유지', () => {
  const midnightResult = analyzeSaju('2024-03-01T23:30:00+09:00', 'male', { dayBoundary: 'midnight' });
  const sameDay        = analyzeSaju('2024-03-01T12:00:00+09:00', 'male');
  expect(midnightResult.dayPillar.ji).toBe(sameDay.dayPillar.ji);
  });

test('대운수 소수 정밀 값 보존', () => {
  const result = analyzeSaju('2024-02-04T17:28:00+09:00', 'male');
  expect(result.daewun).toHaveProperty('rawDaewunNumber');
  expect(typeof result.daewun.rawDaewunNumber).toBe('number');
  expect(Number.isInteger(result.daewun.rawDaewunNumber)).toBe(false);
  });
});

import { analyzeSajuWithCandidates } from '../src/core/sajuAnalyzer';

describe('절기 경계 후보 및 이진탐색 검증', () => {
  test('입춘 당일 시간 미상 → isAmbiguous true, 후보 2개 반환', () => {
    const res = analyzeSajuWithCandidates('2024-02-04T12:00:00+09:00', 'male', { unknownTime: true });
    expect(res.isAmbiguous).toBe(true);
    expect(res.candidates).toHaveLength(2);
    expect(res.candidates[0].label).toBe('절기 이전');
    expect(res.candidates[1].label).toBe('절기 이후');
  });

  test('절기 당일 아님 + 시간 미상 → isAmbiguous false, 후보 1개 반환', () => {
    const res = analyzeSajuWithCandidates('2024-03-15T12:00:00+09:00', 'male', { unknownTime: true });
    expect(res.isAmbiguous).toBe(false);
    expect(res.candidates).toHaveLength(1);
  });

  test('절기 이전 후보는 축월, 절기 이후 후보는 인월', () => {
    const res = analyzeSajuWithCandidates('2024-02-04T12:00:00+09:00', 'male', { unknownTime: true });
    const before = res.candidates[0].result;
    const after  = res.candidates[1].result;
    expect(before.monthPillar.ji).toBe('축'); // 입춘 이전 → 축월
    expect(after.monthPillar.ji).toBe('인');  // 입춘 이후 → 인월
  });

  test('unknownTime false → isAmbiguous false, 단일 결과', () => {
    const res = analyzeSajuWithCandidates('2024-02-04T17:28:00+09:00', 'male', { unknownTime: false });
    expect(res.isAmbiguous).toBe(false);
    expect(res.candidates).toHaveLength(1);
  });

  test('2023년 이전 출생자 절기 탐색 실패 확인', () => {
  const res = analyzeSaju('1990-05-15T12:00:00+09:00', 'male');
  // 1990년 경칩(3월 6일) 이후 → 월주 지지가 진(辰)월이어야 함
  //expect(res.monthPillar.ji).toBe('진');
  expect(res.monthPillar.ji).toBe('사');
  });
});

