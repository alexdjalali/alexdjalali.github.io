"""Committed figure partials and data must equal a fresh render of the repo's sources."""

from __future__ import annotations

from pathlib import Path

import pytest

from figures import build

pytestmark = pytest.mark.integration


def test_generated_files_have_no_drift(repo_root: Path) -> None:
    """No generated partial is missing, hand-edited or stale; run ``uv run figures generate`` to fix."""
    assert build.drift(repo_root) == []
