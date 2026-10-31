"""SVG primitives for the Byrne-style figures.

A figure is a ``Fig``: parts accumulate on a timeline, each carrying an animation class and a
staggered ``animation-delay``. Output is byte-stable (fixed-precision numbers, no randomness).
The ``wc`` and ``bleed`` filters are defined once in the page shell, so a figure only references
them; the motion CSS gives each ``an-*`` class its keyframes.
"""

from __future__ import annotations

PALETTE = {
    "red": "#D62718",
    "yellow": "#F5C400",
    "blue": "#1F4E9E",
    "black": "#111111",
    "white": "#FFFFFF",
}
R, Y, B, K, W = (PALETTE[n] for n in ("red", "yellow", "blue", "black", "white"))
PRIMARIES = [R, Y, B, K]


class Fig:
    """Accumulates SVG parts on a timeline; ``t`` is the next part's animation delay in seconds."""

    def __init__(self, base: float = 0.0) -> None:
        """Start a figure whose first part is delayed by ``base`` seconds."""
        self.t = base
        self.parts: list[str] = []

    def tick(self, dt: float) -> Fig:
        """Advance the timeline by ``dt`` seconds."""
        self.t += dt
        return self

    def _d(self) -> str:
        return f"animation-delay: {self.t:.2f}s"

    def line(
        self,
        a: tuple[float, float],
        b: tuple[float, float],
        w: float = 0.3,
        dt: float = 0.06,
        color: str = K,
    ) -> Fig:
        """Draw a line from ``a`` to ``b`` that strokes itself on."""
        self.parts.append(
            f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
            f'stroke="{color}" stroke-width="{w}" pathLength="1" class="an-draw" '
            f'style="{self._d()}"></line>'
        )
        return self.tick(dt)

    def dashed(
        self, a: tuple[float, float], b: tuple[float, float], w: float = 0.35, dt: float = 0.05
    ) -> Fig:
        """Fade in a dashed guide line from ``a`` to ``b``."""
        self.parts.append(
            f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
            f'stroke="{K}" stroke-width="{w}" stroke-dasharray="1.4 1" class="an-fade" '
            f'style="{self._d()}"></line>'
        )
        return self.tick(dt)

    def ring(self, cx: float, cy: float, r: float, w: float = 0.3, dt: float = 0.1) -> Fig:
        """Draw a circle outline that strokes itself on, starting at twelve o'clock."""
        self.parts.append(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" fill="none" stroke="{K}" '
            f'stroke-width="{w}" pathLength="1" class="an-draw" '
            f'transform="rotate(-90 {cx:.2f} {cy:.2f})" style="{self._d()}"></circle>'
        )
        return self.tick(dt)

    def path(self, d: str, w: float = 0.4, color: str = K, dt: float = 0.1) -> Fig:
        """Draw an SVG path that strokes itself on."""
        self.parts.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" pathLength="1" '
            f'class="an-draw" style="{self._d()}"></path>'
        )
        return self.tick(dt)

    def wash(self, shape: str, opacity: float = 0.9, dt: float = 0.12) -> Fig:
        """Bloom a watercolour wash of ``shape``: a soft bleed halo plus a rough-edged body."""
        self.parts.append(
            f'<g class="an-bloom" style="{self._d()}">'
            f'<g filter="url(#bleed)" opacity="0.48" style="mix-blend-mode: multiply">{shape}</g>'
            f'<g filter="url(#wc)" opacity="{opacity}" style="mix-blend-mode: multiply">'
            f"{shape}</g></g>"
        )
        return self.tick(dt)

    def pop(self, shape: str, dt: float = 0.05) -> Fig:
        """Pop ``shape`` in with a small overshoot."""
        self.parts.append(f'<g class="an-pop" style="{self._d()}">{shape}</g>')
        return self.tick(dt)

    def grow(self, shape: str, vertical: bool = False, dt: float = 0.12) -> Fig:
        """Grow ``shape`` from its left edge, or from its bottom edge when ``vertical``."""
        cls = "an-growy" if vertical else "an-grow"
        self.parts.append(f'<g class="{cls}" style="{self._d()}">{shape}</g>')
        return self.tick(dt)

    def text(
        self,
        x: float,
        y: float,
        s: str,
        size: float = 3.6,
        anchor: str = "middle",
        italic: bool = True,
        fill: str = K,
        dt: float = 0.04,
    ) -> Fig:
        """Fade in a label; ``s`` must already be SVG-safe (``&amp;`` for ``&``)."""
        style = ' font-style="italic"' if italic else ""
        self.parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}"{style} '
            f'fill="{fill}" class="an-fade" style="{self._d()}">{s}</text>'
        )
        return self.tick(dt)

    def raw(self, s: str) -> Fig:
        """Append pre-built markup unchanged."""
        self.parts.append(s)
        return self

    def svg(self, ratio: str = "1", view: str = "0 0 100 100", marks: bool = True) -> str:
        """Return the finished ``<svg class="fig">``; ``build.wrap`` adds the accessible name."""
        body = "".join(self.parts)
        tail = f'<g aria-hidden="true">{registration()}</g>' if marks else ""
        return f'<svg class="fig" viewBox="{view}" style="aspect-ratio: {ratio}">{body}{tail}</svg>'


def registration() -> str:
    """Return drafting crosshairs; the dashed rings turn slowly, like little gears."""
    out: list[str] = []
    for cx, cy in [(4, 4), (96, 4), (4, 96), (96, 96)]:
        out.append(
            f'<line x1="{cx - 2.2}" y1="{cy}" x2="{cx + 2.2}" y2="{cy}" stroke="{K}" '
            f'stroke-width="0.25"></line>'
            f'<line x1="{cx}" y1="{cy - 2.2}" x2="{cx}" y2="{cy + 2.2}" stroke="{K}" '
            f'stroke-width="0.25"></line>'
            f'<circle cx="{cx}" cy="{cy}" r="1.3" fill="none" stroke="{K}" stroke-width="0.25" '
            f'stroke-dasharray="0.5 0.5" class="an-spin"></circle>'
        )
    return "".join(out)


def rect(x: float, y: float, w: float, h: float, c: str) -> str:
    """Return a filled rectangle."""
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{c}"></rect>'


def circ(x: float, y: float, r: float, c: str) -> str:
    """Return a filled circle."""
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{c}"></circle>'


def tri(x: float, y: float, s: float, c: str) -> str:
    """Return a filled upward triangle centred on ``(x, y)`` with half-width ``s``."""
    return (
        f'<polygon points="{x:.2f},{y - s:.2f} {x + s:.2f},{y + s * 0.85:.2f} '
        f'{x - s:.2f},{y + s * 0.85:.2f}" fill="{c}"></polygon>'
    )
