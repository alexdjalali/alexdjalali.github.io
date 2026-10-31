"""Layout guards: nothing in a hero escapes its frame, and images and headlines stay bounded."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from figures.content import post_slugs
from tests.helpers import read_html, site_stylesheet

pytestmark = pytest.mark.integration


def _rule(css: str, selector: str) -> str:
    """Return the body of the first top-level rule whose selector list is exactly ``selector``."""
    match = re.search(r"(?:^|})" + re.escape(selector) + r"\{([^}]*)\}", css)
    assert match, f"no rule for {selector}"
    return match.group(1)


def _media_blocks(css: str, width: str) -> str:
    """Return the bodies of every ``@media (max-width: <width>)`` block in minified ``css``, joined."""
    starts = list(re.finditer(r"@media\s*\(max-width:\s*" + re.escape(width) + r"\)\{", css))
    assert starts, f"no @media (max-width: {width}) block"
    return "".join(css[m.end() : css.index("}}", m.end()) + 1] for m in starts)


@pytest.mark.parametrize(
    "fig", [".article-hero__fig", ".research-hero__fig", ".disclosure-hero__fig", ".notfound__fig"]
)
def test_narrow_hero_figures_shrink_after_their_base_rule(built_site: Path, fig: str) -> None:
    """Below 64rem each hero figure's 20rem rule comes after its base width rule, so it wins the cascade."""
    css = site_stylesheet(built_site)
    base = css.rfind(fig + "{flex:0 1")
    narrow = [
        m.start()
        for m in re.finditer(re.escape(fig) + r"\{flex:(?:none|0 0 auto);width:min\(20rem,100%\)", css)
    ]
    assert base != -1 and narrow and max(narrow) > base


def test_no_compass_ring_overflows_the_hero_figures(built_site: Path) -> None:
    """The decorative compass ring that spilled past the figure frames is gone from home and articles."""
    pages = ["index.html", "posts/how-i-learned-to-love-the-bomb/index.html"]
    assert [
        p
        for p in pages
        if 'class="compass"' in read_html(built_site, p).replace("class=compass", 'class="compass"')
    ] == []


def test_posts_share_their_generated_card_and_no_ai_image_remains(built_site: Path, repo_root: Path) -> None:
    """Every post's social image is its generated card, and the retired AI images are gone."""
    for slug in post_slugs(repo_root / "content" / "posts"):
        html = read_html(built_site, f"posts/{slug}/index.html")
        assert f"images/og/{slug}.png" in html, slug
        assert (repo_root / "static" / "images" / "og" / f"{slug}.png").exists()
        assert "images/posts/" not in html
    retired = ["headshot.png", "suspenders.png", "motorcyle.jpeg", "posts"]
    assert [n for n in retired if (repo_root / "static" / "images" / n).exists()] == []


def test_display_headlines_are_capped_and_narrow_header_stays_compact(built_site: Path) -> None:
    """Headlines top out at 3.75rem, and below 48rem the Books sit on one row under the mark and search."""
    css = site_stylesheet(built_site)
    assert "clamp(2.25rem,4.5vw,3.75rem)" in _rule(css, ".display")
    narrow = _media_blocks(css, "47.99rem")
    assert ".site-header__right{display:contents}" in narrow
    assert ".books__num{display:none}" in narrow
