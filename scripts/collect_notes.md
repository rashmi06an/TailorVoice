# JD Collection Notes — TailorVoice

Honest record of how the job-description corpus was built (PROJECT_SPEC.md Section 5.1). This
file is the source of truth for the "Data" section of `student.md` and `RESULTS.md`.

## Target
300–500 public postings across tech/ML/SDE/product/consulting-adjacent roles.
**Current real count: 0** (only 2 synthetic samples exist so far — see below).

## Method (manual / semi-manual)
1. Find a public job posting. Copy the posting text (no login-walled or paywalled content).
2. Create `data/raw/jd_XXXX.json` with fields: `id`, `title`, `company`, `text`, `source`,
   `collected_on`, and `synthetic: false` for real postings.
3. `id` = the filename stem, zero-padded (`jd_0001`, `jd_0002`, …).
4. `source` = the URL or site name. `collected_on` = today's date (YYYY-MM-DD).
5. Validate with `make data` (runs the loader + schema check and prints corpus stats).

## Legal / terms
- Only public postings. Respect each site's terms of service.
- **If redistribution is unclear, keep the raw text out of any shared output** — ship only the
  ids and my own annotations. `data/raw/` is git-ignored by default.
- Never include personal data of other people.

## Synthetic samples (not counted as real data)
- `jd_sample_0001.json`, `jd_sample_0002.json` are hand-written demo postings with
  `synthetic: true` and `source: "synthetic-sample"`. They exist so the loader, schema, and
  tests have something to run against. They are excluded from the real corpus count and marked
  synthetic in every report.

## De-duplication
The loader rejects duplicate `id`s. Near-duplicate postings (same role reposted) should be
noted here and, if kept, split into the same train/val/test bucket by company to avoid leakage
(Section 5.2 / rule 5).
