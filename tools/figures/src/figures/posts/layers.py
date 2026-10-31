"""The ideal repository structure: nine layers, dependencies pointing down only."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, W, Y, rect

SLUG = "the-ideal-repository-structure"

LAYERS = [
    "Entrypoints",
    "Controllers",
    "Workflows",
    "Pipelines",
    "Services",
    "Repositories",
    "Clients",
    "Foundation",
    "Core interfaces",
]


@register(SLUG)
def layers(_ctx: FigureContext) -> Figure:
    """Stack nine bars with a downward arrow between each pair."""
    f = Fig()
    for i, name in enumerate(LAYERS):
        y = 8 + i * 9.2
        c = R if i == len(LAYERS) - 1 else [B, Y, W, K][i % 4]
        f.grow(rect(26, y, 62, 6.6, c), dt=0.07)
        if c == W:
            f.raw(
                f'<rect x="26" y="{y}" width="62" height="6.6" fill="none" stroke="{K}" '
                f'stroke-width="0.3"></rect>'
            )
        f.text(24, y + 4.7, name, 3, "end", italic=False, dt=0.02)
    for i in range(len(LAYERS) - 1):
        y = 8 + i * 9.2 + 6.6
        f.line((92, y - 2), (92, y + 2.6), w=0.4, dt=0.03).raw(
            f'<polygon points="90.8,{y + 1.8:.2f} 93.2,{y + 1.8:.2f} 92,{y + 3:.2f}" fill="{K}" '
            f'class="an-fade" style="animation-delay: {f.t:.2f}s"></polygon>'
        )
    caption = "Nine stacked layers from entrypoints to core interfaces with dependencies pointing down only"
    return Figure(svg=f.svg(), caption=caption)
