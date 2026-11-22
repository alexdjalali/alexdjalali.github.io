"""What an Interviewer Has to Keep Track Of: a d-tree of questions and the QUD stack it implies."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, W, Y, circ, rect

SLUG = "questions-under-discussion-for-interviewers"

NODES = {
    "Q": (30.0, 16.0),
    "Q.1": (14.0, 40.0),
    "Q.2": (44.0, 40.0),
    "Q.2.1": (34.0, 64.0),
    "Q.2.2": (56.0, 64.0),
}
"""The d-tree (Büring 2003): a superquestion dominating its subquestions."""
EDGES = (("Q", "Q.1"), ("Q", "Q.2"), ("Q.2", "Q.2.1"), ("Q.2", "Q.2.2"))
PATH = ("Q", "Q.2", "Q.2.1")
"""Root to the node currently under discussion."""
CLARIFICATION = "clarify"
"""A question about an utterance, pushed on top and popped without touching the inquiry."""
STACK = (CLARIFICATION, *reversed(PATH))
"""The QUD stack, top first: the clarification sits above the root-to-focus path."""

_R = 5.0
_CLAR_AT = (20.0, 84.0)


def _tree(f: Fig) -> None:
    """Draw the d-tree: path nodes washed in colour, the focus red, off-path nodes as open rings."""
    for a, b in EDGES:
        (ax, ay), (bx, by) = NODES[a], NODES[b]
        f.line((ax, ay + _R), (bx, by - _R), w=0.4 if b in PATH else 0.25)
    for name, (x, y) in NODES.items():
        if name in PATH:
            color = R if name == PATH[-1] else B
            f.wash(circ(x, y, _R, color)).text(x, y + 1.0, name, 2.6, fill=W, italic=False)
        else:
            f.ring(x, y, _R).text(x, y + 1.0, name, 2.6, italic=False)
    fx, fy = NODES[PATH[-1]]
    cx, cy = _CLAR_AT
    f.dashed((fx - 2, fy + _R), (cx + 3, cy - 3))
    f.wash(circ(cx, cy, 4.2, Y), 0.8).text(cx, cy + 1.0, CLARIFICATION, 2.2, italic=False)


def _stack(f: Fig) -> None:
    """Draw the stack on the right, top first, each cell coloured to match its tree node."""
    x, w, h = 70.0, 22.0, 9.0
    top = 30.0
    f.text(x + w / 2, top - 5, "QUD stack", 3.2)
    for i, name in enumerate(STACK):
        y = top + i * (h + 1.5)
        color = Y if name == CLARIFICATION else (R if name == PATH[-1] else B)
        fill = K if color == Y else W
        f.wash(rect(x, y, w, h, color), 0.85).text(
            x + w / 2, y + h / 2 + 1.0, name, 2.8, fill=fill, italic=False
        )
    base = top + len(STACK) * (h + 1.5)
    f.line((x - 1, base), (x + w + 1, base), w=0.5)


@register(SLUG)
def qud(_ctx: FigureContext) -> Figure:
    """Draw a d-tree of questions on the left and the stack it implies on the right."""
    f = Fig()
    _tree(f)
    f.tick(0.15)
    _stack(f)
    caption = (
        "A tree of questions, with the path from the root question to the subquestion under discussion "
        "highlighted, beside the stack it implies; a clarification request sits on top of the stack "
        "and hangs off the tree by a dashed line because it is about an utterance, not the inquiry"
    )
    return Figure(svg=f.svg(), caption=caption)
