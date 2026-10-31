"""Unit tests for the BibTeX loader, run against the real ``static/bib`` files."""

from __future__ import annotations

from pathlib import Path

import pytest

from figures.bib import load_entries, output_by_year, research_summary

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def entries(repo_root: Path):
    """Load the repo's bibliography once."""
    return load_entries(repo_root / "static" / "bib")


def test_one_entry_per_file(repo_root: Path, entries) -> None:
    """Every ``.bib`` file yields exactly one entry."""
    files = list((repo_root / "static" / "bib").glob("*.bib"))
    assert len(entries) == len(files) > 0


def test_patents_are_the_files_named_patent(repo_root: Path, entries) -> None:
    """Patent entries equal the files whose stem contains ``patent``."""
    files = [p for p in (repo_root / "static" / "bib").glob("*.bib") if "patent" in p.stem]
    assert sum(e.kind == "patent" for e in entries) == len(files)
    assert sum(e.kind == "dissertation" for e in entries) == 1


def test_fields_are_parsed(entries) -> None:
    """Braces are stripped and the venue falls back through the venue fields."""
    e = next(e for e in entries if e.key == "djalali2012finnish")
    assert e.year == 2012
    assert "{" not in e.title
    assert e.venue.startswith("Proceedings of the 30th West Coast")


def test_summary_totals_equal_the_entry_count(entries) -> None:
    """Papers, patents and the dissertation partition the entries, by year as well."""
    s = research_summary(entries)
    assert s["papers"] + s["patents"] + s["dissertation"] == s["total"] == len(entries)
    assert sum(n for kinds in s["by_year"].values() for n in kinds.values()) == len(entries)
    assert sum(output_by_year(entries).values()) == len(entries)


def _write_bib(tmp_path: Path, body: str) -> Path:
    """Write one ``.bib`` file holding ``body`` and return its directory."""
    (tmp_path / "x.bib").write_text(body, encoding="utf-8")
    return tmp_path


def test_bare_year_value_is_parsed(tmp_path: Path) -> None:
    """Scholar-style ``year = 2027,`` (no braces or quotes) is read as a year."""
    bib = _write_bib(tmp_path, "@article{k2027,\n  title={T},\n  year = 2027,\n  journal={J}\n}\n")
    assert load_entries(bib)[0].year == 2027


def test_missing_year_names_the_file(tmp_path: Path) -> None:
    """An entry without a year fails with the file name, not a bare ``KeyError``."""
    bib = _write_bib(tmp_path, "@article{k,\n  title={T},\n  journal={J}\n}\n")
    with pytest.raises(ValueError, match=r"x\.bib: no year"):
        load_entries(bib)
