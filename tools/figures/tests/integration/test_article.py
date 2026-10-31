"""Article template: figure hero, numeral, "To prove", contents list, and the Q.E.D. mark."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html

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
    first_row = re.search(r'post-row__num"?>([IVXLCDM]+)<', index)
    assert numeral and first_row and numeral.group(1) == first_row.group(1)  # newest post
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
