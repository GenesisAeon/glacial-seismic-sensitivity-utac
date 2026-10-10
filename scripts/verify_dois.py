"""Resolve every DOI in constants.ALL_CITATIONS (and docs/SOURCES.md) via the Crossref API and
print the registered title/journal/year so they can be compared with our citation text.

Usage: python scripts/verify_dois.py  (network required)
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import requests

from glacial_seismic_sensitivity_utac.constants import ALL_CITATIONS


def dois() -> list[str]:
    out = [c["doi"] for c in ALL_CITATIONS.values()]
    src = Path(__file__).resolve().parents[1] / "docs" / "SOURCES.md"
    if src.exists():
        out += re.findall(r"doi:\s*(10\.\d{4,9}/[^\s);,]+)", src.read_text(encoding="utf-8"))
    return list(dict.fromkeys(d.rstrip(".") for d in out))


def main() -> int:
    bad = 0
    for d in dois():
        try:
            r = requests.get(
                f"https://api.crossref.org/works/{d}",
                timeout=30,
                headers={"User-Agent": "glacial-seismic-sensitivity-utac doi check"},
            )
            if r.status_code != 200 and d.startswith("10.5281/"):  # Zenodo DOIs live at DataCite
                r2 = requests.get(f"https://api.datacite.org/dois/{d}", timeout=30)
                if r2.status_code == 200:
                    a = r2.json()["data"]["attributes"]
                    print(
                        f"OK   {d}: {a['publicationYear']} | DataCite | {a['titles'][0]['title']}"
                    )
                    continue
            if r.status_code != 200:
                print(f"FAIL {d}: HTTP {r.status_code}")
                bad += 1
                continue
            m = r.json()["message"]
            title = (m.get("title") or [""])[0]
            jour = (m.get("container-title") or [""])[0]
            yr = m.get("issued", {}).get("date-parts", [[None]])[0][0]
            print(f"OK   {d}: {yr} | {jour} | {title[:110]}")
        except Exception as exc:  # pragma: no cover - network
            print(f"ERR  {d}: {exc}")
            bad += 1
        time.sleep(0.3)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
