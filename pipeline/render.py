"""Render a quarter's PDF pages to grayscale PNGs per the manifest."""
import json, sys, pathlib
import fitz


def main(manifest_path):
    m = json.load(open(manifest_path))
    outdir = pathlib.Path(m["data_dir"]) / "pages"
    outdir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(m["volume_pdf"])
    lo, hi = m["pdf_pages"]
    off = m["printed_page_offset"]
    for i in range(lo, hi + 1):
        printed = i + off
        out = outdir / f"p{printed:03d}_pdf{i}.png"
        if out.exists():
            continue
        pix = doc[i].get_pixmap(dpi=m["dpi"], colorspace=fitz.csGRAY)
        pix.save(str(out))
        print(f"rendered printed p{printed} (pdf {i}) -> {out.name}")
    print("done")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "manifest_1910Q2.json")
