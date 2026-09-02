# cycle3_q18_genre_vocabulary.md — Q-18 run

**Question.** Does the register's genre-vocabulary drift *because* a term is being contested?

**Answer.** Yes, and the mechanism is larger than the question. The words do not merely change hands. **They partition the communities.** The register has no field for religious community; its genre vocabulary became one.

**Method.** All 22 OCR-bearing volumes, 8,459 pages. Every occurrence of eight genre words; a context window around each; community attribution by marker regex (Christian / Sikh / Muslim / Hindu), argmax with a margin requirement, else `MIXED`/`NONE`. Two controls, both essential and both passed — §2. Artifacts: `dialectic/data/q18_*.json`, scan scripts in scratchpad lineage.

**The classifier is mine (S-12).** Community markers are regexes I wrote; `guru`, `dharm`, `diwan` are genuinely ambiguous across communities. The results below survive because the *controls* discriminate, not because the classifier is good.

---

## 1. The result

Community mix of each genre word's contexts, against the volume's background mix. Tight window (±80 chars, mostly within a single entry).

### `tract` — the Reporter's word, handed from mission to Singh Sabha

| volume | n | CHR | SIKH | MUS | HIN | background CHR/SIK/MUS/HIN |
|---|---|---|---|---|---|---|
| 1867–75 | 108 | **77%** | 6 | 12 | 6 | 29/16/35/20 |
| 1881–84 | 78 | **81%** | 3 | 8 | 9 | 19/19/38/23 |
| *1894–1906* | — | — | — | — | — | **no text layer** |
| 1907–08 | 29 | **0%** | **97%** | 0 | 3 | 7/22/51/21 |
| 1908–09 | 35 | **0%** | **97%** | 0 | 3 | 19/19/43/20 |
| 1910–12 | 93 | 5 | 69% | 8 | 18 | 8/29/40/24 |
| 1913–15 | 87 | 7 | 66% | 10 | 17 | 6/31/40/24 |
| 1920–21 | 47 | 28 | 64% | 2 | 6 | 12/23/46/19 |
| 1926–27 | 27 | 4 | **93%** | 4 | 0 | 4/22/47/26 |
| 1930–31 | 56 | 2 | 34 | 38 | 27 | 3/24/53/19 |
| 1932–35 | 66 | 6 | 30 | 42 | 21 | 4/19/63/14 |

**From 81% Christian to 97% Sikh, with Christian falling to zero, against a background that never exceeds 30% Sikh.** Then dispersal after 1930.

### `risala` — the publishers' word, closing to a single community

| volume | n | CHR | SIKH | MUS | HIN | background |
|---|---|---|---|---|---|---|
| 1867–75 | 39 | 5 | 13 | 67 | 15 | 29/16/35/20 |
| 1881–84 | 30 | 7 | 10 | 57 | 27 | 19/19/38/23 |
| 1891–93 | 34 | 9 | 12 | 76 | 3 | 15/15/50/20 |
| 1910–12 | 13 | 0 | **0** | 69 | 31 | 8/29/40/24 |
| 1913–15 | 20 | 0 | **0** | 85 | 15 | 6/31/40/24 |
| 1920–21 | 9 | 0 | **0** | **100** | 0 | 12/23/46/19 |
| 1926–27 | 11 | 0 | **0** | **100** | 0 | 4/22/47/26 |
| 1930–31 | 11 | 0 | 9 | 91 | 0 | 3/24/53/19 |

Cross-communal and only moderately over-indexed in the 1880s; **Christian and Sikh at literal zero after 1910.**

### `hand-bill` — 60% Christian (1881–84) → 100% Sikh (1910–12)

n is small (10 and 7 at tight window) but the values are absolute and agree with the independent trace in `cycle3_handbill_trace.md`.

### `pamphlet` — the administrative word that fills the gap

Rises from 16 occurrences (1867–75) to 191–210 (1908–12) and stays high. Its community mix **tracks background** throughout, drifting Sikh only in 1918–21 and 1928–31. It is the general-purpose English term the register reaches for as the older words close.

### Frequency, all volumes

```
vol          tract  pamphlet  risala  hand-bill  booklet  circular
1867-75        203        16     103          0        0        33
1881-84        108        23     143         27        0         2
1889-91         38        18     188         18        0         0
1891_1893       66        25     128         10        0         0
1907-08         41        61      47          0        0        58
1908-1909       61       191      58          0        6        16
1910-1912      151       210      43         13       55        12
1913-1915      152        71      68          4        0        16
1922-23         46       100      57          0       12        10
1926-27         49       114      45          1       77         5
1930-31        105       113      23          1       42         1
1941-42         31         8      12          0        1         5
```

**`risala` 188 → 12. `pamphlet` 16 → 210. `booklet` 0 before 1908 → 77 by 1927.** The register's genre vocabulary de-vernacularises across 1907–1912.

---

## 2. The two controls, which are what make this a result

**Control A — null words.** `edition` and `price` have no communal valence. If the effect were an artefact of *where on the page* a word occurs — the catalog is sectioned by LANGUAGE, and Punjabi sections are Sikh-heavy — null words would show the same concentration.

| 1907–08 | CHR | SIKH | MUS | HIN |
|---|---|---|---|---|
| background | 7 | 22 | 51 | 21 |
| `edition` (n=267) | 13 | 23 | 52 | 12 |
| `price` (n=295) | 4 | 22 | 59 | 15 |
| **`tract` (n=29)** | **0** | **97** | **0** | **3** |

Null words track background almost exactly, in every volume, at both window sizes. **The section-position confound is ruled out.**

