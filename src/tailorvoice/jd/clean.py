"""Stage 2a — clean raw job-description text.

Postings arrive with HTML tags, HTML entities, non-breaking spaces, and ragged whitespace.
We strip those to plain text while **preserving line breaks and bullet markers**, because the
segmenter (``segment.py``) relies on lines to find bullets and section headers.

Deliberately dependency-light: a full HTML parser (bs4/lxml) is overkill for the mostly-text
postings we collect, and keeping it to the standard library avoids another install.
"""

from __future__ import annotations

import html
import re

# Block-level tags whose boundaries should become line breaks so structure survives.
_BLOCK_TAGS = re.compile(
    r"</?\s*(?:p|br|div|li|ul|ol|tr|h[1-6]|section|article)\b[^>]*>",
    flags=re.IGNORECASE,
)
_ANY_TAG = re.compile(r"<[^>]+>")
_BULLET_PREFIX = re.compile(r"^[\t ]*[•\-\*•●∙]\s+", flags=re.MULTILINE)
_MULTISPACE = re.compile(r"[^\S\n]+")  # runs of spaces/tabs but NOT newlines
_MULTINEWLINE = re.compile(r"\n{3,}")


def clean_text(raw: str) -> str:
    """Return plain, structure-preserving text from a possibly-HTML posting.

    Steps, in order:
      1. Turn block-level tags into newlines, then drop any remaining tags.
      2. Unescape HTML entities (``&amp;`` -> ``&``) and normalise non-breaking spaces.
      3. Normalise bullet markers to ``- `` and collapse horizontal whitespace.
      4. Collapse 3+ blank lines to one, strip leading/trailing blank space.

    Args:
        raw: the posting text as collected (HTML or plain).

    Returns:
        Cleaned text. Empty input returns an empty string (never raises) — the caller decides
        whether empty is an error (graceful-failure rule 8).
    """
    if not raw:
        return ""
    text = _BLOCK_TAGS.sub("\n", raw)
    text = _ANY_TAG.sub("", text)
    text = html.unescape(text)
    text = text.replace(" ", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = _BULLET_PREFIX.sub("- ", text)
    text = _MULTISPACE.sub(" ", text)
    text = _MULTINEWLINE.sub("\n\n", text)
    # Strip trailing spaces on each line without touching the newlines.
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return text.strip()
