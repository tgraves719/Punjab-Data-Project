# Punjab Data Project — Plan of Record

*Maintained by: Thomas Graves + Claude (pipeline sessions), for the joint project with
Prof. Emmett Davis. Last updated: 2026-07-16.*

This is the governing document for direction and scope. Decisions with rationale live
in [DECISIONS.md](DECISIONS.md); pipeline mechanics in [pipeline/README.md](pipeline/README.md);
extraction schema in [pipeline/schema.md](pipeline/schema.md).

---

## 1. Research questions (fixed)

1. **Homogenization dynamics** (Davis): how a millennia-diverse region violently
   discarded cultural diversity by Partition — "the poverty of homogeneity."
2. **Knowledge processes in empire** (Davis): creation/dissemination of knowledge,
   esp. STEM and vernacular publishing in Western Punjab; networks of authors,
   publishers, printers, schools, discourse communities.
3. **Second-order observation of the imperial catalog** (Thomas): the registry is not
   a window but an *observation operator* — model the observing apparatus itself
   (classifications, glosses, editorializing, the Reporter on Books as actor).
   Lifeworld-colonization / FEP framing held loosely; data leads.

## 2. Current state (as of 2026-07-16)

| Asset | Status |
|---|---|
| **Corpus in punjab.db** | **4,502 entries, 6,944,051 copies — three complete years (1910: 1,408 / 1911: 1,562 / 1912: 1,532), the full SV_412_44_1910-1912 volume.** Twelve quarters, each with manifest → render → extract → postprocess → validate complete. |
| Extraction backends | 1910 in-session (golden set); **1911–1912 via Batch API with claude-opus-4-8**, chosen by a scored bake-off against the 1910Q2 golden quarter (D-015: reg recall 1.000, ~$2/quarter batched; Haiku rejected as false economy). Cost so far ≈ $22 incl. bake-off. |
| Validation | Annual reg sequences: 1910 1–1410, 1911 1–1565 (111 gaps, 17 collisions), 1912 1–1532 (42 gaps, 19 collisions). Adjudication queues total ~986 items across the twelve quarters — mostly print-defect flags, all faithful-to-print on spot-checks. |
| Normalization | aliases.json lang table extended +59 entries across 1911–1912 ingestion (dash-compounds, Panjabi/Pashtu spellings, 'Hindi & Sanskrit' etc.); 4+-language polyglots left verbatim pending a D-008 rule extension — ask Davis. |
| Prior-hand marginalia | Now documented across the whole volume: index leaves at nearly every quarter's end, once bound *inside* a quarter (1911Q1, pdf 237 — shifts the page offset mid-quarter), once on the volume's last leaf (pdf 607). Scripture-serial tracking runs continuously 1910→1912 (Arsh Granthawali II→VIII, Rig Veda 37→74). |
| Explorer | `build_site.py` generalized to every year in the DB (D-012 update, 2026-07-15) → `explore_1910_1912.html` (2.5 MB); deployed as the docs/ site with 1911–1912 scans as web JPEGs. Single-year explore_1910.html preserved. |
| Later volumes | The full 1867–1942 run is on disk under Library 1/Batch 6 (incl. 1913-1915, 1916-1917, 1918-19 for finishing the decade). |

### 2b. Superseded snapshot (2026-07-09, end of the 1910 slice)

