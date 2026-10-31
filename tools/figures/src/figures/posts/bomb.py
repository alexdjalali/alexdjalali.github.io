"""How I learned to love the bomb: one skeptic, a chain reaction."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, circ

SLUG = "how-i-learned-to-love-the-bomb"

LEVELS = 5


@register(SLUG)
def bomb(_ctx: FigureContext) -> Figure:
    """Draw a five-level doubling tree that ends in a red wash."""
    f, rows = Fig(), []
    for lv in range(LEVELS):
        cnt, y = 2**lv, 14 + lv * 16
        rows.append([(10 + (80 / cnt) * (i + 0.5), y) for i in range(cnt)])
    for lv in range(LEVELS):
        for x, y in rows[lv]:
            f.pop(circ(x, y, 3.2 - lv * 0.5, [B, K, K, K, R][lv]), dt=0.02)
        if lv < LEVELS - 1:
            for i, p in enumerate(rows[lv]):
                f.line(p, rows[lv + 1][2 * i], dt=0.02).line(p, rows[lv + 1][2 * i + 1], dt=0.02)
    f.wash(f'<ellipse cx="50" cy="80" rx="44" ry="7" fill="{R}"></ellipse>', 0.55)
    f.text(58, 15, "1 skeptic", 3.4, "start").text(92, 9, "2ⁿ", 4.4, "end")
    caption = "A binary tree that doubles at each of five levels, from one skeptic to a chain reaction"
    return Figure(svg=f.svg(), caption=caption)
