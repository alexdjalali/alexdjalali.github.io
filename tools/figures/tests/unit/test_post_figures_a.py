"""Unit tests for the first four post figures: data invariants and determinism."""

from __future__ import annotations

import re

import pytest

from figures.model import FigureContext
from figures.posts import agile, distributed, patterns, six_months
from figures.svg import B, R, W

pytestmark = pytest.mark.unit

CTX = FigureContext(slug="x", bib=(), locations=(), timeline=())


def test_pattern_parts_sum_to_one_hundred() -> None:
    """The sixteen parts of the post contain exactly one hundred patterns."""
    assert len(patterns.PART_SIZES) == 16
    assert sum(patterns.PART_SIZES) == 100


def test_patterns_figure_has_one_hundred_cells() -> None:
    """The grid draws one popped cell per pattern."""
    svg = patterns.patterns(CTX).svg
    assert len(re.findall(r'class="an-pop"', svg)) == 100


def test_agile_build_bars_are_narrower_than_done_bars() -> None:
    """Each of the three rows draws a blue build bar shorter than its red done bar."""
    svg = agile.agile(CTX).svg
    bars = re.findall(r'class="an-grow" style="[^"]*"><rect[^>]*width="([\d.]+)"[^>]*fill="(#\w+)"', svg)
    assert [c for _, c in bars] == [B, R] * 3
    for (build, _), (done, _) in zip(bars[0::2], bars[1::2], strict=True):
        assert float(build) < float(done)


def test_six_months_states_both_shares() -> None:
    """The two pies are labelled 51% and 32%."""
    svg = six_months.six_months(CTX).svg
    assert ">51%<" in svg
    assert ">32%<" in svg


def test_distributed_has_four_red_and_three_white_nodes() -> None:
    """Four replicas are washed red (the majority); three are outlined white."""
    svg = distributed.distributed(CTX).svg
    red_nodes = [g for g in re.findall(r'<g class="an-bloom".*?</g></g>', svg) if R in g]
    assert len(red_nodes) == 4
    assert len(re.findall(rf'r="4" fill="{W}"', svg)) == 3


@pytest.mark.parametrize(
    "module", [agile.agile, distributed.distributed, patterns.patterns, six_months.six_months]
)
def test_figures_are_deterministic_and_captioned(module) -> None:
    """Two calls give identical output and the caption is non-empty."""
    a, b = module(CTX), module(CTX)
    assert a == b
    assert a.caption.strip()
