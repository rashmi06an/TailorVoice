# TailorVoice — Master Build Spec, FREE EDITION (for Claude Code)

> **FREE EDITION:** this version costs nothing to build or run. No paid API, no API key, no credit card. See rule 11 and Section 19.

> Put this file in the project root as `PROJECT_SPEC.md`, and put the short "CLAUDE.md" block from Section 16 in the root as `CLAUDE.md`.
> Build **phase by phase** (Section 12). After every phase, update `student.md` (Section 13) **in the same working step**. Never use git or GitHub (see rule 10).

---

## 0. Who I am and what this project is for

I am Rashmi, a B.Tech CS & AI student (2024–2028). This is my **flagship AI/ML project for my resume and campus placements**. It must:

1. Be a genuine **ML project** (data, models, training, evaluation, ablations), not a thin LLM wrapper.
2. Be fully **explainable by me** in interviews. Every component must be documented in `student.md` so I can study and explain it.
3. Be **demo-able** with a public link and a short voice demo.
4. Be **honest**: no fabricated metrics, ever.

**One-liner:** TailorVoice is a voice-driven system that reads a job description, extracts the requirements with a trained NER model, semantically matches them against my verified profile, gives an explainable fit score with skill gaps, and rewrites my resume bullets with a **faithfulness verifier** so the rewrite never invents experience.

---

## 1. Non-negotiable rules

1. **Truthfulness:** The rewriter may only rephrase and re-emphasise facts that exist in the user's profile. Every rewritten bullet must link to its source bullet. Never add skills, tools, numbers, or outcomes not in the profile.
2. **No fabricated results:** All numbers in README, `student.md`, and `RESULTS.md` must come from real runs of the evaluation scripts. If a number is unknown, write `TBD` and say how to obtain it. Never invent metrics.
3. **ML-core:** The extraction, matching, scoring and verification stages must each have a **non-LLM trained or classical ML baseline** and be evaluated. A small local open-source LLM (run through Ollama) is used only for the rewriting step (and optionally for pre-labelling data, which must be disclosed). A non-LLM template rewriter must always work as a fallback.
4. **Reproducibility:** fixed random seeds, pinned dependencies, `make` commands for every pipeline stage, data and model versions recorded.
5. **No data leakage:** train/val/test splits are made by *job description* (and company), not by sentence. Test set is touched only for final reporting.
6. **Small and readable:** clear names, type hints, docstrings, comments explaining *why*. No heavy infra (no Kubernetes, no microservices).
7. **Privacy:** resumes are personal data. Real personal data stays in `data/private/` on my machine only and is never uploaded, shared, or zipped into any output. Sample data is synthetic or my own.
8. **Graceful failure:** empty input, huge JDs, model/API failure, bad audio must never crash the app; return clear errors.
9. **Every phase ends with:** tests passing, `student.md` updated, and a short summary of what was done and what is next.
10. **NO GIT, NO GITHUB — absolute rule.** Do not run `git init`, `git add`, `git commit`, `git push`, `git remote`, or create branches, tags, or pull requests. Do not use the `gh` CLI. Do not create `.github/` or GitHub Actions. Do not upload code, data, or documents to any remote service. Everything stays in the local project folder. If a step seems to need git or GitHub (for example a hosting provider), stop and ask me first. I will handle any version control and uploading myself.
11. **ZERO COST — absolute rule.** Use only free, open-source software and free local models. Never add a paid API, a paid service, a subscription, or anything that needs a credit card or an API key. Never send resume or profile text to any third-party service. If something would cost money or need an account, stop and ask me first.

---

## 2. Tech stack

