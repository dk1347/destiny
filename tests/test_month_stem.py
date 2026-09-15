import unittest
import json
from pathlib import Path

from destiny_saju.branches import EarthlyBranch
from destiny_saju.data_registry import RuleRegistry
from destiny_saju.month_stem import month_stem_for
from destiny_saju.stems import HeavenlyStem

ROOT = Path(__file__).parents[1]
REGISTRY = RuleRegistry(ROOT / "data" / "saju", allow_unverified=True)
GOLDEN = json.loads((ROOT / "tests" / "fixtures" / "saju" / "core-rule-golden-v1.json").read_text(encoding="utf-8"))

class MonthStemTests(unittest.TestCase):
    def test_golden_cases(self) -> None:
        for year, branch, expected in GOLDEN["month_stem_cases"]:
            with self.subTest(year=year, branch=branch):
                self.assertEqual(month_stem_for(HeavenlyStem(year), EarthlyBranch(branch), REGISTRY), HeavenlyStem(expected))
