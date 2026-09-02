# Research Agenda — Corpus-Specific Transcription for the Imperial Registrar of Books

*Draft 1, 2026-08-04. Companion to [PLAN.md](PLAN.md) and [DECISIONS.md](DECISIONS.md).
Scope: the transcription/extraction problem only. Analysis questions live in PLAN §1.*

---

## 0. Verdict up front, and three challenges to the framing

**You do not have an OCR problem. You have three different problems that have been
sharing a name, and one of them is already solved.**

| Problem | Status | Right frame |
|---|---|---|
| **A. Record reconstruction** — turn a ruled bureaucratic table into structured bibliographic records | **Solved to ~0.92 weighted / 1.000 reg-recall** (D-015, 4,502 entries) | Structured information extraction under a document grammar |
| **B. Orthographic capture** — the 4,044 native-script title strings that have never been transcribed | **Untouched** (PLAN §6 non-goal) | *Not* OCR. Constrained recognition with a known romanization — a noisy-channel decoding problem with free supervision |
| **C. The annotation layer** — the earlier hand's pencil X-marks, running numerals, "Spec.", index leaves | **Recorded, not modelled** (`marks` populated on 25.1% of entries) | Mark detection + provenance inference. An *observer-of-the-observer* problem |

Everything below is organised around that split. Three challenges before the sections:

