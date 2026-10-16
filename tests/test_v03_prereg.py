"""Integrity of the frozen v0.3 preregistration."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "results" / "frozen_v03_preregistration.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_v03_hash_matches_document() -> None:
    text = (ROOT / "PREREGISTRATION_v0.3.md").read_text(encoding="utf-8")
    m = re.search(r"SHA-256 `([0-9a-f]{64})`", text)
    assert m is not None
    assert m.group(1) == _sha(PREREG)


def test_v03_frozen_dependencies_unchanged() -> None:
    d = json.loads(PREREG.read_text(encoding="utf-8"))
    for key in ("sha256_frozen_v01_v02", "sha256_v03_artefacts", "sha256_code"):
        for rel, h in d[key].items():
            assert _sha(ROOT / rel) == h, f"{rel} changed after v0.3 freeze"


def test_v03_key_choices() -> None:
    d = json.loads(PREREG.read_text(encoding="utf-8"))
    assert d["status"] == "FROZEN"
    assert d["M8"]["window_utc"][0] == "2026-11-01T00:00:00"
    assert d["discriminator"]["thresholds"] == {
        "dm_min": 0.8,
        "shallow_km": 1.0,
        "n_m45_min": 10,
        "dc_max": 46.0,
        "min_mts": 3,
        "iso_max": -0.3,
    }
    assert set(d["known_weaknesses"]) >= {"a_R2_false_alarm_risk", "b_R4_not_transferable"}
