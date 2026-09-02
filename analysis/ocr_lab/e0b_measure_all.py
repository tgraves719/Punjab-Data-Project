"""E0b — the legibility budget measured properly, across all four scripts.

E0 (2026-08-04) reported medians from 41 native crops of one quarter, and
assigned script by language alone. Both are fixed here:

  * every quarter in the database is swept, not one;
  * script is decided from the register's own `char` field and section header,
    so Punjabi printed in the Persian character is not counted as Gurmukhi;
  * the reported statistic is not only the median but the *fraction of crops
    whose i'jam clearance falls below the 2 px sampling floor* at each grid,
    which is the decision-relevant number;
  * dot density (dots per 100 px of title width) is reported as a proxy for how
    much of the script's identity the dots actually carry.

No images are written. Measurement is in memory.

    python e0b_measure_all.py
"""
from __future__ import annotations
import json, pathlib, sqlite3, statistics, sys, time, collections
import numpy as np
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import crops  # noqa: E402
from e0_measure import measure  # reuse the identical component measurement

PIPELINE, DB, NATIVE_DPI = ROOT / "pipeline", ROOT / "punjab.db", 306

PERSO = {"Urdu","Arabic","Persian","Sindhi","Kashmiri","Pushto","Pashtu","Multani","Balochi","Bilochi"}
NAGARI = {"Hindi","Sanskrit","Marathi"}

def script_of(lang: str, char: str, section: str) -> str:
    l, c, s = (lang or ""), (char or "").lower(), (section or "").upper()
    persian_ctx = ("persian" in c or "arabic" in c or "PERSIAN CHARACTER" in s)
    gurmukhi_ctx = ("gurmukhi" in c or "punjabi charac" in c or "GURMUKHI" in s)
    nagari_ctx = ("nagari" in c or "hindi charac" in c or "devanagari" in c)
    if l == "English": return "Latin"
    if l == "Punjabi":
        if persian_ctx: return "Perso-Arabic (Punjabi)"
        return "Gurmukhi"
    if l in NAGARI:
        return "Perso-Arabic (Indic lang)" if persian_ctx else "Devanagari"
    if l in PERSO:
        if gurmukhi_ctx: return "Gurmukhi"
        if nagari_ctx: return "Devanagari"
        return "Perso-Arabic"
    if l.startswith(("Bilingual","Trilingual","Polyglot")) or "," in l:
        return "mixed"
    return "other"

def page_entries(quarter, printed_page, con):
    p = PIPELINE / "data" / quarter / "extractions" / f"p{printed_page:03d}.json"
    if not p.exists(): return []
    recs = json.load(open(p, encoding="utf-8"))
    con.row_factory = sqlite3.Row
    norm = {(str(r["reg"]), str(r["serial"])): dict(r) for r in con.execute(
        "SELECT reg,serial,norm_lang,method FROM entries WHERE quarter=? AND printed_page=?",
        (quarter, printed_page))}
    return [rec | {"norm_lang": norm.get((str(rec.get("reg","")), str(rec.get("serial",""))), {}).get("norm_lang", rec.get("lang","")),
                   "method": norm.get((str(rec.get("reg","")), str(rec.get("serial",""))), {}).get("method","")}
            for rec in recs]

def main():
    con = sqlite3.connect(DB)
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
    rows, pages_used, pages_skipped = [], 0, 0
    t0 = time.time()
    for q in quarters:
        man = json.load(open(PIPELINE / f"manifest_{q}.json"))
        pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
        pages = list(range(lo, hi + 1))
        calib = crops.Page.calibrate_quarter(pdf, pages, NATIVE_DPI)
        for pdf_page in pages:
            want = page_entries(q, pdf_page + off, con)
            if not want: continue
            try:
                pg = crops.Page.render(pdf, pdf_page, NATIVE_DPI, calib)
                found = pg.entries()
            except Exception:
                pages_skipped += 1; continue
            if len(found) != len(want):
                pages_skipped += 1; continue
            pages_used += 1
            for e, rec in zip(found, want):
                img = e.native_image()
                if img is None or img.width < 12: continue
                m = measure(img)
                if m is None: continue
                rows.append({"quarter": q, "printed_page": rec.get("printed_page"),
                             "reg": rec.get("reg"), "serial": rec.get("serial"),
                             "lang": rec.get("norm_lang",""), "char": rec.get("char",""),
                             "section": rec.get("section",""), "method": rec.get("method",""),
                             "script": script_of(rec.get("norm_lang",""), rec.get("char",""), rec.get("section","")),
                             "w": img.width, **{k: m[k] for k in
                               ("body_h","dot_h","dot_gap","n_dots","n_bodies","dots_per_100px")}})
        json.dump(rows, open(HERE / "e0b_results.json", "w"), indent=1)
        print(f"  {q}: cum crops={len(rows)} pages_used={pages_used} skipped={pages_skipped} [{time.time()-t0:.0f}s]", flush=True)
    json.dump(rows, open(HERE / "e0b_results.json", "w"), indent=1)
    print(f"\nTOTAL {len(rows)} native crops | pages used {pages_used}, skipped {pages_skipped} | {time.time()-t0:.0f}s")
    by = collections.defaultdict(list)
    for r in rows: by[r["script"]].append(r)
    for s, sub in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print(f"  {s:28s} n={len(sub)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
