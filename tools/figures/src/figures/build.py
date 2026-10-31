"""Render every figure and data file to its repo path; write them; report drift.

The composition root of the generator: it loads the repo data, builds a ``FigureContext`` per
figure, and returns ``{repo-relative path: content}``. I/O happens only in the loaders and in
``write`` / ``drift``.
"""

from __future__ import annotations

import html
import json
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

import figures.posts  # noqa: F401  (importing registers the post builders)
from figures.bib import load_entries, research_summary
from figures.content import post_slugs, validate_registry
from figures.data import load_locations, load_timeline
from figures.default import default_construction
from figures.model import Figure, FigureContext
from figures.pages import PAGE_FIGURES
from figures.registry import FigureBuilder, registered

PARTIALS = Path("layouts/_partials/figures")
"""Where generated partials live, relative to the repo root."""
KINDS = ("posts", "projects", "talks", "pages")
RESEARCH_JSON = Path("data/figures/research.json")


def wrap(kind: str, key: str, figure: Figure) -> str:
    """Return the ``<figure>`` partial: the svg with an accessible name plus a hidden caption."""
    cap_id = f"fig-{kind}-{key}-cap"
    svg = figure.svg.replace("<svg ", f'<svg role="img" aria-labelledby="{cap_id}" ', 1)
    caption = html.escape(figure.caption)
    return (
        f'<figure class="fig-frame">{svg}'
        f'<figcaption id="{cap_id}" class="visually-hidden">{caption}</figcaption></figure>\n'
    )


def render_all(root: Path, builders: Mapping[str, FigureBuilder] | None = None) -> dict[Path, str]:
    """Return every generated file as ``{repo-relative path: content}``.

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
    out: dict[Path, str] = {}
    for slug in slugs:
        builder = registry.get(slug) or default_construction(slug)
        out[PARTIALS / "posts" / f"{slug}.html"] = wrap("posts", slug, builder(replace(base, slug=slug)))
    for page_key, builder in PAGE_FIGURES.items():
        kind, key = page_key.split("/", 1)
        out[PARTIALS / kind / f"{key}.html"] = wrap(kind, key, builder(replace(base, slug=key)))
    out[RESEARCH_JSON] = json.dumps(research_summary(bib), indent=2, sort_keys=True) + "\n"
    return out


def _stale(root: Path, expected: Mapping[Path, str]) -> list[Path]:
    """Return generated-looking files under the figure partial dirs that nothing produces."""
    found = [p.relative_to(root) for kind in KINDS for p in sorted((root / PARTIALS / kind).glob("*.html"))]
    return [p for p in found if p not in expected]


def write(root: Path) -> list[Path]:
    """Write every generated file, delete stale ones, and return the paths that changed."""
    expected = render_all(root)
    changed: list[Path] = []
    for rel, content in expected.items():
        path = root / rel
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
    bad = [
        rel
        for rel, content in expected.items()
        if not (root / rel).exists() or (root / rel).read_text(encoding="utf-8") != content
    ]
    return sorted([*bad, *_stale(root, expected)])
