import unittest

from destiny_saju.data_registry import DatasetError, load_dataset
from destiny_saju.hidden_stems import hidden_stems_for
from destiny_saju.hour_branch import HourBranch
from destiny_saju.stems import HeavenlyStem


class DatasetAndHiddenStemTests(unittest.TestCase):
    def test_unverified_dataset_is_blocked_by_default(self) -> None:
        with self.assertRaisesRegex(DatasetError, "DATASET_NOT_PRODUCTION_VERIFIED"):
            load_dataset("hidden_stems_v1")

    def test_all_branches_have_one_main_hidden_stem(self) -> None:
        for branch in HourBranch:
            rows = hidden_stems_for(branch)
            self.assertEqual(sum(row.role == "main" for row in rows), 1)
            self.assertEqual([row.display_order for row in rows], list(range(1, len(rows) + 1)))

    def test_reference_values(self) -> None:
        self.assertEqual(hidden_stems_for(HourBranch.JA)[0].stem, HeavenlyStem.GYE)
        self.assertEqual([row.stem for row in hidden_stems_for(HourBranch.IN)], [HeavenlyStem.GAP, HeavenlyStem.BYEONG, HeavenlyStem.MU])
