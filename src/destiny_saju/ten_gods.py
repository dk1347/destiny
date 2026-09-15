from enum import StrEnum

from .stems import HeavenlyStem


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


_ELEMENTS = (
    Element.WOOD, Element.WOOD, Element.FIRE, Element.FIRE, Element.EARTH,
    Element.EARTH, Element.METAL, Element.METAL, Element.WATER, Element.WATER,
)

_TEN_GODS = {
    ("same", True): TenGod.BIGYEON,
    ("same", False): TenGod.GEOPJAE,
    ("generates", True): TenGod.SIKSIN,
    ("generates", False): TenGod.SANGWAN,
    ("controls", True): TenGod.PYEONJAE,
    ("controls", False): TenGod.JEONGJAE,
    ("controlled_by", True): TenGod.PYEONGWAN,
    ("controlled_by", False): TenGod.JEONGGWAN,
    ("generated_by", True): TenGod.PYEONIN,
    ("generated_by", False): TenGod.JEONGIN,
}


def ten_god_for(day_stem: HeavenlyStem, target_stem: HeavenlyStem) -> TenGod:
    stems = list(HeavenlyStem)
    day_index = stems.index(day_stem)
    target_index = stems.index(target_stem)
    day_element = _ELEMENTS[day_index]
    target_element = _ELEMENTS[target_index]
    same_polarity = day_index % 2 == target_index % 2
    elements = list(Element)
    delta = (elements.index(target_element) - elements.index(day_element)) % 5
    relation = {0: "same", 1: "generates", 2: "controls", 3: "controlled_by", 4: "generated_by"}[delta]
    return _TEN_GODS[(relation, same_polarity)]
