"""Gold NER annotations: internal format, loader, and a Label Studio converter.

Internal gold format — one file ``data/annotated/<jd_id>.gold.json``::

    {"id": "jd_0001", "synthetic": false, "entities": [{"start": 10, "end": 16, "label": "SKILL"}]}

The JD text itself is NOT duplicated here; it is looked up from the corpus by id. That keeps a
single source of truth for the text and makes annotations small and diff-friendly.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from tailorvoice.config import PROJECT_ROOT, load_config
from tailorvoice.jd.corpus import load_corpus
from tailorvoice.ner.types import Entity


class GoldDoc(BaseModel):
    """Gold annotations for one JD, joined with its text from the corpus."""

    id: str
    text: str
    entities: list[Entity]
    synthetic: bool = False


def _annotated_dir(annotated_dir: Path | str | None) -> Path:
    if annotated_dir is not None:
        return Path(annotated_dir)
    return PROJECT_ROOT / load_config()["paths"]["data_annotated"]


def load_gold(
    ids: list[str] | None = None,
    *,
    annotated_dir: Path | str | None = None,
) -> list[GoldDoc]:
    """Load gold docs, joining each with its JD text from the corpus.

    Args:
        ids: restrict to these JD ids (e.g. a split); None loads every ``*.gold.json`` present.
        annotated_dir: override the annotated directory (used in tests).

    Raises:
        ValueError: if a gold file references a JD id with no text in the corpus, or a span
        falls outside the text — both are data errors that must fail loudly.
    """
    directory = _annotated_dir(annotated_dir)
    text_by_id = {jd.id: jd.text for jd in load_corpus()}
    docs: list[GoldDoc] = []
    if not directory.exists():
        return docs
    for path in sorted(directory.glob("*.gold.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        jd_id = data["id"]
        if ids is not None and jd_id not in ids:
            continue
        if jd_id not in text_by_id:
            raise ValueError(f"Gold {path.name} references unknown JD id {jd_id!r}")
        text = text_by_id[jd_id]
        ents = []
        for raw in data.get("entities", []):
            start, end = int(raw["start"]), int(raw["end"])
            if not (0 <= start < end <= len(text)):
                raise ValueError(f"Gold {path.name}: span [{start},{end}] out of range for {jd_id}")
            # Re-derive the surface text from offsets so it can never drift from the text.
            ents.append(Entity(start=start, end=end, label=raw["label"], text=text[start:end]))
        docs.append(GoldDoc(id=jd_id, text=text, entities=ents, synthetic=bool(data.get("synthetic", False))))
    return docs


def from_label_studio(export: list[dict]) -> list[dict]:
    """Convert a Label Studio JSON-min export into internal gold dicts.

    Label Studio's "JSON-MIN" export gives, per task, the task ``data`` and a ``label`` list of
    ``{start, end, labels: [...]}`` results. We keep the first label per span. The task data
    must carry the JD ``id`` (set it when importing tasks). Returns dicts ready to write as
    ``<id>.gold.json``; writing them is left to the caller so review stays a manual step.
    """
    out: list[dict] = []
    for task in export:
        jd_id = task.get("id") or task.get("jd_id")
        if not jd_id:
            raise ValueError("Label Studio task is missing a JD 'id' field")
        entities = []
        for res in task.get("label", []):
            labels = res.get("labels") or []
            if not labels:
                continue
            entities.append({"start": int(res["start"]), "end": int(res["end"]), "label": labels[0]})
        out.append({"id": jd_id, "synthetic": False, "entities": entities})
    return out
