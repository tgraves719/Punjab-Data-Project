# Decision Log — Punjab Data Project

Append-only. Each entry: context → decision → consequences. Reversals get a new
entry referencing the old one, never an edit.

---

## D-001 (2026-07, pilot) — Three-layer data model
**Context:** The catalog is both source and object of study; "cleaning" it destroys
evidence about the observing apparatus.
**Decision:** Page image → verbatim imperial record → normalized layer. Verbatim
fields are never edited to fix the catalog; normalization is a separate, inspectable
act (aliases.json + deterministic rules in postprocess.py).
**Consequences:** Every analysis must choose its layer explicitly; misprints and
registrar editorializing remain queryable.

## D-002 (2026-07, pilot) — Provenance and uncertainty policy
**Decision:** Every entry carries pdf_page + printed_page. Uncertain readings go to
`flags` (feeding the adjudication queue), never silently guessed. Davis's sheets are
cross-validation, not gold.
**Consequences:** Queues accumulate (Q2 ~40, Q3 55, Q4 38 items) and require periodic
adjudication sessions against page images.

## D-003 (2026-07, Q2/Q3) — Serial continuity rules
**Context:** Serials looked chaotic until the June→Sept boundary was examined.
**Decision:** Treat serials as continuing across quarters within a year AND across
script subsections of a language (e.g., Q4 PUNJABI—POETRY resumes at 242 after Q3
PUNJABI (PERSIAN CHARACTER)—POETRY ended at 241; URDU (HINDI CHARACTER)—DRAMA s19
continues URDU—DRAMA s18). Registration numbers are one annual sequence.
**Consequences:** Serial monotonicity is a validity check; broken sequences are
evidence of misreads (used to correct p043 Q3) or genuine catalog anomalies (flagged,
e.g. Q4 p34 serial 4 between 19 and 20).

## D-004 (2026-07, Q3) — Ambiguous-glyph resolution with internal evidence
**Context:** Pushto reg 921/924; blur between 3/8 etc.
**Decision:** An ambiguous glyph may be resolved using documented internal evidence
(reg uniqueness within year, serial neighbors), recorded in the flag. This is not a
correction of the record but a reading of it.
**Consequences:** Flags carry the full reasoning chain (e.g., Q4 p15 s298 reg
1331-vs-1381 duplicate analysis).

## D-005 (2026-07, Q3/Q4; amended 2026-07-09) — Prior-hand marginalia are data
**Decision:** Pencil X-marks, running numerals, and handwritten verso indexes are
captured in `marks` and in marginalia_*.md files, but all interpretation (collection
tracking hypothesis) is held as open questions, not findings.
**Amendment (2026-07-09):** These marks are **NOT Davis's** — confirmed with him: they
predate his acquisition of the volumes and are in an unidentified earlier hand. The
data capture is unchanged (we still track every mark), but every attribution was
de-Davis'd across the extractions, marginalia files, explorer UI ("annotated" filter),
and memo. The apparatus is now framed as a prior owner's/reader's second-order
annotation layer — a provenance question, which if anything strengthens the
observation-operator angle.
**Consequences:** Memo (S4) asks Davis about the *source* of the hand, not its meaning.

## D-006 (2026-07, Q3) — Davis-sheet diff made optional
**Context:** No transcription sheets exist for Q3/Q4.
**Decision:** validate.py runs internal checks always, Davis-diff only when a sheet
exists in the manifest.

## D-007 (2026-07-08) — Vertical slice before scaling extraction
**Context:** Year 1910 complete (1,026 entries). Choice: keep extracting (1911+) vs.
build an analysis prototype. Year-level aggregation immediately exposed normalization
debt (lang naming variants, city case/accent duplicates) invisible at page level.
**Decision:** Build the 1910 vertical slice first: S1 normalization, S2 printer–
publisher network, S3 script-market comparison, S4 memo to Davis (see PLAN.md §4).
Extraction resumes afterward, with the API-batch path evaluated once the schema is
validated by real analytical use.
**Consequences:** 1911Q1 deferred; schema fixes land before 40+ more quarters are
extracted; Davis gets a legible artifact.

