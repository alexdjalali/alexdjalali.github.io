"""Home page: the Definition, figures, consulting block and logos."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def test_home_contains_definition_figures_cta_and_logos(built_site: Path, repo_root: Path) -> None:
    """Definition text, latest + up to six cards, both CTAs with original hrefs, one img per logo."""
    html = read_html(built_site, "index.html")
    n_posts = len(list((repo_root / "content" / "posts").glob("*.md")))
    logos = json.loads((repo_root / "data" / "logos.json").read_text(encoding="utf-8"))
    text = re.sub(r"<[^>]+>", "", html)
    assert (
        "A blog is a set of propositions about language, machines, and the systems between them."
        in re.sub(r"\s+", " ", text)
    )
    assert html.count("<svg role=img") + html.count('<svg role="img"') == 1 + min(6, n_posts - 1)
    assert html.count("mailto:alex.djalali@gmail.com") == 2
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
    assert label and re.search(r'<p class="?kicker"?>' + re.escape(label) + "</p>", html)
