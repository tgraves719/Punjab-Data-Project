"""E5b — build an adjudication worksheet for flags on the golden extraction.

E5a could measure the flag channel on the bake-off candidates because gold gave
it truth. On the golden extraction itself there is no external truth: the only
way to learn whether a flag marks a real error is to look at the page.

This renders each sampled entry at the scan's native resolution and lays the
crops out in a numbered montage, alongside a worksheet holding what the
extractor recorded and what it said it was unsure about. The adjudicator reads
the montage and fills in a verdict per entry:

    error      the transcription is wrong; the flag caught a real mistake
    degraded   the transcription is right; the source really is hard to read
    artifact   the transcription is right; the *catalog* is irregular here
               (no serial printed, a genuine collision, a printer's error)
    spurious   the transcription is right and the source is perfectly legible

The distinction that matters for the queue is `error` versus everything else:
it is the fraction of flagged items that a human can actually fix.

    python e5b_build_worksheet.py --quarters 1910Q1 1910Q2 1910Q3 1910Q4 --n 18
"""

from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "pipeline"))

import crops  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "pipeline"
NATIVE_DPI = 306
MAX_H = 300          # cap tall entries in the montage


def sample_flags(quarters: list[str], n: int, seed: int) -> list[dict]:
    """Stratify by flagged field so the sample spans the queue, not just serials."""
    pool: dict[str, list[dict]] = {}
    for q in quarters:
        man = json.load(open(PIPELINE / f"manifest_{q}.json"))
        off = man["printed_page_offset"]
        for path in sorted((PIPELINE / "data" / q / "extractions").glob("p*.json")):
            printed = int(path.stem[1:])
            for pos, e in enumerate(json.load(open(path, encoding="utf-8"))):
                for f in (e.get("flags") or []):
                    field = str(f.get("field", "?"))
                    pool.setdefault(field, []).append({
                        "quarter": q, "printed_page": printed,
                        "pdf_page": printed - off, "pos": pos,
                        "field": field, "issue": f.get("issue", ""),
                        "value": e.get(field, ""), "reg": e.get("reg", ""),
                        "serial": e.get("serial", ""), "title": e.get("title", ""),
                        "volume_pdf": man["volume_pdf"],
                    })
    rng = random.Random(seed)
    for v in pool.values():
        rng.shuffle(v)
    # Round-robin across fields, largest strata first, until n is reached.
    order = sorted(pool, key=lambda k: -len(pool[k]))
    out: list[dict] = []
    while len(out) < n and any(pool[k] for k in order):
        for k in order:
            if pool[k] and len(out) < n:
                out.append(pool[k].pop())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quarters", nargs="+", default=["1910Q1", "1910Q2", "1910Q3", "1910Q4"])
    ap.add_argument("--n", type=int, default=18)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="e5b")
    args = ap.parse_args()

    here = pathlib.Path(__file__).resolve().parent
    items = sample_flags(args.quarters, args.n, args.seed)
    print(f"sampled {len(items)} flags across {len({i['quarter'] for i in items})} quarters")

    # Group by page so each page is rendered once.
    by_page: dict[tuple, list[dict]] = {}
    for it in items:
        by_page.setdefault((it["volume_pdf"], it["quarter"], it["pdf_page"]), []).append(it)

    calib_cache: dict[str, crops.Calibration] = {}
    rows = []
    for (pdf, quarter, pdf_page), group in sorted(by_page.items(), key=lambda kv: kv[0][1:]):
        if quarter not in calib_cache:
            man = json.load(open(PIPELINE / f"manifest_{quarter}.json"))
            lo, hi = man["pdf_pages"]
            calib_cache[quarter] = crops.Page.calibrate_quarter(pdf, range(lo, hi + 1), NATIVE_DPI)
        try:
            page = crops.Page.render(pdf, pdf_page, NATIVE_DPI, calib_cache[quarter])
            entries = page.entries()
        except Exception as exc:
            for it in group:
                it["skip"] = f"geometry failed: {exc}"
                rows.append(it)
            continue

        n_expected = len(json.load(open(
            PIPELINE / "data" / quarter / "extractions" /
            f"p{group[0]['printed_page']:03d}.json", encoding="utf-8")))
        for it in group:
            # Only trust the crop when the page's entry count matches the register.
            if len(entries) != n_expected or it["pos"] >= len(entries):
                it["skip"] = f"page alignment {len(entries)} != {n_expected}"
                rows.append(it)
                continue
            e = entries[it["pos"]]
            c2a, _ = page.geom.col2
            _, c5b = page.geom.col5
            # Through column 6, not just column 5. Copyright is the fourth most
            # flagged field in the corpus (69 flags), and a crop that stops at
            # column 5 cannot show it — two items in the first run of this
            # worksheet were unadjudicable for exactly that reason. Column 6's
            # right border is often cropped off the scan, so its width is taken
            # from the form's proportions.
            right = min(page.gray.shape[1], int(c5b + 0.75 * page.geom.scale))
            y0 = max(0, e.line_top - 8)
            y1 = min(page.gray.shape[0], max(e.y_bottom, e.line_bottom + 8))
            img = Image.fromarray(page.gray).crop((c2a - 60, y0, right, y1))
            it["crop"] = img
            rows.append(it)

    good = [r for r in rows if "crop" in r]
    if not good:
        print("no crops produced")
        return 1

    pad, label_w = 12, 54
    scaled = []
    for r in good:
        img = r["crop"]
        if img.height > MAX_H:
            img = img.crop((0, 0, img.width, MAX_H))
        scaled.append(img)
    width = label_w + max(i.width for i in scaled) + pad
    height = pad + sum(i.height + pad for i in scaled)
    sheet = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(sheet)
    y = pad
    index = []
    for k, (r, img) in enumerate(zip(good, scaled), 1):
        draw.text((10, y + 8), f"{k:02d}", fill=0)
        sheet.paste(img, (label_w, y))
        draw.line([(0, y - pad // 2), (width, y - pad // 2)], fill=190)
        index.append({"n": k, "quarter": r["quarter"], "printed_page": r["printed_page"],
                      "reg": r["reg"], "serial": r["serial"], "field": r["field"],
                      "issue": r["issue"], "extracted_value": r["value"],
                      "title": (r["title"] or "")[:60], "verdict": None})
        y += img.height + pad

    sheet.save(here / f"{args.out}_montage.png")
    json.dump(index, open(here / f"{args.out}_worksheet.json", "w"), indent=1, ensure_ascii=False)
    skipped = [r for r in rows if "crop" not in r]
    print(f"{len(good)} crops -> {args.out}_montage.png ({width}x{height})")
    if skipped:
        print(f"{len(skipped)} skipped: " +
              "; ".join(f"{s['quarter']} p{s['printed_page']} ({s['skip']})" for s in skipped[:6]))
    for i in index:
        print(f"  {i['n']:02d} {i['quarter']} p{i['printed_page']:>3} reg{i['reg']:>4} "
              f"{i['field']:<16} value={str(i['extracted_value'])[:22]!r:<24} {i['issue'][:52]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
