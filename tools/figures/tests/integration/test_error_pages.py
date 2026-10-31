"""404 and search pages, and the mermaid loader's palette."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def test_404_has_headline_search_and_recent_posts(built_site: Path) -> None:
    """The 404 carries the contradiction headline, a search input, and three recent propositions."""
    html = read_html(built_site, "404.html")
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    assert "Suppose this page exists." in text
    assert re.search(r'<input[^>]*id="?search-input"?', html)
    assert "data-index" in html
    assert len(re.findall(r'class="?card prop-card', html)) == 3
    assert "Return to Definition 1" in html


def test_search_page_keeps_script_hooks(built_site: Path) -> None:
    """The search page keeps the ids and data attribute that search.js reads."""
    html = read_html(built_site, "search/index.html")
    for needle in ("search-input", "search-results", "data-index"):
        assert needle in html


def test_no_dark_mode_remains_in_the_base_layout(repo_root: Path, built_site: Path) -> None:
    """The shell has no colour-scheme branches and the mermaid loader reads palette variables."""
    source = (repo_root / "layouts" / "baseof.html").read_text()
    assert "colorscheme" not in source
    assert "prefers-color-scheme" not in source
    assert "getPropertyValue" in source
    assert not re.search(r"#[0-9a-fA-F]{6}\b", source)
    assert "colorscheme" not in read_html(built_site, "index.html")
