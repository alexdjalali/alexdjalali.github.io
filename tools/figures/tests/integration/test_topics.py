"""Topic filter data: every post tag maps to a topic, and the Writing index renders one chip per topic."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def _post_tags(repo_root: Path) -> dict[str, list[str]]:
    tags: dict[str, list[str]] = {}
    for path in (repo_root / "content" / "posts").glob("*.md"):
        m = re.search(r"^tags:\s*\[(.*?)\]", path.read_text(encoding="utf-8"), re.MULTILINE)
        tags[path.stem] = re.findall(r'"([^"]+)"', m.group(1)) if m else []
    return tags


def test_every_post_tag_maps_to_a_topic(repo_root: Path) -> None:
    """No tag is orphaned, so every post can be reached through at least one topic chip."""
    topics = json.loads((repo_root / "data" / "topics.json").read_text(encoding="utf-8"))
    mapped = {t for topic in topics for t in topic["tags"]}
    unmapped = {
        slug: sorted(set(tags) - mapped) for slug, tags in _post_tags(repo_root).items() if set(tags) - mapped
    }
    assert unmapped == {}


def test_every_post_has_at_least_one_topic(repo_root: Path) -> None:
    """A post whose tags match no topic would be hidden by every chip except All."""
    topics = json.loads((repo_root / "data" / "topics.json").read_text(encoding="utf-8"))
    for slug, tags in _post_tags(repo_root).items():
        assert any(set(tags) & set(t["tags"]) for t in topics), slug


def test_writing_index_renders_one_chip_per_topic(built_site: Path, repo_root: Path) -> None:
    """The list page has a chip for each entry in ``data/topics.json``."""
    topics = json.loads((repo_root / "data" / "topics.json").read_text(encoding="utf-8"))
    html = read_html(built_site, "posts/index.html")
    assert len(re.findall(r'<button[^>]*class="?chip"?[^>]*data-topic=', html)) == len(topics)


def test_writing_index_lists_every_post_newest_first(built_site: Path, repo_root: Path) -> None:
    """One item and one figure per post, numerals descending, count text in roman numerals."""
    n = len(list((repo_root / "content" / "posts").glob("*.md")))
    html = read_html(built_site, "posts/index.html")
    assert len(re.findall(r"<li class=\"?post-item\"?", html)) == n
    assert html.count("<svg role=") == n
    nums = [_roman(m) for m in re.findall(r'<span class="?post-row__num"?>([IVXLCDM]+)</span>', html)]
    assert nums == sorted(nums, reverse=True) == list(range(n, 0, -1))
    count = re.search(r'id="?topic-count"?[^>]*>([IVXLCDM]+) of ([IVXLCDM]+) shown', html)
    assert count and count.group(1) == count.group(2)
    assert _roman(count.group(1)) == n


def _roman(s: str) -> int:
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for a, b in zip(s, [*s[1:], ""], strict=True):
        total += -values[a] if b and values[a] < values[b] else values[a]
    return total
