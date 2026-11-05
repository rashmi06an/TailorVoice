#!/usr/bin/env python3
"""Evaluate NER against gold annotations (Phase 2: dictionary baseline).

Usage::

    python scripts/eval_ner.py                 # all annotated JDs
    python scripts/eval_ner.py --split val     # only ids in data/splits/val.txt
    python scripts/eval_ner.py --model baseline

Honesty rules enforced here:
  * If every evaluated JD is synthetic (no real annotations yet), the result is printed as a
    **SYNTHETIC SMOKE TEST**, logged to ``experiments/smoke_*.json`` with ``synthetic: true``,
    and is NEVER written to RESULTS.md. RESULTS table 2 stays TBD until real JDs are labelled.
  * As soon as real annotated JDs exist (``synthetic: false``), the same command produces a
    real run logged via the tracker; ``make eval`` (later) turns real runs into RESULTS.md.

So this script is already "ready for real data": add real ``*.gold.json`` files (and optional
``data/splits/<split>.txt``) and re-run — no code change needed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tailorvoice.config import PROJECT_ROOT, load_config
from tailorvoice.ner.baseline import EntityRulerBaseline
from tailorvoice.ner.data import GoldDoc, load_gold
from tailorvoice.ner.eval import LABELS, PRF, evaluate
from tailorvoice.tracking import log_run


def _read_split(split: str) -> list[str] | None:
    path = PROJECT_ROOT / load_config()["paths"]["data_splits"] / f"{split}.txt"
    if not path.exists():
        print(f"Split file not found: {path} — evaluating all annotated JDs instead.")
        return None
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _print_table(scores: dict[str, PRF]) -> None:
    header = f"{'label':<18}{'P':>8}{'R':>8}{'F1':>8}{'tp':>6}{'fp':>6}{'fn':>6}"
    print(header)
    print("-" * len(header))
    for label in [*LABELS, "overall"]:
        s = scores[label]
        print(
            f"{label:<18}{s.precision:>8.3f}{s.recall:>8.3f}{s.f1:>8.3f}"
            f"{s.tp:>6}{s.fp:>6}{s.fn:>6}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate NER against gold annotations.")
    parser.add_argument("--split", default=None, help="split name (val/test/train) in data/splits/")
    parser.add_argument("--model", default="baseline", choices=["baseline"], help="NER model")
    parser.add_argument("--run-id", default=None, help="experiment run id (default auto)")
    args = parser.parse_args()

    ids = _read_split(args.split) if args.split else None
    gold_docs: list[GoldDoc] = load_gold(ids)
    if not gold_docs:
        print("No gold annotations found in data/annotated/. Nothing to evaluate.")
        sys.exit(1)

    model = EntityRulerBaseline()
    pairs = [(doc.entities, model.extract(doc.text)) for doc in gold_docs]
    scores = evaluate(pairs)

    synthetic_only = all(doc.synthetic for doc in gold_docs)
    n_docs = len(gold_docs)
    split_label = args.split or "all-annotated"

    print()
    if synthetic_only:
        print("=" * 64)
        print("  SYNTHETIC SMOKE TEST — NOT A REAL RESULT, NOT FOR RESULTS.md")
        print(f"  {n_docs} synthetic JD(s); baseline={args.model}; split={split_label}")
        print("=" * 64)
    else:
        print(f"NER eval — model={args.model}; split={split_label}; docs={n_docs}")
    print()
    _print_table(scores)
    print()

    metrics = {
        label: {
            "precision": round(scores[label].precision, 4),
            "recall": round(scores[label].recall, 4),
            "f1": round(scores[label].f1, 4),
            "tp": scores[label].tp,
            "fp": scores[label].fp,
            "fn": scores[label].fn,
        }
        for label in [*LABELS, "overall"]
    }

    if synthetic_only:
        run_id = args.run_id or f"smoke_ner_{args.model}_synthetic"
        path = log_run(
            run_id,
            stage="ner",
            metrics=metrics,
            config={"model": args.model, "split": split_label},
            seed=load_config()["seed"],
            data_version="synthetic-sample",
            notes="SYNTHETIC SMOKE TEST. Not a real result. Excluded from RESULTS.md.",
        )
        print(f"Logged synthetic smoke run to {path.name} (not a result).")
        print("RESULTS.md table 2 (NER) stays TBD until real JDs are annotated.")
    else:
        run_id = args.run_id or f"ner_{args.model}_{split_label}"
        path = log_run(
            run_id,
            stage="ner",
            metrics=metrics,
            config={"model": args.model, "split": split_label},
            seed=load_config()["seed"],
            data_version="real",
            notes=f"Real NER eval on {n_docs} JDs.",
        )
        print(f"Logged real run to {path.name}. Run `make eval` to regenerate RESULTS.md.")


if __name__ == "__main__":
    main()
