"""Courses and Talks carry schema.org Course and Event markup, read from ``data/schema/<page>.json``."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration


def _ld(html: str) -> list[dict[str, Any]]:
    """Return every JSON-LD object on the page."""
    blocks = re.findall(r'<script type="?application/ld\+json"?>(.*?)</script>', html, re.DOTALL)
    return [json.loads(b) for b in blocks]


@pytest.mark.parametrize(("page", "kind"), [("courses", "Course"), ("presentations", "Event")])
def test_page_emits_its_schema_objects(built_site: Path, repo_root: Path, page: str, kind: str) -> None:
    """Each object in the page's schema data file is emitted once, typed and with the schema.org context."""
    expected = json.loads((repo_root / "data" / "schema" / f"{page}.json").read_text(encoding="utf-8"))
    found = [o for o in _ld(read_html(built_site, f"{page}/index.html")) if o.get("@type") == kind]
    assert expected and [o["name"] for o in found] == [o["name"] for o in expected]
    assert all(o["@context"] == "https://schema.org" for o in found)
    assert all(o["url"].endswith(f"/{page}/") for o in found)
