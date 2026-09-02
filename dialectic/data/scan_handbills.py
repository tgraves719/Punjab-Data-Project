import fitz, re, os, glob, json, sys, time

VOLS = sorted(glob.glob("Library 1/Batch 6/SV_412_44_*.pdf"))
HB   = re.compile(r"h[a@o]?[nu][dt][\s\-\.]{0,3}b[il1|!]{2,3}", re.I)
COMM = re.compile(r"b[il1|!]{2,3}[\s\-]*comm?[il1|]?tt?ee", re.I)
NUM  = re.compile(r"\bno\.?\s*([0-9]{1,4})", re.I)
COP  = re.compile(r"\b(\d{1,3},\d{3}|\b[1-9]\d{3,5})\b")

out = []
t0 = time.time(); pages = 0
for v in VOLS:
    d = fitz.open(v); vb = os.path.basename(v)
    for i in range(d.page_count):
        try: t = d[i].get_text()
        except Exception: continue
        pages += 1
        if not t: continue
        flat = re.sub(r"[ \t]+", " ", t)
        if not (HB.search(flat) or COMM.search(flat)): continue
        for ln_i, line in enumerate(flat.split("\n")):
            if HB.search(line) or COMM.search(line):
                ctx = " ".join(flat.split("\n")[max(0,ln_i-2):ln_i+3])
                out.append({"vol": vb, "pdfpage": i+1, "line": line.strip()[:180],
                            "ctx": re.sub(r"\s+"," ",ctx)[:420]})
    pc=d.page_count; d.close()
    print(f"scanned {vb:34s} pages={pc:5d} hits so far={len(out)}", flush=True)

json.dump(out, open("hb_hits.json","w"), indent=1)
print(f"\nTOTAL pages scanned: {pages}  hits: {len(out)}  in {time.time()-t0:.0f}s")
