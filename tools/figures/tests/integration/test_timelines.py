"""About and Resume: generated static lanes sit inside the D3 containers, and no dark-mode path remains."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration

TIMELINE_ASSETS = ["assets/js/cv-timeline.js", "assets/js/about-timeline.js", "assets/css/cv-timeline.css"]


def _inside(html: str, container_id: str) -> str:
    """Return the markup following ``id=<container_id>`` up to its figure's closing tag."""
    m = re.search(rf'id="?{container_id}"?[^>]*>(.*?</figure>)', html, re.DOTALL)
    assert m, f"no static figure inside #{container_id}"
    return m.group(1)


def _entries(html: str, var: str) -> int:
    """Count the objects in the inline ``var <var> = [...]`` data (the minifier unquotes keys)."""
    m = re.search(rf"var {var}\s*=\s*(\[.*?\])\s*;?\s*</script>", html, re.DOTALL)
    assert m, var
    return len(re.findall(r'"?startdate"?\s*:', m.group(1)))


def test_about_has_headshot_static_lifeline_and_location_data(built_site: Path, repo_root: Path) -> None:
    """The About page shows the portrait, a generated lifeline inside the container, and all locations."""
    html = read_html(built_site, "about/index.html")
    assert "headshot" in html
    assert "<svg" in _inside(html, "about-timeline")
    expected = len(json.loads((repo_root / "data" / "locations.json").read_text()))
    assert _entries(html, "locationData") == expected


def test_resume_has_sections_pdf_and_static_lanes(built_site: Path, repo_root: Path) -> None:
    """The Resume page keeps its ids, the PDF link, static lanes, and every timeline entry."""
    html = read_html(built_site, "cv/index.html")
    for needle in ("id=experience", "id=education", "djalali-resume.pdf"):
        assert needle in html.replace('"', "")
    assert "<svg" in _inside(html, "timeline")
    expected = len(json.loads((repo_root / "data" / "timeline.json").read_text()))
    assert _entries(html, "timelineData") == expected


@pytest.mark.parametrize("path", TIMELINE_ASSETS)
def test_timeline_assets_have_no_dark_mode_or_hex(repo_root: Path, path: str) -> None:
    """Timeline code reads the palette at runtime: no colour-scheme branches, no hex literals."""
    text = (repo_root / path).read_text()
    assert not re.search(r"colorscheme|isDarkMode|prefers-color-scheme", text)
    assert not re.search(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b", text)


@pytest.mark.parametrize("path", TIMELINE_ASSETS[:2])
def test_timeline_scripts_clear_their_container(repo_root: Path, path: str) -> None:
    """Each script empties its container before drawing, replacing the static lanes."""
    assert 'container.html("")' in (repo_root / path).read_text()
