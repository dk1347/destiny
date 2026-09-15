from dataclasses import dataclass

from .data_registry import RuleRegistry
from .stems import HeavenlyStem


@dataclass(frozen=True)
class StemAttributes:
    element: str
    yin_yang: str
    order: int


def ordered_stems(registry: RuleRegistry) -> tuple[HeavenlyStem, ...]:
    rows = registry.load("core_tables_v1")["data"]["heavenly_stems"]
    return tuple(HeavenlyStem(row["id"]) for row in sorted(rows, key=lambda row: row["order"]))


def stem_attributes(stem: HeavenlyStem, registry: RuleRegistry) -> StemAttributes:
    rows = registry.load("core_tables_v1")["data"]["heavenly_stems"]
    row = next(item for item in rows if item["id"] == stem.value)
    return StemAttributes(row["element"], row["yin_yang"], row["order"])
