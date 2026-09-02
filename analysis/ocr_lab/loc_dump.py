"""Dump first-line component geometry per entry, once, so detector parameters
can be tuned without re-rendering 600 pages for every setting.

One render pass writes, for each entry on a count-matched page: the Latin frame
estimated from the right of the line, every component's box, and the register's
own `title_native` label.
"""

from __future__ import annotations

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

sys.path.insert(0, str(HERE))
import pagerecs     # noqa: E402

PIPELINE, DB, DPI, STRIDE = ROOT / "pipeline", ROOT / "punjab.db", 306, 3


def main() -> int:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
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
            c2a, c2b = pg.geom.col2
            for e, rec in zip(found, want):
                y0, y1 = e.line_top, e.line_bottom + 1
                if y1 - y0 < 8:
                    continue
                band = pg.ink[y0:y1, c2a:c2b]
                comps = localize._components(band)
                if len(comps) < 4:
                    continue
                frame = localize._latin_frame(comps, band.shape[1])
                if frame is None:
                    continue
                rows.append({
                    "q": q, "reg": rec["reg"], "lang": rec["norm_lang"],
                    "native": bool(rec["native"]),
                    "bracket": e.bracket_x is not None,
                    "bracket_x": (None if e.bracket_x is None else int(e.bracket_x - c2a)),
                    "band_w": int(band.shape[1]), "band_h": int(band.shape[0]),
                    "base": frame[0], "top": frame[1], "xh": frame[2],
                    "comps": [[c["x0"], c["x1"], c["y0"], c["y1"]] for c in comps],
                })
        print(f"  {q}: {len(rows)} entries [{time.time() - t0:.0f}s]", flush=True)
    json.dump(rows, open(HERE / "loc_features.json", "w"))
    print(f"\nTOTAL {len(rows)} entries dumped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
