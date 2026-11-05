# student.md — TailorVoice study guide

> **Living document.** Updated in the same working step as any code change that alters
> behaviour, structure, data flow, models, configs, or metrics. Plain language first,
> technical detail second. Real numbers only — unknown values are written `TBD`.
> Last updated: Phase 1 (2026-11-05).

---

## 0. 60-second pitch and 5-minute walkthrough script

**60-second pitch:** *TBD — written in Phase 11 once real numbers exist.*

**5-minute walkthrough script:** *TBD.*

Interview scripts for each resume bullet (Section 14 of the spec) go here, each tied to a
real measured number. *TBD until the evaluation phases run.*

---

## 1. Problem, users, and why ML (and where LLM is and isn't used)

**Problem.** Students tailoring a resume to each job description do it slowly and often
dishonestly (adding skills they don't have). TailorVoice reads a job description (typed or
dictated), works out what it asks for, compares that to a verified profile, scores the fit
with an explanation, and rewrites existing resume bullets to match the job — without ever
inventing experience.

**Users.** Me (Rashmi) first; students and early-career job seekers generally.

**Why ML, not a thin LLM wrapper.**
- **Extraction** (what the job asks for) is a trained NER model, with a dictionary and a
  spaCy baseline to compare against.
- **Matching** (profile evidence ↔ requirements) is TF-IDF and SBERT retrieval, evaluated.
- **Scoring** (0–100 fit) is a trained regression/boosting model vs a hand-weighted formula,
  evaluated against my own human ratings, with SHAP explanations.
- **Verification** (is a rewrite faithful?) is an NLI model plus rule checks, evaluated on a
  labelled faithful/unfaithful set.

**Where the LLM is used.** Only in the **rewriting** step (stage 8), via a small local model
through Ollama. A deterministic **template** rewriter is always available as a fallback, and
every rewrite must pass the faithfulness verifier (stage 9) or the original bullet is kept.

---

## 2. Big-picture architecture

### Pipeline (stage → input → output)
*Full per-stage input/output tables are filled as each stage is built. Current skeleton
mirrors Section 3 of `PROJECT_SPEC.md`:*

1. **ASR** — audio → transcript + confidence (Phase 6)
2. **JD preprocessing** — raw JD text → cleaned requirement sentences, section tags (Phase 2)
3. **NER extraction** — sentences → entities (SKILL/TOOL/RESPONSIBILITY/EXPERIENCE_LEVEL/EDUCATION) (Phases 2–3)
4. **Skill normalisation** — raw skill strings → canonical skills (Phase 4)
5. **Semantic matching** — requirement → best profile evidence (Phase 4)
6. **Scoring** — features → fit score 0–100 + SHAP reasons + gaps (Phase 5)
7. **Evidence selection** — rank profile bullets, pick top-k (Phase 7/8)
8. **Bullet rewriting** — original bullet + supported keywords → rewritten bullet (Phase 7)
9. **Faithfulness verifier** — (original, rewrite) → pass/fail + reason (Phase 7)
10. **Assembly + PDF + history** — accepted bullets → one-page PDF, SQLite history (Phase 8)

### One end-to-end worked example
*TBD — filled with a real JD snippet and every intermediate output once the pipeline runs
(Phase 8).*

---

## 3. Repository map

