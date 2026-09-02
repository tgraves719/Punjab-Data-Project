"""End-to-end native-crop yield with the template localizer.

The number this exists to move: E0b extracted 511 native crops from 4,502
entries — 11.4% — against 4,044 entries the register says carry a native-script
title. Reported here on the same footing, plus boundary accuracy against the
shape detector's high-precision hits.
"""

from __future__ import annotations

import collections
import json
import pathlib
import sqlite3
import statistics
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import crops     # noqa: E402
import lines     # noqa: E402
import localize  # noqa: E402

sys.path.insert(0, str(HERE))
import pagerecs  # noqa: E402

PIPELINE, DB, DPI = ROOT / "pipeline", ROOT / "punjab.db", 306
STRIDE = int(sys.argv[1]) if len(sys.argv) > 1 else 3


def main() -> int:
    con = sqlite3.connect(DB)
    auth = {(q, str(r)): (a or "").strip()
            for q, r, a in con.execute("select quarter,reg,coalesce(author,'') from entries")}
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]

    seen = native_flagged = got = 0
    pages_ok = pages_bad = 0
    errs = []
    bylang = collections.defaultdict(lambda: [0, 0])
    lines_used = collections.Counter()
    t0 = time.time()

    for q in quarters:
        man = json.load(open(PIPELINE / f"manifest_{q}.json"))
        pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
        pages = list(range(lo, hi + 1))
        calib = crops.Page.calibrate_quarter(pdf, pages, DPI)
        for pdf_page in pages[::STRIDE]:
            want = pagerecs.page_entries(q, pdf_page + off, con)
            if not want:
                continue
            try:
                pg = crops.Page.render(pdf, pdf_page, DPI, calib)
                found = pg.entries()
            except Exception:
                pages_bad += 1
                continue
            if len(found) != len(want):
                pages_bad += 1
                continue
            pages_ok += 1
            for e, rec in zip(found, want):
                seen += 1
                nat = bool(rec.get("native"))
                lang = str(rec.get("norm_lang", ""))
                native_flagged += nat
                has_auth = bool(auth.get((q, str(rec.get("reg"))), ""))
                box, score, li = localize.native_box(pg, e, lines, has_auth)
                if box is not None:
                    got += 1
                    if nat:
                        bylang[lang][0] += 1
                    lines_used[li] += 1
                    if e.bracket_x is not None and li == 0:
                        errs.append(abs((box[2] + 2) - e.bracket_x))
                if nat:
                    bylang[lang][1] += 1
        print(f"  {q}: seen={seen} crops={got} [{time.time()-t0:.0f}s]", flush=True)

    print(f"\npages used {pages_ok}, skipped {pages_bad} "
          f"({100*pages_bad/max(pages_ok+pages_bad,1):.0f}%)")
    print(f"entries on usable pages: {seen}   flagged native: {native_flagged}")
    print(f"native crops produced:   {got}  = {100*got/max(seen,1):.1f}% of entries, "
          f"{100*got/max(native_flagged,1):.1f}% of flagged")
    if errs:
        e = sorted(errs)
        print(f"boundary vs shape-detector bracket (n={len(e)}): "
              f"p50 {e[len(e)//2]}px  p90 {e[int(.9*len(e))]}px  "
              f"<=2px {100*sum(v<=2 for v in e)/len(e):.0f}%")
    print("\nby language (recall against the register's flag):")
    for lang, (a, b) in sorted(bylang.items(), key=lambda kv: -kv[1][1]):
        if b < 15:
            continue
        print(f"  {lang[:30]:32s} n={b:5d}  {100*a/b:5.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
