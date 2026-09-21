import { CHEONGAN, JIJI } from './sajuEngine';

export function getYearPillar(solarUtcDate: Date, ipchunUtcDate: Date) {
  let civilYear = solarUtcDate.getUTCFullYear();
  if (solarUtcDate.getTime() < ipchunUtcDate.getTime()) {
    civilYear -= 1;
  }
  const offset = civilYear - 1984;
  const ganIdx = ((offset % 10) + 10) % 10;
  const jiIdx = ((offset % 12) + 12) % 12;

  return { gan: CHEONGAN[ganIdx], ji: JIJI[jiIdx], ganIdx, jiIdx };
}

export function getMonthPillar(yearGanIdx: number, currentMonthJiIdx: number) {
  const monthOrder = (currentMonthJiIdx - 2 + 12) % 12;
  const baseMonthGanIdx = ((yearGanIdx % 5) * 2 + 2) % 10;
  const monthGanIdx = (baseMonthGanIdx + monthOrder) % 10;

  return { gan: CHEONGAN[monthGanIdx], ji: JIJI[currentMonthJiIdx], ganIdx: monthGanIdx, jiIdx: currentMonthJiIdx };
}
