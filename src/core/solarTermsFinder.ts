import { SolarTermEntry, EMBEDDED_SOLAR_TERMS } from './solarTermsData';

export interface SolarTermMatch {
  currentMajorTerm: SolarTermEntry;
  nextMajorTerm: SolarTermEntry;
  ipchunTerm: SolarTermEntry;
}

/** utcTime 기준 오름차순 정렬된 배열에서 targetUtcTime 이하인 마지막 인덱스 반환 */
function binarySearchFloor(arr: SolarTermEntry[], targetUtcTime: number): number {
  let low = 0;
  let high = arr.length - 1;
  let matchIdx = -1;
  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (arr[mid].utcTime <= targetUtcTime) {
      matchIdx = mid;
      low = mid + 1;
    } else {
      high = mid - 1;
    }
  }
  return matchIdx;
}

export function findSolarTerms(targetUtcTime: number, table: SolarTermEntry[] = EMBEDDED_SOLAR_TERMS): SolarTermMatch {
  const majorTerms = table.filter(t => t.isMajor);
  const ipchunTerms = table.filter(t => t.name === '입춘');

  const majorIdx = binarySearchFloor(majorTerms, targetUtcTime);
  const currentMajorTerm = majorIdx !== -1 ? majorTerms[majorIdx] : majorTerms[0];
  const nextMajorTerm = (majorIdx !== -1 && majorIdx < majorTerms.length - 1)
    ? majorTerms[majorIdx + 1]
    : majorTerms[majorTerms.length - 1];

  const ipchunIdx = binarySearchFloor(ipchunTerms, targetUtcTime);
  const ipchunTerm = ipchunIdx !== -1 ? ipchunTerms[ipchunIdx] : ipchunTerms[0];

  return { currentMajorTerm, nextMajorTerm, ipchunTerm };
}

/** 절기 당일 여부 판단: targetUtcTime이 term 당일(UTC 기준 같은 날)인지 확인 */
export function isSameUtcDay(targetUtcTime: number, termUtcTime: number): boolean {
  const t = new Date(targetUtcTime);
  const s = new Date(termUtcTime);
  return (
    t.getUTCFullYear() === s.getUTCFullYear() &&
    t.getUTCMonth() === s.getUTCMonth() &&
    t.getUTCDate() === s.getUTCDate()
  );
}