"""Skills taxonomy: canonical skill names, their aliases, and a category.

Phase 1 provides the schema, a validated loader, and an exact alias->canonical lookup. The
fuzzy and SBERT fallbacks for normalisation are added in Phase 4 (Section 6.4); keeping them
out of here means the loader has no heavy ML dependency.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from tailorvoice.config import PROJECT_ROOT, load_config

Category = Literal[
    "language",
    "framework",
    "ml",
    "cloud",
    "database",
    "tool",
    "soft_skill",
    "other",
]

NerLabel = Literal["SKILL", "TOOL"]

# Default NER label by category (annotation guidelines §2: named products -> TOOL, fields and
# capabilities -> SKILL). The ``ml`` category is split per entry because it holds both
# capabilities ("Machine Learning", "NLP" -> SKILL) and named libraries ("PyTorch" -> TOOL),
# so those libraries set ``ner_label`` explicitly in the taxonomy file.
_CATEGORY_DEFAULT_NER_LABEL: dict[str, NerLabel] = {
    "language": "SKILL",
    "ml": "SKILL",
    "soft_skill": "SKILL",
    "other": "SKILL",
    "framework": "TOOL",
    "cloud": "TOOL",
    "database": "TOOL",
    "tool": "TOOL",
}


class SkillEntry(BaseModel):
    """One canonical skill plus the surface forms that should map to it."""

    canonical: str = Field(min_length=1)
    category: Category
    aliases: list[str] = Field(default_factory=list)
    # Optional override of the NER label; when None the category default is used.
    ner_label: NerLabel | None = None

    @property
    def label(self) -> NerLabel:
        """The NER label this skill should be tagged as (SKILL or TOOL)."""
        return self.ner_label or _CATEGORY_DEFAULT_NER_LABEL[self.category]


class Taxonomy(BaseModel):
    """The whole taxonomy with a built-in exact-match lookup.

    ``lookup`` is case-insensitive and whitespace-trimmed; it covers canonical names and every
    alias. Anything not found is "uncanonical" and is handled by later fuzzy/SBERT stages.
    """

    version: str
    entries: list[SkillEntry]

    def _index(self) -> dict[str, str]:
        index: dict[str, str] = {}
        for e in self.entries:
            for form in [e.canonical, *e.aliases]:
                index[form.strip().lower()] = e.canonical
        return index

    def lookup(self, surface: str) -> str | None:
        """Return the canonical name for an exact (case-insensitive) match, else None."""
        return self._index().get(surface.strip().lower())

    @property
    def canonical_names(self) -> list[str]:
        return [e.canonical for e in self.entries]


def _taxonomy_path(path: Path | str | None) -> Path:
    if path is not None:
        return Path(path)
    return PROJECT_ROOT / load_config()["paths"]["taxonomy"]


def load_taxonomy(path: Path | str | None = None) -> Taxonomy:
    """Load and validate the taxonomy JSON. Raises ValueError on a malformed file."""
    taxo_path = _taxonomy_path(path)
    if not taxo_path.exists():
        raise FileNotFoundError(f"Taxonomy not found: {taxo_path}")
    data = json.loads(taxo_path.read_text(encoding="utf-8"))
    taxo = Taxonomy.model_validate(data)
    # A duplicate surface form across two canonicals would make normalisation ambiguous.
    seen: dict[str, str] = {}
    for e in taxo.entries:
        for form in [e.canonical, *e.aliases]:
            key = form.strip().lower()
            if key in seen and seen[key] != e.canonical:
                raise ValueError(f"Alias {form!r} maps to both {seen[key]!r} and {e.canonical!r}")
            seen[key] = e.canonical
    return taxo
