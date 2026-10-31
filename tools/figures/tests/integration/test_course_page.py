"""The Courses page presents the software engineering course; the post explaining it names no school."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.helpers import read_html

pytestmark = pytest.mark.integration

NAME = "Professional Software Engineering for AI and Distributed Systems"
POST = "content/posts/professional-software-engineering-for-ai-and-distributed-systems.md"
COURSE_REPO = "https://github.com/alexdjalali/professional-software-engineering"
ORION_REPO = "https://github.com/alexdjalali/orion"


def test_the_post_names_no_institution_and_links_both_public_repositories(repo_root: Path) -> None:
    """The course stands on its own: no school named, and the two public repositories linked."""
    text = (repo_root / POST).read_text(encoding="utf-8")
    assert not re.search(r"georgia tech|gatech", text, re.IGNORECASE)
    assert COURSE_REPO in text
    assert ORION_REPO in text
    assert "solutions" in text.lower()  # says plainly that the solutions are not public


def test_courses_page_has_two_cards_each_with_one_figure(built_site: Path) -> None:
    """The existing course keeps its card; the new one sits beside it with its own figure."""
    html = read_html(built_site, "courses/index.html")
    cards = re.split(r'<div class="?project-card"?>', html)[1:]
    assert len(cards) == 2
    assert all(len(re.findall(r"<svg\b", card)) == 1 for card in cards)
    assert "Applied AI at TIYA Services" in cards[0]
    assert NAME in cards[1]


def test_the_new_card_links_the_repositories_and_the_post(built_site: Path) -> None:
    """A visitor can reach the course, the template and the explanation from the card."""
    card = re.split(r'<div class="?project-card"?>', read_html(built_site, "courses/index.html"))[2]
    for href in (
        COURSE_REPO,
        ORION_REPO,
        "/posts/professional-software-engineering-for-ai-and-distributed-systems/",
    ):
        assert href in card


def test_the_course_page_names_no_institution_for_the_new_course(built_site: Path) -> None:
    """The new card carries no school name."""
    card = re.split(r'<div class="?project-card"?>', read_html(built_site, "courses/index.html"))[2]
    assert not re.search(r"georgia tech|gatech", card, re.IGNORECASE)


def test_the_course_has_structured_data_with_an_instructor_and_no_institution(repo_root: Path) -> None:
    """The Course object names the course and its provider and invents no offering or venue."""
    courses = json.loads((repo_root / "data" / "schema" / "courses.json").read_text(encoding="utf-8"))
    mine = next(c for c in courses if c["name"] == NAME)
    assert mine["@type"] == "Course"
    assert mine["provider"] == {"@type": "Person", "name": "AJ Djalali"}
    assert "hasCourseInstance" not in mine
    assert not re.search(r"georgia|gatech", json.dumps(mine), re.IGNORECASE)
