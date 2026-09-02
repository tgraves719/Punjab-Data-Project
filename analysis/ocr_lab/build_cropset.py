"""Build the native-resolution crop set for the transcription experiments.

For every entry it can locate, this writes the entry's first line — the line
carrying the native-script title and its bracketed romanization — at both the
pipeline's current 140 DPI and the scan's native 306 DPI, together with the
register's own record of that entry.

Only pages whose detected entry count matches the register exactly are kept.
That check is the point: an entry crop is worthless if it is not the entry we
think it is, and the register gives us an independent count per page to test
the alignment against. Pages that fail are reported, not silently dropped.

    python build_cropset.py --quarters 1910Q2 1911Q1 --out cropset
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "pipeline"))

import crops  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "pipeline"
DB = ROOT / "punjab.db"

LOW_DPI = 140          # what render.py currently produces
NATIVE_DPI = 306       # the scans' own resolution


def page_entries(quarter: str, printed_page: int, con: sqlite3.Connection) -> list[dict]:
    """The page's entries in the order they are printed on it.

    The extraction JSONs hold true page order; the database does not. Its rows
    come out grouped by section, so on a page where a section ends and another
    begins — printed page 31 of 1910Q2 runs Miscellaneous 73-79 and then
    Philosophy 1-3 — the database order is 1, 2, 3, 73 … 79 while the page reads
    73 … 79, 1, 2, 3. Zipping detected entries against that order silently
    pairs every crop with the wrong record, which is how this was caught.
    """
    path = PIPELINE / "data" / quarter / "extractions" / f"p{printed_page:03d}.json"
    if not path.exists():
        return []
    recs = json.load(open(path, encoding="utf-8"))

    con.row_factory = sqlite3.Row
    norm = {}
    for r in con.execute(
            "SELECT reg, serial, norm_lang, norm_printer, norm_pcity FROM entries "
            "WHERE quarter=? AND printed_page=?", (quarter, printed_page)):
        norm[(str(r["reg"]), str(r["serial"]))] = dict(r)

    out = []
    for rec in recs:
        n = norm.get((str(rec.get("reg", "")), str(rec.get("serial", ""))), {})
        out.append(rec | {"norm_lang": n.get("norm_lang", rec.get("lang", "")),
                          "norm_printer": n.get("norm_printer", rec.get("printer", "")),
                          "norm_pcity": n.get("norm_pcity", rec.get("pcity", ""))})
    return out


def build_quarter(quarter: str, out: pathlib.Path, con: sqlite3.Connection,
                  limit_pages: int | None = None) -> dict:
    manifest = json.load(open(PIPELINE / f"manifest_{quarter}.json"))
    pdf = manifest["volume_pdf"]
    lo, hi = manifest["pdf_pages"]
    pages = list(range(lo, hi + 1))
    if limit_pages:
        pages = pages[:limit_pages]

    calib = crops.Page.calibrate_quarter(pdf, pages, NATIVE_DPI)
    outdir = out / quarter
    (outdir / "strip_306").mkdir(parents=True, exist_ok=True)
    (outdir / "strip_140").mkdir(parents=True, exist_ok=True)
    (outdir / "native_306").mkdir(parents=True, exist_ok=True)

    offset = manifest["printed_page_offset"]
    records, skipped = [], []
    for pdf_page in pages:
        want = page_entries(quarter, pdf_page + offset, con)
        if not want:
            continue
        try:
            hi_pg = crops.Page.render(pdf, pdf_page, NATIVE_DPI, calib)
            found = hi_pg.entries()
        except Exception as exc:                      # geometry failure
            skipped.append({"pdf_page": pdf_page, "reason": f"{type(exc).__name__}: {exc}"})
            continue
        if len(found) != len(want):
            skipped.append({"pdf_page": pdf_page,
                            "reason": f"count {len(found)} != register {len(want)}"})
            continue

        try:
            lo_pg = crops.Page.render(pdf, pdf_page, LOW_DPI, calib)
            lo_entries = lo_pg.entries() if len(lo_pg.entries()) == len(want) else None
        except Exception:
            lo_entries = None

        for i, (e, rec) in enumerate(zip(found, want)):
            key = f"{quarter}_p{rec['printed_page']}_s{rec['serial']}_r{rec['reg']}"
            e.strip_image().save(outdir / "strip_306" / f"{key}.png")
            if lo_entries:
                lo_entries[i].strip_image().save(outdir / "strip_140" / f"{key}.png")
            nat = e.native_image()
            if nat is not None and nat.width > 8:
                nat.save(outdir / "native_306" / f"{key}.png")

            records.append({
                "key": key,
                "quarter": quarter,
                "pdf_page": pdf_page,
                "printed_page": rec["printed_page"],
                "serial": rec["serial"],
                "reg": rec["reg"],
                "lang": rec.get("norm_lang", ""),
                "char": rec.get("char", ""),
                "topic": rec.get("topic", ""),
                "author": rec.get("author", ""),
                "title_roman": rec.get("title", ""),
                "title_native_flag": bool(rec.get("title_native")),
                "gloss": rec.get("gloss", ""),
                "publisher": rec.get("publisher", ""),
                "printer": rec.get("norm_printer", ""),
                "pcity": rec.get("norm_pcity", ""),
                "date": rec.get("date", ""),
                "has_native_crop": nat is not None and nat.width > 8,
                "has_low_dpi": bool(lo_entries),
                "line_height_px": e.line_bottom - e.line_top,
            })
        print(f"  {quarter} pdf {pdf_page}: {len(want)} entries", flush=True)

    return {"quarter": quarter, "records": records, "skipped": skipped,
            "calibration": calib.to_json(),
            "pages_used": len({r['pdf_page'] for r in records}),
            "pages_skipped": len(skipped)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quarters", nargs="+", required=True)
    ap.add_argument("--out", default="cropset")
    ap.add_argument("--limit-pages", type=int, default=None)
    args = ap.parse_args()

    out = pathlib.Path(__file__).resolve().parent / args.out
    out.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)

    summary = []
    for q in args.quarters:
        print(f"[{q}]", flush=True)
        info = build_quarter(q, out, con, args.limit_pages)
        json.dump(info, open(out / f"{q}_manifest.json", "w"), indent=1)
        summary.append({k: v for k, v in info.items() if k != "records"} |
                       {"n_records": len(info["records"])})
        print(f"  -> {len(info['records'])} entries from {info['pages_used']} pages, "
              f"{info['pages_skipped']} pages skipped", flush=True)

    json.dump(summary, open(out / "summary.json", "w"), indent=1)
    total = sum(s["n_records"] for s in summary)
    print(f"\nTOTAL {total} entry crops across {len(summary)} quarters -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
