"""Load and validate the job-description corpus from ``data/raw/``.

Every file is validated against :class:`JobDescription` on load, so the rest of the pipeline
can assume well-formed records. Loading is deterministic (sorted by id) for reproducibility.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from tailorvoice.config import PROJECT_ROOT, load_config
from tailorvoice.jd.schema import JobDescription

RAW_GLOB = "jd_*.json"


def _raw_dir(raw_dir: Path | str | None) -> Path:
    if raw_dir is not None:
        return Path(raw_dir)
    return PROJECT_ROOT / load_config()["paths"]["data_raw"]


def load_jd(path: Path | str) -> JobDescription:
    """Load and validate one JD file.

    Raises:
        ValueError: with the file path attached if the JSON is invalid or fails the schema,
        so the offending file is obvious.
    """
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return JobDescription.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Invalid JD file {path}: {exc}") from exc


def load_corpus(raw_dir: Path | str | None = None) -> list[JobDescription]:
    """Load every ``jd_*.json`` under the raw dir, validated and sorted by id.

    Returns an empty list (not an error) when no JDs are present yet — the corpus is built up
    manually over time (Section 5.1).
    """
    directory = _raw_dir(raw_dir)
    if not directory.exists():
        return []
    jds = [load_jd(p) for p in sorted(directory.glob(RAW_GLOB))]
    ids = [jd.id for jd in jds]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    if dupes:
        raise ValueError(f"Duplicate JD ids in corpus: {sorted(dupes)}")
    return jds


def corpus_stats(raw_dir: Path | str | None = None) -> dict[str, object]:
    """Return a small summary of the corpus for validation/reporting."""
    jds = load_corpus(raw_dir)
    real = [j for j in jds if not j.synthetic]
    return {
        "total": len(jds),
        "real": len(real),
        "synthetic": len(jds) - len(real),
        "companies": len({j.company for j in jds}),
        "sources": sorted({j.source for j in jds}),
    }
