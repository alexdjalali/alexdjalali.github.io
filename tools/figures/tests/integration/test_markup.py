"""Built pages are well-formed: no tag repeats an attribute, and the footer keeps its link relations."""

from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


class _Attrs(HTMLParser):
    """Record every start tag that repeats an attribute, and each ``<a>``'s ``rel`` tokens."""

    def __init__(self) -> None:
        super().__init__()
        self.duplicates: list[str] = []
        self.rels: dict[str, list[str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        repeated = [k for k, n in Counter(k for k, _ in attrs).items() if n > 1]
        if repeated:
            self.duplicates.append(f"<{tag}> repeats {repeated}")
        if tag == "a":
            a = dict(attrs)
            self.rels.setdefault(a.get("href") or "", []).append(a.get("rel") or "")


def _parse(html: str) -> _Attrs:
    parser = _Attrs()
    parser.feed(html)
    return parser


def test_no_page_repeats_an_attribute(built_site: Path) -> None:
    """Duplicate attributes are invalid HTML and silently drop the later value."""
    bad = {
        str(p.relative_to(built_site)): parsed.duplicates
        for p in sorted(built_site.rglob("index.html"))
        if (parsed := _parse(p.read_text(encoding="utf-8"))).duplicates
    }
    assert bad == {}


def test_footer_rss_link_keeps_rel_alternate(built_site: Path) -> None:
    """The RSS footer link carries ``alternate`` alongside the external-link ``noopener noreferrer``."""
    rels = _parse(read_html(built_site, "index.html")).rels
    rss = [rel for href, found in rels.items() if href.endswith("index.xml") for rel in found]
    assert rss and all({"alternate", "noopener", "noreferrer"} <= set(r.split()) for r in rss)
