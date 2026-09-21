"""Tests for the offline solar-term generator.

The generator needs Skyfield and a JPL ephemeris (``de440s.bsp``, ~32 MB). The
ephemeris is deliberately not committed (docs/55 §4.1), so every test that
actually runs a generation skips when either is unavailable. One test parses
the tool's source instead of importing it, so the canonical term cycle is
guarded even in an environment without Skyfield.

Point ``DESTINY_DE440S_PATH`` at the ephemeris to exercise the full set.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

from destiny_saju.data_registry import _SOLAR_TERM_IDS

KST = timezone(timedelta(hours=9))
_REPO_ROOT = Path(__file__).parents[1]
_SCRIPT = _REPO_ROOT / "tools" / "generate_solar_terms.py"
_CANONICAL = _REPO_ROOT / "src" / "destiny_saju" / "data" / "saju" / "solar_term_instants_v1.json"
_DEFAULT_EPHEMERIS = Path("/tmp/deph/de440s.bsp")

_GENERATED_AT = "2026-09-20T00:00:00Z"


def _source_constant(name: str):
    """Read a literal assignment out of the tool without importing Skyfield."""

    tree = ast.parse(_SCRIPT.read_text(encoding="utf-8"))
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) and node.value else []
        )
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name:
                return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in {_SCRIPT}")


def _ephemeris_path() -> Path:
    return Path(os.environ.get("DESTINY_DE440S_PATH", _DEFAULT_EPHEMERIS))


def _load_tool():
    pytest.importorskip("skyfield", reason="Skyfield is an offline-tool dependency only")
    pytest.importorskip("numpy", reason="numpy is an offline-tool dependency only")
    spec = spec_from_file_location("generate_solar_terms", _SCRIPT)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def tool():
    return _load_tool()


@pytest.fixture(scope="module")
def ephemeris() -> Path:
    path = _ephemeris_path()
    if not path.is_file():
        pytest.skip(
            f"ephemeris not present at {path}; it is not committed (docs/55 §4.1). "
            "Set DESTINY_DE440S_PATH to run generation tests."
        )
    return path


def _generate(tool, ephemeris: Path, destination: Path, from_year: int, to_year: int) -> Path:
    candidate = destination / "candidate.json"
    tool.main([
        "--from-year", str(from_year),
        "--to-year", str(to_year),
        "--ephemeris", str(ephemeris),
        "--output", str(candidate),
        "--audit-output", str(destination / "audit.json"),
        "--report-output", str(destination / "report.txt"),
        "--generated-at", _GENERATED_AT,
    ])
    return candidate


@pytest.fixture(scope="module")
def generated_2026(tool, ephemeris, tmp_path_factory) -> dict:
    destination = tmp_path_factory.mktemp("solar_terms_2026")
    candidate = _generate(tool, ephemeris, destination, 2026, 2026)
    return json.loads(candidate.read_text(encoding="utf-8"))


# --- always runs, no third-party dependency ---------------------------------

def test_tool_restates_the_canonical_solar_term_cycle() -> None:
    """The tool may not import src/, so its copy of the cycle must not drift."""

    assert tuple(_source_constant("SOLAR_TERM_IDS")) == _SOLAR_TERM_IDS


def test_tool_targets_fifteen_degree_steps_from_sohan() -> None:
    ids = _source_constant("SOLAR_TERM_IDS")

    assert ids[0] == "sohan"
    assert len(ids) == 24


# --- generation tests, skipped without Skyfield or the ephemeris ------------

def test_minute_conversion_rounds_at_thirty_seconds(tool) -> None:
    """docs/55 §6: round at :30, never truncate."""

    base = datetime(2026, 6, 21, 17, 24, tzinfo=KST)

    assert tool.round_to_minute(base.replace(second=29, microsecond=900000)).minute == 24
    assert tool.round_to_minute(base.replace(second=30)).minute == 25
    assert tool.round_to_minute(base.replace(second=59, microsecond=999999)).minute == 25
    assert tool.round_to_minute(base.replace(second=0)).minute == 24


def test_margin_measures_distance_from_the_rounding_cutoff(tool) -> None:
    base = datetime(2026, 6, 21, 17, 24, tzinfo=KST)

    assert tool.margin_seconds(base.replace(second=30)) == pytest.approx(0.0)
    assert tool.margin_seconds(base.replace(second=30, microsecond=348000)) == pytest.approx(0.348)
    assert tool.margin_seconds(base.replace(second=29, microsecond=118483)) == pytest.approx(0.881517)


def test_refuses_to_generate_before_1972(tool, tmp_path) -> None:
    """docs/55 §7 defers 1900-1971 until its time scale is decided."""

    with pytest.raises(SystemExit) as error:
        tool.main([
            "--from-year", "1971", "--to-year", "1980",
            "--ephemeris", str(tmp_path / "absent.bsp"),
            "--output", str(tmp_path / "c.json"),
            "--audit-output", str(tmp_path / "a.json"),
            "--report-output", str(tmp_path / "r.txt"),
        ])

    assert "1972" in str(error.value)


def test_refuses_to_overwrite_an_existing_output(tool, tmp_path) -> None:
    existing = tmp_path / "c.json"
    existing.write_text("{}", encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        tool.main([
            "--from-year", "1972", "--to-year", "1972",
            "--ephemeris", str(tmp_path / "absent.bsp"),
            "--output", str(existing),
            "--audit-output", str(tmp_path / "a.json"),
            "--report-output", str(tmp_path / "r.txt"),
        ])

    assert "Refusing to overwrite" in str(error.value)


def test_generated_2026_minutes_match_the_verified_table(generated_2026) -> None:
    """The 26 published instants (2025 boundary pair + 2026) must reproduce."""

    canonical = json.loads(_CANONICAL.read_text(encoding="utf-8"))
    expected = [(row["id"], row["occurs_at"]) for row in canonical["data"]["terms"]]
    produced = [(row["id"], row["occurs_at"]) for row in generated_2026["data"]["terms"]]

    assert produced == expected


def test_candidate_never_claims_production_verification(generated_2026) -> None:
    assert generated_2026["status"] == "pending_verification"
    assert generated_2026["dataset_id"] != "solar_term_instants_v1"
    assert generated_2026["generated_by"] == "astronomical_calculation_with_kasi_crosscheck"

    provenance = generated_2026["data"]["coverage_ranges"][0]["provenance"]
    assert set(provenance) == {"publisher", "reference", "retrieved_on", "precision"}
    assert "KASI" not in provenance["publisher"]
    assert "Korea Astronomy" not in provenance["publisher"]


def test_terms_follow_the_cycle_in_strict_ascending_order(tool, ephemeris, tmp_path) -> None:
    candidate = _generate(tool, ephemeris, tmp_path, 1972, 1973)
    terms = json.loads(candidate.read_text(encoding="utf-8"))["data"]["terms"]

    assert len(terms) == 2 + 2 * 24

    first = _SOLAR_TERM_IDS.index(terms[0]["id"])
    expected = [_SOLAR_TERM_IDS[(first + offset) % 24] for offset in range(len(terms))]
    assert [row["id"] for row in terms] == expected

    instants = [datetime.fromisoformat(row["occurs_at"]) for row in terms]
    assert instants == sorted(instants)
    assert len(set(instants)) == len(instants)
    assert all(instant.utcoffset() == timedelta(hours=9) for instant in instants)
    assert all(instant.second == 0 and instant.microsecond == 0 for instant in instants)


def test_exactly_two_boundary_terms_precede_the_coverage_start(tool, ephemeris, tmp_path) -> None:
    """docs/55 §5.3: 대설 and 동지 of the prior December, and nothing else."""

    candidate = _generate(tool, ephemeris, tmp_path, 1972, 1972)
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    coverage_start = datetime.fromisoformat(payload["data"]["coverage_ranges"][0]["coverage_start"])
    before = [
        row for row in payload["data"]["terms"]
        if datetime.fromisoformat(row["occurs_at"]) < coverage_start
    ]

    assert [row["id"] for row in before] == ["daeseol", "dongji"]
    assert all(datetime.fromisoformat(row["occurs_at"]).year == 1971 for row in before)
    assert coverage_start.year == 1972


def test_generation_is_byte_for_byte_reproducible(tool, ephemeris, tmp_path) -> None:
    first = _generate(tool, ephemeris, tmp_path / "first", 1972, 1972)
    second = _generate(tool, ephemeris, tmp_path / "second", 1972, 1972)

    assert hashlib.sha256(first.read_bytes()).hexdigest() == hashlib.sha256(second.read_bytes()).hexdigest()


def test_audit_records_raw_seconds_and_margin_flags(tool, ephemeris, tmp_path) -> None:
    """docs/55 §8.3 keeps the pre-rounding value the dataset cannot hold."""

    _generate(tool, ephemeris, tmp_path, 2026, 2026)
    audit = json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))
    haji = next(row for row in audit["terms"] if row["id"] == "haji")

    assert haji["kst_raw"].startswith("2026-06-21T17:24:30.")
    assert haji["kst_minute"] == "2026-06-21T17:25:00+09:00"
    assert haji["margin_seconds"] < 1.0
    assert haji["margin_under_1s"] is True
    assert haji["margin_under_5s"] is True

    for row in audit["terms"]:
        assert row["margin_under_1s"] == (row["margin_seconds"] < 1.0)
        assert row["margin_under_5s"] == (row["margin_seconds"] < 5.0)
