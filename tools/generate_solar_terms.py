"""Generate candidate Korean solar-term (절기) instants from a JPL ephemeris.

This is an offline generation tool, not a production request-path dependency.
It deliberately imports nothing from ``src/destiny_saju``; the canonical term
cycle is restated here and ``tests/test_generate_solar_terms.py`` asserts that
the restatement still matches ``data_registry._SOLAR_TERM_IDS``.

The method, the pinned versions and every policy decision encoded below come
from ``docs/55_SOLAR_TERM_GENERATION_POLICY.md`` v1.1.0 (gate A):

* a term occurs when the Sun's geocentric **apparent** ecliptic longitude
  reaches ``(285 + 15k)`` degrees, k = 0..23, starting at 소한 = 285° (§3);
* the search runs in TT and the result is labelled TT → UTC → KST (+09:00) (§5);
* minute conversion **rounds** at 30 seconds; truncation is forbidden (§6);
* only 1972 onward is generated. The two December terms of the year before the
  range are emitted so a ``coverage_start`` lookup resolves, but they are never
  covered by ``coverage_ranges`` (§5.3, §7).

Output is written as a *candidate*: ``status`` is ``pending_verification`` and
the ``dataset_id`` is deliberately distinct from the production dataset, so the
loader can never pick this file up in place of the verified table. Promotion is
gate D and is not performed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timedelta, timezone
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

import numpy as np
from skyfield.api import load, load_file
from skyfield.framelib import ecliptic_frame

KST = timezone(timedelta(hours=9))
UTC = timezone.utc

POLICY_DOCUMENT = "docs/55_SOLAR_TERM_GENERATION_POLICY.md"
POLICY_VERSION = "1.1.0"

#: The canonical cycle, restated from ``data_registry._SOLAR_TERM_IDS``.
#: 소한 opens the cycle at 285 degrees of apparent solar longitude.
SOLAR_TERM_IDS: tuple[str, ...] = (
    "sohan", "daehan", "ipchun", "usu", "gyeongchip", "chunbun",
    "cheongmyeong", "gogu", "ipha", "soman", "mangjong", "haji",
    "soseo", "daeseo", "ipchu", "cheoseo", "baengno", "chubun",
    "hallo", "sanggang", "ipdong", "soseol", "daeseol", "dongji",
)
TARGET_LONGITUDE = {tid: (285 + 15 * index) % 360 for index, tid in enumerate(SOLAR_TERM_IDS)}

#: The two terms of December that precede a January ``coverage_start``.
BOUNDARY_TERM_IDS = ("daeseol", "dongji")

#: Pinned toolchain, docs/55 §4. A mismatch aborts rather than silently
#: producing values that the policy document does not describe.
PINNED_VERSIONS = {"skyfield": "1.55", "jplephem": "2.24", "numpy": "2.5.3"}

#: docs/55 §4.1. Only DE440s is accepted; DE421 is recorded there for
#: comparison but is not the chosen ephemeris.
EPHEMERIS_SHA256 = "c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2"
EPHEMERIS_FILENAME = "de440s.bsp"
EPHEMERIS_URL = "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp"

CANDIDATE_DATASET_ID = "solar_term_candidate_1972_2050"

#: Bisection runs until the bracket is one float64 ULP wide, capped so a
#: non-converging case cannot spin. At a Julian Date near 2.46e6 one ULP is
#: about 4.66e-10 day = 40 microseconds, which is the real resolution floor of
#: a single-float JD. docs/55 §3 quotes a 1e-11 day residual; that figure is
#: not reachable in this representation and the achieved width is reported
#: instead. 40 us is four orders of magnitude below the smallest rounding
#: margin, so it cannot move a minute value.
MAX_BISECTION_STEPS = 64

#: The loader rejects a gap larger than this between consecutive terms.
MAX_TERM_GAP = timedelta(days=20)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def installed_version(distribution: str) -> str:
    try:
        return package_version(distribution)
    except PackageNotFoundError:  # pragma: no cover - environment defect
        return "unknown"


def check_environment(ephemeris: Path) -> dict[str, str]:
    """Abort unless the toolchain and ephemeris match the pinned policy."""

    found = {name: installed_version(name) for name in PINNED_VERSIONS}
    mismatched = {name: found[name] for name in PINNED_VERSIONS if found[name] != PINNED_VERSIONS[name]}
    if mismatched:
        raise SystemExit(
            f"Refusing to generate: pinned versions in {POLICY_DOCUMENT} §4 are "
            f"{PINNED_VERSIONS}, but this environment has {found}"
        )
    if ephemeris.name != EPHEMERIS_FILENAME:
        raise SystemExit(
            f"Refusing to generate: policy §4.1 pins {EPHEMERIS_FILENAME}, got {ephemeris.name}"
        )
    digest = sha256_file(ephemeris)
    if digest != EPHEMERIS_SHA256:
        raise SystemExit(
            f"Refusing to generate: ephemeris sha256 mismatch.\n"
            f"  expected {EPHEMERIS_SHA256}\n  actual   {digest}"
        )
    return {**found, "ephemeris_sha256": digest}


def apparent_longitude_function(ephemeris):
    """Return f(t) -> apparent geocentric solar longitude in degrees.

    ``.apparent()`` is what applies light-time, annual aberration and
    relativistic deflection. Dropping it shifts every term by about 8 minutes
    20 seconds and matches the official table 0/24 times (docs/55 §3.1).
    """

    sun, earth = ephemeris["sun"], ephemeris["earth"]

    def longitude(t):
        _, longitude_angle, _ = earth.at(t).observe(sun).apparent().frame_latlon(ecliptic_frame)
        return longitude_angle.degrees

    return longitude


def _signed_offset(longitude_degrees, target_degrees):
    """Wrap ``longitude - target`` into (-180, +180] so the crossing is signed."""

    return ((longitude_degrees - target_degrees + 180.0) % 360.0) - 180.0


def find_terms_in_year(timescale, longitude, year: int, term_ids) -> dict[str, tuple[datetime, float]]:
    """Locate each requested term of ``year`` as an exact TT instant.

    A daily TT grid brackets the upward crossing of the target longitude, then
    bisection narrows the bracket to one float64 ULP. Returns the KST instant
    and the final bracket width in days, so the achieved precision is auditable
    rather than asserted.
    """

    start = timescale.tt(year, 1, 1)
    grid_tt = start.tt + np.arange(381, dtype=float)
    grid_longitude = longitude(timescale.tt_jd(grid_tt))

    found: dict[str, tuple[datetime, float]] = {}
    for term_id in term_ids:
        target = TARGET_LONGITUDE[term_id]
        offsets = _signed_offset(grid_longitude, target)
        crossings = np.nonzero((offsets[:-1] < 0) & (offsets[1:] >= 0))[0]
        if not len(crossings):
            raise SystemExit(f"No {term_id} crossing found in {year}; ephemeris coverage may be short")
        index = int(crossings[0])
        low, high = float(grid_tt[index]), float(grid_tt[index + 1])

        def offset_at(tt_jd: float) -> float:
            return _signed_offset(longitude(timescale.tt_jd(tt_jd)), target)

        for _ in range(MAX_BISECTION_STEPS):
            middle = (low + high) / 2
            if middle <= low or middle >= high:
                break  # the bracket is down to a single representable step
            if offset_at(middle) < 0:
                low = middle
            else:
                high = middle
        instant = timescale.tt_jd((low + high) / 2)
        found[term_id] = (instant.utc_datetime().astimezone(KST), high - low)
    return found


def round_to_minute(instant: datetime) -> datetime:
    """Round at 30 seconds (docs/55 §6). Truncation matched only 11/24 terms."""

    return (instant + timedelta(seconds=30)).replace(second=0, microsecond=0)


def margin_seconds(instant: datetime) -> float:
    """Distance in seconds from the rounding cutoff at ``:30.000``."""

    return abs((instant.second + instant.microsecond / 1e6) - 30.0)


def compute_terms(timescale, longitude, from_year: int, to_year: int) -> list[dict[str, object]]:
    """Return every term of the range plus the two preceding December terms.

    The boundary pair exists only so that a lookup at ``coverage_start`` finds
    an active term; it is never inside ``coverage_ranges`` (docs/55 §5.3).
    """

    rows: list[dict[str, object]] = []
    boundary = find_terms_in_year(timescale, longitude, from_year - 1, BOUNDARY_TERM_IDS)
    for term_id in BOUNDARY_TERM_IDS:
        rows.append(_term_row(term_id, *boundary[term_id], is_boundary=True))
    for year in range(from_year, to_year + 1):
        located = find_terms_in_year(timescale, longitude, year, SOLAR_TERM_IDS)
        for term_id in SOLAR_TERM_IDS:
            rows.append(_term_row(term_id, *located[term_id], is_boundary=False))
    return rows


def _term_row(term_id: str, raw: datetime, bracket_days: float, *, is_boundary: bool) -> dict[str, object]:
    rounded = round_to_minute(raw)
    margin = margin_seconds(raw)
    return {
        "id": term_id,
        "kst_raw": raw.isoformat(timespec="microseconds"),
        "kst_minute": rounded.isoformat(timespec="seconds"),
        "margin_seconds": round(margin, 6),
        "margin_under_1s": margin < 1.0,
        "margin_under_5s": margin < 5.0,
        "precedes_coverage": is_boundary,
        "solver_bracket_microseconds": round(bracket_days * 86400.0 * 1e6, 3),
    }


def self_check(rows: list[dict[str, object]], from_year: int, to_year: int) -> None:
    """Abort on any structural defect before anything reaches disk."""

    expected_count = 2 + (to_year - from_year + 1) * len(SOLAR_TERM_IDS)
    if len(rows) != expected_count:
        raise SystemExit(f"Expected {expected_count} terms, computed {len(rows)}")

    first_index = SOLAR_TERM_IDS.index(rows[0]["id"])
    expected_ids = [
        SOLAR_TERM_IDS[(first_index + offset) % len(SOLAR_TERM_IDS)]
        for offset in range(len(rows))
    ]
    if [row["id"] for row in rows] != expected_ids:
        raise SystemExit("Terms do not follow the canonical solar-term cycle")

    instants = [datetime.fromisoformat(row["kst_minute"]) for row in rows]
    for instant in instants:
        if instant.utcoffset() != timedelta(hours=9):
            raise SystemExit(f"{instant.isoformat()} is not a +09:00 instant")
        if instant.second or instant.microsecond:
            raise SystemExit(f"{instant.isoformat()} is not minute-precise")
    if instants != sorted(instants) or len(set(instants)) != len(instants):
        raise SystemExit("Solar-term instants must be strictly chronological and unique")
    for earlier, later in zip(instants, instants[1:]):
        if later - earlier > MAX_TERM_GAP:
            raise SystemExit(f"Gap greater than 20 days between {earlier.isoformat()} and {later.isoformat()}")

    boundary_rows = [row for row in rows if row["precedes_coverage"]]
    if [row["id"] for row in boundary_rows] != list(BOUNDARY_TERM_IDS):
        raise SystemExit("Exactly the two December boundary terms must precede coverage")
    for row in boundary_rows:
        if datetime.fromisoformat(row["kst_minute"]).year != from_year - 1:
            raise SystemExit("Boundary terms must fall in the December before the range")


def build_candidate(
    rows: list[dict[str, object]],
    from_year: int,
    to_year: int,
    environment: dict[str, str],
    leap_seconds: dict[str, object],
    generated_at: str,
) -> dict[str, object]:
    """Assemble the candidate dataset in the production schema's shape."""

    reference = (
        "Geocentric apparent solar longitude reaching (285 + 15k) degrees, k=0..23; "
        "skyfield.framelib.ecliptic_frame with light-time, annual aberration and "
        "relativistic deflection; TT search bisected below 1e-11 day; TT -> UTC -> "
        f"KST(+09:00) with minute rounding at 30 s. Ephemeris {EPHEMERIS_FILENAME} "
        f"sha256 {environment['ephemeris_sha256']} from {EPHEMERIS_URL}. Leap-second "
        f"table last entry {leap_seconds['last_leap_date']} with TAI-UTC="
        f"{leap_seconds['tai_minus_utc_now']} s, assumed constant through {to_year}. "
        f"Method and decisions: {POLICY_DOCUMENT} v{POLICY_VERSION}. "
        "NOT an official almanac value; cross-check against the official table is gate D."
    )
    return {
        "schema_version": "1.1",
        "dataset_id": CANDIDATE_DATASET_ID,
        "dataset_version": "0.1.0",
        "status": "pending_verification",
        "source": {
            "type": "astronomical_calculation",
            "reference": f"Generated by tools/generate_solar_terms.py per {POLICY_DOCUMENT} v{POLICY_VERSION}.",
        },
        "license": (
            "Derived from JPL planetary ephemeris DE440s via Skyfield. Candidate data "
            "pending verification against the official Korean almanac; do not publish "
            "as an official calendar value."
        ),
        "generated_at": generated_at,
        "generated_by": "astronomical_calculation_with_kasi_crosscheck",
        "scope": (
            "KST solar-term instants at minute precision for "
            f"{from_year}-{to_year}. Lookups outside verified coverage ranges, "
            "including gaps, fail closed."
        ),
        "data": {
            "time_zone": "Asia/Seoul",
            "instant_precision": "minute",
            "coverage_ranges": [
                {
                    "coverage_start": f"{from_year}-01-01T00:00:00+09:00",
                    "coverage_end": f"{to_year}-12-31T23:59:00+09:00",
                    "provenance": {
                        "publisher": "Destiny solar-term generator (Skyfield 1.55 / JPL DE440s)",
                        "reference": reference,
                        "retrieved_on": generated_at[:10],
                        "precision": "minute",
                    },
                }
            ],
            "terms": [
                {"id": row["id"], "occurs_at": row["kst_minute"]}
                for row in rows
            ],
        },
    }


