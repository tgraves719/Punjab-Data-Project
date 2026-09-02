"""Can the 21% of pages lost to entry-count mismatch be recovered?

loc_diag found the mismatch is dominated by over-detection: +1 on 13 pages, +2
on 4, +3 and +4 on one each, against -1 on 4 and -2 on 1 (n=112). So the
question is whether the spurious boxes can be identified and dropped.

The register knows the registration numbers printed on every page, and the
detector already groups the numerals of each one — so the *digit count* of each
detected box is available and is currently discarded. If the detected
digit-count sequence reproduces the expected one on count-matched pages, digit
count is a reliable alignment key and can be used to drop spurious boxes on
mismatched pages.

This tests that premise before anything is built on it.
"""

from __future__ import annotations

import collections
import json
import pathlib
import sqlite3
import sys
import time

import numpy as np
from scipy import ndimage

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import crops  # noqa: E402

PIPELINE, DB, DPI, STRIDE = ROOT / "pipeline", ROOT / "punjab.db", 306, 4


def detect_with_digits(page):
    """crops.Page._find_entries, but keeping each group's digit count and x-centre."""
    g = page.geom
    x0, x1 = g.col5
    band = page.ink[g.body_top:g.body_bottom, x0 + 2:x1 - 2]
    if band.size == 0:
        return []
    lbl, n = ndimage.label(band)
    if n == 0:
        return []
    heights, boxes = [], []
    for sl_y, sl_x in ndimage.find_objects(lbl):
        h, w = sl_y.stop - sl_y.start, sl_x.stop - sl_x.start
        if h < 6 or w < 3 or h > 0.06 * band.shape[0]:
            continue
        heights.append(h)
        boxes.append((sl_x.start + x0 + 2, sl_y.start + g.body_top,
                      sl_x.stop + x0 + 2, sl_y.stop + g.body_top))
    if not boxes:
        return []
    med = float(np.median(heights))
    boxes = [b for b, h in zip(boxes, heights) if 0.55 * med <= h <= 1.9 * med]
    boxes.sort(key=lambda b: (b[1], b[0]))
    groups = []
    for b in boxes:
        if groups:
            gy0 = min(x[1] for x in groups[-1])
            gy1 = max(x[3] for x in groups[-1])
            if min(gy1, b[3]) - max(gy0, b[1]) > 0.45 * min(gy1 - gy0, b[3] - b[1]):
                groups[-1].append(b)
                continue
        groups.append([b])
    col_width = x1 - x0
    out = []
    for gp in groups:
        if len(gp) > 4:
            continue
        bx = (min(x[0] for x in gp), min(x[1] for x in gp),
              max(x[2] for x in gp), max(x[3] for x in gp))
        bw, bh = bx[2] - bx[0], bx[3] - bx[1]
        if bw > 0.92 * col_width or bw > 5 * bh:
            continue
        out.append({"box": bx, "ndigits": len(gp), "xc": (bx[0] + bx[2]) / 2.0})
    return out


def main() -> int:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
    seq_ok = collections.Counter()
    delta_hist = collections.Counter()
    recoverable = collections.Counter()
    t0 = time.time()
    for q in quarters:
        man = json.load(open(PIPELINE / f"manifest_{q}.json"))
        pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
        pages = list(range(lo, hi + 1))
        calib = crops.Page.calibrate_quarter(pdf, pages, DPI)
        for pdf_page in pages[::STRIDE]:
            want = [dict(r) for r in con.execute(
                "select reg from entries where quarter=? and printed_page=? order by rowid",
                (q, pdf_page + off))]
            if not want:
                continue
            try:
                pg = crops.Page.render(pdf, pdf_page, DPI, calib)
                det = detect_with_digits(pg)
            except Exception:
                continue
            exp = [len(str(r["reg"]).strip()) for r in want]
            got = [d["ndigits"] for d in det]
            d = len(got) - len(exp)
            delta_hist[d] += 1
            if d == 0:
                seq_ok["match" if got == exp else "mismatch"] += 1
                continue
            if d > 0:
                # Try dropping the d boxes whose x-centre deviates most from the
                # median: reg numbers share a column alignment, stray marks do not.
                xs = np.array([x["xc"] for x in det])
                keep = sorted(range(len(det)), key=lambda i: abs(xs[i] - np.median(xs)))[:len(exp)]
                cand = [det[i]["ndigits"] for i in sorted(keep)]
                recoverable["x-align recovers digit sequence" if cand == exp
                            else "x-align does not recover"] += 1
        print(f"  {q} [{time.time() - t0:.0f}s]", flush=True)

    tot = sum(delta_hist.values())
    print(f"\nPAGES: {tot} rendered")
    for d in sorted(delta_hist):
        print(f"  delta {d:+d}: {delta_hist[d]}")
    m, mm = seq_ok["match"], seq_ok["mismatch"]
    print(f"\nOn count-matched pages, does the detected digit-count sequence equal the register's?")
    print(f"  match {m}, mismatch {mm}  -> {100 * m / max(m + mm, 1):.1f}% "
          f"(this is the ceiling on digit count as an alignment key)")
    print(f"\nOn over-detected pages, does x-alignment pruning restore it?")
    for k, v in recoverable.most_common():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
