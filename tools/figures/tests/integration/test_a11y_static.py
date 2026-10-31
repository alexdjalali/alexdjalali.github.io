"""Static accessibility baseline over every built page."""

from __future__ import annotations

import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import pytest

from tests.helpers import site_stylesheet

pytestmark = pytest.mark.integration

ICON_ONLY = re.compile(r"^\s*$")
YELLOW_TEXT = re.compile(r"(?<![-\w])color\s*:\s*var\(--yellow\)")


class _Audit(HTMLParser):
    """Record landmarks, headings, images, icon-only links and figure labelling for one page."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: Counter[str] = Counter()
        self.skip_link = False
        self.imgs_without_alt = 0
        self.unlabeled_links: list[str] = []
        self.figs: list[dict[str, str | None]] = []
        self.ids: dict[str, str] = {}
        self._link: dict[str, str | None] | None = None
        self._link_text = ""
        self._link_has_img = False
        self._cap_id: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        self.tags[tag] += 1
        if tag == "a":
            self._link, self._link_text, self._link_has_img = a, "", False
            if (a.get("href") or "").startswith("#main") and "skip" in (a.get("class") or ""):
                self.skip_link = True
        elif tag == "img":
            if "alt" not in a:
                self.imgs_without_alt += 1
            if self._link is not None:
                self._link_has_img = bool(a.get("alt"))
        elif tag == "svg" and "fig" in (a.get("class") or "").split():
            self.figs.append(a)
        ident = a.get("id")
        if ident:
            self._cap_id = ident if tag == "figcaption" else None
            self.ids[ident] = ""

    def handle_data(self, data: str) -> None:
        if self._link is not None:
            self._link_text += data
        if self._cap_id:
            self.ids[self._cap_id] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "figcaption":
            self._cap_id = None
        if tag == "a" and self._link is not None:
            labelled = self._link.get("aria-label") or self._link.get("title")
            if ICON_ONLY.match(self._link_text) and not self._link_has_img and not labelled:
                self.unlabeled_links.append(self._link.get("href") or "")
            self._link = None


def _pages(site: Path, static: Path) -> list[Path]:
    """Return every theme-built page: a titled document that is not a verbatim copy from ``static/``."""
    pages = []
    for p in sorted(site.rglob("*.html")):
        if (static / p.relative_to(site)).exists():
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "<title" in text and "http-equiv=refresh" not in text.replace('"', "") and "<body" in text:
            pages.append(p)
    return pages


@pytest.fixture(scope="module")
def audits(built_site: Path, repo_root: Path) -> dict[str, _Audit]:
    """Parse every built page once."""
    out: dict[str, _Audit] = {}
    for page in _pages(built_site, repo_root / "static"):
        audit = _Audit()
        audit.feed(page.read_text(encoding="utf-8"))
        out[str(page.relative_to(built_site))] = audit
    assert len(out) > 20
    return out


def test_every_page_has_one_h1_a_main_landmark_and_a_skip_link(audits: dict[str, _Audit]) -> None:
    """Each document has exactly one ``<h1>``, a ``<main>``, and a working skip link."""
    bad = {
        name: (a.tags["h1"], a.tags["main"], a.skip_link)
        for name, a in audits.items()
        if a.tags["h1"] != 1 or a.tags["main"] != 1 or not a.skip_link
    }
    assert bad == {}


def test_images_have_alt_and_icon_only_links_have_labels(audits: dict[str, _Audit]) -> None:
    """No ``<img>`` lacks ``alt`` and no text-less link lacks an accessible name."""
    no_alt = {n: a.imgs_without_alt for n, a in audits.items() if a.imgs_without_alt}
    unlabeled = {n: a.unlabeled_links for n, a in audits.items() if a.unlabeled_links}
    assert (no_alt, unlabeled) == ({}, {})


def test_every_figure_is_labelled_by_a_captioned_figcaption(audits: dict[str, _Audit]) -> None:
    """Each ``svg.fig`` has ``role=img`` and an ``aria-labelledby`` resolving to a non-empty figcaption."""
    bad: list[str] = []
    for name, a in audits.items():
        for fig in a.figs:
            target = fig.get("aria-labelledby") or ""
            if fig.get("role") != "img" or not a.ids.get(target, "").strip():
                bad.append(f"{name}: {target or 'missing aria-labelledby'}")
    assert bad == []
    assert sum(len(a.figs) for a in audits.values()) > 20


def test_yellow_is_never_text_colour_on_white(built_site: Path) -> None:
    """Yellow fails contrast on white: ``color`` may use it only in code blocks and their dark headers."""
    css = site_stylesheet(built_site)
    offenders = []
    for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if YELLOW_TEXT.search(body) and not re.search(r"\bpre\b|\.chroma|\.code-", selector):
            offenders.append(selector.strip()[:80])
    assert offenders == []
