"""Unit tests for the page figures, built from the repo's real data files."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from figures.bib import load_entries
from figures.data import load_locations, load_timeline
from figures.model import FigureContext
from figures.pages import PAGE_FIGURES, career_lanes, lifeline, research_output

pytestmark = pytest.mark.unit

EXPECTED_KEYS = {
    "pages/research-output",
    "pages/lifeline",
    "pages/career-lanes",
    "pages/ai-venn",
    "pages/not-found",
    "talks/enforcing-engineering-discipline",
    "talks/tiya-applied-ai",
    "projects/conversational-document-intelligence",
    "projects/house-proceedings-corpus",
    "projects/enterprise-search-ingestion",
    "projects/perceptivepanda",
    "projects/cleargraph-ask-data",
    "projects/poot",
    "projects/dissertation",
}


@pytest.fixture(scope="module")
def ctx(repo_root: Path) -> FigureContext:
    """Return a context holding the repo's real bibliography, places and timeline."""
    return FigureContext(
        slug="page",
        bib=tuple(load_entries(repo_root / "static" / "bib")),
        locations=tuple(load_locations(repo_root / "data" / "locations.json")),
        timeline=tuple(load_timeline(repo_root / "data" / "timeline.json")),
    )


def _bars(svg: str) -> int:
    return len(re.findall(r'class="an-grow(?:y)?"', svg))


def test_page_figure_keys_are_exactly_the_documented_set() -> None:
    """No page figure is missing and none is undocumented."""
    assert set(PAGE_FIGURES) == EXPECTED_KEYS


def test_lifeline_has_one_bar_per_place(ctx: FigureContext) -> None:
    """The lifeline draws every place once."""
    assert _bars(lifeline(ctx).svg) == len(ctx.locations)


def test_career_lanes_has_one_bar_per_entry(ctx: FigureContext) -> None:
    """The lanes draw every timeline entry once."""
    assert _bars(career_lanes(ctx).svg) == len(ctx.timeline)


def test_research_output_has_a_bar_segment_per_year_and_kind(ctx: FigureContext) -> None:
    """One stacked segment for each (year, kind) pair present in the bibliography."""
    pairs = {(e.year, e.kind) for e in ctx.bib}
    assert _bars(research_output(ctx).svg) == len(pairs)


@pytest.mark.parametrize("key", sorted(EXPECTED_KEYS))
def test_every_page_figure_is_deterministic_and_captioned(key: str, ctx: FigureContext) -> None:
    """Two calls give identical output; captions are non-empty; markup is an svg.fig."""
    a, b = PAGE_FIGURES[key](ctx), PAGE_FIGURES[key](ctx)
    assert a == b
    assert a.caption.strip()
    assert a.svg.startswith('<svg class="fig"')
