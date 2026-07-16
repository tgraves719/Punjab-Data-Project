"""S5 — Interactive explorer, generalized to every year in punjab.db (D-012, D-013).

Generates out/explore_1910_1912.html: a single self-contained file (all data and
code embedded, no network access, no server) that lets Thomas and Davis browse
the corpus — overview dashboard with a register-over-time strip, filterable
entry table with full verbatim records, printer-publisher network (canvas force
layout, built client-side from the embedded entries), the script-market
comparison, and curated exhibits. Originally the 1910 slice explorer; now reads
ALL quarters in the DB (the old single-year build survives as explore_1910.html,
which this script no longer overwrites).

Source linking (D-013): every record's detail panel links to its scan. The
built-in viewer tries `pages/<quarter>/pXXX_pdfYYY.png` (packaged layout) then
the repo-relative pipeline path; a second link deep-opens the bound PDF volume
at the exact page (file:// + #page=N, works in Chrome/Edge/Firefox viewers).

Usage:
  python build_site.py            rebuild the HTML
  python build_site.py --package  also copy all page PNGs (~145 MB) into
                                  out/pages/ so out/ can be zipped for Davis
Inputs: ../../punjab.db, out/network_*.csv, ../../pipeline/manifest_1910Q*.json
"""
import csv, json, pathlib, re, shutil, sqlite3, sys, urllib.parse

from build_network import publisher_entity, SELF_RE  # single source of entity logic (D-011)

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
DB = HERE.parent.parent / "punjab.db"


def copies_int(c):
    d = re.sub(r"[^\d]", "", c or "")
    return int(d) if d else 0


def jdump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


con = sqlite3.connect(DB)
cols = ("quarter printed_page pdf_page serial section norm_lang topic reg copies norm_printer "
        "norm_pcity author title gloss publisher pubcity date price edition educ "
        "periodical copyright notes marks flags_json").split()
entries = []
# order by quarter (chronological: '1910Q1' < … < '1912Q4'), then rowid so each
# quarter keeps its extraction/reading order (page → printed section → serial).
for r in con.execute(f"select {', '.join(cols)} from entries order by quarter, rowid"):
    e = dict(zip(cols, r))
    flags = json.loads(e["flags_json"] or "[]")
    entries.append({
        "q": e["quarter"], "pg": int(e["printed_page"]), "pdf": int(e["pdf_page"]),
        "s": e["serial"],
        "sec": e["section"], "lang": e["norm_lang"], "top": e["topic"],
        "reg": e["reg"], "cop": copies_int(e["copies"]), "pr": e["norm_printer"],
        "city": e["norm_pcity"], "au": e["author"], "ti": e["title"],
        "gl": e["gloss"], "pub": e["publisher"], "pubc": e["pubcity"],
        "dt": e["date"], "price": e["price"], "ed": e["edition"],
        "educ": e["educ"], "per": e["periodical"], "cr": e["copyright"],
        "no": e["notes"], "mk": e["marks"],
        "pube": publisher_entity(e["publisher"]) or "",
        "fl": "; ".join(f"{f.get('field','?')}: {f.get('issue','')}" for f in flags),
    })
con.close()

# per-quarter source info: printed->pdf offset, printed-page range, PDF file URL
QINFO = {}
for e in entries:
    q = e["q"]
    d = QINFO.setdefault(q, {"off": e["pdf"] - e["pg"], "min": e["pg"], "max": e["pg"]})
    d["min"] = min(d["min"], e["pg"])
    d["max"] = max(d["max"], e["pg"])
for q, d in QINFO.items():
    mf = HERE.parent.parent / "pipeline" / f"manifest_{q}.json"
    vol = json.load(open(mf))["volume_pdf"]
    # --public: omit the file:// deep-link into the bound volume (a machine-local
    # path that is useless — and leaks the local directory layout — on the web).
    # The JS hides the "open PDF" links whenever pdfurl is empty.
    d["pdfurl"] = "" if "--public" in sys.argv else \
        "file:///" + urllib.parse.quote(vol.replace("\\", "/"), safe="/:")

# The network tab builds its graphs client-side from the embedded entries
# (D-012 update), so the 1910-slice Gephi CSVs are no longer read here; the
# overview tiles count entities directly from the corpus instead.
nodes, edges = [], []
n_printers = len({e["pr"] for e in entries if e["pr"]})
n_publishers = len({e["pube"] for e in entries if e["pube"]})

EXHIBITS_NEW = [
    {"cite": "1910–1912, every quarter's end-leaf", "title": "A reader tracks the scriptures across three years",
     "blurb": "The unidentified earlier hand's pencil finding-aid runs the length of the bound volume: serialized Arya-Samaj scripture installments are logged quarter by quarter — Arsh Granthawali from volume II (1910) to VIII.6–7 on the volume's literal last leaf (December 1912), the Rig Veda Samhita from installment 37 to 74. One reader, three years, one continuous act of second-order observation over the register.", "search": "Granthawali"},
    {"cite": "1912 Q2 p47 s2", "title": "The new Reporter also registers himself",
     "blurb": "Khalifa Imad-ud-din — who signs the 1911–1912 catalogues as Reporter on Books after Suraj Narayan Mehr — appears inside his own register: a New First Persian Reader, 5,000 copies, compiled by 'Khalifa Imad-ud-din, Reporter on Books, Education Department, Punjab.' The observation operator keeps writing itself into the record, across a change of personnel.", "search": "Persian Reader"},
    {"cite": "1911 Q1 p13 s13", "title": "Thirty thousand handbills",
     "blurb": "Hand Bill No. 33, Sachi Yadgar — verses commemorating Guru Gobind Singh, distributed free by the Khalsa Dewan and the Sikh Hand Bill Committee at 30,000 copies, the largest run of early 1911. Like 1910's almanacs and army forms, the true mass media are free ephemera, not priced books.", "search": "Sachi Yadgar"},
    {"cite": "1912 Q4 p31 s55", "title": "New Fashion ka Beta aur Old Fashion ka Bap",
     "blurb": "A social comedy of generational style-war, its title half in English — and in the register it carries a broken piece of type that the extraction preserved with a flagged lookalike character rather than silently correcting. The verbatim layer keeping faith with the print shop's own accidents.", "search": "New Fashion"},
]

