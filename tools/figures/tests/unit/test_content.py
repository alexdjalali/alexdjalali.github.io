"""Unit tests for post discovery and registry coverage rules (real files in ``tmp_path``)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from figures.content import (
    OrphanFigureError,
    PageCard,
    Site,
    load_site,
    page_cards,
    post_titles,
    validate_registry,
)

pytestmark = pytest.mark.unit


def _post(d: Path, name: str, front: str) -> None:
    (d / name).write_text(f"---\n{front}\n---\nbody\n", encoding="utf-8")


def test_drafts_are_excluded_and_slugs_are_filename_stems(tmp_path: Path) -> None:
    """Only non-draft ``*.md`` files count; the slug is the filename stem."""
    _post(tmp_path, "alpha.md", 'title: "Alpha"\ndraft: false')
    _post(tmp_path, "beta.md", 'title: "Beta"\ndraft: true')
    _post(tmp_path, "gamma.md", 'title: "Gamma"')
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")
    assert list(post_titles(tmp_path)) == ["alpha", "gamma"]


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


def test_malformed_front_matter_fails_naming_the_file(tmp_path: Path) -> None:
    """Unparseable YAML fails with the file's name, not a context-free scanner error."""
    _post(tmp_path, "broken.md", 'title: "unterminated')
    with pytest.raises(ValueError, match="broken.md"):
        post_titles(tmp_path)


@pytest.mark.parametrize(
    ("front", "is_post"),
    [
        ('draft: "true"', False),
        ("draft: 1", False),
        ("draft: 't'", False),
        ("draft: TRUE", False),
        ('draft: "True"', False),
        ('draft: "T"', False),
        ("published: true", True),
        ("Draft: true", False),
        ("published: false", False),
        ('draft: "false"', True),
        ("draft: tRuE", True),
        ("draft: false\npublished: false", True),
        ("draft: true\npublished: true", False),
    ],
)
def test_drafts_follow_hugo(tmp_path: Path, front: str, is_post: bool) -> None:
    """``draft`` is cast like ``strconv.ParseBool`` and wins over ``published``; keys are case-insensitive."""
    _post(tmp_path, "a.md", f"title: A\n{front}")
    assert ("a" in post_titles(tmp_path)) is is_post


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


def test_posts_book_matches_hugo_menu_rules(tmp_path: Path) -> None:
    """A ``/posts/`` url matches, and tied weights are numbered by name as Hugo's menu sorts them."""
    menu = (
        '[[languages.en.menu.main]]\nname = "Zeta"\nweight = 1\nurl = "zeta/"\n'
        '[[languages.en.menu.main]]\nname = "Writing"\nweight = 1\nurl = "/posts/"\n'
    )
    (tmp_path / "hugo.toml").write_text(_SITE + menu, encoding="utf-8")
    assert load_site(tmp_path).posts_book == "Book I · Writing"


def test_posts_book_without_a_name_is_named(tmp_path: Path) -> None:
    """A ``posts/`` menu entry with no ``name`` fails naming ``hugo.toml``, not with a bare KeyError."""
    (tmp_path / "hugo.toml").write_text(
        _SITE + '[[languages.en.menu.main]]\nweight = 1\nurl = "posts/"\n', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="no name"):
        load_site(tmp_path)


def _book(name: str, url: str, weight: int | None = None, ident: str = "") -> str:
    """Return one top-level main-menu entry as TOML."""
    lines = [f'name = "{name}"', f'url = "{url}"']
    lines += [f"weight = {weight}"] if weight is not None else []
    lines += [f'identifier = "{ident}"'] if ident else []
    return "[[languages.en.menu.main]]\n" + "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    ("books", "expected"),
    [
        ([_book("Extra", "x/"), _book("Writing", "posts/", 1)], "Book I · Writing"),
        ([_book("apple", "a/", 1), _book("Writing", "posts/", 1)], "Book II · Writing"),
        ([_book("Writing", "posts/", 1, "b"), _book("Writing", "w/", 1, "a")], "Book II · Writing"),
    ],
    ids=["unweighted-last", "name-case-folded", "identifier-tiebreak"],
)
def test_posts_book_numbering_matches_hugo_menu_sort(tmp_path: Path, books: list[str], expected: str) -> None:
    """Books number in Hugo's menu order: weight (0 or none last), case-folded name, identifier."""
    (tmp_path / "hugo.toml").write_text(_SITE + "".join(books), encoding="utf-8")
    assert load_site(tmp_path).posts_book == expected