| Path | What it does | Key functions/classes | Who calls it | Phase added |
|---|---|---|---|---|
| `src/tailorvoice/__init__.py` | Package marker + version | — | — | 0 |
| `src/tailorvoice/asr/` | Whisper wrapper, audio validation | *TBD* | pipeline stage 1 | 6 |
| `src/tailorvoice/jd/schema.py` | Pydantic `JobDescription` record schema | `JobDescription` | corpus loader, API | 1 |
| `src/tailorvoice/jd/corpus.py` | Load + validate `data/raw/jd_*.json` | `load_jd()`, `load_corpus()`, `corpus_stats()` | `validate_data.py`, later stages | 1 |
| `src/tailorvoice/ner/` | EntityRuler baseline, BERT trainer, inference | *TBD* | pipeline stage 3 | 2–3 |
| `src/tailorvoice/skills/taxonomy.py` | Taxonomy schema + validated loader + exact alias lookup | `SkillEntry`, `Taxonomy`, `load_taxonomy()` | normaliser (Phase 4), `validate_data.py` | 1 |
| `src/tailorvoice/skills/` | (normalisation added in Phase 4) | *TBD* | pipeline stage 4 | 4 |
| `src/tailorvoice/matching/` | TF-IDF, SBERT, evidence retrieval | *TBD* | pipeline stage 5 | 4 |
| `src/tailorvoice/scoring/` | Feature builder, model, SHAP reasons | *TBD* | pipeline stage 6 | 5 |
| `src/tailorvoice/rewrite/` | Prompts, Ollama client, template rewriter | *TBD* | pipeline stage 8 | 7 |
| `src/tailorvoice/verify/` | NLI + rule faithfulness checks | *TBD* | pipeline stage 9 | 7 |
| `src/tailorvoice/pipeline.py` | Orchestrates stages 1–10 | *TBD* | API | 8 |
| `src/tailorvoice/api/` | FastAPI routes, schemas, deps | *TBD* | frontend | 8 |
| `src/tailorvoice/db/` | SQLAlchemy models | *TBD* | API | 8 |
| `src/tailorvoice/export/` | One-page PDF builder | *TBD* | API | 8 |
| `src/tailorvoice/config.py` | Loads YAML config + env settings | `load_config()`, `Settings` | everything | 0 |
| `scripts/check_student_md.py` | Docs self-check (Section 13.4) | `main()` | `make check-docs` | 0 |
| `scripts/validate_data.py` | Validate corpus + taxonomy, print stats | `main()` | `make data` | 1 |
| `scripts/collect_notes.md` | How the JD corpus was collected (honesty record) | — | humans | 1 |
| `docs/annotation_guidelines.md` | NER label definitions, edges, examples | — | annotation | 1 |
| `configs/label_studio_ner.xml` | Label Studio labelling interface for NER | — | Label Studio | 1 |
| `data/taxonomy/skills_taxonomy.json` | Taxonomy v0 (37 canonical skills) | — | `load_taxonomy()` | 1 |

*(Rows filled as each module is implemented. The docs check requires every `src/` directory
to appear here.)*

---

## 4. Data

- **Sources & collection method:** manual/semi-manual from public postings — full method in
  `scripts/collect_notes.md`. Each JD is one file `data/raw/jd_XXXX.json` validated against
  `JobDescription` (`src/tailorvoice/jd/schema.py`: id, title, company, text, source,
  collected_on, synthetic).
- **Sizes (actual at end of Phase 1):** JD corpus = **2** (both synthetic samples, **0 real
  yet**); target 300–500 real. NER annotated 0 (target ≥150); fit pairs 0 (~300); faithfulness
  set 0 (~150); ASR clips 0 (~30). Collecting/annotating is the manual work ahead.
- **Splits:** by job description, 70/15/15, stored in `data/splits/`. *Not created yet (needs
  a real corpus first — Phase 2/3.)*
- **Annotation guidelines summary:** 5 labels — SKILL, TOOL, RESPONSIBILITY, EXPERIENCE_LEVEL,
  EDUCATION — with a priority order (TOOL > EXPERIENCE_LEVEL > EDUCATION > SKILL >
  RESPONSIBILITY) and tightest-span rule. Full doc: `docs/annotation_guidelines.md`. Labelling
  uses `configs/label_studio_ner.xml` in Label Studio.
- **Inter-annotator agreement (self, Cohen's kappa):** *TBD — measured after labelling (re-label
  a 20-JD subset ~1 week later).*
- **Taxonomy:** `data/taxonomy/skills_taxonomy.json` v0 = **37 canonical skills, 79 aliases**
  across language/framework/ml/cloud/database/tool/soft_skill. Loader `load_taxonomy()`
  validates it and rejects an alias that maps to two canonicals.
- **Rating rubric:** *TBD (Phase 5)* — `docs/rating_rubric.md` written when scoring pairs are built.
- **Synthetic data disclosure:** the 2 sample JDs carry `synthetic: true` / source
  `synthetic-sample` and are excluded from the real count. 3–4 synthetic persona profiles for
  fit pairs come in Phase 5, also marked synthetic. My real profile stays in `data/private/` only.
