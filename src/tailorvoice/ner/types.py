"""Shared NER types: one entity span, used by the baseline, the trained model, and eval."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

EntityLabel = Literal["SKILL", "TOOL", "RESPONSIBILITY", "EXPERIENCE_LEVEL", "EDUCATION"]


class Entity(BaseModel):
    """A labelled character span in a JD.

    ``start``/``end`` are 0-based character offsets into the text the entity was extracted
    from (end exclusive), so ``text[start:end] == text`` of the span.
    """

    start: int
    end: int
    label: EntityLabel
    text: str

    def key(self) -> tuple[int, int, str]:
        """Identity for strict entity-level matching (span + label)."""
        return (self.start, self.end, self.label)
