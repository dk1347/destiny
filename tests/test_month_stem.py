import unittest

from destiny_saju.month_stem import month_stem_for
from destiny_saju.stems import HeavenlyStem


class MonthStemTests(unittest.TestCase):
    def test_five_tigers_start_stems(self) -> None:
        self.assertIs(month_stem_for(HeavenlyStem.GAP, 0), HeavenlyStem.BYEONG)
        self.assertIs(month_stem_for(HeavenlyStem.EUL, 0), HeavenlyStem.MU)
        self.assertIs(month_stem_for(HeavenlyStem.BYEONG, 0), HeavenlyStem.GYEONG)
        self.assertIs(month_stem_for(HeavenlyStem.JEONG, 0), HeavenlyStem.IM)
        self.assertIs(month_stem_for(HeavenlyStem.MU, 0), HeavenlyStem.GAP)

    def test_offsets_cycle_through_stems(self) -> None:
        self.assertIs(month_stem_for(HeavenlyStem.GAP, 10), HeavenlyStem.BYEONG)
        with self.assertRaises(ValueError):
            month_stem_for(HeavenlyStem.GAP, 12)
