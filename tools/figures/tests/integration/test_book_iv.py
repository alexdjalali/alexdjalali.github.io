"""Media, Gear and AI disclosure pages keep their content and gain their figures and badges."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def test_media_renders_every_card_with_a_cover(built_site: Path, repo_root: Path) -> None:
    """One card-deck item and one real cover image per entry in content/media.md."""
    source = (repo_root / "content" / "media.md").read_text(encoding="utf-8")
    expected = source.count("card-deck-item")
    html = read_html(built_site, "media/index.html")
    items = re.findall(r'class="?project-card card-deck-item"?', html)
    assert expected > 0 and len(items) == expected
    assert len(re.findall(r'<img src="?/images/[^"\s>]+', html)) >= expected
    assert "card-deck" in (repo_root / "assets" / "js" / "card-deck.js").read_text(encoding="utf-8")


def test_gear_renders_every_category_and_item(built_site: Path, repo_root: Path) -> None:
    """One block per ``categories`` entry in the front matter and one list item per ``items`` entry."""
    front = (repo_root / "content" / "gear.md").read_text(encoding="utf-8").split("---")[1]
    categories = len(re.findall(r"^  - title:", front, re.MULTILINE))
    items = len(re.findall(r"^      - ", front, re.MULTILINE))
    html = read_html(built_site, "gear/index.html")
    assert categories > 0
    assert len(re.findall(r'<section class="?gear-card', html)) == categories
    assert len(re.findall(r"<li>", html.split("gear-grid", 1)[1])) == items


def test_disclosure_has_the_venn_figure_and_both_badges(built_site: Path) -> None:
    """The disclosure page shows the Venn figure and the two badge examples with shared classes."""
    html = read_html(built_site, "ai-disclaimer/index.html")
    assert "fig-pages-ai-venn-cap" in html
    assert "badge-ai" in html and "badge-no-ai" in html
    assert "#2980b9" not in html


def test_about_content_ends_with_the_signature_not_a_figure(built_site: Path) -> None:
    """The About article closes on the signature; the Scout figure lives on Gear, not hanging after it."""
    html = read_html(built_site, "about/index.html")
    start = re.search(r'<article class="?about-content', html)
    assert start
    body = html[start.end() : html.index("</article>", start.end())]
    assert "fig-pages-scout-cap" not in body
    assert "about-signature" in body
