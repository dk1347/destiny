from dataclasses import dataclass

from .branches import EarthlyBranch
from .data_registry import RuleRegistry
from .diagnostics import CalculationInputError, DiagnosticCode
from .stems import HeavenlyStem


@dataclass(frozen=True)
class HiddenStem:
    stem: HeavenlyStem
    role: str
    display_order: int


def hidden_stems_for(branch: EarthlyBranch, registry: RuleRegistry) -> tuple[HiddenStem, ...]:
    if not isinstance(branch, EarthlyBranch):
        raise CalculationInputError(DiagnosticCode.INVALID_BRANCH, "branch")
    dataset = registry.load("hidden_stems_v1")
    rows = dataset["data"]["branch_hidden_stems"][f"branch:{branch.value}"]
    return tuple(HiddenStem(HeavenlyStem(row["stem"].removeprefix("stem:")), row["role"], row["display_order"]) for row in rows)
