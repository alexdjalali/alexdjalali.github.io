"""Unit tests for the remaining post figures: data invariants and determinism."""

from __future__ import annotations

import re

import pytest

from figures.model import FigureContext
from figures.posts import (
    anatomy,
    bomb,
    corpus,
    course,
    decorators,
    devenv,
    layers,
    montague,
    one_row,
    qud,
    query_core,
    worktrees,
)
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


def test_query_core_folds_one_tree_into_every_target() -> None:
    """One filter tree (three leaf clauses) folds into each labelled target: SQL, CQL and a chart."""
    svg = query_core.query_core(CTX).svg
    assert query_core.TARGETS == ("SQL", "CQL", "chart")
    for target in query_core.TARGETS:
        assert f">{target}<" in svg
    for leaf in query_core.LEAVES:
        assert leaf in svg
    assert len(query_core.LEAVES) == 3


def test_bomb_doubles_each_level() -> None:
    """1 + 2 + 4 + 8 + 16 nodes in the five-level tree."""
    svg = bomb.bomb(CTX).svg
    assert len(re.findall(r'class="an-pop"', svg)) == 31


def test_corpus_wires_one_bundle_to_three_readers() -> None:
    """One sheet stack connects to exactly three named readers: people, wiki and index."""
    svg = corpus.corpus(CTX).svg
    assert len(re.findall(r'class="an-draw"[^>]*></line>', svg)) == 3
    for reader in ("people", "wiki", "index"):
        assert f">{reader}<" in svg


def test_one_row_feeds_every_derived_artifact() -> None:
    """One descriptor row is the only authored fact; one drawn line reaches each derived artifact."""
    svg = one_row.one_row(CTX).svg
    assert len(one_row.DERIVED) == 4
    assert len(re.findall(r'class="an-draw"[^>]*></path>', svg)) == len(one_row.DERIVED)
    for label in one_row.DERIVED:
        assert f">{label}<" in svg
    assert ">one row<" in svg


def test_worktrees_cut_every_lane_from_one_base_and_pick_one_commit_each() -> None:
    """Every lane starts at the shared base commit and lands exactly one commit on integration."""
    assert len({lane.start for lane in worktrees.LANES}) == 1
    svg = worktrees.worktrees(CTX).svg
    assert len(re.findall(r'class="an-draw"[^>]*></path>', svg)) == len(worktrees.LANES)
    commit_squares = re.findall(r'<rect[^>]*width="4.00" height="4.00"', svg)
    assert len(commit_squares) == 2 * len(worktrees.LANES)  # a wash draws halo + body
    assert ">integration<" in svg


def test_qud_stack_is_the_path_from_root_to_the_open_node() -> None:
    """The stack beside the d-tree lists the root-to-focus path, with the clarification on top."""
    assert qud.STACK == (qud.CLARIFICATION, *reversed(qud.PATH))
    svg = qud.qud(CTX).svg
    for label in qud.STACK:
        assert f">{label}<" in svg
    assert len(re.findall(r"<circle", svg)) >= len(qud.NODES)


@pytest.mark.parametrize(
    "builder",
    [
        anatomy.anatomy,
        bomb.bomb,
        corpus.corpus,
        course.course,
        decorators.decorators,
        devenv.devenv,
        layers.layers,
        montague.montague,
        one_row.one_row,
        qud.qud,
        query_core.query_core,
        worktrees.worktrees,
    ],
)
def test_figures_are_deterministic_and_captioned(builder) -> None:
    """Two calls give identical output and the caption is non-empty."""
    a, b = builder(CTX), builder(CTX)
    assert a == b
    assert a.caption.strip()
    assert a.svg.startswith('<svg class="fig"')
