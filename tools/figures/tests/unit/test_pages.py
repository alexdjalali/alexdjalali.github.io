"""Unit tests for the page figures, built from the repo's real data files."""

from __future__ import annotations

import itertools
import re
from collections.abc import Callable
from pathlib import Path

import pytest

from figures.bib import load_entries
from figures.constructions import SCALEUPS, TIYA_DAYS, cohort, days_two_three
from figures.data import load_locations, load_timeline
from figures.model import Figure, FigureContext
from figures.pages import PAGE_FIGURES, career_lanes, lifeline, research_output

pytestmark = pytest.mark.unit

EXPECTED_KEYS = {
    "pages/research-output",
    "pages/lifeline",
    "pages/career-lanes",
    "pages/ai-venn",
    "pages/not-found",
    "pages/scout",
    "talks/enforcing-engineering-discipline",
    "talks/tiya-applied-ai",
    "talks/gt-medellin-scaleups",
    "talks/tiya-applied-ai-days-2-3",
    "talks/esslli-2014-conceptual-epistemic",
    "talks/countability-2010",
    "talks/lsa-2008-bridging",
    "talks/lsa-2008-scalar",
    "talks/lsa-2007-said-implicated",
    "courses/tiya-applied-ai",
    "courses/professional-software-engineering",
    "projects/conversational-document-intelligence",
    "projects/knowledge-engine-toolkit",
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


def test_cohort_draws_ten_scaleups_around_one_campus(ctx: FigureContext) -> None:
    """The Medellín talk figure: ten scaleups (the cohort size) ringed around one campus square."""
    assert SCALEUPS == 10
    svg = cohort(ctx).svg
    assert len(re.findall(r'class="an-pop"[^>]*><circle', svg)) == SCALEUPS
    assert len(re.findall(r'<rect[^>]*width="12.00" height="12.00"', svg)) == 2  # a wash: halo + body


def test_days_two_three_washes_only_the_days_being_taught(ctx: FigureContext) -> None:
    """Days 2 and 3 are washed in colour and dated; day 1 is drawn as an outline only."""
    svg = days_two_three(ctx).svg
    assert len(re.findall(r'<rect[^>]*width="24.00" height="24.00" fill="#', svg)) == 2 * 2  # two washes
    assert len(re.findall(r'<rect[^>]*fill="none"', svg)) == 1
    for _, _, date in TIYA_DAYS[1:]:
        assert f">{date}<" in svg


@pytest.mark.parametrize("key", sorted(EXPECTED_KEYS))
def test_every_page_figure_is_deterministic_and_captioned(key: str, ctx: FigureContext) -> None:
    """Two calls give identical output; captions are non-empty; markup is an svg.fig."""
    a, b = PAGE_FIGURES[key](ctx), PAGE_FIGURES[key](ctx)
    assert a == b
    assert a.caption.strip()
    assert a.svg.startswith('<svg class="fig"')


@pytest.mark.parametrize("builder", [lifeline, career_lanes])
def test_axis_end_follows_the_horizon(
    builder: Callable[[FigureContext], Figure], ctx: FigureContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The time axis ends at ``HORIZON``, so bumping it moves the axis with the ongoing bars."""
    before = builder(ctx).svg
    monkeypatch.setattr("figures.pages.HORIZON", 2030.0)
    assert builder(ctx).svg != before


def test_research_output_with_no_bibliography_names_the_cause() -> None:
    """An empty bibliography raises a message naming the cause, not a bare ``ValueError``."""
    empty = FigureContext(slug="page", bib=(), locations=(), timeline=())
    with pytest.raises(ValueError, match="no bibliography"):
        research_output(empty)


@pytest.mark.parametrize(("builder", "year"), [(lifeline, 2034), (career_lanes, 2035)])
def test_ticks_extend_with_the_horizon(
    builder: Callable[[FigureContext], Figure], year: int, ctx: FigureContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A tick year is labelled when ``HORIZON`` reaches it and not before."""
    monkeypatch.setattr("figures.pages.HORIZON", year - 1.0)
    assert f">{year}<" not in builder(ctx).svg
    monkeypatch.setattr("figures.pages.HORIZON", float(year))
    assert f">{year}<" in builder(ctx).svg


def test_toolkit_draws_eight_layers_in_go_and_python(ctx: FigureContext) -> None:
    """Both language columns carry the same eight layers, core to transport, joined by downward arrows."""
    from figures.constructions import TOOLKIT_LAYERS, toolkit

    assert TOOLKIT_LAYERS == (
        "core", "foundation", "clients", "repos", "services", "pipelines", "workflows", "transport",
    )  # fmt: skip
    svg = toolkit(ctx).svg
    for layer in TOOLKIT_LAYERS:
        assert f">{layer}<" in svg
    assert ">Go<" in svg and ">Python<" in svg


def test_semester_draws_fifteen_week_cells_in_seven_pillar_groups(ctx: FigureContext) -> None:
    """One cell per week, coloured by pillar: runs of 3, 2, 2, 2, 2, 2, 2 weeks, labelled with Orion."""
    from figures.constructions import SEMESTER_GROUPS, semester

    assert SEMESTER_GROUPS == (3, 2, 2, 2, 2, 2, 2)
    svg = semester(ctx).svg
    cells = re.findall(r'<g class="an-pop"[^>]*><rect[^>]*fill="([^"]+)"', svg)
    assert len(cells) == 15
    runs = [len(list(group)) for _, group in itertools.groupby(cells)]
    assert runs == list(SEMESTER_GROUPS)
    assert ">Orion<" in svg


@pytest.mark.parametrize(
    ("name", "labels"),
    [
        ("mediated", (">language<", ">concepts<", ">world<")),
        (
            "three_ingredients",
            (">extension<", ">ontological type<", ">morphosyntactic class<", ">count / mass<"),
        ),
        ("bridging", (">focus<", ">referent A<", ">referent B<")),
        ("scalar", (">some<", ">most<", ">all<", ">not all<")),
        ("gradient", (">said<", ">implicated<")),
    ],
)
def test_academic_talk_figures_label_what_each_talk_argues(name: str, labels: tuple[str, ...]) -> None:
    """Each moved academic talk's figure names the terms its argument turns on.

    Why this test is important: the five talks moved from Research to Talks need figures that encode
    their claims, not decoration; a dropped or renamed label means the figure no longer says it.
    What it tests: every expected label is in the builder's SVG, and the caption is non-empty.
    """
    from figures import constructions

    fig = getattr(constructions, name)(FigureContext(slug="page", bib=(), locations=(), timeline=()))
    for label in labels:
        assert label in fig.svg, (name, label)
    assert fig.caption


def test_academic_talk_figures_encode_their_structure() -> None:
    """The figures' shapes carry the argument, not just the labels.

    Why this test is important: a label can survive while the structure it names is lost.
    What it tests: concepts alone are washed between language and world; bridging washes one of two
    referents and leaves the other dashed; the gradient draws ``GRADIENT_STEPS`` cells.
    """
    from figures.constructions import GRADIENT_STEPS, bridging, gradient, mediated

    empty = FigureContext(slug="page", bib=(), locations=(), timeline=())
    assert len(re.findall(r'class="an-bloom"', mediated(empty).svg)) == 1
    b = bridging(empty).svg
    assert len(re.findall(r'class="an-bloom"', b)) == 1
    assert "stroke-dasharray" in b
    assert len(re.findall(r'class="an-pop"[^>]*><rect', gradient(empty).svg)) == GRADIENT_STEPS == 7
