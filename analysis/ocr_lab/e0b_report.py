"""E0b reporting — distributions, not medians, and the below-floor fraction.

The number that decides architecture is not the median clearance. It is the
share of title crops whose i'jam clearance lands below the 2 px sampling floor
at a given render resolution, because those crops are unrecoverable regardless
of the model. Reported per script, with n and IQR so the reader can see how
thin the tail languages are.
"""
from __future__ import annotations
import json, pathlib, statistics, collections

HERE = pathlib.Path(__file__).resolve().parent
DPIS = (140, 306, 600)
FLOOR = 2.0
SRC_DPI = 306.0

rows = json.load(open(HERE / "e0b_results.json"))
rows = [r for r in rows if r["n_dots"] >= 1 and r["dot_gap"] > 0]

def mil(px): return 1000.0 * px / SRC_DPI
def q(v, p): 
    v = sorted(v); i = (len(v)-1)*p; lo, hi = int(i), min(int(i)+1, len(v)-1)
    return v[lo] + (v[hi]-v[lo])*(i-lo)

def block(title, groups):
    print(f"\n{title}")
    print(f"{'group':30s} {'n':>4s} | {'clearance mil (IQR)':>26s} | {'dot mil':>8s} | "
          f"{'% below 2px floor':>26s} | {'dot':>5s}")
    print(f"{'':30s} {'':>4s} | {'':>26s} | {'':>8s} | "
          f"{'@140':>7s} {'@306':>8s} {'@600':>8s} | {'share':>5s}")
    print("-"*112)
    for name, sub in groups:
        if len(sub) < 3: 
            print(f"{name:30s} {len(sub):4d} |  (n too small)"); continue
        gaps = [mil(r["dot_gap"]) for r in sub]
        dots = [mil(r["dot_h"]) for r in sub]
        med, lo, hi = statistics.median(gaps), q(gaps,.25), q(gaps,.75)
        share = statistics.median([r["n_dots"]/max(1,(r["n_dots"]+r["n_bodies"])) for r in sub])
        pct = []
        for d in DPIS:
            below = sum(1 for r in sub if min(mil(r["dot_gap"]), mil(r["dot_h"])) * d/1000.0 < FLOOR)
            pct.append(100.0*below/len(sub))
        print(f"{name:30s} {len(sub):4d} | {med:8.1f}  ({lo:5.1f}-{hi:5.1f}) | {statistics.median(dots):8.1f} | "
              f"{pct[0]:6.0f}% {pct[1]:7.0f}% {pct[2]:7.0f}% | {share:5.2f}")

by = collections.defaultdict(list)
for r in rows: by[r["script"]].append(r)
block(f"BY SCRIPT   (n={len(rows)} native-title crops, all twelve quarters)",
      sorted(by.items(), key=lambda kv: -len(kv[1])))

main = [s for s,v in by.items() if len(v) >= 20]
for s in sorted(main):
    sub = by[s]
    g = collections.defaultdict(list)
    for r in sub:
        g["litho" if "lith" in (r["method"] or "").lower() else "type/other"].append(r)
    if len(g) > 1: block(f"  {s} — by print method", sorted(g.items()))

g = collections.defaultdict(list)
for r in rows: g[r["quarter"][:4]].append(r)
block("BY YEAR (all scripts pooled — drift check, not a trend claim)", sorted(g.items()))

print(f"\nSampling floor = {FLOOR} px on the smaller of (dot height, dot-to-body clearance).")
print("'dot share' = median fraction of components that are satellite marks — a proxy")
print("for how much letter identity the dots carry in that script.")
