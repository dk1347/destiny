from dataclasses import dataclass

from .data_registry import load_dataset
from .hour_branch import HourBranch
from .stems import HeavenlyStem


@dataclass(frozen=True)
class HiddenStem:
    stem: HeavenlyStem
    role: str
    display_order: int


def hidden_stems_for(branch: HourBranch) -> tuple[HiddenStem, ...]:
    dataset = load_dataset("hidden_stems_v1", allow_unverified=True)
    rows = dataset["data"]["branch_hidden_stems"][f"branch:{branch.value}"]
    return tuple(HiddenStem(HeavenlyStem(row["stem"].removeprefix("stem:")), row["role"], row["display_order"]) for row in rows)
