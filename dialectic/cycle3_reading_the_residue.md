# cycle3_reading_the_residue.md

**The dig:** F-05 treats residuality as a *count* — how much falls into "other." That was always the weak form. In this corpus the residue is not a count. It is **967 pieces of prose**, each one the Reporter's own description of a work his scheme could not name. The question worth asking is not *how much* was residual but **what was in it, and whether the excluded world is recoverable from inside the excluding apparatus.**

Cycle 2 (S-11) said: under coarsening the obstruction vanishes and the loss relocates into residuals. It did not say whether relocated loss is *recoverable* or merely *countable*. This tests that.

---

## 1. Method, declared before results (S-12 applied to me)

I built keyword classifiers over `title || gloss`. **Those classifiers are my `κ`.** They were induced by reading contrastive term statistics and then samples, which means:

- The **coverage figure (61%) is inflated by construction** — clusters were fitted to the data they are then measured on. It is an upper bound on structure, not an estimate. It requires validation on a held-out quarter before publication.
- The **concentration figures are not** so vulnerable: one fixed classifier applied to *all* topics equally, comparing where marked entries land. Those comparisons are legitimate.

Everything below distinguishes the two.

---

## 2. The residue is not noise

Log-odds of terms in `Miscellaneous` glosses against all other topics (min. 12 documents):

```
prospectus   5.37   dera       5.34   musketry   5.06   report      4.94
salana       4.91   almanac    4.79   annual     4.66   limited     4.59
pathshala    4.51   association 3.86  geography  3.52   regulations 3.45
jughrafia    3.35   anjuman    2.76   sabha      2.65   conference  2.76
proceedings  2.45   mutual     2.35   articles   2.16   society     2.10
```

`prospectus`, `dera`, `musketry`, `salana`, `almanac`, `pathshala`, `limited` appear **zero times** outside the residual category. These are not stray words. They are the vocabulary of a coherent world.

Decomposition into eleven named clusters (first-match; 61.0% covered — **upper bound, see §1**):

| cluster | n | % of Misc |
|---|---|---|
| **Polemic / social-reform tract** | 192 | 19.9% |
| **Associational / corporate document** | 128 | 13.2% |
| Schooling / textbook | 58 | 6.0% |
| Letter-writing / clerical | 53 | 5.5% |
| Almanac / astrology / charms | 44 | 4.6% |
| Geography / gazetteer | 43 | 4.4% |
| Self-help / vocational | 18 | 1.9% |
| Military / police / drill | 17 | 1.8% |
| Hygiene / domestic | 16 | 1.7% |
| Commercial / trade print | 15 | 1.6% |
| Dictionary / reference | 6 | 0.6% |

The uncovered 377 are not a different sort of thing. Sampled: essay collections, harmonium instruction, riddle books, ready reckoners, price lists, botanical description sheets, and *"An Urdu translation of Smiles' 'Self Help' by Hasan Ali"* — filed under Miscellaneous.

> **Every cluster is a modern print genre. Not one of them is a literature.**

The topic scheme — Poetry, Religion, Language, Fiction, Law, Medicine, Biography, Science, History, Drama, Art, Philosophy, Politics, Travel — is a scheme for **works**. The residue is entirely **documents**: pamphlets, reports, prospectuses, price lists, primers, almanacs, hand-bills, forms.

> **`Miscellaneous` is the boundary between the world of works and the world of print. The scheme could see a literature and could not see a public.**

This is the orientalist-philological carving in operation: it expected a native literature with the genres a colonial scholar knows how to want, and encountered a print public generating tracts and paperwork.

---

## 3. The scheme can name religious dispute and cannot name social reform

Two fixed classifiers, applied identically across all topics.

| topic | n | doctrinal-marked | social-reform-marked |
|---|---|---|---|
| Religion | 774 | **58.5%** | 1.4% |
| Miscellaneous | 967 | 16.0% | **4.9%** |
| Poetry | 1,390 | 24.0% | 3.3% |

Where each kind of entry ends up, corpus-wide:

- **Doctrinal dispute → Religion 41.9%, Miscellaneous 14.4%**
- **Social reform → Miscellaneous 38.5%, Religion 9.0%**

> **Social-reform print is 4.3× more likely to be classed as residue than as Religion.** The register could hold a controversy about the Prophet or the Vedas. It had no place for a tract on widow remarriage, female education, caste, temperance, or child marriage.

This is not a gap in coverage. It is a statement about what the apparatus took the natives to *have*: doctrines, poems, and law — not a reform politics.

---

## 4. The residue is the largest thing in the register

| topic | entries | copies | share of all copies | mean run | median |
|---|---|---|---|---|---|
| **Miscellaneous** | 965 | **1,882,720** | **27.1%** | 1,951 | 1,000 |
| Poetry | 1,390 | 1,758,374 | 25.3% | 1,265 | 1,000 |
| Religion | 773 | 1,136,294 | 16.4% | 1,469 | 1,000 |
| Language | 271 | 840,700 | 12.1% | 3,102 | 1,000 |

**21.5% of entries. 27.1% of all registered copies.** The residual category carries more paper than any named category, including Poetry, on 30% fewer entries.

Medians are 1,000 across the board — a printing convention — so the difference lives entirely in the upper tail. The upper tail is almanacs (100,000 copies), a school geography (50,000), a musketry scoring book (30,000) — and this:

