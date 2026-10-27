"""Assemble the course-kit HTML pages from fragments, the shared stylesheet, and the inline GT logo."""

import pathlib
import re

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    "family=Roboto+Slab:wght@500;600;700&family=Roboto:wght@400;500;700&"
    'family=Roboto+Mono:wght@500&display=swap">\n'
)
PAGES = [
    "facilitator-guide",
    "index",
    "participants",
    "participants-day1",
    "participants-day2",
    "participants-day3",
    "participant-workbook-day1",
    "participant-workbook-day2",
    "participant-workbook-day3",
    "assessment-kit-day1",
    "assessment-kit-day2",
    "assessment-kit-day3",
    "day2-sops",
    "day3-sops",
    "day2-outline",
    "day3-outline",
]


def size(path: pathlib.Path) -> str:
    """Return a human-readable file size, or a dash if the file isn't built yet."""
    if not path.exists():
        return "–"
    n = path.stat().st_size
    return (
        f"{n / 1_048_576:.1f} MB" if n >= 1_048_576 else f"{max(1, round(n / 1024))} KB"
    )


def build(name: str, css: str, logo: str) -> None:
    """Write OUT/<name>.html from build/<name>.html with includes, CSS, and logo injected."""
    frag = (HERE / f"{name}.html").read_text()
    frag = re.sub(
        r"\{\{INCLUDE:([^}]+)\}\}", lambda m: (HERE / m.group(1)).read_text(), frag
    )
    title, body = frag.split("\n", 1)
    html = (
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f"{title}\n{FONTS}<style>\n{css}</style>\n{body.replace('{{LOGO}}', logo)}"
    )
    html = re.sub(r"\{\{SIZE:([^}]+)\}\}", lambda m: size(OUT / m.group(1)), html)
    _ = (OUT / f"{name}.html").write_text(html)
    print(f"{name}.html  {len(html) // 1024} KB")


def main() -> None:
    """Build every page whose fragment exists."""
    css = (HERE / "base.css").read_text()
    logo = (HERE / "logo.svg").read_text().strip()
    for name in PAGES:
        if (HERE / f"{name}.html").exists():
            build(name, css, logo)


if __name__ == "__main__":
    main()
