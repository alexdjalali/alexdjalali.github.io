"""Story 1 truths: the in-repo theme builds, keeps every URL, and exposes four Books."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

from tests.helpers import nav_links, read_html

pytestmark = pytest.mark.integration

PAGES = [
    "index.html",
    "posts/index.html",
    "publications/index.html",
    "presentations/index.html",
    "projects/index.html",
    "about/index.html",
    "cv/index.html",
    "media/index.html",
    "gear/index.html",
    "ai-disclaimer/index.html",
    "search/index.html",
    "archives/index.html",
    "series/index.html",
    "tags/index.html",
    "404.html",
    "index.json",
    "index.xml",
]


def test_hugo_config_has_no_theme_and_coder_is_gone(repo_root: Path) -> None:
    """The root ``theme`` key, ``themes/coder`` and ``.gitmodules`` are all absent."""
    config = tomllib.loads((repo_root / "hugo.toml").read_text(encoding="utf-8"))
    assert "theme" not in config  # [params.giscus] theme is a nested key and allowed
    assert not (repo_root / "themes" / "coder").exists()
    assert not (repo_root / ".gitmodules").exists()


def test_every_pre_redesign_url_still_renders(built_site: Path, repo_root: Path) -> None:
    """Every URL that existed before the redesign has a non-empty built file."""
    posts = sorted(p.stem for p in (repo_root / "content" / "posts").glob("*.md"))
    assert posts, "expected posts in content/posts"
    for rel in [*PAGES, *(f"posts/{slug}/index.html" for slug in posts)]:
        path = built_site / rel
        assert path.is_file() and path.stat().st_size > 0, rel


def test_primary_nav_has_four_books(built_site: Path) -> None:
    """The primary nav lists exactly Writing, Research, Projects, About, in order."""
    links = nav_links(read_html(built_site, "index.html"))["Primary"]
    names = [re.sub(r"^[IVX]+\.\s*", "", t) for t in links]
    assert names == ["Writing", "Research", "Projects", "About"]


@pytest.mark.parametrize(
    ("page", "label", "expected"),
    [
        ("publications/index.html", "Research sections", ["Publications", "Talks"]),
        ("presentations/index.html", "Research sections", ["Publications", "Talks"]),
        (
            "gear/index.html",
            "About sections",
            ["About", "Resume", "Media", "Gear", "AI disclosure"],
        ),
    ],
)
def test_research_and_about_show_subnav(built_site: Path, page: str, label: str, expected: list[str]) -> None:
    """Pages under Research and About render their Book's sub-navigation."""
    assert nav_links(read_html(built_site, page)).get(label) == expected


def test_no_coder_artifacts_in_output(built_site: Path) -> None:
    """No Coder stylesheet or colour-scheme class survives in the built site."""
    html = read_html(built_site, "index.html")
    assert "coder" not in " ".join(re.findall(r'href="([^"]+\.css)"', html))
    assert "colorscheme" not in html
    assert not list(built_site.glob("css/coder*.css"))
