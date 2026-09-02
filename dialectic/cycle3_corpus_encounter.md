# cycle3_corpus_encounter.md — Q-16 answered against a real corpus

**Corpus:** *Catalogue of Books registered in the Punjab under Act XXV of 1867 and Act X of 1890*, quarterly, India Office SV 412/44. Currently ingested: **4,502 entries, 6,944,051 registered copies, twelve quarters, 1910–1912.** Full run 1867–1942 on disk.

All figures below are from `punjab.db` as of this session and are reproducible from the queries recorded here. Nothing in this file is inferred from the project's prose; every number was computed.

---

## 1. Q-16's four questions, answered

**(1) Who made it, for whom, to settle what?**
The colonial state, through the Reporter on Books, under the Press and Registration of Books Act XXV of 1867 — legislated a decade after 1857. This is a **registration and surveillance instrument in bibliographic form**. Legal deposit is its mechanism; monitoring vernacular print is its function.

**This corpus is not data produced by empire. It is empire's carving apparatus, preserved in operation.** That is a much stronger position than Q-16 anticipated, and it changes what the apparatus can do here. `κ` is not something to be reconstructed from outputs — `κ` is the document.

**(2) One regime or two?** Nominally one. In practice this corpus carries **three usable second covers**, which is unusual:
- **the gloss column** — the Reporter's rendering of each work into English (present on 4,046 of 4,502 entries). This *is* `φ: Ω_vernacular ⇀ Ω_administrative`, written down, per record.
- **`title_native` beside romanisation** — 4,044 native-script titles printed next to their own romanisation. A translation pair per record.
- **its own diachronic drift** — the catalog's category vocabulary changes year to year (§4).

**(3) Version history of its own categories?** Yes, and at annual resolution across a 75-year run.

**(4) Does it record what it refused or could not classify?** Yes, in three distinct residues (§2, §3, §4).

> **Verdict: this corpus can carry both halves of the apparatus.** The residuality half (F-05, F-08, F-10) runs on the catalog directly. The cover half (F-06, F-09) runs on the gloss and on the diachronic category vocabulary. The blocking condition in Q-16 is discharged.

---

## 2. The catalog's cover is `language × topic`, and it is literally sectional

The `section` field is the printed section heading. Its form is `LANGUAGE—TOPIC`:

```
URDU—MISCELLANEOUS—CONTINUED.            249
PUNJABI—POETRY—CONTINUED.                222
PUNJABI (IN THE PERSIAN CHARACTER)—POETRY—CONTINUED.   97
URDU—RELIGION.                            57
```

**Each section is a context in the sheaf sense** — a set of records over which a determinate set of questions is jointly askable. The cover `𝓜` is not a modelling choice imposed by us. **It is printed on the page.** F-06's most contestable assumption — that contexts supply a determinate local question-set — is here *given by the source* rather than declared by the analyst.

This is the first time in three cycles that a formal object has been found in the world rather than proposed for it.

---

## 3. Two residues, and they do not identify the same population

`Miscellaneous` is the topic scheme's residual category: **967 of 4,502 = 21.5%**, the second-largest topic after Poetry.

`char` (script annotation) is blank on 3,937 of 4,502. It is filled in **only when the script is not the assumed default**. Markedness is therefore directly measurable.

| norm_lang | n | `Miscellaneous` | `char` annotated |
|---|---|---|---|
| Urdu | 1,875 | **31.0%** | **0.7%** |
| Punjabi | 1,486 | **13.7%** | **28.9%** |
| Hindi | 228 | 26.3% | 13.6% |
| English | 268 | 26.1% | 0.0% |
| Sindhi | 64 | 15.6% | 28.1% |
| Arabic | 58 | 5.2% | 0.0% |

**Findings.**

**(a) The unmarked default is Urdu in the Persian character.** At 0.7% annotation over 1,875 entries, Urdu's script is simply assumed. Punjabi is annotated 29% of the time because Punjabi could be Gurmukhi *or* Persian character and the catalog treats that as requiring specification. **Markedness is the operator, and it names the centre by refusing to name it.**

