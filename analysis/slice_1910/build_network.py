"""S2 — Printer-publisher network for 1910 (PLAN.md §4).

Builds a bipartite network (norm_printer <-> publisher entity) from punjab.db,
weighted by entry count and registered copies. Self-publication ("Author",
"The compiler", etc.) is excluded from edges and reported as its own statistic —
it is a structural feature of this print economy, not noise.

Outputs (out/):
  network_nodes.csv   Id, Label, Type, entries, copies, degree, wdegree  (Gephi-ready)
  network_edges.csv   Source, Target, Weight (=entries), copies          (Gephi-ready)
  authors_top.csv     author, entries, copies, languages
  network_summary.md  headline stats + top tables

Layer note: uses NORMALIZED fields (norm_printer); publisher strings get one
additional deterministic trim (trailing book-seller descriptors) documented here
because aliases.json does not yet carry a publisher entity table (post-slice task).
"""
import csv, pathlib, re, sqlite3
from collections import defaultdict

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
DB = HERE.parent.parent / "punjab.db"

SELF_RE = re.compile(r"^(the\s+)?(author|compiler|translator|editor|artist)s?\b", re.I)

# Publisher entity aliases (slice-local; candidates for aliases.json "publisher"
# once a full publisher entity table exists — see DECISIONS.md D-011). Applied
# AFTER descriptor trimming. Keys are observed variants, values canonical.
PUB_ALIASES = {
    'The "Civil and Military Gazette" Press': "Civil and Military Gazette Press",
    "The 'Civil and Military Gazette' Press": "Civil and Military Gazette Press",
    "The Bharat Literature Company, Limited": "Bharat Literature Company, Limited",
    "Messrs. Gulab Singh and Sons": "Gulab Singh and Sons",
    "M. Gulab Singh and Sons": "Gulab Singh and Sons",
    "Bhai Daya Singh and Sons": "B. Daya Singh and Sons",
    "B. Daya Singh and Son": "B. Daya Singh and Sons",
    "Lala Pokar Das": "Lala Pokhar Das",
    "The Vakil Trading Co., Ltd.": "The Vakil Trading Company, Limited",
}


def copies_int(c):
    digits = re.sub(r"[^\d]", "", c or "")
    return int(digits) if digits else 0


def publisher_entity(p):
    """Trim descriptors; return None for self-publication; apply PUB_ALIASES."""
    p = (p or "").strip().replace("“", '"').replace("”", '"')
    if not p or SELF_RE.match(p):
        return None
    p = re.sub(r",?\s*Book-?sellers?\.?$", "", p, flags=re.I).strip().rstrip(",")
    return PUB_ALIASES.get(p, p) or None


def main():
    con = sqlite3.connect(DB)
    rows = list(con.execute(
        "select norm_printer, norm_publisher, author, norm_lang, copies "
        "from entries where quarter like '1910%'"))
    con.close()
    run(rows)


def run(rows):
    edges = defaultdict(lambda: [0, 0])       # (printer, publisher) -> [entries, copies]
    nodes = defaultdict(lambda: [0, 0])           # (id, type) -> [entries, copies]
    authors = defaultdict(lambda: [0, 0, set()])  # author -> [entries, copies, langs]
    n_self, n_nopub, n_total = 0, 0, len(rows)

    for printer, publisher, author, lang, copies in rows:
        c = copies_int(copies)
        pub = publisher_entity(publisher)
        if printer:
            nodes[(printer, "printer")][0] += 1
            nodes[(printer, "printer")][1] += c
        if pub is None:
            if SELF_RE.match((publisher or "").strip()):
                n_self += 1
            else:
                n_nopub += 1
        else:
            nodes[(pub, "publisher")][0] += 1
            nodes[(pub, "publisher")][1] += c
            if printer:
                edges[(printer, pub)][0] += 1
                edges[(printer, pub)][1] += c
        if author and author.strip():
            a = authors[author.strip()]
            a[0] += 1
            a[1] += c
            a[2].add(lang)

    degree = defaultdict(int)
    wdegree = defaultdict(int)
    for (src, tgt), (w, c) in edges.items():
        degree[(src, "printer")] += 1
        degree[(tgt, "publisher")] += 1
        wdegree[(src, "printer")] += w
        wdegree[(tgt, "publisher")] += w

    with open(OUT / "network_nodes.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["Id", "Label", "Type", "entries", "copies", "degree", "wdegree"])
        for (name, typ), (n, c) in sorted(nodes.items(), key=lambda kv: -kv[1][0]):
            w.writerow([f"{typ}:{name}", name, typ, n, c, degree[(name, typ)], wdegree[(name, typ)]])

    with open(OUT / "network_edges.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["Source", "Target", "Type", "Weight", "copies"])
        for (src, tgt), (n, c) in sorted(edges.items(), key=lambda kv: -kv[1][0]):
            w.writerow([f"printer:{src}", f"publisher:{tgt}", "Undirected", n, c])

    with open(OUT / "authors_top.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["author", "entries", "copies", "languages"])
        for a, (n, c, langs) in sorted(authors.items(), key=lambda kv: -kv[1][0]):
            w.writerow([a, n, c, "; ".join(sorted(langs))])

    printers = [(k[0], v, degree[k], wdegree[k]) for k, v in nodes.items() if k[1] == "printer"]
    publishers = [(k[0], v, degree[k], wdegree[k]) for k, v in nodes.items() if k[1] == "publisher"]

    def table(rows, n=15):
        lines = ["| Name | entries | copies | partners (degree) |", "|---|---|---|---|"]
        for name, (ent, cop), deg, _ in sorted(rows, key=lambda r: -r[1][0])[:n]:
            lines.append(f"| {name} | {ent} | {cop:,} | {deg} |")
        return "\n".join(lines)

    md = f"""# 1910 printer-publisher network — build summary

Source: punjab.db, full year 1910 (Q1-Q4, {n_total} entries). Normalized layer.
Method: bipartite printer<->publisher edges weighted by entries and copies;
self-publication excluded from edges, reported below. See script docstring.

## Headline structure

- Printer nodes: {len(printers)}; publisher nodes: {len(publishers)}; edges: {len(edges)}
- **Self-published entries: {n_self} of {n_total} ({100*n_self/n_total:.0f}%)** — author = publisher;
  the modal "firm" in this economy is a person paying a press.
- Entries with no publisher recorded: {n_nopub}
- Multi-partner printers (degree >= 5): {sum(1 for p in printers if p[2] >= 5)}
- Single-partner publishers: {sum(1 for p in publishers if p[2] == 1)} of {len(publishers)}
  (most publishers use exactly one press; presses are the hubs)

## Top printers
{table(printers)}

## Top publishers (non-self)
{table(publishers)}

Files: network_nodes.csv, network_edges.csv (Gephi-importable), authors_top.csv.
"""
    (OUT / "network_summary.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
