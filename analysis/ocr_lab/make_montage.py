"""Assemble native-script title crops into a numbered montage for blind reading.

Each row is one title, labelled only by index. The catalog's romanization is not
shown — that is the point: the reader must work from the image alone, so that
the result can be compared against a prediction made from the romanization
alone (arm A) and against the two together.

    python make_montage.py --dpi 306 --out montage_306.png
    python make_montage.py --dpi 140 --out montage_140.png   # simulates render.py

The 140 DPI version is produced by downsampling the native crop and scaling it
back up, so both montages present the same physical region at the same size on
screen and differ only in the information the pipeline retained.
"""

from __future__ import annotations

import argparse
import json
import pathlib

from PIL import Image, ImageDraw

ROW_H = 96          # display height per title, in montage pixels
PAD = 10
LABEL_W = 58
NATIVE_DPI = 306


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cropset", default="cropset")
    ap.add_argument("--dpi", type=int, default=NATIVE_DPI)
    ap.add_argument("--script", default=None, help="filter by script, e.g. Perso-Arabic")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base = pathlib.Path(__file__).resolve().parent
    cs = base / args.cropset
    scripts = {r["key"]: r["script"] for r in json.load(open(base / "e0_results.json"))}

    items = []
    for man in sorted(cs.glob("*_manifest.json")):
        info = json.load(open(man))
        for rec in info["records"]:
            if not rec["has_native_crop"]:
                continue
            if args.script and scripts.get(rec["key"], "") != args.script:
                continue
            p = cs / info["quarter"] / "native_306" / f"{rec['key']}.png"
            if p.exists():
                items.append((rec["key"], p))
    if not items:
        print("no crops matched")
        return 1

    rows = []
    for key, path in items:
        img = Image.open(path).convert("L")
        if args.dpi != NATIVE_DPI:
            small = img.resize((max(1, round(img.width * args.dpi / NATIVE_DPI)),
                                max(1, round(img.height * args.dpi / NATIVE_DPI))),
                               Image.LANCZOS)
            img = small.resize(img.size, Image.LANCZOS)
        scale = ROW_H / img.height
        img = img.resize((max(1, round(img.width * scale)), ROW_H), Image.LANCZOS)
        rows.append((key, img))

    width = LABEL_W + PAD + max(r[1].width for r in rows) + PAD
    height = PAD + sum(r[1].height + PAD for r in rows)
    sheet = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(sheet)

    y = PAD
    index = []
    for i, (key, img) in enumerate(rows, 1):
        draw.text((PAD, y + ROW_H // 2 - 6), f"{i:02d}", fill=0)
        sheet.paste(img, (LABEL_W, y))
        draw.line([(LABEL_W - 4, y - PAD // 2), (width, y - PAD // 2)], fill=200)
        index.append({"n": i, "key": key})
        y += img.height + PAD

    sheet.save(base / args.out)
    json.dump(index, open(base / (pathlib.Path(args.out).stem + "_index.json"), "w"), indent=1)
    print(f"{len(rows)} crops -> {args.out} ({width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
