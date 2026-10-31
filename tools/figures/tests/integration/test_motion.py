"""The motion stylesheet animates only with JS and falls back to fully drawn figures."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
ANIMATES = re.compile(r"animation(?:-name)?\s*:\s*(?!none)[a-z]", re.IGNORECASE)


def _bundle(built_site: Path) -> str:
    return next((built_site / "css").glob("site.*.css")).read_text(encoding="utf-8")


def test_bundle_has_keyframes_and_a_reduced_motion_block(built_site: Path) -> None:
    """The built CSS defines ``draw`` and turns off ``.an-draw`` under reduced motion."""
    css = re.sub(r"\s+", "", _bundle(built_site))
    assert "@keyframesdraw" in css
    blocks = re.findall(r"@media\(prefers-reduced-motion:reduce\)\{(.*?)\}\}", css)
    assert any(".an-draw" in b and "animation:none!important" in b for b in blocks)


def test_no_animation_rule_applies_outside_js(repo_root: Path) -> None:
    """Every rule that starts an animation is scoped under ``.js`` (no-JS pages stay static)."""
    css = (repo_root / "assets" / "css" / "motion.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    offenders = [
        sel.strip()
        for sel, body in RULE.findall(css)
        if ANIMATES.search(body)
        and not sel.strip().startswith((".js", "@keyframes"))
        and "!important" not in body
    ]
    assert offenders == []
    assert ".js .fig .an-draw" in css