- **Data versions and how to regenerate:** `make data` loads + validates and prints the stats
  above. Taxonomy version string is `v0-2026-11-05`.

---

## 5. Each ML component

> Template per component: problem it solves · input/output schema + example · algorithm +
> the math that matters · why this over alternatives · training/inference details
> (hyperparameters, seed, hardware, time) · metrics (table + run ID) vs baselines · failure
> modes / error analysis · code pointers · "how to explain this in an interview".

### 5.1 ASR — *TBD (Phase 6)*
### 5.2 JD preprocessing — *TBD (Phase 2)*
### 5.3 NER (requirement extraction) — *TBD (Phases 2–3)*
### 5.4 Skill normalisation — *TBD (Phase 4)*
### 5.5 Semantic matching — *TBD (Phase 4)*
### 5.6 Scoring + SHAP — *TBD (Phase 5)*
### 5.7 Evidence selection — *TBD (Phase 7/8)*
### 5.8 Bullet rewriting — *TBD (Phase 7)*
### 5.9 Faithfulness verifier — *TBD (Phase 7)*

---

## 6. Backend, API and database

- **Endpoint table, request/response examples:** *TBD (Phase 8)* — endpoints listed in
  Section 8 of `PROJECT_SPEC.md`.
- **DB tables:** *TBD (Phase 8)*.
- **Sequence of a request:** *TBD (Phase 8)*.

---

## 7. Frontend

- **Pages:** Profile, New Tailoring (Analyze → Results), History, "How it works". *TBD (Phase 9)*.
- **State flow and which API each page calls:** *TBD (Phase 9)*.

---

## 8. Experiments and results

- **Experiment tracker:** local `experiments/*.json` log (chosen in Phase 0 — see Decision
  Log). Each run records config, seed, data version, a code-content hash, and metrics.
- **Experiment log (run ID | date | change | metric | decision):** *TBD — first real runs in Phase 2.*
- **Ablation summary:** *TBD.*
- Result tables live in `RESULTS.md`, regenerated by `make eval`, never typed by hand.

---

## 9. Testing and quality

- `make test` — pytest. `make lint` — ruff. `make typecheck` — mypy (lenient).
  `make check-docs` — `scripts/check_student_md.py`. `make check` — all of the above.
- **What each test file covers:** `tests/test_smoke.py` — package imports and config load
  (Phase 0). More per-stage tests added each phase.
- **Known gaps:** heavy ML dependencies and models are installed in later phases; Phase 0
  tests cover only scaffolding.

---

## 10. Deployment and operations

- **How to run locally:** `make setup` then (later phases) `make run`. *Full steps TBD.*
- **Env vars:** see `.env.example` (`REWRITER_BACKEND`, `OLLAMA_HOST`, `OLLAMA_MODEL`,
  `WHISPER_MODEL_SIZE`, `DATABASE_URL`, `MAX_INPUT_CHARS`, `RATE_LIMIT_PER_MIN`,
  `FRONTEND_ORIGIN`).
- **Docker:** single `Dockerfile` (filled in Phase 10).
- **Hosting:** lite mode only, decided and done manually by me in Phase 10. *TBD.*
- **Health checks:** `GET /api/v1/health` (Phase 8).
- **Costs:** zero — all local, free, open-source models (Section 19 of spec).
- **Lite vs full mode:** full mode (Ollama + all models) runs on my laptop; lite mode
  (template rewriter, MiniLM, smaller Whisper) is for any free public demo. *Detail TBD.*

---

## 11. Decision log

