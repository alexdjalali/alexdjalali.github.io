"""The legacy theme is gone: no legacy stylesheet, no dark mode, no dead scripts."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

from tests.helpers import read_html, site_stylesheet

pytestmark = pytest.mark.integration

DARK_MODE = re.compile(r"colorscheme|prefers-color-scheme\s*:\s*dark|isDarkMode", re.IGNORECASE)


def test_legacy_stylesheet_is_removed(repo_root: Path) -> None:
    """No ``custom.css`` file and no ``customCSS`` parameter remain."""
    config = tomllib.loads((repo_root / "hugo.toml").read_text(encoding="utf-8"))
    assert not (repo_root / "assets" / "css" / "custom.css").exists()
    assert "customCSS" not in config["params"]


def test_dark_mode_is_absent_from_css_html_and_scripts(built_site: Path, repo_root: Path) -> None:
    """Dark mode was removed by decision; neither CSS, HTML nor scripts may mention it."""
    offenders = ["site.css"] if DARK_MODE.search(site_stylesheet(built_site)) else []
    for page in ("index.html", "posts/index.html", "about/index.html", "cv/index.html"):
        if DARK_MODE.search(read_html(built_site, page)):
            offenders.append(page)
    offenders += [
        p.name
        for p in (repo_root / "assets" / "js").glob("*.js")
        if DARK_MODE.search(p.read_text(encoding="utf-8"))
    ]
    assert offenders == []


def test_every_configured_script_is_present_and_used(repo_root: Path) -> None:
    """Each ``customJS`` entry exists, and no script in ``assets/js`` is left unconfigured or unreferenced."""
    config = tomllib.loads((repo_root / "hugo.toml").read_text(encoding="utf-8"))
    configured = {Path(p).name for p in config["params"]["customJS"]}
    on_disk = {p.name for p in (repo_root / "assets" / "js").glob("*.js")}
    templated = {
        name
        for name in on_disk
        if any(name in t.read_text(encoding="utf-8") for t in (repo_root / "layouts").rglob("*.html"))
    }
    assert configured <= on_disk
    assert on_disk - configured - templated == set()


def test_stylesheet_has_no_dead_animation_and_one_owner_for_the_lemma_box(
    built_site: Path, repo_root: Path
) -> None:
    """No ``gradient-slide`` or sliding ``background-size`` survives; one rule styles the Lemma box."""
    css = site_stylesheet(built_site)
    assert "gradient-slide" not in css
    timeline = (repo_root / "assets" / "css" / "cv-timeline.css").read_text(encoding="utf-8")
    assert re.search(r"background-size:\s*200%\s*100%", timeline) is None
    assert len(re.findall(r"\.post-content blockquote[,{]", css)) == 1
