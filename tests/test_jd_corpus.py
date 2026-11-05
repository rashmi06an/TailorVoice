"""Phase 1 tests: JD schema validation and corpus loading."""

from __future__ import annotations

import json
from datetime import date

import pytest

from tailorvoice.jd.corpus import corpus_stats, load_corpus, load_jd
from tailorvoice.jd.schema import JobDescription


def test_sample_corpus_loads_and_is_marked_synthetic() -> None:
    jds = load_corpus()
    assert len(jds) >= 2
    sample_ids = {j.id for j in jds}
    assert {"jd_sample_0001", "jd_sample_0002"} <= sample_ids
    # The samples must be flagged synthetic so no report treats them as real data.
    for j in jds:
        if j.id.startswith("jd_sample_"):
            assert j.synthetic is True


def test_corpus_stats_separates_real_from_synthetic() -> None:
    stats = corpus_stats()
    assert stats["total"] == stats["real"] + stats["synthetic"]
    assert stats["synthetic"] >= 2


def test_schema_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        JobDescription(
            id="jd_x",
            title="t",
            company="c",
            text="",
            source="s",
            collected_on=date(2026, 11, 5),
        )


def test_schema_rejects_bad_id() -> None:
    with pytest.raises(ValueError):
        JobDescription(
            id="bad id!",
            title="t",
            company="c",
            text="x",
            source="s",
            collected_on=date(2026, 11, 5),
        )


def test_load_jd_wraps_bad_file(tmp_path) -> None:
    bad = tmp_path / "jd_bad.json"
    bad.write_text(json.dumps({"id": "jd_bad"}), encoding="utf-8")  # missing fields
    with pytest.raises(ValueError, match="Invalid JD file"):
        load_jd(bad)


def test_load_corpus_empty_dir_returns_empty(tmp_path) -> None:
    assert load_corpus(tmp_path) == []
