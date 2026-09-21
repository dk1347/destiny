import { CHEONGAN, JIJI } from './sajuEngine';
import { SolarTermMatch } from './solarTermsFinder';

export type Gender = 'male' | 'female';
export type Direction = 'forward' | 'backward';

export interface DaewunStep {
  step: number;
  startAge: number;
  gan: string;
  ji: string;
  ganIdx: number;
  jiIdx: number;
}

export function isYangYearGan(yearGanIdx: number): boolean {
  return yearGanIdx % 2 === 0;
}

export function getDaewunDirection(gender: Gender, yearGanIdx: number): Direction {
  const isYang = isYangYearGan(yearGanIdx);
  return gender === 'male' ? (isYang ? 'forward' : 'backward') : (isYang ? 'backward' : 'forward');
}

export function calculateDaewun(
  birthUtcMs: number,
  gender: Gender,
  yearGanIdx: number,
  monthGanIdx: number,
  monthJiIdx: number,
  solarTerms: SolarTermMatch,
  totalSteps: number = 8
) {
  const direction = getDaewunDirection(gender, yearGanIdx);
  const timeDiffMs = direction === 'forward'
    ? solarTerms.nextMajorTerm.utcTime - birthUtcMs
    : birthUtcMs - solarTerms.currentMajorTerm.utcTime;

  const totalDays = Math.abs(timeDiffMs) / (1000 * 60 * 60 * 24);
  let daewunNum = Math.round(totalDays / 3);
  if (daewunNum < 1) daewunNum = 1;
  if (daewunNum > 10) daewunNum = 10;

  const steps: DaewunStep[] = [];
  const delta = direction === 'forward' ? 1 : -1;

  for (let i = 1; i <= totalSteps; i++) {
    const nextGanIdx = (monthGanIdx + delta * i + 100) % 10;
    const nextJiIdx = (monthJiIdx + delta * i + 120) % 12;
    steps.push({
      step: i,
      startAge: daewunNum + (i - 1) * 10,
      gan: CHEONGAN[nextGanIdx],
      ji: JIJI[nextJiIdx],
      ganIdx: nextGanIdx,
      jiIdx: nextJiIdx,
    });
  }

  return { direction, daewunNumber: daewunNum, steps };
}
