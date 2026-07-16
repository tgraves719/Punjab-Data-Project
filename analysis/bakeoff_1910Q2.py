"""Score the 1910Q2 model bake-off against the golden extractions.

The golden files (pipeline/data/1910Q2/extractions/) are the known-good in-session
transcription. Each candidate model writes to pipeline/data/1910Q2/_baked/<model>/
(via `extract_api.py --out ...`). This script diffs each candidate against gold and
prints an accuracy-per-dollar table so the model choice is empirical, not a guess.

Join key is `reg` (the registration number). reg is annual-unique and is NOT one of
the fields we then score for accuracy — so reg fidelity shows up as recall/precision
(did the model read the number correctly at all), and the other fields are scored only
on entries whose reg matched. An entry whose reg was misread counts as a reg miss; if
its title still matches a gold entry on the same page it's recovered as a secondary
match so its other fields still contribute (and its reg is marked wrong).

Cost uses raw token usage from each dir's _usage.json, priced at Batch API rates
(50% of standard). Sonnet 5 has lower intro input/output pricing through 2026-08-31;
we price at STANDARD to stay conservative — real spend will be lower until then.

Usage:  python bakeoff_1910Q2.py
        python bakeoff_1910Q2.py --baked /abs/path/to/_baked
This writes/reads nothing in git-tracked locations; keep _baked/ out of commits.
"""
import json, glob, pathlib, sys, difflib
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
GOLD = HERE.parent / "pipeline" / "data" / "1910Q2" / "extractions"
BAKED = HERE.parent / "pipeline" / "data" / "1910Q2" / "_baked"

# Standard per-1M-token prices (USD). Batch API bills at half these.
PRICES = {
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-sonnet-5":  (3.0, 15.0),   # intro $2/$10 through 2026-08-31; priced at standard here
    "claude-opus-4-8":  (5.0, 25.0),
    "claude-fable-5":   (10.0, 50.0),
}

# Substantive verbatim fields scored on reg-matched entries (reg/serial/copies/
# title_native are reported as their own headline metrics, not folded in here).
FIELDS = ["printer", "pcity", "author", "title", "publisher", "pubcity",
          "date", "price", "edition", "gloss", "pp_verbatim", "section", "topic"]


def norm(v):
    return " ".join(str(v).split()).strip() if v not in (None, "") else ""


def load_entries(d):
    """All entries from a dir of pNNN.json files, flattened."""
    out = []
    for f in sorted(glob.glob(str(pathlib.Path(d) / "p*.json"))):
        try:
            rows = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"  ! could not parse {f}: {e}", file=sys.stderr)
            continue
        for r in rows:
            out.append(r)
    return out


def by_reg(entries):
    d = {}
    for e in entries:
        r = norm(e.get("reg"))
        if r:
            d.setdefault(r, e)  # first wins on the rare duplicate reg
    return d


def by_page(entries):
    d = defaultdict(list)
    for e in entries:
        d[e.get("printed_page")].append(e)
    return d


def score(gold, cand):
    g_reg, c_reg = by_reg(gold), by_reg(cand)
    g_regs, c_regs = set(g_reg), set(c_reg)
    matched = g_regs & c_regs

    reg_recall = len(matched) / len(g_regs) if g_regs else 0.0
    reg_precision = len(matched) / len(c_regs) if c_regs else 0.0

    # headline field tallies over reg-matched entries
    serial_ok = copies_ok = tn_ok = 0
    field_ok = defaultdict(int)
    for r in matched:
        g, c = g_reg[r], c_reg[r]
        serial_ok += norm(g.get("serial")) == norm(c.get("serial"))
        copies_ok += norm(g.get("copies")) == norm(c.get("copies"))
        tn_ok += bool(g.get("title_native")) == bool(c.get("title_native"))
        for f in FIELDS:
            field_ok[f] += norm(g.get(f)) == norm(c.get(f))

    # secondary recovery: gold entries whose reg was missed but whose title still
    # matches a candidate entry on the same page (reg misread, entry present)
    c_page = by_page(cand)
    recovered = 0
    for r in g_regs - matched:
        g = g_reg[r]
        gt = norm(g.get("title"))
        best = 0.0
        for c in c_page.get(g.get("printed_page"), []):
            best = max(best, difflib.SequenceMatcher(None, gt, norm(c.get("title"))).ratio())
        if best >= 0.85:
            recovered += 1

    n = len(matched) or 1
    other = sum(field_ok.values()) / (len(FIELDS) * n)
    serial_acc, copies_acc, tn_acc = serial_ok / n, copies_ok / n, tn_ok / n

    # entry-count fidelity per page (catches whole-section drops/dupes)
    g_pages, c_pages = by_page(gold), by_page(cand)
    page_count_match = sum(len(g_pages[p]) == len(c_pages.get(p, [])) for p in g_pages)
    page_count_rate = page_count_match / len(g_pages) if g_pages else 0.0

    weighted = (0.35 * reg_recall + 0.15 * serial_acc + 0.15 * copies_acc
                + 0.15 * tn_acc + 0.20 * other)

    return {
        "gold_entries": len(g_regs), "cand_entries": len(c_regs), "matched": len(matched),
        "reg_recall": reg_recall, "reg_precision": reg_precision,
        "recovered_title": recovered, "page_count_rate": page_count_rate,
        "serial_acc": serial_acc, "copies_acc": copies_acc, "title_native_acc": tn_acc,
        "other_field_acc": other, "weighted": weighted,
        "field_ok": {f: field_ok[f] / n for f in FIELDS},
    }


