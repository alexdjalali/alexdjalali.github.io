"""Unit tests for the figure registry and the hash-derived default construction."""

from __future__ import annotations

import pytest

from figures import registry
from figures.default import default_construction
from figures.model import Figure, FigureContext
from figures.registry import DuplicateFigureError, figure_for, register, registered

pytestmark = pytest.mark.unit


def ctx(slug: str) -> FigureContext:
    """Return an empty context for ``slug``."""
    return FigureContext(slug=slug, bib=(), locations=(), timeline=())


@pytest.fixture(autouse=True)
def _isolated_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give each test an empty registry."""
    monkeypatch.setattr(registry, "_REGISTRY", {})


def test_unknown_slug_gets_a_deterministic_default() -> None:
    """An unregistered slug renders the same figure every time."""
    a = figure_for("some-new-post")(ctx("some-new-post"))
    b = figure_for("some-new-post")(ctx("some-new-post"))
    assert a == b
    assert a.svg.startswith('<svg class="fig"')


def test_defaults_differ_between_slugs() -> None:
    """Two different slugs do not share a default figure."""
    a = default_construction("alpha")(ctx("alpha"))
    b = default_construction("beta")(ctx("beta"))
    assert a.svg != b.svg


def test_default_caption_names_the_slug() -> None:
    """The default caption is non-empty and names its slug."""
    fig = default_construction("alpha")(ctx("alpha"))
    assert fig.caption == "Construction for alpha"


def test_registered_slug_returns_its_builder() -> None:
    """A registered builder is returned and listed."""

    @register("my-post")
    def build(c: FigureContext) -> Figure:
        return Figure(svg="<svg/>", caption="mine")

    assert figure_for("my-post") is build
    assert registered() == {"my-post": build}


def test_duplicate_registration_raises() -> None:
    """Registering a slug twice fails loudly."""

    @register("dup")
    def one(c: FigureContext) -> Figure:
        return Figure(svg="<svg/>", caption="one")

    with pytest.raises(DuplicateFigureError, match="dup"):

        @register("dup")
        def two(c: FigureContext) -> Figure:
            return Figure(svg="<svg/>", caption="two")
