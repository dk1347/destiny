export interface SolarTermEntry {
  name: string;
  utcTime: number;
  solarLongitude: number;
  isMajor: boolean;
  monthJiIdx?: number;
}

export const EMBEDDED_SOLAR_TERMS: SolarTermEntry[] = [
  { name: '소한', utcTime: new Date('2024-01-06T04:49:00Z').getTime(), solarLongitude: 285, isMajor: true, monthJiIdx: 1 },
  { name: '입춘', utcTime: new Date('2024-02-04T08:27:00Z').getTime(), solarLongitude: 315, isMajor: true, monthJiIdx: 2 },
  { name: '우수', utcTime: new Date('2024-02-19T04:13:00Z').getTime(), solarLongitude: 330, isMajor: false },
  { name: '경칩', utcTime: new Date('2024-03-05T02:23:00Z').getTime(), solarLongitude: 345, isMajor: true, monthJiIdx: 3 },
  { name: '입춘', utcTime: new Date('2025-02-03T14:10:00Z').getTime(), solarLongitude: 315, isMajor: true, monthJiIdx: 2 },
  { name: '입춘', utcTime: new Date('2026-02-03T19:58:00Z').getTime(), solarLongitude: 315, isMajor: true, monthJiIdx: 2 },
];
