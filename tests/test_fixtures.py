import json
import unittest
from datetime import datetime
from pathlib import Path

from destiny_saju.hour_branch import hour_branch_for_time


class FixtureTests(unittest.TestCase):
    def test_hour_boundary_fixture(self) -> None:
        path = Path(__file__).parent / "fixtures" / "saju" / "hour-boundary-001.json"
        case = json.loads(path.read_text(encoding="utf-8"))
        local_datetime = datetime.fromisoformat(case["resolved_time"]["legal_local_datetime"])
        self.assertEqual(hour_branch_for_time(local_datetime.time()).value, case["expected"]["hour_branch"])
