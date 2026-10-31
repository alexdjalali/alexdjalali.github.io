"""Unit tests for the remaining post figures: data invariants and determinism."""

from __future__ import annotations

import re

import pytest

from figures.model import FigureContext
from figures.posts import anatomy, bomb, course, decorators, devenv, layers, montague
from figures.svg import K

pytestmark = pytest.mark.unit

CTX = FigureContext(slug="x", bib=(), locations=(), timeline=())


def test_anatomy_has_seven_template_squares_and_seventeen_command_dots() -> None:
    """The figure encodes the post's counts: 7 templates, 17 commands."""
    svg = anatomy.anatomy(CTX).svg
    assert len(re.findall(r'<rect[^>]*transform="rotate', svg)) == 7
    assert len(re.findall(rf'r="1.80" fill="{K}"', svg)) == 17


def test_layers_has_nine_layers_and_eight_arrows() -> None:
    """Nine named layers joined by eight downward arrows."""
    assert len(layers.LAYERS) == 9
    svg = layers.layers(CTX).svg
    assert len(re.findall(r"<polygon[^>]*an-fade", svg)) == 8
    for name in layers.LAYERS:
        assert name in svg


def test_montague_draws_every_word_of_the_sentence() -> None:
    """Each word of the example sentence appears as a label."""
    svg = montague.montague(CTX).svg
    for word in montague.SENTENCE.lower().split():
        assert word in svg.lower()


def test_decorators_draws_the_four_rings() -> None:
    """Recovery, Auth, Transaction and Observability are all labelled."""
    svg = decorators.decorators(CTX).svg
    for name in ("Recovery", "Auth", "Transaction", "Observability"):
        assert name in svg


def test_bomb_doubles_each_level() -> None:
    """1 + 2 + 4 + 8 + 16 nodes in the five-level tree."""
    svg = bomb.bomb(CTX).svg
    assert len(re.findall(r'class="an-pop"', svg)) == 31


@pytest.mark.parametrize(
    "builder",
    [
        anatomy.anatomy,
        bomb.bomb,
        course.course,
        decorators.decorators,
        devenv.devenv,
        layers.layers,
        montague.montague,
    ],
)
def test_figures_are_deterministic_and_captioned(builder) -> None:
    """Two calls give identical output and the caption is non-empty."""
    a, b = builder(CTX), builder(CTX)
    assert a == b
    assert a.caption.strip()
    assert a.svg.startswith('<svg class="fig"')
