# E0b — the legibility budget, measured properly

*2026-08-19. Supersedes the E0 figures in `RESULTS.md` and in `OCR_RESEARCH_AGENDA.md` §0 Challenge 2. Scripts: `e0b_measure_all.py`, `e0b_report.py`. Data: `e0b_results.json`.*

**Sweep:** all twelve quarters, 587 pages attempted, **393 used, 194 skipped (33%)** on geometry failure or entry-count mismatch. **511 native-script title crops** measured at the scans' native 306 DPI, in memory, no resampling.

| script | n |
|---|---:|
| Perso-Arabic | 256 |
| Gurmukhi | 125 |
| Perso-Arabic (Punjabi in Persian character) | 62 |
| mixed / bilingual | 40 |
| Devanagari | 21 |
| Latin | 5 |

---

## 1. What E0 got wrong

**E0 used n=41 from one quarter and assigned script by language alone.** Three consequences, all material:

| | E0 (n=41, 1910Q2) | E0b (n=511, twelve quarters) |
|---|---|---|
| Perso-Arabic clearance | 10.6 mil | **16.3 mil** (IQR 8.2–29.4) |
| Gurmukhi clearance | 6.5 mil | **9.8 mil** (IQR 3.3–22.9) |
| Devanagari clearance | **53.1 mil** | **19.6 mil** |

- **The Devanagari figure came from two crops.** 53.1 mil was noise. It was used to claim Devanagari had eight times Gurmukhi's margin. It does not.
- **The Gurmukhi sample was contaminated.** `SCRIPT_OF` mapped Punjabi → Gurmukhi unconditionally, but the register prints whole sections headed `PUNJABI (IN THE PERSIAN CHARACTER)` and annotates `char` per entry. E0b finds **62 Punjabi crops in Perso-Arabic script** — a third of what E0 was calling Gurmukhi.
- **Medians hid the distributions.** IQRs span 3–7×. No architectural decision should have been taken on a median here.

---

## 2. The result

Share of crops whose smaller feature — dot height or dot-to-body clearance — falls below the **2 px sampling floor**. This is the decision statistic: those crops are unrecoverable regardless of model.

| script | n | clearance mil (IQR) | @140 DPI | @306 DPI | @600 DPI |
|---|---:|---|---:|---:|---:|
| Perso-Arabic | 221 | 16.3 (8.2–29.4) | 100% | **14%** | 11% |
| Perso-Arabic (Punjabi) | 52 | 13.1 (6.5–23.3) | 100% | **21%** | 15% |
| Devanagari | 15 | 19.6 (8.2–30.2) | 100% | 20% | 20% |
| **Gurmukhi** | 85 | 9.8 (3.3–22.9) | 98% | **31%** | 26% |

**Two findings, one of which overturns a recommendation.**

### 2.1 The script hierarchy is real, and the language-controlled comparison is the proof

Gurmukhi fails at **31%** against Perso-Arabic's **14%** — a 2.2× difference, not the categorical one E0 implied.

The decisive comparison holds language constant:

> **Punjabi printed in Gurmukhi: 31% below floor. Punjabi printed in the Persian character: 21% below floor.** Same language, same presses, same decade, same scans — **only the script differs, and Gurmukhi is ~1.5× more likely to be unrecoverable.**

That comparison is available only because E0b separates the two, and it is a cleaner result than E0's cross-language one, because it controls for everything except the writing system.

### 2.2 Re-imaging at 600 DPI would help far less than claimed

Doubling resolution removes only **3–5 percentage points**:

`Perso-Arabic 14→11 · Punjabi-in-Persian 21→15 · Gurmukhi 31→26 · Devanagari 20→20`

The reason is in the tail, not the median. Share of crops whose mark is separated from the body by **less than one pixel at 306 DPI**:

| script | clearance = 0 | ≤ 1 px | ≤ 2 px | median (all crops) |
|---|---:|---:|---:|---:|
| Perso-Arabic | 8% | 18% | 30% | 16.3 mil |
| Perso-Arabic (Punjabi) | 10% | 24% | 36% | 10.6 mil |
| Devanagari | 25% | 40% | 45% | 9.8 mil |
| **Gurmukhi** | **30%** | **48%** | 58% | 4.9 mil |

**Thirty percent of Gurmukhi marks are adjacent to the letter body at sub-pixel separation.** Median clearance across all Gurmukhi crops including these is **4.9 mil = 1.5 px at 306 DPI**.

