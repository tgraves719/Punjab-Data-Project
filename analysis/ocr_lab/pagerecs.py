"""Page-ordered records for an entry-crop join.

D-017: the extraction JSONs hold true page order; the database does not — its
rows come out grouped by section, so on a page where one section ends and
another begins the database order is not the reading order. Zipping detected
entries against a plain `SELECT ... WHERE printed_page=?` therefore pairs every
crop after the section break with the wrong record.

That is exactly what happened in the first localization evaluation: it queried
the database directly, and the resulting labels showed English entries flagged
as carrying native-script titles. Every number computed from that pairing was
against shuffled labels.

Use this loader, not a bare SELECT.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "pipeline"


def page_entries(quarter: str, printed_page: int, con: sqlite3.Connection) -> list[dict]:
    path = PIPELINE / "data" / quarter / "extractions" / f"p{printed_page:03d}.json"
    if not path.exists():
        return []
    recs = json.load(open(path, encoding="utf-8"))
    con.row_factory = sqlite3.Row
    norm = {}
    for r in con.execute(
            "SELECT reg, serial, norm_lang, method, title_native FROM entries "
            "WHERE quarter=? AND printed_page=?", (quarter, printed_page)):
        norm[(str(r["reg"]), str(r["serial"]))] = dict(r)
    out = []
    for rec in recs:
        n = norm.get((str(rec.get("reg", "")), str(rec.get("serial", ""))), {})
        native = rec.get("title_native", n.get("title_native"))
        out.append(rec | {
            "norm_lang": n.get("norm_lang", rec.get("lang", "")),
            "method": n.get("method", ""),
            "native": str(native) in ("True", "true", "1") or native is True,
        })
    return out
