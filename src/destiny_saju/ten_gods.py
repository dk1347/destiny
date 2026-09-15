from enum import StrEnum

from .data_registry import RuleRegistry
from .diagnostics import CalculationInputError, DiagnosticCode
from .stems import HeavenlyStem
from .tables import stem_attributes


class Element(StrEnum):
    WOOD = "wood"
    FIRE = "fire"
    EARTH = "earth"
    METAL = "metal"
    WATER = "water"


class TenGod(StrEnum):
    BIGYEON = "bigyeon"
    GEOPJAE = "geopjae"
    SIKSIN = "siksin"
    SANGWAN = "sangwan"
    PYEONJAE = "pyeonjae"
    JEONGJAE = "jeongjae"
    PYEONGWAN = "pyeongwan"
    JEONGGWAN = "jeonggwan"
    PYEONIN = "pyeonin"
    JEONGIN = "jeongin"


def ten_god_for(day_stem: HeavenlyStem, target_stem: HeavenlyStem, registry: RuleRegistry) -> TenGod:
    if not isinstance(day_stem, HeavenlyStem) or not isinstance(target_stem, HeavenlyStem):
        raise CalculationInputError(DiagnosticCode.INVALID_STEM, "day_stem/target_stem")
    day = stem_attributes(day_stem, registry)
    target = stem_attributes(target_stem, registry)
    day_element = Element(day.element)
    target_element = Element(target.element)
    same_polarity = day.yin_yang == target.yin_yang
    elements = list(Element)
    delta = (elements.index(target_element) - elements.index(day_element)) % 5
    relation = {0: "same_element", 1: "day_master_generates_target", 2: "day_master_controls_target", 3: "target_controls_day_master", 4: "target_generates_day_master"}[delta]
    rows = registry.load("ten_gods_v1")["data"]["relation_table"]
    row = next(item for item in rows if item["relation_element"] == relation)
    return TenGod(row["same_polarity" if same_polarity else "different_polarity"])
