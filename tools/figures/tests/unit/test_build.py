"""Unit tests for the generator: a ``tmp_path`` skeleton of the repo, real files, no doubles."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

import pytest

from figures import build, cli
from figures.content import OrphanFigureError
from figures.model import Figure, FigureContext
from figures.registry import registered

pytestmark = pytest.mark.unit

BIB = "@article{a2020x,\n  title = {T},\n  author = {A},\n  journal = {J},\n  year = {2020}\n}\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Build a minimal repo skeleton: posts (one a draft), one bib file, and the data files."""
    (tmp_path / "hugo.toml").write_text(
        'baseURL = "https://example.org/"\ntitle = "site"\n[params]\ndefinition = "A test site."\n',
        encoding="utf-8",
    )
    posts = tmp_path / "content" / "posts"
    posts.mkdir(parents=True)
    (posts / "alpha.md").write_text("---\ntitle: A\n---\nx\n", encoding="utf-8")
    (posts / "beta.md").write_text("---\ntitle: B\n---\nx\n", encoding="utf-8")
    (posts / "wip.md").write_text("---\ntitle: W\ndraft: true\n---\nx\n", encoding="utf-8")
    for slug in registered():  # the real registry is global, so give every registered slug a post
        (posts / f"{slug}.md").write_text("---\ntitle: R\n---\nx\n", encoding="utf-8")
    (tmp_path / "static" / "bib").mkdir(parents=True)
    (tmp_path / "static" / "bib" / "a2020x.bib").write_text(BIB, encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "locations.json").write_text(
        json.dumps([{"startdate": "1990-01-01", "enddate": "", "title": "X", "shorttitle": "X"}]),
        encoding="utf-8",
    )
    (tmp_path / "data" / "timeline.json").write_text(
        json.dumps([{"startdate": "2000-01-01", "enddate": "2001-01-01", "title": "S", "type": "education"}]),
        encoding="utf-8",
    )
    return tmp_path


def test_generate_writes_one_partial_per_post_plus_page_figures(repo: Path) -> None:
    """Posts get a partial each (drafts excluded); page figures and research.json are written."""
    assert cli.main(["generate", "--root", str(repo)]) == 0
    figs = repo / build.PARTIALS
    names = {p.name for p in (figs / "posts").glob("*.html")}
    assert {"alpha.html", "beta.html"} <= names
    assert "wip.html" not in names
    assert (figs / "pages" / "lifeline.html").exists()
    assert (figs / "projects" / "poot.html").exists()
    summary = json.loads((repo / build.RESEARCH_JSON).read_text(encoding="utf-8"))
    assert summary["papers"] == 1


def test_check_is_clean_after_generate_and_names_an_edited_file(repo: Path) -> None:
    """``check`` returns 0 after ``generate`` and 1 once a generated file is edited."""
    cli.main(["generate", "--root", str(repo)])
    assert cli.main(["check", "--root", str(repo)]) == 0
    target = repo / build.PARTIALS / "posts" / "alpha.html"
    target.write_text(target.read_text(encoding="utf-8") + "<!-- hand edit -->", encoding="utf-8")
    assert build.drift(repo) == [build.PARTIALS / "posts" / "alpha.html"]
    assert cli.main(["check", "--root", str(repo)]) == 1


def test_missing_file_is_drift(repo: Path) -> None:
    """A deleted partial counts as drift."""
    cli.main(["generate", "--root", str(repo)])
    (repo / build.PARTIALS / "pages" / "lifeline.html").unlink()
    assert build.PARTIALS / "pages" / "lifeline.html" in build.drift(repo)


def test_deleted_post_makes_its_partial_stale(repo: Path) -> None:
    """Removing a post leaves its partial behind as drift; ``generate`` deletes it."""
    cli.main(["generate", "--root", str(repo)])
    (repo / "content" / "posts" / "beta.md").unlink()
    assert build.drift(repo) == [build.PARTIALS / "posts" / "beta.html", build.OG_DIR / "beta.png"]
    cli.main(["generate", "--root", str(repo)])
    assert not (repo / build.PARTIALS / "posts" / "beta.html").exists()
    assert build.drift(repo) == []


def test_orphan_registration_fails_generation(repo: Path) -> None:
    """A builder registered for a slug with no post makes rendering raise."""

    def ghost(_c: FigureContext) -> Figure:
        return Figure("<svg/>", "ghost")

    with pytest.raises(OrphanFigureError, match="ghost"):
        build.render_all(repo, {"ghost": ghost})


def test_wrap_adds_role_and_a_matching_caption() -> None:
    """The svg is named by a hidden figcaption whose id matches ``aria-labelledby``."""
    out = build.wrap("posts", "alpha", Figure('<svg class="fig" viewBox="0 0 1 1"></svg>', "A & B"))
    label = re.search(r'aria-labelledby="([^"]+)"', out)
    assert label and 'role="img"' in out
    assert f'<figcaption id="{label.group(1)}" class="visually-hidden">A &amp; B</figcaption>' in out


def test_find_root_walks_up_to_hugo_toml(repo: Path) -> None:
    """The root is the nearest ancestor holding hugo.toml."""
    assert cli.find_root(repo / "content" / "posts") == repo


def test_generate_writes_social_cards_and_icons(repo: Path) -> None:
    """Each post gets a PNG social card; the default card, favicons and ``favicon.ico`` are written."""
    cli.main(["generate", "--root", str(repo)])
    cards = {p.name for p in (repo / build.OG_DIR).glob("*.png")}
    assert {"alpha.png", "beta.png"} <= cards and "wip.png" not in cards
    assert (repo / build.FAVICON_ICO).read_bytes()[:4] == b"\x00\x00\x01\x00"
    for rel in (build.OG_DEFAULT, *build.ICONS.values()):
        assert (repo / rel).read_bytes()[:4] == b"\x89PNG"


def test_deleted_post_makes_its_card_stale(repo: Path) -> None:
    """A card whose post is gone is drift until ``generate`` removes it; a missing card is drift."""
    cli.main(["generate", "--root", str(repo)])
    (repo / "content" / "posts" / "beta.md").unlink()
    assert build.OG_DIR / "beta.png" in build.drift(repo)
    cli.main(["generate", "--root", str(repo)])
    (repo / build.OG_DIR / "alpha.png").unlink()
    assert build.drift(repo) == [build.OG_DIR / "alpha.png"]


def test_editing_a_title_makes_its_card_drift(repo: Path) -> None:
    """A card is in sync only while it was drawn from the current title and figure."""
    cli.main(["generate", "--root", str(repo)])
    post = repo / "content" / "posts" / "alpha.md"
    post.write_text("---\ntitle: A renamed post\n---\nx\n", encoding="utf-8")
    assert build.drift(repo) == [build.OG_DIR / "alpha.png"]
    assert cli.main(["generate", "--root", str(repo)]) == 0
    assert build.drift(repo) == []


def test_every_figure_glyph_is_in_a_vendored_font(repo_root: Path) -> None:
    """Cards render with the vendored fonts only, so every non-ASCII label character must be in one."""
    from fontTools.ttLib import TTFont

    from figures.raster import FONT_DIR

    covered: set[int] = set()
    for font in FONT_DIR.glob("*.ttf"):
        covered |= set(TTFont(font).getBestCmap() or {})
    labels = [
        html.unescape(t)
        for content in build.render_all(repo_root).values()
        if isinstance(content, str)
        for t in re.findall(r"<text[^>]*>(.*?)</text>", content)
    ]
    missing = sorted(
        {ch for label in labels for ch in re.sub(r"<[^>]+>", "", label) if ord(ch) not in covered}
    )
    assert missing == []
