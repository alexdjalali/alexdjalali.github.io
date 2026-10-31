"""Render every figure, data file, social card and icon to its repo path; write them; report drift.

The composition root of the generator: it loads the repo data, builds a ``FigureContext`` per
figure, and returns ``{repo-relative path: content}`` — text for partials and data, a ``Raster`` for
the PNG cards and icons (drawn only when ``write`` finds it stale). I/O happens only in the
loaders and in ``write`` / ``drift``.

Rasters are compared by the digest (fonts, resvg version, SVG) stamped into each PNG, not by bytes:
resvg output can differ by a few pixels between CPUs, but a stale card carries a stale digest.
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
from figures.content import load_site, post_slugs, post_titles, validate_registry
from figures.data import load_locations, load_timeline
from figures.default import default_construction
from figures.model import Figure, FigureContext
from figures.pages import CARD_FIGURES, PAGE_FIGURES
from figures.registry import FigureBuilder, registered

PARTIALS = Path("layouts/_partials/figures")
"""Where generated partials live, relative to the repo root."""
KINDS = ("posts", "projects", "talks", "pages")
RESEARCH_JSON = Path("data/figures/research.json")
OG_DIR = Path("static/images/og")
"""One social card per post, ``<slug>.png``."""
OG_DEFAULT = Path("static/images/og-default.png")
FAVICON_ICO = Path("static/favicon.ico")
ICO_SIZES = (16, 32)
"""Tab-icon sizes: each is a ``favicon-<s>x<s>.png`` and both are packed into ``favicon.ico``."""
ICONS = {
    **{s: Path(f"static/images/favicon-{s}x{s}.png") for s in ICO_SIZES},
    180: Path("static/images/apple-touch-icon.png"),
}
"""Square PNG icons by edge length: the tab icons and the 180 px apple-touch icon."""


def wrap(kind: str, key: str, figure: Figure) -> str:
    """Return the ``<figure>`` partial: the svg with an accessible name plus a hidden caption."""
    cap_id = f"fig-{kind}-{key}-cap"
    svg = figure.svg.replace("<svg ", f'<svg role="img" aria-labelledby="{cap_id}" ', 1)
    caption = html.escape(figure.caption)
    return (
        f'<figure class="fig-frame">{svg}'
        f'<figcaption id="{cap_id}" class="visually-hidden">{caption}</figcaption></figure>\n'
    )


def _rasters(root: Path, post_figures: Mapping[str, Figure], definition: Figure) -> dict[Path, raster.Raster]:
    """Return the per-post social cards, the default card and the icons, not yet drawn."""
    site = load_site(root)
    titles = post_titles(root / "content" / "posts")
    og = (raster.OG_SIZE,)
    out: dict[Path, raster.Raster] = {}
    for slug, fig in post_figures.items():
        card = raster.card_svg(site.posts_book, titles[slug], fig.svg, site.name, site.host)
        out[OG_DIR / f"{slug}.png"] = raster.Raster(card, og)
    card = raster.card_svg(
        site.definition_label, site.definition, definition.svg, site.name, site.host, size=42, wrap=26
    )
    out[OG_DEFAULT] = raster.Raster(card, og)
    mark = raster.mark_svg()
    out.update({path: raster.Raster(mark, ((s, s),)) for s, path in ICONS.items()})
    out[FAVICON_ICO] = raster.Raster(mark, tuple((s, s) for s in ICO_SIZES))
    return out


Output = str | raster.Raster
"""A generated file's content: text, or a raster drawn on write."""


def render_all(root: Path, builders: Mapping[str, FigureBuilder] | None = None) -> dict[Path, Output]:
    """Return every generated file as ``{repo-relative path: content}`` (text, or a ``Raster``).

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
    out: dict[Path, Output] = {}
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
    definition = CARD_FIGURES["definition"](replace(base, slug="definition"))
    out.update(_rasters(root, post_figures, definition))
    return out


def _stale(root: Path, expected: Mapping[Path, Output]) -> list[Path]:
    """Return generated-looking files (figure partials, social cards) that nothing produces."""
    found = [p.relative_to(root) for kind in KINDS for p in sorted((root / PARTIALS / kind).glob("*.html"))]
    found += [p.relative_to(root) for p in sorted((root / OG_DIR).glob("*.png"))]
    return [p for p in found if p not in expected]


def _matches(path: Path, content: Output) -> bool:
    """Return whether ``path`` holds ``content``; a raster matches on its stamped digest."""
    if not path.exists():
        return False
    if isinstance(content, raster.Raster):
        return raster.read_stamp(path.read_bytes()) == content.digest
    return path.read_text(encoding="utf-8") == content


def write(root: Path) -> list[Path]:
    """Write every generated file, delete stale ones, and return the paths that changed."""
    expected = render_all(root)
    changed: list[Path] = []
    for rel, content in expected.items():
        path = root / rel
        if _matches(path, content):
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        data = content.render() if isinstance(content, raster.Raster) else content.encode("utf-8")
        path.write_bytes(data)
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
