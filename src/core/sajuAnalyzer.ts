import { resolveSolarTime, DayBoundaryPolicy } from './solarTime';
import { getDayPillar, getTimePillar, CHEONGAN, JIJI } from './sajuEngine';
import { findSolarTerms, isSameUtcDay } from './solarTermsFinder';
import { getYearPillar, getMonthPillar } from './solarTermsEngine';
import { calculateDaewun, Gender } from './daewunEngine';
//import { getSipsin, getJijiSipsin, CHEONGAN_META, JIJI_META } from './sipsinEngine';
import { getSipsin, getJijiSipsin, getJijangganSipsin, getUnseong, CHEONGAN_META, JIJI_META } from './sipsinEngine';

export function analyzeSaju(
  birthDateTimeIso: string,
  gender: Gender,
  options: {
    longitude?: number;
    applySolarTime?: boolean;
    dayBoundary?: DayBoundaryPolicy;
  } = {}
) {
  const { longitude = 126.978, applySolarTime = true, dayBoundary = 'midnight' } = options;

  const timeCorrection = resolveSolarTime(birthDateTimeIso, longitude, applySolarTime);
  const birthUtcMs = timeCorrection.utcDate.getTime();
  const terms = findSolarTerms(birthUtcMs);

  const year = getYearPillar(timeCorrection.utcDate, new Date(terms.ipchunTerm.utcTime));
  const month = getMonthPillar(year.ganIdx, terms.currentMajorTerm.monthJiIdx || 2);
  const isLateNight = timeCorrection.localHour === 23;
  const dayOffset = (isLateNight && (dayBoundary === 'jasi' || dayBoundary === 'splitJasi')) ? 1 : 0;
  const day = getDayPillar(timeCorrection.solarDate, dayOffset);
  const time = getTimePillar(timeCorrection.solarDate, day.ganIdx, dayBoundary);

  const buildPillar = (ganIdx: number, jiIdx: number, isDayGan: boolean = false) => ({
  gan: CHEONGAN[ganIdx],
  ji: JIJI[jiIdx],
  ganSipsin: isDayGan ? '일원' : getSipsin(day.ganIdx, ganIdx),
  jiSipsin: getJijiSipsin(day.ganIdx, jiIdx),
  ganElement: CHEONGAN_META[ganIdx].element,
  jiElement: JIJI_META[jiIdx].element,
  jijanggan: getJijangganSipsin(day.ganIdx, jiIdx),
  unseong: getUnseong(ganIdx, jiIdx),
});

  const daewun = calculateDaewun(birthUtcMs, gender, year.ganIdx, month.ganIdx, month.jiIdx, terms);

  return {
    yearPillar: buildPillar(year.ganIdx, year.jiIdx),
    monthPillar: buildPillar(month.ganIdx, month.jiIdx),
    dayPillar: buildPillar(day.ganIdx, day.jiIdx, true),
    timePillar: buildPillar(time.ganIdx, time.jiIdx),
    daewun,
    correctionLine: timeCorrection.correctionLine,
  };
}

export interface SajuCandidate {
  label: '절기 이전' | '절기 이후';
  result: ReturnType<typeof analyzeSaju>;
}

export function analyzeSajuWithCandidates(
  birthDateIso: string,
  gender: Gender,
  options: {
    longitude?: number;
    applySolarTime?: boolean;
    dayBoundary?: DayBoundaryPolicy;
    unknownTime?: boolean;
  } = {}
): { candidates: SajuCandidate[]; isAmbiguous: boolean } {
  const { unknownTime = false, ...restOptions } = options;

  if (!unknownTime) {
    return {
      candidates: [{ label: '절기 이후', result: analyzeSaju(birthDateIso, gender, restOptions) }],
      isAmbiguous: false,
    };
  }

  // 시간 미상: 날짜만 추출해 UTC 정오(KST 12:00 = UTC 03:00) 기준으로 절기 당일 여부 판단
  const datePart = birthDateIso.substring(0, 10);
  const noonUtcMs = new Date(`${datePart}T03:00:00Z`).getTime();
  const noonIso = `${datePart}T03:00:00Z`;
  const terms = findSolarTerms(noonUtcMs);
  //const termUtcMs = terms.currentMajorTerm.utcTime;
  //const isTermDay = isSameUtcDay(noonUtcMs, termUtcMs);
  const currentTermUtcMs = terms.currentMajorTerm.utcTime;
  const nextTermUtcMs = terms.nextMajorTerm.utcTime;
  const isTermDay = isSameUtcDay(noonUtcMs, currentTermUtcMs) || isSameUtcDay(noonUtcMs, nextTermUtcMs);
  const termUtcMs = isSameUtcDay(noonUtcMs, nextTermUtcMs) ? nextTermUtcMs : currentTermUtcMs;

  if (!isTermDay) {
    return {
      candidates: [{ label: '절기 이후', result: analyzeSaju(noonIso, gender, restOptions) }],
      isAmbiguous: false,
    };
  }

  //const beforeIso = new Date(termUtcMs - 60 * 1000).toISOString();
  //const afterIso  = new Date(termUtcMs + 60 * 1000).toISOString();
  const termDate = new Date(termUtcMs);
  const beforeDate = new Date(termUtcMs - 24 * 60 * 60 * 1000); // 입절 하루 전
  const beforeIso = `${beforeDate.getUTCFullYear()}-${String(beforeDate.getUTCMonth()+1).padStart(2,'0')}-${String(beforeDate.getUTCDate()).padStart(2,'0')}T12:00:00Z`;
  const afterIso  = `${termDate.getUTCFullYear()}-${String(termDate.getUTCMonth()+1).padStart(2,'0')}-${String(termDate.getUTCDate()).padStart(2,'0')}T23:00:00Z`;


  return {
    candidates: [
      { label: '절기 이전', result: analyzeSaju(beforeIso, gender, { ...restOptions, applySolarTime: false }) },
      { label: '절기 이후', result: analyzeSaju(afterIso,  gender, { ...restOptions, applySolarTime: false }) },
    ],
    isAmbiguous: true,
  };
}