# cycle3_handbill_trace.md — the hand-bill across the full run, 1867–1942

**Method.** Full-text scan of all 26 volumes of SV 412/44 (`Library 1/Batch 6`) via PyMuPDF text layers. Tolerant regex for OCR-corrupted `hand-bill` / `handbill`, plus institutional and genre-word probes. **10,214 pages scanned, 103 hits.** Artifacts: `dialectic/data/scan_handbills.py`, `dialectic/data/handbill_hits.json`.

---

## 0. The controlling caveat, stated first because it bounds everything

**Four volumes have no text layer at all.** They are scanned images with no OCR:

| volume | pages |
|---|---|
| 1876–80 | 371 |
| 1894–99 | 511 |
| 1900–1903 | 362 |
| 1904–06 | 511 |
| **total** | **1,755** |

**82.8% of the run is searchable. 17.2% is not, and the unsearchable block is a contiguous thirteen-year hole, 1894–1906.**

This was detected by a control — density of high-frequency English words per page — not by inspection. **Any full-text history of Punjab print silently inherits this hole, and nothing in the file names, page counts, or file sizes announces it.**

> **This is S-15 recurring one level up. The digitisation individuates perfectly — every page is imaged — and fails to aggregate: a page with no text layer is invisible to every kind-level query ever run against the corpus. Empire's register was coarsened once by its topic scheme and again, a century later, by an OCR pipeline. The second coarsening is undetectable unless you run exactly this control, and it is not in any documentation.**

Every absence claimed below is qualified by this. No claim of the form "the series stopped" is made for 1894–1906.

---

## 1. Raw distribution

| volume | hits | note |
|---|---|---|
| 1867–75 | 0 | OCR present — genuine absence |
| 1876–80 | — | **no text layer** |
| **1881–84** | **22** | Nos. 1–46 |
| **1885–87** | **20** | Nos. 60–85 |
| **1888–89** | **10** | Nos. 90–104 |
| **1889–91** | **17** | Nos. 106–129 |
| **1891–93** | **10** | Nos. 130–148 |
| 1894–99 · 1900–03 · 1904–06 | — | **no text layer** |
| 1907–08 | 0 | OCR present — see §3 |
| 1908–09 | 0 | OCR present — see §3 |
| **1910–12** | **13** | Nos. 25–37 |
| **1913–15** | **4** | two new publishers |
| 1916–17 | 1 | |
| 1918–19 | 0 | |
| **1920–21** | **3** | |
| 1922–23 | 0 | but see §3 |
| 1924–25 | 1 | |
| 1926–27 | 1 | |
| 1928–29 | 0 | |
| 1930–31 | 1 | |
| 1932–42 | 0 | four volumes, best OCR density in the run |

---

## 2. The first series is Christian missionary, and its numbering is a clock

The 1880s cluster is not the Sikh series. It is the **Punjab Religious Book Society**, printing at the **Ludhiana Mission Press**: a *monthly* numbered hand-bill series in Urdu.

```
Ludhiana. Mission Press. hand-bill, Nos. 1 to 7.
P. R. B. S. monthly hand bill No. 15, Masih ka marna aur uska ji uthna.   [Christ's death and resurrection]
Khuda ki Ruh — Monthly handbill, No. 19.                                  [The Spirit of God]
Gunah aur Shifa'at — Monthly Hand-bill No. 24.                            [Sin and intercession]
Ek shakhs ke masihi hone ka ahwal — Monthly Haud-bill No. 27.             [An account of a Christian convert]
Darakht-i-be samar aur baghban — Monthly Hand-bill No. 30.                [The fruitless tree and the gardener]
```

Numbers recovered per volume, in sequence and without reset:

```
1881–84   1, 8, 13, 15, 19, 20, 22, 24, 30, 33, 36, 37, 40, 43, 44, 45, 46
1885–87   60, 64, 66, 69, 71, 72, 74, 75, 76, 77, 78, 80, 81, 82, 83, 84, 85
1888–89   90, 92, 96, 97, 101, 103, 104
1889–91   106, 108, 109, 112, 114, 115, 116, 117, 119, 120, 121, 125, 126, 127, 129
1891–93   130, 138, 143, 144, 147, 148
```

