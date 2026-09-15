from .hour_branch import HourBranch
from .stems import HeavenlyStem

_START={HeavenlyStem.GAP:0,HeavenlyStem.GI:0,HeavenlyStem.EUL:2,HeavenlyStem.GYEONG:2,HeavenlyStem.BYEONG:4,HeavenlyStem.SIN:4,HeavenlyStem.JEONG:6,HeavenlyStem.IM:6,HeavenlyStem.MU:8,HeavenlyStem.GYE:8}

def hour_stem_for(day_stem: HeavenlyStem, branch: HourBranch) -> HeavenlyStem:
    return list(HeavenlyStem)[(_START[day_stem]+list(HourBranch).index(branch))%10]
