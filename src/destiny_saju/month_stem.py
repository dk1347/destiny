from .stems import HeavenlyStem


_IN_MONTH_START = {
    HeavenlyStem.GAP: HeavenlyStem.BYEONG, HeavenlyStem.GI: HeavenlyStem.BYEONG,
    HeavenlyStem.EUL: HeavenlyStem.MU, HeavenlyStem.GYEONG: HeavenlyStem.MU,
    HeavenlyStem.BYEONG: HeavenlyStem.GYEONG, HeavenlyStem.SIN: HeavenlyStem.GYEONG,
    HeavenlyStem.JEONG: HeavenlyStem.IM, HeavenlyStem.IM: HeavenlyStem.IM,
    HeavenlyStem.MU: HeavenlyStem.GAP, HeavenlyStem.GYE: HeavenlyStem.GAP,
}


def month_stem_for(year_stem: HeavenlyStem, month_branch_offset_from_in: int) -> HeavenlyStem:
    if not 0 <= month_branch_offset_from_in < 12:
        raise ValueError("month_branch_offset_from_in must be in 0..11")
    stems = list(HeavenlyStem)
    return stems[(stems.index(_IN_MONTH_START[year_stem]) + month_branch_offset_from_in) % 10]