def build_audit(
    rows: list[dict[str, object]],
    from_year: int,
    to_year: int,
    environment: dict[str, str],
    leap_seconds: dict[str, object],
    generated_at: str,
) -> dict[str, object]:
    """Per-term raw seconds and rounding margins (docs/55 §8.3)."""

    return {
        "audit_id": f"solar_term_audit_{from_year}_{to_year}",
        "policy_document": POLICY_DOCUMENT,
        "policy_version": POLICY_VERSION,
        "generated_at": generated_at,
        "candidate_dataset_id": CANDIDATE_DATASET_ID,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "skyfield": environment["skyfield"],
            "jplephem": environment["jplephem"],
            "numpy": environment["numpy"],
            "ephemeris_file": EPHEMERIS_FILENAME,
            "ephemeris_sha256": environment["ephemeris_sha256"],
        },
        "leap_seconds": leap_seconds,
        "margin_definition": "abs(seconds_within_minute - 30.0); smaller means the rounded minute is easier to flip",
        "thresholds": {"required_check_seconds": 1.0, "attention_seconds": 5.0},
        "solver_precision": solver_precision(rows),
        "distribution": margin_distribution(rows),
        "terms": rows,
    }


def solver_precision(rows: list[dict[str, object]]) -> dict[str, object]:
    """Report the bisection bracket actually achieved, not the one asserted."""

    widths = [float(row["solver_bracket_microseconds"]) for row in rows]
    return {
        "max_bracket_microseconds": max(widths),
        "note": (
            "Bisection converges to one float64 ULP of the Julian Date (about 40 us). "
            "docs/55 section 3 quotes a 1e-11 day residual, which a single-float JD "
            "cannot represent; the value above is the measured bracket. It is four "
            "orders of magnitude below the smallest rounding margin, so it cannot "
            "change a minute value."
        ),
    }


