"""The legacy theme is gone: no legacy stylesheet, no dark mode, no dead scripts."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration

DARK_MODE = re.compile(r"colorscheme|prefers-color-scheme\s*:\s*dark|isDarkMode", re.IGNORECASE)


def _stylesheet(built_site: Path) -> str:
    html = read_html(built_site, "index.html")
    match = re.search(r'href="?(/css/site[^"\s>]*\.css)', html)
    assert match, "built home page does not link the site stylesheet"
    return (built_site / match.group(1).lstrip("/")).read_text()


def test_legacy_stylesheet_is_removed(repo_root: Path) -> None:
    """No ``custom.css`` file and no ``customCSS`` parameter remain."""
    config = tomllib.loads((repo_root / "hugo.toml").read_text())
    assert not (repo_root / "assets" / "css" / "custom.css").exists()
    assert "customCSS" not in config["params"]


def test_dark_mode_is_absent_from_css_html_and_scripts(built_site: Path, repo_root: Path) -> None:
    """Dark mode was removed by decision; neither CSS, HTML nor scripts may mention it."""
    offenders = [
        name for name, text in {"site.css": _stylesheet(built_site)}.items() if DARK_MODE.search(text)
    ]
    for page in ("index.html", "posts/index.html", "about/index.html", "cv/index.html"):
        if DARK_MODE.search(read_html(built_site, page)):
            offenders.append(page)
    offenders += [
        p.name for p in (repo_root / "assets" / "js").glob("*.js") if DARK_MODE.search(p.read_text())
    ]
    assert offenders == []


def test_every_configured_script_is_present_and_used(repo_root: Path) -> None:
    """Each ``customJS`` entry exists, and no script in ``assets/js`` is left unconfigured or unreferenced."""
    config = tomllib.loads((repo_root / "hugo.toml").read_text())
    configured = {Path(p).name for p in config["params"]["customJS"]}
    on_disk = {p.name for p in (repo_root / "assets" / "js").glob("*.js")}
    templated = {
        name
        for name in on_disk
        if any(name in t.read_text() for t in (repo_root / "layouts").rglob("*.html"))
    }
    assert configured <= on_disk
    assert on_disk - configured - templated == set()
