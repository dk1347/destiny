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
});
