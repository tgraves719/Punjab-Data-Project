# Punjab Catalog Extraction Pipeline

Turns scanned quarterly catalogs (SV 412/44, Punjab 1867–1942) into a three-layer
structured dataset: **page image → verbatim imperial record → normalized layer**.
The verbatim layer preserves the catalog's own categories, spellings, and glosses;
normalization is our act and is kept separate and inspectable.

Project direction lives in [../PLAN.md](../PLAN.md); every normalization and
methodology decision is logged in [../DECISIONS.md](../DECISIONS.md). Analyses
built on the database live in `../analysis/` (first: `slice_1910/`).

## Stages

1. **render.py** — renders PDF pages to grayscale PNGs per a quarter manifest.
   `python render.py manifest_1910Q2.json`
2. **extract** — one page image → one JSON file of entries (schema in `schema.md`).
   Two interchangeable backends:
   - *In-session*: Claude (in Claude Code) reads each page and writes
     `data/<quarter>/extractions/p<printed>.json` directly.
   - *API*: `python extract_api.py manifest_1910Q2.json` — requires
     `ANTHROPIC_API_KEY`; resumable (skips pages already extracted). Untested
     until a key is available.
3. **postprocess.py** — merges page JSONs; carries section headers, resolves
   "Ditto" printers, computes page-sum from verbatim pagination, applies the
   alias table (`aliases.json`) plus deterministic folds (accent-strip, trailing
   "city" removal — DECISIONS.md D-008) to produce normalized fields, including
   `norm_lang` (canonical language categories; "Periodicals X" folds to "X") and
   `periodical` (from the PERIODICALS section prefix). Writes
   `data/<quarter>/out/entries.csv` and appends to `punjab.db` (SQLite).
   `python postprocess.py manifest_1910Q2.json`
   *Schema note:* adding a normalized column requires dropping the `entries`
   table and re-running postprocess for every loaded quarter.
4. **validate.py** — internal consistency checks (serial monotonicity,
   registration-number collisions, vocabulary membership) plus field-by-field
   diff against Davis's transcription sheets where they overlap. Writes
   `data/<quarter>/out/adjudication_queue.csv` and `validation_report.md`.
   `python validate.py manifest_1910Q2.json`

## Ground rules (do not relax)

- Never edit the verbatim fields to "fix" the catalog; corrections live in the
  normalized fields or the adjudication queue.
- Every entry records `pdf_page` + `printed_page` — full provenance to the scan.
- Uncertain readings (degraded digits, ink loss) go in `flags`, never silently
  guessed. Flagged fields feed the adjudication queue.
- Davis's sheets are cross-validation, not gold: disagreements are adjudicated
  against the page image, both sources correctable.

## Dependencies

`pip install pymupdf openpyxl anthropic` (anthropic only for the API backend).