**(b) The naive prediction is refuted.** Residual-category load does *not* concentrate on the subordinated group. Urdu — the administrative vernacular, the unmarked default — carries **more than twice** Punjabi's `Miscellaneous` rate. The reason is visible in the topic profiles: Punjabi print is 62% Poetry, and Poetry is a category the scheme has. Urdu print is diverse — commercial, legal, medical, polemical — and the scheme was built for a scholarly-orientalist literature (Poetry, Religion, Language, Law, Medicine, Biography, History, Drama, Philosophy).

> **The residual category does not mark who is marginal. It marks where a specific carving fails.** Different carvings fail on different populations.

**(c) The two residues are orthogonal, and this vindicates K-004 empirically.** Punjabi fits the topic scheme and strains the script scheme; Urdu fits the script scheme and strains the topic scheme. Bundling `Ω` into one "lifeworld" measure would average these and see nothing. **The Cycle 1 prohibition on bundling `(Ω, Π, Σ, Γ)` was derived from theory; here it is a measured fact about one field of one register.**

*Honest limit:* the anti-correlation is not clean across all languages — English is unmarked in script (0%) *and* high in `Miscellaneous` (26.1%). The defensible claim is the weaker and sufficient one: **the two residues are not the same residue and do not select the same population.**

---

## 4. The language field is a classification that has given up

62 distinct `norm_lang` values. **Four of them (Urdu, Punjabi, English, Hindi) hold 3,857 entries — 86%.** Fifty multi-language categories hold **408 entries between them**, most with a count of 1:

```
Bilingual (Persian in the Gurmukhi character and Punjabi)      1
Bilingual (Arabic and Punjabi in the Persian character)        1
Polyglot (English, Urdu, Gurmukhi and Nagari)                  1
Hindi, Sanskrit, Punjabi, Urdu and English                     1
English, Urdu, Persian, German, Italian, French, Russian, He…  1
```

A category system in which fifty categories hold one item each has **stopped classifying and started describing.** The tail is not a set of categories; it is the register writing down, one at a time, what its scheme cannot absorb.

**This is the residue in the *cover* half rather than the residuality half**, and it is where a multilingual print culture is visible precisely through the apparatus's failure to reduce it. `Ω_A ≇ Ω_B` is not argued here. It is on the page as a run of hapax legomena.

**Diachronic drift** (Q-16 point 3), language categories per year: **34 → 43 → 41**. New combinations appear as encountered — eleven categories are unique to 1912.

*Caveat, stated rather than smoothed:* the topic vocabulary's apparent growth (24 → 18 → 27) is substantially print/extraction corruption — `Foetry`, `Peotry`, `Potery`, `Medicines`, `Science Mathematical` vs `Science (Mathematical)`. **Diachronic cover analysis on this corpus must separate genuine category invention from typographic variance before any F-09 claim is made.** The language tail does not have this problem; the polyglot strings are too specific to be corruption.

---

## 5. The gloss is `φ` written down — and it is two operations under one column name

Gloss present on 4,046 of 4,502; mean length 83 characters. Rate by language:

| norm_lang | glossed |
|---|---|
| Sindhi | 96.9% |
| Punjabi | 96.4% |
| Urdu | 93.0% |
| Hindi | 85.5% |
| Arabic | 63.8% |
| **English** | **34.7%** |

**The Reporter glosses what is opaque to the imperial reader and leaves transparent what is not.** English needs no rendering; it is the language the apparatus thinks in.

But the rate understates it. Reading the glosses shows **two structurally different operations sharing a column**:

- **Vernacular gloss = narrative retelling.** *"The well-known love story of Sohni and Mahinwal. Mirza Izzat Beg, son of a rich merchant of Bukhara, came in Gujrat (Punjab) and fell in love with Sohni, a beautiful daughter of a potter…"* The work is *replaced* by a précis in the administrative language. The reader never needs the original.
- **English gloss = bibliographic extension.** *"[Containing a description of the station, routes to Dalhousie…, extracts from Municipal Bye-Laws, &c. Compiled by Captain J. B. Hutchinson; revised by H. A. Rose, C. S., Assistant…"* Subtitle, compiler, provenance. The work is *cited*, not replaced.

> **Translation for the vernaculars; citation for English. One field name, two operations, and the difference is exactly the difference between being rendered and being referenced.**

