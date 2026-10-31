"""The CSP admits every third-party stylesheet and font the site loads; robots.txt stays standard."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration

MATH_POST = "posts/dependency-to-lambda/index.html"


def _directive(html: str, name: str) -> set[str]:
    """Return the sources of CSP directive ``name`` from the page's meta policy."""
    policy = re.search(r'http-equiv="?Content-Security-Policy"? content="([^"]+)"', html)
    assert policy
    found = re.search(rf"(?:^|;)\s*{name}\s+([^;]+)", policy.group(1))
    return set(found.group(1).split()) if found else set()


def test_every_external_stylesheet_is_allowed(built_site: Path) -> None:
    """KaTeX's stylesheet (posts with math) and giscus's injected theme pass ``style-src``."""
    html = read_html(built_site, MATH_POST)
    hrefs = re.findall(r'<link rel="?stylesheet"? href="?(https://[^" >]+)', html)
    assert hrefs, "the math post should link KaTeX's stylesheet"
    allowed = _directive(html, "style-src")
    origins = {f"https://{urlparse(h).netloc}" for h in hrefs} | {"https://giscus.app"}
    assert origins <= allowed, origins - allowed


def test_katex_fonts_are_allowed(built_site: Path) -> None:
    """KaTeX loads its fonts from the same CDN as its stylesheet."""
    assert "https://cdn.jsdelivr.net" in _directive(read_html(built_site, MATH_POST), "font-src")


def test_robots_txt_uses_only_standard_directives(built_site: Path) -> None:
    """Every non-comment line of robots.txt is a directive crawlers (and Lighthouse) understand."""
    known = {"user-agent", "allow", "disallow", "sitemap", "crawl-delay"}
    lines = [ln.strip() for ln in read_html(built_site, "robots.txt").splitlines()]
    fields = [ln.split(":", 1)[0].lower() for ln in lines if ln and not ln.startswith("#")]
    assert fields and set(fields) <= known, set(fields) - known
