# TailorVoice

> Public-facing README is written in **Phase 11** with real, measured numbers only.
> For now this is a placeholder so the package builds.

**One-liner:** TailorVoice reads a job description (typed or dictated), extracts its
requirements with a trained NER model, semantically matches them against a verified profile,
gives an explainable 0–100 fit score with skill gaps, and rewrites resume bullets behind a
faithfulness verifier so nothing is invented.

- Full design: [`PROJECT_SPEC.md`](PROJECT_SPEC.md)
- Study guide (how every part works): [`student.md`](student.md)
- Real results: [`RESULTS.md`](RESULTS.md)

## Quick start (Phase 0)

```bash
make setup   # .venv with Python 3.11 + core/dev deps (via uv)
make test    # smoke tests
make check   # lint + tests + docs check
```

Zero cost: all models are free and run locally. See `PROJECT_SPEC.md` Section 19.
