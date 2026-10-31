"""Every class a retained script queries or creates has a rule outside the legacy stylesheet."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

SCRIPTS = [
    "reading-progress",
    "back-to-top",
    "collapsible-code",
    "share",
    "card-deck",
    "search",
    "publication-abstract",
    "topic-filter",
]
# Names that are not site styles: third-party icon classes and the post body container the script reads.
IGNORED = {"fa-solid", "fa-check", "fa-link", "content", "post-content", "bib-link"}
# State and direction hooks the scripts set for tests and assistive tech, with no visual rule of their own.
IGNORED |= {"is-active", "has-multiple", "card-deck-prev", "card-deck-next"}

QUOTED = r"""["']([^"']+)["']"""
SELECTOR_CALLS = re.compile(r"(?:querySelector(?:All)?|closest|matches)\(\s*" + QUOTED)
ID_CALLS = re.compile(r"getElementById\(\s*" + QUOTED)
CLASS_LISTS = re.compile(r"classList\.(?:add|remove|toggle|contains)\(([^)]*)\)")
CLASS_ASSIGN = re.compile(r"className\s*\+?=\s*" + QUOTED)
HTML_CLASS = re.compile(r"""class=\\?["']([^"'\\]+)""")
HTML_ID = re.compile(r"""\sid=\\?["']([^"'\\]+)""")


def _names(source: str) -> tuple[set[str], set[str]]:
    """Return the (classes, ids) a script queries, adds or writes into markup."""
    source = re.sub(r"//.*", "", source)
    classes: set[str] = set()
    ids: set[str] = set()
    for sel in SELECTOR_CALLS.findall(source):
        classes.update(re.findall(r"\.([A-Za-z_][\w-]*)", sel))
        ids.update(re.findall(r"#([A-Za-z_][\w-]*)", sel))
    ids.update(ID_CALLS.findall(source))
    for args in CLASS_LISTS.findall(source):
        classes.update(re.findall(QUOTED, args))
    for value in CLASS_ASSIGN.findall(source) + HTML_CLASS.findall(source):
        classes.update(value.split())
    ids.update(HTML_ID.findall(source))
    classes = {c for c in classes if re.fullmatch(r"[A-Za-z_][\w-]*", c) and not c.startswith("language-")}
    return classes - IGNORED, ids


@pytest.mark.parametrize("script", SCRIPTS)
def test_script_selectors_have_rules(repo_root: Path, script: str) -> None:
    """Each class the script uses appears in a stylesheet other than ``custom.css``."""
    path = repo_root / "assets" / "js" / f"{script}.js"
    if not path.exists():
        pytest.skip(f"{script}.js is added by a later task")
    css = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (repo_root / "assets" / "css").rglob("*.css")
        if p.name != "custom.css"
    )
    classes, _ids = _names(path.read_text(encoding="utf-8"))
    missing = sorted(f".{c}" for c in classes if not re.search(rf"\.{re.escape(c)}(?![\w-])", css))
    assert missing == [], f"{script}.js uses selectors with no non-legacy rule"
