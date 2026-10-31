"""Parse the BibTeX files in ``static/bib`` into ``BibEntry`` values and summarise them."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

from figures.model import BibEntry, BibKind

_HEAD = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,")
_FIELD = re.compile(r"(\w+)\s*=\s*")
_BARE_END = re.compile(r"[,}\n]")
_VENUE_FIELDS = ("journal", "booktitle", "school", "note", "publisher")


def _value(text: str, pos: int) -> tuple[str, int]:
    """Read a ``{...}`` (nested braces) or ``"..."`` value starting at ``pos``."""
    if text[pos] == "{":
        depth, i = 0, pos
        while i < len(text):
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
            if depth == 0:
                break
        return text[pos + 1 : i - 1], i
    end = text.index('"', pos + 1)
    return text[pos + 1 : end], end + 1


def _fields(body: str) -> dict[str, str]:
    """Return the lower-cased fields of one entry body, braces and whitespace stripped."""
    out: dict[str, str] = {}
    pos = 0
    while m := _FIELD.search(body, pos):
        start = m.end()
        if start >= len(body):
            break
        if body[start] in '{"':
            raw, pos = _value(body, start)
        else:
            end = _BARE_END.search(body, start)
            pos = end.start() if end else len(body)
            raw = body[start:pos]
        out[m.group(1).lower()] = " ".join(raw.replace("{", "").replace("}", "").split())
    return out


def _year(path: Path, raw: str) -> int:
    """Parse a ``year`` field, naming the file when it is not an integer."""
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{path.name}: year is not an integer: {raw!r}") from None


def _kind(key: str) -> BibKind:
    if "patent" in key:
        return "patent"
    if "dissertation" in key:
        return "dissertation"
    return "paper"


def load_entries(bib_dir: Path) -> list[BibEntry]:
    """Return one entry per ``*.bib`` file in ``bib_dir``, ordered by year then key."""
    entries: list[BibEntry] = []
    for path in sorted(bib_dir.glob("*.bib")):
        text = path.read_text(encoding="utf-8")
        head = _HEAD.search(text)
        if head is None:
            raise ValueError(f"{path.name}: no BibTeX entry header")
        fields = _fields(text[head.end() :])
        if "year" not in fields:
            raise ValueError(f"{path.name}: no year field")
        venue = next((fields[f] for f in _VENUE_FIELDS if f in fields), "")
        entries.append(
            BibEntry(
                key=head.group(1),
                year=_year(path, fields["year"]),
                title=fields.get("title", ""),
                venue=venue,
                authors=fields.get("author", ""),
                kind=_kind(path.stem),
            )
        )
    return sorted(entries, key=lambda e: (e.year, e.key))


def output_by_year(entries: list[BibEntry] | tuple[BibEntry, ...]) -> dict[tuple[int, str], int]:
    """Return how many entries of each kind were published in each year."""
    return dict(Counter((e.year, e.kind) for e in entries))


def research_summary(entries: list[BibEntry] | tuple[BibEntry, ...]) -> dict[str, Any]:
    """Return the totals Hugo reads from ``data/figures/research.json``."""
    kinds = Counter(e.kind for e in entries)
    by_year: dict[str, dict[str, int]] = {}
    for (year, kind), n in sorted(output_by_year(entries).items()):
        by_year.setdefault(str(year), {})[kind] = n
    return {
        "papers": kinds["paper"],
        "patents": kinds["patent"],
        "dissertation": kinds["dissertation"],
        "total": len(entries),
        "by_year": by_year,
    }
