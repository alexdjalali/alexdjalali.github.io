"""Projects page: one figure per project, no stray mermaid, GitHub links kept."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def test_projects_figures_one_per_project_card(built_site: Path, repo_root: Path) -> None:
    """Each ``.project-card`` in the source gets exactly one figure."""
    source = (repo_root / "content" / "projects.md").read_text(encoding="utf-8")
    cards = source.count('class="project-card"')
    html = read_html(built_site, "projects/index.html")
    assert cards > 0
    assert html.count("<svg role=") == cards


def test_projects_page_has_no_mermaid_and_keeps_github_links(built_site: Path, repo_root: Path) -> None:
    """The unconditional mermaid script is gone and every GitHub link from the source is present."""
    html = read_html(built_site, "projects/index.html")
    assert "mermaid" not in html
    source = (repo_root / "content" / "projects.md").read_text(encoding="utf-8")
    links = set(re.findall(r'href="(https://github\.com/[^"]+)"', source))
    assert links
    for href in links:
        assert href in html


def test_courses_page_carries_the_tiya_course_with_one_figure(built_site: Path, repo_root: Path) -> None:
    """Courses is its own page: one figure per course card, and the TIYA kit links live there."""
    source = (repo_root / "content" / "courses.md").read_text(encoding="utf-8")
    html = read_html(built_site, "courses/index.html")
    assert html.count("<svg role=") == source.count('class="project-card"') > 0
    assert "/presentations/tiya-applied-ai/participants.html" in html
    assert "tiya-applied-ai" not in read_html(built_site, "projects/index.html")


def test_talks_list_the_tiya_course_and_link_to_it(built_site: Path) -> None:
    """Talks names the TIYA course but links to the Courses page instead of carrying its materials."""
    html = read_html(built_site, "presentations/index.html")
    assert "Applied AI at TIYA Services" in html
    assert re.search(r'href="?/courses/"?', html)
    assert "participant-workbook-day1.html" not in html
