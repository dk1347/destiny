import unittest

from destiny_saju.stems import HeavenlyStem
from destiny_saju.ten_gods import TenGod, ten_god_for


class TenGodTests(unittest.TestCase):
    def test_gap_day_master_reference_row(self) -> None:
        expected = list(TenGod)
        actual = [ten_god_for(HeavenlyStem.GAP, target) for target in HeavenlyStem]
        self.assertEqual(actual, expected)

    def test_all_one_hundred_pairs_produce_a_ten_god(self) -> None:
        results = [ten_god_for(day, target) for day in HeavenlyStem for target in HeavenlyStem]
        self.assertEqual(len(results), 100)
        self.assertEqual(set(results), set(TenGod))
