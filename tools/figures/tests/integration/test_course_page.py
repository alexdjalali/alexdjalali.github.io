"""The Courses page presents the software engineering course; the post explaining it names no school."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration

NAME = "Professional Software Engineering for AI and Distributed Systems"
POST_SLUG = "professional-software-engineering-for-ai-and-distributed-systems"
POST = f"content/posts/{POST_SLUG}.md"
COURSE_REPO = "https://github.com/alexdjalali/professional-software-engineering"
ORION_REPO = "https://github.com/alexdjalali/orion"


def _cards(built_site: Path) -> list[str]:
    """Return the HTML of each ``.project-card`` on the Courses page, cut at the next card or the footer."""
    html = read_html(built_site, "courses/index.html")
    return [part.split("<footer", 1)[0] for part in re.split(r'<div class="?project-card"?>', html)[1:]]


def test_the_post_names_no_institution_and_links_both_public_repositories(repo_root: Path) -> None:
    """The course stands on its own: no school named, two public repositories linked, solutions private."""
    text = (repo_root / POST).read_text(encoding="utf-8")
    assert not re.search(r"georgia tech|gatech", text, re.IGNORECASE)
    assert COURSE_REPO in text
    assert ORION_REPO in text
    assert "The solutions are not public." in text


def test_the_new_course_card_follows_the_existing_one_and_is_neutral_and_linked(built_site: Path) -> None:
    """TIYA keeps the first card; the new card is second, names no school, and links repos and post."""
    cards = _cards(built_site)
    assert len(cards) == 2
    assert "Applied AI at TIYA Services" in cards[0]
    new = cards[1]
    assert NAME in new
    assert len(re.findall(r"<svg\b", new)) == 1
    assert not re.search(r"georgia tech|gatech", new, re.IGNORECASE)
    for href in (COURSE_REPO, ORION_REPO, f"/posts/{POST_SLUG}/"):
        assert href in new


def test_the_course_has_structured_data_with_a_provider_and_no_institution(repo_root: Path) -> None:
    """The Course object names the course and its provider and invents no offering or venue."""
    courses = json.loads((repo_root / "data" / "schema" / "courses.json").read_text(encoding="utf-8"))
    mine = next(c for c in courses if c["name"] == NAME)
    assert mine["@type"] == "Course"
    assert mine["provider"] == {"@type": "Person", "name": "AJ Djalali"}
    assert "hasCourseInstance" not in mine
    assert not re.search(r"georgia|gatech", json.dumps(mine), re.IGNORECASE)


def test_each_course_card_states_its_format_and_the_open_course_invites_instructors(built_site: Path) -> None:
    """Both cards open with a format line; the open course tells instructors how to get the solutions."""
    tiya, course = _cards(built_site)
    for card in (tiya, course):
        assert re.search(r'class="?course-meta', card)
    assert "Onsite" in tiya and "Graduate" in course
    assert "calendly.com/alex-djalali/30min" in course


def test_the_tiya_materials_are_grouped_by_day(built_site: Path) -> None:
    """Ten loose buttons become a kit row and one row per day, so the card reads like the other one."""
    tiya = _cards(built_site)[0]
    rows = re.findall(r'<(?:li|div) class="?course-materials__row', tiya)
    assert len(rows) == 4
