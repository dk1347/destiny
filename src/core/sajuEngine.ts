import { DayBoundaryPolicy } from './solarTime';

export const CHEONGAN = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];
export const JIJI = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'];

const EPOCH_DATE = new Date(Date.UTC(1900, 0, 1));
const EPOCH_GAN_IDX = 0;
const EPOCH_JI_IDX = 10;

export function getDayPillar(date: Date, offsetDays: number = 0) {
  //const targetUtc = Date.UTC(date.getFullYear(), date.getMonth(), date.getDate());
  const targetUtc = Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate());
  const diffDays = Math.floor((targetUtc - EPOCH_DATE.getTime()) / 86400000) + offsetDays;

  const ganIdx = (EPOCH_GAN_IDX + (diffDays % 10) + 10) % 10;
  const jiIdx = (EPOCH_JI_IDX + (diffDays % 12) + 12) % 12;

  return { gan: CHEONGAN[ganIdx], ji: JIJI[jiIdx], ganIdx, jiIdx };
}

export function getTimePillar(solarDate: Date, dayGanIdx: number, policy: DayBoundaryPolicy) {
  //const hours = solarDate.getHours();
  const hours = solarDate.getUTCHours();
  //const minutes = solarDate.getMinutes();
  const minutes = solarDate.getUTCMinutes();
  const totalMinutes = hours * 60 + minutes;

  let jiIdx = Math.floor(((totalMinutes + 60) % 1440) / 120);
  let targetDayGanIdx = dayGanIdx;

  if (hours === 23) {
    if (policy === 'jasi' || policy === 'splitJasi') {
      targetDayGanIdx = (dayGanIdx + 1) % 10;
    }
  }

  const baseHourGanIdx = ((targetDayGanIdx % 5) * 2) % 10;
  const timeGanIdx = (baseHourGanIdx + jiIdx) % 10;

  return {
    gan: CHEONGAN[timeGanIdx],
    ji: JIJI[jiIdx],
    ganIdx: timeGanIdx,
    jiIdx,
  };
}
