"""Look at the entries where the bracket is missed.

Threshold analysis on the found brackets is a biased sample by construction —
they pass the tests because they were selected by them. The misses have to be
inspected directly.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import crops   # noqa: E402
import lines   # noqa: E402

sys.path.insert(0, str(HERE))
import pagerecs  # noqa: E402

PIPELINE, DB, DPI = ROOT / "pipeline", ROOT / "punjab.db", 306
WANT = 12


def main() -> int:
    con = sqlite3.connect(DB)
    q = "1910Q2"
    man = json.load(open(PIPELINE / f"manifest_{q}.json"))
    pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
    pages = list(range(lo, hi + 1))
    calib = crops.Page.calibrate_quarter(pdf, pages, DPI)

    rows = []
    for pdf_page in pages:
        if len(rows) >= WANT:
            break
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
            if len(rows) >= WANT:
                break
            if e.bracket_x is not None or not rec.get("native"):
                continue
            if str(rec.get("norm_lang")) == "English":
                continue
            ny0, ny1 = lines.first_line_bounds(pg, e.serial_box, lns)
            img = Image.fromarray(pg.gray).crop((c2a, ny0, c2b, ny1 + 1)).convert("L")
            rows.append((img, f"reg {rec.get('reg')} {str(rec.get('norm_lang'))[:16]} "
                              f"band {ny1 - ny0}px"))

    if not rows:
        print("no misses found")
        return 1
    W = max(im.width for im, _ in rows)
    H = sum(im.height + 20 for im, _ in rows)
    sheet = Image.new("L", (W + 8, H + 8), 255)
    d = ImageDraw.Draw(sheet)
    y = 4
    for im, lab in rows:
        sheet.paste(im, (4, y))
        d.text((6, y + im.height + 3), lab, fill=0)
        y += im.height + 20
    out = HERE / "loc_misses.png"
    sheet.save(out)
    print(f"wrote {out}")
    for _, lab in rows:
        print("  ", lab)
    return 0


if __name__ == "__main__":
    sys.exit(main())