This is the cleanest empirical instance of `φ_{B→A}` in the project, and it makes the anthropologist's Cycle 1 objection concrete: the gloss is a *total function into `Ω_A`* applied to 96% of Punjabi entries. Whatever in those works does not survive précis in English prose is not recorded as lost. It is not recorded.

---

## 6. What this does to the Cycle 3 focal proposition (C-18)

C-18 defined empire as enforced coarsening + residue-as-nonexistent + absent `T₂` + frame-presenting-as-discovery, and flagged its own scandal: **no violence, no extraction — it cannot distinguish the Colonial Office from ISO.** Defence (b) was that coarsening is the mechanism converting extraction into administration, predicting that coarsening precedes or accompanies the stabilisation of extraction.

**This corpus is a hard case for defence (b) as stated.** Book registration extracts nothing from printers. Act XXV of 1867 follows 1857; its function is **intelligence and control**, not revenue. Conditions (i)–(iv) hold in full, and the extraction term is absent.

Two options, to be attacked rather than chosen now:
- **(b′) Weaken the genus from extraction to domination.** Coarsening is how *domination* becomes administration. Cost: "domination" is vaguer than "extraction" and the definition loses its grip on political economy entirely — it may become unable to exclude any bureaucracy.
- **(b″) Distinguish extractive from surveillant coarsening as two imperial modes with different signatures.** The cadastral survey coarsens *in order to* take; the book register coarsens *in order to* see. Prediction, testable on this corpus against a land-revenue corpus: **surveillant coarsening produces high gloss rates and rich residual description (it wants to understand what it cannot classify); extractive coarsening produces low gloss rates and thin residuals (it wants a number).** The 96% vernacular gloss rate and the 50-category polyglot tail are consistent with a surveillant apparatus that *documents its own classificatory failure in detail* — which an extractive one has no reason to do.

**(b″) is the more interesting hypothesis and this corpus can test half of it now.** It requires a paired extractive register (settlement or land-revenue records) to test the other half. Logged as Q-17.

---

## 7. S-12 applied to this project

The apparatus must be turned on the project before it is turned on the catalog. The project has:

- `aliases.json` — a language-folding table, extended by **+59 entries across 1911–1912 ingestion**
- `norm_lang`, `norm_printer`, `norm_pcity`, `norm_publisher`, `norm_pubcity` — a second carving layered over the catalog's
- `DECISIONS.md` — **a numbered log of every fold, with reasons**

> **This is a rare condition: the project has a written record of its own frame declaration.** The five-step S-12 procedure — what was declared, by whom, revisable by what, contestable by whom, what has no place — is answerable here for the *researcher's* `κ` as well as the *Reporter's*. Almost no computational-historical project can do that.

It also means the project has its own live residue. The three 4+-language polyglot values "left verbatim pending a rule" are **the researcher's `Miscellaneous`**, currently unresolved and correctly flagged in PLAN.md §2 as needing a decision. By the argument of §4, the right decision is **not** to fold them: the hapax tail is the signal, and folding it would perform on the record the operation the project exists to observe.

**PLAN.md's stated risk — "normalization overreach: folding categories the catalog genuinely distinguished" — is S-12 as an operational worry, arrived at independently and before this apparatus existed.** That is the second convergence of the cycle, and it is worth more than the first.

---

## 8. What runs now, and what does not

**Runs on ingested data, no new work:**
- F-05 residuality, at annual resolution, on two independent carvings (topic and script markedness).
- F-10 `T₁`/`T₂`: the catalog offers registrants **no contestation of category at all** — neither token nor type. There is no appeal against being classed `Miscellaneous`. This is level-2 colonization in its pure form, and the measurement is a documented absence rather than a rate.
- The markedness/default analysis (§3a) — a direct measurement of which lifeworld the frame was cut for.

**Runs after separating typographic variance from genuine category invention:**
- F-09 diachronic coarsening on the language tail. **Requires the full run, not three years.** 1910–1912 shows drift, not a coarsening event. Candidate real events lie at the boundaries: post-1919, and the 1930s–1942 approach to Partition — which is Davis's research question 1.

**Does not run without a second corpus:**
- The extractive/surveillant contrast (b″), Q-17.

**Must not be claimed:** print runs are publisher supply decisions under legal deposit. Not readership, not literacy, not belief. The README states this; the apparatus must not quietly relax it. Every residuality finding above is a finding about **the register**, not about Punjab.
