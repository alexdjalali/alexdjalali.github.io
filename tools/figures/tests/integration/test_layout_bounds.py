"""Layout guards: nothing in a hero escapes its frame, and images and headlines stay bounded."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html, site_stylesheet

pytestmark = pytest.mark.integration


def _rule(css: str, selector: str) -> str:
    """Return the body of the first top-level rule whose selector list is exactly ``selector``."""
    match = re.search(r"(?:^|})" + re.escape(selector) + r"\{([^}]*)\}", css)
    assert match, f"no rule for {selector}"
    return match.group(1)


def test_no_compass_ring_overflows_the_hero_figures(built_site: Path) -> None:
    """The decorative compass ring that spilled past the figure frames is gone from home and articles."""
    pages = ["index.html", "posts/how-i-learned-to-love-the-bomb/index.html"]
    assert [
        p
        for p in pages
        if 'class="compass"' in read_html(built_site, p).replace("class=compass", 'class="compass"')
    ] == []


def test_post_cover_images_are_height_capped(built_site: Path) -> None:
    """A post's featured image carries the ``post-cover`` class and the stylesheet caps its height."""
    html = read_html(built_site, "posts/how-i-learned-to-love-the-bomb/index.html")
    assert re.search(r'<img class="?post-cover"?', html)
    assert "max-height:24rem" in _rule(site_stylesheet(built_site), ".post-cover")


def test_display_headlines_are_capped_and_narrow_header_stays_compact(built_site: Path) -> None:
    """Headlines top out at 3.75rem, and below 48rem the Books sit on one row under the mark and search."""
    css = site_stylesheet(built_site)
    assert "clamp(2.25rem,4.5vw,3.75rem)" in _rule(css, ".display")
    narrow = re.split(r"@media\s*\(max-width:\s*47\.99rem\)\{", css, maxsplit=1)[1]
    assert ".site-header__right{display:contents}" in narrow
    assert ".books__num{display:none}" in narrow
