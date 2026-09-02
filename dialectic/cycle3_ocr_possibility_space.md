# cycle3_ocr_possibility_space.md — the native-script problem, the dataset question, and whether building it reproduces empire

Companion to `OCR_RESEARCH_AGENDA.md`, which settles architecture. This settles a question the agenda deferred to a paragraph (§10.4): **what happens when the archive becomes a dataset.** The three dialectical cycles produced instruments for exactly this, and they give sharper answers than an ethics section.

---

# PART I — What is actually in hand

**The native-script layer is empty.** `title_native` holds `'True'` / `'False'` — it is a *flag*, not content. **4,044 entries are marked as carrying a native-script title and zero of those strings are captured.** The asset is entirely prospective.

**The physical constraint, measured (E0, `analysis/ocr_lab/`), is script-dependent and this has not been drawn out.** Feature sizes in mils, and their resolution on three sampling grids:

| script | dot | clearance | @140 DPI (current render) | @306 DPI (native scan) | @600 DPI (re-imaging) |
|---|---:|---:|---|---|---|
| Devanagari | 9.8 | **53.1** | 1.4 / 7.4 px | 3.0 / **16.3** px | 5.9 / 31.9 px |
| Perso-Arabic | 9.8 | 10.6 | 1.4 / 1.5 px | 3.0 / 3.2 px | 5.9 / 6.4 px |
| **Gurmukhi** | **7.4** | **6.5** | 1.0 / **0.9 px** | 2.3 / **2.0 px** | 4.4 / 3.9 px |

> **At the resolution of the scans you own, Gurmukhi sits exactly on the 2-pixel recoverability floor while Devanagari has eight times the margin. The sampling grid imposes a hierarchy of scripts, and Punjabi's own script is at the bottom of it.**

This is not a metaphor and not an intention. It is arithmetic: 306 DPI × 6.5 mil clearance = 2.0 px. A scanning resolution chosen by someone who was not thinking about Gurmukhi determines that Gurmukhi will be the hardest script in any dataset built from these images.

> **SUPERSEDED 2026-08-19 by E0b** (`analysis/ocr_lab/E0B_RESULTS.md`, n=511 across twelve quarters). **The table above is wrong and two of its consequences are withdrawn.** E0's Devanagari row rested on **two crops**; its Gurmukhi sample was contaminated with 62 Punjabi-in-Persian-character crops.
>
> **What survives:** Gurmukhi is the least recoverable script here — **31% of crops below the 2 px floor at 306 DPI against Perso-Arabic's 14%** — and the language-controlled comparison confirms it: **Punjabi in Gurmukhi 31%, Punjabi in the Persian character 21%.** Same language, same presses, same decade; only the script differs. The hierarchy is ~2.2×, not categorical.
>
> **What is withdrawn:** Devanagari's supposed eight-fold margin (n=2), and — see §III.6 — the claim that 600 DPI re-imaging is a precondition. Doubling resolution removes only 3–5 percentage points, because the binding population is **sub-pixel adjacency** (30% of Gurmukhi marks), whose origin — lithographic ink merge versus undersampling — cannot be determined from 306 DPI scans.
>
> **Also found:** the register's `method` field is blank for 71.5% of Punjabi and 88.2% of Hindi entries against 3.3% of Urdu — a *third* field recorded differentially by language. **The register's completeness is itself stratified by language**, which invalidates naive cross-language comparison on any sparse field without a recorded-vs-blank control.

**And 1,755 pages have no OCR at all** (`cycle3_handbill_trace.md` §0) — 1876–80, 1894–99, 1900–03, 1904–06.

---

# PART II — Three tasks share the name, and the third is missing from the agenda

The agenda splits OCR into record reconstruction (solved), orthographic capture (untouched), and the annotation layer. The orthographic problem needs a further split that changes everything:

**B1 — Recognition.** `image crop → native-script string`. The target is **the publisher's own typography**, set in Lahore or Amritsar by a Punjabi press. Recovery of an indigenous artefact.

