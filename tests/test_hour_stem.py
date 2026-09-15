import unittest

from destiny_saju.hour_branch import HourBranch
from destiny_saju.hour_stem import hour_stem_for
from destiny_saju.stems import HeavenlyStem


class HourStemTests(unittest.TestCase):
    def test_all_day_stem_and_hour_branch_combinations(self) -> None:
        starts = {
            HeavenlyStem.GAP: HeavenlyStem.GAP, HeavenlyStem.GI: HeavenlyStem.GAP,
            HeavenlyStem.EUL: HeavenlyStem.BYEONG, HeavenlyStem.GYEONG: HeavenlyStem.BYEONG,
            HeavenlyStem.BYEONG: HeavenlyStem.MU, HeavenlyStem.SIN: HeavenlyStem.MU,
            HeavenlyStem.JEONG: HeavenlyStem.GYEONG, HeavenlyStem.IM: HeavenlyStem.GYEONG,
            HeavenlyStem.MU: HeavenlyStem.IM, HeavenlyStem.GYE: HeavenlyStem.IM,
        }
        stems = list(HeavenlyStem)
        for day_stem, start in starts.items():
            for offset, branch in enumerate(HourBranch):
                with self.subTest(day_stem=day_stem, branch=branch):
                    self.assertIs(hour_stem_for(day_stem, branch), stems[(stems.index(start) + offset) % 10])
