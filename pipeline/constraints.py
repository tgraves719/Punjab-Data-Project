"""Grammar constraints on a quarter's extracted entries.

The catalog is a legal instrument produced under the Press and Registration of
Books Act, and its redundancy is enormous: serials run consecutively inside a
section, registration numbers form one dense annual sequence, "Ditto" is a
formal anaphor, dates fall inside a known window. None of that needs a model or
a gold standard to check — which is the point. These checks run on any
extraction, of any quarter, forever, and give a quality signal where no ground
truth exists.

Each check returns Violations carrying the entry index, a code, and a message.
Nothing here corrects anything: a violation is a claim that the extraction and
the document's grammar disagree, and the disagreement may be the document's
(the register does contain genuine collisions and anomalies). Deciding which is
adjudication, and belongs to a human.

Thresholds are calibrated on the validated 1910Q2 golden extraction; where gold
itself violates a rule the rule is marked soft, and the calibration is recorded
beside it so a future reader can see what it was fitted to.

    from constraints import check_quarter
    violations = check_quarter(entries, quarter_end="1910-06-30")
"""

from __future__ import annotations

import collections
import dataclasses
import datetime as dt
import re

# Severity: "hard" — gold never violates it, so a violation is very likely an
# extraction error. "soft" — gold violates it occasionally, because the register
# itself is irregular there; useful in aggregate, not per entry.
HARD, SOFT = "hard", "soft"


@dataclasses.dataclass
class Violation:
    index: int              # position in the quarter's entry list
    code: str
    severity: str
    message: str
    printed_page: int | None = None
    reg: str = ""

    def as_dict(self) -> dict:
        return dataclasses.asdict(self)


def _int(v):
    s = str(v).replace(",", "").strip()
    return int(s) if s.isdigit() else None


def _edit_within(a: str, b: str, k: int) -> bool:
    """True when the Levenshtein distance between a and b is at most k.

    Banded, so the cost is O(k*n) — this runs over every rare-name/common-name
    pair in a quarter.
    """
    a, b = a.casefold(), b.casefold()
    if a == b:
        return True
    if abs(len(a) - len(b)) > k:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        lo, hi = max(1, i - k), min(len(b), i + k)
        for j in range(1, len(b) + 1):
            if j < lo or j > hi:
                cur[j] = k + 1
                continue
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1,
                         prev[j - 1] + (ca != b[j - 1]))
        if min(cur[lo:hi + 1] or [k + 1]) > k:
            return False
        prev = cur
    return prev[len(b)] <= k


def _date(v):
    """Parse the schema's ISO-ish date, ignoring any trailing Hijri year.

    The schema allows `1910-04-25`, `1910-04` when the day is absent, and a
    parenthesised Hijri year appended to either.
    """
    s = str(v).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        try:
            return dt.date(*map(int, m.groups()))
        except ValueError:
            return None
    m = re.match(r"^(\d{4})-(\d{2})", s)
    if m:
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), 1)
        except ValueError:
            return None
    m = re.match(r"^(\d{4})$", s)
    return dt.date(int(m.group(1)), 1, 1) if m else None


# --------------------------------------------------------------------------

