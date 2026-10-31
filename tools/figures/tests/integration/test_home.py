"""Home page: the Definition, figures, consulting block and logos."""

from __future__ import annotations

import json
import re
import tomllib
from html import unescape
from pathlib import Path

import pytest

from tests.helpers import published_posts, read_html

pytestmark = pytest.mark.integration


def test_home_contains_definition_figures_cta_and_logos(built_site: Path, repo_root: Path) -> None:
    """Definition text, up to six cards and no separate latest card, both CTAs, one img per logo."""
    html = read_html(built_site, "index.html")
    n_posts = len(published_posts(repo_root))
    logos = json.loads((repo_root / "data" / "logos.json").read_text(encoding="utf-8"))
    text = re.sub(r"<[^>]+>", "", html)
    assert (
        "A blog is a set of propositions about language, machines, and the systems between them."
        in re.sub(r"\s+", " ", text)
    )
    assert html.count("<svg role=img") + html.count('<svg role="img"') == min(6, n_posts)
    assert "home-latest" not in html
    hero = html[: html.index("consulting__trust")]
    assert hero.count("mailto:alex.djalali@gmail.com") == 1
    booking = re.escape(
        tomllib.loads((repo_root / "hugo.toml").read_text(encoding="utf-8"))["params"]["bookingURL"]
    )
    assert re.search(rf'href="?{booking}"?[^>]*><i[^>]*></i> Book a Call', hero)
    assert "Book a Call" in html and "Get in Touch" in html
    assert len(re.findall(r'<img src="?/images/logos/', html)) == len(logos)
    assert "landing-service-card" not in html


def test_home_counts_come_from_generated_data(built_site: Path, repo_root: Path) -> None:
    """The Research corollary quotes the generated research.json totals."""
    research = json.loads((repo_root / "data" / "figures" / "research.json").read_text(encoding="utf-8"))
    html = read_html(built_site, "index.html")
    assert f"{research['papers']} papers, a dissertation, {research['patents']} patents" in html


def test_home_kicker_is_the_definition_label(built_site: Path, repo_root: Path) -> None:
    """The kicker above the Definition is ``params.definitionLabel``, the label the default card uses."""
    config = tomllib.loads((repo_root / "hugo.toml").read_text(encoding="utf-8"))
    label = config["params"]["definitionLabel"]
    html = read_html(built_site, "index.html")
    kicker = re.search(r'<div class="?home-hero__text"?>\s*<p class="?kicker"?>([^<]*)</p>', html)
    assert label and kicker and unescape(kicker.group(1)) == label


def test_home_grid_opens_with_the_newest_proposition(built_site: Path, repo_root: Path) -> None:
    """With the hero's latest card gone, the propositions grid starts at the newest post."""

    def date(post: Path) -> str:
        found = re.search(r"^date:\s*\"?([^\s\"]+)", post.read_text(encoding="utf-8"), re.MULTILINE)
        assert found, post
        return found.group(1)

    newest = max(published_posts(repo_root), key=date)
    html = read_html(built_site, "index.html")
    grid = html[html.index("card-grid") :]
    first = re.search(r'href="?(/posts/[^/"]+/)', grid)
    assert first and first.group(1) == f"/posts/{newest.stem}/"
