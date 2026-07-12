"""API extraction backend: one rendered page image -> one JSON file of entries.

Requires ANTHROPIC_API_KEY. Resumable: pages with an existing extraction file
are skipped. The in-session backend (Claude reading pages in Claude Code)
produces identical files; the two can be mixed freely.

Usage: python extract_api.py manifest_1910Q2.json [--model claude-sonnet-5]
"""
import base64, json, pathlib, re, sys

MODEL_DEFAULT = "claude-sonnet-5"

SYSTEM = """You transcribe entries from scanned pages of the British 'Catalogue of
Books registered in the Punjab' (early 20th c.). Output ONLY a JSON array of entry
objects following the schema provided. Transcribe verbatim; never correct or invent.
Flag every uncertain reading in `flags`. If a page has no catalog entries (cover,
blank, title page), output []."""


def main(manifest_path, model=MODEL_DEFAULT):
    import anthropic  # deferred so the rest of the pipeline runs without it

    m = json.load(open(manifest_path))
    data = pathlib.Path(m["data_dir"])
    pages = sorted((data / "pages").glob("p*_pdf*.png"))
    exdir = data / "extractions"
    exdir.mkdir(exist_ok=True)
    schema = (pathlib.Path(__file__).parent / "schema.md").read_text(encoding="utf-8")
    client = anthropic.Anthropic()

    for png in pages:
        printed, pdf_page = map(int, re.match(r"p(\d+)_pdf(\d+)", png.stem).groups())
        out = exdir / f"p{printed:03d}.json"
        if out.exists():
            continue
        img = base64.standard_b64encode(png.read_bytes()).decode()
        msg = client.messages.create(
            model=model,
            max_tokens=8000,
            system=SYSTEM,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
                    {"type": "text", "text": (
                        f"Schema:\n{schema}\n\n"
                        f"Constants for every entry: quarter={m['quarter']}, "
                        f"pdf_page={pdf_page}, printed_page={printed}. "
                        "If the first section on the page is a continuation "
                        "('--concluded' or entries with no header above them), set "
                        "section to the header text if shown, else 'CONTINUATION' "
                        "and leave lang/char/topic empty for postprocess to fill. "
                        "Output the JSON array only.")},
                ],
            }],
        )
        text = msg.content[0].text.strip()
        text = re.sub(r"^```(json)?|```$", "", text, flags=re.M).strip()
        entries = json.loads(text)  # fail loudly; page can be re-run
        out.write_text(json.dumps(entries, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"extracted p{printed}: {len(entries)} entries")


if __name__ == "__main__":
    args = sys.argv[1:]
    model = MODEL_DEFAULT
    if "--model" in args:
        i = args.index("--model")
        model = args[i + 1]
        del args[i:i + 2]
    main(args[0] if args else "manifest_1910Q2.json", model)