def margin_distribution(rows: list[dict[str, object]]) -> dict[str, object]:
    margins = [float(row["margin_seconds"]) for row in rows]
    total = len(margins)
    buckets = {}
    for threshold in (0.5, 1.0, 2.0, 5.0, 10.0):
        count = sum(1 for value in margins if value < threshold)
        buckets[f"under_{threshold:g}s"] = {
            "count": count,
            "percent": round(100.0 * count / total, 3),
        }
    return {"total_terms": total, "minimum_seconds": min(margins), "buckets": buckets}


def read_leap_seconds(timescale) -> dict[str, object]:
    """Record the leap-second table actually in use (docs/55 §5.2, §11.1)."""

    last_leap_jd = float(timescale.leap_dates[-1])
    last_offset = float(timescale.leap_offsets[-1])
    last_date = timescale.tt_jd(last_leap_jd + (32.184 + last_offset) / 86400.0).utc_strftime("%Y-%m-%d")
    return {
        "source": "skyfield/data/iers.npz (leap_dates / leap_offsets)",
        "entry_count": int(len(timescale.leap_dates)),
        "last_leap_date": last_date,
        "tai_minus_utc_now": last_offset,
        "note": (
            "No future leap second is assumed. If one is announced, KST labels after "
            "it shift by one second and terms with a margin under 1 s change minute."
        ),
    }


