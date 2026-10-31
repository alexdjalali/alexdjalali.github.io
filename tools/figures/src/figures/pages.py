"""Figures tied to one page: data-driven ones (research, lifeline, career lanes) and the constructions."""

from __future__ import annotations

from figures import constructions as c
from figures.bib import output_by_year
from figures.constructions import LEAD
from figures.data import HORIZON
from figures.model import Figure, FigureContext
from figures.registry import FigureBuilder
from figures.svg import PRIMARIES, B, Fig, R, Y, rect

_KIND_COLOURS = (("paper", B), ("dissertation", Y), ("patent", R))
_LANES = {
    "education": (20, B, "Education"),
    "work": (44, R, "Work"),
    "side": (68, Y, "Side"),
}


def research_output(ctx: FigureContext) -> Figure:
    """Stack papers (blue), the dissertation (yellow) and patents (red) for each year."""
    counts = output_by_year(ctx.bib)
    if not counts:
        raise ValueError("research_output: no bibliography entries (is static/bib empty?)")
    years = list(range(min(y for y, _ in counts), max(y for y, _ in counts) + 1))
    tallest = max(sum(counts.get((yr, k), 0) for k, _ in _KIND_COLOURS) for yr in years)
    unit = min(9.0, 60.0 / tallest)
    bw, x0 = 80 / len(years), 12
    f = Fig(LEAD + 0.1).line((x0, 80), (92, 80), dt=0.1)
    for i, yr in enumerate(years):
        x, y = x0 + i * bw, 80.0
        for kind, colour in _KIND_COLOURS:
            n = counts.get((yr, kind), 0)
            if n:
                h = n * unit
                f.grow(rect(x + 0.6, y - h, bw - 1.2, h, colour), vertical=True, dt=0.05)
                y -= h
        if yr % 4 == 3 or yr == years[-1]:
            f.text(x + bw / 2, 86, str(yr), 3, italic=False, dt=0.01)
    for colour, name, lx in [(B, "papers", 14), (Y, "dissertation", 38), (R, "patents", 70)]:
        f.pop(rect(lx, 9, 3.2, 3.2, colour)).text(lx + 4.5, 12, name, 3.2, "start")
    first, last = years[0], years[-1]
    return Figure(
        f.svg(),
        f"Stacked bars of research output per year from {first} to {last}: "
        "papers, the dissertation and patents",
    )


def lifeline(ctx: FigureContext) -> Figure:
    """Draw the places lived, 1984 to now, as one measured line with a bar per place."""
    y0, y1 = 1984, HORIZON

    def xs(y: float) -> float:
        return 4 + (y - y0) / (y1 - y0) * 92

    f = Fig(LEAD).line((4, 50), (96, 50), w=0.3, dt=0.1)
    for i, place in enumerate(ctx.locations):
        x0, x1 = xs(place.start), xs(place.end)
        mid, up = (x0 + x1) / 2, i % 2 == 0
        f.grow(rect(x0, 46, x1 - x0, 8, PRIMARIES[i % 4]), dt=0.08)
        f.line((mid, 46 if up else 54), (mid, 40 if up else 60), w=0.2, dt=0.01)
        f.text(mid, 37 if up else 64.5, place.short, 2.6, dt=0.02)
    for yr in range(1984, int(HORIZON) + 1, 10):
        f.text(xs(yr), 74, str(yr), 2.6, italic=False, dt=0.01)
    svg = f.svg(ratio="3 / 1", view="0 25 100 55", marks=False)
    return Figure(
        svg, f"A timeline from 1984 to now with one bar for each of {len(ctx.locations)} places lived"
    )


def career_lanes(ctx: FigureContext) -> Figure:
    """Draw education, work and side-work entries as bars in three lanes."""
    y0, y1 = 1999, HORIZON

    def xs(y: float) -> float:
        return 18 + (y - y0) / (y1 - y0) * 78

    f = Fig(LEAD)
    for ly, _colour, name in _LANES.values():
        f.line((18, ly + 8), (96, ly + 8), w=0.2, dt=0.04).text(2, ly + 5, name, 3, "start", italic=False)
    for i, e in enumerate(ctx.timeline):
        ly, colour, _ = _LANES[e.lane]
        width = max(0.8, xs(e.end) - xs(e.start))
        f.grow(rect(xs(e.start), ly + (i % 2) * 4, width, 3.4, colour), dt=0.06)
    for yr in range(2000, int(HORIZON) + 1, 5):
        f.line((xs(yr), 88), (xs(yr), 90), w=0.2, dt=0.01).text(
            xs(yr), 95, str(yr), 2.6, italic=False, dt=0.01
        )
    svg = f.svg(ratio="2 / 1", view="0 10 100 90", marks=False)
    return Figure(svg, f"Career lanes from 1999 to now with a bar for each of {len(ctx.timeline)} entries")


PAGE_FIGURES: dict[str, FigureBuilder] = {
    "pages/research-output": research_output,
    "pages/lifeline": lifeline,
    "pages/career-lanes": career_lanes,
    "pages/ai-venn": c.ai_venn,
    "pages/not-found": c.not_found,
    "pages/scout": c.scout,
    "talks/enforcing-engineering-discipline": c.ratchet,
    "talks/tiya-applied-ai": c.three_days,
    "projects/conversational-document-intelligence": c.nine_formats,
    "projects/house-proceedings-corpus": c.corpus,
    "projects/enterprise-search-ingestion": c.knn,
    "projects/perceptivepanda": c.interview,
    "projects/cleargraph-ask-data": c.nl_to_viz,
    "projects/poot": c.hasse,
    "projects/dissertation": c.comparative,
}
"""Page figures keyed ``<kind>/<key>``, the path of the partial under ``figures/``."""

CARD_FIGURES: dict[str, FigureBuilder] = {"definition": c.definition}
"""Figures drawn only into social cards (``og-default.png``); no partial is written for them."""
