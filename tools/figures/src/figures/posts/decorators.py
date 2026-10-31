"""Decorator pattern for observability and resilience: four nested rings around a call."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, W, Y, circ, rect

SLUG = "decorator-pattern-observability-resilience"

RINGS = [("Recovery", 40, B), ("Auth", 31, Y), ("Transaction", 22, W), ("Observability", 13, K)]


@register(SLUG)
def decorators(_ctx: FigureContext) -> Figure:
    """Draw Recovery, Auth, Transaction and Observability around the service; the call unwinds."""
    f = Fig()
    for name, h, c in RINGS:
        f.wash(rect(50 - h, 50 - h, 2 * h, 2 * h, c), 0.9 if c != W else 1, dt=0.15)
        f.raw(
            f'<rect x="{50 - h}" y="{50 - h}" width="{2 * h}" height="{2 * h}" fill="none" '
            f'stroke="{K}" stroke-width="0.3"></rect>'
        )
        f.text(50, 50 - h + 4, name, 2.9, fill=W if c in (B, K) else K, italic=False)
    f.pop(circ(50, 52, 4.5, R))
    f.path("M2 30 C20 30 34 40 46 50", w=0.6).path("M54 54 C66 64 80 70 98 70", w=0.6, color=R)
    f.text(50, 97, "call in · unwind out", 3.2)
    caption = (
        "A call enters through Recovery, Auth, Transaction and Observability rings, "
        "reaches the service, then unwinds"
    )
    return Figure(svg=f.svg(), caption=caption)