**B2 — Transliteration.** `native ↔ romanization`. The target is **the Reporter's rendering scheme**. This is `φ`, the colonial translation operator, at the orthographic level — the same operation `cycle3_corpus_encounter.md` §5 found in the gloss, one layer down.

**B3 — Retrieval.** `query → ranked crops`, with **no transcription committed at all.**

B3 is absent from the agenda and it is probably the right first move. See Part IV.

---

# PART III — Does building the dataset reproduce empire? Run the instruments.

Not "is colonial data tainted" (unanswerable, and it licenses both paralysis and dismissal). The instruments ask sharper questions.

## III.1 — S-12: what must be declared before the dataset can begin?

Five things, all declared before any model runs, none revisable by evidence the dataset generates, all looking like technical convention:

| declaration | what it fixes | who currently declares it |
|---|---|---|
| **render DPI** | which scripts are recoverable at all (Part I) | a scanner operator, decades ago |
| **the unit** | line / word / title-string / page — what counts as an example | us |
| **the language label set** | `Ω` — and the register's is 62 categories with a 50-category hapax tail | **the Reporter on Books, 1910** |
| **the transcription target** | native orthography, or romanization, or both | us |
| **the evaluation metric** | what "good" means, and which languages can be ignored | us |

**The language label set is the sharpest.** Any ML dataset needs clean labels. The first thing anyone does with 62 categories where 50 hold 408 items is **fold the tail**. `cycle3_corpus_encounter.md` §4 established that the tail *is the signal* — the point at which a multilingual print culture defeats the register's scheme. **Folding it would be the coarsening event, performed by us, at machine scale, and shipped as a standard.**

## III.2 — The transliteration trap

The agenda calls the adjacent romanization "free supervision… obtained without a single human annotation." It is free because **empire already did the labelling**, and what it labelled was its own act of rendering.

`Ω_A ≇ Ω_B` matters here concretely: the romanization is not a transcription of the native string. It is a *mapping into an administrative orthography* that (a) collapses distinctions Perso-Arabic makes, (b) imposes English phonetic conventions, (c) is inconsistent across quarters and Reporters, and (d) was performed for a reader in Calcutta or London.

Two consequences, and they point opposite ways:

**Against.** A model trained to produce romanization has learned `φ`. Publishing it as a transliteration tool ships the colonial rendering scheme as infrastructure — and unlike the original, it runs at scale and for free.

**For, and this is the dialectical turn.** A model that *inverts* `φ` must have modelled `φ`. And `Θ_apparatus` — the observation operator — is precisely what this project exists to study. **The contamination is the instrument.** A learned model of the Reporter's transliteration is a computational object that no historian has ever had: the colonial rendering operator, explicit, queryable, and testable for where it destroys distinctions.

**Resolution — and it is a naming decision, not a technical one:**

> **Never publish the romanization as ground truth. Publish it as a dated reading by a named historical actor.**

Not `title_roman: "Kutta"` but `reading: {text: "Kutta", by: "Reporter on Books, Punjab", date: 1910-05, source: SV412/44 p.73, operator: φ_colonial}`. The claims model in agenda §7.1 already supports this; it costs nothing and it changes the dataset's ontology completely. Ground truth is what the press printed. Everything else is somebody's reading, including ours.

## III.3 — S-15: a flat OCR dataset is a coarsening event

An OCR dataset is maximally individuating: crop → string. Ship 60,000 pairs and you have shipped the register's individuation and destroyed everything above it — **precisely the operation S-15 identifies as the imperial one.**

