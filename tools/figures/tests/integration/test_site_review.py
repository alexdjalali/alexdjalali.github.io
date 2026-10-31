"""Site-review fixes: readable tag names, lean pages, light feeds, a consulting page and coherent series."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

from tests.helpers import published_posts, read_html

pytestmark = pytest.mark.integration

MATH_POST = "posts/dependency-to-lambda/index.html"
PLAIN_POST = "posts/rethinking-agile-in-the-age-of-ai/index.html"
DIAGRAM_POST = "posts/six-months-of-enterprise-development-with-ai/index.html"
LONE_TAGS = {"nlp", "formal-semantics", "education"}
"""Tags of a topic with one post so far; every other tag must group at least two posts."""


def _tags(path: Path) -> list[str]:
    """Return the tag slugs in a post's front matter."""
    found = re.search(r"^tags:\s*\[(.*?)\]", path.read_text(encoding="utf-8"), re.MULTILINE)
    return re.findall(r'"([^"]+)"', found.group(1)) if found else []


def test_tags_render_with_their_proper_names(built_site: Path) -> None:
    """Acronyms stay upper case and slugs lose their hyphens: ``AI``, ``Software Engineering``."""
    html = read_html(built_site, PLAIN_POST)
    terms = re.findall(r'<span class="?tag"?><a href="?/tags/[^">]+/"?>([^<]+)</a>', html)
    assert "AI" in terms
    assert "Software Engineering" in terms
    assert not [t for t in terms if "-" in t or t == "Ai"]


def test_every_tag_but_a_lone_topic_groups_at_least_two_posts(repo_root: Path) -> None:
    """A tag page that lists one post is noise; only declared lone topics may have one."""
    counts = Counter(tag for post in published_posts(repo_root) for tag in _tags(post))
    assert {tag for tag, n in counts.items() if n < 2} <= LONE_TAGS


def test_retired_tag_urls_still_resolve(built_site: Path) -> None:
    """A merged tag's old page redirects to the tag that absorbed it, so inbound links keep working."""
    for old in ("resilience", "neovim", "estimation"):
        page = built_site / "tags" / old / "index.html"
        assert page.is_file(), old
        assert re.search(r'http-equiv="?refresh"?', page.read_text(encoding="utf-8")), old


def test_each_series_is_one_thread(built_site: Path) -> None:
    """Architecture essays and the AI-assisted engineering arc are separate series, not one long list."""
    architecture = read_html(built_site, "series/software-architecture/index.html")
    assert "Rethinking Agile" not in architecture
    ai = read_html(built_site, "series/ai-assisted-engineering/index.html")
    assert "Rethinking Agile" in ai and "How I Learned" in ai


def test_katex_loads_only_on_pages_with_math(built_site: Path) -> None:
    """The math post loads KaTeX; a post with no math and the home page do not."""
    assert "katex.min.js" in read_html(built_site, MATH_POST)
    assert "katex" not in read_html(built_site, PLAIN_POST)
    assert "katex" not in read_html(built_site, "index.html")


def test_mermaid_is_deferred_and_configured_from_a_file(built_site: Path) -> None:
    """Mermaid never blocks parsing, and its palette set-up lives in a fingerprinted script, not inline."""
    html = read_html(built_site, DIAGRAM_POST)
    tag = re.search(r"<script[^>]*mermaid\.min\.js[^>]*>", html)
    assert tag and " defer" in tag.group(0)
    assert "mermaid.initialize" not in html
    assert re.search(r'<script[^>]*src="?/js/mermaid-init[^"\s>]*\.js', html)


def test_site_scripts_are_one_deferred_bundle(built_site: Path) -> None:
    """Every page loads one fingerprinted, deferred script bundle instead of one request per feature."""
    html = read_html(built_site, PLAIN_POST)
    bundles = re.findall(r"<script[^>]*src=\"?/js/site\.[^\"\s>]+\.js[^>]*>", html)
    assert len(bundles) == 1 and " defer" in bundles[0]
    assert not re.search(r'src="?/js/(?:reveal|share|search|back-to-top)\.', html)


def test_only_the_main_feed_carries_full_posts(built_site: Path) -> None:
    """``index.xml`` has full content; tag and series feeds list summaries, so the build stays small."""
    assert "content:encoded" in read_html(built_site, "index.xml")
    assert "content:encoded" not in read_html(built_site, "tags/architecture/index.xml")
    assert "content:encoded" not in read_html(built_site, "series/software-architecture/index.xml")


def test_consulting_page_is_reachable_and_books_a_call(built_site: Path, repo_root: Path) -> None:
    """The consulting page lives in the About book, is linked from Home, and ends in the booking link."""
    html = read_html(built_site, "consulting/index.html")
    assert "calendly.com/alex-djalali/30min" in html
    assert re.search(r'href="?/consulting/"?', read_html(built_site, "index.html"))
    assert (repo_root / "static" / "images" / "og" / "pages" / "consulting.png").is_file()


def test_pull_requests_run_the_site_checks(repo_root: Path) -> None:
    """The build-and-test workflow runs on pull requests too, so a PR shows its checks before merge."""
    import yaml

    workflow = yaml.safe_load((repo_root / ".github" / "workflows" / "hugo.yml").read_text(encoding="utf-8"))
    triggers = workflow.get("on") or workflow.get(True)
    assert "pull_request" in triggers


def test_search_results_show_tag_names_not_slugs(built_site: Path) -> None:
    """The search index carries the same tag names the pages show, so results read ``NLP``, not ``nlp``."""
    import json

    entries = json.loads(read_html(built_site, "index.json"))
    tags = {t for e in entries for t in e["tags"]}
    assert {"NLP", "Software Engineering"} <= tags
    assert not [t for t in tags if "-" in t]
