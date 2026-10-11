"""Build references.bib from verified DOI metadata (Crossref; DataCite for Zenodo DOIs).

Every DOI in dois.txt is resolved; the metadata used in the bibliography is taken from the
registry response, and doi_verification.csv records title, venue and year as returned.
Entries without a DOI are kept in manual.bib (URL references).
Usage: python paper/bib/build_bib.py
"""

from __future__ import annotations

import csv
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote

import requests

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "glacial-seismic-sensitivity-utac paper build (mailto:joberoemer@gmail.com)"}


def _tex(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)  # strip JATS/MathML tags
    s = unicodedata.normalize("NFC", s.strip())
    s = re.sub(r"\s+", " ", s)
    for a, b in (("&amp;", "\\&"), ("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#")):
        s = s.replace(a, b)
    s = s.replace("\\\\&", "\\&")
    for a, b in (
        ("\u223c", "$\\sim$"),
        ("\u2010", "-"),
        ("\u2011", "-"),
        ("\u2019", "'"),
        ("\u2018", "`"),
        ("\u2013", "--"),
        ("\u2014", "---"),
        ("\u00a0", " "),
    ):
        s = s.replace(a, b)
    return s


def crossref(doi: str) -> dict | None:
    r = requests.get(
        f"https://api.crossref.org/works/{quote(doi, safe='')}", headers=UA, timeout=60
    )
    if r.status_code != 200:
        return None
    m = r.json()["message"]
    year = None
    for k in ("published-print", "published-online", "issued", "published"):
        if m.get(k, {}).get("date-parts"):
            year = m[k]["date-parts"][0][0]
            break
    authors = [
        f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
        if a.get("family")
        else a.get("name", "")
        for a in m.get("author", [])
    ]
    return dict(
        registry="crossref",
        type=m.get("type", ""),
        title=(m.get("title") or [""])[0],
        venue=(m.get("container-title") or [""])[0],
        year=year,
        volume=m.get("volume", ""),
        issue=m.get("issue", ""),
        pages=m.get("page", "") or m.get("article-number", ""),
        publisher=m.get("publisher", ""),
        authors=authors,
    )


def datacite(doi: str) -> dict | None:
    r = requests.get(f"https://api.datacite.org/dois/{quote(doi, safe='')}", headers=UA, timeout=60)
    if r.status_code != 200:
        return None
    a = r.json()["data"]["attributes"]
    authors = []
    for c in a.get("creators", []):
        if c.get("familyName"):
            authors.append(f"{c['familyName']}, {c.get('givenName', '')}".strip(", "))
        else:
            authors.append(c.get("name", ""))
    return dict(
        registry="datacite",
        type="dataset-or-software",
        title=a["titles"][0]["title"],
        venue=a.get("publisher", "")
        if isinstance(a.get("publisher"), str)
        else a["publisher"].get("name", ""),
        year=a.get("publicationYear"),
        volume="",
        issue="",
        pages="",
        publisher=a.get("publisher", "")
        if isinstance(a.get("publisher"), str)
        else a["publisher"].get("name", ""),
        authors=authors,
        version=a.get("version") or "",
    )


def entry(key: str, doi: str, m: dict) -> str:
    auth = " and ".join(_tex(x) for x in m["authors"]) or "{Anonymous}"
    f = {"author": auth, "title": "{" + _tex(m["title"]) + "}", "year": str(m["year"]), "doi": doi}
    t = m["type"]
    if m["registry"] == "datacite":
        kind = "misc"
        f["publisher"] = _tex(m["publisher"])
        f["howpublished"] = _tex(m["publisher"])
        if m.get("version"):
            f["version"] = m["version"]
    elif t == "journal-article":
        kind = "article"
        f["journal"] = _tex(m["venue"])
        for k in ("volume", "issue", "pages"):
            if m[k]:
                f["number" if k == "issue" else k] = str(m[k]).replace("-", "--")
    elif t in ("book", "monograph", "edited-book"):
        kind = "book"
        f["publisher"] = _tex(m["publisher"])
    else:
        kind = "misc"
        f["howpublished"] = _tex(m["venue"] or m["publisher"])
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in f.items())
    return f"@{kind}{{{key},\n{body}\n}}\n"


FIXES = {
    "Kreemer, Corn\ufffd": "Kreemer, Corn\u00e9",
    # DataCite lists the CORSSA authors out of order and without the "van" particle
    "Stiphout, Thomas Van and Marsan, David and Zhuang, Jiancang": (
        "van Stiphout, Thomas and Zhuang, Jiancang and Marsan, David"
    ),
}


def main() -> None:
    rows, out = [], []
    for line in (HERE / "dois.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        key, doi = line.split(maxsplit=1)
        m = datacite(doi) if doi.startswith("10.5281/") else (crossref(doi) or datacite(doi))
        time.sleep(0.2)
        if m is None:
            rows.append(
                dict(key=key, doi=doi, status="NOT FOUND", registry="", title="", venue="", year="")
            )
            continue
        rows.append(
            dict(
                key=key,
                doi=doi,
                status="ok",
                registry=m["registry"],
                title=m["title"],
                venue=m["venue"],
                year=m["year"],
            )
        )
        out.append(entry(key, doi, m))
    manual = (HERE / "manual.bib").read_text(encoding="utf-8")
    header = "% Generated by build_bib.py from Crossref/DataCite metadata; do not edit by hand.\n\n"
    body = "\n".join(out)
    for bad, good in FIXES.items():  # known metadata glitches in the registries
        body = body.replace(bad, good)
    (HERE.parent / "references.bib").write_text(header + body + "\n" + manual, encoding="utf-8")
    with open(HERE / "doi_verification.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    bad = [r for r in rows if r["status"] != "ok"]
    print(
        f"{len(rows) - len(bad)} of {len(rows)} DOIs resolved; missing: {[r['key'] for r in bad]}"
    )


if __name__ == "__main__":
    main()
