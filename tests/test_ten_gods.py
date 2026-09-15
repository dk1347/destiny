import unittest
import json
from pathlib import Path

from destiny_saju.data_registry import RuleRegistry
from destiny_saju.branches import EarthlyBranch
from destiny_saju.stems import HeavenlyStem
from destiny_saju.ten_gods import TenGod, ten_god_for

ROOT = Path(__file__).parents[1]
REGISTRY = RuleRegistry(allow_unverified=True)
GOLDEN = json.loads((ROOT / "tests" / "fixtures" / "saju" / "core-rule-golden-v1.json").read_text(encoding="utf-8"))

class TenGodTests(unittest.TestCase):
    def test_golden_cases(self) -> None:
        for day, target, expected in GOLDEN["ten_god_cases"]:
            with self.subTest(day=day, target=target):
                self.assertEqual(ten_god_for(HeavenlyStem(day), HeavenlyStem(target), REGISTRY), TenGod(expected))

    def test_all_one_hundred_pairs_produce_a_ten_god(self) -> None:
        results = [ten_god_for(day, target, REGISTRY) for day in HeavenlyStem for target in HeavenlyStem]
        self.assertEqual(len(results), 100)
        self.assertEqual(set(results), set(TenGod))

    def test_domain_enums_with_same_value_are_not_equal(self) -> None:
        self.assertNotEqual(HeavenlyStem.SIN, EarthlyBranch.SIN)
        self.assertIsNone({HeavenlyStem.SIN: "stem"}.get(EarthlyBranch.SIN))
