import unittest
import json
import tempfile
from importlib.resources import files
from pathlib import Path

from destiny_saju.data_registry import DatasetError, RuleRegistry, load_dataset
from destiny_saju.hidden_stems import hidden_stems_for
from destiny_saju.branches import EarthlyBranch
from destiny_saju.stems import HeavenlyStem
from destiny_saju.hour_stem import hour_stem_for
from destiny_saju.month_stem import month_stem_for
from destiny_saju.ten_gods import ten_god_for

TEST_REGISTRY = RuleRegistry(allow_unverified=True)


class DatasetAndHiddenStemTests(unittest.TestCase):
    def test_unverified_dataset_is_blocked_by_default(self) -> None:
        with self.assertRaisesRegex(DatasetError, "DATASET_NOT_PRODUCTION_VERIFIED"):
            load_dataset("hidden_stems_v1")

    def test_every_calculator_obeys_production_gate(self) -> None:
        production = RuleRegistry()
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

    def test_compact_hidden_stem_table_has_the_recorded_main_middle_residual_rows(self) -> None:
        expected = {
            EarthlyBranch.JA: (HeavenlyStem.GYE,),
            EarthlyBranch.CHUK: (HeavenlyStem.GI, HeavenlyStem.GYE, HeavenlyStem.SIN),
            EarthlyBranch.IN: (HeavenlyStem.GAP, HeavenlyStem.BYEONG, HeavenlyStem.MU),
            EarthlyBranch.MYO: (HeavenlyStem.EUL,),
            EarthlyBranch.JIN: (HeavenlyStem.MU, HeavenlyStem.EUL, HeavenlyStem.GYE),
            EarthlyBranch.SA: (HeavenlyStem.BYEONG, HeavenlyStem.GYEONG, HeavenlyStem.MU),
            EarthlyBranch.O: (HeavenlyStem.JEONG, HeavenlyStem.GI),
            EarthlyBranch.MI: (HeavenlyStem.GI, HeavenlyStem.JEONG, HeavenlyStem.EUL),
            EarthlyBranch.SIN: (HeavenlyStem.GYEONG, HeavenlyStem.IM, HeavenlyStem.MU),
            EarthlyBranch.YU: (HeavenlyStem.SIN,),
            EarthlyBranch.SUL: (HeavenlyStem.MU, HeavenlyStem.SIN, HeavenlyStem.JEONG),
            EarthlyBranch.HAE: (HeavenlyStem.IM, HeavenlyStem.GAP),
        }

        for branch, expected_stems in expected.items():
            with self.subTest(branch=branch):
                self.assertEqual(
                    tuple(row.stem for row in hidden_stems_for(branch, TEST_REGISTRY)),
                    expected_stems,
                )

    def test_broken_reference_is_reported_as_dataset_error(self) -> None:
        source = files("destiny_saju.data.saju")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            for resource in source.iterdir():
                if resource.name.endswith(".json"):
                    (target / resource.name).write_bytes(resource.read_bytes())
            path = target / "month_stem_rules_v1.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["data"]["month_branch_order_from_in"].remove("branch:chuk")
            path.write_text(json.dumps(payload), encoding="utf-8")
            registry = RuleRegistry(target, allow_unverified=True)
            with self.assertRaisesRegex(DatasetError, "DATASET_SCHEMA_INVALID"):
                month_stem_for(HeavenlyStem.GAP, EarthlyBranch.CHUK, registry)

    def test_fault_injections_are_rejected_as_schema_errors(self) -> None:
        source = files("destiny_saju.data.saju")
        injections = (
            ("month_stem_rules_v1", lambda data: data["month_branch_order_from_in"].__setitem__(slice(3, 5), reversed(data["month_branch_order_from_in"][3:5]))),
            ("hour_stem_rules_v1", lambda data: data["hour_branch_order_from_ja"].__setitem__(slice(3, 5), reversed(data["hour_branch_order_from_ja"][3:5]))),
            ("core_tables_v1", lambda data: data["heavenly_stems"][0].__setitem__("id", "contaminated")),
            ("core_tables_v1", lambda data: data["heavenly_stems"][0].__setitem__("yin_yang", "neutral")),
            ("core_tables_v1", lambda data: data["heavenly_stems"][1].__setitem__("yin_yang", "yang")),
            ("hidden_stems_v1", lambda data: data["branch_hidden_stems"]["branch:ja"][0].__setitem__("role", "contaminated")),
        )
        for dataset_id, inject in injections:
            with self.subTest(dataset_id=dataset_id):
                with tempfile.TemporaryDirectory() as temporary:
                    target = Path(temporary)
                    for resource in source.iterdir():
                        if resource.name.endswith(".json"):
                            (target / resource.name).write_bytes(resource.read_bytes())
                    path = target / f"{dataset_id}.json"
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    inject(payload["data"])
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaisesRegex(DatasetError, "DATASET_SCHEMA_INVALID") as error:
                        RuleRegistry(target, allow_unverified=True).load(dataset_id)
                    self.assertEqual(error.exception.code.name, "DATASET_SCHEMA_INVALID")

    def test_registry_returns_defensive_copies(self) -> None:
        first = TEST_REGISTRY.load("core_tables_v1")
        first["data"]["heavenly_stems"].clear()
        second = TEST_REGISTRY.load("core_tables_v1")
        self.assertEqual(len(second["data"]["heavenly_stems"]), 10)

    def test_registry_reports_loaded_dataset_versions_deterministically(self) -> None:
        registry = RuleRegistry(allow_unverified=True)
        registry.load("ten_gods_v1")
        self.assertEqual(
            registry.loaded_dataset_versions(),
            (("core_tables_v1", "1.0.0"), ("ten_gods_v1", "1.0.0")),
        )
