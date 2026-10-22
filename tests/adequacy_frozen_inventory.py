"""Inventory of every frozen file the adequacy module must never change (AP0 guard).

Collected from the frozen documents themselves, so the list cannot drift from the preregistration:

* ``results/frozen_v02_preregistration.json`` -> ``v01_frozen_files_sha256``
* ``results/frozen_v02_addendum_2026-10-10.json`` -> ``amends_files_sha256_unchanged``
* ``results/frozen_v03_preregistration.json`` -> ``sha256_frozen_v01_v02``,
  ``sha256_v03_artefacts``, ``sha256_code``
* the two v0.2 code files bound to tag v0.2.0 by addendum A4.6 (hashes of the tag's blobs)

Line endings: the frozen JSON/preregistration files are checked out byte-exactly (``-text`` in
.gitattributes). Other frozen files (v0.3 artefacts, code) get CRLF on a Windows autocrlf checkout,
so a file passes if its raw bytes *or* its LF-normalised bytes match. A CRLF<->LF conversion is
not a content change; any other edit fails.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: sha256 of the git blobs at tag v0.2.0 (addendum A4.6: the code of release v0.2.0 is binding)
V020_CODE_SHA256 = {
    "src/glacial_seismic_sensitivity_utac/etas_nonstat.py": (
        "7a07a223e453b91462c667b191bb1e4e15e0025e91080044657aaa13c31f2812"
    ),
    "src/glacial_seismic_sensitivity_utac/confirmatory_v02.py": (
        "c986e2b1871036e11ca781cccb2d27ce1de1b3afaa2cb5e9483e4b534377c310"
    ),
}


def frozen_inventory() -> dict[str, str]:
    """Relative path -> frozen SHA-256 (union of all frozen lists; conflicting entries raise)."""
    inv: dict[str, str] = {}

    def add(items: dict[str, str]) -> None:
        for rel, h in items.items():
            if rel in inv and inv[rel] != h:
                raise AssertionError(f"conflicting frozen hashes for {rel}")
            inv[rel] = h

    v02 = json.loads((ROOT / "results/frozen_v02_preregistration.json").read_text(encoding="utf-8"))
    add(v02["v01_frozen_files_sha256"])
    add_doc = ROOT / "results/frozen_v02_addendum_2026-10-10.json"
    add(json.loads(add_doc.read_text(encoding="utf-8"))["amends_files_sha256_unchanged"])
    v03 = json.loads((ROOT / "results/frozen_v03_preregistration.json").read_text(encoding="utf-8"))
    for key in ("sha256_frozen_v01_v02", "sha256_v03_artefacts", "sha256_code"):
        add(v03[key])
    add(V020_CODE_SHA256)
    return inv


def file_matches(rel: str, expected: str) -> bool:
    data = (ROOT / rel).read_bytes()
    if hashlib.sha256(data).hexdigest() == expected:
        return True
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest() == expected


def current_digests(rels: list[str]) -> dict[str, str]:
    """Raw SHA-256 of each file now (used to detect any change during a test session)."""
    return {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in rels}
