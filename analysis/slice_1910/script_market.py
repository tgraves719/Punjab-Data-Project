"""S3 — Script/language market comparison for 1910 (PLAN.md §4).

Three views, coarse to controlled:
  1. Language market table — entries, registered copies, mean/median run,
     %free, %educational, per norm_lang (books only; periodicals separated).
  2. The controlled comparison — the Punjab Hindu Family Mutual Relief Fund
     issues its monthly circular in Urdu, Punjabi (Gurmukhi), and Hindi
     (Nagari): same text, same publisher, same day. Print runs and series
     volume numbers therefore isolate the script variable.
  3. Same-work-both-scripts exhibits pulled by known quarter/page/serial.

Evidentiary scope note (stated wherever these numbers are used): registered
print runs measure *supply decisions by publishers under a legal-deposit
regime*, not readership or literacy. The hierarchy claim is about where
publishers thought paying readers were.

Outputs (out/): market_by_language.csv, relief_fund_series.csv,
market_summary.md, chart_language_market.png, chart_relief_fund.png
"""
import csv, pathlib, re, sqlite3
from statistics import mean, median

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
DB = HERE.parent.parent / "punjab.db"


def copies_int(c):
    d = re.sub(r"[^\d]", "", c or "")
    return int(d) if d else 0


con = sqlite3.connect(DB)
rows = list(con.execute(
    "select norm_lang, copies, price, educ, periodical, title, quarter, printed_page, serial "
    "from entries where quarter like '1910%'"))

# --- 1. language market table (books only) ---
langs = {}
for lang, copies, price, educ, periodical, *_ in rows:
    if periodical == "Y":
        continue
    d = langs.setdefault(lang, {"n": 0, "runs": [], "free": 0, "educ": 0})
    d["n"] += 1
    c = copies_int(copies)
    if c:
        d["runs"].append(c)
    if "free" in (price or "").lower():
        d["free"] += 1
    if educ == "Y":
        d["educ"] += 1

table = []
for lang, d in sorted(langs.items(), key=lambda kv: -kv[1]["n"]):
    runs = d["runs"] or [0]
    table.append({
        "language": lang, "entries": d["n"], "copies": sum(runs),
        "mean_run": round(mean(runs)), "median_run": round(median(runs)),
        "pct_free": round(100 * d["free"] / d["n"]),
        "pct_educ": round(100 * d["educ"] / d["n"]),
    })

with open(OUT / "market_by_language.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(table[0]))
    w.writeheader()
    w.writerows(table)

# --- 2. Relief Fund controlled series ---
fund = list(con.execute(
    "select quarter, printed_page, serial, norm_lang, title, copies, reg from entries "
    "where title like '%Relief Fund%' or title like '%Sahayak Bhandar%' "
    "   or title like '%Sahaik Bhandar%' or title like '%Kutamb%' "
    "order by quarter, norm_lang"))
with open(OUT / "relief_fund_series.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh)
    w.writerow(["quarter", "page", "serial", "language", "title", "copies", "reg"])
    w.writerows(fund)

# --- 3. charts ---
top = [t for t in table if t["entries"] >= 15]
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
names = [t["language"].replace("Bilingual ", "Bil. ") for t in top]
ax[0].barh(names[::-1], [t["entries"] for t in top][::-1], color="#4d6d9a")
ax[0].set_title("Registered titles, 1910")
ax[1].barh(names[::-1], [t["copies"] / 1000 for t in top][::-1], color="#8a5a44")
ax[1].set_title("Registered copies (thousands), 1910")
for a in ax:
    a.tick_params(labelsize=9)
fig.suptitle("The 1910 Punjab print market by language (books, full year Q1–Q4)", fontsize=11)
fig.tight_layout()
fig.savefig(OUT / "chart_language_market.png", dpi=160)
plt.close(fig)

fund_q4 = [(r[3], copies_int(r[5])) for r in fund if r[0] == "1910Q4"]
if fund_q4:
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    labels = [f[0] for f in fund_q4]
    vals = [f[1] for f in fund_q4]
    bars = ax.bar(labels, vals, color=["#4d6d9a", "#8a5a44", "#6a8a5a"][:len(vals)])
    ax.bar_label(bars, fmt="{:,.0f}")
    ax.set_title("One text, three scripts: Relief Fund monthly circular,\n"
                 "same publisher, same day (Aug 1910, regs 1239–1241)", fontsize=10)
    ax.set_ylabel("copies")
    fig.tight_layout()
    fig.savefig(OUT / "chart_relief_fund.png", dpi=160)
    plt.close(fig)

# --- summary ---
md_rows = ["| Language | titles | copies | mean run | median | %free | %educ |",
           "|---|---|---|---|---|---|---|"]
for t in table[:14]:
    md_rows.append(f"| {t['language']} | {t['entries']} | {t['copies']:,} | "
                   f"{t['mean_run']:,} | {t['median_run']:,} | {t['pct_free']} | {t['pct_educ']} |")

fund_rows = ["| Quarter | Language | Copies | Reg | Title |", "|---|---|---|---|---|"]
for q, pg, s, lang, title, copies, reg in fund:
    fund_rows.append(f"| {q} | {lang} | {copies} | {reg} | {title[:60]} |")

md = f"""# 1910 script-market comparison — build summary

Books only (periodicals excluded; 74 periodical issues tracked separately).
Scope note: registered print runs measure publisher supply decisions under the
1867 Act's legal-deposit regime — not readership, not literacy.

## Language market (top rows; full table in market_by_language.csv)
{chr(10).join(md_rows)}

## Controlled comparison: the Relief Fund circular
Same text, same publisher (Secretary, Punjab Hindu Family Mutual Relief Fund,
Lahore), same registration day, three scripts. The Urdu series is at Volume XV
while Hindi/Punjabi are at Volume VIII — the fund ran Urdu-only for its first
seven years.
{chr(10).join(fund_rows)}

Charts: chart_language_market.png, chart_relief_fund.png
"""
(OUT / "market_summary.md").write_text(md, encoding="utf-8")
print(md)
con.close()
