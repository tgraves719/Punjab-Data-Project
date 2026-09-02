"""E0 — is the native script physically recoverable from these scans?

The usual feasibility number for a recogniser is x-height in pixels. For the
Perso-Arabic titles in this catalog that is the wrong measurement. Naskh letter
*skeletons* are few and highly repetitive; what distinguishes b/t/th/p/n/y is
the i'jam — one, two or three dots above or below the rasm. If the dots fuse
into a blob or drop out, the glyph body can be perfectly sharp and the word
still unreadable, by machine or by human. So the binding constraint is dot
separability, and that is what this measures.

Reported per script and per resolution:
  body_h    median height of the main glyph components (the rasm)
  dot_h     median height of the small satellite components (the i'jam)
  dot_gap   median vertical clearance between a dot and the body beneath it
  n_dots    dots per 100 px of title width — a dropout indicator

    python e0_measure.py --cropset cropset
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import statistics

import numpy as np
from PIL import Image
from scipy import ndimage

# A component is treated as i'jam if it is small relative to the line's main
# components and sits clear of them. 0.45 is the trough of the observed
# bimodal height distribution (see report).
DOT_RATIO = 0.45


def components(img: Image.Image) -> tuple[np.ndarray, list]:
    a = np.asarray(img.convert("L"))
    if a.size == 0:
        return a, []
    thr = int(np.percentile(a, 35))
    ink = (a < max(thr, 60)).astype(np.uint8)
    lbl, n = ndimage.label(ink)
    out = []
    for sl_y, sl_x in ndimage.find_objects(lbl):
        h, w = sl_y.stop - sl_y.start, sl_x.stop - sl_x.start
        if h < 2 or w < 2:
            continue
        out.append({"x0": sl_x.start, "x1": sl_x.stop, "y0": sl_y.start,
                    "y1": sl_y.stop, "h": h, "w": w})
    return ink, out


def measure(img: Image.Image) -> dict | None:
    ink, comps = components(img)
    if len(comps) < 2:
        return None
    heights = sorted(c["h"] for c in comps)
    big = statistics.median(heights[len(heights) // 2:])
    if big <= 0:
        return None

    bodies = [c for c in comps if c["h"] >= DOT_RATIO * big]
    dots = [c for c in comps if c["h"] < DOT_RATIO * big]
    if not bodies:
        return None

    # Vertical clearance from each dot to the nearest body it overlaps in x.
    gaps = []
    for d in dots:
        best = None
        for b in bodies:
            if d["x1"] <= b["x0"] or d["x0"] >= b["x1"]:
                continue
            gap = b["y0"] - d["y1"] if d["y1"] <= b["y0"] else d["y0"] - b["y1"]
            if gap >= 0 and (best is None or gap < best):
                best = gap
        if best is not None:
            gaps.append(best)

    width = max(c["x1"] for c in comps) - min(c["x0"] for c in comps)
    return {
        "body_h": statistics.median([c["h"] for c in bodies]),
        "dot_h": statistics.median([c["h"] for c in dots]) if dots else 0.0,
        "dot_w": statistics.median([c["w"] for c in dots]) if dots else 0.0,
        "dot_gap": statistics.median(gaps) if gaps else 0.0,
        "n_dots": len(dots),
        "n_bodies": len(bodies),
        "width": width,
        "dots_per_100px": 100.0 * len(dots) / max(width, 1),
        "ink_frac": float(ink.mean()),
    }


SCRIPT_OF = {
    "Urdu": "Perso-Arabic", "Arabic": "Perso-Arabic", "Persian": "Perso-Arabic",
    "Sindhi": "Perso-Arabic", "Kashmiri": "Perso-Arabic", "Pushto": "Perso-Arabic",
    "Punjabi": "Gurmukhi", "Hindi": "Devanagari", "Sanskrit": "Devanagari",
    "English": "Latin",
}


def script_of(lang: str) -> str:
    if lang in SCRIPT_OF:
        return SCRIPT_OF[lang]
    if lang.startswith("Bilingual") or lang.startswith("Trilingual") or lang.startswith("Polyglot"):
        for k, v in SCRIPT_OF.items():
            if k in lang and v == "Perso-Arabic":
                return "Perso-Arabic (mixed)"
        return "mixed"
    return "other"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cropset", default="cropset")
    ap.add_argument("--out", default="e0_results.json")
    args = ap.parse_args()

    base = pathlib.Path(__file__).resolve().parent / args.cropset
    rows = []
    for man in sorted(base.glob("*_manifest.json")):
        info = json.load(open(man))
        q = info["quarter"]
        for rec in info["records"]:
            if not rec["has_native_crop"]:
                continue
            p = base / q / "native_306" / f"{rec['key']}.png"
            if not p.exists():
                continue
            img = Image.open(p)
            hi = measure(img)
            if hi is None:
                continue
            # The same region as render.py currently delivers it, so the two
            # measurements differ only in resolution.
            lo = measure(img.resize((max(1, round(img.width * 140 / 306)),
                                     max(1, round(img.height * 140 / 306))),
                                    Image.LANCZOS))
            rows.append({"key": rec["key"], "lang": rec["lang"],
                         "script": script_of(rec["lang"]),
                         "hi": hi, "lo": lo})

    if not rows:
        print("no native crops found — run build_cropset.py first")
        return 1

    json.dump(rows, open(base.parent / args.out, "w"), indent=1)

    def agg(subset, side, field):
        vals = [r[side][field] for r in subset if r[side] and r[side][field]]
        return statistics.median(vals) if vals else float("nan")

    # Everything is reported in thousandths of an inch as well as pixels. A
    # count of "dot components resolved" is not comparable across resolutions —
    # it falls simply because a 1-pixel blob is discarded by any sane component
    # filter, which makes the comparison partly definitional. The feature's
    # physical size is the invariant; what changes with DPI is whether the
    # sampling grid can represent it. Two pixels per feature is the floor.
    print(f"E0 — native-script legibility budget   (n={len(rows)} title crops)")
    print("    sizes in 1/1000 inch; px columns show how that lands on each grid\n")
    print(f"{'script':22s} {'n':>3s} | {'body height':>19s} | {'i-jam dot':>19s} | "
          f"{'dot-to-body gap':>19s}")
    print(f"{'':22s} {'':>3s} | {'mil':>7s} {'@306':>5s} {'@140':>5s} | "
          f"{'mil':>7s} {'@306':>5s} {'@140':>5s} | {'mil':>7s} {'@306':>5s} {'@140':>5s}")
    print("-" * 92)

    by = collections.defaultdict(list)
    for r in rows:
        by[r["script"]].append(r)

    summary = {}
    for script, subset in sorted(by.items(), key=lambda kv: -len(kv[1])):
        line = []
        for field in ("body_h", "dot_h", "dot_gap"):
            px306 = agg(subset, "hi", field)
            mil = 1000.0 * px306 / 306.0
            line.append((mil, px306, mil * 140.0 / 1000.0))
        summary[script] = {f: line[i][0] for i, f in
                           enumerate(("body_h_mil", "dot_h_mil", "dot_gap_mil"))}
        print(f"{script:22s} {len(subset):3d} | " + " | ".join(
            f"{m:7.1f} {a:5.1f} {b:5.1f}" for m, a, b in line))

    pa = [r for r in rows if r["script"].startswith("Perso-Arabic")]
    if pa:
        gap_mil = 1000.0 * agg(pa, "hi", "dot_gap") / 306.0
        dot_mil = 1000.0 * agg(pa, "hi", "dot_h") / 306.0
        print()
        print("Perso-Arabic i'jam — the feature that carries letter identity in naskh:")
        for dpi in (140, 306, 400, 600):
            g = gap_mil * dpi / 1000.0
            d = dot_mil * dpi / 1000.0
            verdict = ("below the 2 px sampling floor — dot count not recoverable"
                       if min(g, d) < 2.0 else
                       "at the floor, no margin for ink spread or JPEG noise"
                       if min(g, d) < 3.0 else "resolved with margin")
            print(f"  {dpi:>3d} DPI: dot {d:4.1f} px, clearance {g:4.1f} px  — {verdict}")
        print()
        print("  The scans are 306 DPI, so 400 and 600 are not available without")
        print("  re-imaging the volumes; they are shown to size that decision.")

    json.dump(summary, open(base.parent / "e0_summary.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
