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
