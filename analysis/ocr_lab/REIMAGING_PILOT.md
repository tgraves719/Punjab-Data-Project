# Re-imaging pilot — the 21 pages that decide whether better scans are worth buying

*Spec, 2026-09-02. Governed by [E0B_RESULTS.md](E0B_RESULTS.md) §2.2, which
withdrew the earlier "re-image the volumes at 600 DPI" recommendation and replaced
it with this experiment. Page selection: `reimaging_pilot_pages.json`.*

## 1. The one question this answers

Across the corpus, a large minority of native-script diacritics sit at **sub-pixel
separation from the letter body** at the scans' native 306 DPI — 30% of Gurmukhi
marks, 14% of Perso-Arabic. Those crops are unrecoverable by any model.

**We cannot tell from the existing scans why.** Two possibilities, indistinguishable
at 306 DPI and with opposite consequences:

| | if true | consequence |
|---|---|---|
| **Undersampling** | the marks are separate on the paper; our sampling grid is too coarse to see the gap | re-imaging recovers them, and full re-capture of the corpus is justified and now costed |
| **Ink merge** | the marks are physically joined in the printed artifact — lithographic spread, over-inking, plate wear | **no scanning budget ever recovers them.** The ceiling is in the paper, and the money should go to adjudication labour instead |

One day's imaging settles it. Committing to a full re-capture *without* settling it
risks spending the project's largest single hardware ask on a question the answer to
which was already "no".

## 2. What to capture

**Shelfmark: IOR SV 412/44, Punjab, Vol 13 (1910–12)**, British Library.
(Series confirmed against the Library's own digitisation batch manifest,
`Library 1/Batch 6/Quarterly_Lists_batch_6.xlsx`.)

21 pages, listed in §3, cited by the **printed page number of the quarterly issue** —
these are printed on the page itself, so no folio conversion is needed. Each quarterly
issue restarts its own page numbering, so the quarter must be given with the page.

### Capture requirements, in order of importance

1. **600 DPI or better, optical** — not interpolated. If the device reports an
   effective resolution, record it.
2. **No sharpening. No unsharp mask. No "document"/"text" enhancement mode.**
   This is the one requirement that can silently destroy the experiment: edge
   enhancement manufactures separation between a dot and a letter body, which is
   precisely the measurement being taken. A sharpened 600 DPI capture is worse than
   no capture, because it answers the question falsely and confidently.
3. **Lossless format** — TIFF or PNG. Not JPEG at any quality.
4. **Greyscale is sufficient**; do not binarise or threshold.
5. **A scale reference in frame** if at all possible — a ruler, or the Library's own
   target — so true resolution can be computed rather than trusted.
6. Flat as the binding allows; the measurement is of feature separation in the plane,
   so page curvature near the gutter degrades it.

If archival imaging is not obtainable, **reader photography under the above constraints
is usable** provided the camera is at native resolution with all processing disabled and
a scale reference is in frame. Confirm current reading-room and imaging-order policy
before travelling — do not assume it from prior experience.

## 3. The pages

Selected to over-sample the decisive population rather than to be representative.
Tier **A** pages are dense in sub-pixel crops and carry the question; tier **C** pages
have comfortable clearance and are the **controls** — if the C pages do not sharpen
measurably at 600 DPI, the imaging setup is at fault and the A pages prove nothing.
Do not drop the controls to save four pages.

Coverage: **68 already-measured crops, 34 of them sub-pixel**, across all four scripts
and all twelve quarters (so binding position and any per-session scanning variation are
spread rather than confounded).

