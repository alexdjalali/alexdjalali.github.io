"""Unit tests for post discovery and registry coverage rules (real files in ``tmp_path``)."""

from __future__ import annotations

from pathlib import Path

import pytest

from figures.content import OrphanFigureError, load_site, post_slugs, post_titles, validate_registry

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


def test_titles_are_read_from_front_matter(tmp_path: Path) -> None:
    """``post_titles`` returns each non-draft post's quoted or bare ``title``."""
    _post(tmp_path, "a.md", 'title: "Quoted: yes"')
    _post(tmp_path, "b.md", "title: Bare")
    _post(tmp_path, "c.md", "title: Draft\ndraft: true")
    assert post_titles(tmp_path) == {"a": "Quoted: yes", "b": "Bare"}


def test_site_values_come_from_hugo_toml_and_a_missing_key_is_named(tmp_path: Path) -> None:
    """``load_site`` returns title, host and definition, and names the key that is missing."""
    (tmp_path / "hugo.toml").write_text(
        'baseURL = "https://example.org/"\ntitle = "T"\n[params]\ndefinition = "D."\n', encoding="utf-8"
    )
    assert load_site(tmp_path) == ("T", "example.org", "D.")
    (tmp_path / "hugo.toml").write_text('baseURL = "https://example.org/"\ntitle = "T"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="params.definition"):
        load_site(tmp_path)
