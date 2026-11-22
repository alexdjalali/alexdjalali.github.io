"""One Row Per Cloud: one authored descriptor row from which every per-environment artifact is derived."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, Y, circ, rect, tri

SLUG = "one-row-per-cloud"

DERIVED = ("IaC inputs", "k8s values", "ApplicationSet", "operator login")
"""What the post derives from the row, top to bottom; none of them is written by hand."""

_ROW = (8.0, 44.0, 30.0, 12.0)
"""``(x, y, w, h)`` of the descriptor row."""
_TARGET_Y = (18.0, 40.0, 62.0, 84.0)
_TARGET_X = 70.0


def _mark(i: int, x: float, y: float) -> str:
    """Return the i-th artifact's mark, cycling through the Byrne shapes and colours."""
    if i == 0:
        return rect(x - 4, y - 4, 8, 8, B)
    if i == 1:
        return circ(x, y, 4.2, R)
    if i == 2:
        return tri(x, y - 0.6, 4.6, K)
    return rect(x - 4, y - 4, 8, 8, Y)


@register(SLUG)
def one_row(_ctx: FigureContext) -> Figure:
    """Draw a yellow row on the left with one derivation line fanning out to each artifact."""
    f = Fig()
    x, y, w, h = _ROW
    f.wash(rect(x, y, w, h, Y))
    for k in range(4):
        f.pop(rect(x + 2 + k * 7, y + h / 2 - 0.3, 5, 0.6, K), dt=0.03)
    f.text(x + w / 2, y + h + 6, "one row", 3.6)
    f.tick(0.1)
    sx, sy = x + w, y + h / 2
    for ty in _TARGET_Y:
        f.path(
            f"M{sx:.2f} {sy:.2f} C{sx + 14:.2f} {sy:.2f} {_TARGET_X - 18:.2f} {ty:.2f} "
            f"{_TARGET_X - 6:.2f} {ty:.2f}",
            w=0.45,
            dt=0.08,
        )
    for i, (ty, label) in enumerate(zip(_TARGET_Y, DERIVED, strict=True)):
        f.wash(_mark(i, _TARGET_X, ty), 0.85)
        f.text(_TARGET_X + 7, ty + 1.2, label, 3.0, anchor="start")
    f.text(50, 96, "authored once · everything else derived", 2.8, fill=K, italic=True)
    caption = (
        "A single yellow descriptor row on the left, with one line fanning out to each artifact derived "
        "from it: infrastructure inputs, Kubernetes values, an Argo CD ApplicationSet and the operator login"
    )
    return Figure(svg=f.svg(), caption=caption)
