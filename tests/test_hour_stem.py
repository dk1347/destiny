import unittest
import json
from pathlib import Path

from destiny_saju.branches import EarthlyBranch
from destiny_saju.data_registry import RuleRegistry
from destiny_saju.hour_stem import hour_stem_for
from destiny_saju.stems import HeavenlyStem

ROOT = Path(__file__).parents[1]
REGISTRY = RuleRegistry(allow_unverified=True)
GOLDEN = json.loads((ROOT / "tests" / "fixtures" / "saju" / "core-rule-golden-v1.json").read_text(encoding="utf-8"))

class HourStemTests(unittest.TestCase):
    def test_golden_cases(self) -> None:
        for day, branch, expected in GOLDEN["hour_stem_cases"]:
            with self.subTest(day=day, branch=branch):
                self.assertEqual(hour_stem_for(HeavenlyStem(day), EarthlyBranch(branch), REGISTRY), HeavenlyStem(expected))