def cost(usage_path):
    if not usage_path.exists():
        return None, None
    u = json.load(open(usage_path))
    model = u.get("model", "")
    rin, rout = PRICES.get(model, (0, 0))
    inp = u.get("input_tokens", 0)
    out = u.get("output_tokens", 0)
    cw = u.get("cache_creation_input_tokens", 0)
    cr = u.get("cache_read_input_tokens", 0)
    factor = 0.5 if u.get("batch", True) else 1.0
    dollars = factor * (inp * rin + cw * rin * 1.25 + cr * rin * 0.1 + out * rout) / 1e6
    return model, dollars


def main(baked):
    gold = load_entries(GOLD)
    print(f"gold: {len(gold)} entries across {len(by_page(gold))} pages "
          f"({len(by_reg(gold))} unique reg)\n")

    dirs = sorted(p for p in pathlib.Path(baked).glob("*") if p.is_dir())
    if not dirs:
        print(f"no model dirs under {baked} — run extract_api.py --out {baked}/<model> first")
        return

    rows = []
    for d in dirs:
        cand = load_entries(d)
        if not cand:
            print(f"[{d.name}] no entries; skipping")
            continue
        s = score(gold, cand)
        model, dollars = cost(d / "_usage.json")
        apd = (s["weighted"] / dollars) if dollars else None
        rows.append((d.name, model, s, dollars, apd))

    # headline table
    hdr = f"{'dir':<14}{'weighted':>9}{'reg_rec':>9}{'serial':>8}{'copies':>8}{'nativ':>7}{'other':>7}{'$batch':>9}{'acc/$':>9}"
    print(hdr)
    print("-" * len(hdr))
    for name, model, s, dollars, apd in sorted(rows, key=lambda r: -(r[4] or 0)):
        d_str = f"{dollars:.2f}" if dollars is not None else "  n/a"
        apd_str = f"{apd:.2f}" if apd is not None else "  n/a"
        print(f"{name:<14}{s['weighted']:>9.3f}{s['reg_recall']:>9.3f}"
              f"{s['serial_acc']:>8.3f}{s['copies_acc']:>8.3f}{s['title_native_acc']:>7.3f}"
              f"{s['other_field_acc']:>7.3f}{d_str:>9}{apd_str:>9}")

    # detail per model
    for name, model, s, dollars, apd in rows:
        print(f"\n=== {name} ({model or '?'}) ===")
        print(f"  entries gold={s['gold_entries']} cand={s['cand_entries']} "
              f"matched={s['matched']} recovered-by-title={s['recovered_title']}")
        print(f"  reg recall={s['reg_recall']:.3f} precision={s['reg_precision']:.3f} "
              f"page-count match={s['page_count_rate']:.3f}")
        worst = sorted(s["field_ok"].items(), key=lambda kv: kv[1])[:5]
        print("  weakest fields: " + ", ".join(f"{f}={a:.2f}" for f, a in worst))

    print("\nPick by acc/$ unless reg_recall on the leader is materially worse than a "
          "pricier model — reg/serial/copies are the validation instruments; a cheap "
          "model that fumbles the numbers is a false economy.")


if __name__ == "__main__":
    baked = BAKED
    if "--baked" in sys.argv:
        baked = pathlib.Path(sys.argv[sys.argv.index("--baked") + 1])
    main(baked)
