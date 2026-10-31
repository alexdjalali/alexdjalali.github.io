"""Resume Technologies: rendered from ``data/technologies.json``, every icon served from the site."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def _groups(repo_root: Path) -> list[dict[str, object]]:
    """Return the technology groups from the data file."""
    return json.loads((repo_root / "data" / "technologies.json").read_text(encoding="utf-8"))["groups"]


def test_every_technology_renders_with_a_vendored_icon(built_site: Path, repo_root: Path) -> None:
    """Each data entry is one grid item whose icon is a local file under ``static/images/tech``."""
    html = read_html(built_site, "cv/index.html")
    section = html[html.index("tech-section") :]
    srcs = re.findall(r'<img src="?([^"\s>]+)', section)
    items = [item for group in _groups(repo_root) for item in group["items"]]  # type: ignore[union-attr]
    assert len(srcs) == len(items) > 0
    assert all(src.startswith("/images/tech/") for src in srcs), srcs
    assert [s.rsplit("/", 1)[1] for s in srcs] == [item["icon"] for item in items]
    assert all((repo_root / "static" / "images" / "tech" / item["icon"]).is_file() for item in items)


def test_every_vendored_icon_records_its_source_and_is_used(repo_root: Path) -> None:
    """Every icon file is referenced by exactly one entry, and every entry names an https source."""
    items = [item for group in _groups(repo_root) for item in group["items"]]  # type: ignore[union-attr]
    files = sorted(p.name for p in (repo_root / "static" / "images" / "tech").iterdir())
    assert sorted(item["icon"] for item in items) == files
    assert all(str(item["source"]).startswith("https://") for item in items)


def test_no_third_party_icon_host_remains(built_site: Path, repo_root: Path) -> None:
    """With icons vendored, the CSP and head no longer allow or prefetch the old icon CDN."""
    assert "icepanel" not in (repo_root / "hugo.toml").read_text(encoding="utf-8")
    assert "icepanel" not in read_html(built_site, "cv/index.html")