def check_quarter(entries: list[dict], quarter_end: str | None = None,
                  reg_max: int = 1600) -> list[Violation]:
    """Run every check over one quarter's entries, in page order."""
    v: list[Violation] = []

    def add(i, code, sev, msg):
        e = entries[i] if 0 <= i < len(entries) else {}
        v.append(Violation(i, code, sev, msg,
                           e.get("printed_page"), str(e.get("reg", ""))))

    # --- serial runs -------------------------------------------------------
    # Calibration: in the 1910Q2 gold extraction the serial advances by exactly
    # +1 on all 237 within-section transitions. No exceptions. This is the
    # single most informative constraint the document offers.
    prev_section, prev_serial = None, None
    for i, e in enumerate(entries):
        raw_serial = str(e.get("serial", "")).strip()
        s = _int(e.get("serial"))
        section = str(e.get("section", ""))
        if s is None and raw_serial:
            # An empty serial is reported once, by the required-field check.
            add(i, "serial_nonint", HARD, f"serial {raw_serial!r} is not an integer")
        elif prev_section is not None and section == prev_section and prev_serial is not None:
            if s != prev_serial + 1:
                add(i, "serial_step", HARD,
                    f"serial {prev_serial} -> {s} inside section {section!r} "
                    f"(expected {prev_serial + 1})")
        prev_section, prev_serial = section, s if s is not None else prev_serial

    # --- registration numbers ---------------------------------------------
    regs = []
    for i, e in enumerate(entries):
        r = e.get("reg")
        n = _int(r)
        if n is None:
            add(i, "reg_nonint", HARD, f"reg {r!r} is not an integer")
            continue
        if not (1 <= n <= reg_max):
            add(i, "reg_range", HARD, f"reg {n} outside the annual sequence 1..{reg_max}")
        regs.append((n, i))

    # Soft: the 1910Q2 gold has two genuine collisions (394, 407), so a repeat
    # is a question for adjudication, not evidence of misreading.
    seen = collections.defaultdict(list)
    for n, i in regs:
        seen[n].append(i)
    for n, idxs in seen.items():
        if len(idxs) > 1:
            for i in idxs[1:]:
                add(i, "reg_duplicate", SOFT, f"reg {n} already used at entry {idxs[0]}")

    # --- Ditto, a formal anaphor ------------------------------------------
    prev_printer = None
    for i, e in enumerate(entries):
        verb = str(e.get("printer_verbatim", ""))
        printer = str(e.get("printer", "")).strip()
        if re.search(r"\bditto\b", verb, re.I):
            if not printer:
                add(i, "ditto_unresolved", HARD, "printer_verbatim is Ditto but printer is empty")
            elif prev_printer and printer != prev_printer:
                add(i, "ditto_mismatch", SOFT,
                    f"Ditto resolved to {printer!r} but previous printer was {prev_printer!r}")
        if printer:
            prev_printer = printer

    # --- required fields ---------------------------------------------------
    # `title` is deliberately not required. The catalog sets a long dash for an
    # entry that continues the title above it — the same anaphor as Ditto, one
    # column over — so an empty title beside a filled gloss is the printed form,
    # not an omission. An earlier version of this check raised 47 violations
    # corpus-wide that were almost all continuation entries.
    for i, e in enumerate(entries):
        for f in ("reg", "printer"):
            if not str(e.get(f, "")).strip():
                add(i, f"missing_{f}", HARD, f"required field {f} is empty")
        if not str(e.get("title", "")).strip() and not str(e.get("gloss", "")).strip():
            add(i, "missing_title", HARD, "title and gloss are both empty")
        if not str(e.get("serial", "")).strip():
            add(i, "missing_serial", HARD, "serial is empty")

    # --- numeric fields ----------------------------------------------------
    for i, e in enumerate(entries):
        c = e.get("copies")
        n = _int(c)
        if str(c).strip() and n is None:
            add(i, "copies_nonint", HARD, f"copies {c!r} is not an integer")
        elif n is not None and not (1 <= n <= 200000):
            add(i, "copies_range", SOFT, f"copies {n} outside 1..200000")

    # --- dates -------------------------------------------------------------
    # Calibration: gold dates for 1910Q2 span 1909-01 to 1910-06 — the register
    # notices publications issued well before the quarter, so only the forward
    # edge is hard.
    qend = _date(quarter_end) if quarter_end else None
    for i, e in enumerate(entries):
        raw = str(e.get("date", "")).strip()
        if not raw:
            add(i, "missing_date", SOFT, "date is empty")
            continue
        d = _date(raw)
        if d is None:
            add(i, "date_unparsed", HARD, f"date {raw!r} does not parse")
        elif qend:
            if d > qend:
                add(i, "date_after_quarter", HARD, f"date {d} is after the quarter ends {qend}")
            elif (qend - d).days > 730:
                add(i, "date_far_before", SOFT, f"date {d} is over two years before {qend}")

    # --- closed vocabularies ----------------------------------------------
    # The quarter is its own lexicon: 1910Q2 gold has 16 printer-cities across
    # 321 entries. A city appearing once is not wrong, but it is where misread
    # place names land.
    counts = collections.Counter(str(e.get("pcity", "")).strip()
                                 for e in entries if str(e.get("pcity", "")).strip())
    for i, e in enumerate(entries):
        c = str(e.get("pcity", "")).strip()
        if c and counts[c] == 1:
            add(i, "pcity_singleton", SOFT, f"printer-city {c!r} occurs once in the quarter")

    # --- near-duplicate entity names ---------------------------------------
    # The register reuses a small cast: 1910Q2 names 16 printer-cities and a few
    # dozen presses across 321 entries. A name that appears once and is one or
    # two characters from a name that appears often is not a new press — it is
    # the frequent one, misread. This is where the observed errors actually live
    # ("Qaumi Pross" for "Qaumi Press", "Dipak Bajput Press" for "Dipak Rajput
    # Press"), and unlike the sequence checks it needs no gold, only the
    # extraction's own distribution.
    for field, code, rare_max, common_min in (("printer", "printer_near_duplicate", 1, 4),
                                              ("pcity", "pcity_near_duplicate", 1, 4)):
        freq = collections.Counter(str(e.get(field, "")).strip()
                                   for e in entries if str(e.get(field, "")).strip())
        common = [n for n, c in freq.items() if c >= common_min]
        for i, e in enumerate(entries):
            name = str(e.get(field, "")).strip()
            if not name or freq[name] > rare_max:
                continue
            for other in common:
                if abs(len(other) - len(name)) <= 2 and _edit_within(name, other, 2):
                    add(i, code, HARD,
                        f"{field} {name!r} occurs {freq[name]}x and is within 2 edits "
                        f"of {other!r} ({freq[other]}x)")
                    break

    # --- section headers ---------------------------------------------------
    for i, e in enumerate(entries):
        sec = str(e.get("section", "")).strip()
        if not sec:
            add(i, "missing_section", HARD, "section is empty")
            continue
        lang = str(e.get("lang", "")).strip()
        if lang and lang.split()[0].upper() not in sec.upper():
            add(i, "section_lang_mismatch", SOFT,
                f"lang {lang!r} not present in section {sec!r}")

    return v


def summarise(violations: list[Violation]) -> dict:
    by_code = collections.Counter(v.code for v in violations)
    by_sev = collections.Counter(v.severity for v in violations)
    return {"total": len(violations), "by_severity": dict(by_sev),
            "by_code": dict(by_code.most_common())}


def entries_with_violations(violations: list[Violation],
                            severity: str | None = None) -> set[int]:
    return {v.index for v in violations if severity is None or v.severity == severity}
