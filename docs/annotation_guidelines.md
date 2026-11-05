# NER Annotation Guidelines — TailorVoice

Written **before** labelling (PROJECT_SPEC.md Section 5.2). Label spans in Label Studio using
`configs/label_studio_ner.xml`. Five labels, BIO applied automatically by the training export.

Golden rule: **label what the job asks for**, as written. Do not infer skills that are only
implied. When unsure between two labels, follow the priority order in §6 and note the case.

---

## 1. SKILL
A general capability, technology family, or method the candidate is expected to know.
- **Include:** `Python`, `machine learning`, `NLP`, `data structures`, `REST APIs`,
  `distributed systems`, `deep learning`.
- **Exclude:** a specific named product/tool (that is TOOL), a duty (that is RESPONSIBILITY).
- **Edge:** "experience with Python" → label only `Python` as SKILL (the surrounding words are
  not part of the span). "machine learning models" → `machine learning` is SKILL.

## 2. TOOL
A specific named product, framework, library, platform, or service.
- **Include:** `PyTorch`, `TensorFlow`, `FastAPI`, `Docker`, `Kubernetes`, `AWS`,
  `PostgreSQL`, `Git`, `Hugging Face Transformers`.
- **Border with SKILL:** if it is a *named product you could install or sign up for*, it is a
  TOOL; if it is a *field or capability*, it is a SKILL. `SQL` (the language) = SKILL;
  `PostgreSQL` (the product) = TOOL.

## 3. RESPONSIBILITY
A duty or activity the role performs (usually a verb phrase).
- **Include:** `build and evaluate ML models`, `ship features to production`,
  `write tests`, `collaborate with product teams`.
- **Span:** label the concise action phrase, not the whole sentence or leading bullet marker.

## 4. EXPERIENCE_LEVEL
An explicit experience/seniority requirement.
- **Include:** `2+ years`, `3-5 years of experience`, `senior`, `new grad`, `entry level`,
  `internship`.
- **Exclude:** vague adjectives like "strong" or "solid" on their own.

## 5. EDUCATION
A degree, field of study, or academic requirement.
- **Include:** `Bachelor's degree`, `BS in Computer Science`, `Master's`, `PhD`,
  `degree in a related field`.

---

## 6. Priority order (when a span could fit two labels)
TOOL > EXPERIENCE_LEVEL > EDUCATION > SKILL > RESPONSIBILITY.
Rationale: named tools and hard requirements (experience/education) are the most unambiguous
and most load-bearing for matching; SKILL and RESPONSIBILITY are broader catch-alls.

## 7. Span conventions
- Do not include leading `-`, `•`, numbering, or trailing punctuation.
- Label the **tightest** span that carries the meaning (`Python`, not `experience with Python`).
- Label each occurrence; do not merge two skills joined by "and" into one span
  (`PyTorch or TensorFlow` → two TOOL spans).
- Down-weighted sections ("About us") are usually not labelled unless they state a real
  requirement.

## 8. Worked examples
From `data/raw/jd_sample_0001.json`:
- "Bachelor's degree in Computer Science" → `Bachelor's degree` (EDUCATION),
  `Computer Science` (SKILL/field — label EDUCATION field as part of the degree span if
  contiguous, else SKILL; see §6, prefer keeping the degree phrase as one EDUCATION span).
- "experience with PyTorch or TensorFlow" → `PyTorch` (TOOL), `TensorFlow` (TOOL).
- "Build and evaluate ML models" → `Build and evaluate ML models` (RESPONSIBILITY);
  `ML` within it is not separately labelled (avoid overlapping spans).
- "Comfortable with Git and Linux" → `Git` (TOOL), `Linux` (TOOL).

## 9. Inter-annotator / self-agreement
Re-annotate a 20-JD subset after ~1 week and compute Cohen's kappa (self-agreement). Record
the number and date in `student.md` §4 and `RESULTS.md`. Do not fabricate it.

## 10. Pre-labelling disclosure
If a local Ollama model is used to pre-fill spans to speed up labelling, **every span must be
reviewed by hand**, and `student.md` must state that pre-labelling was used. Never use a paid
or third-party API for pre-labelling.
