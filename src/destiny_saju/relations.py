"""Detect source-backed stem and branch relations without interpreting them."""

from __future__ import annotations

from dataclasses import dataclass

from .data_registry import RuleRegistry
from .four_pillars import FourPillars


_DATASET_ID = "relations_v1"


@dataclass(frozen=True)
class RelationFinding:
    relation_id: str
    relation_type: str
    participants: tuple[str, ...]
    values: tuple[str, ...]
    rule_set_version: str
    resulting_element: str | None = None


def relations_for_pillars(pillars: FourPillars, registry: RuleRegistry) -> tuple[RelationFinding, ...]:
    """Return detected facts from a versioned relation dataset; never interpret them."""

    if not isinstance(pillars, FourPillars):
        raise TypeError("pillars must be a FourPillars instance")
    dataset = registry.load(_DATASET_ID)
    data = dataset["data"]
    findings = []
    stems = (("year_stem", pillars.year.stem.value), ("month_stem", pillars.month.stem.value),
             ("day_stem", pillars.day.stem.value), ("hour_stem", pillars.hour.stem.value))
    branches = (("year_branch", pillars.year.branch.value), ("month_branch", pillars.month.branch.value),
                ("day_branch", pillars.day.branch.value), ("hour_branch", pillars.hour.branch.value))
    for rows, available, prefix in ((data["stem_combinations"], stems, "stem"), (data["branch_relations"], branches, "branch")):
        for row in rows:
            wanted = tuple(item.removeprefix(f"{prefix}:") for item in row["participants"])
            positions = tuple(position for position, value in available if value in wanted)
            if len(positions) < len(wanted):
                continue
            if row["relation_type"] == "branch_self_punishment" and sum(value == wanted[0] for _, value in available) < 2:
                continue
            findings.append(RelationFinding(row["relation_id"], row["relation_type"], positions, wanted, f"{dataset['dataset_id']}@{dataset['dataset_version']}", row.get("resulting_element")))
    return tuple(findings)
