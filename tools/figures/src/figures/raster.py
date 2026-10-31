"""Raster outputs drawn in the house style: per-post social cards, the default card, and favicons.

Everything is SVG composed here and rendered to PNG with resvg, using only the IBM Plex fonts
vendored in ``tools/figures/fonts`` (system fonts are skipped), so a card looks the same on every
machine.
"""

from __future__ import annotations

import re
import struct
import textwrap
from pathlib import Path

import resvg_py

from figures.svg import K, R, W

FONT_DIR = Path(__file__).resolve().parents[2] / "fonts"
"""Vendored IBM Plex TTFs (SIL OFL, see ``OFL.txt`` beside them)."""
OG_SIZE = (1200, 630)
"""Open Graph card size in pixels."""
ICON_SIZES = (16, 32, 180)
"""Favicon sizes: two for ``favicon.ico`` and the browser tab, 180 for the apple-touch icon."""
SITE_URL = "ALEXDJALALI.GITHUB.IO"

_SANS = 'font-family="IBM Plex Sans" font-weight="300"'
_MONO = 'font-family="IBM Plex Mono"'
_FIG_OPEN = re.compile(r'<svg class="fig" viewBox="([^"]+)"[^>]*>')
_BLEED = re.compile(r'<g filter="url\(#bleed\)"[^>]*>.*?</g>', re.DOTALL)
_FILTER_REF = re.compile(r' filter="url\(#[a-z]+\)"')


def png(svg: str, width: int, height: int) -> bytes:
    """Render ``svg`` to PNG bytes at ``width`` x ``height`` with the vendored fonts only."""
    return bytes(
        resvg_py.svg_to_bytes(
            svg_string=svg,
            width=width,
            height=height,
            skip_system_fonts=True,
            font_dirs=[str(FONT_DIR)],
            font_family="IBM Plex Serif",
            serif_family="IBM Plex Serif",
            sans_serif_family="IBM Plex Sans",
            monospace_family="IBM Plex Mono",
        )
    )


def wrap_title(title: str, width: int, max_lines: int = 4) -> list[str]:
    """Wrap ``title`` at ``width`` characters; past ``max_lines`` the last line ends in an ellipsis."""
    lines = textwrap.wrap(title, width) or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" ,.;:") + "…"
    return lines


def flatten(fig_svg: str) -> str:
    """Drop the watercolour filters: halo groups go, washes keep their flat fill and opacity.

    The site's displacement filters depend on the browser's filter-region rules; resvg resolves
    them differently, so cards draw the washes flat, as Byrne's plates do.
    """
    return _FILTER_REF.sub("", _BLEED.sub("", fig_svg))


def _place(fig_svg: str, x: float, y: float, size: float) -> str:
    """Re-root a generated ``<svg class="fig">`` (flattened) as a nested svg at ``(x, y)``."""
    match = _FIG_OPEN.search(fig_svg)
    if match is None:
        raise ValueError('figure markup has no <svg class="fig" viewBox=...> root')
    head = f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{match.group(1)}">'
    return head + flatten(fig_svg[match.end() :])


def card_svg(kicker: str, title: str, fig_svg: str, size: int = 54, wrap: int = 19) -> str:
    """Return a 1200x630 card: mark and name, kicker, wrapped title, and the figure in a frame.

    ``title`` must already be SVG-safe (``&amp;`` for ``&``).
    """
    w, h = OG_SIZE
    lines = wrap_title(title, wrap)
    lead = size * 1.18
    top = 300 - (len(lines) - 1) * lead / 2
    text = "".join(
        f'<text x="72" y="{top + i * lead:.1f}" font-size="{size}" {_SANS} fill="{K}">{line}</text>'
        for i, line in enumerate(lines)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{W}"/>'
        f'<rect x="24" y="24" width="{w - 48}" height="{h - 48}" fill="none" '
        f'stroke="{K}" stroke-width="1.5"/>'
        f'<polygon points="72,108 108,108 72,72" fill="{R}"/>'
        f'<text x="124" y="104" font-size="34" {_SANS} fill="{K}">a.j.djalali</text>'
        f'<text x="72" y="{top - lead + 6:.1f}" font-size="18" {_MONO} letter-spacing="3" fill="{R}">'
        f"{kicker.upper()}</text>{text}"
        f'<text x="72" y="566" font-size="16" {_MONO} letter-spacing="3" fill="{K}">{SITE_URL}</text>'
        f'<rect x="660" y="65" width="500" height="500" fill="{W}" stroke="{K}" stroke-width="1.5"/>'
        f"{_place(fig_svg, 660, 65, 500)}</svg>"
    )


def mark_svg() -> str:
    """Return the site mark, the red right triangle from the header, on white."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        f'<rect width="100" height="100" fill="{W}"/>'
        f'<polygon points="12,88 88,88 12,12" fill="{R}"/></svg>'
    )


def ico(pngs: dict[int, bytes]) -> bytes:
    """Pack square PNGs (keyed by edge length) into an ICO container, smallest first."""
    sizes = sorted(pngs)
    head = struct.pack("<HHH", 0, 1, len(sizes))
    offset = 6 + 16 * len(sizes)
    entries, blobs = b"", b""
    for s in sizes:
        data = pngs[s]
        edge = 0 if s >= 256 else s
        entries += struct.pack("<BBBBHHII", edge, edge, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    return head + entries + blobs
