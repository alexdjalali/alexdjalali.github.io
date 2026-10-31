"""Read the site: post slugs and titles from ``content/posts``, site values from ``hugo.toml``."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable, Mapping
from pathlib import Path
from urllib.parse import urlparse

_FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_DRAFT = re.compile(r"^draft:\s*true\s*$", re.MULTILINE)
_TITLE = re.compile(r"^title:\s*(?:\"(.*)\"|'(.*)'|(.*?))\s*$", re.MULTILINE)


class OrphanFigureError(ValueError):
    """Raised when a registered figure has no post."""


def post_slugs(content_dir: Path) -> list[str]:
    """Return the sorted stems of non-draft ``*.md`` files in ``content_dir``."""
    slugs: list[str] = []
    for path in sorted(content_dir.glob("*.md")):
        match = _FRONT_MATTER.match(path.read_text(encoding="utf-8"))
        if match and _DRAFT.search(match.group(1)):
            continue
        slugs.append(path.stem)
    return slugs


def post_titles(content_dir: Path) -> dict[str, str]:
    """Return ``{slug: title}`` for the non-draft posts in ``content_dir``."""
    titles: dict[str, str] = {}
    for slug in post_slugs(content_dir):
        match = _FRONT_MATTER.match((content_dir / f"{slug}.md").read_text(encoding="utf-8"))
        found = _TITLE.search(match.group(1)) if match else None
        titles[slug] = next((g for g in found.groups() if g is not None), slug) if found else slug
    return titles


def validate_registry(slugs: Iterable[str], registered: Mapping[str, object]) -> None:
    """Raise ``OrphanFigureError`` for any registered slug that has no post.

    An unregistered post is accepted: it gets the default construction.
    """
    known = set(slugs)
    orphans = sorted(set(registered) - known)
    if orphans:
        raise OrphanFigureError(f"registered figures without a post: {', '.join(orphans)}")


def load_site(root: Path) -> tuple[str, str, str]:
    """Return the site ``title``, the ``baseURL`` host and ``params.definition`` from ``hugo.toml``.

    Raises ``ValueError`` naming the first missing key, so a renamed key fails generation rather
    than drawing a blank card.
    """
    config = tomllib.loads((root / "hugo.toml").read_text(encoding="utf-8"))
    values = {
        "title": config.get("title"),
        "baseURL": urlparse(config.get("baseURL") or "").netloc,
        "params.definition": config.get("params", {}).get("definition"),
    }
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise ValueError(f"hugo.toml: missing {missing[0]}")
    return values["title"], values["baseURL"], values["params.definition"]