The kinds that die: the series (a Hand Bill is No. 31 of a campaign), the section (a title's sense depends on its `LANGUAGE—TOPIC` context), the publisher as an actor across five spelling variants, the volume as a document.

**Requirement, cheap and decisive:** every crop ships with its record, its section, its publisher entity, its series membership where known, and its volume/page provenance. **The aggregates the register lacked must travel with the data, or the dataset repeats the crime at higher resolution.**

## III.4 — S-19: build the residue channel deliberately

The register had no field for community, so community migrated into the Reporter's choice of nouns (`cycle3_q18_genre_vocabulary.md`). A dataset schema will do the same thing to its annotators.

**So give it somewhere to go.** Two design consequences that are unusual and follow directly:

1. **A free-text annotator note on every example**, explicitly for what the schema would not let them say. Then *measure its drift against a null baseline* — the S-19 method, turned on our own instrument.
2. **Preserve inter-annotator disagreement as a first-class field rather than resolving it.** Disagreement about a glyph, a language label, or a word boundary is evidence about `Ω`'s inadequacy, not noise to be adjudicated away. This is Cycle 2's Q-10 made buildable.

Almost no dataset does either. Both are publishable design contributions on their own.

## III.5 — C-18 and F-10: a benchmark *is* an enforced cover

This is the decisive analysis and it is not a worry, it is a match on all four conditions.

If a reference dataset for historical Indic and Perso-Arabic print is published by two people in the United States, and its label set, romanization standard, difficulty strata and evaluation metric are fixed there:

| C-18 condition | satisfied? |
|---|---|
| **(i)** A enforces a cover under which B's states must be reported | **Yes.** A benchmark is definitionally an enforced cover: everyone reports on your test set, in your categories. |
| **(ii)** B's residue is rendered *nonexistent*, not merely unrecorded | **Yes, by default.** Kashmiri n=26, Sanskrit n=22, Multani in single digits. Below any reporting threshold they vanish from every results table forever. |
| **(iii)** `T₂` absent — no forum for category revision | **Yes, by default.** Datasets ship; schemas freeze; a v2 is the maintainers' gift. |
| **(iv)** the frame presents as discovery rather than decision | **Yes.** *"We just transcribed what was there."* |

> **A benchmark is the purest enforced cover the modern research economy produces.** It does not merely describe a field; it constitutes what counts as a result in it.

**Cycle 2 established that the answer to this is constitutional, not methodological** (S-13, F-10). Being careful does not satisfy `T₂`. What does:

- **A versioned schema with a public, binding revision procedure** — and named standing in it for institutions whose scripts these are: Punjab University and GC University Lahore, Punjabi University Patiala, Guru Nanak Dev University Amritsar, Sindh and Kashmir archives. Standing, not consultation. The difference is whether they can force a change.
- **Per-language reporting mandatory, aggregate reporting forbidden.** If the metric can only be reported stratified, the tail cannot be optimised away. This is a one-line rule that satisfies (ii) structurally rather than by good intentions.
- **The romanization published as historical annotation, never as target** (III.2) — so no one is compelled to adopt the colonial orthography to score well.
- **The difficulty strata published as a claim about the scans, not about the scripts** (III.6).

## III.6 — The scanner's frame becomes the field's ground truth

From Part I: at 306 DPI, Gurmukhi sits at 2.0 px clearance and Devanagari at 16.3 px.

**A benchmark built on these scans would encode "Gurmukhi is harder than Devanagari" as a property of the script.** Every model trained on it learns that. Every paper reports it. Every subsequent dataset inherits the difficulty distribution. **A sampling rate chosen decades ago, by someone not thinking about Gurmukhi, would become a durable fact about Punjabi in the machine-learning literature.**

This is S-12 in its most physical form, and it produces a hard prerequisite:

> **CORRECTED 2026-08-19 (E0b).** The recommendation that followed — "re-imaging at 600 DPI is the condition under which a reference dataset can be published" — **is withdrawn.** Measured over 511 crops, 600 DPI removes only 3–5 percentage points of below-floor cases (Gurmukhi 31%→26%, Perso-Arabic 14%→11%). The binding population is **sub-pixel adjacency**: 30% of Gurmukhi marks sit less than one pixel from the letter body at 306 DPI. Whether that is lithographic ink merge in the artefact — which no resolution recovers — or undersampling — which 600 DPI fixes — **is not determinable from these scans.**
>
> **Replacement, decisive and cheap: re-image ~20 pages at 600 DPI, stratified by script, and re-run E0b.** If the clearance-zero population resolves, full re-imaging is justified and its benefit is quantified. If it does not, the ceiling is in the ink and no scanning budget moves it.

**The argument of this section is unaffected and if anything strengthened.** A measured 2.2× script hierarchy — confirmed *within* Punjabi, where only the writing system varies — would still be encoded by a benchmark as a property of Gurmukhi. And now the origin of that hierarchy is *known to be unknown*: it may be the scanner, or it may be how these presses inked Gurmukhi in 1910. **Publishing a difficulty stratification while that is unresolved would fix an undiagnosed artefact as a fact about a script.** Any published strata must be labelled a property of *these images*, in the metric name if necessary, until the pilot settles it.

## III.7 — Q-17: archive → benchmark converts surveillant coarsening into extractive

Q-17 distinguished two imperial modes by documentary signature: **surveillant** coarsening documents its own classificatory failure richly (high gloss rates, long hapax tails — the Punjab register); **extractive** coarsening wants a number and leaves thin residuals.

**An ML benchmark is extractive in form.** It wants CER, WER, a leaderboard. Its residuals are thin by design; everything not scored is discarded.

> **Turning this archive into a benchmark converts a surveillant apparatus into an extractive one — and throws away exactly the descriptive richness that made the archive recoverable in the first place** (`cycle3_reading_the_residue.md` §6: the detail survives *because* the register described rather than merely counted).

The gloss is the register's own surveillance product and it is the reason any of the last three days' findings were possible. **Ship the gloss with every crop.** It costs bytes and it is the difference between a dataset and an extraction.

---

# PART IV — Legibility without transcription

The strongest first move, and it is missing from the agenda.

**You do not need transcription to make the archive searchable.** Segmentation-free word spotting and query-by-example embed crops into a vector space and match a query crop — or a romanized query, via the bilingual anchor — without committing to any orthographic output. It is mature for Perso-Arabic and Indic historical print, it needs far less supervision than recognition, and it degrades gracefully.

Why this matters beyond convenience:

> **Retrieval adds a relation. Transcription substitutes a rendering. Only the second is a coarsening.**

A retrieval index leaves the object intact — the crop is still the crop, the press's own ink — and adds an index over it. A transcription *replaces* the object with a string in a chosen orthography, and every downstream user inherits that choice. Retrieval **defers the frame declaration** rather than making it silently.

Practical consequences:
- **A searchable archive of 4,044 native titles ships without an orthographic standard**, without a language-label fold, and without a benchmark. It is the deliverable Davis and Punjabi/Pakistani researchers can actually use, and it commits nothing.
- The romanization gives free query-side supervision: `roman query → crop` is trainable on the existing pairs without ever emitting native text.
- It is the honest use of the bilingual anchor: **use `φ` to index, not to transcribe.**
- It works at 306 DPI. Word-level embedding is far more tolerant of dot loss than character decoding, because word shape carries most of the discriminative signal. **Retrieval is the task the current scans can actually support.**

This inverts the sequencing in the agenda. **Retrieval first, recognition after re-imaging, transliteration published only as historical annotation.**

---

# PART V — The possibility space, at four scales

**Scale 1 — Punjab 1910–12 (in hand).** 4,044 crop/romanization/gloss/language/date/publisher tuples. Enough for the bilingual-anchored task (agenda §9.1), a retrieval index, and a method paper. **No re-imaging needed for retrieval.**

**Scale 2 — Punjab 1867–1942 (on disk, minus the OCR hole).** ~60,000 tuples across **75 years of one serial**. The unique asset here is not size, it is **diachrony**: lithographic naskh giving way to type (2,747 of 4,502 entries are `litho.` in 1910–12 alone), orthographic reform, script politics, printer turnover. **No longitudinal recognition corpus exists for any Indic or Perso-Arabic tradition.** Models trained on one period fail on another and nobody can currently measure that. This is a research contribution size alone cannot buy.

**Scale 3 — all provinces, SV 412/1–48 (Library 2 Batch 7).** Hundreds of thousands of tuples spanning Devanagari, Bengali, Gurmukhi, Gujarati, Tamil, Telugu, Kannada, Malayalam, Oriya, Burmese and Perso-Arabic in several languages — **all under one document grammar, one Act, one column scheme.** A *controlled* cross-script corpus. Nothing remotely like it exists. It is also agenda §9.6's natural experiment for separating instrument from ecology.

**Scale 4 — the convention itself.** Native script + bracketed romanization + gloss was the standard form of colonial bibliography everywhere: British India, the Dutch East Indies, French Indochina, Ottoman and Russian Central Asian surveys, missionary linguistic surveys. **The supervision signal is latent in every colonial archive that used the convention.** The portable contribution is the *method* — and the governance model that goes with it.

For calibration: OpenITI MAKHZAN, the reference open Arabic-script ground truth, is ~1,500 pages. Scale 1 alone is comparable in aligned pairs; Scale 3 is two to three orders of magnitude beyond it.

---

# PART VI — The case against, taken seriously

**1. The 306 DPI ceiling makes a reference dataset premature.** III.6. Publishing now enshrines a script hierarchy produced by equipment. This is the strongest objection and it has a price tag rather than an argument as its answer.

**2. Two people cannot maintain a reference dataset.** Agenda §10.3 already identifies adjudication as the binding constraint at ~3,000 items for Punjab alone. A benchmark adds permanent maintenance: issues, versions, disputed labels, leaderboard integrity. **`T₂` is not only an ethical requirement — it is the only sustainable maintenance model.** The governance that answers the imperialism objection is the same governance that makes the artefact survivable. *That is the strongest argument for doing it properly rather than for not doing it.*

**3. It may simply not be used.** Most DH datasets sit. Mitigation is not marketing; it is that **the retrieval index (Part IV) has users on day one** — Davis, and anyone working on Punjabi print — where a benchmark has users only if a community forms.

**4. Naming the dead.** The dataset names authors, publishers, and their cities in a print ecology that ended on both sides of a partition. Public-domain status settles the legal question and not the other one. This is real, it is not resolved by a licence, and it is a further argument for standing (III.5) rather than consultation.

**5. The reflexive objection, unresolved.** K-011: making the frame explicit is not the same as transferring authority over it. A beautifully documented dataset whose schema nobody in Punjab can change is a *legible* imposition, not a lesser one. **This does not have an answer inside the artefact. It has an answer only in who holds the pen.**

---

# PART VII — What follows

**Do now, cheap, commits nothing:**
1. **Measure E0 properly** — ~100 crops per script, stratified by decade and litho/type. If the Gurmukhi floor holds, it reframes the whole programme and is publishable on its own.
2. **Build the retrieval index** on the 4,044 crops. Ships a usable archive with zero orthographic commitment.
3. **Adopt the reading-not-truth data model** for romanization (III.2). One schema change, before 1913 is ingested.
4. **Document the OCR hole** in the repo. It bounds Davis's work as much as ours.

**Decide before scaling:**
5. **Cost re-imaging at 600 DPI.** It is the precondition for a reference recognition dataset (III.6), and it is now a number, not a wish.
6. **Draft the governance document before the dataset exists.** Versioned schema, binding revision procedure, named standing, mandatory per-language reporting. **Whether this exists determines whether C-18 (i)–(iv) hold of your artefact.** Write it first; it will change the schema.

**The reframing worth holding onto:**

> The question is not whether colonial data can be used. It is **whether the thing you build has a `T₂`** — whether the people whose scripts these are can force a change to the categories.
>
> Empire's register had none, for anyone, ever. That is what made it imperial, more than its content.
>
> A dataset with a real revision procedure is not a colonial artefact with better manners. It is a **structurally different kind of object**, and the difference is measurable by the one test the three cycles kept returning to: **can the classified change the classification?**
