"""Dependency to lambda: a sentence typed and composed the way Montague did."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, Y, circ, rect, tri

SLUG = "dependency-to-lambda"

SENTENCE = "Every tall senator approved the new bill"
LOGICAL_FORM = "∀x[(tall(x) ∧ senator(x)) → approved(x, ιy[new(y) ∧ bill(y)])]"


@register(SLUG)
def montague(_ctx: FigureContext) -> Figure:
    """Draw the parse tree of the sentence with semantic types, then its logical form."""
    f = Fig()
    s, dp, vp = (50, 12), (28, 36), (72, 36)
    det, n, v, np_ = (14, 60), (40, 60), (62, 60), (86, 60)
    f.wash(circ(*s, 5.5, R)).text(s[0] + 9, s[1] + 1.4, "t")
    f.line(s, dp).line(s, vp)
    f.pop(
        f'<circle cx="{dp[0]}" cy="{dp[1]}" r="4.5" fill="none" stroke="{K}" stroke-width="0.9"></circle>'
    ).text(dp[0] - 6, dp[1] - 6, "(e→t)→t", 3)
    f.wash(tri(*vp, 5, Y)).text(vp[0] + 7, vp[1] - 6, "e→t", 3)
    f.line(dp, det).line(dp, n).line(vp, v).line(vp, np_)
    f.pop(circ(*det, 3, K)).wash(tri(*n, 4.5, Y)).pop(tri(*v, 4.5, K)).wash(
        rect(np_[0] - 4, np_[1] - 4, 8, 8, B)
    )
    for (x, y), word in [
        (det, "every"),
        (n, "tall senator"),
        (v, "approved"),
        (np_, "the new bill"),
    ]:
        f.text(x, y + 11, word, 3.4)
    f.tick(0.2).text(50, 86, LOGICAL_FORM, 2.5, italic=False)
    caption = f"Typed composition tree for the sentence “{SENTENCE}” with its logical form below"
    return Figure(svg=f.svg(), caption=caption)
