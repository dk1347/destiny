"""The project's naming and notation standard for calculated values.

Two rules, applied everywhere a result is shown:

* 천간·지지 are written as the bare 한자 form — ``甲``, ``子``.
* 십신 and 12운성 are written 한글 first with the 한자 in parentheses —
  ``비견(比肩)``, ``정관(正官)``, ``건록(建祿)``.

Every label is read from the versioned rule datasets rather than hard-coded, so
display vocabulary stays under the same promotion gate as calculation data.
:func:`format_korean_with_hanja` is the shared formatter; the 12운성 table has
no promoted dataset yet, so this module formats those names but does not claim
to calculate them.
"""

from __future__ import annotations

from ..branches import EarthlyBranch
from ..data_registry import RuleRegistry
from ..stems import HeavenlyStem
from ..ten_gods import TenGod


def format_korean_with_hanja(korean: str, hanja: str) -> str:
    """Return the 한글(한자) 병기 form used for 십신 and 12운성 names."""

    if not korean or not hanja:
        raise ValueError("both a Korean name and a hanja form are required")
    return f"{korean}({hanja})"


def stem_hanja(stem: HeavenlyStem, registry: RuleRegistry) -> str:
    """Return the bare 한자 form of a heavenly stem, e.g. ``甲``."""

    return _row(registry, "heavenly_stems", stem.value)["hanja"]


def branch_hanja(branch: EarthlyBranch, registry: RuleRegistry) -> str:
    """Return the bare 한자 form of an earthly branch, e.g. ``子``."""

    return _row(registry, "earthly_branches", branch.value)["hanja"]


def pillar_hanja(stem: HeavenlyStem, branch: EarthlyBranch, registry: RuleRegistry) -> str:
    """Return a two-character pillar in 한자, e.g. ``甲子``."""

    return stem_hanja(stem, registry) + branch_hanja(branch, registry)


def ten_god_label(ten_god: TenGod, registry: RuleRegistry) -> str:
    """Return a Ten God as 한글(한자), e.g. ``비견(比肩)``."""

    names = registry.load("ten_gods_v1")["data"]["display_names"][ten_god.value]
    return format_korean_with_hanja(names["korean"], names["hanja"])


def _row(registry: RuleRegistry, table: str, row_id: str) -> dict[str, object]:
    rows = registry.load("core_tables_v1")["data"][table]
    return next(row for row in rows if row["id"] == row_id)
