#!/usr/bin/env python3
"""Validate the data foundations and print a summary (Phase 1 done-when check).

Run via ``make data``. Loads every JD against the schema, loads the taxonomy, and prints
counts. Exits non-zero if anything fails to validate, so a broken data file is caught early.
Prints nothing sensitive (counts and sources only) — never full JD text (rule 11 / Section 11).
"""

from __future__ import annotations

import sys

from tailorvoice.jd.corpus import corpus_stats, load_corpus
from tailorvoice.skills.taxonomy import load_taxonomy


def main() -> None:
    try:
        jds = load_corpus()
        stats = corpus_stats()
        taxo = load_taxonomy()
    except (ValueError, FileNotFoundError) as exc:
        print(f"Data validation FAILED: {exc}")
        sys.exit(1)

    print("JD corpus:")
    print(f"  total       : {stats['total']}")
    print(f"  real         : {stats['real']}")
    print(f"  synthetic    : {stats['synthetic']}")
    print(f"  companies    : {stats['companies']}")
    print(f"  sources      : {', '.join(stats['sources']) or '(none)'}")
    print(f"  sample ids   : {', '.join(j.id for j in jds[:5]) or '(none)'}")
    print("Taxonomy:")
    print(f"  version      : {taxo.version}")
    print(f"  canonical    : {len(taxo.entries)}")
    aliases = sum(len(e.aliases) for e in taxo.entries)
    print(f"  aliases      : {aliases}")
    # Quick self-check: a known alias resolves.
    assert taxo.lookup("pytorch") == "PyTorch", "taxonomy lookup broken"
    print("Data validation passed.")


if __name__ == "__main__":
    main()
