"""Merge page extractions -> resolved entries CSV + SQLite (three-layer model).

Verbatim fields pass through untouched; normalized fields (norm_*) are derived
here via aliases.json and deterministic rules. Ditto/section carry-over across
page boundaries is resolved in page order.
"""
import csv, json, pathlib, re, sqlite3, sys, unicodedata

FIELDS = ["quarter", "pdf_page", "printed_page", "section", "lang", "char", "topic",
          "serial", "reg", "copies", "printer_verbatim", "printer", "pcity",
          "author", "title", "title_native", "gloss", "pp_verbatim", "publisher",
          "pubcity", "date", "price", "edition", "format", "method", "educ",
          "copyright", "notes", "marks"]
NORM = ["norm_lang", "periodical", "norm_printer", "norm_pcity", "norm_publisher",
        "norm_pubcity", "pp_sum", "flags_json"]


def fold(s):
    """Deterministic text fold: strip accents (NFKD), collapse whitespace."""
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


def norm_city(v, aliases):
    """City normalization: alias on raw, then fold, drop trailing 'city',
    canonical-case 'Cantonment', alias again on the result (rules per D-008)."""
    if v in aliases:
        return aliases[v]
    c = fold(v)
    c = re.sub(r"\s+city$", "", c, flags=re.I)
    c = re.sub(r"\s+cantonment$", " Cantonment", c, flags=re.I)
    return aliases.get(c, c)


def norm_name(v, aliases):
    """Printer/publisher normalization: alias on raw, then folded form."""
    if v in aliases:
        return aliases[v]
    n = fold(v)
    return aliases.get(n, n)


def pp_sum(v):
    """Sum a verbatim pagination string: '127, 80 and 4' -> 211; ranges count pages."""
    if not v:
        return None
    total, found = 0, False
    for part in re.split(r"[,;]| and ", str(v)):
        part = part.strip()
        rng = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", part)
        if rng:
            total += abs(int(rng.group(2)) - int(rng.group(1))) + 1
            found = True
        elif re.fullmatch(r"\d+", part):
            total += int(part)
            found = True
    return total if found else None


def main(manifest_path):
    m = json.load(open(manifest_path))
    data = pathlib.Path(m["data_dir"])
    here = pathlib.Path(__file__).parent
    aliases = json.load(open(here / "aliases.json", encoding="utf-8"))

    entries = []
    ctx = {"section": "", "lang": "", "char": "", "topic": "", "printer": "", "pcity": ""}
    for f in sorted((data / "extractions").glob("p*.json")):
        for e in json.load(open(f, encoding="utf-8")):
            # section carry-over for continuation pages
            if not e.get("lang") and e.get("section", "").upper() in ("", "CONTINUATION"):
                e["section"], e["lang"], e["char"], e["topic"] = ctx["section"], ctx["lang"], ctx["char"], ctx["topic"]
            ctx.update({"section": e.get("section", ""), "lang": e.get("lang", ""),
                        "char": e.get("char", ""), "topic": e.get("topic", "")})
            # ditto resolution across entries/pages
            pv = str(e.get("printer_verbatim", e.get("printer", "")))
            if re.fullmatch(r"\s*ditto\.?\s*", pv, re.I) or re.search(r"\(ditto\)", str(e.get("printer", "")), re.I):
                e["printer"], e["pcity"] = ctx["printer"], ctx["pcity"]
            e["printer"] = re.sub(r"\s*\(Ditto\)\s*", "", str(e.get("printer", ""))).strip()
            ctx.update({"printer": e.get("printer", ""), "pcity": e.get("pcity", "")})
            entries.append(e)

    rows = []
    for e in entries:
        r = {k: e.get(k, "") for k in FIELDS}
        r["norm_lang"] = aliases["lang"].get(r["lang"], r["lang"])
        r["periodical"] = "Y" if (str(r["section"]).upper().startswith("PERIODICALS")
                                  or str(r["lang"]).startswith("Periodicals")) else ""
        r["norm_printer"] = norm_name(r["printer"], aliases["printer"])
        r["norm_pcity"] = norm_city(r["pcity"], aliases["city"])
        r["norm_publisher"] = norm_name(r["publisher"], aliases["publisher"])
        r["norm_pubcity"] = norm_city(r["pubcity"], aliases["city"])
        r["pp_sum"] = pp_sum(e.get("pp_verbatim"))
        r["flags_json"] = json.dumps(e.get("flags", []), ensure_ascii=False)
        rows.append(r)
    rows.sort(key=lambda r: (int(r["printed_page"]), FIELDS.index("serial") * 0 + int(r["serial"] or 0)))

    out = data / "out"
    out.mkdir(exist_ok=True)
    with open(out / "entries.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS + NORM)
        w.writeheader()
        w.writerows(rows)

    db = sqlite3.connect(here.parent / "punjab.db")
    cols = ", ".join(f'"{c}" TEXT' for c in FIELDS + NORM)
    db.execute(f'CREATE TABLE IF NOT EXISTS entries ({cols})')
    db.execute('DELETE FROM entries WHERE quarter = ?', (m["quarter"],))
    db.executemany(
        f'INSERT INTO entries VALUES ({",".join("?" * len(FIELDS + NORM))})',
        [[str(r[c]) if r[c] is not None else "" for c in FIELDS + NORM] for r in rows])
    db.commit()
    print(f"{len(rows)} entries -> {out / 'entries.csv'} and punjab.db [{m['quarter']}]")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "manifest_1910Q2.json")