| Asset | Status |
|---|---|
| 1910Q1 (March) | **Extracted, validated (2026-07-09): 382 entries.** Quarter ending 31 March 1910; front of the 1910-1912 volume, doc index 2–51 (printed pp. 2–51, offset 0) + prior-hand verso index at doc[52]; regs ~1–383. 16-item queue, all catalog artifacts (2 reg collisions, a printed reg-570 anomaly, cross-section serial resets from the periodical groupings) — no transcription errors; all three outlier suspects (copies 30,000; reg 570; reg 326 dup) verified against page images and confirmed faithful to the original. Prior-hand verso index documented in [data/1910Q1/marginalia_p052.md](pipeline/data/1910Q1/marginalia_p052.md). |
| 1910Q2 (June) | Extracted, validated: 321 entries; cross-checked against Davis sheet (304/320 matched) |
| 1910Q3 (Sept) | Extracted, validated: 423 entries; no Davis sheet; 55-item adjudication queue |
| 1910Q4 (Dec) | Extracted, validated: 282 entries; 38-item queue, all documented flags |
| **Year 1910** | **COMPLETE — all four quarters: 1,408 entries, 1,960,018 copies. Closes the annual registration sequence (regs ~1–1410, a handful of collisions/gaps). By entries: Q3 423 > Q1 382 > Q2 321 > Q4 282.** |
| punjab.db | SQLite (project root), all four quarters loaded (1,408 rows); verbatim + normalized layers |
| Prior-hand marginalia | Documented: pencil X-marks, running numerals, multi-part verso indexes (Q1 doc[52], Q3 p058, Q4 p038). **NOT Davis's** — confirmed with him (2026-07-09) the marks predate his acquisition; an unidentified earlier hand. Tracking retained; provenance/meaning open. |
| extract_api.py | Written, untested (no ANTHROPIC_API_KEY yet) |

## 3. Direction decision

**Build a vertical slice on the completed year 1910 before scaling extraction.**
Rationale (see [DECISIONS.md](DECISIONS.md) D-007): a full year is the source's natural
closed unit (annual registration sequence, cross-quarter serial chains, signed off
Feb 1911); aggregation has already exposed normalization debt that must be fixed
before it is baked into ~40 more quarters; and the slice is the artifact that makes
the project legible to Davis, libraries, and funders. Extraction resumes after the
slice, optionally via the API-batch path once the schema is validated.

## 4. Vertical slice — workstreams and acceptance criteria

### S1. Normalization pass (foundation for S2–S4)
- Extend `aliases.json` with a `lang` table; canonicalize bilingual/trilingual
  naming variants introduced across extraction sessions.
- Add deterministic city folding (accent-strip, trailing "city" removal) ahead of
  alias lookup, per the "aliases + deterministic rules" policy.
- Add derived columns: `norm_lang`, `periodical` (from section prefix).
- Rebuild `punjab.db` (drop + re-run all three quarters) and re-validate.
- **Done when:** year-level `norm_lang` GROUP BY shows one row per real category;
  city top-10 has no case/accent duplicates; all three validation reports unchanged
  or improved.

### S2. Printer–publisher network (1910)
- `analysis/slice_1910/build_network.py` → bipartite edge list (norm_printer ↔
  norm_publisher) weighted by entry count and total copies; node list with
  degree/weighted degree; author top-list. CSV outputs (Gephi-importable).
- **Done when:** edge/node CSVs exist, top-20 table reproduced in the memo, and at
  least one substantive observation documented (e.g., cross-communal brokerage).

### S3. Script-market comparison (1910)
- `analysis/slice_1910/script_market.py` → (a) language × entries/copies/mean-run/
  free%/educ% table; (b) the three-script Relief Fund circular series as the
  controlled comparison; (c) same-text-multiple-scripts exhibit list.
- **Done when:** CSV + summary tables exist and the script-hierarchy claim is stated
  with its precise evidentiary scope (registered print runs ≠ readership).

### S4. Memo to Davis
- `analysis/slice_1910/davis_memo_1910.md`: the year in numbers, the network, the
  script market, exhibit pieces (Reporter-on-Books self-registration; music triangle;
  polemic ring; pan-Islamic translations; canon formation), data-quality statement,
  the marginalia questions for Davis, and proposed next steps.
- **Done when:** memo is self-contained (readable without this repo), cites
  quarter/page/serial for every claim, and lists the open questions for Davis.

### S5. Interactive explorer (added 2026-07-08 at Thomas's request; D-012, D-013)
- `analysis/slice_1910/build_site.py` → `out/explore_1910.html`: single
  self-contained file (no server, no internet) — overview dashboard, filterable
  full-record table, network canvas, script-market view, exhibits, method notes.
- Source linking (D-013): each record's detail panel opens its scanned page in a
  built-in viewer (arrow-key paging, zoom; packaged path → repo path fallback) and
  deep-links the PDF volume at the exact page. `--package` bundles the ~145 MB of
  page scans into out/ for a zippable Davis package.