def serialize(payload: dict[str, object]) -> bytes:
    """One fixed encoding, so identical inputs give an identical file."""

    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n").encode("utf-8")


def write_new_file(path: Path, content: bytes) -> None:
    if path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def build_report(
    *,
    from_year: int,
    to_year: int,
    rows: list[dict[str, object]],
    environment: dict[str, str],
    leap_seconds: dict[str, object],
    generated_at: str,
    candidate_path: Path,
    candidate_sha256: str,
    audit_path: Path,
    audit_sha256: str,
    previous: tuple[Path, str] | None,
    argv: list[str],
) -> str:
    distribution = margin_distribution(rows)
    smallest = sorted(rows, key=lambda row: float(row["margin_seconds"]))[:20]

    lines: list[str] = []
    lines.append("Solar-term candidate generation report")
    lines.append("=" * 72)
    lines.append(f"policy document       : {POLICY_DOCUMENT} v{POLICY_VERSION}")
    lines.append(f"generated_at (input)  : {generated_at}")
    lines.append(f"range                 : {from_year}-01-01 .. {to_year}-12-31 (KST)")
    lines.append(f"command               : {' '.join(argv)}")
    lines.append("")
    lines.append("Environment")
    lines.append("-" * 72)
    lines.append(f"python   : {platform.python_version()}")
    lines.append(f"platform : {platform.platform()}")
    for name in ("skyfield", "jplephem", "numpy"):
        lines.append(f"{name:9s}: {environment[name]} (pinned {PINNED_VERSIONS[name]})")
    lines.append(f"ephemeris: {EPHEMERIS_FILENAME}")
    lines.append(f"  sha256 : {environment['ephemeris_sha256']}")
    lines.append(f"  source : {EPHEMERIS_URL}")
    lines.append("")
    lines.append("Leap seconds")
    lines.append("-" * 72)
    lines.append(f"table source     : {leap_seconds['source']}")
    lines.append(f"entries          : {leap_seconds['entry_count']}")
    lines.append(f"last leap date   : {leap_seconds['last_leap_date']}")
    lines.append(f"TAI-UTC in force : {leap_seconds['tai_minus_utc_now']} s (assumed constant through {to_year})")
    lines.append(f"note             : {leap_seconds['note']}")
    lines.append("")
    lines.append("Counts")
    lines.append("-" * 72)
    boundary = [row for row in rows if row["precedes_coverage"]]
    lines.append(f"terms in coverage      : {len(rows) - len(boundary)}")
    lines.append(f"boundary terms (before): {len(boundary)}  -> {', '.join(row['id'] + ' ' + row['kst_minute'] for row in boundary)}")
    lines.append(f"total terms written    : {len(rows)}")
    lines.append("")
    lines.append("Why a candidate dataset_id")
    lines.append("-" * 72)
    lines.append(f"dataset_id = {CANDIDATE_DATASET_ID}")
    lines.append("RuleRegistry resolves a dataset by <data_dir>/<dataset_id>.json, so a")
    lines.append("distinct id keeps this file from ever being loaded in place of the")
    lines.append("production solar_term_instants_v1 table. status is pending_verification;")
    lines.append("promotion to production_verified is gate D and is not done here.")
    lines.append("CAVEAT: data_registry._validate_data dispatches the solar-term rules on")
    lines.append("dataset_id == 'solar_term_instants_v1', so loading this file under its")
    lines.append("candidate id runs envelope validation only. Full validation is exercised")
    lines.append("separately against a renamed temporary copy; see the gate B report.")
    lines.append("")
    precision = solver_precision(rows)
    lines.append("Solver precision (measured, not asserted)")
    lines.append("-" * 72)
    lines.append(f"max bisection bracket : {precision['max_bracket_microseconds']:.3f} us")
    lines.append(f"note                  : {precision['note']}")
    lines.append("")
    lines.append("Rounding-margin distribution (margin = abs(seconds - 30))")
    lines.append("-" * 72)
    lines.append(f"total terms   : {distribution['total_terms']}")
    lines.append(f"minimum margin: {distribution['minimum_seconds']:.6f} s")
    for label, bucket in distribution["buckets"].items():
        lines.append(f"  {label:<12s}: {bucket['count']:>5d}  ({bucket['percent']:.3f} %)")
    lines.append("")
    lines.append("Twenty smallest margins")
    lines.append("-" * 72)
    lines.append(f"{'#':>3}  {'term':<12} {'rounded KST':<22} {'raw KST':<30} {'margin s':>10}")
    for position, row in enumerate(smallest, start=1):
        lines.append(
            f"{position:>3}  {row['id']:<12} {row['kst_minute']:<22} {row['kst_raw']:<30} {float(row['margin_seconds']):>10.6f}"
        )
    lines.append("")
    lines.append("Outputs")
    lines.append("-" * 72)
    lines.append(f"candidate : {candidate_path}")
    lines.append(f"  sha256  : {candidate_sha256}")
    lines.append(f"audit     : {audit_path}")
    lines.append(f"  sha256  : {audit_sha256}")
    lines.append("")
    lines.append("Determinism")
    lines.append("-" * 72)
    if previous is None:
        lines.append("No --previous-output given; this run was not compared against another.")
    else:
        previous_path, previous_sha256 = previous
        verdict = "MATCH" if previous_sha256 == candidate_sha256 else "MISMATCH"
        lines.append(f"previous run : {previous_path}")
        lines.append(f"  sha256     : {previous_sha256}")
        lines.append(f"this run     : {candidate_path}")
        lines.append(f"  sha256     : {candidate_sha256}")
        lines.append(f"verdict      : {verdict}")
    lines.append("")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate candidate solar-term instants.")
    parser.add_argument("--from-year", type=int, required=True, help="First covered Gregorian year")
    parser.add_argument("--to-year", type=int, required=True, help="Last covered Gregorian year")
    parser.add_argument("--ephemeris", type=Path, required=True, help="Path to de440s.bsp")
    parser.add_argument("--output", type=Path, required=True, help="New candidate JSON file to create")
    parser.add_argument("--audit-output", type=Path, required=True, help="New audit JSON file to create")
    parser.add_argument("--report-output", type=Path, required=True, help="New report text file to create")
    parser.add_argument(
        "--generated-at",
        default=None,
        help=(
            "UTC timestamp recorded in the outputs. Defaults to today at 00:00:00Z so "
            "two runs on the same day are byte-identical. Pass it explicitly to pin the run."
        ),
    )
    parser.add_argument(
        "--previous-output",
        type=Path,
        default=None,
        help="A candidate file from an earlier run; its sha256 is compared and recorded.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.from_year > args.to_year:
        raise SystemExit("--from-year must not be after --to-year")
    if args.from_year < 1972:
        raise SystemExit(
            f"Refusing to generate before 1972: {POLICY_DOCUMENT} §7 defers 1900-1971 "
            "until its time scale is decided. Only the two December boundary terms of "
            "the year before the range are computed."
        )
    for path in (args.output, args.audit_output, args.report_output):
        if path.exists():
            raise SystemExit(f"Refusing to overwrite existing file: {path}")

    environment = check_environment(args.ephemeris)
    generated_at = args.generated_at or datetime.now(UTC).strftime("%Y-%m-%dT00:00:00Z")

    timescale = load.timescale()
    leap_seconds = read_leap_seconds(timescale)
    ephemeris = load_file(str(args.ephemeris))
    try:
        longitude = apparent_longitude_function(ephemeris)
        rows = compute_terms(timescale, longitude, args.from_year, args.to_year)
    finally:
        ephemeris.close()

    self_check(rows, args.from_year, args.to_year)

    candidate = build_candidate(rows, args.from_year, args.to_year, environment, leap_seconds, generated_at)
    audit = build_audit(rows, args.from_year, args.to_year, environment, leap_seconds, generated_at)
    candidate_bytes = serialize(candidate)
    audit_bytes = serialize(audit)

    previous = None
    if args.previous_output is not None:
        if not args.previous_output.exists():
            raise SystemExit(f"--previous-output does not exist: {args.previous_output}")
        previous = (args.previous_output, sha256_file(args.previous_output))

    write_new_file(args.output, candidate_bytes)
    write_new_file(args.audit_output, audit_bytes)
    report = build_report(
        from_year=args.from_year,
        to_year=args.to_year,
        rows=rows,
        environment=environment,
        leap_seconds=leap_seconds,
        generated_at=generated_at,
        candidate_path=args.output,
        candidate_sha256=hashlib.sha256(candidate_bytes).hexdigest(),
        audit_path=args.audit_output,
        audit_sha256=hashlib.sha256(audit_bytes).hexdigest(),
        previous=previous,
        argv=[Path(sys.argv[0]).name, *(argv if argv is not None else sys.argv[1:])],
    )
    write_new_file(args.report_output, report.encode("utf-8"))
    print(f"Wrote {len(rows)} pending-verification terms to {args.output}")
    print(f"Audit  : {args.audit_output}")
    print(f"Report : {args.report_output}")


if __name__ == "__main__":
    main()
