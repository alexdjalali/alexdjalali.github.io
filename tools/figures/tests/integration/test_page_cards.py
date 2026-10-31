"""Every Book page shares its own social card, drawn from the same kicker and headline as its hero."""

from __future__ import annotations

import re
from html import unescape
from pathlib import Path

import pytest

from figures.content import page_cards
from tests.helpers import read_html

pytestmark = pytest.mark.integration

PAGES = (
    "about",
    "ai-disclaimer",
    "courses",
    "cv",
    "gear",
    "media",
    "consulting",
    "presentations",
    "projects",
    "publications",
)


def test_every_book_page_has_its_own_card(repo_root: Path) -> None:
    """Each Book page declares a card; none falls back to the shared default image."""
    assert set(page_cards(repo_root / "content")) == set(PAGES)


@pytest.mark.parametrize("name", PAGES)
def test_page_shares_its_card_and_hero_matches_it(built_site: Path, repo_root: Path, name: str) -> None:
    """The page's og:image is its card, the card exists, and the hero shows the card's kicker."""
    html = read_html(built_site, f"{name}/index.html")
    image = re.search(r'property="?og:image"? content="?([^" >]+)', html)
    assert image and image.group(1).endswith(f"/images/og/pages/{name}.png")
    assert (repo_root / "static" / "images" / "og" / "pages" / f"{name}.png").exists()
    kicker = re.search(r'<p class="?kicker"?>([^<]*)</p>', html)
    assert kicker and unescape(kicker.group(1)) == page_cards(repo_root / "content")[name].kicker
