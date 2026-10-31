"""Render every figure, data file, social card and icon to its repo path; write them; report drift.

The composition root of the generator: it loads the repo data, builds a ``FigureContext`` per
figure, and returns ``{repo-relative path: content}`` — text for partials and data, bytes for the
PNG cards and icons. I/O happens only in the loaders and in ``write`` / ``drift``.

Raster drift is checked by presence, not bytes: the text partials are the reviewed source, and PNG
bytes may differ by a few pixels between resvg builds on different CPUs.
"""

from __future__ import annotations

import html
import json
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

import figures.posts  # noqa: F401  (importing registers the post builders)
from figures import raster
from figures.bib import load_entries, research_summary
from figures.content import post_slugs, post_titles, validate_registry
from figures.data import load_locations, load_timeline
from figures.default import default_construction
from figures.model import Figure, FigureContext
from figures.pages import PAGE_FIGURES
from figures.registry import FigureBuilder, registered

PARTIALS = Path("layouts/_partials/figures")
"""Where generated partials live, relative to the repo root."""
KINDS = ("posts", "projects", "talks", "pages")
RESEARCH_JSON = Path("data/figures/research.json")
OG_DIR = Path("static/images/og")
"""One social card per post, ``<slug>.png``."""
OG_DEFAULT = Path("static/images/og-default.png")
FAVICON_ICO = Path("static/favicon.ico")
ICONS = {
    16: Path("static/images/favicon-16x16.png"),
    32: Path("static/images/favicon-32x32.png"),
    180: Path("static/images/apple-touch-icon.png"),
}
RASTER_FILES = (OG_DEFAULT, FAVICON_ICO, *ICONS.values())
"""Fixed-name raster outputs (per-post cards live under ``OG_DIR``)."""
_DEFINITION = "A blog is a set of propositions about language, machines, and the systems between them."


def wrap(kind: str, key: str, figure: Figure) -> str:
    """Return the ``<figure>`` partial: the svg with an accessible name plus a hidden caption."""
    cap_id = f"fig-{kind}-{key}-cap"
    svg = figure.svg.replace("<svg ", f'<svg role="img" aria-labelledby="{cap_id}" ', 1)
    caption = html.escape(figure.caption)
    return (
        f'<figure class="fig-frame">{svg}'
        f'<figcaption id="{cap_id}" class="visually-hidden">{caption}</figcaption></figure>\n'
    )


def _rasters(root: Path, post_figures: Mapping[str, Figure], definition: Figure) -> dict[Path, bytes]:
    """Return the per-post social cards, the default card and the icons as PNG/ICO bytes."""
    titles = post_titles(root / "content" / "posts")
    out: dict[Path, bytes] = {}
    for slug, fig in post_figures.items():
        svg = raster.card_svg("Book I · Writing", html.escape(titles.get(slug, slug)), fig.svg)
        out[OG_DIR / f"{slug}.png"] = raster.png(svg, *raster.OG_SIZE)
    card = raster.card_svg("Definition 1.", _DEFINITION, definition.svg, size=42, wrap=26)
    out[OG_DEFAULT] = raster.png(card, *raster.OG_SIZE)
    icons = {s: raster.png(raster.mark_svg(), s, s) for s in raster.ICON_SIZES}
    out.update({ICONS[s]: data for s, data in icons.items()})
    out[FAVICON_ICO] = raster.ico({s: icons[s] for s in (16, 32)})
    return out


def render_all(root: Path, builders: Mapping[str, FigureBuilder] | None = None) -> dict[Path, str | bytes]:
    """Return every generated file as ``{repo-relative path: content}`` (text, or bytes for rasters).

    ``builders`` defaults to the registry; raises ``OrphanFigureError`` for a registered slug
    that has no post.
    """
    registry = dict(registered() if builders is None else builders)
    slugs = post_slugs(root / "content" / "posts")
    validate_registry(slugs, registry)
    bib = load_entries(root / "static" / "bib")
    base = FigureContext(
        slug="",
        bib=tuple(bib),
        locations=tuple(load_locations(root / "data" / "locations.json")),
        timeline=tuple(load_timeline(root / "data" / "timeline.json")),
    )
    out: dict[Path, str | bytes] = {}
    post_figures: dict[str, Figure] = {}
    for slug in slugs:
        builder = registry.get(slug) or default_construction(slug)
        post_figures[slug] = builder(replace(base, slug=slug))
        out[PARTIALS / "posts" / f"{slug}.html"] = wrap("posts", slug, post_figures[slug])
    page_figures: dict[str, Figure] = {}
    for page_key, builder in PAGE_FIGURES.items():
        kind, key = page_key.split("/", 1)
        page_figures[page_key] = builder(replace(base, slug=key))
        out[PARTIALS / kind / f"{key}.html"] = wrap(kind, key, page_figures[page_key])
    out[RESEARCH_JSON] = json.dumps(research_summary(bib), indent=2, sort_keys=True) + "\n"
    out.update(_rasters(root, post_figures, page_figures["pages/definition"]))
    return out


def _stale(root: Path, expected: Mapping[Path, str | bytes]) -> list[Path]:
    """Return generated-looking files (figure partials, social cards) that nothing produces."""
    found = [p.relative_to(root) for kind in KINDS for p in sorted((root / PARTIALS / kind).glob("*.html"))]
    found += [p.relative_to(root) for p in sorted((root / OG_DIR).glob("*.png"))]
    return [p for p in found if p not in expected]


def _matches(path: Path, content: str | bytes) -> bool:
    """Return whether ``path`` holds ``content``; a raster only has to exist (see module doc)."""
    if not path.exists():
        return False
    if isinstance(content, bytes):
        return True
    return path.read_text(encoding="utf-8") == content


def write(root: Path) -> list[Path]:
    """Write every generated file, delete stale ones, and return the paths that changed."""
    expected = render_all(root)
    changed: list[Path] = []
    for rel, content in expected.items():
        path = root / rel
        if isinstance(content, bytes):
            if path.exists() and path.read_bytes() == content:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        else:
            if path.exists() and path.read_text(encoding="utf-8") == content:
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        changed.append(rel)
    for rel in _stale(root, expected):
        (root / rel).unlink()
        changed.append(rel)
    return changed


def drift(root: Path) -> list[Path]:
    """Return the paths whose committed content differs from a fresh render (missing, edited, stale)."""
    expected = render_all(root)
    bad = [rel for rel, content in expected.items() if not _matches(root / rel, content)]
    return sorted([*bad, *_stale(root, expected)])
