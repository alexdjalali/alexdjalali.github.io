"""Shared fixtures: a session-scoped build of the real site with the real ``hugo`` binary."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Return the repository root (the directory holding ``hugo.toml``)."""
    assert (REPO_ROOT / "hugo.toml").exists()
    return REPO_ROOT


@pytest.fixture(scope="session")
def built_site(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Return the built site directory.

    Uses ``$BUILT_SITE_DIR`` when set (CI reuses its own build); otherwise runs
    ``hugo --minify`` into a temp dir and fails the session if hugo is missing or errors.
    """
    preset = os.environ.get("BUILT_SITE_DIR")
    if preset:
        return Path(preset)
    hugo = shutil.which("hugo")
    if hugo is None:
        pytest.fail("hugo is not on PATH; integration tests need the real binary")
    out = tmp_path_factory.mktemp("site")
    proc = subprocess.run(
        [hugo, "--minify", "-d", str(out)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(f"hugo failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    return out