## D-008 (2026-07-08) — Language normalization + periodical flag
**Context:** Extraction sessions drifted on compound-language naming ("Bilingual
(Arabic Urdu)" in Q2/Q3 vs "Bilingual (Arabic and Urdu)" in Q4) and on periodicals
(Q2/Q3 recorded lang as "Periodicals Urdu"; Q4 recorded lang "Urdu" with
PERIODICALS section).
**Decision:** (a) Add `lang` table to aliases.json; canonical compound form is
"Bilingual (X and Y)" / "Trilingual (X, Y and Z)" preserving the catalog's language
order. (b) `norm_lang` folds "Periodicals X" → "X"; periodical status becomes a
derived `periodical` column set from the section prefix (PERIODICALS…). (c) Cities
get a deterministic fold (strip accents, collapse whitespace, drop trailing "city")
applied before alias lookup. (d) punjab.db `entries` table is dropped and rebuilt
from all three quarters (schema gains norm_lang, periodical).
**Consequences:** Analyses use norm_lang/norm_pcity; verbatim lang/pcity untouched;
future extraction sessions should still record what the section header says — drift
is now absorbed by the norm layer instead of polluting counts.

## D-009 (2026-07-08) — Slice outputs are file-first, Gephi-compatible
**Decision:** S2/S3 outputs are plain CSVs + markdown summaries under
`analysis/slice_1910/out/`, buildable by re-runnable scripts (no notebook state, no
binary formats). Network CSVs use Gephi-importable node/edge conventions.
**Consequences:** Davis and Thomas can open everything without tooling; scripts are
the documentation of method.

## D-010 (2026-07-08) — Printer entity folds (and deliberate non-folds)
**Context:** The catalog itself alternates between short and full firm names.
**Decision:** Folded as one entity (all same city across all 1910 data):
Rafah-i-'Am (Steam) Press variants → "Rafah-i-Am Steam Press"; "Hindustan Press" →
"Hindustan Steam Press"; "Arya Press" → "Arya Steam Press" (both Lahore only);
"Dipak Rajput Press" → "Dipak Rajput Printing Works"; Rose Bazar spelling variants;
Hamidiya variants. **Not folded:** "Rajput Printing Works" is kept distinct from
"Dipak Rajput Printing Works" — the catalog prints both forms within single pages,
so they are plausibly two firms; revisit with address evidence.
**Consequences:** If Arya Press turns out to be a distinct Amritsar firm in later
years, the alias must become year/city-scoped (would need a rule upgrade).

## D-011 (2026-07-08) — Publisher entity resolution is slice-local, for now
**Context:** First network build exposed publisher variants (quote styles for the
CMG Press; The/Messrs./M. prefixes; Son/Sons; Pokar/Pokhar) that distort top-N
tables. A full publisher entity table is real historical work (hundreds of names,
honorific conventions, firm successions) and exceeds slice scope.
**Decision:** build_network.py applies (a) descriptor trimming (", Book-sellers"
etc.), (b) a small documented PUB_ALIASES dict for observed high-frequency variants,
(c) self-publication detection (author/compiler/translator/editor patterns) reported
as a statistic rather than forced into the entity network. norm_publisher in the DB
remains lightly normalized (aliases.json) — the slice does not rebuild it.
**Consequences:** Publisher counts in slice outputs may differ slightly from raw DB
GROUP BYs; the PUB_ALIASES dict is the seed for the eventual aliases.json publisher
table (post-slice task, PLAN.md §5).

## D-012 (2026-07-08) — Explorer is a single self-contained HTML file
**Context:** Thomas asked for an interactive way to visualize and explore the 1910
findings, shareable with Davis.
**Decision:** `analysis/slice_1910/build_site.py` generates
`out/explore_1910.html`: one file, all data embedded as JSON, vanilla JS (no CDN,
no server, no build chain) — opens by double-click, emailable, archive-stable.
Tabs: overview dashboard, filterable full-record table (verbatim + flags + marginalia
marks per entry), canvas force-layout printer–publisher network, script-market
comparison, curated exhibits (cross-linked to the records), method & caveats.
Rebuild after any DB change with `python build_site.py`.
**Consequences:** File is ~0.7 MB and grows with the corpus; when the dataset spans
multiple years it will need pagination or a real static-site split (revisit then).
Verified functionally in a browser (all tabs, filters, canvases, crosslinks; no
console errors).
**2026-07-09 update:** first force layout pinned nodes in a ring at the canvas
border (repulsion ≫ centering + hard clamping). Rewritten: alpha-cooled simulation
in unbounded space, collision resolution, smoothed auto-fit-to-view instead of
clamping. Network tab gained a type switcher, all graphs computed client-side from
the embedded entries (build_network.py refactored to expose publisher_entity for
reuse): Printer↔Publisher, Printer↔Language (press multilingualism), Printer↔Printer
via shared publishers (cooperation backbone), Author↔Printer. Verified: 0% of drawn
content in border strip; all four types build; slider re-thresholds live.

## D-013 (2026-07-08) — Source-page linking: rendered PNGs first, PDF deep-link second
**Context:** Thomas asked whether the explorer can link records directly to the
source page. The bound volume PDF is huge and machine-specific; but the pipeline
already renders every page as `p<printed:03d>_pdf<pdf>.png` with a constant
printed→pdf offset per quarter, and every entry carries both page numbers.
**Decision:** Two mechanisms in the explorer's detail panel: (a) a built-in scan
viewer that loads the page PNG — trying the packaged layout `out/pages/<quarter>/`
first, then the repo-relative pipeline path — with arrow-key paging across the
quarter and click-to-zoom; (b) an "open PDF at p.N" link using `file:///…#page=N`
(volume paths read from the quarter manifests at build time; works in
Chromium/Firefox built-in viewers when the HTML is opened from disk). A
`--package` build flag copies all page PNGs (~145 MB) into out/ so the folder can
be zipped for Davis with scans included. No PDF.js or embedded PDF: the PNGs are
already the pipeline's provenance layer, and a 200 MB+ embedded viewer serves no
one.
**Consequences:** The emailed single file degrades gracefully (viewer explains how
to get scans; PDF link still works on any machine holding the volume at the same
path). The explorer is now a full verification loop: claim → record → flag →
source pixel.

## D-014 (2026-07-09) — 1910Q1 extracted; year 1910 closed as the slice's unit
**Context:** Audit caught that the "1910 complete" claim in the docs was actually
only Apr–Dec (Q2/Q3/Q4 = 1,026 entries); Q1 (Jan–Mar, quarter ending 31 March 1910)
was never extracted. A full year is the source's natural closed unit (D-007), so Q1
was in scope. Q1 sits at the **front of the 1910-1912 volume** (SV_412_44_1910-1912.pdf),
not the earlier-assumed 1908-1910 volume: doc index 2–51 = printed pp. 2–51, **offset 0**
(the manifest's `pdf_page` is PyMuPDF's 0-indexed `doc[]` index, so render.py's `doc[i]`
and the ad-hoc `doc[pdfpg-1]` recon differ by one — reconciled against render.py + the
Q2 manifest). A prior-hand multi-part index verso (an earlier annotator's, not Davis's
— see D-005) is at doc[52].
**Decision:** Extracted all 50 content pages in-session (382 entries), plus the verso
as an empty record with its prior-hand index documented separately in
`data/1910Q1/marginalia_p052.md`. Validation queue = 16 items, all **catalog
artifacts, not transcription errors**: 2 genuine reg collisions (249 at p28-s12/p42-s15;
306 at p38-s8/p49-s6), a printed **reg 570** far out of the 1–383 range (p18 s67), a
30,000-copy outlier (a real mass-issue army musketry form, p2 s1), a printed 1→3 serial
jump (p22 Sindhi Fiction), and cross-section serial resets where the topic-grouping
lumps books + periodicals (Urdu-Law, Urdu-Misc). Per the standing rule, all are
**flagged, not silently corrected**; the three plausible-misread suspects (30000, 570,
326-dup) were each re-checked against the page image and confirmed faithful to the
original before being left in the queue.
**Consequences:** Year 1910 is now genuinely complete — 1,408 entries, 1,960,018
copies, closing the annual registration sequence (regs ~1–1410 with a few
collisions/gaps). Q1 is the 2nd-largest quarter by entries (382, after Q3's 423).
The vertical slice (D-007) now runs on a real full year; the slice scripts
(build_network / script_market / build_site / davis_memo) must be re-run to fold Q1 in.
Next extraction target is 1911 (same volume, 1911Q1 at PDF 195).