- **Language:** Python 3.11
- **Speech:** `faster-whisper` (Whisper base/small, CPU int8 so it runs on a Mac laptop)
- **NLP/ML:** `spaCy` (baseline + tooling), `transformers` + `torch` (DistilBERT/BERT token classification), `sentence-transformers` (SBERT, e.g. `all-MiniLM-L6-v2`), `scikit-learn` (TF-IDF, logistic regression, gradient boosting), `shap` (explanations), `rapidfuzz` (fuzzy skill normalisation)
- **Faithfulness check:** NLI cross-encoder (e.g. `cross-encoder/nli-deberta-v3-small`) + rule-based checks (numbers, named tools)
- **Rewriter (two backends behind one `Rewriter` interface, mockable for tests):**
  1. `ollama` (default when available): a small local instruct model served by Ollama on `localhost`, called over its local HTTP API. No key, no cost, text never leaves my machine.
  2. `template` (always-available fallback): a deterministic, rule-based rewriter (action-verb swaps, keyword re-ordering, trimming) that is faithful by construction and needs no model.
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy + SQLite
- **Frontend:** React + Vite + TypeScript (keep it small; if time is short, Streamlit is an acceptable fallback, decided in Phase 9)
- **Tracking:** MLflow (local file store) or a simple `experiments/*.json` log, pick one in Phase 0 and stick to it
- **Labelling:** Label Studio (local)
- **PDF:** WeasyPrint or ReportLab for one-page resume export
- **Quality:** `pytest`, `ruff`, `mypy` (lenient); run locally through `make check` (no CI service, no git hooks)
- **Packaging/run:** `uv` or `pip` + `requirements.txt`, `Makefile`, Docker (single Dockerfile for deploy)
- **Deploy:** primary target is running locally plus a recorded demo. An optional free public demo in "lite mode" (see Section 18.8 and 19.4) is decided in Phase 10; I verify any host's current free-tier limits myself.

---

## 3. System architecture and data flow

```
 Voice (mic/audio file)                Pasted JD text
        │                                    │
        ▼                                    │
 [1] ASR: faster-whisper ───────────────────►│
        │  (transcript + confidence)         │
        ▼                                    ▼
 [2] JD preprocessing (clean, segment into requirement sentences)
        │
        ▼
 [3] Requirement extraction: NER model
        │   entities: SKILL, TOOL, RESPONSIBILITY, EXPERIENCE_LEVEL, EDUCATION
        ▼
 [4] Skill normalisation (taxonomy + embedding/fuzzy match: "PyTorch" == "pytorch")
        │
        ▼
 [5] Semantic matching vs user profile
        │   TF-IDF baseline  vs  SBERT cosine  (per requirement → best profile evidence)
        ▼
 [6] Scoring model: features → fit score 0–100 + SHAP explanation + gap list
        │
        ▼
 [7] Evidence selection: choose most relevant projects/bullets for this JD
        │
        ▼
 [8] Bullet rewriting (LLM, constrained prompt, uses only selected evidence)
        │
        ▼
 [9] Faithfulness verifier: NLI entailment + number/tool checks
        │      fail → retry once → else fall back to original bullet
        ▼
 [10] Resume assembly + PDF export + history storage (SQLite)
```

Every stage has: typed input/output (Pydantic schema), a logged latency, a unit test, and a section in `student.md`.

---

## 4. Repository structure (keep ≤ ~60 files for v1)

