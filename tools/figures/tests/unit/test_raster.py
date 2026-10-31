"""Unit tests for the raster outputs: social cards, favicons and the icon container."""

from __future__ import annotations

import re
import struct
from collections.abc import Iterator
from pathlib import Path

import pytest

from figures.build import ICONS
from figures.raster import (
    FONT_DIR,
    OG_SIZE,
    Raster,
    card_svg,
    flatten,
    ico,
    mark_svg,
    png,
    read_stamp,
    renderer_fingerprint,
    stamp,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def fresh_fingerprint() -> Iterator[None]:
    """Clear the cached renderer fingerprint before and after, so a patched one never leaks."""
    renderer_fingerprint.cache_clear()
    yield
    renderer_fingerprint.cache_clear()


def _png_size(data: bytes) -> tuple[int, int]:
    """Return the width and height stored in a PNG's IHDR chunk."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


_TITLE_LINE = re.compile(
    r'<text x="72" y="[\d.]+" font-size="([\d.]+)" font-family="IBM Plex Sans"[^>]*>([^<]*)</text>'
)


def test_title_too_long_at_every_size_is_cut_after_four_lines() -> None:
    """Past the smallest size a title keeps four word-wrapped lines and the last ends in an ellipsis."""
    title = " ".join(f"word{i}" for i in range(40))
    svg = card_svg("K", title, '<svg class="fig" viewBox="0 0 1 1"></svg>', "n", "u")
    lines = [text for _, text in _TITLE_LINE.findall(svg)]
    words = " ".join(lines).removesuffix("…").split()
    assert len(lines) == 4 and lines[-1].endswith("…")
    assert words == title.split()[: len(words)]
    assert {size for size, _ in _TITLE_LINE.findall(svg)} == {"42"}


def test_card_renders_at_social_card_size() -> None:
    """A card with a figure and a title renders as a 1200x630 PNG."""
    fig = '<svg class="fig" viewBox="0 0 100 100" style="aspect-ratio: 1"><circle cx="50" cy="50" r="30"/>'
    fig += "</svg>"
    svg = card_svg("Book I · Writing", "A title & more", fig, "a.j.djalali", "example.org")
    assert "A title &amp; more" in svg and "EXAMPLE.ORG" in svg
    assert _png_size(png(svg, *OG_SIZE)) == OG_SIZE


def test_mark_and_icon_container() -> None:
    """The mark renders at each icon size, and ``ico`` packs PNGs behind a valid ICO directory."""
    pngs = [png(mark_svg(), s, s) for s in ICONS]
    assert [_png_size(p) for p in pngs] == [(s, s) for s in ICONS]
    data = ico(dict(zip(ICONS, pngs, strict=True)))
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    assert (reserved, kind, count) == (0, 1, len(ICONS))
    first_size, first_offset = struct.unpack("<II", data[14:22])
    assert data[first_offset : first_offset + first_size] == pngs[0]


def test_fonts_are_vendored() -> None:
    """The raster fonts ship with the generator, so cards render the same on every machine."""
    assert {p.name for p in FONT_DIR.glob("*.ttf")} >= {
        "IBMPlexSans-Light.ttf",
        "IBMPlexSerif-Regular.ttf",
        "IBMPlexSerif-Italic.ttf",
        "IBMPlexMono-Regular.ttf",
        "NotoSansMath-Regular.ttf",
    }


def test_upright_labels_render_in_the_upright_serif() -> None:
    """A label without ``font-style="italic"`` draws in the upright face, not the italic one."""

    def label(style: str) -> bytes:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60">'
            f'<text x="10" y="45"{style} font-size="40">nvim</text></svg>'
        )
        return png(svg, 200, 60)

    assert label("") != label(' font-style="italic"')


def test_flatten_drops_halos_and_filter_references() -> None:
    """Halo groups vanish and washes lose their filter but keep fill and opacity."""
    fig = (
        '<g filter="url(#bleed)" opacity="0.48"><rect fill="#1F4E9E"></rect></g>'
        '<g filter="url(#wc)" opacity="0.9"><rect fill="#D62718"></rect></g>'
    )
    assert flatten(fig) == '<g opacity="0.9"><rect fill="#D62718"></rect></g>'


def test_flatten_drops_a_halo_whose_shape_has_nested_groups() -> None:
    """A halo is removed up to its own closing tag, so a grouped shape never unbalances the figure."""
    shape = '<g><rect fill="#1F4E9E"></rect></g>'
    fig = (
        f'<g class="an-bloom"><g filter="url(#bleed)" opacity="0.48">{shape}</g>'
        f'<g filter="url(#wc)" opacity="0.9">{shape}</g></g>'
    )
    assert flatten(fig) == f'<g class="an-bloom"><g opacity="0.9">{shape}</g></g>'


def test_stamp_round_trips_and_keeps_the_png_valid() -> None:
    """A digest stamped into a PNG reads back, and the image still decodes to the same size."""
    data = stamp(png(mark_svg(), 16, 16), "ab" * 32)
    assert read_stamp(data) == "ab" * 32
    assert _png_size(data) == (16, 16)
    assert read_stamp(png(mark_svg(), 16, 16)) is None


def test_raster_digest_tracks_its_source_and_is_stamped_into_every_image() -> None:
    """The digest changes with the SVG; single PNGs and each PNG inside an ICO carry it."""
    one, other = Raster(mark_svg(), ((16, 16),)), Raster(mark_svg() + " ", ((16, 16),))
    assert one.digest != other.digest
    assert read_stamp(one.render()) == one.digest
    icon = Raster(mark_svg(), ((16, 16), (32, 32)))
    data = icon.render()
    assert data[:4] == b"\x00\x00\x01\x00" and data.count(icon.digest.encode()) == 2


def test_title_is_wrapped_before_it_is_escaped() -> None:
    """Entities do not count toward the line width and are never split across lines."""
    svg = card_svg("K", "Q&A Q&A Q&A Q&A Q&A", '<svg class="fig" viewBox="0 0 1 1"></svg>', "n", "u", wrap=7)
    lines = re.findall(r"<text[^>]*font-size=\"54\"[^>]*>(.*?)</text>", svg)
    assert lines and all(line.endswith("Q&amp;A") for line in lines) and "…" not in svg


def test_long_title_shrinks_before_it_is_truncated() -> None:
    """A title too long for four lines at the default size is set smaller, whole, before any ellipsis."""
    title = "Professional Software Engineering for AI and Distributed Systems"
    svg = card_svg("K", title, '<svg class="fig" viewBox="0 0 1 1"></svg>', "n", "u")
    lines = _TITLE_LINE.findall(svg)
    assert lines and all(float(size) < 54 for size, _ in lines)
    assert " ".join(text for _, text in lines) == title


@pytest.mark.usefixtures("fresh_fingerprint")
def test_digest_covers_the_fonts_and_renderer(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Changing a vendored font's bytes, or the resvg version, changes every raster's digest."""
    font = tmp_path / "Face.ttf"
    font.write_bytes(b"one")
    monkeypatch.setattr("figures.raster.FONT_DIR", tmp_path)
    before = Raster(mark_svg(), ((16, 16),)).digest
    font.write_bytes(b"two")
    renderer_fingerprint.cache_clear()
    after_font = Raster(mark_svg(), ((16, 16),)).digest
    monkeypatch.setattr("figures.raster.importlib.metadata.version", lambda _: "0.0.0")
    renderer_fingerprint.cache_clear()
    after_version = Raster(mark_svg(), ((16, 16),)).digest
    assert len({before, after_font, after_version}) == 3


def test_stamp_refuses_non_png_data() -> None:
    """Stamping assumes a PNG signature and IHDR; anything else is an error, not silent corruption."""
    with pytest.raises(ValueError, match="not a PNG"):
        stamp(b"GIF89a" + b"\x00" * 40, "ab" * 32)
