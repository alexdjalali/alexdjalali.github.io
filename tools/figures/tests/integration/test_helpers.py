"""Template helpers (rise, numeral, construction), run through a probe page in a scratch site copy."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROBE_LAYOUT = """{{ define "content" }}
<ol id="numerals">
{{- range where site.RegularPages "Section" "posts" -}}
<li data-slug="{{ .File.ContentBaseName }}">{{ partial "numeral.html" . }}</li>
{{- end -}}
</ol>
<p id="rise">{{ partial "rise.html" "Hello brave new world" }}</p>
<div id="shortcode">{{ .Content }}</div>
{{ end }}
"""
PROBE_PAGE = '---\ntitle: Probe\ntype: probe\n---\n{{< construction "projects/perceptivepanda" >}}\n'
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def _roman_to_int(s: str) -> int:
    total = 0
    for a, b in zip(s, [*s[1:], ""], strict=True):
        total += -ROMAN[a] if b and ROMAN[a] < ROMAN[b] else ROMAN[a]
    return total


@pytest.fixture(scope="module")
def probe(repo_root: Path, tmp_path_factory: pytest.TempPathFactory) -> str:
    """Build a scratch copy of the site with a probe page and return that page's HTML."""
    work = tmp_path_factory.mktemp("probe")
    for name in ("layouts", "assets", "data", "i18n"):
        shutil.copytree(repo_root / name, work / name)
    config = (repo_root / "hugo.toml").read_text().replace("enableGitInfo = true", "enableGitInfo = false")
    (work / "hugo.toml").write_text(config)  # the scratch copy is not a git repository
    shutil.copytree(repo_root / "content" / "posts", work / "content" / "posts")
    (work / "content" / "probe.md").write_text(PROBE_PAGE)
    (work / "layouts" / "probe").mkdir()
    (work / "layouts" / "probe" / "single.html").write_text(PROBE_LAYOUT)
    out = work / "public"
    hugo = shutil.which("hugo")
    assert hugo, "hugo is required"
    proc = subprocess.run(
        [hugo, "-s", str(work), "-d", str(out)], capture_output=True, text=True, check=False
    )
    assert proc.returncode == 0, proc.stderr
    return (out / "probe" / "index.html").read_text()


def test_numerals_are_distinct_and_form_one_to_n(probe: str, repo_root: Path) -> None:
    """Post numerals are 1..N with no repeats, where N is the number of posts."""
    n = len(list((repo_root / "content" / "posts").glob("*.md")))
    pairs = re.findall(r'<li data-slug="([^"]+)">([IVXLCDM]+)</li>', probe)
    assert len(pairs) == n
    assert sorted(_roman_to_int(r) for _, r in pairs) == list(range(1, n + 1))


def test_posts_sharing_a_date_get_consecutive_numerals(probe: str) -> None:
    """The two posts dated 2026-02-22 are ranked next to each other."""
    ranks = {s: _roman_to_int(r) for s, r in re.findall(r'<li data-slug="([^"]+)">([IVXLCDM]+)</li>', probe)}
    a = ranks["decorator-pattern-observability-resilience"]
    b = ranks["how-i-learned-to-love-the-bomb"]
    assert abs(a - b) == 1


def test_rise_wraps_each_word_with_increasing_delay(probe: str) -> None:
    """Each word is its own ``.rise`` span; delays are 0.15s + 0.06s per word."""
    delays = re.findall(r'<span class="?rise"? style="?animation-delay: ([0-9.]+)s"?>', probe)
    assert delays == ["0.15", "0.21", "0.27", "0.33"]


def test_construction_shortcode_renders_the_figure_once(probe: str) -> None:
    """The shortcode outputs one generated figure with no extra wrapper."""
    block = re.search(r'<div id="?shortcode"?>(.*?)</div>', probe, re.DOTALL)
    assert block
    assert block.group(1).count("<svg") == 1
    assert block.group(1).count("fig-frame") == 1
