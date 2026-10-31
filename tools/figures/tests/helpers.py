"""Small helpers shared by the integration tests."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


def read_html(site: Path, rel: str) -> str:
    """Return the text of ``rel`` inside the built site."""
    return (site / rel).read_text(encoding="utf-8")


class _NavLinks(HTMLParser):
    """Collect the link texts inside every ``<nav aria-label=...>``, keyed by label."""

    def __init__(self) -> None:
        super().__init__()
        self.navs: dict[str, list[str]] = {}
        self._label: str | None = None
        self._in_a = False
        self._buf = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag == "nav" and a.get("aria-label"):
            self._label = a["aria-label"]
            self.navs.setdefault(self._label or "", [])
        elif tag == "a" and self._label is not None:
            self._in_a, self._buf = True, ""

    def handle_data(self, data: str) -> None:
        if self._in_a:
            self._buf += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._in_a and self._label is not None:
            text = " ".join(self._buf.split())
            if text:
                self.navs[self._label].append(text)
            self._in_a = False
        elif tag == "nav":
            self._label = None


def nav_links(html: str) -> dict[str, list[str]]:
    """Return ``{aria-label: [link text, ...]}`` for every labelled ``<nav>`` in ``html``."""
    parser = _NavLinks()
    parser.feed(html)
    return parser.navs