**Challenge 1 — your bottleneck is not modelling, it is evaluation and adjudication labour.**
You have 986 queued flags, no record-level gold set beyond one quarter, and a human
transcription (Davis's sheet) with a ~10% registration-number error rate. Any model
improvement you make is currently unmeasurable. Building a better recogniser before
building a record-level evaluation harness is the classic way to spend a year and not
know if you moved.

**Challenge 2 — the most valuable thing you can do this week costs nothing and involves no ML.**
Your scans are **2526 × 4163 px (≈306 DPI)**. `pipeline/render.py` renders at
`dpi: 140` — a **2.2× linear, 4.8× areal discard of the source signal**, applied to
precisely the material that is hardest.

**Now measured, not asserted** (E0, 2026-08-04, n=19 Perso-Arabic titles; see
[analysis/ocr_lab/RESULTS.md](analysis/ocr_lab/RESULTS.md)). The binding constraint is
not x-height — it is the **i'jam**, the dots that alone distinguish b/t/th/p/n/y in
naskh. Those dots measure **9.8 mil** (≈0.25 mm) with **10.6 mil** clearance to the
letter body. On the sampling grid:

| | dot | clearance | |
|---|---:|---:|---|
| 140 DPI (today) | 1.4 px | 1.6 px | **below the 2 px floor — dot identity unrecoverable** |
| 306 DPI (native) | 3.0 px | 3.5 px | resolved, little margin |
| 600 DPI (re-imaging) | 5.9 px | 6.9 px | comfortable |

So the current render does not degrade the diacritics, it **destroys** them: the feature
is smaller than the sample spacing. A blind read of the 140 DPI crops confirms the
predicted error mode exactly — letter bodies survive, dots do not, and every error is a
dot error (*Zindagi* read as *Zadgi*, *Regimental* as *Rehmandal*, *Kawwa* as *Akwa*).
The 140 DPI choice was right for whole-page VLM extraction, where token cost scales with
pixels; it is wrong for crops. This also newly puts **re-imaging the volumes at 600 DPI**
on the table as a costable decision rather than a vague wish.

**Challenge 3 — the LLM's priors are the same force your project studies.**
You suspect LLMs are valuable because transcription is probabilistic. True, but the
consequence runs the other way from the usual reading. A fluent post-corrector applied
to a colonial register will regularise Punjabi and Sindhi spellings toward standard
Urdu, unfamiliar printer names toward frequent ones, and vernacular forms toward the
canonical — because that is where its probability mass is. It will do this *more* to
Sindhi, Kashmiri, Multani and Pushto than to Urdu, because those languages are thinner
in pretraining. **An unconstrained LLM corrector re-enacts the homogenisation dynamic
that is Davis's research question, inside the instrument.** This is not a rhetorical
point: it is measurable, it dictates a hard design rule (§5), and it is probably the
most publishable idea in this document (§9.3).

---

## 1. Problem formulation

### 1.1 The abstraction an experienced researcher would choose

Not "recognise the text." Rather:

> **Infer a posterior over structured records given page images, under a known
> document grammar and known bureaucratic constraints.**
>
> `P(R | I) ∝ P(I | R) · P(R)` where `R` is a quarter's worth of records, `P(I|R)` is
> the rendering/degradation channel, and `P(R)` is the *catalog's own grammar*.

The reason this framing is right, and not just decoration, is that `P(R)` here is
unusually strong and *fully known*. This is a legal instrument produced under the Press
and Registration of Books Act 1867. Its redundancy is enormous:

- **Serial numbers** are monotone within each language–topic section and continue across
  quarters within a year.
- **Registration numbers** form one dense annual sequence (1910: 1–1410 over 1,408
  entries; 1912: 1–1532 with only 42 gaps). *You know almost the entire set of values
  that must appear on the year's pages before you read them.*
- **`Ditto`** is a formal anaphor: 24.3% of printer fields (1,093 entries) are resolved
  by rule, not by reading.
- **Section headers** declare language, script, and topic, and govern every entry beneath
  them until superseded.
- **Six columns** with fixed semantics, ruled on the page.
- **Cross-references** ("Previous edition noticed in entry No. 239 at page 41 of the
  Catalogue for the quarter ending 31st March, 1906") link records across volumes.
- **Entity reuse**: 4,502 entries draw on only 350 printers and 59 printer-cities.

A page is therefore not free text. **It is a parse, not a read.** Any architecture that
treats pages as i.i.d. images and characters as i.i.d. symbols is throwing away most of
the available information. The single largest accuracy gain still on the table for
problem A is *joint inference over a quarter* rather than per-page independent
extraction (§3.E).

### 1.2 Which of your candidate framings apply

- **OCR** — applies only to problem B, and only to a bounded sub-image (a 1–5 word
  title string), never to the page.
- **Document understanding / layout analysis** — mostly *solved by the document itself*.
  The columns are ruled; the ruling is findable by projection profile in milliseconds.
  Don't spend model capacity on it.
- **Vision-language modelling** — the right tool for problem A. Already validated.
- **Sequence transduction** — the right tool for problem B, but with a twist: the target
  sequence is *conditioned on a known transliteration of itself*.
- **Bayesian inference** — the right meta-frame, and the one that lets you keep
  uncertainty instead of destroying it (§7). Treat it as a real posterior, not as a
  metaphor: the deliverable per field is a ranked candidate set with mass, not a string.
- **Information extraction** — yes, and specifically *IE under hard constraints*
  (integer-programming / CRF over a quarter), which is underused in DH.

### 1.3 The formulation that fits your theoretical commitments

Your project already commits to modelling the **observation operator**, not just the
observed ([theory memo](analysis/slice_1910/davis_memo_1910.md); PLAN §1.3). The
transcription system is a *second* observation operator stacked on the first. Formally
you are estimating

```
lifeworld  --(imperial registration apparatus)-->  catalog page  --(our pipeline)-->  records
                        Θ_apparatus                                    Θ_pipeline
```

and the methodological commitment that follows is exact and cheap to honour: **the
pipeline's parameters must be as documented, as versioned, and as criticisable as the
apparatus's.** Practically that means every transcription is stamped with model id,
prompt hash, render DPI, and constraint set — so that in five years a reader can ask
"what did the instrument do to this record?" the same way you now ask it of Suraj
Narayan Mehr. Your three-layer data model (image → verbatim → normalised) already
encodes this; it needs a fourth column, not a fourth layer: *provenance of the reading
itself*.

---

## 2. Data first — what to compute before touching a model

Your corpus is the asset, and much of this is computable **today** from `punjab.db` and
the page PNGs. Ordered by value.

### 2.1 The physical measurement pass (do this first — it decides architecture)

- **Native resolution audit per volume.** Embedded scan dimensions, effective DPI,
  JPEG quality, colour vs grayscale, across all volumes 1867–1942. *Measured for
  SV_412_44_1910-1912: 2526×4163, JPEG, ~306 DPI.* Do not assume the other volumes match
  — 75 years of microfilming and rescanning will not be uniform, and the answer changes
  your feasible architecture per volume.
- **x-height of native-script type, in pixels, at native DPI, per script per decade.**
  This is *the* feasibility number for problem B. My eyeball estimate from the 306 DPI
  crop of 1910Q2 p.31 is ~22–28 px for the Perso-Arabic titles — marginal but workable.
  Measure it properly with connected-component statistics; if some decade sits at 12 px,
  no model will save you and the honest answer is "not recoverable at this scan
  quality," which is itself a finding worth recording.
- **Typographic census across the run.** Which fount for the Perso-Arabic titles, and
  when does it change? 1910–1912 is **naskh**, typeset, not nastaliq lithography — which
  is very good news, because the Latin/Arabic HTR gap literature is dominated by
  nastaliq and manuscript hands. Expect the 1860s–80s volumes to look different. A
  typographic changepoint analysis over 75 years is a small paper by itself and it tells
  you where to shard your training data.
- **Degradation covariates per page**: skew angle, bleed-through energy, local contrast,
  ink-spread estimate, stamp/marginalia occlusion, rule-line completeness. These become
  the features of a **page difficulty model** — used for routing (§3.F), for stratified
  sampling of gold data (§2.4), and as a covariate in error analysis.

### 2.2 The redundancy audit (decides how much you can get for free)

Compute, per quarter: what fraction of each field is *determined* by constraints given
the rest of the page?

- Reg numbers: given the annual sequence and the entries around it, how often is a
  missing/illegible reg uniquely recoverable? (1912 had 42 gaps in 1,532 — so the answer
  is "almost always.")
- Serials: monotonicity + section resets.
- Printer: Ditto chains (24.3% free) plus a 350-entity closed vocabulary.
- Cities: 59 distinct. Effectively a closed set — a spelling that isn't in it is a flag,
  not a new city.

**Deliverable: a per-field "constraint coverage" table.** It tells you directly where
model improvement is worth paying for and where a rule is strictly better. My prediction:
`reg`, `serial`, `printer`, `pcity` are largely constraint-recoverable; `title`,
`gloss`, `author`, `price`, `date` are not. That is the real target list.

### 2.3 The supervision inventory (the hidden asset)

This is the most important thing in this document.

**Every native-script title on the page is printed immediately adjacent to its own
romanization, in brackets, followed by an English gloss.**

```
73  کتا  [ Kutta.  The Dog. ]  1 sheet.  [9th May, 1910.] 22 × 18, litho., 1st edition.
```

You already have the roman side transcribed for **4,044 entries** (the `title_native`
flag marks exactly these; `title` holds the catalog's own romanization). So you hold
**4,044 (image-crop, romanization, English gloss, language, subject, author, publisher)
tuples** — for three years of one province. Across the full Punjab run that is on the
order of **60,000**; across the ~40 provincial registers of SV 412/1–48 (your Library 2
Batch 7), plausibly **hundreds of thousands**.

That is a free, at-scale, aligned supervision signal for Perso-Arabic and Indic
historical print recognition, obtained without a single human annotation. Nothing of
that size exists publicly — OpenITI MAKHZAN, the reference open Arabic-script ground
truth set, is ~1,500 pages total with 8 printed Urdu publications. This is the asset.
See §9.2.

Native-script strings awaiting capture, from `punjab.db` (2026-08-04):

| Language | native-script titles | of entries | share |
|---|---:|---:|---:|
| Urdu | 1,769 | 1,875 | 94.3% |
| Punjabi | 1,455 | 1,486 | 97.9% |
| Hindi | 224 | 228 | 98.2% |
| Bilingual (Arabic & Urdu) | 89 | 89 | 100% |
| Bilingual (Hindi & Sanskrit) | 70 | 89 | 78.7% |
| Sindhi | 62 | 64 | 96.9% |
| Arabic | 49 | 58 | 84.5% |
| Bilingual (Persian & Urdu) | 38 | 39 | 97.4% |
| Persian | 35 | 36 | 97.2% |
| Kashmiri | 26 | 26 | 100% |
| Sanskrit | 22 | 22 | 100% |
| English | 11 | 268 | 4.1% |
| **Total** | **4,044** | **4,502** | **89.8%** |

Note the tail: Kashmiri at 26, Sanskrit at 22, Multani in single digits. **These are the
languages where a fluent corrector will do the most damage and where you have the least
data to fine-tune on.** Design for the tail, report the tail (§8.5).

### 2.4 The failure inventory

You already have a labelled failure set and haven't used it as one: **789 entries
carrying 829 flags**, self-reported by the extractor, distributed as

`serial 242 · copies 112 · reg 75 · copyright 69 · date 46 · pp_verbatim 45 · title 35 · author 30 · price 29 · edition 25`

Two things to do with it:

1. **Calibration study.** Adjudicate a stratified sample of ~200 flags against the page
   images. What fraction of flags are real errors? What fraction of real errors carry a
   flag? That gives you precision and recall *of the uncertainty channel itself* — which
   is the number that determines whether flags can be trusted to route human attention
   (§7). Nobody in the DH-OCR literature reports this and it is cheap for you to get.
2. **Error taxonomy.** The distribution above is informative on its own: flags cluster on
   *numeric* fields (serial, copies, reg, copyright = 498/829 = 60%), i.e. on
   short, low-redundancy, high-consequence strings. Language modelling cannot help with
   digits. Resolution and constraints can. This is a direct argument for Challenge 2
   and §3.E over any fine-tuning effort.

Also mine `Punjabi Books 20240401b.xlsx` for the *human* error taxonomy — the ~10% reg
error rate in Davis's sheet is not noise, it is a measurement of what unaided human
transcription of this material costs, and it belongs in your paper as the baseline.

### 2.5 Where current systems fail — diagnose, don't assume

Run a deliberate failure sweep on 20 pages stratified by difficulty, comparing: Tesseract
(`eng`, `urd`, `pan`), a classical layout pipeline, and your current VLM extraction.
Record failures by *category*, not by CER. My priors on what you'll find, stated so they
can be falsified:

- Classical OCR will fail catastrophically on inline script mixing *within a line* — the
  entry `Budh Singh, B.—ਪੰਜਾਬੀ ਬੋਲੀ ਦੇ ਪ੍ਰਚਾਰ … [ Punjabi Boli de prachar te sawar lai …`
  puts Latin and Gurmukhi in one text line, which breaks the standard
  segment-then-recognise-per-script assumption.
- Table detection will fail on ruled cells whose contents span 6 wrapped lines and whose
  logical entry boundary is a *serial number*, not a rule.
- The VLM will fail on: degraded digits, margin-cut column 6, pencil strokes crossing
  numerals, and — critically — it will *silently drop entries* when a page is dense.
  Entry-drop is the failure mode that matters (Haiku dropped 69 entries in one quarter,
  D-015) and it does not show up in CER at all.

---

## 3. Architecture search

Six candidates, simple to state-of-the-art. The recommendation is **D + E**.

### A. Classical pipeline (Tesseract / ABBYY / OCR4all)
Binarise → deskew → layout → line seg → per-script recognisers → rule-based parse.
*Strength:* free, deterministic, auditable, no hallucination — literally cannot invent a
word that isn't in the image. *Weakness:* inline script mixing; entry-boundary logic;
Ditto anaphora; degraded small type. *Verdict:* **not viable as the system**, but keep
one classical recogniser in the stack as an **independent second opinion** — its errors
are uncorrelated with a VLM's, which makes it valuable for agreement-based confidence
(§8.4). Adobe OCR, which Davis offered to fund, is in this family; it will not read the
Perso-Arabic titles at all.

### B. Specialist line-level HTR (Kraken / eScriptorium, TrOCR-family)
Train a CRNN or transformer line recogniser on Arabic-script and Indic lines.
*Strength:* the mature, correct tool for problem B; ALTO-XML ground-truth workflow that
DH reviewers recognise; OpenITI MAKHZAN gives you a warm start for Perso-Arabic.
*Weakness:* needs ground truth; the reported Latin↔Arabic-script HTR gap is a persistent
**5–7 CER points even at full data scale**, with ~30% of Arabic substitution errors
caused by visually-similar-character confusion vs ~15% for Latin — i.e. exactly the
dotting/rasm confusions your degraded 6-point naskh will produce.
*Verdict:* **use it for the title crops only**, and — the key move — don't run it
unconstrained (see D).

### C. End-to-end VLM structured extraction (**your current system**)
Whole page → JSON records, schema in a cached system prefix.
*Strength:* handles layout, anaphora, section carry, glosses, and self-reports
uncertainty — the thing classical pipelines cannot do. Empirically validated on your own
data: reg recall 1.000, weighted 0.916, ~$2/quarter batched.
*Weakness:* entry drop; no localisation (you get the record, not the pixels it came
from); no calibrated confidence; cannot read the native script at 140 DPI; cost scales
with pages, and the full empire-wide corpus is ~10²–10³ × your current spend.
*Verdict:* **keep as the backbone for problem A.** It is doing well and replacing it
would be a mistake.

### D. Two-channel hybrid — **recommended**

> The VLM parses the record and *localises* the native-script span. A specialist
> recogniser decodes that crop at native resolution, **constrained by the romanization
> the VLM has already read from the same line.**

```
page @140dpi ──▶ VLM extraction ──▶ record + bbox for native title span
                                          │
                        crop @306dpi ─────┤
                                          ▼
             candidate Urdu/Gurmukhi orthographies  ◀── romanization + gloss + language
                    generated by transliteration prior
                                          │
                     visual rescoring (specialist HTR / CTC likelihood)
                                          ▼
                    posterior over orthographic strings (top-k retained)
```

Why this is the right architecture, and not merely a clever one:

- The unconstrained task (read tiny degraded naskh) is hard. The constrained task
  (choose among the Urdu spellings consistent with the printed romanization *Gainda*,
  gloss *The Rhinoceros*, subject *Miscellaneous*, publisher *Qaumi Press Siálkot*) is
  **enormously** easier — the candidate set is often size 1–5.
- The transliteration literature is unambiguous that **Roman→Urdu is the easy
  direction** (Urdu orthography is standardised; roman transliteration is not), which is
  precisely the direction the catalog hands you.
- It fails safe. If the visual channel is uninformative, you fall back to the
  transliteration prior and *say so* — you get a distribution, not a fabrication.
- It generates its own training data: high-confidence outputs become ground truth for
  fine-tuning the specialist (§6.3), which then sharpens the visual channel, which
  resolves more cases. A genuine bootstrap.

*Weakness:* requires bounding boxes, which your current VLM output doesn't carry; needs a
transliteration model; two systems to maintain. All tractable.

### E. Global constraint layer — **recommended, highest ROI, no ML**
After extraction, run **joint inference over a whole quarter/year**: serial monotonicity
and section resets, annual reg-sequence density, Ditto propagation, closed-vocabulary
snapping for printer/city, date monotonicity within a quarter, `pp_sum` consistency.
Formulate as an ILP or a factor graph; where a field's extracted value violates
constraints, prefer the constraint-satisfying candidate *and record the intervention*.
*Strength:* deterministic, auditable, corrects exactly the numeric fields where 60% of
your flags live, needs no training data, and gives you an **unsupervised quality
estimator** you can run on ungolded quarters (§8.2).
*Weakness:* can mask genuine catalog anomalies — and your corpus *has* genuine anomalies
(printed reg 570 outside the 1–383 range; real collisions at 249 and 306). Mitigation is
absolute: the constraint layer **never overwrites the verbatim layer**, it emits a
proposal with a reason. Same discipline as D-008 normalisation.

### F. Agentic / self-verifying OCR
Model inspects its own output, re-crops uncertain regions, re-reads at higher DPI,
re-queries.
*Verdict:* **mostly reducible to something cheaper.** The useful 80% is "re-render the
uncertain region at native resolution and look again," which you can do deterministically
by routing on flags — no agent loop, no unbounded cost. Keep the *selective re-look*,
drop the agency. The genuinely agentic part worth keeping is cross-quarter lookup
("this entry says 'previous edition noticed in entry 239, p.41, quarter ending 31 March
1906' — go read that entry"), which is retrieval over your own corpus (§6.5).

### G. Distilled small VLM
Fine-tune an open 3–8B VLM on Opus outputs + adjudicated gold, for the empire-scale run.
*Verdict:* **not now; mandatory later.** Rough arithmetic: 609 pages ≈ 3 years, so Punjab
1867–1942 ≈ 15,000 pages ≈ $600 at your current batch rate — affordable. All ~40
provincial registers ≈ 300k–600k pages ≈ $25k–50k — not affordable, and that is the
scale at which distillation stops being an optimisation and becomes the enabling
condition. Design the data layout now so this is a swap, not a rewrite.

### Explicitly rejected
- **Mixture-of-experts as an architecture choice.** You are not training a foundation
  model; MoE here is vocabulary borrowed from a different problem. What you actually want
  — routing different scripts to different specialists — is D, and calling it MoE adds
  nothing but reviewer suspicion.
- **A single end-to-end model that outputs everything including native script.** It
  couples two problems with very different data regimes and error costs, and it destroys
  the constraint that makes B tractable.

---

## 4. Script identification

**Challenge the premise: in this corpus, page- and entry-level script identification is
not an open problem — the document performs it for you.** Every entry sits under a
section header that declares language and, where ambiguous, script:
`URDU—PHILOSOPHY.`, `PUNJABI MISCELLANEOUS.`, `"Punjabi characters"`, `"Persian
character"`. That header is already extracted (`section` 100% filled; `lang` 100%;
`char` 12.5% — populated exactly where the catalog itself disambiguates).

So the real questions are narrower and more interesting:

1. **Span detection, not classification.** You need the *bounding box* of the
   native-script run inside a line of roman type. Do this jointly: the VLM localises (it
   already reads the line), and a connected-component script classifier verifies. Latin,
   Perso-Arabic, Gurmukhi and Devanagari are trivially separable by visual statistics
   (headline/shirorekha presence, baseline continuity, dot density, ascender profile) —
   this is a 20-line feature classifier, not a research problem. **Use script ID as
   verification of a strong prior, not as discovery.**
2. **Header-vs-script mismatch is a finding, not an error.** Punjabi appears in Gurmukhi
   *and* in Shahmukhi (Perso-Arabic); Kashmiri is Perso-Arabic; the 1910Q1 Mahajani
   bookkeeping primer is a third case. Where the declared language and the observed
   script diverge, you have located a point where the apparatus's classification scheme
   and print reality come apart. **Log every mismatch to a table; that table is
   analysable evidence about the observation operator**, and it feeds directly into your
   script-market work (analysis/slice_1910/script_market.py).
3. **Recursive/iterative script ID** — worth it only in one place: multi-script entries
   (the trilingual and polyglot titles, e.g. the three-script Relief Fund circulars, the
   polyglot Bhagavad Gita with Besant's English). There, run span detection → recognise
   → check the recognised string's script against the span classifier → re-segment on
   disagreement. Bound it at two iterations.
4. **Language ID ≠ script ID.** Keep them as separate fields with separate provenance,
   because your corpus separates them and collapsing them would destroy the Punjabi
   Gurmukhi/Shahmukhi distinction that is central to the partition question.

---

## 5. The role of large language models — what is real and what is hype

Sorted honestly.

### Genuinely valuable

**5.1 Structured extraction under a document grammar (proven on your data).**
The largest win, already banked. Classical pipelines cannot resolve `Ditto`, cannot carry
`—concluded.` sections across pages, cannot decide that a bracketed clause is a gloss and
an unbracketed one is a price. Keep.

**5.2 Candidate generation for the native script (§3.D).**
An LLM conditioned on romanization + gloss + language + author + publisher is an
excellent *proposer* of Urdu orthographies. This is the single highest-value new LLM
role in the system. Note the strict division of labour: **the LLM proposes, the image
disposes.** Never let the proposal stand without visual rescoring.

**5.3 Uncertainty reporting (now calibrated — and it means something different than assumed).**
E5 measured it. Against actual errors a flag has precision 0.13 and recall 0.30–0.56:
high-recall, low-precision, the mirror image of constraint violations, and nearly
disjoint from them (Jaccard 0.05–0.11). On the *golden* extraction, **0 of 17 adjudicated
flags were transcription errors** — 53% were catalog artefacts, 35% genuinely degraded
source, 12% legible-but-unusual values.

So the flags are not a weak error detector; they are a good *anomaly* detector being read
as an error detector. Precision for errors is bounded above by the extraction's real
error rate, so on an accurate extraction most flags must be "false positives" for error
while remaining true for what they actually claim. **Read them as a register of source
anomalies** (§7.2), and use constraint violations when the question is where the
extraction is wrong. Their real power is in combination: flag ∩ violation reaches
precision 0.67–1.00, flag ∪ violation reaches recall 0.48–0.67.

**5.4 Entity normalisation and record linkage.**
350 printers, 2,091 publishers, 2,018 authors, with orthographic drift across years
(+59 language aliases in two years alone). An LLM proposing merge candidates, with a
human-auditable `aliases.json` as the only thing that actually takes effect, is exactly
the right shape: model suggests, file decides, decision is reviewable. This is already
your D-010 policy — extend it to printers and publishers before the drift compounds.

**5.5 Synthetic data generation for the specialist.**
Take a known romanization → generate the Urdu/Gurmukhi orthography → typeset in a
period-appropriate fount → apply your *measured* degradation model (§2.1) → get labelled
training lines by the hundred thousand. This is how you train the visual channel in D
without annotating anything. Fidelity of the degradation model is the whole game;
fit it to real crops, don't hand-wave it.

**5.6 Human review assistance.**
Not "here is the corrected text" but "here is the crop, here are three candidate
readings with their evidence, here is the constraint that flagged it, here is the same
printer's name on four other pages." Assistance means assembling evidence, not
delivering verdicts (§7).

**5.7 Cross-corpus retrieval.**
Resolving "previous edition noticed in entry No. 239 at page 41 of the Catalogue for the
quarter ending 31st March, 1906" by actually retrieving that entry. Genuinely agentic,
genuinely useful, and it builds the reprint network that Davis's question 2 needs.

### Hype, or actively harmful here

**5.8 Free-running LLM post-correction of verbatim fields — prohibit it.**
The evidence is against it and your regime is the worst case. The published finding is
that post-correction gains are language-dependent and can be negative, that models
introduce new and qualitatively different errors, and — most relevant to you — that
**overcorrection dominates in low-noise settings**, which is exactly where your reg-recall-1.000
extraction sits. Your corpus adds three aggravating factors: (i) primary-source text
whose value *is* its verbatim form; (ii) proper nouns and transliterations with no
correct "modern" form; (iii) languages thin in pretraining. Rule: **no LLM output may
overwrite a verbatim field. Ever. It may only propose, with the proposal stored beside
the original.** This is a strengthening of your existing three-layer commitment, and it
should go into DECISIONS.md.

**5.9 Historical spelling normalisation at the transcription layer.**
Same rule. Normalisation is an *analysis-layer* operation; performing it during
transcription destroys the evidence of variation, and variation in spelling of names,
places, and titles is data about the print ecology, not noise.

**5.10 LLM token logprobs as confidence.**
Poorly calibrated in general, unavailable or awkward through the Batch API, and
measuring the wrong thing (fluency of the output, not fidelity to the image). Replace
with: cross-run agreement, cross-model agreement, cross-architecture agreement (VLM vs
classical), and constraint satisfaction. These are all cheap and all better.

**5.11 "LLMs will do layout analysis."**
They will, and they'll charge you tokens for finding lines that a projection profile
finds for free and deterministically. Use rules where rules work.

**5.12 The differential-legibility hazard — measure it, don't just avoid it.**
Following Challenge 3: any LLM involvement anywhere in the stack should be audited for
whether its benefit is distributed evenly across languages. If post-correction improves
Urdu by 3 CER points and degrades Sindhi by 1, the aggregate looks like a win and the
system has quietly made the corpus *more* Urdu-centric than the empire made it. §8.5.

---

## 6. Fine-tuning strategy — sequenced by return on effort

**The ordering matters more than the items.** Do not do 3 before 2.

**0 — Re-render at native resolution.** (hours, $0) Add a `crop_dpi` to the manifests;
keep page-level rendering at 140 for VLM cost, render crops at 306. Nothing else in this
list is correctly measurable until this is done.

**1 — Build the record-level evaluation harness and a stratified gold set.** (1–2 weeks)
Extend `analysis/bakeoff_1910Q2.py` from one quarter to a difficulty-stratified gold set
of ~500 entries spanning multiple decades, scripts, and scan qualities. Include entries
you *expect* to fail. Without this you cannot detect a regression, and at 60k entries a
silent regression is unrecoverable. **This is the highest-ROI item in the whole
document after item 0.**

**2 — The global constraint layer (§3.E).** (1–2 weeks, no ML) Attacks the 60% of flags
that sit on numeric fields; yields an unsupervised quality signal for every future
quarter.

**3 — Native-script capture via the two-channel architecture (§3.D).** (the real research
project) Sequence within it:
   a. Localise native spans; re-crop at 306 DPI; build the (crop, romanization) dataset —
      4,044 pairs today, ~60k at Punjab scale.
   b. **Ablation first**: how much of the target is recoverable from the romanization
      alone, with no image? (§10 experiment E2.) If a pure transliteration prior already
      hits 60–70% exact-match, the visual channel's job is disambiguation, and you should
      build a cheap reranker rather than a heavy recogniser. *Run this before choosing a
      recogniser.*
   c. Warm-start a Kraken/TrOCR-family recogniser from OpenITI MAKHZAN + synthetic data
      (§5.5); fine-tune on high-confidence bootstrap outputs.
   d. Iterate the bootstrap, with a held-out gold set gating every round.

**4 — Active learning on the flag queue.** (ongoing) Route human adjudication by
*expected effect on conclusions*, not by model confidence (§7.3). Corrections flow back
as gold, versioned, never overwriting.

**5 — Retrieval augmentation — narrow.** Retrieve over **your own corpus** (entity
lexicon, prior quarters, cross-referenced entries), never over the open web. The corpus
is its own best index; external retrieval imports exactly the modern priors you're
trying to keep out.

**6 — Distillation to a small open VLM.** (when you commit to multi-province scale)

**7 — RL from human corrections.** Last, and probably never. Preference optimisation on
a corpus this small, with reward derived from a handful of adjudicators, mostly teaches
the model your adjudicators' idiosyncrasies — and does so in a way that is far harder to
audit than an alias table. If you want to encode human judgement, encode it as data and
rules, not as weights.

**Instruction tuning** is subsumed by 6. **Fine-tuning a general VLM on whole pages** is
strictly worse than 6 for cost and worse than 3 for the native script.

---

## 7. Human-in-the-loop design

### 7.1 Uncertainty should be preserved, and the data model should make that cheap

Right now a record is a row. That forces a single reading. Move to a **claims model**:

```
claim(entry_id, field, value, source, confidence, evidence_ref, timestamp, superseded_by)
```

where `source` ∈ {opus-4-8@promptsha, kraken-urdu-v3, davis-xlsx-2024, adjudicator:TG,
earlier-hand-pencil, constraint-layer}. A "record" becomes a *view* over claims under a
stated resolution policy. Consequences:

- Davis's sheet stops being a diff to reconcile and becomes a **co-equal witness**.
- The earlier hand's pencil marks become claims about the *same* entries, letting you ask
  what that reader was selecting for — turning provenance mystery into analysis (§9.5).
- Disagreement is representable without being resolved, which is what your
  epistemological commitments require and what a single-value schema silently forbids.
- Corrections are appends, not overwrites — so training data accumulates automatically
  and reproducibility survives.

This is a schema change, and it gets more expensive every quarter you ingest. **Do it
before 1913.**

### 7.1b Split the queue at intake — the flags are two different things

E5b changes the shape of the human loop. Of 17 adjudicated flags on the golden
extraction, none was a transcription error; ~65% recorded a fact about the *catalog*
(registration collisions, `intique` set for *intrigue*, `1318 Hijri` against an 1910
date, a printer with no city, a missing edition ordinal) and ~35% marked genuinely
degraded print.

Those are not the same work item and must not share a queue:

- **"Check my reading"** (~35%, ~350 items corpus-wide) — a human re-reads pixels, and
  the output is a confirmed or corrected value. This closes.
- **"The source is odd"** (~65%, ~640 items) — the output is a *property of the record*,
  and it should live beside the record permanently. **This never closes.** Filing it in a
  task list guarantees it is eventually marked done and lost.

This is the strongest practical argument for the claims model in §7.1, and it makes the
"before 1913" deadline sharper: artifacts need somewhere durable to live before there are
forty more quarters of them.

### 7.2 What the historian actually sees

Never a bare corrected string. The unit of review is: **crop at native resolution +
ranked candidates with mass + the constraint or flag that raised it + corpus context**
(same printer elsewhere, same serial neighbourhood, prior edition if cross-referenced).
One keystroke to accept, one to reject, one to escalate, free-text for "the catalog is
wrong here" — which is a genuinely different verdict from "we misread it" and must be
storable as such. Your explorer (`build_site.py`, D-013 source-linking) is already 70% of
this interface.

### 7.3 The novel bit: route attention by value of information

Standard active learning surfaces the model's least-confident items. **That is the wrong
criterion for history.** Surface the items whose resolution would most change a
*published aggregate* — top-20 printer rankings, language-share trends, the copies
distribution, network centralities. An uncertain digit in a 50-copy pamphlet's serial is
noise; an uncertain digit in a 30,000-copy print run moves your headline number.

Concretely: for each uncertain field, sample from its candidate distribution, recompute
the target statistics, and rank by variance induced. This costs almost nothing (you have
the DB and the statistics scripts already) and it is, as far as I can find, not standard
practice in DH transcription workflows. It is a small methods contribution on its own.

### 7.4 Corrections as training data

Every adjudication writes a claim with source and timestamp; the gold set is a *query*
over claims, not a hand-maintained file. Gate every model update on a frozen held-out
slice that adjudication is not allowed to touch, or you will fine-tune on your own test
set within a year.

---

## 8. Evaluation — what actually matters

CER and WER are nearly the wrong metrics here. A page can have 1% CER and be useless if
the 1% is concentrated in registration numbers; it can have 8% CER in the glosses and be
perfectly fine for every question you want to ask.

**8.1 Record-level primaries.**
- *Entry recall* — fraction of printed entries that appear at all. **The dominant failure
  mode** (69 dropped entries, D-015) and invisible to CER.
- *Field-exact accuracy per field*, weighted by analytic importance (your bake-off
  weighting is already right in spirit: reg 0.35, then serial/copies/title).
- *Key integrity* — reg-sequence density, duplicate rate, join success against the
  previous quarter.

**8.2 Constraint-satisfaction rate as an unsupervised proxy — tested, and qualified.**
The original claim was that constraint satisfaction would let you monitor quality across
15,000 pages with no gold data, and so avoid discovering in 2029 that volumes 1893–1897
were quietly bad. **E3 says: as an alarm yes, as a measurement no.**

What holds:

- **Entry-level triage.** A hard violation makes an entry ~7× more likely to carry a
  key-field error (precision 0.56 against a 0.08 base), catching a third of all errors
  while flagging ~5% of entries. This is how you order an adjudication queue (§7.3).
- **Regression alarm across quarters.** The four in-session 1910 quarters run at 0.7–1.6
  hard violations per 100 entries; the eight API-batch quarters run at 2.7–9.0. That gap
  is now visible on quarters that have no gold — exactly the intended use.
- **Complementarity.** Corpus-wide, 172 entries carry a hard violation and 789 carry an
  extractor flag, but only 71 carry both. The two uncertainty channels are largely
  independent, so rank the queue on their union — and this is direct support for §8.4's
  preference for agreement over any single self-reported signal.

What does not hold: **the signal has dynamic range but poor resolution.** An 8× gap in
error rate shows up as a 1.8× gap in violation rate, so constraint counts cannot certify
a quarter or choose between two decent models. Quality estimation at scale still needs
gold, which makes item 1 of §6 more important, not less.

**And the correction that generalises:** what actually carried the result was not a
grammar rule but the **lexicon** check — *the corpus is its own dictionary*. A press
named once that sits within two edits of a press named twenty-six times is the frequent
one, misread. That single check took entry-level lift from 2.8× to 6.7×, because the
grammar constrains the *skeleton* (serial, reg, Ditto) and good models are already
near-perfect there — Opus makes zero registration errors in 321 entries while making 20
printer-name errors. **For this corpus, redundancy of entities beats redundancy of
sequence**, which corrects the emphasis in §2.2 and is the same insight that makes §5.4
valuable. Full result in [analysis/ocr_lab/RESULTS.md](analysis/ocr_lab/RESULTS.md).

**8.3 Downstream-invariance — the metric historians should care about.**
Propagate the transcription posterior into the actual analyses and report *conclusion
stability*: does the top-20 printer ranking hold under resampling? Do the language-share
trends? Does the network's community structure? A transcription system should be
evaluated on whether its errors move the findings — and this reframing is publishable in
itself, because almost nobody does it.

**8.4 Confidence calibration.**
Precision/recall of the flag channel (§2.4); agreement rates across runs, models, and
architectures; reliability diagrams. Report agreement as the operational confidence, not
logprobs.

**8.5 Differential legibility — report always, never aggregate away.**
Every metric, stratified by language, script, decade, and scan quality. State explicitly:
"error rate 1.8% overall; 1.2% Urdu; 4.6% Sindhi; 7.1% Kashmiri (n=26)." A single
aggregate number on a multilingual colonial corpus is a political act disguised as a
summary — it lets the best-resourced language speak for the archive. This metric is also
your §9.3 research contribution, so you get it for free.

**8.6 Human baselines and ceilings.**
Report against Davis's sheet as a *human* baseline (~10% reg error), and report
inter-adjudicator agreement on the gold set. Gold is not truth; say so with a number.

**8.7 Cost.** Accuracy-per-dollar at batch pricing (already implemented), plus
*cost-per-corrected-record* including human adjudication time — which will dominate, and
which is the number that decides whether the multi-province project is feasible.

---

## 9. Research opportunities

Ranked by novelty × feasibility. These are the ones I'd actually write.

**9.1 Bilingual-anchored recognition: reading the vernacular through the imperial
romanization.** *(document AI venue: ICDAR/ICFHR; DH venue: DHQ/CHR)*
A new task with free supervision: recover native orthography from a degraded crop
conditioned on an adjacent printed transliteration. It generalises far beyond you —
colonial-era bibliographies, gazetteers, census schedules, missionary linguistic surveys
and consular records across the British, French and Dutch empires used the same
native-script + bracketed-romanization + gloss convention. The method is portable; the
supervision is everywhere; nobody has framed it as a task.

**9.2 The largest historical Indic/Perso-Arabic print recognition dataset, built without
annotation.** *(dataset/resource paper)*
Hundreds of thousands of (crop, romanization, gloss, language, date, place) tuples from
SV 412/1–48. Compare: OpenITI MAKHZAN, the reference open resource, is ~1,500 pages.
Licensing and colonial-provenance ethics need real thought (§10.4), not a checkbox — but
this is a field-shifting resource if done carefully.

**9.3 Model-induced homogenisation of the archive.** *(the one that unifies your project)*
Hypothesis: modern language models, applied as correctors to a multilingual colonial
corpus, reduce orthographic and onomastic variance, and do so *asymmetrically* by
language in proportion to pretraining representation — thereby reproducing, in the
instrument, the very hierarchy of scripts and languages the corpus documents. This is
measurable with what you already have: variance of name forms before/after correction,
per language; correction acceptance rate per language against gold; drift of rare forms
toward frequent ones. It speaks to ML fairness researchers *and* to postcolonial
historiography with the same numbers, and it is a direct empirical instantiation of
"colonisation of the lifeworld" as exogenous control of evidence standards — the model's
prior as a steering medium imposing high-precision low-dimensional expectations on a
diverse ecology. **This is your paper.**

**9.4 Constraint-based unsupervised quality estimation for serial bureaucratic
documents.** *(methods paper, small but useful)*
Formalise the grammar of a legally-mandated register as constraints; show that
satisfaction rate predicts error rate; demonstrate quality monitoring at scale without
gold data. Applies to censuses, shipping registers, court rolls, parish registers,
land-revenue settlements — a large fraction of the world's archived state records.

**9.5 Reading the reader: computational provenance of an unidentified hand.**
The pencil apparatus spans 609 pages of the 1910–1912 volume: X-marks, running numerals
(28→116 within a quarter), "Spec." notes, multi-part index leaves at nearly every
quarter's end, one bound *inside* a quarter. Detect the marks, model the selection rule
(what distinguishes marked from unmarked entries — language? subject? publisher?
copyright status? multi-part serials?), and you have inferred a historical reader's
research question from their marginal traces. This is second-order observation made
operational, and it is a lovely, self-contained DH paper.

**9.6 The observation operator across provinces.** *(the long game, and the strongest
social-science contribution)*
The same instrument (the 1867 Act, one form, one column scheme) applied to ~40 different
print ecologies over 75 years. That is a natural experiment for separating instrument
from ecology: variation in the apparatus (Acts of 1867/1890/1907/1910, category-scheme
revisions) identifies `Θ_apparatus`; variation across provinces at fixed apparatus
identifies ecology. A joint estimation of both is a genuinely new object for
computational history and is exactly the formal move your theory memo commits to.

**9.7 Counter-archive triangulation as a measurement-error model.**
Davis's physical collection contains referents of catalog entries. That gives *direct*
measurement of catalog distortion — what the registrar recorded vs what the book is.
Formalise as a measurement-error / validation-sample design (a well-developed statistical
apparatus), and you can correct corpus-wide estimates using a small validated subsample.
Rare in DH; standard in survey statistics; a real methodological import.

**9.8 A benchmark: structured extraction from ruled multilingual bureaucratic tables.**
OmniDocBench, olmOCR-Bench and the rest are modern-document-centric. A benchmark of
colonial administrative tables — mixed script inline, anaphoric `Ditto`, wrapped
multi-line cells, marginalia occlusion, entry boundaries defined semantically rather than
geometrically — targets failure modes current systems genuinely have. Cheap for you to
carve out of work you're doing anyway.

---

## 10. Long-term vision — and what to disbelieve about it

### 10.1 Which of your four futures is real

- **"An archival operating system"** — *resist this.* It is the most seductive and the
  most common way DH infrastructure projects die: they become platforms nobody adopts,
  maintained by one person, unfundable after the grant. Your existing instinct is
  better and should be held: static files, no server, double-clickable, readable in
  2050 (D-009/D-012). The archive's stability requirement and the software industry's
  norms are in direct conflict; you have already chosen correctly.
- **"A multilingual historical transcription platform"** — real, but as a *method plus
  dataset plus reference implementation*, not as a hosted service. Ship the method so
  others can run it on their corpus; don't run their corpus for them.
- **"A foundation model for colonial archives"** — real only as *data + a fine-tune*.
  Nobody will pretrain from scratch for this, and they won't need to. The moat is the
  aligned multilingual historical dataset (§9.2), not weights. Weights depreciate
  annually; a well-documented corpus with provenance does not.
- **"Infrastructure for computational history"** — **this is the right one**, and the
  form it should take is a *panel dataset*: registered print across the provinces of
  British India, 1867–1942, with entity resolution, provenance, and uncertainty
  preserved. A new observational object for historical social science. Everything else in
  this document is in service of that.

### 10.2 The architecture that gets you there

Nothing exotic. Keep the per-quarter pipeline; add (i) a claims table, (ii) a constraint
layer, (iii) a native-script channel, (iv) a distilled recogniser when province count
> 1. The scaling cliff you identified (PLAN §8) is real and its fix is known. Resist
adding a service tier until someone other than you needs one.

### 10.3 The one thing that will actually determine success

Not model quality. **Whether the adjudication loop is sustainable by two people.** At
15,000 pages and a 5% flag rate you are looking at ~3,000 adjudications for Punjab
alone. Value-of-information routing (§7.3) is not a nicety; it is the difference between
a finishable project and an unfinishable one. Design the human loop first and the models
around it.

### 10.4 What to think about before scaling

- **Provenance and ethics of the counter-archive.** Publishing an at-scale dataset
  derived from colonial records that name authors, publishers and their cities is not
  neutral — much of this print ecology ended up on the wrong side of a partition, and
  descendants exist. The right posture is neither "it's public domain" nor paralysis:
  document provenance, publish the apparatus alongside the data, and think about who in
  Punjab and Pakistan should be a collaborator rather than a subject. This belongs in the
  agenda now, not at publication.
- **Your own instrument's documentation.** Every claim in the final dataset should carry
  the model, prompt, resolution, and constraint set that produced it — so that the
  pipeline is as criticisable as the registrar. That is the methodological commitment
  your theory already makes; the claims table (§7.1) is what makes it true rather than
  aspirational.

---

## 11. Critical-path experiments (falsifiable, cheap, do these first)

Results in [analysis/ocr_lab/RESULTS.md](analysis/ocr_lab/RESULTS.md); code in
`analysis/ocr_lab/` and `pipeline/crops.py`.

| # | Experiment | Decides | Status |
|---|---|---|---|
| **E0** | Native-script legibility budget in physical units against the sampling grid | Whether problem B is feasible, and at what resolution | **DONE** — i'jam dots are 9.8 mil; 140 DPI is *below* the 2 px sampling floor, 306 clears it, 600 would be comfortable |
| **E1** | Blind read of native-title crops at 140 DPI | Quantifies the resolution loss; sets the DPI policy | **DONE (pilot, n=8 blind)** — 4/8 exact, 4/8 with dot errors, 0 unrecognisable; the error mode is exactly what E0 predicts |
| **E2** | Romanization alone vs with the crop vs crop-only | *The key design decision.* Reranker or recogniser? | **PILOT DONE** — the romanization resolves 4/4 of the image channel's failures |
| **E3** | Constraint violations vs known errors, scored on the 1910Q2 bake-off and run over all twelve quarters | Whether §8.2 unsupervised QE is trustworthy | **DONE** — entry-level triage works (**7× lift**, 33% recall, ~5% flagged) and it raises a real alarm on 1911–1912; but it has poor resolution and cannot certify a quarter. §8.2 qualified. The lexicon check, not the grammar, carried it |
| **E4** | 3 independent extraction runs of one quarter; agreement vs gold | Whether cross-run agreement is a usable confidence signal | next, ~$6 |
| **E5** | Flag precision/recall on the bake-off, plus adjudication of gold flags against page images | Precision/recall of the uncertainty channel — gates all HITL design | **DONE (E5a full; E5b pilot n=17, not the 200 specified)** — flags are high-recall/low-precision (prec 0.13, recall 0.30–0.56) and nearly disjoint from constraints (Jaccard 0.05–0.11); **0/17 gold flags were transcription errors**, 65% were source anomalies. §7 revised |
| **E6** | LLM post-corrector on gold; per-language ΔCER **and** variance reduction in name forms | Tests §9.3's homogenisation hypothesis on data you already have | next, ~$10 |

**What the pilots settled.** The two channels fail in complementary places: the image
recovers the consonantal skeleton and loses the diacritics; the romanization carries
exactly what the diacritics carry. That is the precondition for §3.D, so the two-channel
architecture now rests on evidence rather than on argument.

**What they could not settle, and why it matters.** Arms cannot be isolated when one
reader performs them in sequence — reading the image contaminates the text-only arm. The
fix is architectural, not a matter of discipline: **each arm must be an independent model
call carrying only its own inputs.** That is the first thing to run once an API key is
available, and the requirement generalises to any inter-rater or ablation work on this
corpus.

E2 and E6 remain the two that could each become a paper.

---

## 12. Immediate decisions this agenda implies

1. **Add `crop_dpi` to manifests; render crops at native resolution.** (supersedes the
   implicit 140-DPI-everywhere policy)
2. **Adopt the claims model before ingesting 1913.** Retrofit cost grows every quarter.
3. **Record a decision prohibiting LLM overwrite of verbatim fields** — propose-only,
   stored alongside. (DECISIONS.md, extends D-008)
4. **Promote native-script capture from "deferred non-goal" (PLAN §6) to a named
   workstream** — it is where the research contribution is.
5. **Build the stratified gold set and record-level harness before the next model
   comparison.** Generalise `bakeoff_1910Q2.py` beyond one quarter.
6. **Always report metrics stratified by language.** Never publish a single aggregate
   error rate for this corpus.

---

## Sources consulted (2026-08-04)

- [From Press to Pixels: Evolving Urdu Text Recognition](https://arxiv.org/html/2505.13943v3)
- [Urdu Katib Handwritten Dataset (historical Urdu HTR, CRNN baselines)](https://arxiv.org/html/2606.19139)
- [Performance Gap Analysis between Latin and Arabic Scripts HTR](https://arxiv.org/abs/2606.18884) — the 5–7 CER-point persistent gap; 30% vs 15% visually-similar-character substitutions
- [OpenITI MAKHZAN: Arabic, Persian, Ottoman Turkish and Urdu print/manuscript ground truth](https://openhumanitiesdata.metajnl.com/articles/10.5334/johd.465) — ~1,500 pages, 8 printed Urdu publications, ALTO XML, CC BY-NC-SA
- [OpenITI Arabic-script OCR Catalyst Project](https://openiti.org/projects/OpenITI%20AOCP%20Phase%20Two.html) and [eScriptorium](https://escriptorium.eu/about/)
- [OCR Error Post-Correction with LLMs in Historical Documents: No Free Lunches](https://arxiv.org/abs/2502.01205)
- [ICDAR 2026 HIPE-OCRepair Competition on LLM-Assisted OCR Post-Correction](https://arxiv.org/html/2607.08143v1) — cMER metric, overcorrection in low-noise settings
- [dots.ocr: Multilingual Document Layout Parsing in a Single VLM](https://arxiv.org/pdf/2512.02498)
- [olmOCR / olmOCR-Bench](https://olmocr.allenai.org/papers/olmocr.pdf)
- [Reading or Guessing? Visual Grounding Failures of VLMs for OCR in Ancient Greek Editions](https://arxiv.org/pdf/2605.27750)
- [Low-Resource Transliteration for Roman-Urdu and Urdu Using Transformer-Based Models](https://aclanthology.org/2025.loresmt-1.13/) — Roman→Urdu is the easier direction
- [Lexically Aware Semi-Supervised Learning for OCR Post-Correction](https://arxiv.org/pdf/2111.02622)
- [Unsilencing Colonial Archives via Automated Entity Recognition](https://arxiv.org/pdf/2210.02194)
- [Unlocking colonial records with AI (large-scale historical transcription)](https://www.tandfonline.com/doi/full/10.1080/20548923.2025.2484828)
- [AWESOME-OCR-LLM: OCR in the Era of Large Language Models](https://github.com/yuliang-liu/awesome-ocr-llm)
