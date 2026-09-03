# Integrity sweep — does the stored record match its own specification?

*2026-09-02. Closes the sweep D-019(e) asked for and opens one it did not anticipate.
Tool: `verbatim_sweep.py` (re-runnable per year). Output: `verbatim_sweep.json`.*

Two questions, both about the gap between what `pipeline/schema.md` promises and what
`punjab.db` holds. One was open since August; the other was found while answering it and
matters more, because it silently mis-answers the most obvious query a user of the
published data would write.

---

## 1. The `copies` column violates its own spec, and a naive query undercounts by 17%

`schema.md` specifies `copies` as **"number of copies (column 4), digits only."**

**573 of 4,502 values (12.7%) carry a thousands separator** — `"1,000"`, `"2,0C0"` — and
the column is TEXT. So:

```sql
select sum(cast(copies as integer)) from entries;   -- 5,784,297   WRONG
```

SQLite stops casting at the comma, reading `"1,000"` as `1`. The correct total is

```sql
select sum(cast(replace(copies, ',', '') as integer)) from entries;   -- 6,944,051
```

**The naive form undercounts by 1,159,754 copies — 16.7% of the corpus.** Both forms
run without error or warning, and the wrong one is the one a person writes first.

This is not hypothetical: the figure 5,784,297 had already propagated into a draft
funding document. The published site is unaffected — `build_site.py` strips non-digits
via `copies_int()` and reports 6,944,051 — so the site and the draft disagreed, which is
how it was caught.

**Actions.** (a) Normalise `copies` to an integer column in postprocess, keeping the
printed form in a `copies_verbatim` field so the verbatim layer is not the thing that
gets sacrificed to fix this. (b) Until then, any published data dictionary must carry the
`replace()` idiom. (c) Audit the other TEXT-typed numeric fields for the same shape.

> The general lesson is worth more than the fix. **Three-layer discipline was applied to
> spelling and never to number formatting.** `copies` is doing verbatim duty and analytic
> duty in one column, and the analytic reading silently loses a sixth of the corpus. The
> project's stated method — image, verbatim record, normalised layer, never collapsed —
> is exactly the thing that would have prevented this, and it was not applied here.

## 2. The verbatim layer holds, with five identified exceptions

D-019(e) recorded one case where the stored value silently absorbed a correction and
asked for a sweep. Method: the extractor's own flags are the witness — where a flag
quotes what the page prints (`printed 'X'`), compare that quotation against the value
stored for the same field.

**132 flag-quotes report a page reading. 60 diverge from the stored value.** Split by
what the schema actually promises:

| | n | reading |
|---|---:|---|
| **Fields the schema declares verbatim** | **11** | candidate breaches — examined individually below |
| Fields the schema declares normalised (`copies` digits-only, `date` ISO-ish, `edition` ordinal, `method`/`format` controlled, `reg`) | 49 | **not breaches.** The flag records broken type in the source (`'1,0C0'`, `'25o'`, `'4C0'`, `'adition'`, `'iitho.'`) and the stored value is the specified normalisation. This is the schema working. |

Of the 11 candidates, individually inspected:

**Genuine — 5 entries, 2 patterns:**

- **1 silent spelling correction.** `1910Q2 p20 s141 reg 504` — the page prints
  *Stara-i-Hiud Press*; `printer_verbatim` holds *Stara-i-Hind Press, Delhi.* The flag
  preserves the truth; the field labelled verbatim does not. This is D-019(e)'s case,
  now confirmed to be the only one of its kind in the corpus.
- **4 fabricated currency markers.** `1911Q2 s146 reg 379`, `1911Q2 s63 reg 795`,
  `1911Q4 s265 reg 1531`, `1911Q4 s268 reg 1379` — the page prints *"Price, 4 annas"*
  and the record holds *"Rs. 4 annas"*. The column label was replaced by a rupee marker
  the page does not print. **This is a correctness problem as well as a fidelity one:**
  an anna is one-sixteenth of a rupee, so *"Rs. 4 annas"* is not a well-formed price and
  could be read as four rupees. Contained: the incoherent `Rs. N annas` form occurs
  **exactly 4 times in 4,374 priced entries**, and they are precisely these four. The
  correct bare form (`"4 annas"`) is used in 1,350 entries.

**Not breaches — 6 entries:** four where the flag concerns the broken printed *label*
(`'Frice'`, `'Pr.ce'`) rather than the value; two author flags about partly obscured
text elsewhere in the entry.

**One extraction error found incidentally, running the other way:**
`1911Q3 p12 s177 reg 917` stores `pubcity = "Pesh, war"` where the page correctly prints
*Peshawar* — a spurious comma in the record, not in the source.

### What this licenses saying

The verbatim layer's guarantee holds across 4,502 entries with **five known exceptions,
all now identified by quarter, page, serial and registration number**. That is a
defensible claim; *"preserved exactly"*, unqualified, is not, and should not be written
again. Per PLAN §6 these are not corrected here — correction is a separate adjudication
pass — but they are no longer unknown.

The sweep is cheap and should run after every year is ingested; it depends only on the
extractor continuing to flag aggressively, which D-019 established it does.

---

## 3. Addendum — the most famous press in North India is missing from our top-printer list

Found while cross-checking Prof. Davis's bibliography against the corpus, and recorded
here because it is the same class of problem: the stored layer not meaning what a reader
of the analysis would assume.

`norm_printer` holds the Newal Kishore establishment under **six** values differing in the
spelling of the proprietor's name (`Nawal`/`Newal`, `Kishor`/`Kishore`) as well as in the
works. Folding **only the spelling**, which is unambiguous alias debt, merges six buckets
and takes the distinct-printer count from **350 to 344**:

| entries | value |
|---:|---|
| 82 | Newal Kishore Gas Printing Works |
| 78 | Newal Kishore Press |
| 36 | Newal Kishore Steam Press |
| 3 | (joint imprints and one further works) |

**197 entries for the firm** — which would make it the **third-largest printing
establishment in the corpus**, level with Hindustan Steam Press (200) and behind only
Wazir-i-Hind (433) and Sri Gurmat (270). It currently appears nowhere in the top eight,
because it is split three ways.

Two separable issues:

1. **Spelling variants are debt** and should go into `aliases.json` at the next pass. This
   is the same normalisation debt D-018(b) recorded for Mufid-i-Am, Wazir-i-Hind and
   others; Newal Kishore is simply the costliest instance.
2. **Works versus firm is a genuine analytic choice, not a bug**, and it should be made
   deliberately rather than by default. The Gas Printing Works, the Steam Press and the
   Press may be distinct plants of one house. For a network analysis of the print economy
   the firm is usually the actor; for a study of production capacity the works may be.
   Whichever is chosen, the other should remain recoverable — this is exactly what the
   verbatim/normalised split is for. Worth putting to Prof. Davis.

The reason this matters beyond one entity: Newal Kishore is the best-known press in North
India and the subject of a standard monograph (Ulrike Stark, *An Empire of Books*, 2007 —
absent from the bibliography, and worth adding). Any book historian reading a top-printer
table for colonial Punjab will look for it first. Its absence reads as a data error even
when the underlying counts are correct.