| Date | Decision | Alternatives | Reason | Consequences |
|---|---|---|---|---|
| 2026-11-05 | Experiment tracker = local `experiments/*.json` log | MLflow local file store | Zero extra dependency, trivially readable on a CPU laptop, no server to run; fits the zero-cost rule | Must hand-write a tiny logging helper; no MLflow UI (acceptable) |
| 2026-11-05 | `uv`-managed Python 3.11 (not system 3.14) | System Python 3.14 | spaCy/torch/faster-whisper wheels are not reliably available for 3.14; spec pins 3.11 | Interpreter managed in `.venv` via uv; reproducible |
| 2026-11-05 | Tracker confirmed = `experiments/*.json` (kept) | MLflow | Confirmed by Rashmi; zero dependency | No MLflow UI (acceptable) |
| 2026-11-05 | Frontend: plan **Streamlit as default**, final call deferred to Phase 9 | React+Vite+TS | Rashmi's choice; Streamlit is faster to build and demo for a solo student, no Node build step | API must stay framework-agnostic so either frontend can call it; React remains possible in Phase 9 |
| 2026-11-05 | JD stored as one JSON file per posting, validated by Pydantic on load | Single CSV/JSONL corpus | Easy to add/edit one posting by hand; a bad file fails loudly and names itself | Many small files (fine at v1 scale) |

---

## 12. Limitations, risks, and honest caveats

- Small, self-annotated dataset → my own annotation bias; inter-annotator agreement is
  *self*-agreement, not multi-person.
- Synthetic persona profiles are used for scoring pairs and are clearly marked synthetic.
- **Zero-cost consequences:** local small-model rewrites are lower quality than a large
  hosted model, so the verifier rejects more rewrites — reported as a measured rejection
  rate, never hidden. First run on CPU is slow; latency is reported as median and p95 per
  stage in both lite and full mode.
- No performance is claimed that was not measured in this free setup.
- *More caveats added as real results arrive.*

---

## 13. Glossary

- **WER** — Word Error Rate: fraction of words wrong in a transcript vs ground truth. *More detail as ASR is built.*
- **NER** — Named Entity Recognition: labelling spans of text (here: SKILL, TOOL, etc.).
- **BIO** — tagging scheme: Begin / Inside / Outside of an entity span.
- **SBERT** — Sentence-BERT: a model that turns a sentence into a vector for similarity.
- **Cosine similarity** — angle-based similarity between two vectors (1 = identical direction).
- **TF-IDF** — term-frequency × inverse-document-frequency: classic sparse text vector.
- **NLI** — Natural Language Inference: does sentence A entail / contradict / stay neutral to B.
- **SHAP** — Shapley-value feature attributions: how much each feature pushed a prediction.
- **MRR** — Mean Reciprocal Rank: average of 1/(rank of first correct hit).
- **nDCG** — normalised Discounted Cumulative Gain: ranking quality with position discount.
- **Calibration** — mapping raw model output to a meaningful scale (here 0–100).
- **Cohen's kappa** — agreement between two labellings corrected for chance agreement
  (1 = perfect, 0 = chance). Used here for *self*-agreement on re-annotated JDs.
- **Taxonomy** — our curated list of canonical skill names, each with aliases and a category.
- **Alias** — a surface spelling that maps to a canonical skill (e.g. `k8s` → `Kubernetes`).
- **Canonical name** — the single agreed spelling of a skill that everything normalises to.
- **Span** — a contiguous stretch of characters/tokens that an entity label covers.
- *(Extended each phase.)*

---

## 14. Viva / interview Q&A

> Grows every phase; target ≥ 40 questions by the end, each with a model answer.

1. **Q: Is this just an LLM wrapper?**
   A: No. Extraction, matching, scoring and verification are each trained/classical ML with
   evaluated baselines. The LLM only rephrases existing bullets, and every rephrase must pass
   a faithfulness verifier or the original is kept.
2. **Q: How do you stop it inventing experience?**
   A: The rewriter is only given facts from the profile; the verifier checks NLI entailment
   plus number/tool rules; failures fall back to the original bullet.
3. **Q: Why split data by job description, not by sentence?**
   A: To prevent leakage — sentences from the same JD are correlated, so splitting by JD keeps
   train and test genuinely independent.
4. **Q: Why keep both a template rewriter and an LLM rewriter?**
   A: The template rewriter is faithful by construction and always available (zero cost, no
   model); the LLM gives more natural phrasing when Ollama is running. We measure the LLM's
   rejection rate honestly.
5. **Q: What does "zero cost" change about your results?**
   A: Smaller local models mean more verifier rejections and slower CPU latency; both are
   measured and reported, never hidden.