```
tailorvoice/
├── CLAUDE.md                  # short rules for Claude Code (Section 16)
├── PROJECT_SPEC.md            # this file
├── student.md                 # LIVING study doc (Section 13) — most important doc
├── README.md                  # public-facing, written in Phase 11
├── RESULTS.md                 # real evaluation tables only (auto-generated numbers)
├── Makefile
├── pyproject.toml / requirements.txt
├── Dockerfile
├── configs/                   # yaml configs: models, weights, thresholds, seeds
├── data/
│   ├── raw/                   # collected JDs (public postings; keep local, never redistribute)
│   ├── annotated/             # NER gold labels (Label Studio export + converted)
│   ├── splits/                # train/val/test ids
│   ├── taxonomy/              # skills_taxonomy.json (canonical skills + aliases)
│   ├── pairs/                 # (JD, profile) pairs with human fit ratings
│   └── private/               # my real profile (local only)
├── src/tailorvoice/
│   ├── asr/                   # whisper wrapper, audio validation
│   ├── jd/                    # cleaning, segmentation
│   ├── ner/                   # baseline (EntityRuler), BERT trainer, inference
│   ├── skills/                # normalisation, taxonomy loader
│   ├── matching/              # tfidf, sbert, evidence retrieval
│   ├── scoring/               # feature builder, model, explanations
│   ├── rewrite/               # prompts, LLM client, bullet rewriter
│   ├── verify/                # NLI + rule checks
│   ├── pipeline.py            # orchestrates stages 1–10
│   ├── api/                   # FastAPI routes, schemas, deps
│   ├── db/                    # SQLAlchemy models
│   └── export/                # PDF builder
├── scripts/                   # train_ner.py, eval_*.py, build_pairs.py, make_report.py
├── tests/                     # unit + integration tests, fixtures
├── notebooks/                 # EDA & error analysis (cleaned)
├── experiments/               # tracked runs
├── frontend/                  # React app
└── docs/                      # architecture diagram, model cards, decisions
```

---

## 5. Data plan (this is what makes it a real ML project)

### 5.1 Job descriptions corpus
- Target **300–500 JDs** for tech/ML/SDE/product/consulting-adjacent roles, collected manually/semi-manually from public postings. Record source and date for each. Respect site terms; if redistribution is unclear, keep raw text out of git and ship only IDs + my annotations.
- Store as `data/raw/jd_0001.json` with fields: `id, title, company, text, source, collected_on`.
- Write `scripts/collect_notes.md` documenting exactly how data was collected (needed for honest reporting).

