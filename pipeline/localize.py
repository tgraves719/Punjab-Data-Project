"""Locate the native-script title of an entry.

History, because two approaches failed first and the reasons are worth keeping:

  * The shape-test bracket detector in crops.py reaches 17% recall. Rendering
    the misses shows the bracket is plainly legible in most of them, so the six
    tests, not the glyph, are the problem - worn lithographic strokes break the
    "solid left column" requirement above all. Its precision is excellent
    (~2% FP), which makes it a good source of training patches and a bad
    detector.

  * Finding the native span by non-conformity to the Latin baseline reaches 65%
    recall at 28% false positives with a median boundary error of 3.5
    x-heights - useless for cropping. Per-component separation is real
    (AUC 0.754 on title-first entries) but too weak to survive aggregation.

What works is template matching. The catalog's Latin fount is metal set and
every scan is 306 DPI, so the opening bracket is near-constant: 35 px tall
(p05 29, p95 37), 12 px wide (p05 11, p95 14), measured over 158 instances.
Templates are harvested from the shape detector's high-precision hits.

Two details matter, and both were found the hard way:

  * peak selection. Taking the global maximum lands on the *closing* bracket of
    the gloss for about a third of entries. Taking the first index over a
    permissive threshold lands on a tall native stroke - alif, lam, a danda -
    a median 311 px early. What works is the leftmost peak that is also within
    `rel` of the global maximum.
  * search every line of the entry, not only its first. Some entries open with
    a continuation line carrying no bracket at all.
"""

from __future__ import annotations

import pathlib

import numpy as np

TH, TW = 40, 16
_TEMPLATE = None


def template(path=None):
    global _TEMPLATE
    if _TEMPLATE is None:
        p = pathlib.Path(path or pathlib.Path(__file__).resolve().parents[1]
                         / "analysis" / "ocr_lab" / "bracket_template.npy")
        _TEMPLATE = np.load(p).astype(np.float32)
    return _TEMPLATE


def ncc_curve(band: np.ndarray, tmpl: np.ndarray) -> np.ndarray:
    """Normalised cross-correlation of tmpl over band, one score per x."""
    h, w = tmpl.shape
    H, W = band.shape
    if W < w or H < h:
        return np.zeros(0, np.float32)
    t = tmpl - tmpl.mean()
    tn = float(np.linalg.norm(t)) or 1.0
    strip = band[:h].astype(np.float32)
    out = np.zeros(W - w + 1, np.float32)
    for x in range(W - w + 1):
        s = strip[:, x:x + w]
        s = s - s.mean()
        sn = float(np.linalg.norm(s))
        out[x] = 0.0 if sn < 1e-6 else float((s * t).sum() / (sn * tn))
    return out


def leftmost_match(band, tmpl, absmin: float = 0.80, rel: float = 0.92,
                   guard: int = 6):
    """(x, score) of the leftmost strong peak, or (None, score).

    Swept against 65 entries whose bracket position is known independently
    (loc_peak.py). At absmin 0.80 / rel 0.92 the gross-error tail disappears:
    p90 error 3 px, 86% within 2 px. Relaxing absmin to 0.72 finds more
    brackets but brings back a p90 of 848 px, i.e. wrong-glyph matches.
    A low-scoring entry should be queued, not cropped badly.
    """
    c = ncc_curve(band, tmpl)
    if c.size == 0:
        return None, 0.0
    m = float(c.max())
    idx = np.where(c >= max(absmin, rel * m))[0]
    if idx.size == 0:
        return None, m
    x = int(idx[0])
    lo, hi = max(0, x - guard), min(c.size, x + guard + 1)
    return int(lo + int(np.argmax(c[lo:hi]))), m


def _dash_left_bound(comps, bracket_x, xh):
    """Right edge of the em-dash following a roman author name, if present.

    Found in 90% of author-first entries; the measured gap from dash to bracket
    has a median of 11 x-heights, which is the width of a two or three word
    native title, so it is finding the right glyph.
    """
    d = [c for c in comps
         if c["x1"] <= bracket_x - 2
         and (c["x1"] - c["x0"]) >= 2.5 * (c["y1"] - c["y0"])
         and (c["x1"] - c["x0"]) >= 0.6 * xh]
    return max((c["x1"] for c in d), default=None)


def native_box(page, entry, lines_mod, has_author: bool, absmin: float = 0.80,
               pad: int = 6, later_line_absmin: float = 0.88):
    """(box, score, line_index) of the native-script title in page coordinates.

    Returns (None, score, -1) when no confident bracket is found; the caller
    should queue those rather than emit a crop. `has_author` comes from the
    register, which knows whether the entry is author-first, and decides
    whether the span starts at the column edge or after the em-dash.

    Later lines are held to a stricter threshold than the first. Searching the
    whole entry was added because some entries open on a continuation line with
    no bracket at all, but at a uniform threshold it back-fires: when the first
    line's bracket just misses the bar, a spurious match on line two is taken
    instead, which is worse than returning nothing. Measured end to end, that
    put the boundary-error p90 at 597 px against 3 px for first-line matches.
    """
    from scipy import ndimage

    c2a, c2b = page.geom.col2
    lns, _ = lines_mod.page_lines(page)
    # Index 0 must be the line beside the serial. Selecting lines by the entry's
    # y-range instead puts a continuation line first whenever the serial's own
    # line starts a few pixels above y_top, which silently made "first line"
    # mean the second one for a large share of entries.
    first = lines_mod.first_line_bounds(page, entry.serial_box, lns)
    cand = [first] + [ln for ln in lns
                      if ln[0] > first[1] and ln[0] <= entry.y_bottom + 4]
    tmpl = template()
    best_score = 0.0

    for li, (y0, y1) in enumerate(cand[:3]):
        g = page.gray[y0:y0 + TH, c2a:c2b]
        if g.shape[0] < TH:
            g = np.pad(g, ((0, TH - g.shape[0]), (0, 0)), constant_values=255)
        bar = absmin if li == 0 else later_line_absmin
        bx, score = leftmost_match(g, tmpl, bar)
        best_score = max(best_score, score)
        if bx is None:
            continue
        left = c2a
        if has_author:
            band = page.ink[y0:y1 + 1, c2a:c2b]
            lbl, n = ndimage.label(band)
            comps = []
            for sl_y, sl_x in ndimage.find_objects(lbl):
                h, w = sl_y.stop - sl_y.start, sl_x.stop - sl_x.start
                if h < 3 or w < 2:
                    continue
                comps.append({"x0": sl_x.start, "x1": sl_x.stop,
                              "y0": sl_y.start, "y1": sl_y.stop})
            xh = max(6.0, (y1 - y0) / 2.2)
            e = _dash_left_bound(comps, bx, xh)
            if e is not None:
                left = c2a + e
        right = c2a + bx
        if right - left < 8:
            continue
        return (max(0, left - pad), max(0, y0 - pad), right - 2, y1 + pad), score, li
    return None, best_score, -1
