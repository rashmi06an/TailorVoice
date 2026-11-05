# TailorVoice Makefile — local only. NO CI, NO git hooks, NO GitHub Actions (spec rule 10).
# All commands run on this laptop. Heavy ML extras are installed per-phase, not here.
#
# Only `setup` touches installs (via uv). Every other target calls the venv binaries
# directly, so running tests/evals never re-syncs the environment.

PYTHON_VERSION := 3.11
VENV := .venv
UV := uv
PY := $(VENV)/bin/python

.DEFAULT_GOAL := help

.PHONY: help
help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup:  ## Create .venv (Python 3.11 via uv) and install core + dev dependencies
	$(UV) venv --python $(PYTHON_VERSION) $(VENV)
	$(UV) pip install --python $(PY) -e .
	$(UV) pip install --python $(PY) pytest ruff mypy types-pyyaml
	@echo "Setup complete. Phase 0 installs core + dev tools only; ML/ASR/API extras come later."

.PHONY: test
test:  ## Run pytest
	$(PY) -m pytest

.PHONY: lint
lint:  ## Run ruff (lint + format check)
	$(VENV)/bin/ruff check .
	$(VENV)/bin/ruff format --check .

.PHONY: format
format:  ## Auto-format with ruff
	$(VENV)/bin/ruff format .
	$(VENV)/bin/ruff check --fix .

.PHONY: typecheck
typecheck:  ## Run mypy (lenient)
	$(VENV)/bin/mypy src scripts || true

.PHONY: check-docs
check-docs:  ## Verify student.md is consistent (Section 13.4)
	$(PY) scripts/check_student_md.py

.PHONY: check
check: lint test check-docs  ## Full local gate: lint + tests + docs check

# --- Data (Phase 1) -----------------------------------------------------------------------
.PHONY: data
data:  ## Validate JD corpus + taxonomy and print stats
	$(PY) scripts/validate_data.py

# --- Evaluation (Phase 2+) ----------------------------------------------------------------
.PHONY: eval-ner
eval-ner:  ## Evaluate NER baseline vs gold (synthetic smoke until real JDs are labelled)
	$(PY) scripts/eval_ner.py $(if $(SPLIT),--split $(SPLIT),)

.PHONY: eval
eval: eval-ner  ## Run all evaluations (RESULTS.md is regenerated from REAL runs only)
	@echo "Note: RESULTS.md is regenerated from real (non-synthetic) runs only; synthetic smoke tests are excluded."

# --- Stubs for later phases (fail clearly until implemented) ------------------------------
.PHONY: train-ner run
train-ner:  ## (Phase 3) Train the NER model
	@echo "Not implemented until Phase 3."; exit 1

run:  ## (Phase 8+) Start backend + frontend locally
	@echo "Not implemented until Phase 8."; exit 1
