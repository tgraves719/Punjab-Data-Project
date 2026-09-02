"""Look at the bands. Six render passes of geometry statistics produced AUCs at
chance, which usually means the thing being measured is not the thing assumed.

Writes a montage of first-line bands from column 2, labelled with the register's
`title_native` flag, so the input to the localizer can be inspected directly.
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

import crops  # noqa: E402

sys.path.insert(0, str(HERE))
import pagerecs  # noqa: E402

PIPELINE, DB, DPI = ROOT / "pipeline", ROOT / "punjab.db", 306
WANT_PER_CLASS = 8


def main() -> int:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    q = "1910Q2"
    man = json.load(open(PIPELINE / f"manifest_{q}.json"))
    pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
    pages = list(range(lo, hi + 1))
    calib = crops.Page.calibrate_quarter(pdf, pages, DPI)

    picked = {True: [], False: []}
    for pdf_page in pages:
        if all(len(v) >= WANT_PER_CLASS for v in picked.values()):
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
        c2a, c2b = pg.geom.col2
        for e, rec in zip(found, want):
            nat = bool(rec["native"])
            if len(picked[nat]) >= WANT_PER_CLASS:
                continue
            y0, y1 = max(0, e.line_top - 4), e.line_bottom + 5
            img = Image.fromarray(pg.gray).crop((c2a, y0, c2b, y1))
            picked[nat].append((img, f"{rec['reg']} {str(rec['norm_lang'])[:18]} native={nat}"))

    rows = picked[True] + picked[False]
    if not rows:
        print("nothing picked")
        return 1
    W = max(im.width for im, _ in rows)
    H = sum(im.height + 22 for im, _ in rows)
    sheet = Image.new("L", (W + 8, H + 8), 255)
    d = ImageDraw.Draw(sheet)
    y = 4
    for im, lab in rows:
        sheet.paste(im, (4, y))
        d.text((6, y + im.height + 4), lab, fill=0)
        y += im.height + 22
    out = HERE / "loc_look.png"
    sheet.save(out)
    print(f"wrote {out}  ({len(rows)} bands, {W}x{H})")
    for _, lab in rows:
        print("  ", lab)
    return 0


if __name__ == "__main__":
    sys.exit(main())
