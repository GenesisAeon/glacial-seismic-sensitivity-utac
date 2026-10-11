# P133 preprint (draft for v0.2.1)

`P133_preprint.pdf` is the draft preprint describing glacial-seismic-sensitivity-utac up to
release v0.2.0 plus the exploratory global baseline. Status: **draft, not peer reviewed**.

**Corresponding author:** Johann Benjamin Römer, independent researcher,
Marburger Ring 34 B, 35274 Kirchhain-Großseelheim, Germany.
Email: jbroemer@web.de (primary), joberoemer@gmail.com (secondary).
Certified IT specialist for application development (Fachinformatiker für Anwendungsentwicklung),
background in web design. "MOR collective" is only the informal working name of the
author's collaboration with several AI systems, not a legal entity or institution.

Funding: none (independent, self-funded). Competing interests: none declared.

## Contents

| Path | What |
|---|---|
| `P133_preprint.tex` | LaTeX source (pdflatex + biblatex/biber, author-year) |
| `references.bib` | Generated bibliography (do not edit by hand) |
| `bib/dois.txt` | Citation key -> DOI list (repo `docs/SOURCES.md`, `docs/BASELINE_GLOBAL.md`, plus BH 1995, IAAFT, Turcotte & Schubert) |
| `bib/build_bib.py` | Resolves every DOI via the Crossref API (DataCite as fallback for Zenodo/CORSSA), writes `references.bib` and `bib/doi_verification.csv` |
| `bib/manual.bib` | References without DOI (data services, SPOTL, IERS, SGU report, repository/PyPI) |
| `figures/make_paper_figures.py` | Re-renders figures 1-7 (PDF + PNG) from the CSV files in `results/` only |

## Build

```bash
python paper/figures/make_paper_figures.py   # figures from results/*.csv
python paper/bib/build_bib.py                # needs network (Crossref/DataCite)
cd paper && latexmk -pdf P133_preprint.tex   # or: make
```

## Provenance of numbers

Every number in the text and tables is taken from a file in `results/` (named in the table
and figure captions) or from the repository documents that quote them (`docs/RESULTS.md`,
`docs/BASELINE_GLOBAL.md`, `PREREGISTRATION*.md`, `docs/reviews/REVIEW_RESPONSE_v0.2.md`).
Exploratory analyses are labelled [EXPL], preregistered ones [PREREG].
