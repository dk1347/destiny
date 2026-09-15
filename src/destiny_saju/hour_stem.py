from .branches import EarthlyBranch
from .data_registry import RuleRegistry
from .diagnostics import CalculationInputError, DiagnosticCode
from .stems import HeavenlyStem
from .tables import ordered_stems

def hour_stem_for(day_stem: HeavenlyStem, branch: EarthlyBranch, registry: RuleRegistry) -> HeavenlyStem:
    if not isinstance(day_stem, HeavenlyStem):
        raise CalculationInputError(DiagnosticCode.INVALID_STEM, "day_stem")
    if not isinstance(branch, EarthlyBranch):
        raise CalculationInputError(DiagnosticCode.INVALID_BRANCH, "branch")
    rules = registry.load("hour_stem_rules_v1")["data"]
    day_ref = f"stem:{day_stem.value}"
    group = next(row for row in rules["rat_start_by_day_stem_group"] if day_ref in row["day_stems"])
    start = HeavenlyStem(group["ja_hour_start_stem"].removeprefix("stem:"))
    offset = rules["hour_branch_order_from_ja"].index(f"branch:{branch.value}")
    stems = ordered_stems(registry)
    return stems[(stems.index(start) + offset) % len(stems)]
