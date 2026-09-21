export type DayBoundaryPolicy = 'midnight' | 'jasi' | 'splitJasi';

export interface SolarCorrectionResult {
  utcDate: Date;
  civilKST: Date;
  solarDate: Date;
  offsetMinutes: number;
  correctionLine: string;
}

export function calculateEoT(date: Date): number {
  const startOfYear = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  const dayOfYear = Math.floor((date.getTime() - startOfYear.getTime()) / 86400000) + 1;
  const B = (360 / 365) * (dayOfYear - 81) * (Math.PI / 180);
  return 9.87 * Math.sin(2 * B) - 7.53 * Math.cos(B) - 1.5 * Math.sin(B);
}

export function resolveSolarTime(
  localDateTimeStr: string,
  longitude: number = 126.978,
  applyTrueSolar: boolean = true
): SolarCorrectionResult {
  const inputDate = new Date(localDateTimeStr);
  const longitudeCorrectionMin = (longitude - 135.0) * 4;
  const eotMin = applyTrueSolar ? calculateEoT(inputDate) : 0;
  const totalCorrectionMin = applyTrueSolar ? (longitudeCorrectionMin + eotMin) : 0;

  const solarDate = new Date(inputDate.getTime() + totalCorrectionMin * 60 * 1000);
  const sign = totalCorrectionMin >= 0 ? '+' : '';
  const correctionLine = `입력: ${localDateTimeStr} | 경도보정: ${longitudeCorrectionMin.toFixed(2)}분 | 균시차: ${eotMin.toFixed(2)}분 | 총보정: ${sign}${totalCorrectionMin.toFixed(2)}분 -> 진태양시: ${solarDate.toISOString()}`;

  return {
    utcDate: inputDate,
    civilKST: inputDate,
    solarDate,
    offsetMinutes: totalCorrectionMin,
    correctionLine,
  };
}
