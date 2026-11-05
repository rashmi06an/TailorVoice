"""Minimal experiment tracker: one JSON file per run under ``experiments/``.

Chosen over MLflow in Phase 0 (see student.md Decision Log) to stay zero-dependency and
laptop-friendly. Each run records config, seed, a content hash of the code snapshot, and the
metrics, so ``RESULTS.md`` can be regenerated from these files and never hand-typed.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tailorvoice.config import PROJECT_ROOT

EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


def code_snapshot_hash(root: Path | None = None) -> str:
    """Return a short hash of all ``src/`` file contents (not git — spec rule 10).

    Gives each run a reproducible fingerprint of the code that produced it without using
    version control.
    """
    src_root = (root or PROJECT_ROOT) / "src"
    hasher = hashlib.sha256()
    for file in sorted(src_root.rglob("*.py")):
        hasher.update(file.relative_to(src_root).as_posix().encode())
        hasher.update(file.read_bytes())
    return hasher.hexdigest()[:12]


def log_run(
    run_id: str,
    *,
    stage: str,
    metrics: dict[str, Any],
    config: dict[str, Any] | None = None,
    seed: int | None = None,
    data_version: str | None = None,
    notes: str = "",
) -> Path:
    """Write one experiment run to ``experiments/<run_id>.json`` and return its path.

    Args:
        run_id: unique id, e.g. ``"ner_distilbert_001"``.
        stage: pipeline stage name, e.g. ``"ner"``.
        metrics: real measured numbers only (never fabricated).
        config: the config dict used (optional).
        seed: random seed used.
        data_version: identifier of the data snapshot used.
        notes: free text.
    """
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "run_id": run_id,
        "stage": stage,
        "timestamp": datetime.now(UTC).isoformat(),
        "seed": seed,
        "data_version": data_version,
        "code_hash": code_snapshot_hash(),
        "config": config or {},
        "metrics": metrics,
        "notes": notes,
    }
    out = EXPERIMENTS_DIR / f"{run_id}.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    return out
