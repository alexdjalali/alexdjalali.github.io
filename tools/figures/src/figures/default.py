"""Default construction: a geometric cover derived from a slug's hash, so no post is ever blank."""

from __future__ import annotations

import hashlib
from collections.abc import Callable

from figures.model import Figure, FigureContext
from figures.svg import PRIMARIES, Fig, W, circ, rect, tri


def default_construction(slug: str) -> Callable[[FigureContext], Figure]:
    """Return a builder that draws three washed shapes chosen by ``sha256(slug)``."""
    digest = hashlib.sha256(slug.encode()).digest()

    def build(_ctx: FigureContext) -> Figure:
        h = digest
        f = Fig()
        f.raw(rect(0, 0, 100, 100, PRIMARIES[h[0] % 4] if h[0] % 3 else W))
        shapes = [
            lambda c, s: circ(50 + (h[1] % 30) - 15, 50 + (h[2] % 30) - 15, s, c),
            lambda c, s: rect(50 - s, 50 - s + (h[3] % 20) - 10, 2 * s, 2 * s, c),
            lambda c, s: tri(50 + (h[4] % 30) - 15, 54, s, c),
        ]
        for k in range(3):
            color = PRIMARIES[(h[5 + k] + k + 1) % 4]
            f.wash(shapes[h[8 + k] % 3](color, 34 - k * 10), 0.95)
        return Figure(svg=f.svg(marks=False), caption=f"Construction for {slug}")

    return build
