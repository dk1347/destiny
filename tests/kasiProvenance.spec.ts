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
});
