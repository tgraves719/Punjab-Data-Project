"""Per-page text-line segmentation for column 2, and a first-line bound that
does not swallow its neighbour.

`crops.Page._first_line_bounds` thresholds the column-2 row profile at 4% of its
maximum and keeps the run overlapping the serial's centre. At 306 DPI that
threshold is low enough that a descender from the line above or an ascender from
the line below bridges the gap, so the run spans two text lines. Measured band
heights ran to 67 px against a ~30 px line, and the consequence propagates:

  * `_find_bracket` tests bracket height against that band, so a correct bracket
    is rejected for being too short — 68% of all bracket misses (loc_diag);
  * any geometry computed on the band mixes two baselines, which is why
    entry-level baseline non-conformity came out *higher* for all-Latin English
    entries (0.367) than for native-script ones (0.261).

Here the page's line pitch is estimated once from the whole column, line cores
are found at a threshold high enough to keep neighbours apart, and each core is
then grown outward only as far as the trough between it and the next.
"""

from __future__ import annotations

import numpy as np


def _runs(mask):
    out, start = [], None
    for i, v in enumerate(mask):
        if v and start is None:
            start = i
        elif not v and start is not None:
            out.append((start, i - 1))
            start = None
    if start is not None:
        out.append((start, len(mask) - 1))
    return out


def page_lines(page, core_frac: float = 0.30, edge_frac: float = 0.08):
    """Text lines in column 2 as (top, bottom) in page coordinates, plus pitch."""
    c2a, c2b = page.geom.col2
    prof = page.ink[page.geom.body_top:page.geom.body_bottom, c2a + 2:c2b - 2].sum(axis=1)
    if prof.size == 0 or prof.max() == 0:
        return [], 0.0
    p = prof.astype(float)
    if p.size > 5:                       # light smoothing, one line is many rows
        k = np.ones(3) / 3.0
        p = np.convolve(p, k, mode="same")
    hi = p.max()
    cores = _runs(p > core_frac * hi)
    cores = [c for c in cores if c[1] - c[0] >= 2]
    if not cores:
        return [], 0.0
    centres = [0.5 * (a + b) for a, b in cores]
    pitch = float(np.median(np.diff(centres))) if len(centres) > 2 else float(
        np.median([b - a for a, b in cores]) * 1.6)

    lines = []
    for i, (a, b) in enumerate(cores):
        lo_stop = 0 if i == 0 else int(0.5 * (cores[i - 1][1] + a))
        hi_stop = len(p) - 1 if i == len(cores) - 1 else int(0.5 * (b + cores[i + 1][0]))
        t = a
        while t > lo_stop and p[t - 1] > edge_frac * hi:
            t -= 1
        bt = b
        while bt < hi_stop and p[bt + 1] > edge_frac * hi:
            bt += 1
        lines.append((page.geom.body_top + t, page.geom.body_top + bt))
    return lines, pitch


def first_line_bounds(page, serial_box, lines=None):
    """Vertical extent of the text line in column 2 beside a serial number."""
    if lines is None:
        lines, _ = page_lines(page)
    if not lines:
        return serial_box[1], serial_box[3]
    centre = 0.5 * (serial_box[1] + serial_box[3])
    inside = [ln for ln in lines if ln[0] - 4 <= centre <= ln[1] + 4]
    if inside:
        return min(inside, key=lambda ln: ln[1] - ln[0])
    return min(lines, key=lambda ln: abs(0.5 * (ln[0] + ln[1]) - centre))
