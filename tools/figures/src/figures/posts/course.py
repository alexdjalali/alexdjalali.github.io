"""Professional software engineering course: Orion, a deliberately broken system."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, Y, rect

SLUG = "professional-software-engineering-for-ai-and-distributed-systems"

NODES = {
    "api": (50, 16),
    "auth": (20, 36),
    "svc": (50, 42),
    "queue": (80, 36),
    "db": (30, 70),
    "cache": (70, 70),
    "llm": (50, 84),
}
GOOD = [("api", "svc"), ("api", "auth"), ("svc", "db"), ("svc", "cache"), ("queue", "svc")]
BROKEN = [("auth", "db"), ("cache", "llm"), ("api", "queue")]


@register(SLUG)
def course(_ctx: FigureContext) -> Figure:
    """Draw the service graph; students inherit the red edges and repair them."""
    f = Fig()
    for a, b in GOOD:
        f.line(NODES[a], NODES[b], w=0.4)
    for a, b in BROKEN:
        f.line(NODES[a], NODES[b], w=0.9, color=R)
        mx, my = (NODES[a][0] + NODES[b][0]) / 2, (NODES[a][1] + NODES[b][1]) / 2
        f.pop(
            f'<g transform="translate({mx:.2f} {my:.2f})">'
            f'<line x1="-2.4" y1="-2.4" x2="2.4" y2="2.4" stroke="{K}" stroke-width="0.8"></line>'
            f'<line x1="-2.4" y1="2.4" x2="2.4" y2="-2.4" stroke="{K}" stroke-width="0.8"></line></g>'
        )
    for name, (x, y) in NODES.items():
        f.wash(rect(x - 5, y - 4, 10, 8, B if name != "llm" else Y), dt=0.06)
    f.text(50, 96, "inherit · diagnose · defend", 3.4)
    caption = (
        "A service graph with five sound edges and three broken red edges "
        "that students inherit, diagnose and defend"
    )
    return Figure(svg=f.svg(), caption=caption)
