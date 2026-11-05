"""Entity-level precision / recall / F1 for NER.

Strict matching: a predicted entity counts as correct only if a gold entity has the **same
span and the same label** (standard entity-level / "exact" scoring). This is the metric for
RESULTS table 2 and is dependency-free and transparent, so the number is easy to explain.

(Token-level seqeval reporting is added in Phase 3 alongside the trained models; the strict
entity score here is what the dictionary baseline and the model are compared on.)
"""

from __future__ import annotations

from collections import defaultdict

from pydantic import BaseModel

from tailorvoice.ner.types import Entity, EntityLabel

LABELS: tuple[EntityLabel, ...] = (
    "SKILL",
    "TOOL",
    "RESPONSIBILITY",
    "EXPERIENCE_LEVEL",
    "EDUCATION",
)


class PRF(BaseModel):
    """Precision/recall/F1 with the raw counts behind them."""

    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int


def _prf(tp: int, fp: int, fn: int) -> PRF:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return PRF(precision=precision, recall=recall, f1=f1, tp=tp, fp=fp, fn=fn)


def score_document(gold: list[Entity], pred: list[Entity]) -> dict[str, tuple[int, int, int]]:
    """Return per-label (tp, fp, fn) for one document using strict span+label matching.

    Duplicate identical spans are de-duplicated per side first (a gold span matched once).
    """
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])  # label -> [tp, fp, fn]
    gold_keys = {e.key() for e in gold}
    pred_keys = {e.key() for e in pred}
    for key in pred_keys:
        label = key[2]
        if key in gold_keys:
            counts[label][0] += 1  # tp
        else:
            counts[label][1] += 1  # fp
    for key in gold_keys:
        if key not in pred_keys:
            counts[key[2]][2] += 1  # fn
    return {label: (c[0], c[1], c[2]) for label, c in counts.items()}


def evaluate(
    docs: list[tuple[list[Entity], list[Entity]]],
) -> dict[str, PRF]:
    """Aggregate (gold, pred) pairs into per-label and ``overall`` micro-averaged PRF.

    Args:
        docs: list of (gold_entities, pred_entities) per document.

    Returns:
        Mapping label -> PRF for each of the five labels (present or not) plus ``"overall"``.
    """
    totals: dict[str, list[int]] = {label: [0, 0, 0] for label in LABELS}
    for gold, pred in docs:
        for label, (tp, fp, fn) in score_document(gold, pred).items():
            totals[label][0] += tp
            totals[label][1] += fp
            totals[label][2] += fn
    result = {label: _prf(*totals[label]) for label in LABELS}
    micro = [sum(totals[label][i] for label in LABELS) for i in range(3)]
    result["overall"] = _prf(*micro)
    return result
