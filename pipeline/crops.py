"""Native-resolution crop extraction for the Registrar of Books catalogs.

The catalog page is a ruled six-column table. Column 1 holds nothing but the
entry's serial number, so the serial blobs give us a reliable vertical anchor
for every entry on the page. Column 2 holds the entry body, whose *first* line
begins with the native-script title (optionally preceded by "Author, B.—") and
is followed by "[ Romanization. English gloss.]".

This module locates those regions and cuts them at the scan's native
resolution, rather than the 140 DPI used for whole-page VLM extraction.

Geometry is derived from the page itself (rules, ink) — nothing is hardcoded to
a particular quarter. All coordinates are in pixels of the rendered page at the
requested DPI, after deskew.

Usage
-----
    from crops import Page
    pg = Page.render(pdf_path, pdf_page=83, dpi=306)
    for e in pg.entries():
        e.strip_image().save(f"{e.serial}.png")   # serial + first line of col 2
        e.native_image().save(f"{e.serial}_nat.png")  # up to the '[' only
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import sys

import numpy as np
from PIL import Image

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None

from scipy import ndimage

NATIVE_DPI_DEFAULT = 306


# --------------------------------------------------------------------------
# thresholding / deskew
# --------------------------------------------------------------------------

def otsu(gray: np.ndarray) -> int:
    """Otsu threshold for a uint8 grayscale array."""
    hist = np.bincount(gray.ravel(), minlength=256).astype(float)
    total = hist.sum()
    csum = np.cumsum(hist)
    msum = np.cumsum(hist * np.arange(256))
    best_t, best_v = 128, -1.0
    for t in range(1, 255):
        wb = csum[t]
        wf = total - wb
        if wb == 0 or wf == 0:
            continue
        mb = msum[t] / wb
        mf = (msum[-1] - msum[t]) / wf
        v = wb * wf * (mb - mf) ** 2
        if v > best_v:
            best_t, best_v = t, v
    return best_t


def estimate_skew(ink: np.ndarray, limit: float = 1.2, step: float = 0.05) -> float:
    """Skew angle in degrees that maximises row-projection sharpness.

    Text lines and rules both align when the page is level, so the variance of
    the row sums peaks at the correct angle. Search is coarse-to-fine on a
    downsampled copy — the answer only needs to be good to ~0.02 deg.
    """
    small = ink[::3, ::3].astype(np.float32)

    def sharpness(angle: float) -> float:
        rot = ndimage.rotate(small, angle, reshape=False, order=0, mode="constant")
        prof = rot.sum(axis=1)
        return float(np.var(np.diff(prof)))

    coarse = np.arange(-limit, limit + 1e-9, step * 4)
    best = max(coarse, key=sharpness)
    fine = np.arange(best - step * 4, best + step * 4 + 1e-9, step)
    return float(max(fine, key=sharpness))


def deskew(gray: np.ndarray, angle: float) -> np.ndarray:
    if abs(angle) < 0.01:
        return gray
    return ndimage.rotate(gray, angle, reshape=False, order=1,
                          mode="constant", cval=255).astype(np.uint8)


# --------------------------------------------------------------------------
# page geometry
# --------------------------------------------------------------------------

def _runs(idx: np.ndarray, gap: int = 3) -> list[tuple[int, int]]:
    """Group a sorted index array into (start, end) runs, merging gaps <= gap."""
    out: list[list[int]] = []
    for i in idx:
        if out and i - out[-1][-1] <= gap:
            out[-1].append(int(i))
        else:
            out.append([int(i)])
    return [(g[0], g[-1]) for g in out]


@dataclasses.dataclass
class Geometry:
    """Rules and column boundaries, in deskewed page pixels.

    Which rules survive a scan varies from page to page — some pages lose the
    left border, others the right — so columns are identified by structure
    rather than by position in the detected list. Column 2 (the entry body) is
    by far the widest cell and is unmistakable; everything else is located
    relative to it.
    """
    h_rules: list[tuple[int, int]]
    v_rules: list[tuple[int, int]]
    body_top: int
    body_bottom: int
    columns: list[tuple[int, int]]
    col1: tuple[int, int]
    col2: tuple[int, int]
    col5: tuple[int, int]
    scale: float


def _vertical_rule_peaks(band: np.ndarray, prominence: float = 0.22) -> list[int]:
    """x positions of vertical rules inside a table band.

    These volumes are bound and slightly warped, so a rule drifts a few pixels
    across the page height and an absolute column-sum threshold misses it. A
    small horizontal dilation absorbs the drift; the rules then stand out as
    sharp peaks above a local background of ordinary text density, which is what
    we detect rather than an absolute level.
    """
    from scipy import signal

    dil = ndimage.maximum_filter1d(band, size=7, axis=1)
    col = dil.sum(axis=0) / max(1, band.shape[0])
    bg = ndimage.median_filter(col, size=121)
    peaks, _ = signal.find_peaks(col - bg, prominence=prominence, distance=20)
    return [int(p) for p in peaks]


def _horizontal_rule_peaks(band: np.ndarray, min_fill: float = 0.72) -> list[int]:
    """y positions of horizontal rules within the table's x-range.

    Same warp problem as the vertical rules, same remedy. The separation is
    clean once the profile is measured across the table only: a rule fills
    0.85-1.0 of the span, while the densest line of type reaches about 0.6.
    """
    from scipy import signal

    dil = ndimage.maximum_filter1d(band, size=7, axis=0)
    row = dil.sum(axis=1) / max(1, band.shape[1])
    bg = ndimage.median_filter(row, size=121)
    peaks, _ = signal.find_peaks(row - bg, prominence=0.25, distance=15)
    return [int(p) for p in peaks if row[p] >= min_fill]


@dataclasses.dataclass
class Calibration:
    """Layout constants shared by every page of a quarter.

    Per-page rule detection is not reliable on its own: these volumes are bound
    and warped, rules break up, the left border is cropped away on some pages
    and the right on others, and bleed-through invents rules that are not there.
    But the *layout* is a printed constant within a quarter, so the robust
    procedure is to measure it once across many pages and then fit each page to
    it, repairing whatever that page's scan lost. Only two things need to be
    found per page: where the table starts vertically, and where column 2 is.
    """
    dpi: int
    body_delta: float          # (body_top - table top rule), in units of column-3 width
    scale: float = 1.0         # body_delta is already scale-normalised
    n_pages: int = 0

    def to_json(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, d: dict) -> "Calibration":
        return cls(**d)


def _raw_rules(ink: np.ndarray) -> tuple[list[int], list[int]]:
    h, _ = ink.shape
    xs = _vertical_rule_peaks(ink[int(0.10 * h):int(0.97 * h)])
    if len(xs) < 2:
        return [], []
    ys = _horizontal_rule_peaks(ink[:, min(xs):max(xs)])
    return sorted(xs), ys


def calibrate(pages: list[np.ndarray], dpi: int) -> Calibration:
    """Measure the height of the column-heading block across a quarter's pages.

    This is the one landmark the ratio signature cannot supply, because it is
    vertical. The rule closing the headings is missed on a fair number of pages;
    measured as a multiple of column-3 width on the pages where it *is* found,
    it transfers to the pages where it is not.
    """
    deltas = []
    for ink in pages:
        xs, ys = _raw_rules(ink)
        if len(xs) < 4 or len(ys) < 2:
            continue
        try:
            *_, scale = _find_interior_block(sorted(xs))
        except ValueError:
            continue
        top = [y for y in ys if y < 0.40 * ink.shape[0]]
        if len(top) >= 2:
            deltas.append((max(top) - min(ys)) / scale)
    if not deltas:
        raise ValueError("calibration failed: no page yielded a heading block")
    return Calibration(dpi=dpi, body_delta=float(np.median(deltas)), n_pages=len(deltas))


# Printed proportions of the six-column form, expressed relative to column 3
# (printer and place of printing). The scans differ in magnification by several
# percent from page to page, so the layout is matched by ratio, never by pixels.
_C3 = 1.0
_RATIO_C4 = 0.348      # number of copies
_RATIO_C5 = 0.348      # registration number
_RATIO_C2 = 3.45       # entry body
_RATIO_C1 = 0.31       # serial number


def _find_interior_block(xs: list[int]) -> tuple[int, int, int, int, float]:
    """Locate the rules bounding columns 3, 4 and 5.

    Columns 3-5 have a distinctive width signature — one wide cell followed by
    two narrow ones of equal width — that survives any change of magnification
    when read as ratios. Matching it identifies each rule's role in the form,
    which indexing the detected rules positionally cannot do: some pages lose
    the left border, others the right, and bleed-through adds rules that were
    never printed.
    """
    best, best_err = None, float("inf")
    for i in range(len(xs) - 3):
        g1, g2, g3 = xs[i + 1] - xs[i], xs[i + 2] - xs[i + 1], xs[i + 3] - xs[i + 2]
        if g1 <= 0 or g2 <= 0 or g3 <= 0:
            continue
        err = abs(g2 / g1 - _RATIO_C4) + abs(g3 / g1 - _RATIO_C5)
        if err < best_err:
            best, best_err = (xs[i], xs[i + 1], xs[i + 2], xs[i + 3], float(g1)), err
    if best is None or best_err > 0.16:
        raise ValueError(f"interior column block not found (best ratio error {best_err:.3f})")
    return best


def find_geometry(ink: np.ndarray, calib: Calibration | None = None) -> Geometry:
    h, w = ink.shape
    xs, ys = _raw_rules(ink)
    if len(xs) < 4:
        raise ValueError(f"only {len(xs)} vertical rules found")
    if not ys:
        raise ValueError("no horizontal rules found — is this a catalog page?")

    r23, r34, r45, r56, scale = _find_interior_block(xs)
    col5 = (r45 + 3, r56 - 3)

    # Column 2 ends at the rule opening the interior block. Its left rule is
    # used when the scan kept it, and inferred from the form's proportions when
    # it did not.
    left = [x for x in xs if x < r23 - 0.5 * scale]
    if left and abs((r23 - left[-1]) / scale - _RATIO_C2) < 0.25:
        r12 = left[-1]
    else:
        r12 = int(r23 - _RATIO_C2 * scale)
    col2 = (r12 + 3, r23 - 3)
    col1 = (max(0, int(r12 - _RATIO_C1 * scale)), r12 - 3)

    # The body starts below the column-heading block. The table's top rule is
    # the most reliable landmark on the page, so measure down from it.
    if calib is not None and calib.body_delta:
        body_top = int(min(ys) + calib.body_delta * scale)
    else:
        top = [y for y in ys if y < 0.40 * h]
        body_top = max(top) if top else ys[0]

    # The rule closing the table at the foot is often broken or cropped away, so
    # take the body's bottom from the interior block's own ink extent.
    band = ink[body_top:]
    refcol = band[:, max(0, r23 - 3):r23 + 4].max(axis=1)
    on = np.where(refcol)[0]
    body_bottom = body_top + (int(on.max()) if len(on) else band.shape[0] - 1)

    v_rules = [(x - 2, x + 2) for x in xs]
    columns = [(p + 1, q - 1) for (_, p), (q, _) in zip(v_rules, v_rules[1:])]
    h_rules = [(y - 2, y + 2) for y in ys]
    return Geometry(h_rules, v_rules, body_top, body_bottom, columns,
                    col1, col2, col5, scale)


# --------------------------------------------------------------------------
# entry anchors and strips
# --------------------------------------------------------------------------

@dataclasses.dataclass
class Entry:
    """One catalog entry located on the page."""
    page: "Page"
    index: int
    y_top: int
    y_bottom: int
    serial_box: tuple[int, int, int, int]  # x0, y0, x1, y1 of the serial blob
    line_top: int
    line_bottom: int
    bracket_x: int | None

    @property
    def serial_height(self) -> int:
        return self.serial_box[3] - self.serial_box[1]

    def strip_box(self, pad: int = 6) -> tuple[int, int, int, int]:
        """The entry's first line, across the whole of column 2.

        This is the line that carries the native-script title followed by its
        bracketed romanization and English gloss.
        """
        c2a, c2b = self.page.geom.col2
        return (max(0, c2a - pad), max(0, self.line_top - pad),
                min(self.page.gray.shape[1], c2b + pad), self.line_bottom + pad)

    def native_box(self, pad: int = 6) -> tuple[int, int, int, int] | None:
        """Column 2, from its left edge up to the opening '[' of the gloss.

        This is the region that contains the native-script title (and, when the
        entry is author-first, the author's name before the em dash). Returns
        None when no bracket was located on the first line.
        """
        if self.bracket_x is None:
            return None
        c2a, _ = self.page.geom.col2
        return (c2a, max(0, self.line_top - pad),
                self.bracket_x, self.line_bottom + pad)

    def _crop(self, box, scale=1):
        img = Image.fromarray(self.page.gray).crop(box)
        if scale != 1:
            img = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
        return img

    def strip_image(self, scale: int = 1) -> Image.Image:
        return self._crop(self.strip_box(), scale)

    def native_image(self, scale: int = 1) -> Image.Image | None:
        box = self.native_box()
        return None if box is None else self._crop(box, scale)


def render_gray(pdf_path, pdf_page: int, dpi: int) -> tuple[np.ndarray, float]:
    """Render one page to a deskewed grayscale array."""
    if fitz is None:
        raise RuntimeError("PyMuPDF (fitz) is required to render pages")
    doc = fitz.open(str(pdf_path))
    pix = doc[pdf_page].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    gray = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).copy()
    doc.close()
    angle = estimate_skew((gray < otsu(gray)).astype(np.uint8))
    return deskew(gray, angle), angle


class Page:
    def __init__(self, gray: np.ndarray, threshold: int, skew: float,
                 meta: dict | None = None, calib: Calibration | None = None):
        self.gray = gray
        self.threshold = threshold
        self.skew = skew
        self.meta = meta or {}
        self.ink = (gray < threshold).astype(np.uint8)
        self.geom = find_geometry(self.ink, calib)
        self._entries: list[Entry] | None = None

    # -- construction -------------------------------------------------------

    @classmethod
    def render(cls, pdf_path, pdf_page: int, dpi: int = NATIVE_DPI_DEFAULT,
               calib: Calibration | None = None) -> "Page":
        gray, angle = render_gray(pdf_path, pdf_page, dpi)
        return cls(gray, otsu(gray), angle,
                   {"pdf": str(pdf_path), "pdf_page": pdf_page, "dpi": dpi}, calib)

    @staticmethod
    def calibrate_quarter(pdf_path, pdf_pages, dpi: int = NATIVE_DPI_DEFAULT,
                          sample: int = 12) -> Calibration:
        step = max(1, len(pdf_pages) // sample)
        inks = []
        for p in list(pdf_pages)[::step][:sample]:
            gray, _ = render_gray(pdf_path, p, dpi)
            inks.append((gray < otsu(gray)).astype(np.uint8))
        return calibrate(inks, dpi)

    # -- entry detection ----------------------------------------------------

    def entries(self) -> list[Entry]:
        if self._entries is None:
            self._entries = self._find_entries()
        return self._entries

    def _find_entries(self) -> list[Entry]:
        """Locate entries by their registration numbers.

        Column 5 is the anchor rather than column 1. Both hold nothing but
        digits on the entry's first line, but column 1 sits against the page
        edge and collects everything the margin holds — the earlier hand's
        pencil crosses and running numerals, gutter shadow, the border rule —
        while column 5 is interior and clean. Registration numbers are also
        printed on 100% of entries, and known independently from the register,
        so the alignment can be checked afterwards.
        """
        g = self.geom
        x0, x1 = g.col5
        band = self.ink[g.body_top:g.body_bottom, x0 + 2:x1 - 2]
        if band.size == 0:
            return []

        lbl, n = ndimage.label(band)
        if n == 0:
            return []
        objs = ndimage.find_objects(lbl)

        # Serial numerals: filter out speckle and the marginal pencil strokes
        # that cross into column 1.
        heights = []
        boxes = []
        for sl_y, sl_x in objs:
            h = sl_y.stop - sl_y.start
            w = sl_x.stop - sl_x.start
            if h < 6 or w < 3:
                continue
            if h > 0.06 * band.shape[0]:      # long pencil strokes, rules
                continue
            heights.append(h)
            boxes.append((sl_x.start + x0 + 2, sl_y.start + g.body_top,
                          sl_x.stop + x0 + 2, sl_y.stop + g.body_top))
        if not boxes:
            return []

        med = float(np.median(heights))
        boxes = [b for b, h in zip(boxes, heights) if 0.55 * med <= h <= 1.9 * med]
        boxes.sort(key=lambda b: (b[1], b[0]))

        # Digits of one serial share a line: merge boxes whose vertical spans
        # overlap substantially.
        groups: list[list[tuple[int, int, int, int]]] = []
        for b in boxes:
            if groups:
                gy0 = min(x[1] for x in groups[-1])
                gy1 = max(x[3] for x in groups[-1])
                overlap = min(gy1, b[3]) - max(gy0, b[1])
                if overlap > 0.45 * min(gy1 - gy0, b[3] - b[1]):
                    groups[-1].append(b)
                    continue
            groups.append([b])

        # A registration number is one to four numerals. This rejects rule
        # fragments and the stray marks that survive the height filter.
        col_width = x1 - x0
        merged = []
        for gp in groups:
            if len(gp) > 4:
                continue
            bx = (min(x[0] for x in gp), min(x[1] for x in gp),
                  max(x[2] for x in gp), max(x[3] for x in gp))
            bw, bh = bx[2] - bx[0], bx[3] - bx[1]
            if bw > 0.92 * col_width or bw > 5 * bh:
                continue
            merged.append(bx)

        entries = []
        for i, box in enumerate(merged):
            y_top = box[1]
            y_bot = merged[i + 1][1] - 1 if i + 1 < len(merged) else self.geom.body_bottom
            line_top, line_bottom = self._first_line_bounds(box)
            entries.append(Entry(self, i, y_top, y_bot, box, line_top, line_bottom,
                                 bracket_x=None))
        for e in entries:
            e.bracket_x = self._find_bracket(e)
        return entries

    def _first_line_bounds(self, serial_box) -> tuple[int, int]:
        """Vertical extent of the text line in column 2 beside a serial."""
        c2a, c2b = self.geom.col2
        y0 = max(self.geom.body_top, serial_box[1] - 18)
        y1 = min(self.geom.body_bottom, serial_box[3] + 18)
        rows = self.ink[y0:y1, c2a + 2:c2b - 2].sum(axis=1)
        if rows.size == 0 or rows.max() == 0:
            return serial_box[1], serial_box[3]
        on = rows > max(2.0, 0.04 * rows.max())
        idx = np.where(on)[0]
        if idx.size == 0:
            return serial_box[1], serial_box[3]
        # Keep the run that overlaps the serial's own vertical centre.
        centre = (serial_box[1] + serial_box[3]) // 2 - y0
        for a, b in _runs(idx, gap=4):
            if a - 6 <= centre <= b + 6:
                return y0 + a, y0 + b
        return y0 + idx.min(), y0 + idx.max()

    def _find_bracket(self, e: Entry) -> int | None:
        """x where the romanization begins — the opening '[' of the gloss.

        Hunting the bracket glyph directly does not work: a tall narrow stroke
        with a solid left edge is also alif, lam and kaf in the Perso-Arabic
        titles, and the vowel signs in the Gurmukhi ones.

        What does work is to use the catalog's Latin fount as a reference frame.
        The roman type is metal-set and utterly regular — nearly every component
        rests on a common baseline and stands within a common x-height — while
        the native-script titles violate both: Perso-Arabic hangs dots and tails
        below the baseline, Gurmukhi carries its headline and vowel signs above.
        So the native span is found as the run of components that do *not*
        conform to the Latin frame, and the bracket is then identified within
        that much smaller candidate set by its serifs.
        """
        c2a, c2b = self.geom.col2
        y0, y1 = e.line_top, e.line_bottom + 1
        if y1 - y0 < 8:
            return None
        band = self.ink[y0:y1, c2a:c2b]
        lbl, n = ndimage.label(band)
        if n == 0:
            return None

        comps = []
        for sl_y, sl_x in ndimage.find_objects(lbl):
            h, w = sl_y.stop - sl_y.start, sl_x.stop - sl_x.start
            if h < 3 or w < 2:
                continue
            comps.append((sl_x.start, sl_x.stop, sl_y, sl_x))
        if len(comps) < 4:
            return None
        comps.sort()

        lh = y1 - y0
        prev_right = 0
        for x_start, x_stop, sl_y, sl_x in comps:
            gap = x_start - prev_right
            prev_right = max(prev_right, x_stop)
            sub = band[sl_y, sl_x]
            h, w = sub.shape
            # Proportions of '[': as tall as the line's type, a third as wide.
            if not (0.55 * lh <= h <= 1.15 * lh):
                continue
            if not (0.18 * lh <= w <= 0.40 * lh):
                continue
            # A solid left column is what actually separates the bracket from
            # every letter in this fount — measured over a page, no roman glyph
            # exceeds 0.43 here while the bracket reaches 0.97. Requiring the
            # right column to be open excludes ']'.
            if sub[:, 0].mean() < 0.75 or sub[:, -1].mean() > 0.5:
                continue
            # At least one serif must show; the lower one is often faded.
            k = max(1, h // 5)
            top = sub[:k].sum(axis=1).mean()
            bot = sub[-k:].sum(axis=1).mean()
            mid = sub[k:-k].sum(axis=1).mean() if h > 2 * k else top
            if mid <= 0 or max(top, bot) < 1.3 * mid:
                continue
            # The catalog sets a space before the bracket. Perso-Arabic letters
            # that pass the shape tests — kaf above all — sit inside a word and
            # have no such gap, so this is what keeps the crop from being cut
            # through the middle of the title.
            if gap < 0.30 * lh:
                continue
            return x_start + c2a
        return None

    # -- debug --------------------------------------------------------------

    def overlay(self, path) -> None:
        """Write a visual check of the detected geometry and entries."""
        from PIL import ImageDraw
        img = Image.fromarray(self.gray).convert("RGB")
        d = ImageDraw.Draw(img)
        for a, b in self.geom.v_rules:
            d.rectangle([a, self.geom.body_top, b, self.geom.body_bottom],
                        outline=(0, 160, 255), width=3)
        for e in self.entries():
            d.rectangle(e.serial_box, outline=(255, 0, 0), width=3)
            d.rectangle(e.strip_box(), outline=(0, 200, 0), width=3)
            nb = e.native_box()
            if nb:
                d.rectangle(nb, outline=(255, 0, 255), width=4)
        img.save(path)


# --------------------------------------------------------------------------

def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    pdf, page = argv[1], int(argv[2])
    dpi = int(argv[3]) if len(argv) > 3 else NATIVE_DPI_DEFAULT
    pg = Page.render(pdf, page, dpi)
    print(json.dumps({
        "skew_deg": round(pg.skew, 3),
        "threshold": pg.threshold,
        "columns": pg.geom.columns,
        "body": [pg.geom.body_top, pg.geom.body_bottom],
        "entries": len(pg.entries()),
        "with_bracket": sum(1 for e in pg.entries() if e.bracket_x),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
