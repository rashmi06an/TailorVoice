"""Phase 0 smoke tests: the scaffolding imports and config loads.

Fast, no models, no network. More per-stage tests are added in later phases.
"""

from __future__ import annotations

import tailorvoice
from tailorvoice.config import get_settings, load_config


def test_package_has_version() -> None:
    assert tailorvoice.__version__


def test_config_loads_and_has_core_sections() -> None:
    cfg = load_config()
    assert cfg["seed"] == 42
    assert set(cfg["ner_labels"]) == {
        "SKILL",
        "TOOL",
        "RESPONSIBILITY",
        "EXPERIENCE_LEVEL",
        "EDUCATION",
    }
    # Hand-weighted scoring formula must sum to 100 (spec Section 6.6).
    assert sum(cfg["scoring"]["weights"].values()) == 100


def test_settings_have_local_defaults() -> None:
    s = get_settings()
    assert s.rewriter_backend in {"ollama", "template"}
    assert s.ollama_host.startswith("http")
    assert s.max_input_chars > 0
