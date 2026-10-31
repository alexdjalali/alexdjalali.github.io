"""``figures generate`` and ``figures check``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def find_root(start: Path) -> Path:
    """Walk up from ``start`` to the directory that holds ``hugo.toml``."""
    for candidate in [start, *start.parents]:
        if (candidate / "hugo.toml").exists():
            return candidate
    raise FileNotFoundError(f"no hugo.toml found above {start}")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI; ``check`` returns 1 when any generated file has drifted."""
    from figures import build

    parser = argparse.ArgumentParser(
        prog="figures",
        description="Generate the theme's SVG figures, research data, PNG social cards and favicons.",
    )
    parser.add_argument("command", choices=["generate", "check"])
    parser.add_argument("--root", type=Path, default=None, help="repo root (default: nearest hugo.toml)")
    args = parser.parse_args(argv)
    root = (args.root or find_root(Path.cwd())).resolve()
    if args.command == "generate":
        changed = build.write(root)
        print(f"generated: {len(changed)} file(s) changed")
        return 0
    drifted = build.drift(root)
    for path in drifted:
        print(f"drift: {path}", file=sys.stderr)
    return 1 if drifted else 0
