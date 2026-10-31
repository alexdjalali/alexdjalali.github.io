"""Rethinking Agile: agent build time against time until done-done, on a log scale (Table 1)."""

from __future__ import annotations

import math

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, R, rect

SLUG = "rethinking-agile-in-the-age-of-ai"

ROWS = [("Epic", 30, 2880, 10080), ("Story", 50, 90, 1440), ("Task", 70, 10, 20)]
"""``(level, y, build minutes, done-done minutes)`` from the essay's Table 1."""


@register(SLUG)
def agile(_ctx: FigureContext) -> Figure:
    """Draw build and done-done bars for epics, stories and tasks."""
    f = Fig()

    def lx(v: float) -> float:
        return 24 + v / 4.1 * 68

    f.line((lx(0), 82), (94, 82), dt=0.1)
    ticks = [
        (0, "1 min"),
        (math.log10(60), "1 hr"),
        (math.log10(1440), "1 day"),
        (math.log10(10080), "1 wk"),
    ]
    for v, t in ticks:
        f.line((lx(v), 80.5), (lx(v), 83.5), dt=0.03).text(lx(v), 88, t, 3.2, dt=0.02)
    for name, y, build, done in ROWS:
        f.text(5, y + 1.5, name, 3.8, "start", italic=False)
        f.grow(rect(lx(0), y - 6, lx(math.log10(build)) - lx(0), 5, B), dt=0.15)
        f.grow(rect(lx(0), y, lx(math.log10(done)) - lx(0), 5, R), dt=0.1)
        f.dashed((lx(math.log10(build)), y - 8), (lx(math.log10(build)), y + 7))
    f.pop(rect(24, 9, 3.5, 3.5, B)).text(29, 12.2, "agent build", 3.4, "start")
    f.pop(rect(54, 9, 3.5, 3.5, R)).text(59, 12.2, "done-done", 3.4, "start")
    caption = (
        "Agent build time against time until done-done for epics, stories and tasks, "
        "on a log scale from one minute to one week"
    )
    return Figure(svg=f.svg(), caption=caption)
