"""Find the bracket by template matching instead of by six shape tests.

The six-test detector reaches 17% recall. Inspecting the misses shows the
bracket is plainly present and legible in most of them, so the tests, not the
glyph, are the problem: worn lithographic strokes break the "solid left column"
requirement, and continuation lines and mis-cut bands account for the rest.

The catalog's Latin fount is metal-set and the scans are all 306 DPI, so the
glyph is nearly constant: measured over 158 confirmed instances, 35 px tall
(p05 29, p95 37) and 12 px wide (p05 11, p95 14). That is exactly the situation
template matching is for, and it needs no thresholds on shape.

Templates are harvested from the entries where the existing detector fires — a
high-precision, low-recall source of ground truth — averaged, and matched by
normalised cross-correlation along every entry's first line.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import statistics
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

import crops   # noqa: E402
import lines   # noqa: E402

sys.path.insert(0, str(HERE))
import pagerecs  # noqa: E402

PIPELINE, DB, DPI, STRIDE = ROOT / "pipeline", ROOT / "punjab.db", 306, 3
TH, TW = 40, 16            # template box, a little larger than the glyph


def patch(gray, x, ytop, h, w=TW):
    y0 = ytop
    sub = gray[y0:y0 + h, x:x + w]
    if sub.shape != (h, w):
        out = np.full((h, w), 255, np.uint8)
        out[:sub.shape[0], :sub.shape[1]] = sub
        return out
    return sub


def ncc(band, tmpl):
    """Normalised cross-correlation of tmpl over band, per x. Returns array."""
    h, w = tmpl.shape
    H, W = band.shape
    if W < w or H < h:
        return np.zeros(max(W - w + 1, 1))
    t = tmpl.astype(np.float32)
    t -= t.mean()
    tn = np.linalg.norm(t) or 1.0
    out = np.zeros(W - w + 1, np.float32)
    strip = band[:h].astype(np.float32)
    for x in range(W - w + 1):
        s = strip[:, x:x + w]
        s = s - s.mean()
        sn = np.linalg.norm(s)
        out[x] = 0.0 if sn < 1e-6 else float((s * t).sum() / (sn * tn))
    return out


def main() -> int:
    con = sqlite3.connect(DB)
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
    bands, meta, tmpls = [], [], []
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
                ny0, ny1 = lines.first_line_bounds(pg, e.serial_box, lns)
                g = pg.gray[ny0:ny0 + TH, c2a:c2b]
                if g.shape[0] < TH:
                    g = np.pad(g, ((0, TH - g.shape[0]), (0, 0)), constant_values=255)
                bands.append(g.copy())
                meta.append({"lang": rec.get("norm_lang", ""), "native": bool(rec.get("native")),
                             "brx": None if e.bracket_x is None else int(e.bracket_x - c2a)})
                if e.bracket_x is not None:
                    tmpls.append(patch(pg.gray, e.bracket_x, ny0, TH))
        print(f"  {q}: {len(bands)} bands, {len(tmpls)} templates [{time.time()-t0:.0f}s]", flush=True)

    if len(tmpls) < 20:
        print("not enough templates")
        return 1
    T = np.stack(tmpls).astype(np.float32)
    tmpl = np.median(T, axis=0)
    np.save(HERE / "bracket_template.npy", tmpl)

    POS = [i for i, m in enumerate(meta) if m["lang"] != "English" and m["native"]]
    NEG = [i for i, m in enumerate(meta) if m["lang"] == "English" and not m["native"]]
    ANCH = [i for i, m in enumerate(meta) if m["brx"] is not None]
    print(f"\nbands {len(bands)}  templates {len(tmpls)}  POS {len(POS)}  NEG {len(NEG)}  anchored {len(ANCH)}")

    scores, argx = [], []
    for g in bands:
        c = ncc(g, tmpl)
        scores.append(float(c.max()) if c.size else 0.0)
        argx.append(int(c.argmax()) if c.size else -1)

    print(f"\n{'thresh':>7s} {'recall':>8s} {'FP':>7s} {'edge err (xh~13px)':>20s}")
    for th in (0.35, 0.45, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80):
        rec = 100 * sum(scores[i] >= th for i in POS) / max(len(POS), 1)
        fp = 100 * sum(scores[i] >= th for i in NEG) / max(len(NEG), 1)
        errs = [abs(argx[i] - meta[i]["brx"]) for i in ANCH if scores[i] >= th]
        e = statistics.median(errs) if errs else float("nan")
        print(f"{th:7.2f} {rec:7.1f}% {fp:6.1f}% {e:15.1f} px  (n={len(errs)})")

    json.dump({"scores": scores, "argx": argx, "meta": meta},
              open(HERE / "loc_template.json", "w"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
