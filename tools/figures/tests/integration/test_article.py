"""Article template: figure hero, numeral, "To prove", contents list, and the Q.E.D. mark."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import published_posts, read_html

pytestmark = pytest.mark.integration

POST = "posts/rethinking-agile-in-the-age-of-ai/index.html"


def test_article_has_figure_numeral_prove_toc_and_qed(built_site: Path) -> None:
    """The Rethinking Agile page carries every element of the proposition layout."""
    html = read_html(built_site, POST)
    assert re.search(
        r'<svg role="?img"? aria-labelledby="?fig-posts-rethinking-agile-in-the-age-of-ai-cap', html
    )
    numeral = re.search(r"Proposition ([IVXLCDM]+)\.", html)
    index = read_html(built_site, "posts/index.html")
    slug = POST.split("/")[1]
    row = re.search(rf'href="?/posts/{slug}/"?[^>]*>\s*<span class="?post-row__num"?>([IVXLCDM]+)<', index)
    assert numeral and row and numeral.group(1) == row.group(1)  # same numeral as its index row
    assert "To prove:" in html
    assert "Q.E.D." in html


def test_contents_has_one_entry_per_h2(built_site: Path) -> None:
    """The Contents list's top-level entries equal the h2 headings of the rendered body."""
    html = read_html(built_site, POST)
    body = html.split("post-content", 1)[1]
    h2s = len(re.findall(r"<h2[ >]", body))
    toc = re.search(r'id="?TableOfContents"?>(.*?)</nav>', html, re.DOTALL)
    assert toc and h2s > 0
    top_level = re.findall(
        r"<li>\s*<a href",
        re.sub(r"<ul>.*?</ul>", "", toc.group(1)[toc.group(1).index("<ul>") + 4 :], flags=re.DOTALL),
    )
    assert len(top_level) == h2s


def test_retained_article_features_remain(built_site: Path) -> None:
    """Reading progress, share buttons, related posts, author bio, post nav and giscus all render."""
    html = read_html(built_site, POST)
    for needle in ("reading-progress", "copy-link-btn", "author-bio", "post-nav", "giscus"):
        assert needle in html, needle


def test_every_post_ends_with_a_feed_prompt(built_site: Path, repo_root: Path) -> None:
    """Each published post invites readers to follow along, linking the site's RSS feed."""
    for post in published_posts(repo_root):
        html = read_html(built_site, f"posts/{post.stem}/index.html")
        follow = re.search(r'class="?follow-along"?[^>]*>(.*?)</', html, re.DOTALL)
        feed = re.search(r'href="?(?:https://alexdjalali\.github\.io)?/index\.xml"?', html)
        assert follow and feed, post.stem
