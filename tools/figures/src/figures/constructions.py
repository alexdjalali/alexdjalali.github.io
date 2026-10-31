"""Constructions for talks, projects and the AI-disclosure and 404 pages (no repo data needed)."""

from __future__ import annotations

from figures.model import Figure, FigureContext
from figures.svg import PRIMARIES, B, Fig, K, R, W, Y, circ, rect

LEAD = 0.2
"""Delay before a page figure starts drawing, so it follows the headline."""


def ratchet(_ctx: FigureContext) -> Figure:
    """Enforcing engineering discipline: a ratchet that only goes down."""
    f = Fig(LEAD)
    d, x, y = "M10 24", 10, 24
    for _ in range(6):
        d += f" L{x + 13:.1f} {y + 3:.1f} L{x + 13:.1f} {y + 13:.1f}"
        x, y = x + 13, y + 10
    f.path(d, w=0.9).wash(f'<path d="{d} L88 88 L10 88 Z" fill="{B}"></path>', 0.6)
    f.pop(circ(86, 84, 3, R)).text(50, 96, "violations ↓ only", 3.4)
    return Figure(f.svg(), "A staircase that only descends: guardrail violations can fall but never rise")


def three_days(_ctx: FigureContext) -> Figure:
    """Draw the TIYA course: three days, three squares."""
    f = Fig(LEAD)
    for i, (c, label) in enumerate([(B, "Generative AI"), (Y, "Agentic AI"), (R, "Advanced")]):
        x = 10 + i * 28
        f.wash(rect(x, 30, 24, 24, c)).text(x + 12, 64, f"Day {i + 1}", 3.6, italic=False).text(
            x + 12, 70, label, 3
        )
        if i < 2:
            f.line((x + 25, 42), (x + 27, 42), w=0.5)
    return Figure(f.svg(), "Three squares for the three course days: generative AI, agentic AI, advanced")


