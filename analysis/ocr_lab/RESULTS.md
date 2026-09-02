# OCR lab — first results (E0, E1, E2 pilot)

*2026-08-04. Code in this directory; agenda in [../../OCR_RESEARCH_AGENDA.md](../../OCR_RESEARCH_AGENDA.md).*

Sample: 1910Q2, 248 entry crops from 32 of 42 pages, 41 with a tight native-script
title crop, of which 19 Perso-Arabic and 19 Gurmukhi.

---

## E0 — the legibility budget, in physical units

The feasibility question for these titles is not x-height. Naskh letter skeletons are
few and repetitive; **b/t/th/p/n/y are distinguished only by i'jam** — the dots. If the
dots cannot be counted the glyph body can be perfectly sharp and the word still
unreadable. So the measurement is the dot's physical size against the sampling grid.

| script | n | body height | i'jam dot | dot-to-body clearance |
|---|---:|---:|---:|---:|
| Perso-Arabic | 19 | 101 mil | **9.8 mil** | **10.6 mil** |
| Gurmukhi | 19 | 103 mil | 7.4 mil | 6.5 mil |
| Devanagari | 2 | 57 mil | 9.8 mil | 53 mil |

(mil = 1/1000 inch. Devanagari n=2 — indicative only.)

What that lands on, per resolution:

