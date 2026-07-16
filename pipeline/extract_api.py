"""API extraction backend: one rendered page image -> one JSON file of entries.

Requires ANTHROPIC_API_KEY. Resumable: pages that already have an extraction file
in the output dir are skipped, so a re-run only fills gaps. The in-session backend
(Claude reading pages in Claude Code) produces identical files; the two mix freely.

Default path is the Batch API (50% cheaper, results keyed by custom_id = "pNNN").
Use --sync for an immediate single-request loop (handy for a 1-page smoke test).

Usage:
  python extract_api.py manifest_1910Q2.json                      # batch, default model
  python extract_api.py manifest_1910Q2.json --model claude-opus-4-8
  python extract_api.py manifest_1910Q2.json --out data/1910Q2/_baked/haiku --model claude-haiku-4-5
  python extract_api.py manifest_1910Q2.json --sync --limit 1     # smoke test, one page

Bake-off note: point --out at a SCRATCH dir (e.g. data/<q>/_baked/<model>). Never
run a model into data/<q>/extractions/ during testing — those are the golden files,
and because existing pages are skipped it would extract nothing and look "done".

The output dir also gets _usage.json (token totals) so bakeoff scoring can price runs.
"""
import base64, json, pathlib, re, sys, time

MODEL_DEFAULT = "claude-sonnet-5"
MAX_TOKENS = 8000

SYSTEM = """You transcribe entries from scanned pages of the British 'Catalogue of
Books registered in the Punjab' (early 20th c.). Output ONLY a JSON array of entry
objects following the schema below. Transcribe verbatim; never correct or invent.
Flag every uncertain reading in `flags`. If a page has no catalog entries (cover,
blank, title page), output []."""

# Schema is appended to the system prompt (a stable prefix across every page) with a
# cache breakpoint, so only the per-page image is uncached. The shared prefix is small,
# so cache savings are modest and may fall below a model's minimum-cacheable size
# (Opus 4.8 / Haiku 4.5: 4096 tokens; Sonnet 5: 2048) — in which case it silently
# won't cache. That's fine; output tokens dominate cost here regardless.


def _build_system():
    schema = (pathlib.Path(__file__).parent / "schema.md").read_text(encoding="utf-8")
    return [{
        "type": "text",
        "text": SYSTEM + "\n\nSCHEMA:\n" + schema,
        "cache_control": {"type": "ephemeral"},
    }]


def _user_content(png_b64, quarter, pdf_page, printed):
    return [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": png_b64}},
        {"type": "text", "text": (
            f"Constants for every entry: quarter={quarter}, pdf_page={pdf_page}, "
            f"printed_page={printed}. If the first section on the page is a continuation "
            "('--concluded' or entries with no header above them), set section to the "
            "header text if shown, else 'CONTINUATION' and leave lang/char/topic empty "
            "for postprocess to fill. Output the JSON array only.")},
    ]


def _text_of(msg):
    """First text block. Robust to a leading thinking block (we disable thinking, but
    a model could still emit one under adaptive defaults)."""
    return next(b.text for b in msg.content if b.type == "text")


def _parse(text):
    text = text.strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.M).strip()
    return json.loads(text)  # fail loudly; the page can be re-run


def _pending_pages(m, exdir):
    """(png_path, printed, pdf_page) for pages that still need extracting."""
    data = pathlib.Path(m["data_dir"])
    out = []
    for png in sorted((data / "pages").glob("p*_pdf*.png")):
        printed, pdf_page = map(int, re.match(r"p(\d+)_pdf(\d+)", png.stem).groups())
        if not (exdir / f"p{printed:03d}.json").exists():
            out.append((png, printed, pdf_page))
    return out


def _add_usage(totals, usage):
    for k in ("input_tokens", "output_tokens",
              "cache_creation_input_tokens", "cache_read_input_tokens"):
        totals[k] = totals.get(k, 0) + (getattr(usage, k, 0) or 0)


def _write_usage(exdir, model, totals, n_pages):
    (exdir / "_usage.json").write_text(
        json.dumps({"model": model, "pages": n_pages, "batch": True, **totals}, indent=1),
        encoding="utf-8")


