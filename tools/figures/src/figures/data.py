"""Load ``data/locations.json`` and ``data/timeline.json`` into typed values."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from figures.model import Lane, Place, TimelineEntry

HORIZON = 2026.9
"""End of the time axis, and the end of any ongoing entry. A constant, so output stays byte-stable."""


def fractional_year(iso: str) -> float:
    """Convert ``YYYY-MM-DD`` to a fractional year; an empty string means ongoing."""
    if not iso:
        return HORIZON
    d = date.fromisoformat(iso)
    return d.year + (d.month - 1) / 12


def load_locations(path: Path) -> list[Place]:
    """Return the places lived, in file order."""
    rows: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    return [
        Place(fractional_year(r["startdate"]), fractional_year(r.get("enddate", "")), r["shorttitle"])
        for r in rows
    ]


def _lane(row: dict[str, Any]) -> Lane:
    if row.get("type") == "education":
        return "education"
    return "side" if row.get("lane") == "side" else "work"


def load_timeline(path: Path) -> list[TimelineEntry]:
    """Return the education and work entries, in file order, each assigned a lane."""
    rows: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    return [
        TimelineEntry(
            start=fractional_year(r["startdate"]),
            end=fractional_year(r.get("enddate", "")),
            title=r["title"],
            short=r.get("shorttitle", r["title"]),
            type=r["type"],
            lane=_lane(r),
        )
        for r in rows
    ]
