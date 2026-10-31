"""Read the site: post slugs and titles from ``content/posts``, site values from ``hugo.toml``."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

_FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


class OrphanFigureError(ValueError):
    """Raised when a registered figure has no post."""


def _front_matter(path: Path) -> dict[str, Any] | None:
    """Return the YAML front matter of ``path`` as a mapping, or ``None`` when it has none."""
    match = _FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    data = yaml.safe_load(match.group(1)) if match else None
    return data if isinstance(data, dict) else None


def post_slugs(content_dir: Path) -> list[str]:
    """Return the sorted stems of non-draft ``*.md`` files in ``content_dir``."""
    slugs: list[str] = []
    for path in sorted(content_dir.glob("*.md")):
        front = _front_matter(path)
        if front and front.get("draft") is True:
            continue
        slugs.append(path.stem)
    return slugs


def post_titles(content_dir: Path) -> dict[str, str]:
    """Return ``{slug: title}`` for the non-draft posts in ``content_dir``.

    Raises ``ValueError`` naming the file when a post has no front matter or no non-empty string
    ``title``, so generation fails rather than drawing a card headlined by the slug.
    """
    titles: dict[str, str] = {}
    for slug in post_slugs(content_dir):
        path = content_dir / f"{slug}.md"
        title = (_front_matter(path) or {}).get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{path.name}: front matter has no string title")
        titles[slug] = title.strip()
    return titles


def validate_registry(slugs: Iterable[str], registered: Mapping[str, object]) -> None:
    """Raise ``OrphanFigureError`` for any registered slug that has no post.

    An unregistered post is accepted: it gets the default construction.
    """
    known = set(slugs)
    orphans = sorted(set(registered) - known)
    if orphans:
        raise OrphanFigureError(f"registered figures without a post: {', '.join(orphans)}")


_ROMAN = ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"))


def _roman(n: int) -> str:
    """Return ``n`` (1-39) as a roman numeral, as ``layouts/_partials/roman.html`` does."""
    out = ""
    for value, symbol in _ROMAN:
        count, n = divmod(n, value)
        out += symbol * count
    return out


@dataclass(frozen=True, slots=True)
class Site:
    """The site values drawn on the social cards, all read from ``hugo.toml``."""

    name: str
    """The site ``title``."""
    host: str
    """The ``baseURL`` host."""
    definition: str
    """``params.definition``: the Home headline and the default card's title."""
    definition_label: str
    """``params.definitionLabel``: the kicker above it."""
    posts_book: str
    """The posts kicker, e.g. ``Book I · Writing``: the ``posts/`` Book's place and name in the main menu."""


def _posts_book(config: Mapping[str, Any]) -> str:
    """Return ``Book <numeral> · <name>`` for the top-level main-menu entry whose url is ``posts/``.

    Books are numbered by weight among the top-level entries, as the header numbers them.
    """
    lang = config.get("defaultContentLanguage", "en")
    entries = config.get("languages", {}).get(lang, {}).get("menu", {}).get("main", [])
    books = sorted((e for e in entries if "parent" not in e), key=lambda e: e.get("weight", 0))
    for i, book in enumerate(books, start=1):
        if book.get("url") == "posts/":
            return f"Book {_roman(i)} · {book['name']}"
    raise ValueError(f"hugo.toml: no top-level languages.{lang}.menu.main entry with url posts/")


def load_site(root: Path) -> Site:
    """Return the card's site values from ``hugo.toml``.

    Raises ``ValueError`` naming the first missing key, so a renamed key fails generation rather
    than drawing a blank card.
    """
    config = tomllib.loads((root / "hugo.toml").read_text(encoding="utf-8"))
    params = config.get("params", {})
    values = {
        "title": config.get("title"),
        "baseURL": urlparse(config.get("baseURL") or "").netloc,
        "params.definition": params.get("definition"),
        "params.definitionLabel": params.get("definitionLabel"),
    }
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise ValueError(f"hugo.toml: missing {missing[0]}")
    return Site(*values.values(), posts_book=_posts_book(config))
