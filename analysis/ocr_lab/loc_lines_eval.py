"""Does correcting the line band fix the bracket, and does the span detector
then separate native from Latin?

One render pass measures, per entry: the old band, the re-segmented band, the
bracket found under each, and the component geometry under the new band.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import statistics
import sys
import time

import numpy as np
from scipy import ndimage

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import crops     # noqa: E402
import lines     # noqa: E402
import localize  # noqa: E402

sys.path.insert(0, str(HERE))
import pagerecs  # noqa: E402

PIPELINE, DB, DPI, STRIDE = ROOT / "pipeline", ROOT / "punjab.db", 306, 3


def bracket_in(page, y0, y1):
    """crops._find_bracket, against an explicit band."""
    c2a, c2b = page.geom.col2
    if y1 - y0 < 8:
        return None
    band = page.ink[y0:y1, c2a:c2b]
    lbl, n = ndimage.label(band)
    if n == 0:
        return None
    comps = []
    for sl_y, sl_x in ndimage.find_objects(lbl):
        h, w = sl_y.stop - sl_y.start, sl_x.stop - sl_x.start
        if h < 3 or w < 2:
            continue
        comps.append((sl_x.start, sl_x.stop, sl_y, sl_x))
    if len(comps) < 4:
        return None
    comps.sort()
    lh = y1 - y0
    prev_right = 0
    for x_start, x_stop, sl_y, sl_x in comps:
        gap = x_start - prev_right
        prev_right = max(prev_right, x_stop)
        sub = band[sl_y, sl_x]
        h, w = sub.shape
        if not (0.55 * lh <= h <= 1.15 * lh):
            continue
        if not (0.18 * lh <= w <= 0.40 * lh):
            continue
        if sub[:, 0].mean() < 0.75 or sub[:, -1].mean() > 0.5:
            continue
        k = max(1, h // 5)
        top, bot = sub[:k].sum(axis=1).mean(), sub[-k:].sum(axis=1).mean()
        mid = sub[k:-k].sum(axis=1).mean() if h > 2 * k else top
        if mid <= 0 or max(top, bot) < 1.3 * mid:
            continue
        if gap < 0.30 * lh:
            continue
        return x_start + c2a
    return None


def main() -> int:
    con = sqlite3.connect(DB)
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
    out = []
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
            lns, pitch = lines.page_lines(pg)
            c2a, c2b = pg.geom.col2
            for e, rec in zip(found, want):
                ny0, ny1 = lines.first_line_bounds(pg, e.serial_box, lns)
                band = pg.ink[ny0:ny1 + 1, c2a:c2b]
                comps = localize._components(band)
                frame = localize._latin_frame(comps, band.shape[1]) if len(comps) >= 4 else None
                out.append({
                    "q": q, "reg": rec.get("reg"), "lang": rec.get("norm_lang", ""),
                    "native": bool(rec.get("native")),
                    "old_h": int(e.line_bottom - e.line_top), "new_h": int(ny1 - ny0),
                    "pitch": float(pitch),
                    "old_br": e.bracket_x is not None,
                    "new_br": bracket_in(pg, ny0, ny1 + 1) is not None,
                    "base": None if not frame else frame[0],
                    "top": None if not frame else frame[1],
                    "xh": None if not frame else frame[2],
                    "comps": [[c["x0"], c["x1"], c["y0"], c["y1"]] for c in comps],
                    "brx": (None if bracket_in(pg, ny0, ny1 + 1) is None
                            else int(bracket_in(pg, ny0, ny1 + 1) - c2a)),
                })
        print(f"  {q}: {len(out)} [{time.time()-t0:.0f}s]", flush=True)

    json.dump(out, open(HERE / "loc_lines.json", "w"))
    oh = [r["old_h"] for r in out]
    nh = [r["new_h"] for r in out]
    pt = [r["pitch"] for r in out if r["pitch"]]
    print(f"\nn={len(out)}   line pitch median {statistics.median(pt):.0f} px")
    print(f"band height  old: median {statistics.median(oh):.0f}  p90 {np.percentile(oh,90):.0f}  max {max(oh)}")
    print(f"band height  new: median {statistics.median(nh):.0f}  p90 {np.percentile(nh,90):.0f}  max {max(nh)}")
    POS = [r for r in out if r["lang"] != "English" and r["native"]]
    NEG = [r for r in out if r["lang"] == "English" and not r["native"]]
    for tag in ("old_br", "new_br"):
        rec = 100 * sum(r[tag] for r in POS) / max(len(POS), 1)
        fp = 100 * sum(r[tag] for r in NEG) / max(len(NEG), 1)
        print(f"bracket {tag:7s}: recall {rec:5.1f}%   FP {fp:5.1f}%   (POS {len(POS)}, NEG {len(NEG)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