**No. 1 to No. 148, monotone, across twelve years of a monthly series — 148 months is 12.3 years.** The internal numbering and the external calendar agree to within a few months. **The series is its own clock, and it validates the scan: a numbering this consistent across five separately-OCR'd volumes cannot be regex noise.**

---

## 3. The series did not stop. The register's word for it did.

The apparent collapse after 1893 is two artefacts stacked.

**Artefact one:** 1894–1906 has no text layer (§0).

**Artefact two, and the real finding:** in 1907–09 the OCR is good and hand-bill hits are **zero** — while the **Punjab Religious Book Society appears 7 and 14 times** in those same volumes, publishing the same kind of object:

```
1908  [Asma-i-Ilahi. Certain names of God with explanation of their meanings.] Pp. 12.
      Published by the Punjab Religious Book Society, Lahore.  8°, litho., 2nd edition. Price, 3 pies.
1908  [Sachcha Islam. This book teaches that Christ is the only saviour…] Pp. 12.
      Punjab Religious Book Society, Lahore.  8°, litho., 3rd edition. Price, 3 pies.
```

And by 1922 the same publisher is running a **numbered series again — under a different genre word, with the numbering restarted**:

```
1922  [No. 2, Bara Kaun Hai. A pamphlet attempting to show that he is great who follows
       Christ in self-sacrifice.] Pp. 16. The Punjab Religious Book Society, Lahore. 16°, litho.
1922  [No. 3, Mera Qarz Kaun Bharega… Pamphlet No. 3, attempting to show that Christ came
       to clear off the debts of man towards God.] Pp. 8. The Punjab Religious Book Society, Lahore.
```

Same publisher, same city, same format (16°, litho, 8–16 pp), same evangelical function, same numbered-series structure. **Called "hand-bill" in 1885 and "pamphlet No. 3" in 1922.**

Institutional presence of the Society across the run confirms continuity independent of any genre word: **1885 · 1889 · 1891–93 · 1907–08 (7) · 1908–09 (14) · 1910–12 · 1913–15 · 1916–17 · 1918–19 · 1920–21 (8) · 1922–23 (19) · 1924–25 (9) · 1926–27 (16) · 1928–29 · 1930–31 · 1932–35 · 1936–38 · 1941–42.** Continuous, 1885 to 1942.

Meanwhile `tract` is the register's *stable* genre word — 196 occurrences in 1867–75, 150+ in 1910–15, 105 in 1930–31, 124 in 1932–35 — present throughout, while `hand-bill` flickers on for twelve years, off for twenty, and on again for twenty.

> **The object persisted for sixty years. The register's name for it did not, and neither did its numbering. No query on any single description recovers the series. Only the publisher string does — and the publisher string is itself variant.**

This is the sharpest confirmation of S-15 available: **loss of kind, not of detail, demonstrated longitudinally.** Every individual item is recorded, accurately, with a description. The *series* — the thing that has a strategy, a budget, a doctrine and a fifty-year existence — is not an object the register can hold, and its own vocabulary drifts enough to hide it from anyone searching the register on the register's terms.

---

## 4. The word migrates, and the migration is the history

`Hand Bill Committee` as a phrase occurs in **exactly one volume in the entire run: 1910–12, 8 times.** The word `hand-bill` detaches from the mission and reattaches, and what it attaches to, in order:

| date | publisher | content |
|---|---|---|
| 1881–93 | **Punjab Religious Book Society**, Ludhiana Mission Press | monthly evangelical tracts, Urdu, Nos. 1–148+ |
| 1910–12 | **The Sikh Hand Bill Committee, Lahore** | Sikh moral reform, Punjabi, Nos. 25–37, **20,000–30,000 copies each** |
| 1913 | *(Ahmadi, inferred)* — recorded only as *"Mirzai Sahiban ke Handbill No. 10 ka Jawab"* | a **refutation** of a Qadiani hand-bill: the Ahmadiyya were running their own numbered series |
| 1914 | **Gurmat Handbill Pracharak Agency, Amritsar** | *"Hand bill No. 1, October 1914, in praise of Guru Nanak"* — 4,000 copies, **free** |
| 1917 | Church Mission High School master, Amritsar | temperance |
| 1920 | **Sikh Sahayak Sabha, Baramula (Kashmir)** | *"Avidiya te bharm da jal, No. I"* — spread of education among Sikhs |
| 1920 | *(Sikh)* | *"Eh tan garki ai. Handbill on the uplifting of the depressed classes and their conversion to Sikhism."* |
| 1926 | *(Muslim)* | possibility of a prophet after Muhammad — the Ahmadi controversy |
| 1930 | *(Sikh, intra-communal)* | *"A contradiction to the handbill issued by a member of the Dhan Pothohar Sabha, Amritsar."* |

