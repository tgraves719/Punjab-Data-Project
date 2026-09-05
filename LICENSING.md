# Licensing

This repository holds three different kinds of thing, and one licence cannot sensibly
cover them. What follows is the authoritative statement; `LICENSE` at the root remains the
GPL-3.0 text, which governs the code.

| What | Licence | SPDX |
|---|---|---|
| **Code** — everything in `pipeline/`, `analysis/**/*.py`, and any other executable script | **GNU GPL v3.0 or later** — see [`LICENSE`](LICENSE) | `GPL-3.0-or-later` |
| **Data** — the extraction JSONs, `entries.csv`, the adjudication queues, `aliases.json`, the manifests, and every derived record | **CC0 1.0 Universal** (public domain dedication) — https://creativecommons.org/publicdomain/zero/1.0/ | `CC0-1.0` |
| **Prose** — the memos, `DECISIONS.md`, `PLAN.md`, `OCR_RESEARCH_AGENDA.md`, `README.md`, `dialectic/`, and the results write-ups in `analysis/` | **CC BY 4.0** — https://creativecommons.org/licenses/by/4.0/ | `CC-BY-4.0` |

The published explorer (`docs/index.html`) is a combined work: the code that renders it is
GPL-3.0, the records it embeds are CC0.

The full legal texts are referenced by their canonical URLs rather than transcribed here,
so that what this repository grants is exactly what Creative Commons publishes and cannot
drift from it through a copying error.

## Why the split

**The data is CC0 because most of it is not ours to license.** The underlying catalogue is
a government record published between 1867 and 1942; its text is out of copyright. A
faithful transcription of a public-domain work does not attract a new copyright — it is
precisely the fidelity that the whole project is built on. Asserting rights over the
registrar's own words in order to attach conditions to them would be both legally doubtful
and contrary to the point. Where we have added something ownable — the normalisation
decisions, the schema, the entity resolution — we dedicate it to the public domain too,
because a dataset that scholars must negotiate over is a dataset that goes unused.

**The prose is CC BY because it is genuinely authored.** The decision log, the research
agenda and the results memos are original scholarly writing, and attribution is the
currency they trade in.

**The code stays GPL-3.0** as it has been. It is a research instrument; copyleft keeps
improvements to it visible.

## How to cite

Citation is *requested, not required* — that is what CC0 means, and we would rather be
used than obeyed. `CITATION.cff` at the repository root carries the machine-readable form,
which GitHub renders as a "Cite this repository" button.

If you use the data, please also cite the source record itself (below). And if you find an
error in it, we would be glad to hear about it: the corpus is validated but not certified,
and `analysis/integrity/INTEGRITY_SWEEP.md` lists what we already know is wrong.

## The source material, and one thing still to check

*Catalogue of Books registered in the Punjab under Act XXV of 1867 and Act X of 1890*,
quarterly. British Library, India Office Records **SV 412/44** (Punjab; 26 bound volumes,
1867–1942).

The **text** of these catalogues is a public-domain government record.

The **page images** are a separate question, and an open one. The scans this project works
from came from a British Library digitisation batch, and nothing in this repository records
what terms, if any, attached to their supply. Rendered page images from twelve quarters are
currently published under `docs/pages/` so that every record links back to its source.

> **Open item:** establish how those scans were supplied and under what conditions, and
> adjust `docs/pages/` if required. The extracted *data* is unaffected either way — facts
> transcribed from a public-domain text carry no rights forward — but the republished
> images are a distinct question that should be answered rather than assumed. Until it is,
> treat the images in `docs/pages/` as reproduced for source verification, and consult the
> British Library before redistributing them in bulk.

This is the "neither *it's public domain* nor paralysis" posture set out in
`OCR_RESEARCH_AGENDA.md` §10.4, applied to ourselves.

## Beyond licensing

A licence settles what may legally be done with this material. It does not settle what
ought to be. This dataset names authors, publishers, printers and their cities, drawn from
a print ecology much of which ended up on the wrong side of a partition, and whose
descendants exist. `OCR_RESEARCH_AGENDA.md` §10.4 records the commitment that follows:
document provenance, publish the apparatus alongside the data so the pipeline is as
criticisable as the registrar was, and treat people in Punjab and Pakistan as potential
collaborators rather than as subjects.
