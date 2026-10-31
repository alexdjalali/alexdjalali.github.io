"""Top 50 techniques for distributed engineering: seven replicas, a partition, a majority of four."""

from __future__ import annotations

import math

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import Fig, K, R, W, circ

SLUG = "top-50-techniques-for-distributed-engineering"

MAJORITY = [0, 4, 5, 6]
MINORITY = [1, 2, 3]


@register(SLUG)
def distributed(_ctx: FigureContext) -> Figure:
    """Draw seven nodes split by a partition; the four-node side can still commit."""
    f, n, r = Fig(), 7, 32
    pts = [
        (
            50 + r * math.cos(2 * math.pi * k / n - math.pi / 2),
            50 + r * math.sin(2 * math.pi * k / n - math.pi / 2),
        )
        for k in range(n)
    ]
    for side in (MAJORITY, MINORITY):
        for a, i in enumerate(side):
            for j in side[a + 1 :]:
                f.line(pts[i], pts[j], dt=0.04)
    for i in MAJORITY:
        f.wash(circ(*pts[i], 5, R), dt=0.08)
    for i in MINORITY:
        f.pop(
            f'<circle cx="{pts[i][0]:.2f}" cy="{pts[i][1]:.2f}" r="4" fill="{W}" '
            f'stroke="{K}" stroke-width="0.4"></circle>'
        )
    f.tick(0.2).line((70, 6), (50, 96), w=0.6).text(22, 96, "4 &gt; 7 / 2", 3.8)
    caption = "Seven replicas split by a network partition; the four-node majority can still commit"
    return Figure(svg=f.svg(), caption=caption)