**What cannot be determined from these scans:** whether that population is *ink merge in the printed artifact* — lithographic spread, in which case no resolution recovers it — or *undersampling*, in which case 600 DPI resolves it to ~2 px. The two are indistinguishable at the resolution we have, and the difference decides whether re-imaging is worth anything.

> **Replaces the earlier recommendation.** Not "re-image the volumes at 600 DPI." Instead: **re-image ~20 pages at 600 DPI, stratified by script, and re-run E0b on them.** If the clearance-zero population resolves, full re-imaging is justified and its benefit is now quantified. If it does not, the ceiling is in the ink and no scanning budget will move it. This is a decisive experiment costing a day.

---

## 3. Two measurements that failed, reported as failures

**The functional-load proxy does not discriminate.** Median share of components that are satellite marks: Perso-Arabic 0.53, Gurmukhi 0.60, Devanagari 0.55, Punjabi-in-Persian 0.56, Latin 0.45. It measures component fragmentation, not how much letter identity the marks carry. **The intended point stands qualitatively and remains unmeasured**: in naskh, b/t/th/p/n/y share one rasm and differ *only* by i'jam, so dot loss destroys letter identity; a lost anusvara usually does not. Clearance is therefore not commensurable across scripts as a measure of consequence. A real functional-load measure would need a confusability count over each script's inventory — worth doing, not done here.

**The print-method split is unusable, and why is itself a finding.** Grouping by `method` gave Gurmukhi litho n=1 against "type/other" n=84 — because `method` is *blank* for most Punjabi entries, and blanks were pooled with type. The blank rate is stratified by language:

| | n | blank |
|---|---:|---:|
| Bilingual (Arabic & Urdu) | 89 | 1.1% |
| Urdu | 1,875 | 3.3% |
| Arabic | 58 | 13.8% |
| Sindhi | 64 | 14.1% |
| **Punjabi** | 1,486 | **71.5%** |
| **Hindi** | 228 | **88.2%** |
| Bilingual (Hindi & Sanskrit) | 89 | 92.1% |
| English | 268 | 100% |

> **This is the third field found to be recorded differentially by language**, after `char` (script annotated for Punjabi 28.9% of the time, for Urdu 0.7%) and the genre vocabulary (`dialectic/cycle3_q18_genre_vocabulary.md`).
>
> **The register's completeness is itself stratified by language.** Any statistic computed from `method`, `char`, or any sparse field is differentially reliable across languages, and naive cross-language comparison on those fields is invalid without a recorded-vs-blank control. This affects the project's descriptive claims generally, not only E0b.

---

## 4. The bottleneck is localization, not recognition

**511 native crops from 4,502 entries — 11.4% — against 4,044 entries flagged as carrying a native-script title.** Two losses compound:

- **33% of pages fail** the geometry or entry-count check and are dropped whole (194 of 587). Correctly dropped: a crop paired with the wrong record is worse than no crop.
- Of the remaining pages, `native_box()` yields a crop for roughly **1.4 entries per page against a median of 8**. It requires locating the opening `[` of the gloss on the entry's first line and returns nothing otherwise — author-first entries, wrapped titles, and any bracket-detection failure all yield nothing.

> **Before any model question, ~88% of the supervision signal is unreached — not degraded, unreached.** Localization recall is the highest-leverage engineering target in the native-script programme by a wide margin, and it needs no ML: the bracket is a printed glyph in a ruled column.

---

## 5. What holds, and at what confidence

| claim | status |
|---|---|
| At the current 140 DPI render, native script is unrecoverable — 97–100% below floor, every script | **Confirmed, unchanged** |
| Gurmukhi is the least recoverable script in this corpus | **Confirmed**, 31% vs 14%, and confirmed language-controlled (31% vs 21% within Punjabi) |
| Devanagari has a large margin over the other scripts | **Withdrawn.** Rested on n=2; the n=21 figure is 20% below floor, comparable to Punjabi-in-Persian |
| 600 DPI re-imaging is a precondition for a reference dataset | **Withdrawn.** 3–5 point improvement; the binding population is sub-pixel adjacency of unknown origin |
| The scanning grid imposes a script hierarchy | **Holds, at 2.2×** rather than categorically — and its origin (ink vs sampling) is undetermined pending the 20-page pilot |
| Dot share measures functional load | **Rejected.** Does not discriminate |
| Gurmukhi litho is worse than Gurmukhi type | **Untestable here.** `method` is 71.5% blank for Punjabi |

**Devanagari n=15–21 remains thin.** Hindi and Sanskrit are 250 entries in the whole three-year corpus; this will not improve without more years. Report it as thin; do not build on it.