### 5.2 NER annotation
- Label set: `SKILL`, `TOOL`, `RESPONSIBILITY`, `EXPERIENCE_LEVEL`, `EDUCATION`.
- Write `docs/annotation_guidelines.md` with definitions, edge cases, and examples before labelling.
- Annotate **at least 150 JDs** by hand in Label Studio. Optional: pre-labelling with a local Ollama model only (never a paid or third-party API) to speed up, but **every label must be reviewed by me**, and `student.md` must state that pre-labelling was used.
- Measure **inter-annotator consistency** by re-annotating a 20-JD subset after a week (self-agreement, Cohen's kappa). Report it.
- Split by JD: 70/15/15 train/val/test, stored in `data/splits/`.

### 5.3 Skills taxonomy
- Build `skills_taxonomy.json`: canonical name, aliases, category (language, framework, ML, cloud, tool, soft skill). Start from annotated entities, cluster aliases semi-automatically, review by hand.

### 5.4 Fit-rating pairs (for the scoring model)
- Create **~300 (JD, profile) pairs**: my real profile plus 3–4 clearly labelled synthetic persona profiles (different strengths) × sampled JDs.
- I rate each pair 1–5 (rubric in `docs/rating_rubric.md`). Use a small CLI (`scripts/rate_pairs.py`) to make rating fast.
- Mark synthetic personas as synthetic in every report.

### 5.5 Faithfulness test set
- Create **~150 (original bullet, rewritten bullet)** pairs: some faithful, some deliberately unfaithful (added tool, inflated number, new claim). Labelled faithful / unfaithful. Used to evaluate the verifier.

### 5.6 ASR test set
- Record **~30 short clips** of me dictating JDs/profile snippets (varying pace, background noise, accent-heavy technical terms like "PyTorch", "Kubernetes") with ground-truth transcripts, for WER measurement.

---

## 6. ML components in detail

### 6.1 ASR (stage 1)
- `faster-whisper` base vs small, int8 CPU. Return transcript, per-segment confidence, language.
- Post-processing: a **tech-term correction** step using the skills taxonomy (fuzzy-match low-confidence tokens, e.g. "pie torch" → "PyTorch"). Evaluate WER **with and without** this correction.
- Validation: max audio length, supported formats, silence detection.

### 6.2 JD preprocessing (stage 2)
- Clean HTML/boilerplate, split into sentences/bullets, tag sections (responsibilities / requirements / preferred / about-us) using a simple rule + small classifier; down-weight "about us" text.

### 6.3 Requirement extraction NER (stage 3)
- **Baseline A:** spaCy `EntityRuler` using the taxonomy (pure dictionary).
- **Baseline B:** spaCy trained NER (`blank("en")` or `en_core_web_sm` tok2vec).
- **Main model:** `distilbert-base-uncased` (and optionally `bert-base`) token classification, BIO tags, trained with HF `Trainer`.
- Metrics: entity-level precision/recall/F1 (`seqeval`), per-label F1, confusion on boundary vs type errors. Report on held-out test JDs.
- Error analysis notebook: top 30 failure cases categorised.

### 6.4 Skill normalisation (stage 4)
- Exact alias lookup → `rapidfuzz` fuzzy match → SBERT nearest-neighbour fallback with a threshold. Unknown skills kept as "uncanonical" and flagged.
- Evaluate normalisation accuracy on a hand-labelled sample.

### 6.5 Semantic matching (stage 5)
- For each extracted requirement, retrieve the best-matching evidence (project bullet, skill, coursework) from my profile.
- **Baseline:** TF-IDF cosine. **Main:** SBERT cosine. **Optional stretch:** fine-tune SBERT with contrastive/MultipleNegativesRanking loss on requirement–evidence pairs built from my annotations.
- Metrics on a labelled requirement→evidence set: Recall@1/3, MRR, nDCG. Compare TF-IDF vs SBERT vs fine-tuned.

### 6.6 Scoring model (stage 6)
- Features per (JD, profile): required-skill coverage (weighted by importance), preferred-skill coverage, mean/max SBERT similarity, TF-IDF similarity, project-relevance score, experience-level gap, education match, count of unmatched required skills.
- Models: (a) **hand-weighted formula** baseline (weights in config, sum to 100); (b) **Ridge/Logistic regression**; (c) **Gradient boosting** (XGBoost/LightGBM or sklearn). Use 5-fold CV grouped by JD.
- Metrics: Spearman/Pearson vs my 1–5 ratings, MAE, and ranking quality (does it rank better-fit JDs higher for the same profile?). Calibrate to 0–100.
- **Explainability:** SHAP values → plain-language reasons ("+12: you cover 8/10 required skills; −9: no cloud experience shown").
- **Fallback:** if SBERT or the model fails to load, use the formula baseline so the app still returns a score.

### 6.7 Evidence selection (stage 7)
- Rank projects/bullets by relevance to the JD, choose top-k for a one-page resume, enforce length limits.

### 6.8 Bullet rewriting (stage 8)
- LLM prompt contract: input = one original bullet + extracted JD keywords that the profile **already supports**; output = one rewritten bullet (≤ 1 line, action verb first), plus the `source_bullet_id`. Forbidden: new tools, new numbers, new outcomes. Temperature low. Because small local models make more mistakes: request JSON-constrained output, keep prompts short with 2–3 few-shot examples, and treat the verifier as mandatory. Track and report the **rejection rate** (how often the verifier rejects the local model's rewrite and the original or template rewrite is used instead) as a real metric in `RESULTS.md`.
- Also produce **gap suggestions** (what the user could learn/do), clearly separate from the resume text.

### 6.9 Faithfulness verifier (stage 9)
- Checks: (1) NLI entailment (original ⇒ rewritten) above threshold; (2) every number in rewrite exists in original; (3) every tool/skill in rewrite exists in profile or original; (4) length/format rules.
- On failure: one stricter retry, then fall back to original bullet and tell the user.
- Evaluate on the faithfulness test set: precision/recall for catching unfaithful rewrites. Report **hallucination rate with vs without verifier** on a stress set.

---

## 7. Evaluation and experiments

- `make eval` runs every evaluation script and regenerates `RESULTS.md` (tables built from files in `experiments/`, never typed by hand).
- Required result tables:
  1. ASR: WER (base vs small; with vs without tech-term correction).
  2. NER: P/R/F1 per label (dictionary baseline vs spaCy vs DistilBERT).
  3. Matching: Recall@k, MRR, nDCG (TF-IDF vs SBERT vs fine-tuned if done).
  4. Scoring: Spearman, MAE (formula vs ridge vs GBM).
  5. Faithfulness: verifier P/R, hallucination rate with/without verifier.
  6. End-to-end latency per stage and total (median, p95) on CPU.
- **Ablations:** remove each stage and show the effect on the final score quality and faithfulness.
- Log every run (config, seed, data version, code snapshot hash computed from file contents, metrics) in the tracker.
- Include a "Limitations & honest caveats" section (small dataset, my own annotation bias, synthetic personas, etc.).

---

## 8. Backend API (FastAPI, versioned `/api/v1`)

- `GET /health`
- `POST /profile`, `PUT /profile`, `GET /profile`
- `POST /transcribe` (audio file → transcript)
- `POST /jd/analyze` (text → extracted + normalised requirements)
- `POST /match` (JD + profile → score, SHAP reasons, gaps, evidence map)
- `POST /tailor` (JD + profile → rewritten bullets with source links + verifier status)
- `POST /export/pdf`
- `GET /history`, `GET /history/{id}`, `DELETE /history/{id}`

Each endpoint: Pydantic request/response models, error codes documented, request IDs, structured logs, input size limits.

---

## 9. Frontend (small, clean, mobile friendly)

Pages: **Profile**, **New Tailoring** (record or paste JD → analysis → score → side-by-side original vs rewritten bullets with verifier badges), **History**. Show the score breakdown chart, missing skills, and a clear "this is the original wording" toggle. A **"How it works" page** that renders the pipeline diagram (great for demos and interviews).

---

## 10. Testing

- Unit tests for each stage with small fixtures; the LLM client and Whisper are mocked in fast tests.
- Property-style tests for the verifier (e.g. adding a number must fail).
- Integration test for the full pipeline on 3 fixture JDs.
- Regression test: scoring is monotonic (adding a required skill the profile has never lowers the score).
- `make check` runs ruff + pytest + the `student.md` docs check locally. No CI, no GitHub Actions.

---

## 11. Security and privacy

- Secrets only via env vars, `.env.example` provided, `.env` stays local and is never shared.
- Rate limit and size-limit uploads; validate audio type.
- Do not log full resume text; log IDs and lengths.
- `data/private/` is local only; never upload it or include it in any export.

---

## 12. Phases (build in this order; stop after each for my review)

| Phase | Goal | Deliverables | Done when |
|---|---|---|---|
| 0 | Setup | project folder (no git repo), env, Makefile, configs, empty `student.md` skeleton, tracker choice | `make test` runs green |
| 1 | Data foundations | collection notes, JD corpus loader, annotation guidelines, taxonomy v0, Label Studio config | schemas validated; sample JDs load |
| 2 | JD preprocessing + baseline extraction | cleaner, segmenter, EntityRuler baseline, eval script | baseline F1 on val reported |
| 3 | NER model | spaCy + DistilBERT training scripts, inference module, error analysis | test-set F1 table in `RESULTS.md` |
| 4 | Skill normalisation + matching | normaliser, TF-IDF + SBERT retrieval, eval script | Recall@k/MRR table |
| 5 | Scoring | feature builder, formula baseline, ridge/GBM, SHAP reasons, fallback | scoring table + explanation demo |
| 6 | ASR | Whisper wrapper, tech-term correction, WER eval | WER table |
| 7 | Rewrite + verifier | prompts, Ollama client, template rewriter, NLI + rule verifier, retry/fallback, rejection-rate eval | faithfulness table + rejection rate |
| 8 | Pipeline + API + DB | orchestrator, endpoints, history, PDF export, tests | end-to-end test passes |
| 9 | Frontend | pages, diagram, voice recording | full demo flow works locally |
| 10 | Deploy (prepare only) | Dockerfile, env var lists, numbered manual deploy steps, health check; I deploy by hand | steps verified locally in Docker |
| 11 | Polish | README, architecture diagram, model cards, demo script, 2-min video script, resume bullets (using real numbers) | `RESULTS.md` + README consistent |

At the end of each phase Claude Code must output: **(a)** what was built, **(b)** files changed, **(c)** test status, **(d)** what was added to `student.md`, **(e)** real metrics produced (or `TBD`), **(f)** next-phase plan and any decision needed from me.

---

## 13. `student.md` — the living study document (CRITICAL)

Purpose: after the build, I must be able to open **only this file** and explain the whole project in an interview, from the problem to the ML details to the code layout, without re-reading the code.

### 13.1 Rules for maintaining it
1. Update `student.md` **in the same working step** as any code change that alters behaviour, structure, data flow, models, configs, or metrics. A change without a `student.md` update is incomplete.
2. Write in **plain language first, technical detail second**. Assume I know ML basics but not this codebase.
3. Always link to exact paths and function/class names (`src/tailorvoice/ner/train.py::train()`), and say **what it takes in, what it returns, and why it exists**.
4. Never leave stale text. If a design changed, rewrite the section and add an entry in the Decision Log explaining the old vs new and why.
5. Real numbers only; every metric cites the experiment run ID and date. Unknown → `TBD`.
6. Keep a running **"Things I should be able to explain"** checklist and a **Viva Q&A** section, growing every phase.
7. Include small worked examples with actual inputs/outputs from the pipeline, not just descriptions.

### 13.2 Required structure (create the skeleton in Phase 0, fill as you go)

See `student.md` for the maintained skeleton. Headings 0–17 as listed in the spec.

### 13.3 Per-phase update checklist (Claude Code must run this at the end of every phase)
- [ ] Repository map updated for new/changed/removed files
- [ ] Component section added or revised using the template
- [ ] Worked example refreshed with real outputs
- [ ] Experiment log and metrics updated with run IDs
- [ ] Decision log entry added for any design choice
- [ ] Glossary and Viva Q&A extended (≥ 5 new Q&As per phase)
- [ ] Reproduce-from-scratch commands verified to actually run
- [ ] Phase changelog entry written
- [ ] Nothing in `student.md` contradicts the code or `RESULTS.md`

### 13.4 Auto-checks
`scripts/check_student_md.py` (run via `make check-docs`, part of `make check`) verifies: every file under `src/` appears in the repository map; every experiment run ID referenced exists in `experiments/`; required headings are present; no `TODO` left in finished phases.

---

## 14. Resume and interview positioning (fill ONLY with real numbers at the end)

Resume bullet templates (placeholders must be replaced with real measured values, or the bullet reworded to avoid them):
- Built **TailorVoice**, an end-to-end ML system (Whisper ASR → DistilBERT NER → SBERT semantic matching → explainable scoring) that tailors resumes to job descriptions from voice or text input.
- Fine-tuned a DistilBERT NER model on **[N]** hand-annotated job descriptions, reaching **[F1]** entity-level F1 vs **[baseline F1]** for a dictionary baseline.
- Designed a faithfulness verifier (NLI + rule checks) that cut unsupported claims in rewritten bullets from **[x%]** to **[y%]** on a **[n]**-example stress set.
- Trained an explainable fit-score model (**[model]**, Spearman **[ρ]** vs human ratings) with SHAP-based reasons; deployed via FastAPI + React with p95 latency **[ms]**.

`student.md` section 0 must contain the matching interview script for each bullet.

---

## 15. Stretch goals (only after Phase 11, only if time permits)

- Fine-tune SBERT with contrastive loss; compare to off-the-shelf.
- Active learning loop for NER annotation (uncertainty sampling) and measure label-efficiency.
- Multilingual voice input (Hinglish) with WER evaluation.
- Fine-tune a small seq2seq model (e.g. t5-small / flan-t5-small) on verified (original, rewritten) pairs and compare with the Ollama model and the template rewriter.
- Simple bias/robustness audit (does score change with name, gender pronouns, college name? It should not).

---

## 16. Contents for `CLAUDE.md`

See `CLAUDE.md` in the repo root.

---

## 17. First instruction to give Claude Code

> Read `PROJECT_SPEC.md` and `CLAUDE.md` fully. Do **Phase 0 only**: create the project skeleton from Section 4, the Makefile, configs, local checks (no CI), the `student.md` skeleton from Section 13.2 with all headings present, and the docs check script. Do not run any git command. Confirm Python/uv setup works on my Mac. Then give me the Phase 0 summary in the format from Section 12 and stop. Do not start Phase 1 until I say "go".

---

## 18. Product behaviour carried over from my original 6-part prompts

Everything in this section is required in addition to Sections 1–17. Where it overlaps, this section adds the detail.

### 18.1 How to work with me (voice-first)
- I dictate my instructions, so keep explanations short and numbered and easy to follow when read aloud.
- When I must choose, give at most three options and recommend one.
- If my instruction is unclear, ask one short question before proceeding.
- Tell me in one line before changing anything from this spec, and wait for my answer.
- Wispr Flow dictation types into any active text field, so the app needs no speech engine for dictating text. TailorVoice's own Whisper stage is for uploaded or recorded audio. Both paths must work.

### 18.2 Dictation-friendly UI
- Large text areas with a visible word counter on each.
- No auto-format, auto-capitalise, or whitespace stripping of what is typed or dictated.
- Autosave every text area to local storage every few seconds, restore on reload.
- Keep focus in the text area after saving so dictation can continue.
- Visible warning when text nears the backend input limit.

### 18.3 Pages and behaviour
- **Profile:** basic details, education, skills, projects with bullet points, achievements. Add/remove items, clear Save button, saved confirmation.
- **Analyze:** big job-description text area, company name field, live word counter, Analyze button; extracted skills, tools and responsibilities shown as tags.
- **Results:** large score with ring or bar, score per category, matched items in green, missing items in amber each with a suggestion, plain-language explanation (plus SHAP reasons). Below: side-by-side original (left) and rewritten (right) bullets, with a label when a bullet was kept unchanged and why. Each rewrite has Accept, Keep original, and Edit.
- **History:** list with company, date, score; open one; delete with confirmation.
- Every action has loading, empty and error states with plain messages. Never show raw errors. Handle network failure, rate-limit and input-too-long cases clearly.
- When the system runs in fallback mode (Ollama not running or a model file missing), show a banner: "AI is offline, showing basic matching."
- Design: clean, calm, mobile friendly, one accent colour, generous spacing, large touch targets, simple top navigation, dark mode if cheap, accessibility basics (labels, keyboard navigation, contrast).
- Frontend reads the backend URL from a Vite env variable with a local default; include the proxy/CORS note for local development.

### 18.4 Backend requirements
- Settings from env vars (no secrets needed): `REWRITER_BACKEND` (`ollama` or `template`), `OLLAMA_HOST` (default `http://localhost:11434`), `OLLAMA_MODEL`, `WHISPER_MODEL_SIZE`, database URL, max input length, rate limit, allowed frontend origin. Sensible local defaults. CORS for the frontend origin only.
- If Ollama is not running or the chosen model is not pulled, the app still starts, switches to the `template` rewriter, and logs a clear warning.
- Simple in-memory per-IP rate limiting.
- Endpoint to delete all data for a profile (`DELETE /api/v1/profile/{id}/data`), with cascade delete across related tables.
- Never log resume text, job-description text, or personal details. Log only request path, status code, timing, and error type. Never return raw stack traces.
- Rewriting rules: every bullet under 25 words, starts with a strong verb, returns the index of its original bullet, adds no number, tool, or company name that is not in the profile. A bullet that fails the truthfulness check keeps the original and is marked unchanged with a reason.
- One command starts both frontend and backend locally.

### 18.5 PDF export
- One-page, single-column, ATS-friendly PDF from the accepted bullets: name and contact line, education, skills, projects with bullets, achievements. Standard font, simple headings, consistent spacing.
- Prefer a pure-Python library with no system dependencies; tell me which one and why.
- Overflow handling: reduce spacing slightly first, then trim the lowest-relevance items, and tell the user what was trimmed.
- Download PDF button on the Results and History pages, with loading and error states.

### 18.6 Error-handling pass (Phase 8, rechecked in Phase 11)
Check and fix each of these, then list what was checked and changed with file paths: empty profile, empty job description, extremely long job description, profile with no projects, model timeout, invalid model JSON, rate limit hit, profile deleted while on a page, backend down, plus bad audio and a missing NER or SBERT model file.

### 18.7 End-to-end test
One backend test with a mocked LLM and mocked Whisper that runs the full flow: create profile, analyze, match, tailor, export PDF, list history, delete. One command runs the whole test suite.

### 18.8 Deployment (prepare only, never execute)
- Provide the Dockerfile or start command, env var lists for backend and frontend, production CORS setup, and numbered manual deployment steps with the exact dashboard settings to type.
- Recommend one backend host and one frontend host in two lines. Prefer options that do not require GitHub; if the best option does require GitHub or any git push, say so and wait for me.
- Explain SQLite persistence on free tiers and what to do if the disk resets. Preload a sample profile so reviewers can try the app without typing.
- A health check URL I can open in a browser.
- Claude Code must not deploy, push, or upload anything itself.
- Free hosts usually cannot run a local LLM. The public demo therefore runs in **lite mode**: the `template` rewriter, with the lighter models (smaller Whisper or text-only input, MiniLM SBERT). Full mode (Ollama + everything) runs on my laptop and in the recorded demo video. Document both modes in the README and `student.md`.

### 18.9 Pre-launch checklist
Live link opens on mobile; sample profile preloaded; no secrets or personal data in the browser or logs; PDF downloads correctly; fallback banner appears and the template rewriter still works when Ollama is stopped.

### 18.10 Launch material (Phase 11), written in my voice: simple, honest, student-friendly, no hype
- Two-minute demo script with timestamps.
- README with the sections listed in the spec.
- About 250-word write-up with clearly marked blanks for real numbers. No invented results.
- LinkedIn post (short and detailed) plus one X post.
- Three honest resume bullets under 25 words each.
- A short list of what I must do manually.

---

## 19. Zero-cost setup (FREE EDITION)

### 19.1 What I install myself (all free)
- Python 3.11, `uv` or pip, Node 18+ (only if I keep the React frontend).
- **Ollama** (local model runner). Then I pull one small instruct model. Claude Code recommends a model for my Mac's RAM and verifies it exists with `ollama list` before using it. Prefer a ~3B-parameter model first.
- Optional: `ffmpeg`.
- No accounts, no API keys, no credit card.

### 19.2 Free model downloads (automatic, public)
Whisper (via `faster-whisper`), spaCy models, DistilBERT, `all-MiniLM-L6-v2`, and the small NLI cross-encoder are downloaded from Hugging Face. Public models need no account. Claude Code must report the total download size before downloading and wait for my OK.

### 19.3 Free compute
- Everything must run on my laptop CPU. Use small models, int8 where possible, small batch sizes, and cache embeddings.
- Optional free GPU (Colab/Kaggle) for NER training only. Only JD data may leave my laptop, never my profile, resume, or voice recordings.

### 19.4 Free hosting (optional, my decision, done manually)
- Lite mode only. I verify current free-tier limits myself.
- Fallback: README with screenshots + recorded demo video + one-command local run.

### 19.5 Honest consequences of going free (must appear in `student.md` section 12 and the README)
- Local small-model rewrites are lower quality, so the verifier rejects more rewrites. Reported as a measured rejection rate.
- The first run is slower on CPU. Report median and p95 latency per stage in lite and full mode.
- Never claim performance that was not measured in this free setup.
