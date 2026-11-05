#!/usr/bin/env python3
"""Docs self-check for student.md (PROJECT_SPEC.md Section 13.4).

Verifies, as far as is automatable, that the study doc stays honest and in sync with the code:

1. Every directory under ``src/tailorvoice/`` appears in the Repository map (Section 3).
2. Every experiment run id referenced in student.md exists as ``experiments/<id>.json``.
3. All required top-level headings (0..17) are present.
4. No stray ``TODO`` marker is left in a phase that is marked done in the changelog.

Exit code is non-zero if any check fails, so ``make check`` surfaces a drifting doc.
Run via ``make check-docs``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STUDENT_MD = PROJECT_ROOT / "student.md"
SRC_DIR = PROJECT_ROOT / "src" / "tailorvoice"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

REQUIRED_HEADINGS = [f"## {i}." for i in range(18)]  # headings 0..17

# A "run id" reference looks like run_id=xxx, run `xxx`, or "run ID xxx"; we match the
# experiments filename convention: tokens that also exist as experiments/<token>.json.
RUN_ID_PATTERN = re.compile(r"\b([a-z][a-z0-9_]{2,})\b")


def read_student_md() -> str:
    if not STUDENT_MD.exists():
        _fail([f"student.md not found at {STUDENT_MD}"])
    return STUDENT_MD.read_text(encoding="utf-8")


def check_src_dirs_in_map(text: str) -> list[str]:
    """Each src subpackage directory name must appear somewhere in student.md."""
    errors: list[str] = []
    if not SRC_DIR.exists():
        return [f"src package dir missing: {SRC_DIR}"]
    for child in sorted(SRC_DIR.iterdir()):
        if child.is_dir() and not child.name.startswith("__"):
            token = f"{child.name}/"
            if token not in text and child.name not in text:
                errors.append(
                    f"src/ dir '{child.name}' not referenced in student.md repository map"
                )
    return errors


def check_required_headings(text: str) -> list[str]:
    return [f"missing required heading '{h}'" for h in REQUIRED_HEADINGS if h not in text]


def check_referenced_run_ids(text: str) -> list[str]:
    """Any token that looks like 'run id XXX' must have experiments/XXX.json.

    We only enforce ids introduced explicitly as 'run id'/'run ID' to avoid false positives
    on ordinary prose. Until real runs exist this is a no-op.
    """
    errors: list[str] = []
    existing = (
        {p.stem for p in EXPERIMENTS_DIR.glob("*.json")} if EXPERIMENTS_DIR.exists() else set()
    )
    for m in re.finditer(r"run[ _]?id[:\s=]+`?([A-Za-z0-9_]+)`?", text, flags=re.IGNORECASE):
        rid = m.group(1)
        if rid.lower() in {"the", "run", "tbd"}:
            continue
        if rid not in existing:
            errors.append(f"referenced run id '{rid}' has no experiments/{rid}.json")
    return errors


def check_no_todo_in_done_phases(text: str) -> list[str]:
    """Flag an uppercase TODO anywhere; finished phases must not leave them.

    Early on this is advisory; we only fail on literal 'TODO' (not 'TBD', which is allowed).
    """
    if "TODO" in text:
        return ["student.md contains a 'TODO' marker (use 'TBD' with a plan instead)"]
    return []


def _fail(errors: list[str]) -> None:
    print("student.md check FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)


def main() -> None:
    text = read_student_md()
    errors: list[str] = []
    errors += check_required_headings(text)
    errors += check_src_dirs_in_map(text)
    errors += check_referenced_run_ids(text)
    errors += check_no_todo_in_done_phases(text)
    if errors:
        _fail(errors)
    print("student.md check passed.")


if __name__ == "__main__":
    main()