EXHIBITS = [
    {"cite": "Q4 p28 s70 & p39 s4", "title": "The observer observed",
     "blurb": "Suraj Narayan Mehr — the Reporter on Books who signs these catalogs — registers his own Vedanta-and-Sufism poetry (Kalam-i-Mehr, 8,000 copies) and a verse Bhagavad Gita filling the Sadhu Magazine special number, copyrights both to 'Reporter on Books' as his identity, then signs the page. An earlier hand pencilled 'Spec.' beside the Gita.", "search": "Kalam-i-Mehr",
     "img": "img/mehr_colophon_1910q1.png", "cap": "His signature closes every quarter's list. Here the foot of the March 1910 catalogue (printed p. 51): “Suraj Narayan Mehr, Reporter on Books, Education Department, Punjab” — the compiler signing the register he also appears inside."},
    {"cite": "Q2–Q4, 21 issues", "title": "One text, three scripts",
     "blurb": "The Punjab Hindu Family Mutual Relief Fund's monthly circular, printed simultaneously in Urdu (5,000–8,000/issue, series Vol. XV), Punjabi (~1,000, Vol. VIII) and Hindi (~900, Vol. VIII) — a controlled measurement of the script hierarchy, run monthly by the fund itself.", "search": "Relief Fund"},
    {"cite": "Q4 p26 s183, p18 s2, p30 s91 · Q1 p37 s45, p6 s6", "title": "The music question, all three fronts",
     "blurb": "A copyrighted 5,000-copy harmonium tutor (Guldasta-i-Harmonium), an Urdu raga manual (Rag Binod), and a translation of Qazi Sanaullah Panipati defending music's permissibility in Islam — commerce, pedagogy, and theology of the soundscape in one quarter. Q1 shows the same front opening earlier in the year: the harmonium tutor's own first edition (Guldasta-i-Harmonium, Part I), and a Froebel kindergarten songbook (Balodyan Sangit ki Pahili Kyari) — Western school-music pedagogy arriving alongside the reed organ.", "search": "Harmonium"},
    {"cite": "Q4 p30 s90, p28 s5, p32 s4", "title": "One editor's pan-Islamic program",
     "blurb": "Insha-Ullah of the Watan registers the Gospel of Barnabas (via the 1908 Cairo Arabic edition), Knight's Awakening of Turkey, and Garnett's The Turkish People — Cairo and Istanbul reaching Lahore within two years, through one man's list.", "search": "Barnabas"},
    {"cite": "Q4 p30 s92", "title": "Draper in Urdu",
     "blurb": "Zafar Ali Khan (later of the Zamindar) translates J. W. Draper's History of the Conflict between Religion and Science — 504 pages, copyrighted, and filed by the registrar under RELIGION.", "search": "Maraka-i-Mazhab"},
    {"cite": "Q4 p16 s15, p29 s82, p32 s103, p23 s155, p31 s100", "title": "The polemic ring",
     "blurb": "Sikh shuddhi dialogue; Jain rebuttal of the Satyarth Prakash; Muslim critique of the Vedas; Arya attack on Genesis; printed proceedings of a live Sunni–'Wahabi' village debate (250 free copies). Every community answers every other, through the same presses.", "search": "Shudhi"},
    {"cite": "Q4 p19 s15–16, p20 s34", "title": "Shakespeare and the penny dreadful arrive together",
     "blurb": "Khun-i-Nahaq urf Hamlet, a third edition of Dilfarosh (Merchant of Venice), and G. W. M. Reynolds's Necromancer — the Victorian repertoire adapted for the Urdu market by Hindu munshis.", "search": "Hamlet"},
    {"cite": "Q4 p26–27 s59–62 (regs 1246–1249)", "title": "Canon formation in one day",
     "blurb": "The Vakil Trading Co. of Amritsar registers four Hali titles in a single transaction, continuing its Sir Syed / Shibli / Azad reprint program from Q3 — a commercial firm assembling the Urdu canon in real time.", "search": "Hali"},
    {"cite": "Q3 p33 s90", "title": "The 100,000-copy almanac",
     "blurb": "Mash-hur-i-Alam Jantri 1911 — the largest print run registered in 1910, an almanac; the year's true mass medium is the calendar, not the book.", "search": "Jantri"},
    {"cite": "Q4 p18 s1, p35 s1, p36 s1", "title": "The taxonomy under strain",
     "blurb": "A Tibetan Kalachakra calendar from Bashahr state; 'SANSKRIT IN PERSIAN CHARACTER' (a Vishnu Sahasranama glossary for Urdu-script devotees); 'POLYGLOT' (a four-script copybook by a serving sepoy, his third title of the quarter). The registry's categories visibly improvise.", "search": "Kalchakr"},
    {"cite": "Q4 p15 s297", "title": "Print counterinsurgency",
     "blurb": "Jawab-i-Pagri-Sambhal-o-Jatta — a loyalist verse rebuttal of the 1907 agrarian-agitation anthem, in its second edition: the state's side of a song war, conducted in pamphlets.", "search": "Pagri"},
    {"cite": "Q4 p14 s285–287", "title": "The street observed",
     "blurb": "Qissa-i-Photo Amritsar (a verse exposé of the brothel quarter), a dacoit ballad of Sundar Singh Dharwi, and Hinduon ka Asli Khaka (economic-communal polemic) — the bazaar's own sociology, at six pies.", "search": "Qissa-i-Photo"},
    {"cite": "Q1 p48 s1", "title": "One scripture, four languages, a Theosophist mediator",
     "blurb": "The Bhagavad Gita filed under POLYGLOT: the Sanskrit text with Hindi and Urdu renderings by Diwan Maya Das and an English translation by Mrs. Annie Besant, bound as one Lahore edition. A single sacred text refracted through four scripts and a European occult-nationalist — the year's most layered act of observation, and a clean picture of how a text is made to mean across languages at once.", "search": "Besant"},
    {"cite": "Q1 p42 s19", "title": "The imperial courtroom, borrowed for a trial of the caliphs",
     "blurb": "Sharh-i-Kauz-i-Maktum argues a Shia–Sunni dispute as a mock lawsuit: the Sunnis are cast as plaintiffs and the Shias as defendants, issues are framed, evidence is heard from both counsels, and judgment is delivered — for the Shias. The colonial court's procedure, the most visible face of imperial power, repurposed as the container for a religious argument.", "search": "Kauz-i-Maktum"},
    {"cite": "Q1 p50–51 s1–9", "title": "The empire's law report, doubled into Urdu",
     "blurb": "The Punjab Record — the official judicial law-reports, English, edited by an English barrister — runs in Q1 as a parallel Urdu edition: nine issues edited by an Indian barrister (Ganpat Rai) at the Civil & Military Gazette press, down to a separately-registered Urdu index volume. The instrument of imperial law translating itself, finding-apparatus and all, for native practitioners.", "search": "Urdu Punjab Record"},
    {"cite": "Q1 p44, p46 s1, p47 s1", "title": "One tongue, many scripts",
     "blurb": "Q1's bilingual sections catch the script system in motion: Urdu love-verse set in Gurmukhi (Nagma Sukhan Kamal); a midwifery handbook in Roman Urdu by an American woman doctor (Dai Gari ke Asul); a glossary of English words transliterated into Urdu script (Zaruri Angrezi Alfaz); and bookkeeping in the merchants' Mahajani shorthand (Mahajani Darpan). The language holds still; the script is the battlefield — the disaggregation that hardens by Partition.", "search": "Nagma Sukhan Kamal"},
]
# the original exhibits were written when the explorer covered 1910 only;
# prefix the year so their cites stay unambiguous in the multi-year build
for _x in EXHIBITS:
    _x["cite"] = "1910 " + _x["cite"]
EXHIBITS = EXHIBITS_NEW + EXHIBITS

# self-publication share and adjudication-queue total, computed live so the
# overview tiles and the method notes never drift from the data (see this file's
# history: hardcoded "33%"/"131" went stale when Q1 was added).
n_self = sum(1 for e in entries if SELF_RE.match((e["pub"] or "").strip()))
n_queue = 0  # flag + internal items; excludes Davis-sheet reconciliation rows (a
             # separate transcription cross-check, not a flagged catalog reading)
for q in QINFO:
    qf = HERE.parent.parent / "pipeline" / "data" / q / "out" / "adjudication_queue.csv"
    if qf.exists():
        with open(qf, encoding="utf-8-sig") as fh:
            n_queue += sum(1 for row in csv.DictReader(fh)
                           if (row.get("source") or "").strip() != "davis")

META = {
    "entries": len(entries), "copies": sum(e["cop"] for e in entries),
    "printers": n_printers,
    "publishers": n_publishers,
    "years": len({e["q"][:4] for e in entries}),
    "selfpub": f"{round(100 * n_self / len(entries))}%",
    "selfpub_n": n_self,
    "flagged": n_queue,
}

# chronological register-over-time strip: [quarter, titles, copies]
from collections import OrderedDict
_tl = OrderedDict()
for e in entries:
    d = _tl.setdefault(e["q"], [0, 0])
    d[0] += 1
    d[1] += e["cop"]
