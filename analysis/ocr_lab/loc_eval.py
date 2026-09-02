"""Recall and precision of native-span localization, against the register's own flag.

`title_native` records whether the catalog printed a native-script title for an
entry. That is an independent label for exactly this task, so both recall and
false positives can be measured without annotating anything.
"""

from __future__ import annotations

import collections
import json
import pathlib
import sqlite3
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import crops        # noqa: E402
import localize     # noqa: E402

PIPELINE, DB, DPI = ROOT / "pipeline", ROOT / "punjab.db", 306
STRIDE = 5          # 20% page sample


def main() -> int:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
    stat = collections.Counter()
    bylang = collections.defaultdict(collections.Counter)
    t0 = time.time()

    for q in quarters:
        man = json.load(open(PIPELINE / f"manifest_{q}.json"))
        pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
        pages = list(range(lo, hi + 1))
        calib = crops.Page.calibrate_quarter(pdf, pages, DPI)
        for pdf_page in pages[::STRIDE]:
            want = [dict(r) for r in con.execute(
                "select reg,serial,norm_lang,title_native from entries "
                "where quarter=? and printed_page=?", (q, pdf_page + off))]
            if not want:
                continue
            try:
                pg = crops.Page.render(pdf, pdf_page, DPI, calib)
                found = pg.entries()
            except Exception:
                continue
            if len(found) != len(want):
                continue
            for e, rec in zip(found, want):
                nat = str(rec["title_native"]) == "True"
                old = e.bracket_x is not None
                new = localize.native_span(pg, e) is not None
                stat["old", nat, old] += 1
                stat["new", nat, new] += 1
                bylang[rec["norm_lang"]]["new", nat, new] += 1
        print(f"  {q} [{time.time() - t0:.0f}s]", flush=True)

    def rep(tag, label):
        tp, fn = stat[tag, True, True], stat[tag, True, False]
        fp, tn = stat[tag, False, True], stat[tag, False, False]
        print(f"  {label:32s} n_native={tp + fn:5d}   recall {100 * tp / max(tp + fn, 1):5.1f}%"
              f"   precision {100 * tp / max(tp + fp, 1):5.1f}%"
              f"   FP {fp}/{fp + tn} non-native")

    print("\nNATIVE-SPAN LOCALIZATION  (20% page sample, count-matched pages only)")
    rep("old", "bracket detector (crops.py)")
    rep("new", "Latin-frame span (localize.py)")

    print("\n  by language, new detector (n >= 15):")
    for lang, c in sorted(bylang.items(),
                          key=lambda kv: -(kv[1]["new", True, True] + kv[1]["new", True, False])):
        tp, fn = c["new", True, True], c["new", True, False]
        if tp + fn < 15:
            continue
        print(f"    {str(lang)[:30]:32s} n={tp + fn:4d}   recall {100 * tp / max(tp + fn, 1):5.1f}%")

    json.dump({f"{k[0]}|{k[1]}|{k[2]}": v for k, v in stat.items()},
              open(HERE / "loc_eval.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
