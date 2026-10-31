"""Research and Talks pages: figures, generated counts, and the retained links and toggles."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def _hrefs(text: str, cls: str) -> list[str]:
    return re.findall(rf'<a [^>]*href="?([^"\s>]+)"?[^>]*class="?[^">]*{cls}', text) + re.findall(
        rf'<a [^>]*class="?[^">]*{cls}[^>]*href="?([^"\s>]+)', text
    )


def test_research_hero_counts_match_bib_files(built_site: Path, repo_root: Path) -> None:
    """The lede quotes the paper and patent counts derived from the .bib file names."""
    files = [p.stem for p in (repo_root / "static" / "bib").glob("*.bib")]
    patents = sum("patent" in f for f in files)
    papers = sum("patent" not in f and "dissertation" not in f for f in files)
    html = read_html(built_site, "publications/index.html")
    assert f"{papers} papers, {patents} patents" in html
    assert "fig-pages-research-output-cap" in html


def test_every_bib_link_resolves(built_site: Path) -> None:
    """Each local .bib href on the Research page points at a file in the built site."""
    html = read_html(built_site, "publications/index.html")
    local = [h for h in re.findall(r'href="?(/bib/[^"\s>]+\.bib)', html)]
    assert local
    for href in local:
        assert (built_site / href.lstrip("/")).is_file(), href


def test_abstract_toggle_selector_matches_each_abstract(built_site: Path, repo_root: Path) -> None:
    """Each source ``<li>`` with an abstract still yields one ``.pub-abstract`` for the toggle."""
    source = (repo_root / "content" / "publications.md").read_text(encoding="utf-8")
    expected = len(re.findall(r'class="pub-abstract"', source))
    html = read_html(built_site, "publications/index.html")
    assert expected > 0
    assert len(re.findall(r'class="?pub-abstract"?', html)) == expected


def test_talks_has_two_figures_and_all_links(built_site: Path, repo_root: Path) -> None:
    """Two talk figures render and every bib-link href from the source is present."""
    html = read_html(built_site, "presentations/index.html")
    source = (repo_root / "content" / "presentations.md").read_text(encoding="utf-8")
    assert html.count("<svg role=") == 2
    for href in set(re.findall(r'href="([^"]+)" class="bib-link"', source)):
        assert href in html, href
