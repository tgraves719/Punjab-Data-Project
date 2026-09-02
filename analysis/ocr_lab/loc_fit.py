"""Fit and evaluate the native-span detector on bracket-anchored ground truth.

Per-component separability, measured on title-first non-English entries where
everything left of the bracket really is native script (author-first entries
put a roman author name there and were contaminating the earlier measurement):

    |y1 - baseline| / x-height     native 0.357   latin 0.051   AUC 0.754
    |y0 - ascender| / x-height     native 0.368   latin 0.167   AUC 0.683

So baseline non-conformity is the right signal after all; the first attempt
failed because it was scored against noisy labels and fitted against a
contaminated native side, not because the premise was wrong.

The span is then the maximal-scoring contiguous run of non-conforming
components (Kadane), which finds a native title flanked by a roman author on
the left and the romanization on the right without needing a single changepoint.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sqlite3
import statistics

HERE = pathlib.Path(__file__).resolve().parent
ROWS = json.load(open(HERE / "loc_features.json"))

con = sqlite3.connect(HERE.parents[1] / "punjab.db")
con.text_factory = lambda b: b.decode("utf-8", "replace")
AUTH = {(q, str(r)): (a or "").strip()
        for q, r, a in con.execute("select quarter,reg,coalesce(author,'') from entries")}
for r in ROWS:
    r["author"] = AUTH.get((r["q"], str(r["reg"])), "?")

POS = [r for r in ROWS if r["lang"] != "English" and r["native"]]
NEG = [r for r in ROWS if r["lang"] == "English" and not r["native"]]
ANCH = [r for r in ROWS if r.get("bracket_x") and r["author"] == "" and r["lang"] != "English"]


def score_comps(r):
    base, top, xh = r["base"], r["top"], r["xh"]
    out = []
    for x0, x1, y0, y1 in r["comps"]:
        s = max(abs(y1 - base), 0.55 * abs(y0 - top)) / xh
        out.append((x0, x1, s))
    return out


def span(r, theta, lam, min_score, min_w):
    cs = score_comps(r)
    if len(cs) < 4:
        return None
    best = cur = 0.0
    bi = bj = ci = 0
    for i, (x0, x1, s) in enumerate(cs):
        v = 1.0 if s > theta else -lam
        if cur + v > v:
            cur += v
        else:
            cur, ci = v, i
        if cur > best:
            best, bi, bj = cur, ci, i
    if best < min_score:
        return None
    a, b = cs[bi][0], cs[bj][1]
    if (b - a) < min_w * r["xh"]:
        return None
    return a, b


def evaluate(theta, lam, min_score, min_w):
    tp = sum(span(r, theta, lam, min_score, min_w) is not None for r in POS)
    fp = sum(span(r, theta, lam, min_score, min_w) is not None for r in NEG)
    errs = []
    for r in ANCH:
        sp = span(r, theta, lam, min_score, min_w)
        if sp is not None:
            errs.append(abs(sp[1] - r["bracket_x"]) / r["xh"])
    return (100 * tp / len(POS), 100 * fp / len(NEG),
            statistics.median(errs) if errs else float("nan"), len(errs))


def main() -> int:
    print(f"POS {len(POS)}  NEG {len(NEG)}  anchored-title-first {len(ANCH)}")
    base_r = 100 * sum(r["bracket"] for r in POS) / len(POS)
    base_f = 100 * sum(r["bracket"] for r in NEG) / len(NEG)
    print(f"bracket baseline: recall {base_r:.1f}%  FP {base_f:.1f}%\n")

    grid = []
    for theta, lam, ms, mw in itertools.product(
            (0.12, 0.18, 0.25, 0.35), (0.4, 0.7, 1.0, 1.5),
            (1.5, 2.5, 3.5, 5.0), (0.5, 1.0)):
        rec, fp, err, n = evaluate(theta, lam, ms, mw)
        grid.append((rec, fp, err, n, theta, lam, ms, mw))

    print(f"{'FP ceiling':>10s} | {'recall':>7s} | {'edge err':>9s} | "
          f"{'theta':>5s} {'lam':>4s} {'minS':>5s} {'minW':>5s}")
    print("-" * 66)
    for ceil in (2, 5, 10, 15, 25):
        cand = [g for g in grid if g[1] <= ceil]
        if not cand:
            print(f"{ceil:9d}% |   none")
            continue
        rec, fp, err, n, theta, lam, ms, mw = max(cand, key=lambda g: g[0])
        print(f"{ceil:9d}% | {rec:6.1f}% | {err:8.2f}x | {theta:5.2f} {lam:4.1f} "
              f"{ms:5.1f} {mw:5.1f}   (actual FP {fp:.1f}%, n_edge {n})")
    print("\nedge err = |predicted right edge - bracket x| in x-heights, median,")
    print("measured on title-first entries where the bracket is known.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
