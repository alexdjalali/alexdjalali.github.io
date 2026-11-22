"""One Checkout Per Story: worktree lanes cut from one base, each landing one commit on integration."""

from __future__ import annotations

from dataclasses import dataclass

from figures.model import Figure, FigureContext
from figures.registry import register
from figures.svg import B, Fig, K, R, Y, circ, rect

SLUG = "one-checkout-per-story"


@dataclass(frozen=True)
class Lane:
    """One worktree: its label, colour, the base point it is cut from, and its height on the page."""

    label: str
    color: str
    start: tuple[float, float]
    y: float


BASE = (12.0, 82.0)
"""The shared base commit, sitting on the integration branch."""
LANES = (
    Lane("worktree 1", R, BASE, 18.0),
    Lane("worktree 2", B, BASE, 36.0),
    Lane("worktree 3", Y, BASE, 54.0),
)
"""Three parallel worktrees, all cut from the same base commit."""

_FORK_X, _TIP_X = 22.0, 50.0
_PICK_X = (88.0, 76.0, 64.0)
"""Where each lane lands, top lane farthest, so the cherry-pick arcs nest without crossing."""


@register(SLUG)
def worktrees(_ctx: FigureContext) -> Figure:
    """Draw three lanes rising from one base commit, each cherry-picked once onto the integration line."""
    f = Fig()
    bx, by = BASE
    f.line((bx, by), (94, by), w=0.6)
    f.wash(circ(bx, by, 2.6, K))
    f.text(bx, by + 8, "base", 3.0)
    f.text(94, by + 8, "integration", 3.0, anchor="end")
    for lane in LANES:
        sx, sy = lane.start
        f.line((sx, sy), (_FORK_X, lane.y), w=0.35, color=lane.color, dt=0.04)
        f.line((_FORK_X, lane.y), (_TIP_X, lane.y), w=0.35, color=lane.color, dt=0.04)
        f.text(_FORK_X + 1, lane.y - 3, lane.label, 2.8, anchor="start")
    f.tick(0.1)
    for lane in LANES:
        f.wash(rect(_TIP_X, lane.y - 2, 4, 4, lane.color))
    f.tick(0.1)
    for lane, px in zip(LANES, _PICK_X, strict=True):
        tx, ty = _TIP_X + 4, lane.y
        f.path(
            f"M{tx:.2f} {ty:.2f} C{px:.2f} {ty:.2f} {px:.2f} {ty:.2f} {px:.2f} {by - 2.2:.2f}",
            w=0.45,
            color=lane.color,
            dt=0.08,
        )
        f.pop(circ(px, by, 2.0, lane.color))
    f.text(50, 96, "one story · one worktree · one commit", 2.8)
    caption = (
        "Three worktree lanes, red, blue and yellow, are cut from one base commit; each ends in a "
        "single commit that is cherry-picked onto the integration branch"
    )
    return Figure(svg=f.svg(), caption=caption)
