"""Six months of enterprise development with AI: fix-or-refactor commits, with and without a theory."""

from __future__ import annotations

import math

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import Fig, R, Y, circ

SLUG = "six-months-of-enterprise-development-with-ai"

SHARES = [(28, 0.51, "no theory"), (72, 0.32, "a theory")]
"""``(centre x, share, label)`` for the two pies."""


def sector(cx: float, cy: float, r: float, frac: float) -> str:
    """Return the path of a pie sector covering ``frac`` of the circle, clockwise from the top."""
    a0, a1 = -math.pi / 2, -math.pi / 2 + 2 * math.pi * frac
    return (
        f"M{cx} {cy} L{cx + r * math.cos(a0):.2f} {cy + r * math.sin(a0):.2f} "
        f"A{r} {r} 0 {1 if frac > 0.5 else 0} 1 "
        f"{cx + r * math.cos(a1):.2f} {cy + r * math.sin(a1):.2f} Z"
    )


@register(SLUG)
def six_months(_ctx: FigureContext) -> Figure:
    """Draw two pies: 51% of commits fix or refactor without a theory, 32% with one."""
    f = Fig()
    for cx, frac, name in SHARES:
        f.ring(cx, 46, 20).wash(circ(cx, 46, 20, Y), 0.7).wash(
            f'<path d="{sector(cx, 46, 20, frac)}" fill="{R}"></path>', dt=0.2
        )
        f.text(cx, 76, f"{round(frac * 100)}%", 7, italic=False).text(cx, 83, name, 3.8)
    f.text(50, 93, "share of commits that fix or refactor", 3.2)
    caption = "Share of commits that fix or refactor: 51% without a theory, 32% with one"
    return Figure(svg=f.svg(), caption=caption)
