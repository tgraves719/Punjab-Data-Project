# Native-script localization — results

*2026-08-19. Code: `pipeline/localize.py`, `pipeline/lines.py`. Evaluation: `loc_final.py`, `loc_peak.py`, `loc_template.py`, `loc_diag.py`. Supersedes the crop yield reported in `E0B_RESULTS.md` §4.*

**The number this set out to move:** E0b extracted 511 native crops from 4,502 entries — **11.4%** — against 4,044 entries the register says carry a native-script title. Localization, not recognition, was the binding constraint on the whole native-script programme.

---

## 1. Result

Twelve quarters, 1-in-4 page sample, 99 usable pages, 753 entries.

| | before | after |
|---|---:|---:|
| native crops per entry | 11.4% | **52.2%** |
| of entries flagged native | ~13% | **58.1%** |
| boundary error, p50 | — | **0 px** |
| boundary error, p90 | — | **3 px** |
| boundary within 2 px | — | **89%** (n=75) |

Recall by language is even across scripts, which was the risk worth checking — a localizer quietly worse on the tail languages would have rebuilt the script hierarchy E0b found in the scanning resolution:

`Arabic 71.4% · Sindhi 60.0% · Urdu 55.6% · Hindi 54.3% · Punjabi 50.4%`

**The remaining ~40% is not lost, it is unconfident.** `native_box` returns the correlation score with the box; entries below the bar should be queued, not cropped badly. Relaxing the threshold to 0.62 raises recall to 83% and destroys the boundary (p90 597 px) — the wrong trade for a supervision corpus, and the reason for the two-tier design.

---

## 2. What works

**Template matching.** The catalog's Latin fount is metal set and every scan is 306 DPI, so the opening bracket is near-constant: **35 px tall (p05 29, p95 37), 12 px wide (p05 11, p95 14)**, measured over 158 instances. Templates are harvested from the old shape detector's hits — it has ~2% false positives, which makes it an excellent harvester and a bad detector.

**Leftmost peak within 8% of the global maximum.** Neither end of the correlation curve works alone:
- global maximum → lands on the **closing** bracket of the gloss for ~30% of entries;
- first index over a permissive threshold → lands on a tall native stroke (alif, lam, a danda), a median **311 px early**.

Swept against 65 entries with independently known bracket positions, there is a cliff at `absmin` 0.80: the gross-error tail vanishes (p90 848 px → 3 px). Below it, wrong-glyph matches return immediately.

**Line segmentation** (`lines.py`). `crops._first_line_bounds` thresholds the column-2 row profile at 4% of its maximum, low enough that a descender from the line above bridges the gap. Band height median 44 → 36 px against a 50 px line pitch. This did **not** improve bracket recall, but it fixed the geometry it was corrupting: entry-level baseline conformity had been pointing the *wrong way* (all-Latin English entries scoring 0.367 against native entries' 0.261) purely because a two-line band has two baselines.

**Em-dash left bound.** For author-first entries the span starts after the dash, not at the column edge. A wide flat component left of the bracket finds it in **90%** of author-first cases; the measured dash-to-bracket gap has a median of 11 x-heights, which is the width of a two- or three-word native title — the confirmation that it is finding the right glyph. 42.3% of entries are title-first and need no dash.

---

## 3. What failed, with numbers, so it is not retried

**Baseline-conformity span detection.** 65% recall at 28% false positives, median boundary error **3.5 x-heights**. Per-component separation is genuine on title-first entries (`|y1 - baseline|/xh`: native 0.357, Latin 0.051, **AUC 0.754**) but too weak to survive aggregation into a span. Useless for cropping.

**Threshold-tuning the six shape tests.** The measurement that made this look promising — the found brackets sit comfortably inside every threshold, only 4% failing width — is a **pure selection effect**. Those are the instances the tests selected. It says nothing about the 83% missed.

**Rendering the misses is what settled it.** The bracket is plainly legible in most failures; the tests, not the glyph, are the problem, and worn lithographic strokes breaking the "solid left column" requirement are the largest single cause.

---

## 4. Four measurement errors, all mine, all the same shape

Every one was a mismatch between what the evaluation measured and what the code did — not a modelling failure — and each produced plausible-looking statistics for some time before surfacing.

1. **D-017 reintroduced.** Four scripts paired crops via a bare `SELECT ... WHERE printed_page=?`, which returns section-grouped order, not page order. Fixed in `pagerecs.py`. It happened not to change the sample that caught it, which is why *looking at an image* rather than re-reading code is what found the real problem.

2. **The negative class was wrong.** False-positive rates were computed against English entries — but **English entries have brackets too**. The bracket marks where the romanization begins, not whether native script is present. "52.8% FP" was the detector correctly finding brackets and being penalised for it. Read properly the same run showed bracket localization at ~93% of all entries.

3. **`title_native` is noisy.** It flags **11 all-Latin English entries** as carrying native script and denies it for 137 vernacular ones. Verified against the printed registration numbers in column 5 — reg 507/406/465/492/678/493 all match their labels index for index, so the pairing is right and the flag is wrong. Evaluation now runs on a clean subset (positives non-English *and* flagged; negatives English *and* not flagged).

4. **The band handed to the matcher was not the band it was tuned on.** `native_box` selected candidate lines by the entry's y-range, but `y_top` comes from the serial's bounding box and the text line beside it routinely starts a few pixels higher — so index 0 was often the entry's *second* line. The 0.80 threshold tuned on the serial's line was being applied to a continuation line, and the stricter later-line bar to the line that actually held the bracket. Both ends inverted. Fixing it took boundary p90 from 552 px to 3 px and recall from 54.7% to 58.1%.

---

## 5. Open

**Page loss is now the dominant term: 34%**, untouched. Over-detection dominates (+1 on 13 pages, +2 on 4, +3 and +4 on one each, against -1 on 4 and -2 on 1). `loc_align.py` is written and tests the premise that the detector's discarded per-box **digit counts** — the register knows every reg number on the page — can prune spurious boxes. About 8% of the loss is `only 2 vertical rules found`, a geometry problem that pruning will not touch.

**Everything here is scored against borrowed ground truth.** Boundary accuracy is measured against the old shape detector's own output (~2% FP), the peak sweep rests on n=65, and the register's own flag is demonstrably noisy. **A hand-checked gold set of a few hundred entries is now the cheapest high-value item in the project** — it would simultaneously retire the uncertainty in E0b's script hierarchy, this localizer's boundary claim, and the label itself.

**Recall recovery, if wanted.** The single template is a pixel-wise median of 162 patches and is likely blurred by misalignment. Aligning patches before averaging, or clustering into two or three templates and taking the max correlation, is the obvious next attempt at raising recall without moving the threshold. Not tried.

**Warrants a DECISIONS entry** — the localizer replaces the bracket detector for crop extraction and introduces a confidence-gated queue, which is a method choice of the kind D-001..D-019 record.
