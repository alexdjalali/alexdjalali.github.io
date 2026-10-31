"""Anatomy of an AI engineering system: three model tiers, seven templates, seventeen commands."""

from __future__ import annotations

import math

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, Y, circ

SLUG = "anatomy-of-an-ai-engineering-system"

TEMPLATES = 7
COMMANDS = 17


@register(SLUG)
def anatomy(_ctx: FigureContext) -> Figure:
    """Draw three concentric tiers carrying seven template squares and seventeen command dots."""
    f = Fig()
    for radius, colour, opacity in [(38, B, 0.55), (25, Y, 0.85), (12, R, 0.9)]:
        f.ring(50, 48, radius).wash(circ(50, 48, radius, colour), opacity)
    for k in range(TEMPLATES):
        a = 2 * math.pi * k / TEMPLATES - math.pi / 2
        x, y = 50 + 25 * math.cos(a), 48 + 25 * math.sin(a)
        f.pop(
            f'<rect x="{x - 2.2:.2f}" y="{y - 2.2:.2f}" width="4.4" height="4.4" fill="{K}" '
            f'transform="rotate({math.degrees(a):.1f} {x:.2f} {y:.2f})"></rect>',
            dt=0.06,
        )
    for k in range(COMMANDS):
        a = 2 * math.pi * k / COMMANDS - math.pi / 2
        f.pop(circ(50 + 38 * math.cos(a), 48 + 38 * math.sin(a), 1.8, K), dt=0.035)
    f.text(50, 50, "3", 6, italic=False).text(50, 95, "17 commands · 7 templates · 3 tiers", 3.2)
    caption = "Three concentric model tiers carrying seven template squares and seventeen command dots"
    return Figure(svg=f.svg(), caption=caption)
