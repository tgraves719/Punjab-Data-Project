"""E5a — how good is the extractor's own uncertainty channel?

The pipeline's schema tells the extractor to flag uncertain readings
"aggressively", and it does: 789 of 4,502 entries carry a flag. Every
human-in-the-loop design in the agenda assumes those flags are worth following.
Nobody has checked.

Checking needs ground truth, and the 1910Q2 bake-off has it: three models
extracted the quarter we hold a validated transcription of, and each emitted its
own flags. So we can ask, without any human adjudication:

  Q1  Does a flag on an entry predict an error on that entry?
  Q2  Does a flag on a *field* predict an error in *that field*?
  Q3  Are flags and grammar constraints (E3) redundant or complementary?

What this cannot measure is whether a flag on the *golden* extraction marks a
real error, because there gold is the thing being judged. That needs a human
looking at page images, and is E5b.

    python e5_flag_channel.py
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "pipeline"))

import e3_constraint_qe as E3          # noqa: E402
from constraints import check_quarter  # noqa: E402


def flagged_fields(entry: dict) -> set[str]:
    return {str(f.get("field", "")).strip() for f in (entry.get("flags") or [])
            if str(f.get("field", "")).strip()}


def rates(pred, truth) -> dict:
    return E3.rates(list(pred), list(truth))


def show(name: str, st: dict) -> None:
    print(f"  {name:34s} prec {st['precision']:.2f}  recall {st['recall']:.2f}  "
          f"base {st['base_rate']:.2f}  lift {st['lift']:5.2f}  "
          f"(flagged {st['flagged']:3d}/{st['n']})")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="e5_results.json")
    args = ap.parse_args()

    gold = E3.load(E3.GOLD)
    results = {}

    for model in ("claude-opus-4-8", "claude-sonnet-5", "claude-haiku-4-5"):
        cand = E3.load(E3.BAKED / model)
        if not cand:
            continue
        pairs = E3.match(gold, cand)
        err = E3.error_labels(gold, cand, pairs, E3.KEY_FIELDS)
        viol = check_quarter(cand, E3.QUARTER_END)
        hard = {v.index for v in viol if v.severity == "hard"}

        has_flag = [bool(c.get("flags")) for c in cand]
        has_viol = [i in hard for i in range(len(cand))]
        either = [f or v for f, v in zip(has_flag, has_viol)]
        both = [f and v for f, v in zip(has_flag, has_viol)]

        print(f"\n=== {model} ===")
        print("Q1 — entry level: does a flag predict a key-field error?")
        st_flag = rates(has_flag, err)
        show("flag", st_flag)
        show("constraint violation (E3)", rates(has_viol, err))
        show("flag OR violation", rates(either, err))
        show("flag AND violation", rates(both, err))

        # Q2 — field level. Only fields both channels can speak about.
        print("Q2 — field level: does a flag on a field predict an error there?")
        per_field = {}
        for f in E3.KEY_FIELDS:
            p, t = [], []
            for i, c in enumerate(cand):
                j = pairs.get(i)
                if j is None:
                    continue                      # unmatched: no field truth
                p.append(f in flagged_fields(c))
                t.append(E3.norm(c.get(f)) != E3.norm(gold[j].get(f)))
            if any(p):
                st = rates(p, t)
                per_field[f] = st
                show(f"  flag on {f}", st)
            else:
                per_field[f] = None
                print(f"    flag on {f:22s} — never flagged")

        # Q3 — overlap
        nf, nv = sum(has_flag), sum(has_viol)
        nb = sum(both)
        print(f"Q3 — overlap: {nf} flagged, {nv} violations, {nb} both "
              f"(Jaccard {nb / max(nf + nv - nb, 1):.2f})")

        results[model] = {
            "n": len(cand), "errors": sum(err),
            "flag": st_flag, "flagged": nf, "violations": nv, "both": nb,
            "field": {k: v for k, v in per_field.items()},
        }

    # The golden extraction's own flags, for context (no truth available).
    gviol = check_quarter(gold, E3.QUARTER_END)
    gh = {v.index for v in gviol if v.severity == "hard"}
    gf = [i for i, g in enumerate(gold) if g.get("flags")]
    print(f"\ngold 1910Q2: {len(gf)} flagged entries, {len(gh)} hard violations, "
          f"{len(set(gf) & gh)} both — E5b adjudicates these against page images")

    json.dump(results, open(pathlib.Path(__file__).resolve().parent / args.out, "w"),
              indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