def run_batch(manifest_path, model, out_dir):
    import anthropic
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    m = json.load(open(manifest_path))
    exdir = pathlib.Path(out_dir) if out_dir else pathlib.Path(m["data_dir"]) / "extractions"
    exdir.mkdir(parents=True, exist_ok=True)
    pending = _pending_pages(m, exdir)
    if not pending:
        print("nothing to do — all pages already extracted in", exdir)
        return
    print(f"{len(pending)} pages -> Batch API ({model})")

    system = _build_system()
    requests = []
    for png, printed, pdf_page in pending:
        img = base64.standard_b64encode(png.read_bytes()).decode()
        requests.append(Request(
            custom_id=f"p{printed:03d}",
            params=MessageCreateParamsNonStreaming(
                model=model, max_tokens=MAX_TOKENS,
                thinking={"type": "disabled"},
                system=system,
                messages=[{"role": "user", "content": _user_content(img, m["quarter"], pdf_page, printed)}],
            ),
        ))

    client = anthropic.Anthropic()
    batch = client.messages.batches.create(requests=requests)
    print("batch", batch.id, "submitted; polling…")
    while True:
        b = client.messages.batches.retrieve(batch.id)
        if b.processing_status == "ended":
            break
        print(f"  {b.processing_status}: processing={b.request_counts.processing}")
        time.sleep(20)

    totals, ok, errs = {}, 0, 0
    for r in client.messages.batches.results(batch.id):
        pid = r.custom_id
        if r.result.type != "succeeded":
            errs += 1
            print(f"  {pid}: {r.result.type} — left unwritten, re-run to retry")
            continue
        msg = r.result.message
        entries = _parse(_text_of(msg))
        (exdir / f"{pid}.json").write_text(
            json.dumps(entries, indent=1, ensure_ascii=False), encoding="utf-8")
        _add_usage(totals, msg.usage)
        ok += 1
        print(f"  {pid}: {len(entries)} entries")
    _write_usage(exdir, model, totals, ok)
    print(f"done: {ok} pages written, {errs} errored -> {exdir}")


def run_sync(manifest_path, model, out_dir, limit=None):
    import anthropic
    m = json.load(open(manifest_path))
    exdir = pathlib.Path(out_dir) if out_dir else pathlib.Path(m["data_dir"]) / "extractions"
    exdir.mkdir(parents=True, exist_ok=True)
    pending = _pending_pages(m, exdir)
    if limit:
        pending = pending[:limit]
    system = _build_system()
    client = anthropic.Anthropic()
    totals, ok = {}, 0
    for png, printed, pdf_page in pending:
        img = base64.standard_b64encode(png.read_bytes()).decode()
        msg = client.messages.create(
            model=model, max_tokens=MAX_TOKENS,
            thinking={"type": "disabled"},
            system=system,
            messages=[{"role": "user", "content": _user_content(img, m["quarter"], pdf_page, printed)}],
        )
        entries = _parse(_text_of(msg))
        (exdir / f"p{printed:03d}.json").write_text(
            json.dumps(entries, indent=1, ensure_ascii=False), encoding="utf-8")
        _add_usage(totals, msg.usage)
        ok += 1
        print(f"p{printed}: {len(entries)} entries")
    totals_out = {"model": model, "pages": ok, "batch": False, **totals}
    (exdir / "_usage.json").write_text(json.dumps(totals_out, indent=1), encoding="utf-8")
    print(f"done: {ok} pages -> {exdir}")


def _flag(args, name, has_value=True):
    if name not in args:
        return None
    i = args.index(name)
    if has_value:
        val = args[i + 1]
        del args[i:i + 2]
        return val
    del args[i]
    return True


if __name__ == "__main__":
    args = sys.argv[1:]
    model = _flag(args, "--model") or MODEL_DEFAULT
    out_dir = _flag(args, "--out")
    limit = _flag(args, "--limit")
    sync = _flag(args, "--sync", has_value=False)
    manifest = args[0] if args else "manifest_1910Q2.json"
    if sync:
        run_sync(manifest, model, out_dir, int(limit) if limit else None)
    else:
        run_batch(manifest, model, out_dir)
