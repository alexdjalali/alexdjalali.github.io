"""Code blocks carry Chroma classes and the stylesheet maps them to the palette."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html, site_stylesheet

pytestmark = pytest.mark.integration


def test_code_blocks_use_chroma_classes(built_site: Path) -> None:
    """A highlighted block renders ``class=chroma`` with token spans instead of inline styles."""
    html = read_html(built_site, "posts/the-ideal-repository-structure/index.html")
    assert re.search(r'<pre[^>]*class="?chroma"?', html)
    assert re.search(r'<span class="?k[dn]?"?>', html)
    assert 'style="color:#' not in html


def test_stylesheet_defines_token_rules_without_blue(built_site: Path, repo_root: Path) -> None:
    """The built CSS has the keyword rule and the syntax source never colours a token blue."""
    css = site_stylesheet(built_site)
    assert ".chroma .k," in css or ".chroma .k{" in css
    assert "var(--blue)" not in (repo_root / "assets" / "css" / "syntax.css").read_text(encoding="utf-8")
