"""Phase 1 tests: taxonomy loading and exact-alias lookup."""

from __future__ import annotations

import json

import pytest

from tailorvoice.skills.taxonomy import load_taxonomy


def test_taxonomy_loads() -> None:
    taxo = load_taxonomy()
    assert taxo.version
    assert len(taxo.entries) >= 20
    assert "Python" in taxo.canonical_names


def test_lookup_is_case_insensitive_and_covers_aliases() -> None:
    taxo = load_taxonomy()
    assert taxo.lookup("pytorch") == "PyTorch"
    assert taxo.lookup("  PY TORCH ") == "PyTorch"
    assert taxo.lookup("sklearn") == "scikit-learn"
    assert taxo.lookup("k8s") == "Kubernetes"
    assert taxo.lookup("totally-unknown-skill") is None


def test_ambiguous_alias_rejected(tmp_path) -> None:
    bad = tmp_path / "taxo.json"
    bad.write_text(
        json.dumps(
            {
                "version": "test",
                "entries": [
                    {"canonical": "A", "category": "tool", "aliases": ["shared"]},
                    {"canonical": "B", "category": "tool", "aliases": ["shared"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="maps to both"):
        load_taxonomy(bad)
