# Punjab Data Project — Plan of Record

*Maintained by: Thomas Graves + Claude (pipeline sessions), for the joint project with
Prof. Emmett Davis. Last updated: 2026-07-09.*

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

## 2. Current state (as of 2026-07-09)

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

## 5. After the slice (sequenced, not yet started)

1. Adjudication session: work the four queues (Q1 16, Q2, Q3 55, Q4 38) against page
   images. Q1's are all catalog artifacts already triaged; Q3's 55 remain the priority.
2. Decide API-batch scaling (est. $100–200/decade) vs. continued in-session
   extraction; 1911Q1 starts at PDF 195 of SV_412_44_1910-1912.pdf.
3. Priority order for next extractions: 1910 is now a complete year (all four quarters,
   regs ~1–1410) — the vertical slice's closed unit is in hand. Next is 1911 (same
   SV_412_44_1910-1912.pdf volume, 1911Q1 at PDF 195).
4. Davis meeting: marginalia **provenance** — the pencil apparatus (X-marks, running
   numerals, verso indexes incl. Q1 doc[52]) predates his acquisition, so the question
   shifts from "what did you record" to whether he knows the source hand; memo feedback;
   xlsx reconciliation for 1920/1930/1940.

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
