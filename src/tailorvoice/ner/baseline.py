"""Stage 3 — Baseline A: dictionary NER with a spaCy EntityRuler.

This is the non-LLM baseline every later NER model is compared against (rule 3). It tags:

* SKILL / TOOL — from the skills taxonomy (canonical + aliases), case-insensitively.
* EXPERIENCE_LEVEL — regex-ish token patterns ("2+ years", "senior", "new grad", ...).
* EDUCATION — degree keywords ("Bachelor's degree", "B.Tech", "PhD", ...).

By design it cannot find RESPONSIBILITY (free-form verb phrases): a dictionary has no way to,
so its recall there is ~0. That gap is exactly why we train a model in Phase 3, and the eval
will show it. We keep the baseline honest rather than faking RESPONSIBILITY rules.

Runs on a blank English pipeline (no model download), so patterns match deterministically.
"""

from __future__ import annotations

import spacy
from spacy.language import Language

from tailorvoice.ner.types import Entity
from tailorvoice.skills.taxonomy import Taxonomy, load_taxonomy

# Token patterns for EXPERIENCE_LEVEL. spaCy Matcher dicts; LOWER is case-insensitive.
_EXPERIENCE_PATTERNS: list[list[dict]] = [
    # "2+ years", "3 years", "2-5 years", "2 to 5 years"
    [{"LIKE_NUM": True}, {"TEXT": "+", "OP": "?"}, {"LOWER": {"IN": ["year", "years"]}}],
    [{"LIKE_NUM": True}, {"TEXT": "-"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["year", "years"]}}],
    [{"LIKE_NUM": True}, {"LOWER": "to"}, {"LIKE_NUM": True}, {"LOWER": {"IN": ["year", "years"]}}],
    [{"LOWER": "new"}, {"LOWER": "grad"}],
    [{"LOWER": "new"}, {"LOWER": "graduate"}],
    [{"LOWER": "entry"}, {"LOWER": "level"}],
    [{"LOWER": {"IN": ["senior", "junior", "sr", "jr", "intern", "internship"]}}],
]

# Token patterns for EDUCATION.
_EDUCATION_PATTERNS: list[list[dict]] = [
    [{"LOWER": {"IN": ["bachelor", "bachelor's", "bachelors", "master", "master's", "masters"]}}],
    [{"LOWER": {"IN": ["bachelor", "bachelor's", "master", "master's"]}}, {"LOWER": "degree"}],
    [{"LOWER": {"IN": ["phd", "ph.d", "ph.d.", "doctorate"]}}],
    [{"LOWER": {"IN": ["b.tech", "btech", "b.e", "b.s", "bs", "b.sc", "m.tech", "m.s", "ms"]}}],
    [{"LOWER": "degree"}],
]


class EntityRulerBaseline:
    """Dictionary + pattern NER. Build once, call :meth:`extract` per text."""

    def __init__(self, taxonomy: Taxonomy | None = None) -> None:
        self.taxonomy = taxonomy or load_taxonomy()
        self.nlp = self._build(self.taxonomy)

    @staticmethod
    def _build(taxonomy: Taxonomy) -> Language:
        nlp = spacy.blank("en")
        # phrase_matcher_attr=LOWER makes the string (phrase) patterns case-insensitive and
        # tokenise the same way as the doc, which handles "C++", "Node.js" correctly.
        ruler = nlp.add_pipe(
            "entity_ruler",
            config={"phrase_matcher_attr": "LOWER", "validate": True},
        )
        patterns: list[dict] = []
        for entry in taxonomy.entries:
            label = entry.label  # SKILL or TOOL
            for surface in [entry.canonical, *entry.aliases]:
                patterns.append({"label": label, "pattern": surface})
        for pat in _EXPERIENCE_PATTERNS:
            patterns.append({"label": "EXPERIENCE_LEVEL", "pattern": pat})
        for pat in _EDUCATION_PATTERNS:
            patterns.append({"label": "EDUCATION", "pattern": pat})
        ruler.add_patterns(patterns)
        return nlp

    def extract(self, text: str) -> list[Entity]:
        """Return entities found in ``text``, sorted by start offset.

        Empty input returns an empty list (never raises) — graceful-failure rule 8.
        """
        if not text:
            return []
        doc = self.nlp(text)
        ents = [
            Entity(start=e.start_char, end=e.end_char, label=e.label_, text=e.text)
            for e in doc.ents
        ]
        return sorted(ents, key=lambda e: (e.start, e.end))
