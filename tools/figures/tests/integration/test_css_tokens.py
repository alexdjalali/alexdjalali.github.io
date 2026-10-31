"""Design tokens live in ``tokens.css`` only, and the built head links one fingerprinted bundle."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration

PALETTE = {"#D62718", "#F5C400", "#1F4E9E", "#111111", "#FFFFFF"}
GREYS = {"#3A3A3A", "#4A4A4A", "#D9D9D9", "#F7F7F5", "#A8A8A8"}
# Files still carrying literals: legacy bundles removed by later tasks, and vendored icon CSS.
EXEMPT = {"tokens.css", "custom.css", "cv-timeline.css", "fontawesome.css"}
LITERAL = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\(")


def test_no_hex_literals_outside_tokens(repo_root: Path) -> None:
    """Every stylesheet except the exempt ones refers to colours through ``var(--…)`` only."""
    offenders = {}
    for css in (repo_root / "assets" / "css").rglob("*.css"):
        if css.name in EXEMPT:
            continue
        hits = LITERAL.findall(css.read_text())
        if hits:
            offenders[str(css.relative_to(repo_root))] = hits
    assert not offenders


def test_tokens_hexes_are_the_palette(repo_root: Path) -> None:
    """``tokens.css`` defines only the five palette colours and the documented greys."""
    text = (repo_root / "assets" / "css" / "tokens.css").read_text()
    found = {h.upper() for h in re.findall(r"#[0-9a-fA-F]{6}\b", text)}
    assert PALETTE <= found
    assert found <= PALETTE | GREYS


def test_head_links_one_site_bundle(built_site: Path) -> None:
    """The home ``<head>`` links exactly one ``site.*.css`` stylesheet."""
    html = read_html(built_site, "index.html")
    assert len(re.findall(r'href="?/css/site\.[^"\s>]+\.css', html)) == 1
