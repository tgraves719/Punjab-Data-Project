"""Tune the native-span detector on dumped features.

The first version traded recall for precision badly: recall 17% -> 66% but false
positives on non-native entries went 12% -> 56%. The cause is the `rises` test —
Latin capitals and ascenders rise above a frame whose top is the *median* top of
a line mixing caps, ascenders and x-height letters, so an all-Latin line marks
itself as native.

This sweeps the discriminators over the dumped geometry and reports the
recall / false-positive frontier, so the operating point is chosen rather than
guessed. `title_native` is the label.
"""

from __future__ import annotations

import itertools
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROWS = json.load(open(HERE / "loc_features.json"))


def spans(row, tol, use_rises, r_frac, h_frac, min_frac, min_n, min_dens):
    base, top, xh = row["base"], row["top"], row["xh"]
    comps = row["comps"]
    marks = []
    for x0, x1, y0, y1 in comps:
        m = abs(y1 - base) > tol * xh
        if not m and h_frac is not None:
            m = y1 > base + h_frac * xh
        if not m and use_rises:
            m = y0 < top - r_frac * xh
        marks.append(m)
    runs, cur = [], None
    for (x0, x1, y0, y1), m in zip(comps, marks):
        if not m:
            continue
        if cur is None:
            cur = [x0, x1, 1]
        elif x0 - cur[1] <= 1.6 * xh:
            cur[1] = max(cur[1], x1)
            cur[2] += 1
        else:
            runs.append(cur)
            cur = [x0, x1, 1]
    if cur is not None:
        runs.append(cur)
    ok = []
    for a, b, n in runs:
        w = b - a
        if n < min_n or w < min_frac * xh:
            continue
        if min_dens and n / max(w / xh, 0.5) < min_dens:
            continue
        ok.append((a, b, n))
    if not ok:
        return None
    return max(ok, key=lambda r: r[1] - r[0])


def score(**kw):
    tp = fn = fp = tn = 0
    for r in ROWS:
        hit = spans(r, **kw) is not None
        if r["native"]:
            tp += hit
            fn += not hit
        else:
            fp += hit
            tn += not hit
    return tp, fn, fp, tn


def main() -> int:
    n_nat = sum(1 for r in ROWS if r["native"])
    print(f"loaded {len(ROWS)} entries — {n_nat} native, {len(ROWS) - n_nat} non-native")
    base_hit = sum(1 for r in ROWS if r["bracket"] and r["native"])
    base_fp = sum(1 for r in ROWS if r["bracket"] and not r["native"])
    print(f"bracket baseline: recall {100 * base_hit / n_nat:.1f}%  "
          f"FP {100 * base_fp / max(len(ROWS) - n_nat, 1):.1f}%\n")

    grid = []
    for tol, rises, h_frac, min_n, dens in itertools.product(
            (0.25, 0.35, 0.45, 0.60, 0.80),
            (False, True),
            (None, 0.45, 0.70),
            (2, 3, 4),
            (0, 1.5, 2.5)):
        tp, fn, fp, tn = score(tol=tol, use_rises=rises, r_frac=0.55, h_frac=h_frac,
                               min_frac=0.55, min_n=min_n, min_dens=dens)
        rec, fpr = 100 * tp / max(tp + fn, 1), 100 * fp / max(fp + tn, 1)
        grid.append((rec, fpr, tol, rises, h_frac, min_n, dens))

    # Pareto frontier: highest recall at each false-positive ceiling.
    print(f"{'FP ceiling':>11s} | {'recall':>7s} | {'tol':>5s} {'rises':>6s} "
          f"{'hang':>5s} {'min_n':>6s} {'dens':>5s}")
    print("-" * 62)
    for ceil in (5, 10, 15, 20, 30, 40, 60):
        cand = [g for g in grid if g[1] <= ceil]
        if not cand:
            print(f"{ceil:10d}% |    none")
            continue
        best = max(cand, key=lambda g: g[0])
        rec, fpr, tol, rises, h_frac, min_n, dens = best
        print(f"{ceil:10d}% | {rec:6.1f}% | {tol:5.2f} {str(rises):>6s} "
              f"{str(h_frac):>5s} {min_n:6d} {dens:5.1f}   (actual FP {fpr:.1f}%)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