def test_posts_book_found_by_page_ref(tmp_path: Path) -> None:
    """A Book that points at the posts section with ``pageRef`` is found like one with ``url``."""
    toml = _SITE + '[[languages.en.menu.main]]\nname = "Writing"\nweight = 1\npageRef = "/posts"\n'
    (tmp_path / "hugo.toml").write_text(toml, encoding="utf-8")
    assert load_site(tmp_path).posts_book == "Book I · Writing"


@pytest.mark.parametrize(
    ("line", "bad", "key"),
    [
        ('title = "T"', "title = 1", "title"),
        ('baseURL = "https://example.org/"', "baseURL = 1", "baseURL"),
        ('definition = "D."', "definition = true", "params.definition"),
        ('definitionLabel = "Def 1."', "definitionLabel = 2", "params.definitionLabel"),
    ],
)
def test_non_string_site_value_is_named(tmp_path: Path, line: str, bad: str, key: str) -> None:
    """A site value of the wrong type fails naming its key, not deep inside parsing or card drawing."""
    (tmp_path / "hugo.toml").write_text(_SITE.replace(line, bad) + _MENU, encoding="utf-8")
    with pytest.raises(ValueError, match=f"not a string: {re.escape(key)}$"):
        load_site(tmp_path)


def test_non_integer_menu_weight_is_named(tmp_path: Path) -> None:
    """A Book with a non-integer weight fails naming ``hugo.toml`` and the entry, not a bare cast error."""
    (tmp_path / "hugo.toml").write_text(
        _SITE + _book("Writing", "posts/").replace('url = "posts/"', 'url = "posts/"\nweight = "first"'),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="hugo.toml: menu entry Writing weight must be a TOML integer"):
        load_site(tmp_path)


def test_base_url_without_a_host_is_named(tmp_path: Path) -> None:
    """A scheme-less ``baseURL`` is a string with no host; the error says so rather than "missing"."""
    toml = _SITE.replace('"https://example.org/"', '"example.org/"') + _MENU
    (tmp_path / "hugo.toml").write_text(toml, encoding="utf-8")
    with pytest.raises(ValueError, match="baseURL has no host"):
        load_site(tmp_path)


def test_card_host_drops_userinfo_and_port(tmp_path: Path) -> None:
    """The card prints the bare host, never credentials or a port from ``baseURL``."""
    toml = _SITE.replace('"https://example.org/"', '"https://user:pw@Example.org:8443/"') + _MENU
    (tmp_path / "hugo.toml").write_text(toml, encoding="utf-8")
    assert load_site(tmp_path).host == "example.org"


def test_page_cards_read_kicker_headline_and_figure_from_front_matter(tmp_path: Path) -> None:
    """A top-level page with a ``card`` figure gets a social card from its own kicker and headline."""
    (tmp_path / "about.md").write_text(
        '---\ntitle: About\nkicker: "Book IV."\nheadline: "About: {homes} homes."\n'
        "card: pages/lifeline\n---\n",
        encoding="utf-8",
    )
    (tmp_path / "search.md").write_text("---\ntitle: Search\n---\n", encoding="utf-8")
    assert page_cards(tmp_path) == {
        "about": PageCard(kicker="Book IV.", headline="About: {homes} homes.", figure="pages/lifeline")
    }


def test_page_card_without_a_headline_is_an_error(tmp_path: Path) -> None:
    """A page that asks for a card but gives no headline fails generation, naming the file."""
    (tmp_path / "gear.md").write_text(
        '---\ntitle: Gear\nkicker: "K"\ncard: pages/scout\n---\n', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="gear.md"):
        page_cards(tmp_path)
