import unittest
import json
from pathlib import Path

from destiny_saju.branches import EarthlyBranch
from destiny_saju.data_registry import RuleRegistry
from destiny_saju.month_stem import month_stem_for
from destiny_saju.stems import HeavenlyStem

ROOT = Path(__file__).parents[1]
REGISTRY = RuleRegistry(allow_unverified=True)
GOLDEN = json.loads((ROOT / "tests" / "fixtures" / "saju" / "core-rule-golden-v1.json").read_text(encoding="utf-8"))

class MonthStemTests(unittest.TestCase):
    def test_production_registry_loads_month_stem_rules(self) -> None:
        self.assertEqual(month_stem_for(HeavenlyStem.GAP, EarthlyBranch.IN, RuleRegistry()), HeavenlyStem.BYEONG)

    def test_golden_cases(self) -> None:
        for year, branch, expected in GOLDEN["month_stem_cases"]:
            with self.subTest(year=year, branch=branch):
                self.assertEqual(month_stem_for(HeavenlyStem(year), EarthlyBranch(branch), REGISTRY), HeavenlyStem(expected))

    def test_golden_cases_cover_every_month_branch(self) -> None:
        self.assertEqual({branch for _, branch, _ in GOLDEN["month_stem_cases"]}, {branch.value for branch in EarthlyBranch})
