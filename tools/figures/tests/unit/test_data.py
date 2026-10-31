"""Unit tests for the locations and timeline loaders, run against the real data files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from figures.data import HORIZON, fractional_year, load_locations, load_timeline

pytestmark = pytest.mark.unit


def test_fractional_year() -> None:
    """Months become fractions of a year; an empty end means ongoing."""
    assert fractional_year("1988-07-01") == 1988.5
    assert fractional_year("") == HORIZON


def test_locations_match_the_data_file(repo_root: Path) -> None:
    """One place per row, with a positive span."""
    path = repo_root / "data" / "locations.json"
    places = load_locations(path)
    assert len(places) == len(json.loads(path.read_text(encoding="utf-8")))
    assert all(p.end > p.start for p in places)


def test_timeline_lanes(repo_root: Path) -> None:
    """Education is its own lane; the entries tagged ``side`` land in the side lane; the rest are work."""
    path = repo_root / "data" / "timeline.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    entries = load_timeline(path)
    assert len(entries) == len(rows)
    for row, entry in zip(rows, entries, strict=True):
        expected = "education" if row["type"] == "education" else row.get("lane", "work")
        assert entry.lane == expected
    assert {e.lane for e in entries} == {"education", "work", "side"}
