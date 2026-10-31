"""Archive, series and taxonomy term pages render with the repo's real posts."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import published_posts, read_html

pytestmark = pytest.mark.integration


def test_archive_lists_every_post(built_site: Path, repo_root: Path) -> None:
    """The archive has one row per post in ``content/posts``, each with a numeral."""
    n = len(published_posts(repo_root))
    html = read_html(built_site, "archives/index.html")
    assert len(re.findall(r'class="?archive-item', html)) == n
    assert len(re.findall(r'class="?archive-num"?>[IVXLCDM]+<', html)) == n
    assert f"{n} posts" in html


def test_series_and_tags_pages_render(built_site: Path) -> None:
    """The series index, its single series page, and the tag index render their headings."""
    assert "series-card" in read_html(built_site, "series/index.html")
    assert "series-post-item" in read_html(built_site, "series/software-architecture/index.html")
    assert "Tags" in read_html(built_site, "tags/index.html")
