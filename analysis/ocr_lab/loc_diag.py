"""Diagnose localization recall: why pages drop, and why brackets are missed.

Instruments the two compounding losses measured in E0b:
  (1) 33% of pages dropped on geometry failure or entry-count mismatch;
  (2) on surviving pages, ~1.4 native crops per ~8 entries.

Reports the *reason* in each case rather than the rate, so the fix is aimed.
"""
from __future__ import annotations
import json, pathlib, sqlite3, sys, collections, time
import numpy as np
from scipy import ndimage

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import crops  # noqa: E402

PIPELINE, DB = ROOT / "pipeline", ROOT / "punjab.db"
DPI = 306

def bracket_reject_reason(page, e):
    """Re-run _find_bracket's tests, returning the first that rejects."""
    c2a, c2b = page.geom.col2
    y0, y1 = e.line_top, e.line_bottom + 1
    if y1 - y0 < 8: return "line_too_short"
    band = page.ink[y0:y1, c2a:c2b]
    lbl, n = ndimage.label(band)
    if n == 0: return "no_ink"
    comps = []
    for sl_y, sl_x in ndimage.find_objects(lbl):
        h, w = sl_y.stop - sl_y.start, sl_x.stop - sl_x.start
        if h < 3 or w < 2: continue
        comps.append((sl_x.start, sl_x.stop, sl_y, sl_x))
    if len(comps) < 4: return "too_few_components"
    comps.sort()
    lh = y1 - y0
    reasons = collections.Counter()
    prev_right = 0
    for x_start, x_stop, sl_y, sl_x in comps:
        gap = x_start - prev_right
        prev_right = max(prev_right, x_stop)
        sub = band[sl_y, sl_x]
        h, w = sub.shape
        if not (0.55*lh <= h <= 1.15*lh): reasons["height"] += 1; continue
        if not (0.18*lh <= w <= 0.40*lh): reasons["width"] += 1; continue
        if sub[:,0].mean() < 0.75 or sub[:,-1].mean() > 0.5: reasons["left_edge"] += 1; continue
        k = max(1, h//5)
        top, bot = sub[:k].sum(axis=1).mean(), sub[-k:].sum(axis=1).mean()
        mid = sub[k:-k].sum(axis=1).mean() if h > 2*k else top
        if mid <= 0 or max(top,bot) < 1.3*mid: reasons["serif"] += 1; continue
        if gap < 0.30*lh: reasons["no_space_before"] += 1; continue
        return None                      # would have been found
    if not reasons: return "no_candidate"
    return "last:" + reasons.most_common(1)[0][0]

def main():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    quarters = [r[0] for r in con.execute("select distinct quarter from entries order by 1")]
    page_fail = collections.Counter(); count_delta = collections.Counter()
    br = collections.Counter(); lh_stats = []
    n_pages = n_entries = 0
    t0 = time.time()
    for q in quarters:
        man = json.load(open(PIPELINE / f"manifest_{q}.json"))
        pdf, (lo, hi), off = man["volume_pdf"], man["pdf_pages"], man["printed_page_offset"]
        pages = list(range(lo, hi+1))
        calib = crops.Page.calibrate_quarter(pdf, pages, DPI)
        for pdf_page in pages[::5]:                       # 20% sample, all quarters
            printed = pdf_page + off
            want = [dict(r) for r in con.execute(
                "select reg,serial,norm_lang,title_native from entries where quarter=? and printed_page=?",
                (q, printed))]
            if not want: continue
            try:
                pg = crops.Page.render(pdf, pdf_page, DPI, calib); found = pg.entries()
            except Exception as exc:
                page_fail[type(exc).__name__ + ": " + str(exc)[:44]] += 1; continue
            n_pages += 1
            d = len(found) - len(want)
            count_delta[d] += 1
            if d != 0: continue
            for e, rec in zip(found, want):
                n_entries += 1
                lh_stats.append(e.line_bottom - e.line_top)
                native_expected = str(rec["title_native"]) == "True"
                if e.bracket_x is not None:
                    br[("hit", native_expected)] += 1
                else:
                    br[(bracket_reject_reason(pg, e), native_expected)] += 1
        print(f"  {q} done [{time.time()-t0:.0f}s]", flush=True)

    print(f"\nSAMPLE: {n_pages} pages passing geometry, {n_entries} entries on count-matched pages")
    print("\nPAGE-LEVEL: geometry exceptions")
    for k, v in page_fail.most_common(8): print(f"  {v:4d}  {k}")
    print("\nPAGE-LEVEL: detected minus register entry count")
    for d in sorted(count_delta): print(f"  {d:+3d}: {count_delta[d]:4d} pages")
    tot = sum(count_delta.values())
    print(f"  exact match: {count_delta[0]}/{tot} = {100*count_delta[0]/max(tot,1):.0f}%")
    print("\nENTRY-LEVEL: bracket outcome, split by whether register says a native title exists")
    agg = collections.defaultdict(lambda: [0,0])
    for (reason, nat), v in br.items(): agg[reason][0 if nat else 1] += v
    print(f"  {'outcome':26s} {'native=True':>12s} {'native=False':>13s}")
    for reason, (a,b) in sorted(agg.items(), key=lambda kv: -sum(kv[1])):
        print(f"  {reason:26s} {a:12d} {b:13d}")
    if lh_stats:
        import statistics
        print(f"\n  first-line height px: median {statistics.median(lh_stats):.0f} "
              f"min {min(lh_stats)} max {max(lh_stats)}")
    json.dump({"page_fail": dict(page_fail), "count_delta": {str(k):v for k,v in count_delta.items()},
               "bracket": {f"{k[0]}|{k[1]}": v for k,v in br.items()}},
              open(HERE/"loc_diag.json","w"), indent=1)
    return 0

if __name__ == "__main__":
    sys.exit(main())
