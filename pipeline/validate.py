"""Internal consistency checks + diff against Davis's transcription sheet.

Outputs: out/adjudication_queue.csv (every disagreement/flag, with provenance)
and out/validation_report.md (summary counts by category).
"""
import csv, json, pathlib, re, sys
from collections import defaultdict


def norm(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def digits(s):
    return re.sub(r"[^0-9]", "", str(s or ""))


def fuzzy_same(a, b):
    a, b = norm(a), norm(b)
    if not a and not b:
        return True
    aw, bw = set(a.split()), set(b.split())
    return len(aw & bw) / max(1, min(len(aw), len(bw))) >= 0.5 if aw and bw else a == b


def main(manifest_path):
    m = json.load(open(manifest_path))
    data = pathlib.Path(m["data_dir"])
    rows = list(csv.DictReader(open(data / "out" / "entries.csv", encoding="utf-8-sig")))
    queue, report = [], defaultdict(int)

    def q(row, source, field, ours, theirs, issue):
        queue.append({"printed_page": row["printed_page"], "pdf_page": row["pdf_page"],
                      "lang": row["lang"], "topic": row["topic"], "serial": row["serial"],
                      "source": source, "field": field, "extraction": ours,
                      "other": theirs, "issue": issue})
        report[f"{source}:{issue if source != 'davis' else field}"] += 1

    # --- internal checks -------------------------------------------------
    seen_reg = defaultdict(list)
    seq = defaultdict(list)
    for r in rows:
        if r["reg"]:
            seen_reg[r["reg"]].append(r)
        if r["serial"]:
            seq[(r["lang"], r["topic"], r["char"])].append(r)
        for fl in json.loads(r["flags_json"] or "[]"):
            q(r, "flag", fl.get("field", "?"), "", "", fl.get("issue", "uncertain reading"))
        if r["copies"] and not (10 <= int(digits(r["copies"]) or 0) <= 20000):
            q(r, "internal", "copies", r["copies"], "", "copies outside plausible range")
    for reg, rs in seen_reg.items():
        if len(rs) > 1:
            for r in rs:
                q(r, "internal", "reg", reg, "", f"registration no. appears {len(rs)}x in quarter")
    for key, rs in seq.items():
        serials = [int(r["serial"]) for r in rs if r["serial"]]
        for a, b in zip(serials, serials[1:]):
            if b not in (a + 1, a):  # allow same-page split entries
                q(rs[0], "internal", "serial", f"{a}->{b}", "",
                  f"non-consecutive serials in {key[0]}-{key[1]}")

    # --- Davis sheet diff (skipped when the quarter has no transcription) --
    matched = unmatched_gt = 0
    if not m.get("davis_sheet"):
        return finish(m, data, rows, queue, report, matched, unmatched_gt)
    import openpyxl
    ds = m["davis_sheet"]
    ws = openpyxl.load_workbook(ds["workbook"], read_only=True)[ds["sheet"]]
    grows = list(ws.iter_rows(values_only=True))
    g = [[str(v).strip() if v is not None else "" for v in r] for r in grows[1:]]
    # sheet cols: 0 Lang,1 Char,2 Topic,3 Printer,4 City,5 Copies,6 Serial,7 Registr,
    #             8 Vol,9 #,10 Pg,11 Pp,12 Author,13 Publisher,14 City,15 Educ,16 gloss
    def gt_key(lang, char, topic, pg, serial):
        """Normalize Davis's and extraction conventions to a shared join key."""
        lang, char, topic = norm(lang), norm(char), norm(topic)
        lang = lang.replace(" and ", " ")
        char = char.replace(" characters", "").replace(" character", "")
        m = re.match(r"periodicals \((.+)\)", topic)
        if m:  # extraction side: topic 'Periodicals (Law)' -> lang 'periodicals <lang>'
            lang, topic = f"periodicals {lang}", m.group(1)
        if lang.startswith("periodicals"):
            lang = re.sub(r"\s+", " ", lang)
        return (pg, lang, char, topic[:6], str(serial))

    gmap = defaultdict(list)
    for r in g:
        if r[10] and digits(r[10]):
            gmap[gt_key(r[0], r[1], r[2], int(digits(r[10])), r[6])].append(r)

    # pass 1: join on registration number where unique in both sources
    gt_by_reg = defaultdict(list)
    for r in g:
        if digits(r[7]):
            gt_by_reg[digits(r[7])].append(r)
    ext_by_reg = defaultdict(list)
    for r in rows:
        if digits(r["reg"]):
            ext_by_reg[digits(r["reg"])].append(r)
    pairs, gt_used_p1 = {}, set()
    for reg, es in ext_by_reg.items():
        gs = gt_by_reg.get(reg, [])
        if len(es) == 1 and len(gs) == 1:
            pairs[id(es[0])] = gs[0]
            gt_used_p1.add(id(gs[0]))

    gt_used = set(gt_used_p1)
    for r in rows:
        cand = pairs.get(id(r))
        if cand is None:
            # pass 2: positional key for rows without a unique reg join
            key = gt_key(r["lang"], r["char"], r["topic"], int(r["printed_page"]), r["serial"])
            cands = [c for c in gmap.get(key, []) if id(c) not in gt_used]
            if not cands:
                cands = [c for k, cs in gmap.items() for c in cs
                         if k[0] == key[0] and k[1] == key[1] and k[2] == key[2] and k[4] == key[4]
                         and id(c) not in gt_used]
            cand = cands[0] if cands else None
            if cand is not None:
                gt_used.add(id(cand))
        if cand is None:
            q(r, "davis", "match", "", "", "entry not found in Davis sheet")
            continue
        matched += 1
        if digits(cand[10]) and digits(cand[10]) != digits(r["printed_page"]):
            q(r, "davis", "page", r["printed_page"], cand[10], "value differs")
        if digits(cand[7]) != digits(r["reg"]):
            q(r, "davis", "reg", r["reg"], cand[7], "value differs")
        if digits(cand[5]) != digits(r["copies"]):
            q(r, "davis", "copies", r["copies"], cand[5], "value differs")
        if cand[11] and r["pp_sum"] and abs(int(digits(cand[11]) or 0) - int(r["pp_sum"])) > max(20, 0.1 * int(r["pp_sum"])):
            q(r, "davis", "pp", f"{r['pp_verbatim']} (sum {r['pp_sum']})", cand[11], "pagination differs")
        if not fuzzy_same(cand[3], r["printer"]):
            q(r, "davis", "printer", r["printer"], cand[3], "value differs")
        if not fuzzy_same(cand[12], r["author"]):
            q(r, "davis", "author", r["author"], cand[12], "value differs")
    unmatched_gt = sum(1 for rs in gmap.values() for c in rs if id(c) not in gt_used)
    return finish(m, data, rows, queue, report, matched, unmatched_gt)


def finish(m, data, rows, queue, report, matched, unmatched_gt):
    out = data / "out"
    out.mkdir(exist_ok=True)
    with open(out / "adjudication_queue.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(queue[0].keys()) if queue else ["none"])
        w.writeheader()
        w.writerows(queue)
    lines = [f"# Validation report — {m['quarter']}", "",
             f"- extracted entries: {len(rows)}",
             f"- matched to Davis sheet: {matched}",
             f"- Davis rows not matched by any extraction: {unmatched_gt}",
             f"- adjudication queue: {len(queue)} items", "", "## By category"]
    lines += [f"- {k}: {v}" for k, v in sorted(report.items())]
    (out / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "manifest_1910Q2.json")
