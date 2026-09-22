export type Element = '목' | '화' | '토' | '금' | '수';
export type YinYang = '양' | '음';

export const CHEONGAN_META = [
  { char: '갑', element: '목' as Element, yinYang: '양' as YinYang },
  { char: '을', element: '목' as Element, yinYang: '음' as YinYang },
  { char: '병', element: '화' as Element, yinYang: '양' as YinYang },
  { char: '정', element: '화' as Element, yinYang: '음' as YinYang },
  { char: '무', element: '토' as Element, yinYang: '양' as YinYang },
  { char: '기', element: '토' as Element, yinYang: '음' as YinYang },
  { char: '경', element: '금' as Element, yinYang: '양' as YinYang },
  { char: '신', element: '금' as Element, yinYang: '음' as YinYang },
  { char: '임', element: '수' as Element, yinYang: '양' as YinYang },
  { char: '계', element: '수' as Element, yinYang: '음' as YinYang },
];

export const JIJI_META = [
  { char: '자', element: '수', mainGan: 9 },
  { char: '축', element: '토', mainGan: 5 },
  { char: '인', element: '목', mainGan: 0 },
  { char: '묘', element: '목', mainGan: 1 },
  { char: '진', element: '토', mainGan: 4 },
  { char: '사', element: '화', mainGan: 2 },
  { char: '오', element: '화', mainGan: 3 },
  { char: '미', element: '토', mainGan: 5 },
  { char: '신', element: '금', mainGan: 6 },
  { char: '유', element: '금', mainGan: 7 },
  { char: '술', element: '토', mainGan: 4 },
  { char: '해', element: '수', mainGan: 8 },
];

/** 지장간: [여기, 중기, 본기] — 없으면 null */
export interface JijangganEntry {
  yeogiGanIdx: number;        // 여기
  junggiGanIdx: number | null; // 중기 (없는 지지도 있음)
  bongiGanIdx: number;        // 본기
}

export const JIJANGGAN: JijangganEntry[] = [
  // 자: 임(여기), 계(본기)
  { yeogiGanIdx: 8, junggiGanIdx: null, bongiGanIdx: 9 },
  // 축: 계(여기), 신(중기), 기(본기)
  { yeogiGanIdx: 9, junggiGanIdx: 7, bongiGanIdx: 5 },
  // 인: 무(여기), 병(중기), 갑(본기)
  { yeogiGanIdx: 4, junggiGanIdx: 2, bongiGanIdx: 0 },
  // 묘: 갑(여기), 을(본기)
  { yeogiGanIdx: 0, junggiGanIdx: null, bongiGanIdx: 1 },
  // 진: 을(여기), 계(중기), 무(본기)
  { yeogiGanIdx: 1, junggiGanIdx: 9, bongiGanIdx: 4 },
  // 사: 무(여기), 경(중기), 병(본기)
  { yeogiGanIdx: 4, junggiGanIdx: 6, bongiGanIdx: 2 },
  // 오: 병(여기), 기(중기), 정(본기)
  { yeogiGanIdx: 2, junggiGanIdx: 5, bongiGanIdx: 3 },
  // 미: 정(여기), 을(중기), 기(본기)
  { yeogiGanIdx: 3, junggiGanIdx: 1, bongiGanIdx: 5 },
  // 신: 무(여기), 임(중기), 경(본기)
  { yeogiGanIdx: 4, junggiGanIdx: 8, bongiGanIdx: 6 },
  // 유: 경(여기), 신(본기)
  { yeogiGanIdx: 6, junggiGanIdx: null, bongiGanIdx: 7 },
  // 술: 신(여기), 정(중기), 무(본기)
  { yeogiGanIdx: 7, junggiGanIdx: 3, bongiGanIdx: 4 },
  // 해: 무(여기), 갑(중기), 임(본기)
  { yeogiGanIdx: 4, junggiGanIdx: 0, bongiGanIdx: 8 },
];

export interface JijangganSipsin {
  yeogi: { gan: string; sipsin: string };
  junggi: { gan: string; sipsin: string } | null;
  bongi: { gan: string; sipsin: string };
}

/** 12운성 — 행(천간 0~9) × 열(지지 0~11) */
// 갑(0), 을(1), 병(2), 정(3), 무(4), 기(5), 경(6), 신(7), 임(8), 계(9)
// 자(0), 축(1), 인(2), 묘(3), 진(4), 사(5), 오(6), 미(7), 신(8), 유(9), 술(10), 해(11)
export const UNSEONG_NAMES = [
  '장생', '목욕', '관대', '건록', '제왕', '쇠', '병', '사', '묘', '절', '태', '양',
] as const;
export type Unseong = typeof UNSEONG_NAMES[number];

/**
 * 12운성 기준표: 각 천간의 장생지(시작 지지 인덱스)
 * 양간은 순행(+1), 음간은 역행(-1)
 */
const JANGSAENG_JI: Record<number, number> = {
  0: 2,  // 갑 → 인(장생)
  1: 6,  // 을 → 오(장생) — 음간 역행
  2: 2,  // 병 → 인(장생)  ※ 병·무 동궁
  3: 9,  // 정 → 유(장생) — 음간 역행
  4: 2,  // 무 → 인(장생)
  5: 9,  // 기 → 유(장생) — 음간 역행
  6: 5,  // 경 → 사(장생)
  7: 0,  // 신 → 자(장생) — 음간 역행
  8: 8,  // 임 → 신(장생)
  9: 3,  // 계 → 묘(장생) — 음간 역행
};

export function getUnseong(ganIdx: number, jiIdx: number): Unseong {
  const isYang = CHEONGAN_META[ganIdx].yinYang === '양';
  const startJi = JANGSAENG_JI[ganIdx];
  const direction = isYang ? 1 : -1;
  const step = ((jiIdx - startJi) * direction + 12) % 12;
  return UNSEONG_NAMES[step];
}

const CHEONGAN_CHARS = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'];

export function getJijangganSipsin(dayGanIdx: number, jijiIdx: number): JijangganSipsin {
  const entry = JIJANGGAN[jijiIdx];
  return {
    yeogi: {
      gan: CHEONGAN_CHARS[entry.yeogiGanIdx],
      sipsin: getSipsin(dayGanIdx, entry.yeogiGanIdx),
    },
    junggi: entry.junggiGanIdx !== null ? {
      gan: CHEONGAN_CHARS[entry.junggiGanIdx],
      sipsin: getSipsin(dayGanIdx, entry.junggiGanIdx),
    } : null,
    bongi: {
      gan: CHEONGAN_CHARS[entry.bongiGanIdx],
      sipsin: getSipsin(dayGanIdx, entry.bongiGanIdx),
    },
  };
}

const ORDER: Record<Element, number> = { 목: 0, 화: 1, 토: 2, 금: 3, 수: 4 };

export function getSipsin(dayGanIdx: number, targetGanIdx: number): string {
  const me = CHEONGAN_META[dayGanIdx];
  const target = CHEONGAN_META[targetGanIdx];
  const sameYinYang = me.yinYang === target.yinYang;
  const diff = (ORDER[target.element] - ORDER[me.element] + 5) % 5;

  if (diff === 0) return sameYinYang ? '비견' : '겁재';
  if (diff === 1) return sameYinYang ? '식신' : '상관';
  if (diff === 2) return sameYinYang ? '편재' : '정재';
  if (diff === 3) return sameYinYang ? '편관' : '정관';
  return sameYinYang ? '편인' : '정인';
}

export function getJijiSipsin(dayGanIdx: number, jijiIdx: number): string {
  return getSipsin(dayGanIdx, JIJI_META[jijiIdx].mainGan);
}