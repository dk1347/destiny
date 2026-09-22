import { getSipsin, getJijangganSipsin, getUnseong, JIJANGGAN } from '../src/core/sipsinEngine';

describe('십신 산출', () => {
  test('갑일간 기준 십신 전체', () => {
    // 갑(0) 기준
    expect(getSipsin(0, 0)).toBe('비견');  // 갑→갑
    expect(getSipsin(0, 1)).toBe('겁재');  // 갑→을
    expect(getSipsin(0, 2)).toBe('식신');  // 갑→병
    expect(getSipsin(0, 3)).toBe('상관');  // 갑→정
    expect(getSipsin(0, 4)).toBe('편재');  // 갑→무
    expect(getSipsin(0, 5)).toBe('정재');  // 갑→기
    expect(getSipsin(0, 6)).toBe('편관');  // 갑→경
    expect(getSipsin(0, 7)).toBe('정관');  // 갑→신
    expect(getSipsin(0, 8)).toBe('편인');  // 갑→임
    expect(getSipsin(0, 9)).toBe('정인');  // 갑→계
  });

  test('경일간 기준 십신', () => {
    expect(getSipsin(6, 6)).toBe('비견');  // 경→경
    expect(getSipsin(6, 7)).toBe('겁재');  // 경→신
    expect(getSipsin(6, 0)).toBe('편재');  // 경→갑
    expect(getSipsin(6, 4)).toBe('편인');  // 경→무
  });
});

describe('지장간 및 지장간 십신', () => {
  test('인(寅) 지장간: 무(여기)·병(중기)·갑(본기)', () => {
    const result = getJijangganSipsin(0, 2); // 갑일간, 인(idx=2)
    expect(result.yeogi.gan).toBe('무');
    expect(result.yeogi.sipsin).toBe('편재');
    expect(result.junggi?.gan).toBe('병');
    expect(result.junggi?.sipsin).toBe('식신');
    expect(result.bongi.gan).toBe('갑');
    expect(result.bongi.sipsin).toBe('비견');
  });

  test('자(子) 지장간: 임(여기)·중기없음·계(본기)', () => {
    const result = getJijangganSipsin(0, 0); // 갑일간, 자(idx=0)
    expect(result.yeogi.gan).toBe('임');
    expect(result.junggi).toBeNull();
    expect(result.bongi.gan).toBe('계');
    expect(result.bongi.sipsin).toBe('정인');
  });

  test('오(午) 지장간: 병(여기)·기(중기)·정(본기)', () => {
    const result = getJijangganSipsin(0, 6); // 갑일간, 오(idx=6)
    expect(result.yeogi.gan).toBe('병');
    expect(result.junggi?.gan).toBe('기');
    expect(result.bongi.gan).toBe('정');
    expect(result.bongi.sipsin).toBe('상관');
  });

  test('12지지 지장간 본기 누락 없음', () => {
    for (let i = 0; i < 12; i++) {
      const result = getJijangganSipsin(0, i);
      expect(result.bongi.gan).toBeTruthy();
      expect(result.yeogi.gan).toBeTruthy();
    }
  });
});

describe('12운성 산출', () => {
  test('갑(양목) 장생지는 인(寅)', () => {
    expect(getUnseong(0, 2)).toBe('장생');
  });

  test('갑(양목) 12운성 순행 전체', () => {
    const expected = ['장생','목욕','관대','건록','제왕','쇠','병','사','묘','절','태','양'];
    // 인(2)부터 순행
    const jijis = [2,3,4,5,6,7,8,9,10,11,0,1];
    jijis.forEach((ji, i) => {
      expect(getUnseong(0, ji)).toBe(expected[i]);
    });
  });

  test('경(양금) 장생지는 사(巳)', () => {
    expect(getUnseong(6, 5)).toBe('장생');
  });

  test('임(양수) 장생지는 신(申)', () => {
    expect(getUnseong(8, 8)).toBe('장생');
  });

  test('을(음목) 장생지는 오(午)', () => {
    expect(getUnseong(1, 6)).toBe('장생');
  });

  test('을(음목) 역행 — 오(장생)→사(목욕)', () => {
    expect(getUnseong(1, 5)).toBe('목욕');
  });
});