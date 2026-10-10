"""Integrity of the v0.2 preregistration and of the frozen v0.1.0 files."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from glacial_seismic_sensitivity_utac import confirmatory_v02 as C2
from glacial_seismic_sensitivity_utac import etas_nonstat as E

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "results" / "frozen_v02_preregistration.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_v01_frozen_files_unchanged() -> None:
    d = json.loads(PREREG.read_text())
    for rel, h in d["v01_frozen_files_sha256"].items():
        assert _sha(ROOT / rel) == h, f"{rel} changed after v0.1.0"


def test_prereg_hash_matches_document() -> None:
    text = (ROOT / "PREREGISTRATION_v0.2.md").read_text()
    m = re.search(r"SHA-256[^`]*`([0-9a-f]{64})`", text)
    assert m is not None
    assert m.group(1) == _sha(PREREG)


def test_prereg_key_choices() -> None:
    d = json.loads(PREREG.read_text())
    assert d["C2"]["window_start"] == "2027-01-01"
    assert d["H2"]["H2_1"]["primary_pair"] == ["SE_Alaska_AK", "Interior_AK_ctrl"]
    assert d["H2"]["tmax_yr"] == 1.0
    assert [lk["alpha"] for lk in d["C2"]["looks"]] == [0.01, 0.04]


def test_c2_null_and_alternative_on_synthetic_data() -> None:
    trig = dict(K=0.0276, alpha=1.0, c_yr=0.002, p=1.15, tmax_yr=1.0)
    base = dict(mc_ref=2.0, log_mu_ref=float(np.log(50.0)), sigma_year=0.1, n_ref_years=10, **trig)
    bl = {"regions": {"SE_Alaska_AK": base, "Interior_AK_ctrl": base}}
    kw = dict(K=0.0276, alpha=1.0, c=0.002, p=1.15)

    def cat(mu: float, seed: int) -> pd.DataFrame:
        c = E.simulate(lambda t: mu + 0 * t, 2026.0, 2030.0, rng=np.random.default_rng(seed), **kw)
        return c

    null = C2.evaluate_pair(cat(50, 1), cat(50, 2), bl, 2030.0)
    assert abs(null["z"]) < 3
    alt = C2.evaluate_pair(cat(100, 3), cat(50, 4), bl, 2030.0)
    assert alt["D"] == pytest.approx(np.log(2), abs=3 * alt["se"])
    assert alt["reject"]