```
 30,000  Hand Bill No. 33, "Sachi Yadgar"          1911Q1  Punjabi
 20,000  Hand Bill No. 25, "Sidak de Bere Par"     1910Q3  Punjabi
 20,000  Hand Bill No. 27, "Apne Augun"            1910Q3  Punjabi
 20,000  Hand-bill No. 28, "Wah! Bhaiji! Wah!"     1910Q4  Punjabi
 20,000  Hand-bill No. 30, "Hai Kal"               1910Q4  Punjabi
 20,000  Hand Bill No. 31, "Mapian de Ladale"      1911Q1  Punjabi
 20,000  Hand-Bill No. 35, February 1911, "Holi"   1911Q2  Punjabi
 20,000  Hand Bill No. 37, "Sachcha Vakhkhar"      1911Q3  Punjabi
```

---

## 5. The case: the Sikh Hand Bill Committee, Lahore

A **numbered, dated, serialized mass-distribution campaign**. Nos. 25–37 appear within this three-year window; the numbering shows the series both precedes and outruns it. Ten entries captured by keyword: **174,000 copies.** Subjects: gambling, the celebration of Holi, indulgent parenting, worldliness, resignation to God, self-examination, the value of knowledge — a sustained programme of Sikh social reform aimed at a mass Punjabi readership.

Three facts about how the register handled it:

**(a) The series is split across three topics.** Eight entries to `Miscellaneous`, one to `Poetry`, one to `Fiction` — assigned by each item's surface content, because **the scheme has no context in which "which series is this?" is an askable question.** There is no global section assigning a topic to the series. This is contextuality on a real object: local assignment succeeds every time, global assignment does not exist.

**(b) The publisher fragments into five strings.** *The Sikh Hand Bill Committee* / *The Sikh Hand-bill Committee* / *The Sikh Hand bill Committee* / *The Sikh Hand Bill Committee, Lahore* / a joint imprint with *The Khalsa Dewan, Maghiana*. `norm_publisher` did not fold them. **The apparatus that cannot see the campaign as a kind also cannot see the committee as one actor** — and the project's own normalization layer currently reproduces that. *(Actionable: `aliases.json` case.)*

**(c) Nothing was missed.** The Reporter read every hand-bill and wrote an accurate one-line description of each. There is no failure of observation anywhere in this record.

---

## 6. The theoretical result

> **S-15. Enforced coarsening destroys kinds, not details.**

The register saw every item. It described each one accurately. What it could not do was **aggregate** — there is no predicate in its `Ω` under which 174,000 copies of a single committee's numbered campaign fall together. The record survives; the kind does not.

This gives S-11 a mechanism and corrects F-05's weak form:

- **F-05 as stated** measures residual *load* — a count. That measures how often the carving fails.
- **F-05 corrected** must measure **loss of aggregability**: the residue's internal structure, and whether objects that belong together in the world are separable within the scheme.

The corollary is the important one. **Power operates on aggregates** — counts, trends, kinds, threats. A classification that individuates perfectly and aggregates wrongly produces an apparatus that **sees everything and knows nothing**. The Punjab register is that apparatus, and this is a sharper account of imperial epistemic failure than "empire simplifies." Empire did not simplify here. It described in detail, at scale, for seventy-five years, and could not name what it was watching.

**And this is why the recovery is possible at all.** The detail survives *because* the apparatus was descriptive rather than merely enumerative. An extractive register that recorded only counts would leave nothing to read back.

> **Q-17's surveillant arm moves from *consistent with* to *supported by* evidence.** Surveillant coarsening documents its own classificatory failure in detail, and that documentation is the condition of its later critique. **The register's thoroughness is what makes it possible to use its own product against its categories.**

That is immanent critique in the strict sense, executed rather than proposed — and it is a worked answer to the source paper's closing question. Not a better model of the apparatus. **The apparatus's own record, read against its own scheme.**

---

## 7. What must not be claimed

- **Copies are supply, not readership, not literacy, not belief.** Every figure above is a fact about the *register*, not about Punjab. 20,000 copies is a committee's decision, not 20,000 readers.
- **Three years.** 1910–1912 is drift, not a coarsening event. No F-09 claim is made here.
- **The clusters are mine.** §1. The 61% is an upper bound and needs held-out validation.
- **The Reporter was not blind.** He was accurate and thorough. The failure is in `Ω`, not in observation, and conflating the two would lose the entire finding.
- **No causal claim about Partition is made.** The reform and communal-polemic print of 1910–12 is the print of the associational formations that later hardened; that is a description of what is in the register, not a demonstration of a causal path.

---

## 8. What this hands the project

1. **A defensible research claim** with the evidentiary scope stated: the imperial print register's topic scheme was cut for a literature and could not represent an associational and reformist print public, which was by volume the largest thing it recorded.
2. **Davis's question 1, with an instrument.** The associational and communal-reform print that fed the formations of Partition is *in* the register and *invisible to* its scheme — recoverable only from the residue. That is a route into "the poverty of homogeneity" that runs through the coloniser's own paperwork.
3. **Thomas's question 3, executed.** The registry as observation operator, characterized: `Ω` cut for works, `φ` (the gloss) translating for vernaculars and citing for English, markedness naming Urdu-in-Persian-character as the unmarked centre, and the residue carrying the largest volume of print in the province.
4. **A normalization decision that cuts against the current plan** — again. Do not fold the hand-bill publisher variants silently: record the fold *and* keep a series-level entity, because the series is the object the register could not hold and the project now can. Same logic as the polyglot tail (`cycle3_corpus_encounter.md` §7): **the project's job is to build the aggregates the register lacked, not to reproduce its individuation.**
5. **The next runnable test:** extend the hand-bill trace to the full 1867–1942 run. A numbered series with dated issues is a rare gift — it gives a continuous, self-indexing thread through seventy-five years of a classification scheme, and the gaps in its numbering are a direct measure of registration compliance and of the register's own attention.
