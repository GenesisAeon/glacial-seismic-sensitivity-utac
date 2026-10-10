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


def test_c2_baselines_frozen_against_this_prereg() -> None:
    f = ROOT / "results" / "frozen_v02_baselines.json"
    b = json.loads(f.read_text())
    assert b["prereg_sha256"] == _sha(PREREG)
    assert {"SE_Alaska_AK", "Interior_AK_ctrl"} <= set(b["regions"])
    assert _sha(f) == "e2fc568c93622c97607c122c210ed5fcccace0d2440b8cd420fddd931be9f401"


def test_c2_se_formula_is_the_frozen_json_formula_without_factor() -> None:
    # Pins the implemented C2 SE to the frozen JSON formula (no 1.25 factor). The ambiguity with
    # section 2 of PREREGISTRATION_v0.2.md is listed in the dated addendum draft (docs/);
    # if Johann decides otherwise, that goes into a dated, hashed addendum and this test changes.
    d = json.loads(PREREG.read_text())
    assert "1.25" not in d["C2"]["se"] and "factor" not in d["C2"]["se"]
    rng = np.random.default_rng(3)
    t = np.sort(rng.uniform(2026.0, 2030.0, 400))
    cat = pd.DataFrame(dict(t=t, mag=np.full(len(t), 2.5)))
    base = dict(
        mc_ref=2.0,
        K=1e-9,
        alpha=1.0,
        c_yr=1e-3,
        p=1.1,
        tmax_yr=1.0,
        log_mu_ref=np.log(100.0),
        sigma_year=0.3,
        n_ref_years=10,
    )
    r = C2.region_change(cat, base, 2030.0)
    se_new = 1.0 / np.sqrt(r["n_new"])  # Poisson limit for negligible triggering
    expect = np.sqrt(se_new**2 + 0.3**2 / 3 + 0.3**2 / 10)
    assert r["se"] == pytest.approx(expect, rel=1e-3)
