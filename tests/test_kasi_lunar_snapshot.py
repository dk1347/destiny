from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_SCRIPT = Path(__file__).parents[1] / "tools" / "kasi_lunar_snapshot.py"
_SPEC = spec_from_file_location("kasi_lunar_snapshot", _SCRIPT)
assert _SPEC and _SPEC.loader
_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def test_parse_lunar_day_response_preserves_leap_month_flag() -> None:
    payload = (Path(__file__).parent / "fixtures" / "kasi_lun_cal_info_response.xml").read_bytes()

    assert _MODULE.parse_lunar_day_response(payload) == {
        "solar_date": "2026-09-18",
        "lunar_year": 2026,
        "lunar_month": 8,
        "lunar_day": 8,
        "is_leap_month": False,
        "lunar_month_days": 30,
    }
