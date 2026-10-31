"""Unit tests for the raster outputs: social cards, favicons and the icon container."""

from __future__ import annotations

import struct

import pytest

from figures.raster import (
    FONT_DIR,
    ICON_SIZES,
    OG_SIZE,
    Raster,
    card_svg,
    flatten,
    ico,
    mark_svg,
    png,
    read_stamp,
    stamp,
    wrap_title,
)

pytestmark = pytest.mark.unit


def _png_size(data: bytes) -> tuple[int, int]:
    """Return the width and height stored in a PNG's IHDR chunk."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    return struct.unpack(">II", data[16:24])


def test_title_wraps_to_at_most_four_lines() -> None:
    """Long titles wrap on word boundaries and are cut with an ellipsis after four lines."""
    lines = wrap_title("one two three four five six seven eight nine ten eleven twelve thirteen", 12)
    assert 1 < len(lines) <= 4
    assert all(len(line) <= 13 for line in lines)
    assert lines[-1].endswith("…")


def test_card_renders_at_social_card_size() -> None:
    """A card with a figure and a title renders as a 1200x630 PNG."""
    fig = '<svg class="fig" viewBox="0 0 100 100" style="aspect-ratio: 1"><circle cx="50" cy="50" r="30"/>'
    fig += "</svg>"
    svg = card_svg("Book I · Writing", "A title & more", fig, "a.j.djalali", "example.org")
    assert "A title &amp; more" in svg and "EXAMPLE.ORG" in svg
    assert _png_size(png(svg, *OG_SIZE)) == OG_SIZE


def test_mark_and_icon_container() -> None:
    """The mark renders at each icon size, and ``ico`` packs PNGs behind a valid ICO directory."""
    pngs = [png(mark_svg(), s, s) for s in ICON_SIZES]
    assert [_png_size(p) for p in pngs] == [(s, s) for s in ICON_SIZES]
    data = ico(dict(zip(ICON_SIZES, pngs, strict=True)))
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    assert (reserved, kind, count) == (0, 1, len(ICON_SIZES))
    first_size, first_offset = struct.unpack("<II", data[14:22])
    assert data[first_offset : first_offset + first_size] == pngs[0]


def test_fonts_are_vendored() -> None:
    """The raster fonts ship with the generator, so cards render the same on every machine."""
    assert {p.name for p in FONT_DIR.glob("*.ttf")} >= {
        "IBMPlexSans-Light.ttf",
        "IBMPlexSerif-Italic.ttf",
        "IBMPlexMono-Regular.ttf",
    }


def test_flatten_drops_halos_and_filter_references() -> None:
    """Halo groups vanish and washes lose their filter but keep fill and opacity."""
    fig = (
        '<g filter="url(#bleed)" opacity="0.48"><rect fill="#1F4E9E"></rect></g>'
        '<g filter="url(#wc)" opacity="0.9"><rect fill="#D62718"></rect></g>'
    )
    assert flatten(fig) == '<g opacity="0.9"><rect fill="#D62718"></rect></g>'


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
    assert data[:4] == b"\x00\x00\x01\x00" and read_stamp(data) == icon.digest


def test_title_is_wrapped_before_it_is_escaped() -> None:
    """Entities do not count toward the line width and are never split across lines."""
    svg = card_svg("K", "Q&A Q&A Q&A Q&A Q&A", '<svg class="fig" viewBox="0 0 1 1"></svg>', "n", "u", wrap=7)
    assert svg.count("Q&amp;A") == 5 and "&amp\n" not in svg
