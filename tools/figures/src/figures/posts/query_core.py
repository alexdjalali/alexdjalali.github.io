"""One query language: a single filter tree folds into SQL, CQL and a chart."""

from __future__ import annotations

import math

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, W, Y, circ, rect, tri

SLUG = "one-query-language-from-filter-chip-to-chart"

LEAVES = ("status = indexed", "created ≥ Oct 1", "name ~ report")
"""The three leaf clauses of the example filter: (status ∧ (created ∨ name))."""
TARGETS = ("SQL", "CQL", "chart")
"""What the one tree compiles into, top to bottom."""

_ROOT, _OR = (22, 26), (33, 50)
_LEAF_AT = ((12, 50), (24, 74), (42, 74))
_TARGET_Y = (20, 50, 80)


def _edge(
    a: tuple[float, float], b: tuple[float, float], ra: float, rb: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Return the segment from ``a`` to ``b`` trimmed by node radii ``ra`` and ``rb``."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    return (a[0] + ux * ra, a[1] + uy * ra), (b[0] - ux * rb, b[1] - uy * rb)


def _tree(f: Fig) -> None:
    """Draw the filter tree: an AND root, an OR group, and three leaf clauses (edges under nodes)."""
    for a, b, ra, rb in (
        (_ROOT, _LEAF_AT[0], 5, 3.6),
        (_ROOT, _OR, 5, 4),
        (_OR, _LEAF_AT[1], 4, 3.2),
        (_OR, _LEAF_AT[2], 4, 3.2),
    ):
        start, end = _edge(a, b, ra, rb)
        f.line(start, end)
    f.wash(circ(*_ROOT, 5, R)).text(_ROOT[0], _ROOT[1] + 1.5, "∧", 4.5, fill=W, italic=False)
    f.pop(
        f'<circle cx="{_OR[0]}" cy="{_OR[1]}" r="4" fill="{W}" stroke="{K}" stroke-width="0.9"></circle>'
    ).text(_OR[0], _OR[1] + 1.4, "∨", 4, italic=False)
    shapes = (
        tri(*_LEAF_AT[0], 3.6, Y),
        rect(_LEAF_AT[1][0] - 3, _LEAF_AT[1][1] - 3, 6, 6, B),
        circ(*_LEAF_AT[2], 3.2, K),
    )
    for (x, y), shape, label in zip(_LEAF_AT, shapes, LEAVES, strict=True):
        f.wash(shape).text(x, y + 8, label, 2.5)


def _targets(f: Fig) -> None:
    """Fold the tree into each target: two query panels and a small bar chart."""
    for y in _TARGET_Y:
        f.path(f"M46 50 C52 50 52 {y} 58 {y}", w=0.5, color=R)
    sql_y, cql_y, chart_y = _TARGET_Y
    f.wash(rect(58, sql_y - 7, 36, 14, B)).text(76, sql_y + 1.2, TARGETS[0], 4, fill=W, italic=False)
    f.text(76, sql_y + 12, "WHERE … AND (… OR …)", 2.4, italic=False)
    f.wash(rect(58, cql_y - 7, 36, 14, Y)).text(76, cql_y + 1.2, TARGETS[1], 4, italic=False)
    f.text(76, cql_y + 12, "pushdown + residual", 2.4)
    base = chart_y + 7
    for i, (h, c) in enumerate(((6, K), (11, R), (8, B), (13, Y))):
        f.grow(rect(61 + i * 8, base - h, 5, h, c), vertical=True, dt=0.06)
    f.line((59, base), (93, base), w=0.3)
    f.text(76, base + 5, TARGETS[2], 3.2)


@register(SLUG)
def query_core(_ctx: FigureContext) -> Figure:
    """Draw one filter tree on the left folding into SQL, CQL and a chart on the right."""
    f = Fig()
    _tree(f)
    f.tick(0.15)
    _targets(f)
    caption = (
        "One filter tree, an AND of a status clause with an OR of a date and a name clause, "
        "folds into a SQL WHERE clause, a CQL query with a residual predicate, and a bar chart"
    )
    return Figure(svg=f.svg(), caption=caption)
