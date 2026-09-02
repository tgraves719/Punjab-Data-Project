"""E3 — can the document's own grammar tell us where an extraction is wrong?

The question is whether constraint violations predict transcription errors. If
they do, we get quality estimation on the ~40 quarters that will never have a
gold standard, which is the difference between monitoring the full 1867-1942 run
and hoping.

The test uses the 1910Q2 bake-off: three models extracted the same quarter that
we hold a validated in-session transcription of, so every candidate entry has a
known error label. Constraints are computed from each candidate alone, never
from gold.

Three questions, in increasing order of difficulty:

  Q1  Does the violation count rank the models the way measured accuracy does?
      (Quarter level. This is what model selection would use.)
  Q2  Do pages with more violations have more errors?
      (Page level. This is what routes a human's attention.)
  Q3  Does a violation on an entry predict an error on that entry?
      (Entry level. The hardest, and the one that would let us auto-triage.)

    python e3_constraint_qe.py
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from constraints import check_quarter  # noqa: E402

GOLD = ROOT / "pipeline" / "data" / "1910Q2" / "extractions"
BAKED = ROOT / "pipeline" / "data" / "1910Q2" / "_baked"
QUARTER_END = "1910-06-30"

# Fields scored for the error label. These are the register's own validation
# instruments — discrete, verifiable, and what the project's conclusions rest on.
#
# Deliberately excluded: price, publisher, title, edition, date, pp_verbatim.
# Comparing those across extraction runs measures transcription *convention*,
# not accuracy — "1st edition" vs "1st", "Re. 1, 8 annas (paper cover.)" vs
# "Re. 1, 8 annas (paper)", "(1327)" vs "(1327 Hijri)". A first version of this
# script scored them and reported a 28% error rate for the model the bake-off
# measured at reg recall 1.000; almost all of it was punctuation.
KEY_FIELDS = ["reg", "serial", "copies", "printer", "pcity"]
WIDE_FIELDS = KEY_FIELDS + ["author", "publisher", "pubcity", "topic"]

_COMBINING = dict.fromkeys(range(0x0300, 0x0370))


def norm(v) -> str:
    """Compare on substance, not on typographic convention.

    Folds the diacritics the catalog sets on place names (Qádián/Qadian),
    the thousands separators on counts (1,000/1000), trailing points, and case.
    """
    import unicodedata
    if v in (None, ""):
        return ""
    s = unicodedata.normalize("NFKD", str(v)).translate(_COMBINING)
    s = " ".join(s.split()).strip().rstrip(".").strip()
    if s.replace(",", "").isdigit():
        s = s.replace(",", "")
    return s.casefold()


def load(d: pathlib.Path) -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(d / "p*.json"))):
        try:
            out += json.load(open(f, encoding="utf-8"))
        except Exception as exc:
            print(f"  ! {f}: {exc}", file=sys.stderr)
    return out


def match(gold: list[dict], cand: list[dict]) -> dict[int, int | None]:
    """Map candidate index -> gold index.

    Joins on (printed_page, reg) first, then (printed_page, serial), then
    (printed_page, title). An entry that matches nothing is counted as an error:
    either its registration number was misread or the entry is spurious.
    """
    by_reg, by_serial, by_title = {}, {}, {}
    for j, g in enumerate(gold):
        p = g.get("printed_page")
        by_reg.setdefault((p, norm(g.get("reg"))), j)
        by_serial.setdefault((p, norm(g.get("serial"))), j)
        by_title.setdefault((p, norm(g.get("title")).lower()), j)

    out, used = {}, set()
    for i, c in enumerate(cand):
        p = c.get("printed_page")
        for table, key in ((by_reg, norm(c.get("reg"))),
                           (by_serial, norm(c.get("serial"))),
                           (by_title, norm(c.get("title")).lower())):
            j = table.get((p, key))
            if j is not None and j not in used:
                out[i], _ = j, used.add(j)
                break
        else:
            out[i] = None
    return out


def error_labels(gold, cand, pairs, fields) -> list[bool]:
    labels = []
    for i, c in enumerate(cand):
        j = pairs.get(i)
        if j is None:
            labels.append(True)
            continue
        g = gold[j]
        labels.append(any(norm(c.get(f)) != norm(g.get(f)) for f in fields))
    return labels


def rates(pred: list[bool], truth: list[bool]) -> dict:
    tp = sum(1 for p, t in zip(pred, truth) if p and t)
    fp = sum(1 for p, t in zip(pred, truth) if p and not t)
    fn = sum(1 for p, t in zip(pred, truth) if not p and t)
    tn = sum(1 for p, t in zip(pred, truth) if not p and not t)
    base = (tp + fn) / max(len(truth), 1)
    prec = tp / max(tp + fp, 1)
    return {"n": len(truth), "flagged": tp + fp, "errors": tp + fn,
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": prec, "recall": tp / max(tp + fn, 1),
            "base_rate": base, "lift": (prec / base) if base else float("nan")}


def spearman(x: list[float], y: list[float]) -> float:
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    if n < 3:
        return float("nan")
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baked", default=str(BAKED))
    ap.add_argument("--out", default="e3_results.json")
    args = ap.parse_args()

    gold = load(GOLD)
    gold_viol = check_quarter(gold, QUARTER_END)
    print(f"gold 1910Q2: {len(gold)} entries, {len(gold_viol)} violations "
          f"({sum(1 for v in gold_viol if v.severity == 'hard')} hard)\n")

    models = sorted(p for p in pathlib.Path(args.baked).iterdir()
                    if p.is_dir() and not p.name.startswith("_"))
    results = {}

    print("Q1 — quarter level: do violations rank the models like accuracy does?\n")
    print(f"{'model':22s} {'entries':>7s} {'hard':>6s} {'soft':>6s} "
          f"{'hard/100':>9s} | {'err(key)':>9s} {'err(wide)':>10s}")
    print("-" * 78)

    rows = []
    for m in models:
        cand = load(m)
        if not cand:
            continue
        viol = check_quarter(cand, QUARTER_END)
        pairs = match(gold, cand)
        err_key = error_labels(gold, cand, pairs, KEY_FIELDS)
        err_wide = error_labels(gold, cand, pairs, WIDE_FIELDS)
        hard = [v for v in viol if v.severity == "hard"]
        soft = [v for v in viol if v.severity == "soft"]
        row = {
            "model": m.name, "entries": len(cand),
            "hard": len(hard), "soft": len(soft),
            "hard_per_100": 100 * len(hard) / len(cand),
            "err_key": sum(err_key) / len(cand),
            "err_wide": sum(err_wide) / len(cand),
            "viol": viol, "cand": cand, "err_key_labels": err_key,
            "err_wide_labels": err_wide,
        }
        rows.append(row)
        print(f"{m.name:22s} {len(cand):7d} {len(hard):6d} {len(soft):6d} "
              f"{row['hard_per_100']:9.1f} | {100*row['err_key']:8.1f}% "
              f"{100*row['err_wide']:9.1f}%")

    if len(rows) >= 3:
        rho = spearman([r["hard_per_100"] for r in rows],
                       [r["err_key"] for r in rows])
        print(f"\n  Spearman(hard violations, key-field error rate) = {rho:+.2f} "
              f"over {len(rows)} models")

    # ---- Q2: page level ---------------------------------------------------
    print("\nQ2 — page level: do pages with more violations have more errors?\n")
    for r in rows:
        per_page_v = collections.Counter()
        per_page_e = collections.Counter()
        pages = set()
        for i, c in enumerate(r["cand"]):
            p = c.get("printed_page")
            pages.add(p)
            per_page_e[p] += int(r["err_key_labels"][i])
        for v in r["viol"]:
            if v.severity == "hard":
                per_page_v[v.printed_page] += 1
        pages = sorted(pages)
        rho = spearman([per_page_v[p] for p in pages], [per_page_e[p] for p in pages])
        flagged = [p for p in pages if per_page_v[p] > 0]
        err_on_flagged = sum(per_page_e[p] for p in flagged)
        err_total = sum(per_page_e.values())
        print(f"  {r['model']:22s} rho={rho:+.2f}   "
              f"{len(flagged):2d}/{len(pages)} pages flagged capture "
              f"{err_on_flagged}/{err_total} errors "
              f"({100*err_on_flagged/max(err_total,1):.0f}%)")
        r["page_rho"] = rho
        r["page_capture"] = err_on_flagged / max(err_total, 1)
        r["pages_flagged_frac"] = len(flagged) / max(len(pages), 1)

    # ---- Q3: entry level --------------------------------------------------
    print("\nQ3 — entry level: does a violation predict an error on that entry?\n")
    print(f"{'model':22s} {'pred':>16s} {'prec':>6s} {'recall':>7s} "
          f"{'base':>6s} {'lift':>6s}")
    print("-" * 68)
    for r in rows:
        hard_idx = {v.index for v in r["viol"] if v.severity == "hard"}
        any_idx = {v.index for v in r["viol"]}
        for name, idx in (("hard only", hard_idx), ("hard or soft", any_idx)):
            pred = [i in idx for i in range(len(r["cand"]))]
            st = rates(pred, r["err_key_labels"])
            print(f"{r['model']:22s} {name:>16s} {st['precision']:6.2f} "
                  f"{st['recall']:7.2f} {st['base_rate']:6.2f} {st['lift']:6.2f}")
            r.setdefault("entry", {})[name] = st

    out = {"quarter": "1910Q2", "gold_entries": len(gold),
           "gold_violations": len(gold_viol),
           "models": [{k: v for k, v in r.items()
                       if k not in ("viol", "cand", "err_key_labels", "err_wide_labels")}
                      for r in rows]}
    json.dump(out, open(pathlib.Path(__file__).resolve().parent / args.out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
