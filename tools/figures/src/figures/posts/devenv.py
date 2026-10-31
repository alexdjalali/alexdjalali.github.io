"""My development environment: one terminal split into neovim, git and zsh."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, W, Y, circ, rect

SLUG = "my-development-environment"

PANES = [(12, 22, 46, 60, B, "nvim"), (60, 22, 28, 28, R, "git"), (60, 52, 28, 30, Y, "zsh")]


@register(SLUG)
def devenv(_ctx: FigureContext) -> Figure:
    """Draw a black terminal window split into three coloured panes."""
    f = Fig()
    f.wash(rect(10, 14, 80, 70, K), 0.95)
    for x, y, w, h, c, name in PANES:
        f.grow(rect(x, y, w, h, c), dt=0.15).text(
            x + 2, y + 5, name, 3.4, "start", italic=False, fill=W if c != Y else K
        )
    for k in range(3):
        f.pop(circ(15 + k * 4, 18, 1.1, W), dt=0.05)
    f.raw(f'<rect x="64" y="72" width="2.2" height="3.6" fill="{K}" class="an-blink"></rect>')
    f.text(50, 94, "$ ./install.sh", 3.6, italic=False)
    caption = "A terminal window split into neovim, git and zsh panes, rebuilt by one install command"
    return Figure(svg=f.svg(), caption=caption)
