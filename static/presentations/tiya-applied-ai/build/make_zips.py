"""Zip each day's exercise files, and each day's whole kit, from the file lists in make_pages.py.

Writes downloads/tiya-ai-materials-<day>.zip (participants) and downloads/tiya-ai-kit-<day>.zip
(instructors: that day's pages, slides, PDFs, and files, plus the facilitator guide).
"""

import pathlib
import zipfile

from agenda_data import DAYS
from make_pages import KIT

KIT_ROOT = pathlib.Path(__file__).parent.parent
SHARED = ["facilitator-guide.html", "downloads/facilitator-guide.pdf"]
"""The only files that cover every day; each day's kit carries them."""


def day_files(key: str) -> list[str]:
    """Every kit file that belongs to one day."""
    k = KIT[key]
    files = [
        f"{key}-slides.html",
        f"downloads/{key}-slides.pdf",
        f"downloads/{key}-slides.pptx",
        f"agenda-{key}.html",
        f"downloads/agenda-{key}.pdf",
        f"participant-workbook-{key}.html",
        f"downloads/participant-workbook-{key}.pdf",
        f"assessment-kit-{key}.html",
        f"downloads/assessment-kit-{key}.pdf",
        f"participants-{key}.html",
        *[p for _, _, page, pdf in k.extra_docs for p in (page, pdf)],
        *([f"{key}-sops.html"] if k.sops_page else []),
        *[f.path for f in k.files],
        *SHARED,
    ]
    return files


def write_zip(name: str, paths: list[str]) -> None:
    """Zip the given kit-relative paths; fail loudly if one is missing."""
    missing = [p for p in paths if not (KIT_ROOT / p).exists()]
    if missing:
        raise SystemExit(f"{name}: missing {', '.join(missing)}")
    out = KIT_ROOT / "downloads" / name
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(KIT_ROOT / p, p)
    print(f"downloads/{name}  {out.stat().st_size // 1024} KB")


def main() -> None:
    """Write both zips for every day."""
    for key in DAYS:
        write_zip(f"tiya-ai-materials-{key}.zip", [f.path for f in KIT[key].files])
        write_zip(f"tiya-ai-kit-{key}.zip", day_files(key))


if __name__ == "__main__":
    main()
