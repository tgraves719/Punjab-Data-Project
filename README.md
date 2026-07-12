# Punjab Data Project

**A computational sociological analysis of British Punjab through the imperial print register, 1867–1942.**
Thomas Graves, with Prof. Emmett Davis.

## The live explorer

**→ https://www.mixedrealitymusician.com/Punjab-Data-Project/** *(GitHub Pages, served from `docs/`)*

An interactive explorer of the complete year **1910**: all four quarterly
*Catalogues of Books registered in the Punjab* under Act XXV of 1867 and Act X
of 1890 — **1,408 entries, 1,960,018 registered copies** (India Office SV 412/44).
Filterable entry table, printer–publisher network, script-market analysis,
curated exhibits, and a built-in scan viewer that opens every record's source
page image.

## What this repo contains

| Path | Contents |
|---|---|
| `docs/` | The published site: the self-contained explorer (`index.html`) plus the rendered page scans (`pages/<quarter>/`) it links to |
| `pipeline/` | Extraction pipeline: `render.py` → per-page extraction JSONs → `postprocess.py` (normalization, SQLite) → `validate.py` (sequence checks, adjudication queues); `schema.md`, `aliases.json`, per-quarter manifests |
| `pipeline/data/<quarter>/extractions/` | The verbatim record layer: one JSON per catalog page, the catalog's own words preserved (misprints, editorializing and all) |
| `pipeline/data/<quarter>/out/` | Derived open data: `entries.csv`, `adjudication_queue.csv`, `validation_report.md` |
| `pipeline/data/<quarter>/marginalia_*.md` | Documentation of the handwritten verso indexes found in the bound volumes |
| `analysis/slice_1910/` | Analysis scripts over the year: `build_network.py`, `script_market.py`, `build_site.py` (regenerates `docs/index.html`), with CSV/PNG outputs in `out/` |
| `PLAN.md` / `DECISIONS.md` | Plan of record and the numbered decision log (D-001…) governing every normalization fold and method choice |

## Method in one paragraph

Three layers, kept separate: **page image → verbatim record → normalized layer.**
Every entry carries full provenance (printed page + PDF page); the catalog's
wording is never silently corrected — uncertain readings are flagged into
per-quarter adjudication queues with stated reasoning. Registration numbers run
as one annual sequence (1–1410 in 1910) and serial numbers chain across quarters
within each language–topic section; both are used as validation instruments.

## What is deliberately not here

- The bound-volume scans (~25 GB of India Office PDFs) — only the per-page PNG
  renders needed by the explorer are published, under `docs/pages/`.
- The SQLite database (`punjab.db`) — regenerable:
  `cd pipeline && python postprocess.py manifest_1910Q1.json` (repeat per quarter).
- Private working material (interpretive memos, collaborator transcription files).

## Rebuilding the site

```
cd pipeline
python postprocess.py manifest_1910Q1.json   # …Q2, Q3, Q4: rebuilds punjab.db
cd ../analysis/slice_1910
python build_network.py && python script_market.py
python build_site.py --public               # web build: no local-path PDF links
cp out/explore_1910.html ../../docs/index.html
python build_site.py                        # local build (with PDF deep-links)
```

## Source

*Catalogue of Books registered in the Punjab under Act XXV of 1867 and Act X of
1890*, quarterly, British Library India Office Records SV 412/44. Public-domain
government record. Print runs measure publisher supply decisions under a
legal-deposit regime — not readership, not literacy.
