from datetime import time
import unittest

from destiny_saju.hour_branch import HourBranch, hour_branch_for_time


class HourBranchTests(unittest.TestCase):
    def test_hour_branch_boundaries(self) -> None:
        cases = [
        (time(23, 0), HourBranch.JA),
        (time(0, 59, 59), HourBranch.JA),
        (time(1, 0), HourBranch.CHUK),
        (time(2, 59), HourBranch.CHUK),
        (time(11, 0), HourBranch.O),
        (time(22, 59), HourBranch.HAE),
        ]
        for local_time, expected in cases:
            with self.subTest(local_time=local_time):
                self.assertIs(hour_branch_for_time(local_time), expected)

    def test_hour_branch_does_not_decide_day_boundary(self) -> None:
        self.assertIs(hour_branch_for_time(time(23, 0)), HourBranch.JA)

    def test_hour_branch_rejects_non_time_input(self) -> None:
        with self.assertRaises(TypeError):
            hour_branch_for_time("23:00")  # type: ignore[arg-type]
