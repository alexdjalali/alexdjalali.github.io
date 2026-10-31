"""Unit tests for post discovery and registry coverage rules (real files in ``tmp_path``)."""

from __future__ import annotations

from pathlib import Path

import pytest

from figures.content import OrphanFigureError, post_slugs, validate_registry

pytestmark = pytest.mark.unit


def _post(d: Path, name: str, front: str) -> None:
    (d / name).write_text(f"---\n{front}\n---\nbody\n", encoding="utf-8")


def test_drafts_are_excluded_and_slugs_are_filename_stems(tmp_path: Path) -> None:
    """Only non-draft ``*.md`` files count; the slug is the filename stem."""
    _post(tmp_path, "alpha.md", 'title: "Alpha"\ndraft: false')
    _post(tmp_path, "beta.md", 'title: "Beta"\ndraft: true')
    _post(tmp_path, "gamma.md", 'title: "Gamma"')
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")
    assert post_slugs(tmp_path) == ["alpha", "gamma"]


def test_orphan_registration_raises_naming_the_slug() -> None:
    """A registered slug with no post fails and says which."""
    with pytest.raises(OrphanFigureError, match="ghost"):
        validate_registry(["alpha"], {"alpha": object(), "ghost": object()})


def test_unregistered_post_is_accepted() -> None:
    """A post with no registry entry is fine; the default applies."""
    validate_registry(["alpha", "new-post"], {"alpha": object()})
