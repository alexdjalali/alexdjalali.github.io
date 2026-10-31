"""Unit tests for the SVG primitives: determinism, shared-filter references, and timing."""

from __future__ import annotations

import re

import pytest

from figures.svg import PALETTE, Fig, circ, rect, registration, tri

pytestmark = pytest.mark.unit


def _build() -> str:
    f = Fig()
    f.line((0, 0), (10, 10)).dashed((0, 5), (9, 5)).ring(50, 50, 10).path("M0 0 L5 5")
    f.wash(circ(50, 50, 5, PALETTE["red"])).pop(rect(1, 1, 4, 4, PALETTE["blue"]))
    f.grow(rect(0, 0, 3, 3, PALETTE["black"])).text(5, 5, "x").raw("<g/>")
    return f.svg()


def test_same_call_sequence_yields_identical_output() -> None:
    """Two identical builds are byte-identical."""
    assert _build() == _build()


def test_svg_has_no_defs_and_only_shared_filters() -> None:
    """Filters are defined once in the page shell; figures only reference ``wc`` and ``bleed``."""
    out = _build()
    assert "<defs" not in out
    refs = set(re.findall(r'filter="url\(#([^)]+)\)"', out))
    assert refs == {"wc", "bleed"}
    assert out.startswith('<svg class="fig" viewBox=')


def test_registration_marks_are_aria_hidden() -> None:
    """The drafting marks are decoration, hidden from assistive technology."""
    assert '<g aria-hidden="true">' in _build()
    assert registration().count("an-spin") == 4


def test_marks_can_be_omitted() -> None:
    """``marks=False`` drops the registration group."""
    assert "an-spin" not in Fig().line((0, 0), (1, 1)).svg(marks=False)


@pytest.mark.parametrize(
    ("shape", "tag"),
    [
        (rect(0, 0, 1, 1, "#111111"), "<rect"),
        (circ(1, 1, 1, "#111111"), "<circle"),
        (tri(1, 1, 1, "#111111"), "<polygon"),
    ],
)
def test_helpers_emit_expected_element(shape: str, tag: str) -> None:
    """Each helper returns its SVG element."""
    assert shape.startswith(tag)


def test_delays_increase_with_tick() -> None:
    """Animation delays never decrease along the build sequence."""
    f = Fig(0.5)
    f.line((0, 0), (1, 1)).tick(0.3).line((0, 0), (2, 2)).pop(circ(1, 1, 1, "#111111"))
    delays = [float(d) for d in re.findall(r"animation-delay: ([0-9.]+)s", f.svg())]
    assert delays == sorted(delays)
    assert delays[0] == 0.5
    assert len(set(delays)) == len(delays)


def test_animation_classes_are_used() -> None:
    """Parts carry the documented animation classes."""
    out = _build()
    for cls in ("an-draw", "an-bloom", "an-pop", "an-grow", "an-fade"):
        assert cls in out
