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
    """Definition, up to six cards (no latest card), both CTAs, a linked name per trusted-by entry."""
    html = read_html(built_site, "index.html")
    n_posts = len(published_posts(repo_root))
    logos = json.loads((repo_root / "data" / "trusted.json").read_text(encoding="utf-8"))
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
    assert "/images/logos/" not in html  # names, not 48 px bitmaps
    trust = html[html.index("consulting__trust") : html.index("rule-black")]
    names = [unescape(n) for n in re.findall(r'<a [^>]*class="?consulting__name"?[^>]*>([^<]+)</a>', trust)]
    assert names == [logo["name"] for logo in logos]
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


def test_projects_corollary_names_both_sections(built_site: Path) -> None:
    """The Book III corollary on home points at Projects and names both its sections, Systems and Courses."""
    html = read_html(built_site, "index.html")
    card = re.search(r'href="?/projects/"?[^>]*class="?card corollary"?>(.*?)</a>', html, re.DOTALL)
    assert card
    text = re.sub(r"<[^>]+>", " ", card.group(1))
    assert "Systems" in text and "courses" in text.lower()


def test_consulting_block_carries_its_proof_line(built_site: Path) -> None:
    """The consulting pitch is backed by one line of evidence: built Ask Data, sold PerceptivePanda."""
    html = read_html(built_site, "index.html")
    proof = re.search(r'class="?consulting__proof"?>(.*?)</p>', html, re.DOTALL)
    assert proof
    text = unescape(re.sub(r"<[^>]+>", "", proof.group(1)))
    assert "Ask Data" in text and "PerceptivePanda" in text and "Zapier" in text
