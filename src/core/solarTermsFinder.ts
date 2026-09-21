import { SolarTermEntry, EMBEDDED_SOLAR_TERMS } from './solarTermsData';

export interface SolarTermMatch {
  currentMajorTerm: SolarTermEntry;
  nextMajorTerm: SolarTermEntry;
  ipchunTerm: SolarTermEntry;
}

export function findSolarTerms(targetUtcTime: number, table: SolarTermEntry[] = EMBEDDED_SOLAR_TERMS): SolarTermMatch {
  const majorTerms = table.filter(t => t.isMajor);
  let low = 0;
  let high = majorTerms.length - 1;
  let matchIdx = -1;

  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (majorTerms[mid].utcTime <= targetUtcTime) {
      matchIdx = mid;
      low = mid + 1;
    } else {
      high = mid - 1;
    }
  }

  const currentMajorTerm = matchIdx !== -1 ? majorTerms[matchIdx] : majorTerms[0];
  const nextMajorTerm = (matchIdx !== -1 && matchIdx < majorTerms.length - 1) ? majorTerms[matchIdx + 1] : majorTerms[majorTerms.length - 1];

  const ipchunTerms = table.filter(t => t.name === '입춘');
  let ipchunIdx = 0;
  for (let i = 0; i < ipchunTerms.length; i++) {
    if (ipchunTerms[i].utcTime <= targetUtcTime) ipchunIdx = i;
    else break;
  }

  return { currentMajorTerm, nextMajorTerm, ipchunTerm: ipchunTerms[ipchunIdx] };
}
