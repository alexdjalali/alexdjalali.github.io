"""Unit tests for post discovery and registry coverage rules (real files in ``tmp_path``)."""

from __future__ import annotations

from pathlib import Path

import pytest

from figures.content import OrphanFigureError, Site, load_site, post_slugs, post_titles, validate_registry

pytestmark = pytest.mark.unit


def _post(d: Path, name: str, front: str) -> None:
    (d / name).write_text(f"---\n{front}\n---\nbody\n", encoding="utf-8")


def test_drafts_are_excluded_and_slugs_are_filename_stems(tmp_path: Path) -> None:
    """Only non-draft ``*.md`` files count; the slug is the filename stem."""
    _post(tmp_path, "alpha.md", 'title: "Alpha"\ndraft: false')
    _post(tmp_path, "beta.md", 'title: "Beta"\ndraft: true')
    _post(tmp_path, "gamma.md", 'title: "Gamma"')
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")
    assert post_slugs(tmp_path) == ["alpha", "gamma"]


def test_orphan_registration_raises_naming_the_slug() -> None:
    """A registered slug with no post fails and says which."""
    with pytest.raises(OrphanFigureError, match="ghost"):
        validate_registry(["alpha"], {"alpha": object(), "ghost": object()})


def test_unregistered_post_is_accepted() -> None:
    """A post with no registry entry is fine; the default applies."""
    validate_registry(["alpha", "new-post"], {"alpha": object()})


def test_titles_are_read_from_front_matter(tmp_path: Path) -> None:
    """``post_titles`` returns each non-draft post's quoted or bare ``title``."""
    _post(tmp_path, "a.md", 'title: "Quoted: yes"')
    _post(tmp_path, "b.md", "title: Bare")
    _post(tmp_path, "c.md", "title: Draft\ndraft: true")
    assert post_titles(tmp_path) == {"a": "Quoted: yes", "b": "Bare"}


def test_titles_follow_yaml_escapes_and_block_scalars(tmp_path: Path) -> None:
    """Escaped quotes and folded block scalars yield the title Hugo shows, not their source text."""
    _post(tmp_path, "a.md", r'title: "Say \"hi\""')
    _post(tmp_path, "b.md", "title: 'It''s'")
    _post(tmp_path, "c.md", "title: >\n  Folded\n  title")
    assert post_titles(tmp_path) == {"a": 'Say "hi"', "b": "It's", "c": "Folded title"}


@pytest.mark.parametrize("front", ["draft: false", "title:", "title: [a, b]"])
def test_post_without_a_usable_title_fails_naming_the_file(tmp_path: Path, front: str) -> None:
    """A post with no string title fails generation instead of drawing a card headlined by its slug."""
    _post(tmp_path, "nameless.md", front)
    with pytest.raises(ValueError, match="nameless.md"):
        post_titles(tmp_path)


def test_post_without_front_matter_fails_naming_the_file(tmp_path: Path) -> None:
    """A post with no front matter block at all is an error, not a slug-titled card."""
    (tmp_path / "bare.md").write_text("just text\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bare.md"):
        post_titles(tmp_path)


_MENU = """
[[languages.en.menu.main]]
identifier = "research"
name = "Research"
weight = 1
url = "publications/"
[[languages.en.menu.main]]
identifier = "talks"
parent = "research"
name = "Talks"
weight = 1
url = "presentations/"
[[languages.en.menu.main]]
identifier = "writing"
name = "Writing"
weight = 2
url = "posts/"
"""
_SITE = (
    'baseURL = "https://example.org/"\ntitle = "T"\n[params]\ndefinition = "D."\ndefinitionLabel = "Def 1."\n'
)


def test_site_values_come_from_hugo_toml(tmp_path: Path) -> None:
    """Site values come from ``hugo.toml``; the posts Book is numbered by its menu weight."""
    (tmp_path / "hugo.toml").write_text(_SITE + _MENU, encoding="utf-8")
    assert load_site(tmp_path) == Site("T", "example.org", "D.", "Def 1.", "Book II · Writing")


@pytest.mark.parametrize(
    ("drop", "key"),
    [
        ('definition = "D."\n', "params.definition"),
        ('definitionLabel = "Def 1."\n', "params.definitionLabel"),
    ],
)
def test_missing_site_value_is_named(tmp_path: Path, drop: str, key: str) -> None:
    """A missing key fails generation and names the key, rather than drawing a blank card."""
    (tmp_path / "hugo.toml").write_text(_SITE.replace(drop, "") + _MENU, encoding="utf-8")
    with pytest.raises(ValueError, match=key):
        load_site(tmp_path)


def test_menu_without_a_posts_book_is_named(tmp_path: Path) -> None:
    """With no top-level menu entry for ``posts/``, the card kicker cannot be drawn: fail naming it."""
    (tmp_path / "hugo.toml").write_text(
        _SITE + _MENU.replace('url = "posts/"', 'url = "blog/"'), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="posts/"):
        load_site(tmp_path)
