from .branches import EarthlyBranch
from .data_registry import RuleRegistry
from .diagnostics import CalculationInputError, DiagnosticCode
from .stems import HeavenlyStem
from .tables import ordered_stems


def month_stem_for(year_stem: HeavenlyStem, month_branch: EarthlyBranch, registry: RuleRegistry) -> HeavenlyStem:
    if not isinstance(year_stem, HeavenlyStem):
        raise CalculationInputError(DiagnosticCode.INVALID_STEM, "year_stem")
    if not isinstance(month_branch, EarthlyBranch):
        raise CalculationInputError(DiagnosticCode.INVALID_BRANCH, "month_branch")
    rules = registry.load("month_stem_rules_v1")["data"]
    year_ref = f"stem:{year_stem.value}"
    group = next(row for row in rules["tiger_start_by_year_stem_group"] if year_ref in row["year_stems"])
    start = HeavenlyStem(group["in_month_start_stem"].removeprefix("stem:"))
    branch_ref = f"branch:{month_branch.value}"
    offset = rules["month_branch_order_from_in"].index(branch_ref)
    stems = ordered_stems(registry)
    return stems[(stems.index(start) + offset) % len(stems)]