def nine_formats(_ctx: FigureContext) -> Figure:
    """Conversational document intelligence: nine formats feed one index that answers questions."""
    f = Fig(LEAD)
    for i in range(9):
        x, y = 10 + (i % 3) * 13, 20 + (i // 3) * 20
        f.pop(rect(x, y, 10, 13, PRIMARIES[i % 4]))
        f.line((x + 11, y + 6), (60, 50), w=0.25, dt=0.03)
    f.ring(74, 50, 14).wash(circ(74, 50, 14, R)).text(74, 52, "Q &amp; A", 3.6, fill=W, italic=False)
    f.text(50, 92, "9 formats → one index → answers", 3.2)
    return Figure(f.svg(), "Nine document formats feeding one index that answers questions")


def corpus(_ctx: FigureContext) -> Figure:
    """House Proceedings Corpus: 2,700 transcripts, 181 million tokens."""
    f = Fig(LEAD)
    for i in range(270):
        x, y = 8 + (i % 18) * 3.2, 14 + (i // 18) * 4.2
        f.pop(circ(x, y, 0.9, [B, K, B, R][i % 4]), dt=0.004)
    f.line((66, 45), (74, 45), w=0.6).wash(rect(76, 14, 14, 62, Y), 0.95)
    f.text(83, 82, "181M", 3.8, italic=False).text(32, 86, "2,700 transcripts", 3.4).text(
        83, 88, "tokens", 3.2
    )
    return Figure(f.svg(), "A field of dots for 2,700 transcripts condensed into 181 million tokens")


_KNN_POINTS = [
    (18, 22), (30, 70), (72, 18), (84, 66), (60, 82), (24, 44), (78, 40),
    (40, 18), (88, 86), (14, 84), (50, 60), (56, 40), (44, 52), (62, 56),
]  # fmt: skip


def knn(_ctx: FigureContext) -> Figure:
    """Enterprise search and ingestion: a query and its four nearest neighbours."""
    f = Fig(LEAD)
    for i, p in enumerate(_KNN_POINTS):
        f.pop(circ(*p, 2.2, B if i < 10 else Y), dt=0.04)
    f.ring(52, 50, 14, w=0.4).wash(circ(52, 50, 14, Y), 0.35)
    for p in _KNN_POINTS[10:]:
        f.line((52, 50), p, w=0.3, dt=0.05)
    f.pop(
        f'<rect x="49.5" y="47.5" width="5" height="5" fill="{R}" transform="rotate(45 52 50)"></rect>'
    ).text(50, 95, "query · k nearest", 3.4)
    return Figure(f.svg(), "A query point linked to its four nearest neighbours among scattered documents")


def interview(_ctx: FigureContext) -> Figure:
    """PerceptivePanda: an interview as alternating questions and answers."""
    f = Fig(LEAD)
    for i, w in enumerate([46, 30, 52, 24, 40, 34]):
        left = i % 2 == 0
        f.grow(rect(10 if left else 90 - w, 12 + i * 12, w, 7, B if left else R), dt=0.14)
    f.text(50, 94, "AI asks · customer answers", 3.4)
    return Figure(f.svg(), "Six alternating bars: the AI asks in blue, the customer answers in red")


def nl_to_viz(_ctx: FigureContext) -> Figure:
    """ClearGraph and Tableau Ask Data: words become bars."""
    f = Fig(LEAD)
    for i, w in enumerate(["sales", "by", "region", "2019"]):
        f.text(14 + i * 22, 18, w, 4.4, italic=False)
    for i, (h, c) in enumerate([(30, B), (44, R), (22, Y), (38, B)]):
        f.line((14 + i * 22, 21), (14 + i * 22, 82 - h - 2), w=0.25, dt=0.04)
        f.grow(rect(8 + i * 22, 82 - h, 12, h, c), vertical=True, dt=0.1)
    f.line((4, 82), (96, 82))
    return Figure(f.svg(), "The words “sales by region 2019” each linked to a bar in a chart")


_HASSE = {
    "∅": (50, 86), "a": (24, 62), "b": (50, 62), "c": (76, 62),
    "ab": (24, 36), "ac": (50, 36), "bc": (76, 36), "abc": (50, 12),
}  # fmt: skip
_HASSE_EDGES = [
    ("∅", "a"), ("∅", "b"), ("∅", "c"), ("a", "ab"), ("a", "ac"), ("b", "ab"),
    ("b", "bc"), ("c", "ac"), ("c", "bc"), ("ab", "abc"), ("ac", "abc"), ("bc", "abc"),
]  # fmt: skip


def hasse(_ctx: FigureContext) -> Figure:
    """Partial Order Optimality Theory: the Boolean lattice on three constraints."""
    f = Fig(LEAD)
    for lo, hi in _HASSE_EDGES:
        f.line(_HASSE[lo], _HASSE[hi], dt=0.05)
    for k, (x, y) in _HASSE.items():
        c = R if k == "abc" else B if len(k) == 2 else Y if len(k) == 1 else K
        f.wash(circ(x, y, 4.2, c), dt=0.06).text(x + 7, y + 1.3, k, 3.4, "start")
    return Figure(f.svg(), "The Boolean lattice on three constraints, drawn as a Hasse diagram")


def comparative(_ctx: FigureContext) -> Figure:
    """Dissertation on comparatives: Kim is taller than Lee, two degrees on a scale."""
    f = Fig(LEAD)
    f.line((14, 86), (14, 10), w=0.4).text(10, 12, "d", 3.6)
    f.grow(rect(30, 26, 18, 60, R), vertical=True).grow(rect(60, 44, 18, 42, B), vertical=True)
    f.dashed((14, 26), (30, 26)).dashed((14, 44), (60, 44))
    f.text(39, 92, "Kim", 3.6).text(69, 92, "Lee", 3.6).text(84, 35, "≻", 6, italic=False)
    return Figure(f.svg(), "Two bars on a degree scale: Kim's height exceeds Lee's")


def ai_venn(_ctx: FigureContext) -> Figure:
    """AI disclosure: the author and Claude overlap, so the intersection is not empty."""
    f = Fig(LEAD)
    f.ring(38, 50, 26).ring(62, 50, 26)
    f.wash(circ(38, 50, 26, B), 0.6).wash(circ(62, 50, 26, Y), 0.7)
    f.raw('<clipPath id="fig-venn-clip"><circle cx="38" cy="50" r="26"></circle></clipPath>')
    f.wash(f'<circle cx="62" cy="50" r="26" fill="{R}" clip-path="url(#fig-venn-clip)"></circle>')
    f.text(24, 52, "author", 3.8).text(76, 52, "Claude", 3.8).text(50, 52, "site", 3.8, fill=W, italic=False)
    f.text(50, 92, "A ∩ C ≠ ∅", 4, italic=False)
    return Figure(f.svg(), "Two overlapping circles, author and Claude, whose intersection is the site")


def not_found(_ctx: FigureContext) -> Figure:
    """404: a triangle whose angles sum to 190 degrees, so the page cannot exist."""
    f = Fig(LEAD)
    a, b, c = (16, 80), (84, 80), (50, 20)
    f.wash(f'<polygon points="16,80 84,80 50,20" fill="{Y}"></polygon>', 0.8)
    f.line(a, b, w=0.5).line(b, c, w=0.5).line(c, a, w=0.5)
    f.text(26, 76, "70°", 3.8).text(74, 76, "60°", 3.8).text(50, 32, "60°", 3.8)
    f.text(50, 92, "Σ = 190° ⊥", 4.4, italic=False, fill=R)
    return Figure(f.svg(), "A triangle with angles of 70, 60 and 60 degrees summing to 190: a contradiction")
