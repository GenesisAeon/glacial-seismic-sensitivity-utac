"""Freeze the v0.3 preregistration: write results/frozen_v03_preregistration.json.

Run once, before the M8 window opens (2026-11-01). Content = the reviewed S3 draft
(scripts/v03_prereg_draft.build_doc) plus freeze metadata and the SHA-256 of the discriminator
code. Refuses to overwrite an existing frozen file.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from v03_prereg_draft import build_doc, sha  # noqa: E402

OUT = ROOT / "results" / "frozen_v03_preregistration.json"
CODE = (
    "src/glacial_seismic_sensitivity_utac/v03_discriminator.py",
    "src/glacial_seismic_sensitivity_utac/v03_features.py",
    "scripts/v03_s2_validation.py",
)


def main() -> int:
    if OUT.exists():
        print(f"{OUT} exists - frozen files are never overwritten", file=sys.stderr)
        return 1
    doc = build_doc()
    doc["status"] = "FROZEN"
    doc["frozen_on"] = "2026-10-15"
    doc["approved_by"] = "J. Roemer (freeze approved as is, thresholds unchanged)"
    doc["document"] = "PREREGISTRATION_v0.3.md"
    doc["decisions_open"] = []
    doc["sha256_code"] = {p: sha(p) for p in CODE}
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUT.name, hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
