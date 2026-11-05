"""Stage 2b — segment a cleaned JD into requirement-bearing units with a section tag.

Why: downstream matching/scoring should weight a line under "Requirements" more than a line
under "About us". We split the posting into sentences/bullets and tag each with the section it
falls under, using a lightweight rule (header keywords). A learned section classifier is a
later refinement (Section 6.2); the rule is enough to down-weight boilerplate now and is fully
deterministic, which keeps tests stable.

Sentence splitting uses spaCy's rule-based ``sentencizer`` on a blank English pipeline — no
model download needed and deterministic, so results don't drift with a model version.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Literal

import spacy
from pydantic import BaseModel
from spacy.language import Language

Section = Literal["responsibilities", "requirements", "preferred", "about", "other"]

# Header keywords -> section. First match wins; checked on a short, lowercased header line.
_SECTION_KEYWORDS: list[tuple[Section, tuple[str, ...]]] = [
    ("responsibilities", ("responsibilit", "what you'll do", "what you will do", "the role", "duties")),
    ("requirements", ("requirement", "qualification", "what we're looking for", "what we are looking for",
                      "must have", "skills", "who you are", "you have")),
    ("preferred", ("preferred", "nice to have", "bonus", "plus", "good to have", "desirable")),
    ("about", ("about us", "about the company", "about ", "who we are", "our mission", "benefits", "perks")),
]

# A line that looks like a section header: short, often ending with ':' and no sentence period.
_HEADER_MAX_WORDS = 8

# Down-weight factor applied to "about"/boilerplate sections by later stages. Stored here so the
# weighting policy lives next to the tagging that produces it.
SECTION_WEIGHT: dict[Section, float] = {
    "responsibilities": 1.0,
    "requirements": 1.0,
    "preferred": 0.7,
    "about": 0.2,
    "other": 0.6,
}


class Segment(BaseModel):
    """One sentence or bullet from a JD, with its char span and section."""

    text: str
    start: int
    end: int
    section: Section
    is_bullet: bool

    @property
    def weight(self) -> float:
        return SECTION_WEIGHT[self.section]


@lru_cache(maxsize=1)
def _sentencizer() -> Language:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    return nlp


def _match_header(line: str) -> Section | None:
    """Return the section a header line introduces, or None if it isn't a header."""
    stripped = line.strip()
    if not stripped or len(stripped.split()) > _HEADER_MAX_WORDS:
        return None
    lowered = stripped.lower().rstrip(":")
    for section, keywords in _SECTION_KEYWORDS:
        if any(k in lowered for k in keywords):
            return section
    return None


def segment_jd(text: str) -> list[Segment]:
    """Split cleaned JD ``text`` into tagged segments, preserving char offsets.

    Processing is line-aware: a bullet line is one segment; a prose line is split into
    sentences. The "current section" updates whenever a header line is seen. Offsets are into
    the exact ``text`` passed in, so entities found later can be mapped back.
    """
    segments: list[Segment] = []
    current: Section = "other"
    offset = 0
    for line in text.split("\n"):
        line_start = offset
        offset += len(line) + 1  # +1 for the '\n' we split on

        header_section = _match_header(line)
        if header_section is not None:
            current = header_section
            continue  # the header itself is not a requirement unit

        stripped = line.strip()
        if not stripped:
            continue

        is_bullet = bool(re.match(r"^\s*-\s+", line))
        if is_bullet:
            content = re.sub(r"^\s*-\s+", "", line)
            lead = line.find(content, 0)
            s = line_start + (lead if lead >= 0 else 0)
            segments.append(
                Segment(
                    text=content.strip(),
                    start=s,
                    end=s + len(content.strip()),
                    section=current,
                    is_bullet=True,
                )
            )
            continue

        # Prose line: sentence-split and record each sentence's span within the line.
        doc = _sentencizer()(line)
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if not sent_text:
                continue
            rel = line.find(sent_text)
            s = line_start + (rel if rel >= 0 else sent.start_char)
            segments.append(
                Segment(
                    text=sent_text,
                    start=s,
                    end=s + len(sent_text),
                    section=current,
                    is_bullet=False,
                )
            )
    return segments
