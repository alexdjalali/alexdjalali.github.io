"""Frozen value types shared by the loaders, the registry and the builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BibKind = Literal["paper", "dissertation", "patent"]
Lane = Literal["education", "work", "side"]


@dataclass(frozen=True, slots=True)
class BibEntry:
    """One BibTeX entry from ``static/bib``."""

    key: str
    """Cite key, which is also the file stem."""
    year: int
    """Publication year."""
    title: str
    """Title as written in the entry."""
    venue: str
    """Journal, proceedings, school or patent note; empty when the entry has none."""
    authors: str
    """Author field as written."""
    kind: BibKind
    """``patent`` and ``dissertation`` are detected from the key; everything else is a paper."""


@dataclass(frozen=True, slots=True)
class Place:
    """A place lived, from ``data/locations.json``."""

    start: float
    """Start as a fractional year (``1988.5`` is mid-1988)."""
    end: float
    """End as a fractional year."""
    short: str
    """Short label drawn on the lifeline."""


@dataclass(frozen=True, slots=True)
class TimelineEntry:
    """One education or work entry from ``data/timeline.json``."""

    start: float
    """Start as a fractional year."""
    end: float
    """End as a fractional year; ongoing entries end at the current build horizon."""
    title: str
    """Full title."""
    short: str
    """Short title."""
    type: str
    """``education`` or ``job`` as written in the data."""
    lane: Lane
    """Lane the career-lanes figure draws it in."""


@dataclass(frozen=True, slots=True)
class Figure:
    """A finished figure: the SVG markup and a one-sentence description of what it plots."""

    svg: str
    """``<svg class="fig">`` markup."""
    caption: str
    """Accessible description; never empty."""


@dataclass(frozen=True, slots=True)
class FigureContext:
    """Everything a builder may read: its slug and the repo data."""

    slug: str
    """Post slug, or the page key for page figures."""
    bib: tuple[BibEntry, ...]
    """All bibliography entries."""
    locations: tuple[Place, ...]
    """Places lived, in order."""
    timeline: tuple[TimelineEntry, ...]
    """Education and work entries, in order."""
