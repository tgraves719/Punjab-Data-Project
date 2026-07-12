# Pilot extraction & validation report — Quarter ending 30 June 1910, printed pages 2–8

**Date:** 2026-07-06
**Source scan:** `Library 1/Batch 6/SV_412_44_1910-1912.pdf`, PDF pages 55–61 (printed pages 2–8)
**Ground truth:** `Punjabi Books 20240401b.xlsx`, sheet "1910" (Emmett Davis's hand transcription), rows with Pg ≤ 8 (50 rows)
**Method:** Vision-model reading of page renders (140 dpi grayscale), field-by-field diff against the transcription. Extraction file: `pilot_june1910_pages2-8_extraction.json`.

## Key identification

- The "1910" sheet transcribes the **quarterly list for the quarter ending 30 June 1910** (Act XXV of 1867 + Act X of 1890 catalog), which begins at PDF page 55 of SV_412_44_1910-1912.pdf. Confirmed by exact serial/registration alignment (e.g. Punjabi–Fiction serials 15–22 = printed page 8).
- Serial numbers restart per language–topic section and continue across quarters within a year. Join key = printed page + language + topic + serial.
- The sheet's two `City` columns are: col 5 = printer's city, col 15 = publisher's city.
- `Educ` = the catalog's "(Designed for educational purposes.)" annotation. `Char` = script when the section header specifies one, e.g. "HINDI (PUNJABI CHARACTERS)". `Housekeeping` = Davis's own content gloss.

## Results

50/50 entries on these pages found in both sources. 48 auto-matched; 2 pairing failures, both caused by transcription slips:

1. *Matan-al-Arbain-ul-Nauwiyya* (Sadar Anjuman Ahmadiya, Qadian, reg. 704) is filed under Arabic–**Philosophy** in the sheet; the catalog has it under Arabic–**Religion** (serial 2).
2. *Mirqat* (reg. 494) has serial "22" in the sheet; catalog reads serial 2 (Arabic–Philosophy).

Of ~384 compared field values, 29 raw disagreements; excluding the 7 knock-on artifacts of the mispairing above, **22 genuine disagreements**, classified:

### A. Registration-number errors in the transcription (5) — ~10% of rows
| Page | Entry | Sheet | Scan reads |
|---|---|---|---|
| 2 | English–Law s2 (Indian Arms Act) | 450 | 459 |
| 2 | English–Medicine s1 (The Doctor) | 299 | 399 |
| 2 | English–Misc s4 (Fleming) | 406 | 408 (406 is the reg. of a *different* Harnam Das entry on p3 — likely copy slip) |
| 2 | English–Misc s6 (Khosla's Directory) | 626 | 698 (626 duplicates s3's reg. — copy slip) |
| 3 | Arabic–Language s2 (Qaida-i-Baghdadi) | 428 | 678 |

### B. Copies discrepancies (2)
- p8 Punjabi–Fiction s16 (*Lampat Shikari*): sheet 500, scan clearly **600**.
- p5 Hindi–Language s5 (*Shabdawali*): sheet 4,000, scan read as 6,000 — digit degraded, needs human adjudication.

### C. Pagination policy (5)
For multi-part books Davis records an approximate **sum** of parts (e.g. "Pp. 13 and 552" → 565 ✓ exact; "164, 159 and 181" → 500 ≈ 504; Khosla's Directory → 2600 ≈ 2718). The extraction should store the verbatim pagination string plus a computed sum.

### D. Name spelling/transliteration variants (~7)
Sheet typos or variants vs. catalog print: "Davi Davalu"→Devi Dayalu; "Sanatab Dharm Sabha"→Sanatan Dharam Sabha (×2); "Bailabh Bijays"→Ballabh Bijaya; "Riwalpindi"→Ráwalpindi (×3); "Banun"→Bannu. Entity resolution must normalize these regardless of source.

### E. Semantic/parsing conventions (3)
Author-vs-publisher assignment for organization-published works; publisher city inferred by Davis where catalog gives none ("Dera" from "22nd Derajat Mountain Battery").

## Fields the catalog holds that the transcription does not

Title (native script + romanization + English gloss), full publication date, price, edition number, format (8°/16°), print method (litho.), the British annotator's content summary (often a full plot/polemic description), copyright-registration column, and cross-references between quarters ("Previous edition noticed in entry No. 7 at page 4 … quarter ending 30 June 1909"). Content summaries and edition numbers are analytically rich (reception/reprint dynamics; the annotator's own classificatory gaze).

## Layout/parsing hazards catalogued

"Ditto" in printer column; sections continuing across pages ("—concluded"); serial sequences continuing across quarters; two-city semantics; Hijri + Christian dual dates; archival stamps overprinting text ("Rejected 28 JUN 1917"); pencil X-marks on many entries (provenance unknown — worth asking Davis).

## Implication

Scan-side vision extraction on these pages was more accurate than the existing hand transcription wherever the print is legible; disagreements cluster in exactly the fields (multi-digit numbers) where hand transcription is weakest. The right architecture is: vision extraction of everything → automatic diff against Davis's sheets where they overlap → small human adjudication queue for degraded digits. Corpus scale: Batch 6 (Punjab 1867–1942) ≈ 26 volumes ≈ 10,000 pages ≈ 60,000–80,000 entries; Batch 7 adds the other provinces of British India for comparative work.