| | dot | clearance | verdict |
|---|---:|---:|---|
| **140 DPI** (what `render.py` produces today) | 1.4 px | 1.6 px | **below the 2 px sampling floor — dot count is not recoverable** |
| **306 DPI** (the scans' native resolution) | 3.0 px | 3.5 px | resolved, but 3 px is the low end |
| 400 DPI | 3.9 px | 4.6 px | comfortable — requires re-imaging |
| 600 DPI | 5.9 px | 6.9 px | comfortable — requires re-imaging |

**Conclusion.** Rendering at 140 DPI destroys the diacritic layer of the Perso-Arabic
titles — not degrades it, destroys it: the feature is smaller than the sample spacing.
Re-rendering at the scans' native 306 DPI recovers it, with little margin to spare.
A 600 DPI re-imaging would move Perso-Arabic capture from "just possible" to
"comfortable", and that is now a costable decision rather than a guess.

Two honest caveats. First, "resolved with margin" at 3.0 px is generous; ink spread and
JPEG artefacts eat into it. Second, an earlier version of this measurement reported
"66% of dot components lost at 140 DPI"; that figure was partly definitional, since any
component filter discards a 1-pixel blob. The physical-units framing above replaces it.

Verification that 306 DPI carries real information and is not empty magnification:
the RMS difference between the true 306 render and a 140 render upsampled to 306 is
**38% of the crop's own contrast** (`zoom_140_vs_306.png` shows it at pixel scale).

---

## E1 — blind reading at 140 DPI

19 Perso-Arabic title crops were read from the image alone, with no access to the
catalog's romanization (`montage_PA_140.png`, `e1_read_140.json`). Eight of the 19 were
fully blind — their romanizations had not been seen at any point in the session. The
rest are excluded: nine had appeared in an earlier text dump, and two have the
romanization printed inside the crop because the native-span cut failed on them.

**Blind subset, n=8, image only, 140 DPI:**

| outcome | n | |
|---|---:|---|
| exact | 4 | Mirqat; Qissa Tota wa Maina Mukammal; Raja Saryal Lila; Bail |
| approximately right, ≥1 wrong letter | 4 | see below |
| unrecognisable | 0 | |

All four errors are diacritic errors, and every one of them is exactly the failure E0
predicts:

| read | correct | error |
|---|---|---|
| زادگی | زندگی (*Zindagi*) | nun dropped — dot below |
| رہمنڈل | رجمنٹل (*Regimental*) | dots on jim/te |
| اکوا | کوا (*Kawwa*) | spurious leading alif from broken ink |
| سچی ما تا ئین | *Sachchi Mataen* | word division only |

The physical prediction and the observed error mode agree: at 140 DPI the letter
*bodies* survive and the *dots* do not, so reading degrades into precisely the
confusions that dots exist to prevent.

---

## E2 — how much work does the image actually have to do?

This is the pilot that decides the architecture, and its result is unambiguous even at
n=8: **the catalog's own romanization resolves every one of the image channel's
failures.**

- *Zindagi* fixes زادگی → زندگی.
- *Regimental* fixes رہمنڈل → رجمنٹل.
- *Kawwa* fixes اکوا → کوا.
- *Sachchi Mataen* fixes the word division.

4 of 4. The visual channel got the consonantal skeleton right in 8 of 8 cases and the
diacritics wrong in 4; the romanization carries exactly the information the diacritics
carry. The two channels fail in complementary places, which is the precondition for the
two-channel architecture (agenda §3.D) to work.

Arm A (romanization → orthography, no image, `e2_armA_text_only.json`) was recorded
before any crop was viewed, but against a key list that a subsequently-fixed ordering
bug had scrambled, so it is retained as a protocol artefact rather than scored.

**The methodological finding is as important as the result:** arms cannot be isolated
when one reader performs all of them in sequence. Reading arm C contaminates arm A, and
the fix is not discipline but architecture — each arm must be an independent model call
with only its own inputs in context. That needs the Batch API path
(`pipeline/extract_api.py`), and it is the first thing to do when a key is available.

---

## Infrastructure built

`pipeline/crops.py` — native-resolution crop extraction.

- Page geometry from the rules, matched by **ratio** rather than pixels: these scans
  vary in magnification by several percent from page to page, so absolute widths do not
  calibrate. Columns 3-5 have a distinctive width signature (one wide cell, two equal
  narrow ones) that identifies each rule's role in the form; some pages lose the left
  border and others the right, so indexing detected rules positionally does not work.
- Entries anchored on **column 5, the registration number** — not column 1. Both hold
  only digits on the entry's first line, but column 1 sits against the page edge and
  collects the earlier hand's pencil crosses, running numerals and gutter shadow.
- Warp, not skew: the two halves of a page differ by up to a third of a degree, so
  baselines are fitted per line rather than corrected globally.
- Alignment is **validated against the register**, not assumed: pages whose detected
  entry count disagrees with the catalog's own record are reported and dropped. 32 of 42
  pages of 1910Q2 align exactly; the 10 failures are listed in the crop-set manifest.

`analysis/ocr_lab/` — `build_cropset.py`, `e0_measure.py`, `make_montage.py`.

### Two failures worth recording

**The ordering bug.** The first crop set paired every crop with the wrong record. The
database returns a page's entries grouped by section, not in page order: printed page 31
of 1910Q2 reads 73-79 then 1-3, while the database returns 1, 2, 3, 73-79. Zipping
detected entries against that order is silently wrong — every field is plausible, just
attached to the wrong image. It was caught only because a montage showed *Gainda* where
the index claimed *Vedanta Philosophy*. The fix reads page order from the per-page
extraction JSONs, which preserve it. **Any future work that joins images to records must
not use database row order.**

**The native-span cut is not solved.** Locating the `[` that opens the romanization
succeeds on only ~18% of entries. Tall narrow strokes with a solid left edge are also
alif, lam and kaf in Perso-Arabic and the vowel signs in Gurmukhi; an inter-word-gap
rule agrees with the bracket on only 44% of cases, because the catalog's justified
setting opens Latin word spaces as wide as the gap before the bracket. Entry-level
strips are reliable and are what the crop set is built on; the tight native-span cut
should be done by the VLM at localisation time (agenda §3.D), not by a classical rule.

---

## E3 — can the document's own grammar tell us where an extraction is wrong?

The prize is quality estimation without gold: ~40 quarters of the 1867–1942 run will
never have a validated transcription, and something has to certify them.

`pipeline/constraints.py` implements the checks the register's grammar supports — serial
runs, registration range and uniqueness, `Ditto` resolution, required fields, numeric
plausibility, the date window, and near-duplicate entity names. Calibration on the golden
1910Q2: **the serial advances by exactly +1 on all 237 within-section transitions,
without exception.** Checks that gold itself violates (reg collisions, singleton cities)
are marked soft and reported separately.

The test uses the 1910Q2 bake-off — three models extracted the quarter we hold a
validated transcription of — so every candidate entry carries a known error label.
Constraints are computed from each candidate alone, never from gold.

### Result

| | quarter level (Q1) | page level (Q2) | entry level (Q3) |
|---|---|---|---|
| **verdict** | ordering correct, scale compressed | weak but consistent | **works as triage** |
| evidence | violations/100 of 8.1 / 5.0 / 4.4 against error rates 70.4% / 8.4% / 5.6% — right order, but an 8× error gap shows up as a 1.8× violation gap | ρ ≈ +0.30 to +0.37; flagged pages hold 39–53% of errors | precision 0.56, recall 0.33 at a 0.08 base — **lift 6.7×** (Opus); 8.9× (Sonnet) |

A hard violation makes an entry roughly **seven times more likely** to carry a key-field
error, catching a third of all errors while flagging ~5% of entries. That is a good way
to order an adjudication queue. With n=3 models, the quarter-level ordering is one of six
possible arrangements and is not by itself evidence; the cross-quarter scan below is
stronger.

### The errors are not where the grammar looks

| | reg | serial | copies | printer | pcity | entries with ≥1 error |
|---|---:|---:|---:|---:|---:|---:|
| opus-4-8 | 0 | 4 | 2 | **20** | 2 | 27 (8.4%) |
| sonnet-5 | 1 | 4 | 6 | **8** | 0 | 18 (5.6%) |
| haiku-4-5 | 74 | 36 | 40 | **136** | 14 | 226 (70.4%) + 15 unmatched |

The grammar constrains the *skeleton* — serial, reg, Ditto — and a good model is already
near-perfect there: Opus makes **zero registration errors in 321 entries**. Errors
concentrate in printer and place names, which the grammar says nothing about.

What did the work was therefore not a grammar rule but the **lexicon** check — *the
corpus is its own dictionary*. A press named once that sits within two edits of a press
named twenty-six times is the frequent one, misread. That single check raised entry-level
lift from 2.8× to 6.7×. **For this corpus, redundancy of entities beats redundancy of
sequence** — a correction to the emphasis in agenda §2.2.

### Corpus-wide scan, and a regression alarm

Running the checker over all twelve ingested quarters:

| quarter | entries | hard/100 | | quarter | entries | hard/100 |
|---|---:|---:|---|---|---:|---:|
| 1910Q1 | 382 | **0.8** | | 1911Q3 | 395 | 6.8 |
| 1910Q2 | 321 | **1.6** | | 1911Q4 | 372 | 7.8 |
| 1910Q3 | 423 | **0.7** | | 1912Q1 | 378 | 9.0 |
| 1910Q4 | 282 | **1.1** | | 1912Q2 | 382 | 4.7 |
| 1911Q1 | 339 | 8.0 | | 1912Q3 | 372 | 2.7 |
| 1911Q2 | 456 | 5.5 | | 1912Q4 | 400 | 3.2 |

The four 1910 quarters — the in-session golden extraction — run at 0.7–1.6 hard
violations per 100 entries. The eight API-batch quarters run at 2.7–9.0, **three to eight
times higher**, concentrated in `serial_step`, `missing_serial` and
`printer_near_duplicate`. This is precisely the "discover in 2029 that a volume was
quietly bad" case the checker was built for, and it is firing now, on quarters that have
no gold. It should be read as an alarm worth investigating, not as a measured error rate:
the checker has useful *dynamic range* and poor *resolution*.

### Constraints are complementary to the model's own flags

Across the corpus, 172 entries carry a hard violation and 789 carry an extractor flag,
but only **71 carry both**. So 59% of constraint-flagged entries — about 100 entries —
were never flagged by the extractor and would otherwise never be looked at. The two
uncertainty channels are largely independent, which is the useful case: it argues for
ranking the adjudication queue on the union, and it supports agenda §8.4's preference for
agreement-based confidence over any single self-reported signal.

Spot-checking against page images confirmed the flag channel works where it fires: the
empty serial on 1912Q1 reg 66 carries the extractor's own note, *"serial number
illegible/degraded in margin"* — and the page shows the serial cut into the binding
margin. The extraction was right to leave it empty and right to say so.

### Two checks of mine that were wrong

Both were caught by adjudicating flagged entries against the page image, which is the
only way to tell a bad check from a bad extraction.

- **`missing_title` fired on continuation entries.** The catalog sets a long dash for an
  entry continuing the title above it — the same anaphor as `Ditto`, one column over — so
  an empty title beside a filled gloss is the printed form. 47 corpus-wide violations
  were almost all this. Now fires only when title *and* gloss are empty: 15.
  Worth noting as a schema gap: nothing in `schema.md` marks an entry as a title
  continuation, so the distinction has to be inferred.
- **`missing_serial` and `serial_nonint` double-counted** the same empty fields.

### Caveat on the error label

A first version of this script scored `price`, `publisher`, `title`, `edition` and `date`
and reported a 28% error rate for the model the bake-off measured at reg recall 1.000.
Almost all of it was convention: `1,000` vs `1000`, `Qádián` vs `Qadian`, `1st edition`
vs `1st`, `(1327)` vs `(1327 Hijri)`. Those fields are excluded and the comparison folds
diacritics, thousands separators, trailing points and case. **Any future cross-run
comparison on this corpus has to do the same, or it will measure house style.**

### One finding that touches a decision

**Sonnet 5 may beat the model D-015 selected.** D-015 chose opus-4-8 because Sonnet's
batch was still queued when the decision was made. Scored now on the register's own
validation fields, Sonnet makes **18 key-field errors to Opus's 27** — the gap is almost
entirely printer names (8 vs 20) — at roughly a third of the price. Opus keeps a
one-error edge on registration numbers, the field D-015 weighted most heavily, so this is
not an automatic reversal. It is enough to justify re-running `bakeoff_1910Q2.py` before
the 1913–1915 ingestion, where the choice compounds across ~40 more quarters.

---

## E5 — is the uncertainty channel worth following?

The schema tells the extractor to flag uncertain readings "aggressively", and it does:
789 of 4,502 entries carry a flag, and PLAN §5 treats the resulting ~986 items as an
adjudication backlog. Every human-in-the-loop design in the agenda assumes those flags
are worth a historian's time. Nobody had checked.

### E5a — flag precision and recall, measured where truth exists

On the 1910Q2 bake-off each candidate emitted its own flags, and gold gives the error
labels, so this needs no human at all.

| predictor | precision | recall | lift |
|---|---:|---:|---:|
| **flag** (Opus) | 0.13 | 0.30 | 1.6× |
| **flag** (Sonnet) | 0.13 | 0.56 | 2.3× |
| constraint violation (E3) | 0.50–0.56 | 0.33 | 6.7–8.9× |
| flag **OR** violation | 0.14–0.19 | **0.48–0.67** | 2.2–2.5× |
| flag **AND** violation | **0.67–1.00** | 0.15–0.22 | 7.9–17.8× |

The two channels are almost disjoint — Jaccard **0.05–0.11**. That gives a concrete
triage policy rather than a single queue:

1. **flag ∩ violation** — very small, precision 0.67–1.00. Near-certain errors.
2. **violation only** — precision ~0.5, still cheap.
3. **flag only** — precision ~0.13, but this is where most of the recall lives.

At the field level the picture sharpens: a flag on `serial` carries 16–20× lift, on
`copies` 36× (Sonnet), on `pcity` 160×. But a flag on **`reg` has precision 0.00 for both
good models** — they flag registration numbers they then read correctly. Reg flags are
the most reassuring and least useful part of the queue.

### E5b — what the flags on the *golden* extraction actually are

E5a cannot speak to the corpus we actually ship, because there gold is the thing being
judged. So 19 flags were drawn stratified across flagged fields from the four 1910
quarters and adjudicated against native-resolution crops (`e5b_verdicts.json`).

**n = 17 adjudicable. Real transcription errors: 0.** (95% upper bound ~16% — this is a
pilot, not the 200-item study the agenda specified.)

| verdict | n | share | |
|---|---:|---:|---|
| **artifact** — transcription right, the *catalog* is irregular | 9 | 53% | reg collisions; `intique` for *intrigue* set in the source; `1318 Hijri` against a 1910 date; "Magazine Press," with no city; a missing ordinal before "edition"; no price line |
| **degraded** — transcription right or best-available, source genuinely hard | 6 | 35% | smudged pagination; a serial overwritten by the earlier hand's pencil X; a copyright cell cut at the page edge |
| **plausibility** — source perfectly legible, value merely unusual | 2 | 12% | print runs of 187 and 1,090 |

### What this changes

**The flag queue is not an error queue. It is a register of source anomalies.** Roughly
two thirds of it (65%) records facts about the catalog that need no correction — they
need *preserving*. Only about a third asks a human to re-read pixels. Treating ~986 items
as a backlog of suspected mistakes mis-frames the work and inflates it: projected over
the corpus, ~350 items want a human's eyes and ~640 are findings.

This has a direct design consequence, and it strengthens the claims model (agenda §7.1):
an artifact verdict is not a task to close but **a property of the document**, and it
belongs beside the record permanently, not in a work queue that someone eventually marks
done. The queue should be split at intake into "check my reading" and "the source is
odd", because they have different readers, different outputs, and different lifetimes.

It also reframes E5a's low precision. A flag's precision *for errors* is bounded by the
extraction's actual error rate; on a good extraction most flags must be false positives
for "error" while remaining true positives for "this is hard or odd" — which is what they
literally say. **The flags are well calibrated to their own semantics and badly matched to
the use we were putting them to.** The fix is to read them as what they are, and to lean
on constraint violations (E3) when the question is specifically "where is this wrong".

One quiet finding worth recording: on 1910Q2 p20 the page prints `Stara-i-Hiud Press`
(a broken *n*), the flag says so — and the stored value was silently normalised to
`Stara-i-Hind`. That is a small breach of the verbatim layer's guarantee. Worth a sweep
for other cases where a flag documents a correction the value already absorbed.

### A defect in my own instrument

The first worksheet cropped columns 2–5, so two `copyright` flags were unadjudicable —
and `copyright` is the fourth most flagged field in the corpus (69 flags). Column 6's
right border is often cropped off the scan, so the crop now takes its width from the
form's proportions. On re-run the flag proved exactly right: `No. 1__ dated the 6__
September, 191_`, cut at the page edge. **Any adjudication interface must show the whole
row, including the column the flag is about** — obvious in retrospect, and it silently
removed 12% of the sample before it was noticed.
