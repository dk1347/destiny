from datetime import datetime, timedelta, timezone

from destiny_saju.branches import EarthlyBranch
from destiny_saju.data_registry import RuleRegistry
from destiny_saju.month_pillar import month_pillar_for_datetime
from destiny_saju.stems import HeavenlyStem
from destiny_saju.year_pillar import year_pillar_for_datetime


KST = timezone(timedelta(hours=9))


def test_year_pillar_changes_at_ipchun_not_new_year() -> None:
    registry = RuleRegistry(allow_unverified=True)
    boundary = datetime(2026, 2, 4, 5, 2, tzinfo=KST)

    assert year_pillar_for_datetime(boundary - timedelta(minutes=1), registry).stem is HeavenlyStem.EUL
    assert year_pillar_for_datetime(boundary - timedelta(minutes=1), registry).branch is EarthlyBranch.SA
    assert year_pillar_for_datetime(boundary, registry).stem is HeavenlyStem.BYEONG
    assert year_pillar_for_datetime(boundary, registry).branch is EarthlyBranch.O
    # Dongji is a solar term, not another year boundary.  The 2026 year
    # remains active after the December dongji instant.
    assert year_pillar_for_datetime(datetime(2026, 12, 22, 5, 50, tzinfo=KST), registry).stem is HeavenlyStem.BYEONG
    assert year_pillar_for_datetime(datetime(2026, 12, 22, 5, 50, tzinfo=KST), registry).branch is EarthlyBranch.O


def test_month_pillar_uses_latest_major_solar_term() -> None:
    registry = RuleRegistry(allow_unverified=True)
    ipchun = datetime(2026, 2, 4, 5, 2, tzinfo=KST)
    gyeongchip = datetime(2026, 3, 5, 22, 59, tzinfo=KST)

    assert month_pillar_for_datetime(ipchun - timedelta(minutes=1), registry).branch is EarthlyBranch.CHUK
    assert month_pillar_for_datetime(ipchun - timedelta(minutes=1), registry).stem is HeavenlyStem.GI
    assert month_pillar_for_datetime(ipchun, registry).branch is EarthlyBranch.IN
    assert month_pillar_for_datetime(ipchun, registry).stem is HeavenlyStem.GYEONG
    assert month_pillar_for_datetime(gyeongchip, registry).branch is EarthlyBranch.MYO
    assert month_pillar_for_datetime(gyeongchip, registry).stem is HeavenlyStem.SIN