| quarter | issue | printed p. | crops measured | of which ≤1 px | median clearance px | dominant script | tier |
|---|---|---:|---:|---:|---:|---|---|
| 1910Q1 | qr end 31 Mar 1910 | **13** | 3 | 3 | 0.0 | Gurmukhi | A · Gurmukhi |
| 1910Q1 | qr end 31 Mar 1910 | **24** | 4 | 2 | 1.8 | Perso-Arabic | A · Perso-Arabic |
| 1910Q1 | qr end 31 Mar 1910 | **28** | 4 | 2 | 2.8 | Perso-Arabic | A · Perso-Arabic |
| 1910Q2 | qr end 30 Jun 1910 | **10** | 3 | 3 | 0.0 | Gurmukhi | A · Gurmukhi |
| 1910Q2 | qr end 30 Jun 1910 | **18** | 4 | 2 | 1.5 | Perso-Arabic (Punjabi) | A · Punjabi-in-Persian |
| 1910Q2 | qr end 30 Jun 1910 | **35** | 3 | 2 | 1.0 | Perso-Arabic | A · Perso-Arabic |
| 1910Q3 | qr end 30 Sep 1910 | **16** | 3 | 2 | 0.0 | Gurmukhi | A · Gurmukhi |
| 1910Q3 | qr end 30 Sep 1910 | **21** | 2 | 2 | 1.0 | Perso-Arabic (Punjabi) | A · Punjabi-in-Persian |
| 1910Q3 | qr end 30 Sep 1910 | **39** | 3 | 2 | 0.0 | Perso-Arabic | A · Perso-Arabic |
| 1910Q4 | qr end 31 Dec 1910 | **30** | 4 | 1 | 1.8 | Perso-Arabic | B · breadth |
| 1911Q1 | qr end 31 Mar 1911 | **34** | 3 | 0 | 7.0 | Perso-Arabic | C · control |
| 1911Q2 | qr end 30 Jun 1911 | **6** | 2 | 2 | 0.0 | Devanagari | A · Devanagari |
| 1911Q2 | qr end 30 Jun 1911 | **23** | 4 | 1 | 4.0 | Gurmukhi | B · breadth |
| 1911Q3 | qr end 30 Sep 1911 | **21** | 4 | 0 | 5.0 | Gurmukhi | C · control |
| 1911Q4 | qr end 31 Dec 1911 | **3** | 2 | 1 | 1.5 | Devanagari | A · Devanagari |
| 1911Q4 | qr end 31 Dec 1911 | **19** | 3 | 0 | 5.0 | Perso-Arabic | C · control |
| 1912Q1 | qr end 31 Mar 1912 | **23** | 3 | 0 | 6.0 | Devanagari | C · control |
| 1912Q2 | qr end 30 Jun 1912 | **4** | 3 | 3 | 0.0 | Devanagari | A · Devanagari |
| 1912Q3 | qr end 30 Sep 1912 | **10** | 4 | 3 | 0.5 | Gurmukhi | A · Gurmukhi |
| 1912Q3 | qr end 30 Sep 1912 | **11** | 4 | 2 | 1.0 | Gurmukhi | A · Gurmukhi |
| 1912Q4 | qr end 31 Dec 1912 | **25** | 3 | 1 | 7.0 | Perso-Arabic (Punjabi) | A · Punjabi-in-Persian |

## 4. What happens to the images

`analysis/ocr_lab/e0b_measure_all.py` re-runs unchanged on the new captures; the
crops are already localised (`pipeline/localize.py`) and the 68 measured crops give a
**paired** comparison, same crop at both resolutions, which is far stronger than
comparing distributions.

## 5. Decision rule, fixed in advance

Stated before the data exists, so the result cannot be read to suit the preferred answer.

Let *S* = share of the 34 sub-pixel crops whose clearance resolves to **≥ 2 px** at 600 DPI,
with the control pages confirming the capture is sound.

- **S ≥ 0.5** — undersampling dominates. Full re-imaging of the Punjab run is justified;
  cost it and put it in the institutional ask as a funded line.
- **S ≤ 0.2** — ink merge dominates. **Withdraw the re-imaging ask entirely** and say so
  publicly. The ceiling is in the artifact. Redirect the argument to adjudication labour
  and to script-aware confidence reporting, and record the affected population as a
  permanent, quantified limit of the dataset.
- **0.2 < S < 0.5** — partial. Re-image selectively by script: the per-script *S* will
  differ, and Gurmukhi is expected to be worst. Fund by script, not by volume.

In all three branches the result is publishable: a measured legibility budget for a
colonial print register, per script, is not something the field currently has.

## 6. Note on what this is not

This measures **recoverability of the printed image**, not transcription accuracy. Even
at perfect clearance the recognition problem remains — but it becomes a modelling problem
with an achievable ceiling instead of one bounded by physics. See
[LOCALIZATION_RESULTS.md](LOCALIZATION_RESULTS.md) for the other half, where the binding
constraint was reach rather than resolution.
