"""Tune peak selection on the correlation curve.

Recall is solved — 86.5% of flagged entries get a crop — but the boundary is
not: leftmost-above-threshold lands a median 311 px away from the shape
detector's bracket, because a tall vertical stroke in the native script (alif,
lam, a danda) clears 0.62 before the real bracket does. Taking the global
maximum instead puts a third of boundaries hundreds of pixels too far right, on
the closing bracket of the gloss.

So neither end works alone. This dumps the correlation curve for entries whose
bracket position is known from the shape detector, and sweeps rules of the form
"leftmost peak within a margin of the global maximum" against it.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import crops     # noqa: E402
import lines     # noqa: E402
import localize  # noqa: E402

sys.path.insert(0, str(HERE))
import pagerecs  # noqa: E402

PIPELINE, DB, DPI = ROOT / "pipeline", ROOT / "punjab.db", 306
STRIDE = int(sys.argv[1]) if len(sys.argv) > 1 else 6


def main() -> int:
    con = sqlite3.connect(DB)
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
    tmpl = localize.template()
    rows = []
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
                continue
            if len(found) != len(want):
                continue
            lns, _ = lines.page_lines(pg)
            c2a, c2b = pg.geom.col2
            for e, rec in zip(found, want):
                if e.bracket_x is None:
                    continue
                y0, y1 = lines.first_line_bounds(pg, e.serial_box, lns)
                g = pg.gray[y0:y0 + localize.TH, c2a:c2b]
                if g.shape[0] < localize.TH:
                    g = np.pad(g, ((0, localize.TH - g.shape[0]), (0, 0)), constant_values=255)
                c = localize.ncc_curve(g, tmpl)
                if c.size == 0:
                    continue
                rows.append({"truth": int(e.bracket_x - c2a),
                             "curve": [round(float(v), 3) for v in c]})
        print(f"  {q}: {len(rows)} anchored [{time.time()-t0:.0f}s]", flush=True)

    json.dump(rows, open(HERE / "loc_curves.json", "w"))
    print(f"\nanchored curves: {len(rows)}")

    def pick(c, absmin, rel, guard=6):
        m = float(np.max(c))
        thr = max(absmin, rel * m)
        idx = np.where(c >= thr)[0]
        if idx.size == 0:
            return None
        x = int(idx[0])
        lo, hi = max(0, x - guard), min(len(c), x + guard + 1)
        return lo + int(np.argmax(c[lo:hi]))

    print(f"\n{'absmin':>7s} {'rel':>6s} | {'found':>6s} {'p50':>6s} {'p90':>7s} {'<=2px':>7s} {'<=8px':>7s}")
    print("-" * 56)
    best = None
    for absmin in (0.55, 0.62, 0.68, 0.72, 0.76, 0.80):
        for rel in (0.0, 0.80, 0.88, 0.92, 0.96, 1.0):
            errs, miss = [], 0
            for r in rows:
                c = np.asarray(r["curve"], np.float32)
                p = pick(c, absmin, rel)
                if p is None:
                    miss += 1
                else:
                    errs.append(abs(p - r["truth"]))
            if not errs:
                continue
            e = sorted(errs)
            hit = 100 * len(errs) / len(rows)
            ok2 = 100 * sum(v <= 2 for v in e) / len(e)
            ok8 = 100 * sum(v <= 8 for v in e) / len(e)
            print(f"{absmin:7.2f} {rel:6.2f} | {hit:5.0f}% {e[len(e)//2]:6d} "
                  f"{e[int(.9*len(e))]:7d} {ok2:6.0f}% {ok8:6.0f}%")
            score = ok2 * hit / 100.0
            if best is None or score > best[0]:
                best = (score, absmin, rel, ok2, hit)
    if best:
        print(f"\nbest by (%<=2px x found): absmin={best[1]:.2f} rel={best[2]:.2f} "
              f"-> {best[3]:.0f}% within 2px on {best[4]:.0f}% found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
