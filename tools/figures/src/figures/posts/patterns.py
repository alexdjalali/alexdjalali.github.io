"""100 patterns: the post's sixteen parts drawn as one hundred cells."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import PRIMARIES, Fig, rect

SLUG = "100-patterns-for-production-go-and-python"

PART_SIZES = [9, 7, 6, 3, 9, 5, 8, 7, 7, 7, 6, 5, 5, 7, 2, 7]
"""Patterns per part; sums to 100."""


@register(SLUG)
def patterns(_ctx: FigureContext) -> Figure:
    """Fill a 10×10 grid in reading order, one colour per part."""
    f, i = Fig(), 0
    for p, size in enumerate(PART_SIZES):
        for _ in range(size):
            x, y = 10 + (i % 10) * 8, 8 + (i // 10) * 8
            f.pop(rect(x + 0.6, y + 0.6, 6.8, 6.8, PRIMARIES[p % 4]), dt=0.014)
            i += 1
    for k in range(11):
        f.line((10, 8 + k * 8), (90, 8 + k * 8), w=0.25, dt=0.02).line(
            (10 + k * 8, 8), (10 + k * 8, 88), w=0.25, dt=0.02
        )
    f.text(50, 95, "XVI parts · C patterns", 3.6)
    caption = "A ten-by-ten grid of one hundred cells filled in reading order across sixteen parts"
    return Figure(svg=f.svg(), caption=caption)
