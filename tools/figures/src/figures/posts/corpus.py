"""Your docs are a corpus now: one stack of markdown files wired to its three readers."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, W, Y, circ, rect, tri

SLUG = "your-docs-are-a-corpus-now"

FILES = "1,266"
"""Markdown files in the bundle: 1,128 under ``docs/`` plus 138 READMEs."""

SHEETS = [(37.0, 37.0, 0.45), (40.0, 40.0, 0.65), (43.0, 43.0, 0.9)]
"""``(x, y, opacity)`` of each sheet in the stack, back to front; every sheet is 14 x 18."""

READERS = [
    ("people", (50.0, 13.0), (50.0, 37.0), (50.0, 19.0)),
    ("wiki", (17.0, 76.0), (40.0, 58.0), (22.0, 72.0)),
    ("index", (83.0, 76.0), (57.0, 61.0), (78.0, 72.0)),
]
"""``(label, centre, line start on the stack, line end at the reader)`` for each reader."""


def reader_shape(label: str, x: float, y: float) -> str:
    """Return a reader's mark: red circle (people), blue square (wiki), black triangle (index)."""
    if label == "people":
        return circ(x, y, 6, R)
    if label == "wiki":
        return rect(x - 5.5, y - 5.5, 11, 11, B)
    return tri(x, y - 0.8, 6.5, K)


@register(SLUG)
def corpus(_ctx: FigureContext) -> Figure:
    """Draw a yellow stack of sheets joined by three lines to people, the wiki and the index."""
    f = Fig()
    for x, y, opacity in SHEETS:
        f.wash(rect(x, y, 14, 18, Y), opacity)
    for k in range(4):
        f.pop(rect(46.0, 46.6 + 3 * k, 8.0 - 2 * (k % 2), 0.6, K), dt=0.03)
    for _, _, start, end in READERS:
        f.line(start, end, w=0.4, dt=0.08)
    for label, (x, y), _, _ in READERS:
        f.wash(reader_shape(label, x, y), 0.85)
        if label == "people":
            f.text(x, y + 1.2, label, 3.2, fill=W)
        else:
            f.text(x, y + 12, label, 3.8)
    f.text(50, 94, f"{FILES} files · one OKF bundle · three readers", 3.2)
    caption = (
        "A stack of 1,266 markdown files joined by three lines to its readers: "
        "people, the wiki and the retrieval index"
    )
    return Figure(svg=f.svg(), caption=caption)