- **Done when:** opens by double-click, all tabs functional, no console errors,
  every record shows verbatim fields + flags + marginalia, exhibits cross-link
  into the filtered table, and any record can be traced to its source pixels in
  two clicks. ✅ Verified 2026-07-08 (scan viewer fallback + paging + PDF href
  checked in live browser).

## 5. After the slice — updated sequence (2026-07-16)

Items 2–3 of the original list are DONE (API-batch decided by bake-off, D-015;
1911 and 1912 ingested). Current queue:

1. **Finish the 1910s decade:** 1913–1915 volume next (SV_412_44_1913-1915.pdf on
   disk); map quarter boundaries by probe-render (watch for inserted prior-hand
   leaves and unnumbered first pages — both occurred in this volume), then the
   standard per-quarter pipeline. Keep extending aliases.json per year at ingestion.
2. **Adjudication session(s):** ~986 queued items across twelve quarters. Priorities:
   the reg collisions and serial jumps (validation instruments), then the flagged
   digits. 1910's queues are triaged; 1911–1912's are not.
3. **Davis meeting:** marginalia provenance (the hand now demonstrably spans the whole
   1910-1912 volume, tracking scripture serials to the last leaf); the three 4+-language
   polyglot lang values needing a canonical rule; xlsx reconciliation for 1920/1930/1940.
4. **Aggregates layer** (see §8): emit per-quarter aggregate counts from postprocess —
   the data contract for time-dynamics views; cheap now, costly to retrofit.

## 8. Scaling & observatory roadmap (added 2026-07-16)

The system has exactly one scaling cliff: the explorer embeds all entries as JSON in
one HTML file (2.5 MB at 3 years; dead by ~15–20k entries ≈ end of the 1910s).
Everything else (SQLite, per-quarter pipeline, manifests) scales to the full
1867–1942 corpus (~60–80k entries) unchanged.

- **Now, per-year habits (compound with data):** extend entity aliases at each
  ingestion (drift is real: +59 lang aliases in two years; printers/publishers will
  be worse — D-010's year-scoping warning stands); emit per-quarter aggregates
  (norm_lang × topic × city × printer counts/copies — a few hundred KB for the whole
  corpus) so time-dynamics views never need full records up front.
- **At decade completion (~1919):** split the explorer into a static shell + per-year
  gzipped JSON shards, lazy-loaded; first real time-dynamics tab built on the
  aggregates; single-file builds remain as year-slice exports for emailing.
  Still no server — static files on Pages preserve the archive-stability guarantee
  (D-009/D-012) and never strain at this corpus size.
- **Scans on the web:** full-corpus PNGs ≈ 7 GB, over the Pages budget. Convention
  from 2026-07-16: post-1910 quarters deploy as **web-compressed JPEGs (~150 KB/page,
  quality 55)** in docs/pages/ — the scan viewer tries .png, then .jpg, then the
  repo-relative path. 1910's PNGs stay as deployed. Revisit object storage if/when
  the site nears the 1 GB Pages ceiling.
- **Probably never:** a server-side backend. Reconsider only for corpus-wide
  full-text search over glosses.

## 6. Non-goals (explicitly out of scope for the slice)

- No re-extraction or correction of verbatim fields (adjudication is a separate pass).
- No FEP/network-theoretic modeling yet — descriptive statistics and network
  construction only; theory enters after Davis has seen the descriptive layer.
- No OCR of native-script title strings (title_native flag marks them; deferred).
- No comparative-province work (Batch 7 / SV 412/1–48) until Punjab pipeline is stable.

## 7. Risks / watch items

- **Normalization overreach:** folding categories the catalog genuinely distinguished.
  Mitigation: norm layer never overwrites verbatim; every fold is in aliases.json or
  a documented rule; DECISIONS.md records each.
- **Marginalia interpretation:** the pencil apparatus is an unidentified earlier
  hand's (confirmed 2026-07-09 it is NOT Davis's — it predates his acquisition); all
  claims about its purpose are hypotheses, flagged as open provenance questions, not
  findings.
- **Single-transcriber bias:** in-session extraction is one reader (Claude); the
  adjudication queue and Davis's Q2 sheet are the current checks. API re-extraction
  of a sample quarter would give inter-rater agreement — candidate post-slice task.
