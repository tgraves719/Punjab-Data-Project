"""Settle whether crop-to-record pairing is correct, by eye.

Everything downstream depends on it and two rounds of statistics have now
produced results that only make sense if the labels are shuffled. The
registration number is printed on the page in column 5 and is known from the
register, so a full-width strip carrying both is a direct check: read the
printed number, compare it to the label.
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


def main() -> int:
    q = sys.argv[1] if len(sys.argv) > 1 else "1910Q2"
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    con = sqlite3.connect(DB)
    man = json.load(open(PIPELINE / f"manifest_{q}.json"))
    pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
    pages = list(range(lo, hi + 1))
    calib = crops.Page.calibrate_quarter(pdf, pages, DPI)

    pdf_page = pages[0] + target - 1 if target < pages[0] else target
    want = pagerecs.page_entries(q, pdf_page + off, con)
    pg = crops.Page.render(pdf, pdf_page, DPI, calib)
    found = pg.entries()
    print(f"{q} pdf_page {pdf_page} printed {pdf_page + off}: "
          f"detected {len(found)}, register {len(want)}")

    rows = []
    for i, e in enumerate(found):
        rec = want[i] if i < len(want) else {}
        y0, y1 = max(0, e.line_top - 6), e.line_bottom + 7
        img = Image.fromarray(pg.gray).crop((0, y0, pg.gray.shape[1], y1))
        img.thumbnail((1400, 400))
        rows.append((img, f"idx {i}  label: reg={rec.get('reg')} "
                          f"lang={str(rec.get('norm_lang'))[:16]} native={rec.get('native')}"))

    W = max(im.width for im, _ in rows)
    H = sum(im.height + 20 for im, _ in rows)
    sheet = Image.new("L", (W + 8, H + 8), 255)
    d = ImageDraw.Draw(sheet)
    y = 4
    for im, lab in rows:
        sheet.paste(im, (4, y))
        d.text((6, y + im.height + 3), lab, fill=0)
        y += im.height + 20
    out = HERE / "loc_pairing.png"
    sheet.save(out)
    print(f"wrote {out}")
    for _, lab in rows:
        print("  ", lab)
    return 0


if __name__ == "__main__":
    sys.exit(main())
