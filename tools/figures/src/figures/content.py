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
    """Return the YAML front matter of ``path`` with lower-cased keys (as Hugo reads them), or ``None``.

    Raises ``ValueError`` naming the file when the YAML does not parse.
    """
    match = _FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    try:
        data = yaml.safe_load(match.group(1)) if match else None
    except yaml.YAMLError as err:
        raise ValueError(f"{path.name}: front matter is not valid YAML: {err}") from err
    return {str(k).lower(): v for k, v in data.items()} if isinstance(data, dict) else None


_TRUE_STRINGS = frozenset({"1", "t", "T", "TRUE", "true", "True"})
"""The strings Go's ``strconv.ParseBool`` (behind Hugo's ``cast.ToBool``) reads as true."""


def _to_bool(value: object) -> bool:
    """Cast a front-matter value as Hugo's ``cast.ToBool``: ``_TRUE_STRINGS``, or a non-zero number."""
    if isinstance(value, bool | int | float):
        return bool(value)
    return isinstance(value, str) and value in _TRUE_STRINGS


def _is_draft(front: Mapping[str, Any]) -> bool:
    """Return whether Hugo treats the page as a draft: ``draft`` when set, else ``published`` false."""
    if "draft" in front:
        return _to_bool(front["draft"])
    return "published" in front and not _to_bool(front["published"])


def _posts(content_dir: Path) -> dict[str, dict[str, Any] | None]:
    """Return ``{slug: front matter}`` for the non-draft ``*.md`` files in ``content_dir``, sorted."""
    posts: dict[str, dict[str, Any] | None] = {}
    for path in sorted(content_dir.glob("*.md")):
        front = _front_matter(path)
        if front and _is_draft(front):
            continue
        posts[path.stem] = front
    return posts


def post_titles(content_dir: Path) -> dict[str, str]:
    """Return ``{slug: title}`` for the non-draft posts in ``content_dir``.

    Raises ``ValueError`` naming the file when a post has no front matter or no non-empty string
    ``title``, so generation fails rather than drawing a card headlined by the slug.
    """
    titles: dict[str, str] = {}
    for slug, front in _posts(content_dir).items():
        title = (front or {}).get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"{slug}.md: front matter has no string title")
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


def _menu_order(entry: Mapping[str, Any]) -> tuple[bool, int, str, str, str]:
    """Sort key matching Hugo's menu order: weight (0 or unset last), case-folded name, identifier."""
    weight, name = entry.get("weight", 0), str(entry.get("name", ""))
    if not isinstance(weight, int) or isinstance(weight, bool):
        raise ValueError(
            f"hugo.toml: menu entry {name or '(unnamed)'} weight must be a TOML integer, got {weight!r}"
        )
    return (weight == 0, weight, name.casefold(), name, str(entry.get("identifier", "")))


def _posts_book(config: Mapping[str, Any]) -> str:
    """Return ``Book <numeral> · <name>`` for the top-level main-menu entry for ``posts``.

    The entry is found by ``url`` or ``pageRef``; Books are numbered in Hugo's menu order, as the
    header numbers them.
    """
    lang = config.get("defaultContentLanguage", "en")
    where = f"hugo.toml: languages.{lang}.menu.main"
    entries = config.get("languages", {}).get(lang, {}).get("menu", {}).get("main", [])
    books = sorted((e for e in entries if "parent" not in e), key=_menu_order)
    for i, book in enumerate(books, start=1):
        if str(book.get("url") or book.get("pageRef") or "").strip("/") == "posts":
            if not book.get("name"):
                raise ValueError(f"{where}: the posts/ entry has no name")
            return f"Book {_roman(i)} · {book['name']}"
    raise ValueError(f"{where}: no top-level entry with url or pageRef posts/")


def load_site(root: Path) -> Site:
    """Return the card's site values from ``hugo.toml``.

    Raises ``ValueError`` naming the first key that is missing or not a string, or a ``baseURL``
    with no host, so a renamed or mistyped key fails generation rather than drawing a blank card.
    """
    config = tomllib.loads((root / "hugo.toml").read_text(encoding="utf-8"))
    params = config.get("params", {})
    values = {
        "title": config.get("title"),
        "baseURL": config.get("baseURL"),
        "params.definition": params.get("definition"),
        "params.definitionLabel": params.get("definitionLabel"),
    }
    missing = [key for key, value in values.items() if not isinstance(value, str) or not value]
    if missing:
        raise ValueError(f"hugo.toml: missing or not a string: {missing[0]}")
    values["baseURL"] = urlparse(values["baseURL"]).netloc
    if not values["baseURL"]:
        raise ValueError("hugo.toml: baseURL has no host (it needs a scheme, e.g. https://)")
    return Site(
        name=values["title"],
        host=values["baseURL"],
        definition=values["params.definition"],
        definition_label=values["params.definitionLabel"],
        posts_book=_posts_book(config),
    )