**Control B — window tightening.** A neighbouring-entry artefact must *weaken* when the window shrinks from ±260 to ±80 characters. It does the opposite:

| | wide (±260) | tight (±80) |
|---|---|---|
| `tract` 1907–08 | 94% Sikh | **97%** |
| `tract` 1926–27 | 81% Sikh | **93%** |
| `risala` 1920–21 | 91% Muslim | **100%** |
| `risala` 1926–27 | 87% Muslim | **100%** |
| `edition` (all) | ≈ background | ≈ background |

**Sharpening under tightening is the signature of a genuine per-entry association.** The confound is excluded from both directions.

---

## 3. Two mechanisms, separated by where the word lives

The structured 1910–12 slice records the romanised **title** (the publisher's own words) separately from the **gloss** (the Reporter's). That separates authorship:

| word | in TITLE | in GLOSS |
|---|---|---|
| `risala` | **62** | 2 |
| `hand-bill` | **9** | 2 |
| `tract` | 22 | **52** |
| `pamphlet` | 8 | **237** |
| `booklet` | 1 | **64** |

**Mechanism A — publishers' self-naming.** `risala` is part of works' own titles (*Risala-i-…*), 45 of 62 in Urdu. `hand-bill` likewise, because the Sikh committee *named its issues* "Hand Bill No. 31." These words sort by community because **the communities sorted their own self-descriptions**, and the register merely transliterated.

**Mechanism B — the Reporter's descriptive habit.** `tract`, `pamphlet`, `booklet` are overwhelmingly the register's own words. And `tract` — the one showing the total 81%-Christian → 97%-Sikh handover — is **a word the publishers largely did not use of themselves.**

> **So it is not only that publishers relabelled. The register's own describer developed a lexical habit that sorted communities, using a word of his own.**

---

## 4. What this establishes

> **S-19. A category a classification scheme forbids reappears in its descriptive vocabulary.**

The register's `Ω` has language, topic, printer, publisher, city, copies, price, format, method. **It has no field for religious community** — the single most consequential fact about Punjabi print in this period, and one the Reporter plainly knew, since the glosses are saturated with it.

The classification could not enter `Ω`. It entered `Σ` — the semantic layer — as a lexical habit. **You cannot recover community by querying the register's fields. You recover it by measuring which words the describer chose.**

This gives Cycle 1's K-004 an empirical mechanism. `Ω` and `Σ` are not two aspects of one object; **they stand in compensatory relation. What the categorical layer forbids, the semantic layer carries.** Bundling them into one "lifeworld" measure would have destroyed exactly this.

**And it yields a general method.** To find what a classification scheme suppresses, do not audit its categories — a suppressed category is by definition not there. **Measure the drift of the descriptive vocabulary against a null-word baseline.** The suppressed distinction appears as lexical stratification with no categorical correlate.

The instrument transfers directly: **any corpus pairing a structured schema with free-text human description can be audited this way** — administrative archives, clinical records, and annotated ML training sets. A label taxonomy that omits a distinction its annotators find salient should show the same signature: systematic lexical drift with no schema correlate. That is a runnable audit for what a labelling scheme forbids its annotators to say.

**And it answers Q-18 better than Q-18 asked.** The words do not drift *because* they are contested. **They partition.** By 1910–1930 the register's genre vocabulary reads: `tract` → Sikh, `risala` → Muslim, `pamphlet` → administrative-general, `hand-bill` → Sikh, `booklet` → Muslim-leaning. **The communal classification the scheme refused to make was made anyway, in the choice of nouns.**

---

## 5. Limits

- **The `tract` handover happens inside the OCR hole.** `Tract` is 81% Christian through 1884, dispersed and thin in 1885–93 (n=10–22), and 97% Sikh by 1907–08. The transition completes somewhere in 1893–1907, and **thirteen of those fourteen years have no text layer** (Q-19). The endpoints are solid; the mechanism of transfer is unobservable with current scans. **This is the single strongest argument for prioritising OCR of the 1894–1906 volumes.**
- **Community attribution is regex-based and crude.** `guru`, `dharm`, `diwan` are genuinely shared. The controls, not the classifier, carry the result.
- **`hand-bill` and `risala` late-period n are small** (7–13 at tight window). Values are extreme but intervals are wide.
- **Direction of causation between the two mechanisms is not established.** Whether the Reporter's `tract` habit followed the Sikh adoption of the genre or helped constitute it is not decidable from the register alone.
- **This is a fact about the register's language.** It is evidence about what the apparatus could and could not say. It is not, on its own, evidence about Punjabi religious life.

---

## 6. Consequence for C-18

C-18(iv) held that an imperial frame "presents as discovery rather than decision." This complicates it in a specific way.

The frame is also **reactive**. Its describers, denied a category, improvised one; and the improvised category tracked the communal contest going on in the print market. So the register is not a fixed grid imposed on a changing world. **It is a participant whose vocabulary was moved by the thing it was watching, in a register that had no way to record that it had moved.**

That is a *third* mode alongside the extractive and surveillant coarsening of Q-17: an apparatus whose categories are stable on paper and whose *usage* drifts underneath them, unrecorded, so that a century later the drift is recoverable only by counting words the scheme never treated as data.

**Q-20 (new):** does the drift precede or follow the mobilisation it tracks? If the Reporter's `tract` usage turns Sikh *before* the Sikh tract-publishing operation reaches scale, the register anticipated the formation — which would make it an instrument of communal recognition, not merely a record of one. Testing this needs the 1894–1906 volumes. **Everything now waits on that hole.**
