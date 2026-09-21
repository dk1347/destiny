import { resolveSolarTime, DayBoundaryPolicy } from './solarTime';
import { getDayPillar, getTimePillar, CHEONGAN, JIJI } from './sajuEngine';
import { findSolarTerms } from './solarTermsFinder';
import { getYearPillar, getMonthPillar } from './solarTermsEngine';
import { calculateDaewun, Gender } from './daewunEngine';
import { getSipsin, getJijiSipsin, CHEONGAN_META, JIJI_META } from './sipsinEngine';

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
  const birthUtcMs = timeCorrection.solarDate.getTime();
  const terms = findSolarTerms(birthUtcMs);

  //const year = getYearPillar(timeCorrection.solarDate, new Date(terms.ipchunTerm.utcTime));
  const year = getYearPillar(timeCorrection.utcDate, new Date(terms.ipchunTerm.utcTime));
  const month = getMonthPillar(year.ganIdx, terms.currentMajorTerm.monthJiIdx || 2);
  const day = getDayPillar(timeCorrection.solarDate);
  const time = getTimePillar(timeCorrection.solarDate, day.ganIdx, dayBoundary);

  const buildPillar = (ganIdx: number, jiIdx: number, isDayGan: boolean = false) => ({
    gan: CHEONGAN[ganIdx],
    ji: JIJI[jiIdx],
    ganSipsin: isDayGan ? '일원' : getSipsin(day.ganIdx, ganIdx),
    jiSipsin: getJijiSipsin(day.ganIdx, jiIdx),
    ganElement: CHEONGAN_META[ganIdx].element,
    jiElement: JIJI_META[jiIdx].element,
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
