"""Traditional two-hour earthly-branch windows.

This module only selects the hour branch. Day-boundary and Zi-hour treatment
remain Calculation Profile decisions and must not be inferred here.
"""

from __future__ import annotations

from datetime import time
from enum import StrEnum


class HourBranch(StrEnum):
    JA = "ja"
    CHUK = "chuk"
    IN = "in"
    MYO = "myo"
    JIN = "jin"
    SA = "sa"
    O = "o"
    MI = "mi"
    SIN = "sin"
    YU = "yu"
    SUL = "sul"
    HAE = "hae"


_BRANCHES_BY_TWO_HOUR_BLOCK: tuple[HourBranch, ...] = (
    HourBranch.JA,
    HourBranch.JA,
    HourBranch.CHUK,
    HourBranch.CHUK,
    HourBranch.IN,
    HourBranch.IN,
    HourBranch.MYO,
    HourBranch.MYO,
    HourBranch.JIN,
    HourBranch.JIN,
    HourBranch.SA,
    HourBranch.SA,
    HourBranch.O,
    HourBranch.O,
    HourBranch.MI,
    HourBranch.MI,
    HourBranch.SIN,
    HourBranch.SIN,
    HourBranch.YU,
    HourBranch.YU,
    HourBranch.SUL,
    HourBranch.SUL,
    HourBranch.HAE,
    HourBranch.HAE,
)


def hour_branch_for_time(local_time: time) -> HourBranch:
    """Return the branch for a resolved calculation-basis local time.

    The conventional windows are Zi 23:00–00:59, Chou 01:00–02:59,
    through Hai 21:00–22:59. Seconds and microseconds do not affect the
    result. This function deliberately does not change the civil date at 23:00.
    """

    if not isinstance(local_time, time):
        raise TypeError("local_time must be a datetime.time instance")

    return _BRANCHES_BY_TWO_HOUR_BLOCK[(local_time.hour + 1) % 24]