6. **Q: Why have a skills taxonomy at all — why not just string-match?**
   A: The same skill appears many ways (`pytorch`, `py torch`, `torch`). The taxonomy maps all
   of these to one canonical name so matching and scoring count them once. It is the backbone
   for the dictionary NER baseline and for skill normalisation.
7. **Q: How do you stop one alias meaning two different skills?**
   A: `load_taxonomy()` builds a surface→canonical index and raises if any alias maps to two
   canonicals, so the data can't silently become ambiguous.
8. **Q: Why split JD data by job description instead of randomly by sentence (again, concretely)?**
   A: Sentences from one posting share wording and style; random sentence splits would leak
   that style into the test set and inflate scores. Splitting whole JDs keeps test postings
   genuinely unseen.
9. **Q: Your corpus has 2 JDs — isn't that nothing?**
   A: Phase 1 only builds the *machinery* (schema, loader, taxonomy, guidelines) and ships 2
   synthetic samples to exercise it. Collecting 300–500 real postings is the manual data work
   that follows; the count is reported honestly as 0 real so far.
10. **Q: What are your five NER labels and the tie-break rule?**
    A: SKILL, TOOL, RESPONSIBILITY, EXPERIENCE_LEVEL, EDUCATION. When a span could be two, the
    priority is TOOL > EXPERIENCE_LEVEL > EDUCATION > SKILL > RESPONSIBILITY — named tools and
    hard requirements are the least ambiguous and most useful for matching.

---

## 15. "Things I should be able to explain" checklist

- [ ] The full pipeline, stage by stage, with one worked example
- [ ] Why each stage has a non-LLM baseline and how it scored vs the main model
- [ ] How the faithfulness verifier works and what it catches
- [ ] How the fit score is computed and explained (SHAP)
- [ ] The data: sizes, splits, annotation, agreement, synthetic disclosure
- [ ] Every metric in RESULTS.md and the run that produced it
- [ ] How to run and reproduce everything from scratch
- *(Ticked as I confirm understanding.)*

---

## 16. Phase changelog (newest first)

### Phase 1 — Data foundations (2026-11-05)
- Added JD record schema (`src/tailorvoice/jd/schema.py`) and corpus loader
  (`src/tailorvoice/jd/corpus.py`: `load_jd`, `load_corpus`, `corpus_stats`) with validation
  and duplicate-id detection.
- Added skills taxonomy schema + loader (`src/tailorvoice/skills/taxonomy.py`) and a v0
  taxonomy of 37 canonical skills / 79 aliases (`data/taxonomy/skills_taxonomy.json`).
- Wrote `docs/annotation_guidelines.md` (5 labels, priority order, worked examples),
  `scripts/collect_notes.md`, and `configs/label_studio_ner.xml`.
- Added `scripts/validate_data.py` wired to `make data`; shipped 2 synthetic sample JDs
  (flagged `synthetic: true`).
- Decisions: kept the JSON tracker; planned Streamlit as the default frontend (final call in
  Phase 9). Added tests `tests/test_jd_corpus.py`, `tests/test_taxonomy.py` (12 tests total).
- `make data` and `make check` both green. No git, no paid services, no model downloads.

### Phase 0 — Setup (2026-11-05)
- Created project skeleton (Section 4 of spec), Makefile, YAML configs, `.env.example`,
  `config.py` (settings + config loader), `experiments/` JSON tracker helper,
  `scripts/check_student_md.py` docs check, smoke test, this `student.md` skeleton.
- Chose Python 3.11 via `uv` and `experiments/*.json` as the tracker.
- No git used. No ML models downloaded yet (deferred to the phases that need them).

---

## 17. How to reproduce everything from scratch

```bash
# 1. Install uv (https://docs.astral.sh/uv/) and Ollama (https://ollama.com) — free, no account.
# 2. From the project root:
make setup        # creates .venv with Python 3.11 and installs dependencies
make test         # Phase 0: smoke tests pass
make data         # Phase 1: validate JD corpus + taxonomy, print stats

# Later phases add:
# make train-ner   # train the NER model (Phase 3)
# make eval        # run all evaluations and regenerate RESULTS.md
# make run         # start backend + frontend locally (Phase 8+)
```
*(Commands are verified to run at the end of each phase; later targets are stubs until their
phase.)*
