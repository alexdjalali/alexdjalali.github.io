"""Slug-keyed registry of figure builders, with a deterministic default for unknown slugs."""

from __future__ import annotations

from collections.abc import Callable

from figures.default import default_construction
from figures.model import Figure, FigureContext

FigureBuilder = Callable[[FigureContext], Figure]

_REGISTRY: dict[str, FigureBuilder] = {}


class DuplicateFigureError(ValueError):
    """Raised when a slug is registered twice."""


def register(slug: str) -> Callable[[FigureBuilder], FigureBuilder]:
    """Return a decorator that registers a builder for ``slug``."""

    def deco(builder: FigureBuilder) -> FigureBuilder:
        if slug in _REGISTRY:
            raise DuplicateFigureError(f"figure already registered for {slug!r}")
        _REGISTRY[slug] = builder
        return builder

    return deco


def registered() -> dict[str, FigureBuilder]:
    """Return a copy of the registry."""
    return dict(_REGISTRY)


def figure_for(slug: str) -> FigureBuilder:
    """Return the builder registered for ``slug``, else the slug's default construction."""
    return _REGISTRY.get(slug) or default_construction(slug)
