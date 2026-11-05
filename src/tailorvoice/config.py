"""Configuration loading for TailorVoice.

Two layers, kept separate on purpose:

* ``Settings`` — runtime/environment settings (ports, backends, limits) read from env vars
  with safe local defaults. These change per machine/deploy, so they live in the environment,
  not in version-controlled YAML. See ``.env.example``.
* ``load_config()`` — the model/weights/threshold/seed config from ``configs/default.yaml``.
  These describe *the experiment* and must be reproducible, so they live in YAML.

Why split them: a deploy should be able to change ``OLLAMA_HOST`` without editing the tuned
scoring weights, and a reproduced experiment should not depend on someone's local port.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = two levels up from this file (src/tailorvoice/config.py -> project root).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "default.yaml"


class Settings(BaseSettings):
    """Environment-driven settings with local defaults.

    No secrets are required (zero-cost rule): every field has a working local default.
    Values are read from the process environment or a local ``.env`` file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Rewriter backend: "ollama" (local model) or "template" (deterministic fallback).
    rewriter_backend: str = "template"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # ASR
    whisper_model_size: str = "base"

    # Storage
    database_url: str = "sqlite:///./tailorvoice.db"

    # Guards
    max_input_chars: int = 20_000
    rate_limit_per_min: int = 60

    # CORS: only the local frontend origin by default.
    frontend_origin: str = "http://localhost:5173"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached environment settings."""
    return Settings()


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    """Load the YAML experiment config.

    Args:
        path: optional override; defaults to ``configs/default.yaml``.

    Returns:
        The parsed config as a plain dict.

    Raises:
        FileNotFoundError: if the config file is missing (so a misconfigured run fails loudly
        rather than silently using defaults).
    """
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Config at {config_path} did not parse to a mapping.")
    return data
