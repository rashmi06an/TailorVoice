"""Typed schema for a job-description record.

One JSON file per JD under ``data/raw/jd_*.json`` (PROJECT_SPEC.md Section 5.1). Keeping the
shape in Pydantic means a malformed or hand-edited file fails loudly at load time instead of
corrupting a training run later.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class JobDescription(BaseModel):
    """A single collected job posting.

    Attributes:
        id: stable identifier, e.g. ``"jd_0001"`` (also the filename stem).
        title: role title as posted.
        company: hiring company (or ``"unknown"`` if a posting hid it).
        text: the raw posting text (kept local; public postings only).
        source: where it came from (URL or site name) — needed for honest reporting.
        collected_on: the date it was collected.
        synthetic: True for sample/demo JDs that were written, not collected. Marked so no
            report ever treats synthetic text as real collected data (rule 2, Section 5.4).
    """

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    text: str = Field(min_length=1)
    source: str = Field(min_length=1)
    collected_on: date
    synthetic: bool = False

    @field_validator("id")
    @classmethod
    def _id_shape(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError(f"id must be alphanumeric/underscore, got {v!r}")
        return v
