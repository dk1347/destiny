import unittest
from pathlib import Path

from destiny_saju.data_registry import DatasetError, RuleRegistry, load_dataset
from destiny_saju.hidden_stems import hidden_stems_for
from destiny_saju.branches import EarthlyBranch
from destiny_saju.stems import HeavenlyStem
from destiny_saju.hour_stem import hour_stem_for
from destiny_saju.month_stem import month_stem_for
from destiny_saju.ten_gods import ten_god_for

DATA_DIR = Path(__file__).parents[1] / "data" / "saju"
TEST_REGISTRY = RuleRegistry(DATA_DIR, allow_unverified=True)


class DatasetAndHiddenStemTests(unittest.TestCase):
    def test_unverified_dataset_is_blocked_by_default(self) -> None:
        with self.assertRaisesRegex(DatasetError, "DATASET_NOT_PRODUCTION_VERIFIED"):
            load_dataset("hidden_stems_v1", data_dir=DATA_DIR)

    def test_every_calculator_obeys_production_gate(self) -> None:
        production = RuleRegistry(DATA_DIR)
        calls = (
            lambda: hidden_stems_for(EarthlyBranch.JA, production),
            lambda: hour_stem_for(HeavenlyStem.GAP, EarthlyBranch.JA, production),
            lambda: month_stem_for(HeavenlyStem.GAP, EarthlyBranch.IN, production),
            lambda: ten_god_for(HeavenlyStem.GAP, HeavenlyStem.GAP, production),
        )
        for call in calls:
            with self.assertRaisesRegex(DatasetError, "DATASET_NOT_PRODUCTION_VERIFIED"):
                call()

    def test_all_branches_have_one_main_hidden_stem(self) -> None:
        for branch in EarthlyBranch:
            rows = hidden_stems_for(branch, TEST_REGISTRY)
            self.assertEqual(sum(row.role == "main" for row in rows), 1)
            self.assertEqual([row.display_order for row in rows], list(range(1, len(rows) + 1)))

    def test_reference_values(self) -> None:
        self.assertEqual(hidden_stems_for(EarthlyBranch.JA, TEST_REGISTRY)[0].stem, HeavenlyStem.GYE)
        self.assertEqual([row.stem for row in hidden_stems_for(EarthlyBranch.IN, TEST_REGISTRY)], [HeavenlyStem.GAP, HeavenlyStem.BYEONG, HeavenlyStem.MU])