**The Sikhs did not merely adopt the missionary printing form. They adopted its name**, constituting a body called *The Sikh Hand Bill Committee* — self-conscious appropriation of an evangelical apparatus, label included.

And the content arc across fifty years is a single trajectory:

> **inter-religious conversion (mission, 1880s) → intra-communal moral reform (Singh Sabha, 1910s) → competitive conversion of the depressed classes (1920) → intra-communal factional attack (1930).**

A communication technology enters Punjab as a tool for converting others, is taken up by each community in turn, and is progressively turned inward — first on one's own community's morals, then on the unaffiliated as a demographic prize, then on one's own faction. **That is homogenisation legible as a genre history**, and it is Davis's research question 1 traced through a single word across sixty years of the coloniser's own paperwork.

The 1920 entry — *"the uplifting of the depressed classes and their conversion to Sikhism"* — sits exactly on the census-community arithmetic that drove Punjab's communal consolidation.

---

## 5. What the register did with all of this

Every item above was recorded, described accurately, and classified. In the structured slice (1910–12), the Sikh Hand Bill Committee's series was distributed across **`Miscellaneous` (8), `Poetry` (1), `Fiction` (1)**, and the publisher fragmented into **five spelling variants**.

Across the full run there is **no point at which the register has a category for the hand-bill, for a numbered series, or for a publisher's campaign.** It has categories for Poetry, Religion, Language, Fiction, Law, Medicine, Biography, Science, History, Drama, Art, Philosophy — for *works*. It never acquires one for the thing that ran through its own pages for sixty years at tens of thousands of copies an issue.

---

## 6. Limits — none of these are recoverable by more scanning

- **The 1894–1906 hole is total** (§0). Nothing here describes those thirteen years.
- **Recall is unknown and certainly incomplete.** The scan finds English-language descriptions containing a recognisable `hand-bill`. Items the Reporter called *tract*, *leaflet*, *pamphlet*, or *ishtihar* are invisible to it — and §3 shows that is exactly what happened after 1907. **The trace under-counts the phenomenon by construction, and the size of the undercount is the finding.** The only recall check available: in 1910–12, where both a structured extraction and the raw scan exist, the scan recovered a comparable number of items to the database (13 hits vs. 12 matching entries). That validates the method on a well-OCR'd volume and says nothing about the others.
- **Ahmadi attribution in 1913 is inferred** from a refutation's title, not from a registered Ahmadi entry. The counter-series is attested only through its opponent.
- **Copies are supply.** 20,000 hand-bills is a committee's decision about paper, not 20,000 readers.
- **No causal claim about Partition.** The trajectory in §4 is a description of what is in the register.

---

## 7. Consequences

**For the project.** The series-level entity is now demonstrably necessary and demonstrably not derivable from any single field. Publisher-string variants, genre-word drift, and numbering resets each defeat a different naive query. **Building the aggregates the register lacked is not an optional enrichment; it is the only way the object becomes visible at all.** And the OCR hole must be documented in the repo — it silently bounds every full-text claim anyone will ever make against this corpus, including Davis's.

**For the apparatus.** S-15 is confirmed longitudinally and extended: the loss of kind is not only synchronic (no category for the series) but **diachronic — the register's own kind-vocabulary drifts, so that even the descriptions do not aggregate across time.** A residual category is a failure of extension; genre-word drift is a failure of *identity through time*. They are different failures and only the second is invisible to a single-year analysis.

**New question, Q-18:** does genre-word drift correlate with the arrival of a competitor? `Hand-bill` becomes unavailable to the mission's own series at roughly the moment other communities take up the name. Whether a register's vocabulary drifts *because* a term is being contested is testable across the run — and if it is, then **the classification scheme is not merely failing to see the mobilisation; it is being moved by it.**
