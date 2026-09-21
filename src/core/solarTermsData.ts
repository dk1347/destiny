export interface SolarTermEntry {
  name: string;
  utcTime: number;
  solarLongitude: number;
  isMajor: boolean;
  monthJiIdx?: number;
}

export const EMBEDDED_SOLAR_TERMS: SolarTermEntry[] = [
  // ── 2024년 ──────────────────────────────────────────
  { name: '소한',  utcTime: new Date('2024-01-06T04:49:00Z').getTime(), solarLongitude: 285, isMajor: true,  monthJiIdx: 1  },
  { name: '대한',  utcTime: new Date('2024-01-20T22:07:00Z').getTime(), solarLongitude: 300, isMajor: false },
  { name: '입춘',  utcTime: new Date('2024-02-04T08:27:00Z').getTime(), solarLongitude: 315, isMajor: true,  monthJiIdx: 2  },
  { name: '우수',  utcTime: new Date('2024-02-19T04:13:00Z').getTime(), solarLongitude: 330, isMajor: false },
  { name: '경칩',  utcTime: new Date('2024-03-05T02:23:00Z').getTime(), solarLongitude: 345, isMajor: true,  monthJiIdx: 3  },
  { name: '춘분',  utcTime: new Date('2024-03-20T03:06:00Z').getTime(), solarLongitude: 0,   isMajor: false },
  { name: '청명',  utcTime: new Date('2024-04-04T07:02:00Z').getTime(), solarLongitude: 15,  isMajor: true,  monthJiIdx: 4  },
  { name: '곡우',  utcTime: new Date('2024-04-19T13:59:00Z').getTime(), solarLongitude: 30,  isMajor: false },
  { name: '입하',  utcTime: new Date('2024-05-05T00:10:00Z').getTime(), solarLongitude: 45,  isMajor: true,  monthJiIdx: 5  },
  { name: '소만',  utcTime: new Date('2024-05-20T13:00:00Z').getTime(), solarLongitude: 60,  isMajor: false },
  { name: '망종',  utcTime: new Date('2024-06-05T04:10:00Z').getTime(), solarLongitude: 75,  isMajor: true,  monthJiIdx: 6  },
  { name: '하지',  utcTime: new Date('2024-06-21T20:51:00Z').getTime(), solarLongitude: 90,  isMajor: false },
  { name: '소서',  utcTime: new Date('2024-07-06T14:20:00Z').getTime(), solarLongitude: 105, isMajor: true,  monthJiIdx: 7  },
  { name: '대서',  utcTime: new Date('2024-07-22T07:44:00Z').getTime(), solarLongitude: 120, isMajor: false },
  { name: '입추',  utcTime: new Date('2024-08-07T01:09:00Z').getTime(), solarLongitude: 135, isMajor: true,  monthJiIdx: 8  },
  { name: '처서',  utcTime: new Date('2024-08-22T15:55:00Z').getTime(), solarLongitude: 150, isMajor: false },
  { name: '백로',  utcTime: new Date('2024-09-07T04:11:00Z').getTime(), solarLongitude: 165, isMajor: true,  monthJiIdx: 9  },
  { name: '추분',  utcTime: new Date('2024-09-22T13:44:00Z').getTime(), solarLongitude: 180, isMajor: false },
  { name: '한로',  utcTime: new Date('2024-10-08T01:00:00Z').getTime(), solarLongitude: 195, isMajor: true,  monthJiIdx: 10 },
  { name: '상강',  utcTime: new Date('2024-10-23T04:15:00Z').getTime(), solarLongitude: 210, isMajor: false },
  { name: '입동',  utcTime: new Date('2024-11-07T04:20:00Z').getTime(), solarLongitude: 225, isMajor: true,  monthJiIdx: 11 },
  { name: '소설',  utcTime: new Date('2024-11-22T01:56:00Z').getTime(), solarLongitude: 240, isMajor: false },
  { name: '대설',  utcTime: new Date('2024-12-06T23:17:00Z').getTime(), solarLongitude: 255, isMajor: true,  monthJiIdx: 0  },
  { name: '동지',  utcTime: new Date('2024-12-21T17:20:00Z').getTime(), solarLongitude: 270, isMajor: false },

  // ── 2025년 ──────────────────────────────────────────
  { name: '소한',  utcTime: new Date('2025-01-05T10:33:00Z').getTime(), solarLongitude: 285, isMajor: true,  monthJiIdx: 1  },
  { name: '대한',  utcTime: new Date('2025-01-20T03:59:00Z').getTime(), solarLongitude: 300, isMajor: false },
  { name: '입춘',  utcTime: new Date('2025-02-03T14:10:00Z').getTime(), solarLongitude: 315, isMajor: true,  monthJiIdx: 2  },
  { name: '우수',  utcTime: new Date('2025-02-18T10:06:00Z').getTime(), solarLongitude: 330, isMajor: false },
  { name: '경칩',  utcTime: new Date('2025-03-05T08:07:00Z').getTime(), solarLongitude: 345, isMajor: true,  monthJiIdx: 3  },
  { name: '춘분',  utcTime: new Date('2025-03-20T09:01:00Z').getTime(), solarLongitude: 0,   isMajor: false },
  { name: '청명',  utcTime: new Date('2025-04-04T12:48:00Z').getTime(), solarLongitude: 15,  isMajor: true,  monthJiIdx: 4  },
  { name: '곡우',  utcTime: new Date('2025-04-19T19:56:00Z').getTime(), solarLongitude: 30,  isMajor: false },
  { name: '입하',  utcTime: new Date('2025-05-05T05:57:00Z').getTime(), solarLongitude: 45,  isMajor: true,  monthJiIdx: 5  },
  { name: '소만',  utcTime: new Date('2025-05-20T18:54:00Z').getTime(), solarLongitude: 60,  isMajor: false },
  { name: '망종',  utcTime: new Date('2025-06-05T10:05:00Z').getTime(), solarLongitude: 75,  isMajor: true,  monthJiIdx: 6  },
  { name: '하지',  utcTime: new Date('2025-06-21T02:42:00Z').getTime(), solarLongitude: 90,  isMajor: false },
  { name: '소서',  utcTime: new Date('2025-07-07T20:05:00Z').getTime(), solarLongitude: 105, isMajor: true,  monthJiIdx: 7  },
  { name: '대서',  utcTime: new Date('2025-07-22T13:29:00Z').getTime(), solarLongitude: 120, isMajor: false },
  { name: '입추',  utcTime: new Date('2025-08-07T07:01:00Z').getTime(), solarLongitude: 135, isMajor: true,  monthJiIdx: 8  },
  { name: '처서',  utcTime: new Date('2025-08-22T21:34:00Z').getTime(), solarLongitude: 150, isMajor: false },
  { name: '백로',  utcTime: new Date('2025-09-07T09:52:00Z').getTime(), solarLongitude: 165, isMajor: true,  monthJiIdx: 9  },
  { name: '추분',  utcTime: new Date('2025-09-22T19:19:00Z').getTime(), solarLongitude: 180, isMajor: false },
  { name: '한로',  utcTime: new Date('2025-10-08T06:41:00Z').getTime(), solarLongitude: 195, isMajor: true,  monthJiIdx: 10 },
  { name: '상강',  utcTime: new Date('2025-10-23T09:51:00Z').getTime(), solarLongitude: 210, isMajor: false },
  { name: '입동',  utcTime: new Date('2025-11-07T10:04:00Z').getTime(), solarLongitude: 225, isMajor: true,  monthJiIdx: 11 },
  { name: '소설',  utcTime: new Date('2025-11-22T07:36:00Z').getTime(), solarLongitude: 240, isMajor: false },
  { name: '대설',  utcTime: new Date('2025-12-07T05:04:00Z').getTime(), solarLongitude: 255, isMajor: true,  monthJiIdx: 0  },
  { name: '동지',  utcTime: new Date('2025-12-21T23:03:00Z').getTime(), solarLongitude: 270, isMajor: false },

  // ── 2026년 입춘 ──────────────────────────────────────
  { name: '입춘',  utcTime: new Date('2026-02-03T19:58:00Z').getTime(), solarLongitude: 315, isMajor: true,  monthJiIdx: 2  },
];