TIMELINE = [[q, n, c] for q, (n, c) in _tl.items()]

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Punjab 1910–1912 — the imperial print register</title>
<style>
:root{--ink:#2b2620;--paper:#f7f3ea;--card:#fffdf7;--rule:#d8cfbc;--acc:#8a5a44;--acc2:#4d6d9a;--dim:#7a7060}
*{box-sizing:border-box}
body{margin:0;font:15px/1.55 Georgia,'Times New Roman',serif;background:var(--paper);color:var(--ink)}
header{padding:26px 30px 12px;border-bottom:3px double var(--rule)}
header h1{margin:0;font-size:24px;font-weight:normal;letter-spacing:.4px}
header p{margin:4px 0 0;color:var(--dim);font-size:13.5px}
nav{display:flex;gap:4px;padding:10px 26px 0;border-bottom:1px solid var(--rule);flex-wrap:wrap}
nav button{font:14px Georgia,serif;padding:8px 16px;border:1px solid var(--rule);border-bottom:none;
 background:#efe9db;color:var(--ink);cursor:pointer;border-radius:6px 6px 0 0}
nav button.on{background:var(--card);font-weight:bold}
main{padding:22px 30px;max-width:1200px;margin:0 auto}
section{display:none}section.on{display:block}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin:10px 0 22px}
.card{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:14px 20px;min-width:150px}
.card b{display:block;font-size:26px}.card span{color:var(--dim);font-size:12.5px}
h2{font-size:19px;font-weight:normal;border-bottom:1px solid var(--rule);padding-bottom:5px;margin:26px 0 12px}
.bar{display:flex;align-items:center;margin:3px 0;font-size:13px}
.bar .lbl{width:190px;text-align:right;padding-right:10px;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .trk{flex:1;display:flex;align-items:center;gap:8px}
.bar .fill{height:15px;border-radius:2px;min-width:2px}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
select,input[type=text]{font:13.5px Georgia,serif;padding:6px 8px;border:1px solid var(--rule);border-radius:5px;background:var(--card);color:var(--ink)}
input[type=text]{width:230px}
label.ck{font-size:13px;color:var(--dim)}
table{border-collapse:collapse;width:100%;background:var(--card);font-size:13px}
th{position:sticky;top:0;background:#efe9db;text-align:left;padding:7px 9px;border-bottom:2px solid var(--rule);cursor:default;white-space:nowrap}
td{padding:6px 9px;border-bottom:1px solid #ece5d4;vertical-align:top}
tr.rw{cursor:pointer}tr.rw:hover{background:#f3edde}
.count{color:var(--dim);font-size:13px;margin:8px 2px}
#detail{position:fixed;right:0;top:0;bottom:0;width:min(480px,92vw);background:var(--card);
 border-left:2px solid var(--rule);padding:22px 26px;overflow-y:auto;box-shadow:-6px 0 18px rgba(0,0,0,.12);display:none;z-index:40}
#detail.on{display:block}
#detail h3{margin:0 40px 4px 0;font-size:17px}
#detail .x{position:absolute;top:12px;right:14px;font-size:22px;cursor:pointer;color:var(--dim);background:none;border:none}
.fld{margin:7px 0;font-size:13.5px}.fld b{color:var(--dim);font-weight:normal;font-size:11.5px;text-transform:uppercase;letter-spacing:.6px;display:block}
.flag{background:#f6e8d8;border-left:3px solid var(--acc);padding:6px 9px;font-size:12.5px;margin-top:8px}
canvas{background:var(--card);border:1px solid var(--rule);border-radius:8px;max-width:100%}
.zoomctl{display:inline-flex;gap:3px}
.zoomctl button{font:inherit;font-size:13px;line-height:1;min-width:26px;padding:4px 7px;background:var(--card);border:1px solid var(--rule);border-radius:5px;color:var(--ink);cursor:pointer}
.zoomctl button:hover{background:var(--rule)}
.legend{font-size:12.5px;color:var(--dim);margin:6px 2px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin:0 4px 0 12px}
#tip{position:fixed;background:#332d24;color:#f7f3ea;padding:7px 11px;border-radius:6px;font-size:12.5px;pointer-events:none;display:none;z-index:50;max-width:280px}
#scan{position:fixed;inset:0;background:rgba(30,26,20,.93);z-index:60;display:none;flex-direction:column}
#scan.on{display:flex}
#scanBar{display:flex;gap:10px;align-items:center;padding:10px 18px;color:#f7f3ea;font-size:13.5px}
#scanBar button{font:13px Georgia,serif;padding:5px 12px;border:1px solid #6a6154;border-radius:5px;background:#443c30;color:#f7f3ea;cursor:pointer}
#scanBar .sp{flex:1}
#scanWrap{flex:1;overflow:auto;text-align:center;padding:0 18px 18px}
#scanImg{max-width:100%;background:#fff;cursor:zoom-in;border-radius:3px}
#scanImg.zoom{max-width:none;cursor:zoom-out}
#scanMsg{color:#e8ddc8;padding:40px;font-size:14px;display:none}
.srcBtn{font:12.5px Georgia,serif;padding:4px 10px;border:1px solid var(--rule);border-radius:5px;background:#efe9db;cursor:pointer;margin-right:8px}
.ex{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:14px 18px;margin:12px 0}
.ex h3{margin:0 0 2px;font-size:16px}.ex .cite{color:var(--acc);font-size:12.5px}
.ex p{margin:7px 0 8px;font-size:13.5px}
.ex button{font:12.5px Georgia,serif;padding:4px 10px;border:1px solid var(--rule);border-radius:5px;background:#efe9db;cursor:pointer}
.note{background:#efe9db;border-radius:8px;padding:12px 16px;font-size:13px;color:var(--dim);margin:14px 0}
footer{padding:18px 30px;color:var(--dim);font-size:12px;border-top:1px solid var(--rule);margin-top:30px}
</style></head><body>
<header>
 <h1>Punjab, 1910–1912 — three years of the imperial print register</h1>
 <p>Catalogue of Books registered in the Punjab under Act XXV of 1867 and Act X of 1890 · twelve quarters, March 1910 – December 1912 · extracted from SV 412/44 · Graves &amp; Davis</p>
</header>
<nav>
 <button data-t="ov" class="on">Overview</button>
 <button data-t="en">Explore the %%NENT%% entries</button>
 <button data-t="nw">Printer–publisher network</button>
 <button data-t="mk">The script market</button>
 <button data-t="ex">Exhibits</button>
 <button data-t="me">Method &amp; caveats</button>
</nav>
<main>
<section id="ov" class="on">
 <div class="cards" id="ovCards"></div>
 <h2>The register over time — titles and copies by quarter</h2>
 <div id="ovTime"></div>
 <h2>Registered titles and copies by language (books; periodicals excluded)</h2>
 <div id="ovLang"></div>
 <h2>Topics</h2><div id="ovTopic"></div>
 <h2>Where it was printed</h2><div id="ovCity"></div>
</section>
<section id="en">
 <div class="controls">
  <select id="fQ"><option value="">All quarters</option></select>
  <select id="fL"><option value="">All languages</option></select>
  <select id="fT"><option value="">All topics</option></select>
  <select id="fC"><option value="">All print cities</option></select>
  <select id="fP"><option value="">All printers</option></select>
  <input type="text" id="fS" placeholder="Search title, gloss, author, notes…">
  <label class="ck"><input type="checkbox" id="fFlag"> flagged only</label>
  <label class="ck"><input type="checkbox" id="fEduc"> educational</label>
  <label class="ck"><input type="checkbox" id="fMark"> annotated</label>
 </div>
 <div class="count" id="enCount"></div>
 <div style="max-height:70vh;overflow:auto;border:1px solid var(--rule);border-radius:8px">
 <table><thead><tr><th>Qtr</th><th>p.s</th><th>Language</th><th>Topic</th><th>Title</th><th>Author</th><th>Printer</th><th>Copies</th><th>Price</th></tr></thead>
 <tbody id="enBody"></tbody></table></div>
</section>
<section id="nw">
 <div class="controls">
  <select id="nwType">
   <option value="pp">Printer ↔ Publisher</option>
   <option value="pl">Printer ↔ Language</option>
   <option value="xx">Printer ↔ Printer (shared publishers)</option>
   <option value="ap">Author ↔ Printer</option>
  </select>
  <label class="ck">min. entries per node <input type="range" id="nwMin" min="1" max="20" value="3" style="vertical-align:middle"> <span id="nwMinV">3</span></label>
  <span class="zoomctl"><button id="nwOut" title="Zoom out">&minus;</button><button id="nwIn" title="Zoom in">+</button><button id="nwFit" title="Reset / fit to view">Fit</button></span>
  <span class="legend" id="nwLegend"></span>
  <span class="legend" id="nwStats" style="margin-left:auto"></span>
 </div>
 <canvas id="nwC" width="1140" height="640" style="touch-action:none"></canvas>
 <div class="note" id="nwCap"></div>
</section>
<section id="mk">
 <h2>One text, three scripts: the Relief Fund circular (1910)</h2>
 <p style="max-width:760px">The Punjab Hindu Family Mutual Relief Fund issued its monthly circular in Urdu, Punjabi (Gurmukhi) and Hindi (Nagari) — same text, same publisher, same registration day, consecutive registration numbers. Average copies per issue, by quarter:</p>
 <canvas id="mkC" width="700" height="330"></canvas>
 <div class="note">The Urdu edition is at series <b>Volume XV</b>; Hindi and Punjabi at <b>Volume VIII</b> — a Hindu mutual-aid society spoke to its members in Urdu only for its first seven years. Print runs measure publisher supply decisions, not readership.</div>
 <h2>Language market table (books only)</h2>
 <div style="max-height:50vh;overflow:auto;border:1px solid var(--rule);border-radius:8px">
 <table><thead><tr><th>Language</th><th>Titles</th><th>Copies</th><th>Median run</th><th>% free</th><th>% educational</th></tr></thead>
 <tbody id="mkBody"></tbody></table></div>
</section>
<section id="ex"><div id="exList"></div></section>
<section id="me">
 <h2>Method</h2>
 <div class="note" style="color:var(--ink)">
 <p><b>Source.</b> Scanned quarterly <i>Catalogues of Books registered in the Punjab</i> (India Office SV 412/44), all twelve quarters of 1910, 1911 and 1912 — the complete 1910–1912 bound volume. Registration numbers run as one annual sequence per year (1910: 1–1410; 1911: 1–1565; 1912: 1–1532). 1910 was transcribed in-session and cross-checked against Prof. Davis's independent hand-transcription; 1911–1912 were extracted via the Batch API with the model chosen by a scored bake-off against the 1910 golden quarter (decision log D-015).</p>
 <p><b>Three-layer model.</b> Page image → verbatim record (the catalog's own words, misprints and editorializing preserved) → normalized layer (our act: spelling folds, script variants, press-name aliases — every fold documented in the project decision log). This explorer displays normalized language/printer/city and verbatim everything else.</p>
 <p><b>Provenance.</b> Every entry carries printed page + serial ("p.s" column) and PDF page. Each record's detail panel links straight to its source: "view scanned page" opens the page image in this window (arrow keys page through the quarter; click to zoom). Local builds additionally deep-link the bound-volume PDF at the exact page. If the scan viewer reports missing images, open this file from inside the project folder or rebuild with <code>python build_site.py --package</code>.</p>
 <p><b>Uncertainty.</b> %%FLAGGED%% items sit in the twelve quarters' adjudication queues (degraded digits, margin-cut copyright numbers, pencil-obscured serials, plus cross-entry checks such as registration collisions) — per-entry flags are visible in the detail panel and filterable ("flagged only").</p>
 <p><b>Scope.</b> Registered print runs measure publisher supply decisions under a legal-deposit regime.</p>
 <p><b>Prior-hand marginalia.</b> The bound volume carries pencil annotations — X-marks, a running margin count, "Specimen" notes, and handwritten multi-part indexes at nearly every quarter's end (once bound <i>inside</i> a quarter, 1911 Q1; once on the volume's very last leaf, after December 1912) — in an earlier, unidentified hand that <i>predates</i> Prof. Davis's acquisition of the volumes (confirmed with him). We capture them per-entry (the "annotated" filter) and per-leaf (marginalia_*.md in the quarter data folders) as a second-order layer over the register; their provenance and meaning remain an open question.</p>
 </div>
</section>
</main>
<div id="detail"><button class="x" onclick="closeDetail()">×</button><div id="detailBody"></div></div>
<div id="tip"></div>
<div id="scan">
 <div id="scanBar">
  <button onclick="scanNav(-1)">← previous page</button>
  <button onclick="scanNav(1)">next page →</button>
  <span id="scanCap"></span><span class="sp"></span>
  <a id="scanPdf" target="_blank" style="color:#e8ddc8">open in PDF</a>
  <button onclick="closeScan()">close ×</button>
 </div>
 <div id="scanWrap"><img id="scanImg" alt="scanned catalog page"><div id="scanMsg"></div></div>
</div>
<footer>Generated from punjab.db by analysis/slice_1910/build_site.py · verbatim layer preserves the catalog as printed · normalization per DECISIONS.md D-008/D-010/D-011 · July 2026</footer>
<script>
const E=%%ENTRIES%%,NODES=%%NODES%%,EDGES=%%EDGES%%,EXH=%%EXHIBITS%%,META=%%META%%,QINFO=%%QINFO%%,TL=%%TIMELINE%%;
const $=id=>document.getElementById(id);
const fmt=n=>n.toLocaleString('en-US');
const qlbl=q=>q.slice(0,4)+' Q'+q[5];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
/* tabs */
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{
 document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
 document.querySelectorAll('main section').forEach(x=>x.classList.remove('on'));
 b.classList.add('on');$(b.dataset.t).classList.add('on');
 if(b.dataset.t==='nw')initNet();if(b.dataset.t==='mk')drawFund();});
/* ---------- overview ---------- */
(function(){
 const c=$('ovCards');
 [[fmt(META.entries),'entries extracted'],[fmt(META.copies),'registered copies'],
  [META.printers,'printing houses'],[META.publishers,'publisher entities'],
  [META.selfpub,'self-published'],[fmt(META.flagged),'flagged items']]
 .forEach(([b,s])=>{const d=document.createElement('div');d.className='card';d.innerHTML='<b>'+b+'</b><span>'+s+'</span>';c.appendChild(d);});
 function bars(el,agg,color,fmtv,max){
  const rows=Object.entries(agg).sort((a,b)=>b[1]-a[1]).slice(0,max||10);
  const top=rows[0][1];
  el.innerHTML=rows.map(([k,v])=>'<div class="bar"><div class="lbl" title="'+esc(k)+'">'+esc(k)+
   '</div><div class="trk"><div class="fill" style="width:'+(90*v/top)+'%;background:'+color+'"></div><span>'+fmtv(v)+'</span></div></div>').join('');
 }
 const langN={},langC={},topN={},cityN={};
 E.forEach(e=>{if(e.per!=='Y'){langN[e.lang]=(langN[e.lang]||0)+1;langC[e.lang]=(langC[e.lang]||0)+e.cop;}
  topN[e.top]=(topN[e.top]||0)+1;if(e.city)cityN[e.city]=(cityN[e.city]||0)+1;});
 const wrap=document.createElement('div');wrap.style.cssText='display:flex;gap:40px;flex-wrap:wrap';
 const d1=document.createElement('div'),d2=document.createElement('div');
 d1.style.flex='1';d2.style.flex='1';d1.style.minWidth='420px';d2.style.minWidth='420px';
 d1.innerHTML='<div class="legend">titles</div>';d2.innerHTML='<div class="legend">copies</div>';
 const b1=document.createElement('div'),b2=document.createElement('div');
 d1.appendChild(b1);d2.appendChild(b2);wrap.appendChild(d1);wrap.appendChild(d2);
 $('ovLang').appendChild(wrap);
 bars(b1,langN,'#4d6d9a',fmt);bars(b2,langC,'#8a5a44',fmt);
 bars($('ovTopic'),topN,'#6a8a5a',fmt,10);bars($('ovCity'),cityN,'#8a7a44',fmt,8);
 /* chronological timeline: two ALIGNED panels (titles | copies), each series on
    its own common baseline and its own scale — never two scales on one row
    (the dual-axis mistake, horizontal edition). A faint dashed rule marks each
    panel's median quarter as an anchor for "normal" without distorting scale. */
 const tmax=Math.max(...TL.map(r=>r[1])),cmax=Math.max(...TL.map(r=>r[2]));
 const med=a=>{const s=[...a].sort((x,y)=>x-y),m=s.length>>1;return s.length%2?s[m]:(s[m-1]+s[m])/2;};
 const tmed=med(TL.map(r=>r[1])),cmed=med(TL.map(r=>r[2]));
 const cell=(v,max,mv,color,label)=>'<div style="position:relative;display:flex;align-items:center;gap:8px;min-height:17px">'+
  '<div style="position:absolute;left:'+(72*mv/max)+'%;top:-3px;bottom:-3px;border-left:1px dashed #c5b892" title="median quarter"></div>'+
  '<div class="fill" style="width:'+(72*v/max)+'%;background:'+color+';position:relative;height:15px;border-radius:2px;min-width:2px;flex:none"></div><span style="font-size:12.5px">'+label+'</span></div>';
 $('ovTime').innerHTML=
  '<div style="display:grid;grid-template-columns:70px 1fr 1fr;gap:4px 26px;align-items:center;max-width:1050px">'+
  '<div></div><div class="legend">titles registered</div><div class="legend">copies registered</div>'+
  TL.map(([q,n,c])=>'<div class="lbl" style="width:auto;text-align:right;padding:0">'+qlbl(q)+'</div>'+
   cell(n,tmax,tmed,'#4d6d9a',fmt(n))+cell(c,cmax,cmed,'#8a5a44',fmt(c))).join('')+
  '</div><div class="legend" style="margin-top:6px">each panel has its own scale and baseline — compare bars within a column; read across a row to spot quarters where titles and copies decouple (mass ephemera). Dashed line = median quarter.</div>';
})();
/* ---------- entries ---------- */
function opts(sel,vals,byName){const cnt={};vals.forEach(v=>{if(v)cnt[v]=(cnt[v]||0)+1;});
 Object.entries(cnt).sort(byName?(a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0:(a,b)=>b[1]-a[1]).forEach(([v,n])=>{
  const o=document.createElement('option');o.value=v;o.textContent=v+' ('+n+')';sel.appendChild(o);});}
opts($('fQ'),E.map(e=>e.q),true);opts($('fL'),E.map(e=>e.lang));opts($('fT'),E.map(e=>e.top));
opts($('fC'),E.map(e=>e.city));opts($('fP'),E.map(e=>e.pr));
['fQ','fL','fT','fC','fP','fS','fFlag','fEduc','fMark'].forEach(id=>$(id).addEventListener('input',renderTable));
let shown=[];
function renderTable(){
 const q=$('fQ').value,L=$('fL').value,T=$('fT').value,C=$('fC').value,P=$('fP').value,
  s=$('fS').value.toLowerCase(),fo=$('fFlag').checked,eo=$('fEduc').checked,mo=$('fMark').checked;
 shown=E.filter(e=>(!q||e.q===q)&&(!L||e.lang===L)&&(!T||e.top===T)&&(!C||e.city===C)&&(!P||e.pr===P)
  &&(!fo||e.fl)&&(!eo||e.educ==='Y')&&(!mo||e.mk)
  &&(!s||(e.ti+' '+e.gl+' '+e.au+' '+e.no+' '+e.pub).toLowerCase().includes(s)));
 $('enCount').textContent='Showing '+(shown.length>400?'first 400 of ':'')+fmt(shown.length)+' of '+fmt(E.length)+' entries'+
  (shown.length?' · '+fmt(shown.reduce((a,e)=>a+e.cop,0))+' copies':'');
 $('enBody').innerHTML=shown.slice(0,400).map((e,i)=>'<tr class="rw" data-i="'+i+'"><td>'+esc(e.q)+'</td><td>'+e.pg+'.'+e.s+
  '</td><td>'+esc(e.lang)+'</td><td>'+esc(e.top)+'</td><td>'+esc(e.ti)+(e.fl?' <span title="flagged" style="color:#8a5a44">⚑</span>':'')+
  (e.mk?' <span title="marginalia (earlier hand)" style="color:#4d6d9a">✎</span>':'')+'</td><td>'+esc(e.au)+'</td><td>'+esc(e.pr)+
  '</td><td>'+(e.cop?fmt(e.cop):'')+'</td><td>'+esc(e.price)+'</td></tr>').join('');
 document.querySelectorAll('#enBody tr').forEach(tr=>tr.onclick=()=>showDetail(shown[+tr.dataset.i]));
}
let curE=null;
function showDetail(e){
 curE=e;
 const F=[['Section',e.sec],['Registration no.',e.reg],['Author',e.au],['Gloss (registrar’s summary)',e.gl],
  ['Publisher',e.pub+(e.pubc?' — '+e.pubc:'')],['Printer',e.pr+(e.city?', '+e.city:'')],['Date',e.dt],
  ['Copies',e.cop?fmt(e.cop):''],['Price',e.price],['Edition',e.ed],['Educational',e.educ],['Periodical',e.per],
  ['Copyright',e.cr],['Extractor notes',e.no],['Marginalia (earlier hand)',e.mk]];
 $('detailBody').innerHTML='<h3>'+esc(e.ti)+'</h3><div class="cite" style="color:#8a5a44;font-size:12.5px">'+qlbl(e.q)+
  ' · printed page '+e.pg+', serial '+e.s+' · PDF page '+e.pdf+'</div>'+
  '<div class="fld" style="margin-top:10px"><button class="srcBtn" onclick="openScan(curE.q,curE.pg)">view scanned page</button>'+
  (QINFO[e.q].pdfurl?'<a class="srcBtn" style="text-decoration:none;display:inline-block" target="_blank" href="'+pdfHref(e.q,e.pdf)+'">open PDF at p.'+e.pdf+'</a>':'')+'</div>'+
  F.filter(([k,v])=>v).map(([k,v])=>'<div class="fld"><b>'+k+'</b>'+esc(v)+'</div>').join('')+
  (e.fl?'<div class="flag"><b>Flagged:</b> '+esc(e.fl)+'</div>':'');
 $('detail').classList.add('on');
}
/* ---------- source viewer ---------- */
function pdfHref(q,pdf){return QINFO[q].pdfurl+'#page='+pdf}
let scanQ=null,scanPg=0;
function scanFile(q,pg){const i=QINFO[q];return 'p'+String(pg).padStart(3,'0')+'_pdf'+(pg+i.off)+'.png'}
function openScan(q,pg){
 scanQ=q;scanPg=pg;const i=QINFO[q],fn=scanFile(q,pg);
 /* packaged PNG, then packaged web-compressed JPEG (how post-1910 quarters are
    deployed to the docs/ site to stay inside the Pages size budget), then repo path */
 const cands=['pages/'+q+'/'+fn,'pages/'+q+'/'+fn.replace('.png','.jpg'),'../../../pipeline/data/'+q+'/pages/'+fn];
 const img=$('scanImg'),msg=$('scanMsg');
 img.style.display='block';msg.style.display='none';img.classList.remove('zoom');
 let k=0;img.onerror=()=>{if(++k<cands.length)img.src=cands[k];
  else{img.style.display='none';msg.style.display='block';
   msg.textContent='Scan image not found. Open this file from the project folder, or rebuild with "python build_site.py --package" to bundle the page images.';}};
 img.src=cands[0];
 $('scanCap').textContent=qlbl(q)+' · printed page '+pg+' · PDF page '+(pg+i.off);
 const pu=QINFO[q].pdfurl,pa=$('scanPdf');
 if(pu){pa.style.display='';pa.href=pu+'#page='+(pg+i.off);}else{pa.style.display='none';}
 $('scan').classList.add('on');
}
function scanNav(d){const i=QINFO[scanQ];const pg=Math.max(i.min,Math.min(i.max,scanPg+d));if(pg!==scanPg)openScan(scanQ,pg)}
function closeScan(){$('scan').classList.remove('on')}
$('scanImg').onclick=()=>$('scanImg').classList.toggle('zoom');
document.addEventListener('keydown',e=>{if(!$('scan').classList.contains('on'))return;
 if(e.key==='ArrowLeft')scanNav(-1);if(e.key==='ArrowRight')scanNav(1);if(e.key==='Escape')closeScan();});
function closeDetail(){$('detail').classList.remove('on')}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeDetail()});
renderTable();
/* ---------- network ---------- */
const NTYPES={
 pp:{legend:[['printer','#8a5a44'],['publisher','#4d6d9a']],
  cap:'Which publishers use which presses. Publishers almost always bind to a single press — presses are the hubs. Self-published entries (a third of the year) are excluded by design; node size = entries in the year.'},
 pl:{legend:[['printer','#8a5a44'],['language','#6a8a5a']],
  cap:'Which presses print which languages. Press multilingualism made visible: the same shops serve the Urdu, Gurmukhi and Nagari markets — capital crosses the script lines that content draws.'},
 xx:{legend:[['printer','#8a5a44']],
  cap:'Presses joined when at least one publisher used both — the cooperation backbone of print capital. Edge thickness = number of shared publishers.'},
 ap:{legend:[['author','#7a5a8a'],['printer','#8a5a44']],
  cap:'Authors and the presses that printed them (raise the slider to see only prolific authors). Reveals house authors, multi-press careers, and the one-press poets of the qissa market.'}};
let net=null;
function initNet(){if(!net){
 /* full-bleed sizing: break out of main's 1200px column so the graph gets the
    whole window (buffer sized 1:1 — no CSS downscaling blur) */
 const cv=$('nwC'),colW=cv.parentElement.clientWidth||1140;
 cv.width=Math.max(colW,Math.min(window.innerWidth-70,1900));
 cv.height=Math.max(640,Math.min(window.innerHeight-250,1050));
 cv.style.maxWidth='none';cv.style.marginLeft=Math.min(0,(colW-cv.width)/2)+'px';
 net=makeNet(cv);
 $('nwMin').oninput=()=>{$('nwMinV').textContent=$('nwMin').value;net.rebuild();};
 $('nwType').onchange=()=>net.rebuild();}}
function makeNet(cv){
 const ctx=cv.getContext('2d');
 let ns=[],es=[],drag=null,pan=null,hover=null,sel=null,raf=null,alpha=0,autofit=true;
 const view={s:1,ox:cv.width/2,oy:cv.height/2};
 const SMIN=0.08,SMAX=12;
 function zoomAt(mx,my,f){autofit=false;
  const wx=(mx-view.ox)/view.s,wy=(my-view.oy)/view.s;
  view.s=Math.max(SMIN,Math.min(SMAX,view.s*f));
  view.ox=mx-wx*view.s;view.oy=my-wy*view.s;draw();}
 const COL={printer:'#8a5a44',publisher:'#4d6d9a',language:'#6a8a5a',author:'#7a5a8a'};
 function agg(type,min){
  const nmap=new Map(),emap=new Map();
  const nd=(id,typ)=>{const k=typ+':'+id;let o=nmap.get(k);
   if(!o){o={id:k,label:id,type:typ,n:0,cop:0};nmap.set(k,o)}return o};
  const ed=(a,b)=>{const k=a<b?a+'|'+b:b+'|'+a;emap.set(k,(emap.get(k)||0)+1)};
  if(type==='xx'){
   const bp=new Map();
   E.forEach(e=>{if(!e.pr||!e.pube)return;
    const p=nd(e.pr,'printer');p.n++;p.cop+=e.cop;
    if(!bp.has(e.pube))bp.set(e.pube,new Set());bp.get(e.pube).add(e.pr);});
   bp.forEach(set=>{const ps=[...set];
    for(let i=0;i<ps.length;i++)for(let j=i+1;j<ps.length;j++)
     ed('printer:'+ps[i],'printer:'+ps[j]);});
  }else{
   E.forEach(e=>{let a=null,b=null;
    if(type==='pp'){if(e.pr&&e.pube){a=nd(e.pr,'printer');b=nd(e.pube,'publisher')}}
    else if(type==='pl'){if(e.pr&&e.lang){a=nd(e.pr,'printer');b=nd(e.lang,'language')}}
    else if(type==='ap'){if(e.pr&&e.au){a=nd(e.au,'author');b=nd(e.pr,'printer')}}
    if(a){a.n++;a.cop+=e.cop}if(b){b.n++;b.cop+=e.cop}
    if(a&&b)ed(a.id,b.id);});
  }
  const keep=new Set();nmap.forEach(o=>{if(o.n>=min)keep.add(o.id)});
  const edges=[];emap.forEach((w,k)=>{const i=k.indexOf('|'),a=k.slice(0,i),b=k.slice(i+1);
   if(keep.has(a)&&keep.has(b))edges.push({a,b,w})});
  const used=new Set();edges.forEach(e=>{used.add(e.a);used.add(e.b)});
  const nodes=[...nmap.values()].filter(o=>used.has(o.id));
  const deg={};edges.forEach(e=>{deg[e.a]=(deg[e.a]||0)+1;deg[e.b]=(deg[e.b]||0)+1});
  nodes.forEach(o=>o.deg=deg[o.id]||0);
  return{nodes,edges};
 }
 function rebuild(){
  const type=$('nwType').value,min=+$('nwMin').value;
  const g=agg(type,min),ix={};
  // sunflower/phyllotaxis seeding: even, non-overlapping, and the spread grows
  // with node count (radius ∝ √i) so dense low-threshold graphs don't start
  // stacked on top of each other and explode on the first step.
  ns=g.nodes.map((o,i)=>{ix[o.id]=i;
   const ang=i*2.3999632,R=28+Math.sqrt(i)*22;
   return{...o,x:Math.cos(ang)*R,y:Math.sin(ang)*R,vx:0,vy:0};});
  es=g.edges.map(e=>({...e,ai:ix[e.a],bi:ix[e.b]}));
  sel=null;hover=null;alpha=1;autofit=true;
  $('nwStats').textContent=ns.length+' nodes · '+es.length+' edges';
  $('nwCap').textContent=NTYPES[type].cap;
  $('nwLegend').innerHTML=NTYPES[type].legend.map(([t,c])=>
   '<span class="dot" style="background:'+c+'"></span>'+t).join('')+
   ' · node size = entries · scroll to zoom, drag background to pan, drag a node to move it, click to highlight';
  loop();
 }
 const r=n=>4+Math.sqrt(n.n)*1.7;
 function step(){
  /* uniform-grid neighbor search: repulsion + collision in ONE local pair pass,
     ~O(n) instead of the old two O(n²) loops — this is what lets the
     min-entries=1 hairball (~2,000 nodes) settle in seconds instead of minutes. */
  const k=alpha,N=ns.length;
  const CUT=N>900?230:500,CUT2=CUT*CUT,CELL=CUT;
  const grid=new Map();
  for(let i=0;i<N;i++){const n=ns[i];
   const kk=Math.floor(n.x/CELL)+':'+Math.floor(n.y/CELL);
   const cl=grid.get(kk);if(cl)cl.push(n);else grid.set(kk,[n]);}
  const NB=[[0,0],[1,0],[0,1],[1,1],[1,-1]];
  grid.forEach((cell,kk)=>{
   const ci=kk.indexOf(':'),cx=+kk.slice(0,ci),cy=+kk.slice(ci+1);
   for(const[ox,oy]of NB){
    const other=(ox||oy)?grid.get((cx+ox)+':'+(cy+oy)):cell;
    if(!other)continue;
    for(let i=0;i<cell.length;i++){const a=cell[i];
     for(let j=(other===cell?i+1:0);j<other.length;j++){const b=other[j];
      let dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy;if(d2<1)d2=1;
      if(d2<CUT2){const f=1500*k/d2;a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f;}
      const d=Math.sqrt(d2),minD=(r(a)+r(b))/Math.max(view.s,0.5)+3;
      if(d<minD){const push=(minD-d)/d*0.45,px=dx*push,py=dy*push;
       if(a!==drag){a.x+=px;a.y+=py}if(b!==drag){b.x-=px;b.y-=py}}
     }}}});
  es.forEach(e=>{const a=ns[e.ai],b=ns[e.bi];
   let dx=b.x-a.x,dy=b.y-a.y;const d=Math.sqrt(dx*dx+dy*dy)||1;
   const rest=60+1.4*(r(a)+r(b));
   const f=(d-rest)/d*0.05*k*Math.min(2,0.5+e.w/2);
   dx*=f;dy*=f;a.vx+=dx;a.vy+=dy;b.vx-=dx;b.vy-=dy;});
  const VMAX=55,BOUND=8000;
  ns.forEach(n=>{n.vx-=n.x*0.006*k;n.vy-=n.y*0.006*k;
   const sp=Math.hypot(n.vx,n.vy);if(sp>VMAX){const s=VMAX/sp;n.vx*=s;n.vy*=s;}
   if(n!==drag){n.x+=n.vx;n.y+=n.vy}n.vx*=0.55;n.vy*=0.55;
   if(!isFinite(n.x)||!isFinite(n.y)){n.x=(Math.random()-0.5)*80;n.y=(Math.random()-0.5)*80;n.vx=n.vy=0;}
   n.x=n.x<-BOUND?-BOUND:n.x>BOUND?BOUND:n.x;n.y=n.y<-BOUND?-BOUND:n.y>BOUND?BOUND:n.y;});
 }
 function fit(){
  if(!ns.length)return false;
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  ns.forEach(n=>{if(n.x<x0)x0=n.x;if(n.x>x1)x1=n.x;if(n.y<y0)y0=n.y;if(n.y>y1)y1=n.y;});
  const pad=70;
  let s=Math.min((cv.width-2*pad)/Math.max(60,x1-x0),(cv.height-2*pad)/Math.max(60,y1-y0));
  s=Math.max(0.06,Math.min(1.2,s));  /* allow fitting the min-entries=1 hairball */
  const cx=(x0+x1)/2,cy=(y0+y1)/2;
  const ds=(s-view.s)*0.12,dox=((cv.width/2-cx*view.s)-view.ox)*0.12,doy=((cv.height/2-cy*view.s)-view.oy)*0.12;
  view.s+=ds;view.ox+=dox;view.oy+=doy;
  return Math.abs(ds)>0.0008||Math.abs(dox)>0.4||Math.abs(doy)>0.4;
 }
 const SX=n=>n.x*view.s+view.ox,SY=n=>n.y*view.s+view.oy;
 function labelCut(){const v=ns.map(n=>n.n).sort((a,b)=>b-a);
  return v[Math.min(21,v.length-1)]||0;}
 function draw(){
  ctx.clearRect(0,0,cv.width,cv.height);
  const nb={};if(sel){es.forEach(e=>{if(e.a===sel.id)nb[e.b]=1;if(e.b===sel.id)nb[e.a]=1});nb[sel.id]=1;}
  es.forEach(e=>{const a=ns[e.ai],b=ns[e.bi];
   const on=sel&&(e.a===sel.id||e.b===sel.id);
   ctx.strokeStyle=on?'rgba(138,90,68,.9)':(sel?'rgba(120,110,90,.05)':'rgba(120,110,90,'+Math.min(.34,.07+e.w*.045)+')');
   ctx.lineWidth=on?1+Math.min(e.w,5):Math.min(1+e.w*.25,3.5);
   ctx.beginPath();ctx.moveTo(SX(a),SY(a));ctx.lineTo(SX(b),SY(b));ctx.stroke();});
  // nodes: fill + a thin background-coloured halo so overlapping dots stay distinct
  // (they read as layered discs instead of merging into one blob when zoomed out).
  ns.forEach(n=>{const dimmed=sel&&!nb[n.id];
   ctx.globalAlpha=dimmed?.12:1;
   const x=SX(n),y=SY(n),rr=r(n),on=(n===hover||n===sel);
   ctx.beginPath();ctx.arc(x,y,rr,0,7);
   ctx.fillStyle=COL[n.type]||'#666';ctx.fill();
   ctx.lineWidth=on?1.8:1.2;ctx.strokeStyle=on?'#2b2620':'#fffdf7';ctx.stroke();
   ctx.globalAlpha=1;});
  // labels: greedy, non-overlapping. Priority = selected/hovered, then biggest nodes.
  // Skipped collisions mean few labels show zoomed-out, more as you zoom in — no stacks.
  const cut=labelCut();
  const cands=ns.filter(n=>!(sel&&!nb[n.id])&&(n===sel||n===hover||n.n>=cut||(sel&&nb[n.id])));
  cands.sort((a,b)=>((b===sel||b===hover)?1e9:b.n)-((a===sel||a===hover)?1e9:a.n));
  ctx.font='11px Georgia';ctx.textBaseline='middle';
  const placed=[];
  for(const n of cands){
   const x=SX(n),y=SY(n),rr=r(n),forced=(n===sel||n===hover);
   const t=n.label.length>26?n.label.slice(0,25)+'…':n.label;
   const w=ctx.measureText(t).width,lx=x+rr+3,box=[lx-1,y-7,lx+w+1,y+7];
   let hit=false;for(const p of placed){if(box[0]<p[2]&&box[2]>p[0]&&box[1]<p[3]&&box[3]>p[1]){hit=true;break;}}
   if(hit&&!forced)continue;
   ctx.lineWidth=3;ctx.strokeStyle='#fffdf7';ctx.strokeText(t,lx,y);   // halo for legibility
   ctx.fillStyle='#2b2620';ctx.fillText(t,lx,y);
   placed.push(box);}
  ctx.textBaseline='alphabetic';
 }
 function loop(){cancelAnimationFrame(raf);
  (function frame(){
   if(alpha>0.02||drag){const reps=ns.length>1200?1:2;for(let i=0;i<reps;i++)step();
    if(!drag)alpha*=(ns.length>900?0.97:0.985);}
   const moving=autofit?fit():false;
   draw();
   raf=(alpha>0.015||drag||moving)?requestAnimationFrame(frame):null;
  })();}
 function world(ev){const b=cv.getBoundingClientRect();
  const mx=(ev.clientX-b.left)*cv.width/b.width,my=(ev.clientY-b.top)*cv.height/b.height;
  return[(mx-view.ox)/view.s,(my-view.oy)/view.s];}
 function at(wx,wy){for(let i=ns.length-1;i>=0;i--){const n=ns[i];
  const dx=wx-n.x,dy=wy-n.y,rr=(r(n)+4)/view.s;
  if(dx*dx+dy*dy<rr*rr)return n;}return null;}
 function cpos(ev){const b=cv.getBoundingClientRect();
  return[(ev.clientX-b.left)*cv.width/b.width,(ev.clientY-b.top)*cv.height/b.height];}
 cv.onmousemove=ev=>{
  if(pan){const[mx,my]=cpos(ev);view.ox=pan.ox+(mx-pan.mx);view.oy=pan.oy+(my-pan.my);
   autofit=false;draw();return;}
  const[wx,wy]=world(ev);
  if(drag){drag.x=wx;drag.y=wy;return;}
  hover=at(wx,wy);cv.style.cursor=hover?'pointer':'grab';
  const t=$('tip');
  if(hover){t.style.display='block';t.style.left=(ev.clientX+14)+'px';t.style.top=(ev.clientY+10)+'px';
   t.innerHTML='<b>'+esc(hover.label)+'</b><br>'+hover.type+' · '+hover.n+' entries · '+
    fmt(hover.cop)+' copies · '+hover.deg+' connections';}
  else t.style.display='none';
  if(!raf)draw();};
 cv.onmousedown=ev=>{const[wx,wy]=world(ev);drag=at(wx,wy);
  if(drag){alpha=Math.max(alpha,0.12);loop();}
  else{const[mx,my]=cpos(ev);pan={mx,my,ox:view.ox,oy:view.oy};cv.style.cursor='grabbing';$('tip').style.display='none';}};
 cv.onmouseup=ev=>{
  if(pan){pan=null;cv.style.cursor='grab';return;}
  if(drag){const[wx,wy]=world(ev);const n=at(wx,wy);
  if(n===drag)sel=(sel===drag?null:drag);
  drag=null;alpha=Math.max(alpha,0.25);loop();}};
 cv.onmouseleave=()=>{$('tip').style.display='none';hover=null;drag=null;pan=null;if(!raf)draw();};
 cv.onwheel=ev=>{ev.preventDefault();const[mx,my]=cpos(ev);
  zoomAt(mx,my,Math.exp(-ev.deltaY*0.0015));};
 $('nwIn').onclick=()=>zoomAt(cv.width/2,cv.height/2,1.35);
 $('nwOut').onclick=()=>zoomAt(cv.width/2,cv.height/2,1/1.35);
 $('nwFit').onclick=()=>{autofit=true;loop();};
 rebuild();return{rebuild};
}
/* ---------- market ---------- */
(function(){
 const M=%%MARKET%%;
 $('mkBody').innerHTML=M.map(t=>'<tr><td>'+esc(t.language)+'</td><td>'+t.entries+'</td><td>'+fmt(t.copies)+
  '</td><td>'+fmt(t.median_run)+'</td><td>'+t.pct_free+'</td><td>'+t.pct_educ+'</td></tr>').join('');
})();
let fundDrawn=false;
function drawFund(){
 if(fundDrawn)return;fundDrawn=true;
 const F=%%FUND%%;/* rows: [quarter,lang,avg] */
 const cv=$('mkC'),ctx=cv.getContext('2d');
 const qs=['Q2','Q3','Q4'],langs=['Hindi','Punjabi','Urdu'],cols={'Hindi':'#4d6d9a','Punjabi':'#8a5a44','Urdu':'#6a8a5a'};
 const max=Math.max(...F.map(r=>r[2]));
 const gw=cv.width/qs.length;
 ctx.font='12px Georgia';
 qs.forEach((q,qi)=>{
  langs.forEach((l,li)=>{
   const row=F.find(r=>r[0]===q&&r[1]===l);if(!row)return;
   const h=(cv.height-70)*row[2]/max,x=qi*gw+40+li*62,y=cv.height-40-h;
   ctx.fillStyle=cols[l];ctx.fillRect(x,y,48,h);
   ctx.fillStyle='#2b2620';ctx.fillText(fmt(Math.round(row[2])),x+2,y-5);
   ctx.fillStyle='#7a7060';ctx.fillText(l.slice(0,4),x+8,cv.height-24);});
  ctx.fillStyle='#2b2620';ctx.font='bold 13px Georgia';
  ctx.fillText(q+' 1910',qi*gw+95,cv.height-6);ctx.font='12px Georgia';});
}
/* ---------- exhibits ---------- */
$('exList').innerHTML=EXH.map((x,i)=>'<div class="ex"><h3>'+esc(x.title)+'</h3><div class="cite">'+esc(x.cite)+
 '</div><p>'+esc(x.blurb)+'</p>'+
 (x.img?'<figure style="margin:2px 0 10px"><img loading="lazy" src="'+esc(x.img)+'" alt="'+esc(x.cap||x.title)+'" style="max-width:100%;display:block;border:1px solid var(--rule);border-radius:6px;background:#fffdf7"><figcaption style="font-size:12px;color:var(--dim);margin-top:5px;line-height:1.4">'+esc(x.cap||'')+'</figcaption></figure>':'')+
 '<button data-s="'+esc(x.search)+'">view the records →</button></div>').join('');
document.querySelectorAll('.ex button').forEach(b=>b.onclick=()=>{
 $('fS').value=b.dataset.s;['fQ','fL','fT','fC','fP'].forEach(id=>$(id).value='');
 ['fFlag','fEduc','fMark'].forEach(id=>$(id).checked=false);renderTable();
 document.querySelector('nav button[data-t=en]').click();});
</script></body></html>
"""

# market table computed live across all years (books only, per D-008 norm_lang);
# replaces the 1910-slice market_by_language.csv so the table covers the corpus
from statistics import median
_mk = {}
for e in entries:
    if e["per"] == "Y":
        continue
    d = _mk.setdefault(e["lang"], {"n": 0, "cop": 0, "runs": [], "free": 0, "educ": 0})
    d["n"] += 1
    d["cop"] += e["cop"]
    if e["cop"]:
        d["runs"].append(e["cop"])
    if (e["price"] or "").strip().lower().startswith("free"):
        d["free"] += 1
    if e["educ"] == "Y":
        d["educ"] += 1
market = [{"language": k, "entries": d["n"], "copies": d["cop"],
           "median_run": int(median(d["runs"])) if d["runs"] else 0,
           "pct_free": f"{round(100 * d['free'] / d['n'])}%",
           "pct_educ": f"{round(100 * d['educ'] / d['n'])}%"}
          for k, d in sorted(_mk.items(), key=lambda kv: -kv[1]["n"])
          if d["n"] >= 2]

fund_avg = []
with open(OUT / "relief_fund_series.csv", encoding="utf-8-sig") as fh:
    rows = [r for r in csv.DictReader(fh) if "Monthly Circular" in r["title"]]
from collections import defaultdict
acc = defaultdict(list)
for r in rows:
    acc[(r["quarter"][-2:].replace("Q", "Q"), r["language"])].append(copies_int(r["copies"]))
for (q, lang), vals in sorted(acc.items()):
    fund_avg.append([f"Q{q[-1]}", lang, sum(vals) / len(vals)])

html = (HTML.replace("%%ENTRIES%%", jdump(entries))
            .replace("%%NODES%%", jdump(nodes))
            .replace("%%EDGES%%", jdump(edges))
            .replace("%%EXHIBITS%%", jdump(EXHIBITS))
            .replace("%%META%%", jdump(META))
            .replace("%%MARKET%%", jdump(market))
            .replace("%%FUND%%", jdump(fund_avg))
            .replace("%%QINFO%%", jdump(QINFO))
            .replace("%%TIMELINE%%", jdump(TIMELINE))
            .replace("%%FLAGGED%%", str(META["flagged"]))
            .replace("%%SELFPUB%%", META["selfpub"])
            .replace("%%NENT%%", f"{len(entries):,}"))

out_file = OUT / "explore_1910_1912.html"
out_file.write_text(html, encoding="utf-8")
print(f"{out_file} written: {len(html)/1024:.0f} KB, {len(entries)} entries, "
      f"{len(nodes)} nodes, {len(edges)} edges")

if "--package" in sys.argv:
    total = 0
    for q in QINFO:
        src = HERE.parent.parent / "pipeline" / "data" / q / "pages"
        dst = OUT / "pages" / q
        dst.mkdir(parents=True, exist_ok=True)
        for png in src.glob("*.png"):
            shutil.copy2(png, dst / png.name)
            total += png.stat().st_size
    print(f"packaged page scans -> {OUT / 'pages'} ({total/1e6:.0f} MB); "
          f"zip the out/ folder to share with scans included")
