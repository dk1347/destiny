"""Create an auditable one-year lunar-calendar snapshot from KASI's OpenAPI.

This is an offline acquisition tool, not a production request-path dependency.
It intentionally reads the API credential only from ``KASI_SERVICE_KEY`` and
does not print it. Review the generated JSON before promoting any portion into
a versioned Destiny dataset.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from xml.etree import ElementTree


API_URL = "https://apis.data.go.kr/B090041/openapi/service/LrsrCldInfoService/getLunCalInfo"


def _child_text(parent: ElementTree.Element, name: str) -> str:
    value = parent.findtext(name)
    if value is None or not value.strip():
        raise ValueError(f"KASI response is missing {name}")
    return value.strip()


def parse_lunar_day_response(payload: bytes) -> dict[str, object]:
    """Parse one successful KASI solar-date response without retaining a key."""

    root = ElementTree.fromstring(payload)
    header = root.find("./header")
    if header is None:
        raise ValueError("KASI response is missing header")
    if _child_text(header, "resultCode") != "00":
        raise ValueError(f"KASI request failed: {_child_text(header, 'resultMsg')}")
    item = root.find("./body/items/item")
    if item is None:
        raise ValueError("KASI response contains no calendar item")
    return {
        "solar_date": "-".join((
            _child_text(item, "solYear"),
            _child_text(item, "solMonth").zfill(2),
            _child_text(item, "solDay").zfill(2),
        )),
        "lunar_year": int(_child_text(item, "lunYear")),
        "lunar_month": int(_child_text(item, "lunMonth")),
        "lunar_day": int(_child_text(item, "lunDay")),
        "is_leap_month": _child_text(item, "lunLeapmonth") == "윤",
        "lunar_month_days": int(_child_text(item, "lunNday")),
    }


def fetch_lunar_day(service_key: str, civil_date: date) -> dict[str, object]:
    query = urlencode({
        "ServiceKey": service_key,
        "solYear": f"{civil_date.year:04d}",
        "solMonth": f"{civil_date.month:02d}",
        "solDay": f"{civil_date.day:02d}",
    })
    with urlopen(f"{API_URL}?{query}", timeout=30) as response:  # noqa: S310 - fixed HTTPS endpoint
        return parse_lunar_day_response(response.read())


def build_year_snapshot(year: int, service_key: str) -> dict[str, object]:
    """Fetch every Gregorian day in one year, preserving the official mapping."""

    current = date(year, 1, 1)
    final = date(year + 1, 1, 1)
    entries: list[dict[str, object]] = []
    while current < final:
        entry = fetch_lunar_day(service_key, current)
        if entry["solar_date"] != current.isoformat():
            raise ValueError(f"KASI response date mismatch for {current.isoformat()}")
        entries.append(entry)
        current += timedelta(days=1)
    return {
        "schema_version": "1.0.0",
        "dataset_id": "kasi_lunar_calendar_snapshot",
        "status": "pending_verification",
        "source": {
            "publisher": "Korea Astronomy and Space Science Institute (KASI)",
            "reference": "data.go.kr dataset 15012679 / getLunCalInfo",
            "retrieved_for_solar_year": year,
        },
        "entries": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True, help="Gregorian year to acquire")
    parser.add_argument("--output", type=Path, required=True, help="New JSON file to create")
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {args.output}")
    service_key = os.environ.get("KASI_SERVICE_KEY")
    if not service_key:
        raise SystemExit("KASI_SERVICE_KEY is required; do not put the key in the command or repository.")
    snapshot = build_year_snapshot(args.year, service_key)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(snapshot['entries'])} pending-verification entries to {args.output}")


if __name__ == "__main__":
    main()
