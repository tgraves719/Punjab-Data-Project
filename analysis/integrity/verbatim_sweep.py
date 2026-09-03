"""Sweep for breaches of the verbatim layer's guarantee.

D-019(e) recorded one case -- 1910Q2 p20 reg 504, where the page prints
'Stara-i-Hiud Press' and the stored value had been silently normalised to
'Stara-i-Hind Press' -- and asked for a sweep. This is that sweep, kept
runnable so it can be repeated after every year is ingested.

Method: the extractor's own flags are the witness. Where a flag quotes what the
page prints ("printed 'X'", "page reads 'X'"), that quotation is compared with
the value actually stored for the same field. A mismatch means the record
disagrees with the extractor's own reading of the page.

Only fields the schema declares verbatim can breach. `copies` (digits only),
`date` (ISO-ish), `serial`, `edition` and `method` are normalised BY SPEC, so a
mismatch there is the schema working, not failing -- they are reported
separately rather than counted.

Usage:  python analysis/integrity/verbatim_sweep.py [path/to/punjab.db]
"""
import json, re, sqlite3, sys, unicodedata
from collections import Counter

# Field -> columns holding its stored value, per pipeline/schema.md.
VERBATIM = {
    "printer": ["printer_verbatim", "printer"], "printer_verbatim": ["printer_verbatim"],
    "author": ["author"], "publisher": ["publisher"], "pcity": ["pcity"],
    "pubcity": ["pubcity"], "price": ["price"], "gloss": ["gloss"],
    "notes": ["notes"], "section": ["section"], "copyright": ["copyright"],
    "pp": ["pp_verbatim"], "title": ["title"],
}
TYPED = {  # normalised by specification -- divergence here is not a breach
    "copies": ["copies"], "date": ["date"], "serial": ["serial"], "reg": ["reg"],
    "edition": ["edition"], "method": ["method"], "format": ["format"],
    "lang": ["lang"], "char": ["char"],
}
Q = "['\u2018\u2019\"\u201c\u201d]"
SOURCE_READING = re.compile(
    r"(?:printed|prints|page (?:reads|shows|has|prints)|reads|set as|appears as"
    r"|source (?:reads|has)|shows)\s*(?:as\s*)?" + Q + r"([^'\u2018\u2019\"\u201c\u201d]{2,60})" + Q,
    re.I)


def fold(s):
    """Compare on letters and digits only, accents folded."""
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def sweep(db):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "select * from entries where flags_json is not null "
        "and flags_json not in ('', '[]', 'null')").fetchall()
    breaches, typed, quotes = [], [], 0
    for r in rows:
        try:
            flags = json.loads(r["flags_json"])
        except Exception:
            continue
        for f in flags if isinstance(flags, list) else []:
            if not isinstance(f, dict):
                continue
            field = (f.get("field") or "").strip()
            cols = VERBATIM.get(field) or TYPED.get(field)
            if not cols:
                continue
            for m in SOURCE_READING.finditer(f.get("issue") or ""):
                quotes += 1
                page = m.group(1).strip()
                stored = [r[c] for c in cols if c in r.keys() and r[c] not in (None, "")]
                fp = fold(page)
                if not fp:
                    continue
                # The page reading should be recoverable from the stored value.
                if any(fp in fold(v) or fold(v) in fp for v in stored):
                    continue
                hit = {"quarter": r["quarter"], "printed_page": r["printed_page"],
                       "serial": r["serial"], "reg": r["reg"], "field": field,
                       "page_reading": page, "stored": [str(v) for v in stored],
                       "flag": (f.get("issue") or "")[:160]}
                (breaches if field in VERBATIM else typed).append(hit)
    return breaches, typed, quotes, len(rows)


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "punjab.db"
    breaches, typed, quotes, n = sweep(db)
    print(f"flagged entries scanned            : {n}")
    print(f"flag-quotes reporting a page reading: {quotes}")
    print(f"typed-field divergences (by spec)   : {len(typed)}  "
          f"{Counter(h['field'] for h in typed).most_common()}")
    print(f"VERBATIM-FIELD CANDIDATES           : {len(breaches)}  "
          f"{Counter(h['field'] for h in breaches).most_common()}\n")
    for h in breaches:
        print(f"{h['quarter']} p{h['printed_page']} s{h['serial']} reg {h['reg']} [{h['field']}]")
        print(f"   page   : {h['page_reading']!r}")
        print(f"   stored : {h['stored']}")
        print(f"   flag   : {h['flag']}\n")
    json.dump({"breach_candidates": breaches, "typed_by_spec": typed},
              open("analysis/integrity/verbatim_sweep.json", "w"), indent=1)
    print("wrote analysis/integrity/verbatim_sweep.json")
