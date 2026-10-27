"""Second addendum (A8 + A9): hashes and key choices. Runs on the DRAFT until the freeze (F4)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from glacial_seismic_sensitivity_utac.etas_adequacy import gate_sim

ROOT = Path(__file__).resolve().parents[1]
FROZEN = sorted(ROOT.glob("results/frozen_v04_addendum_2*.json"))
ADDENDUM = FROZEN[-1] if FROZEN else ROOT / "results" / "frozen_v04_addendum_draft.json"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def add() -> dict:  # type: ignore[type-arg]
    return json.loads(ADDENDUM.read_text(encoding="utf-8"))


def test_unchanged_files_still_match(add: dict) -> None:  # type: ignore[type-arg]
    for rel, h in add["amends_files_sha256_unchanged"].items():
        assert _sha(ROOT / rel) == h, f"{rel} changed"


def test_new_frozen_and_code_hashes_hold_once_frozen(add: dict) -> None:  # type: ignore[type-arg]
    if add["status"] != "FROZEN":
        pytest.skip("draft: texts and code may still change until the freeze")
    for key in ("new_frozen_files_sha256", "code_sha256"):
        for rel, h in add[key].items():
            assert _sha(ROOT / rel) == h, f"{rel} changed after the freeze"
    assert isinstance(add["A8_gate"]["seed"], int)
    doc = (ROOT / add["document"]).read_text(encoding="utf-8")
    assert _sha(ADDENDUM) in doc, "the Nachtrag must quote the SHA-256 of its JSON"


def test_a8_matches_code_and_frozen_inputs(add: dict) -> None:  # type: ignore[type-arg]
    g = add["A8_gate"]
    assert g["variant"] == "L+T3" and g["level"] == 0.005
    assert gate_sim.gate_lenient_t3.__defaults__ == (0.005,)
    assert g["T1_n_sim"] == g["T2_bootstrap_B"] == 10_000
    prereg = json.loads((ROOT / "results/frozen_v02_preregistration.json").read_text("utf-8"))
    assert g["looks"] == prereg["C2"]["looks"]
    assert g["reference_n"] == {"SE_Alaska_AK": 5442, "Interior_AK_ctrl": 2098}
    assert g["mc_ref"] == 2.1 and g["window_start"] == "2027-01-01"


def test_a9_is_the_zone_spec(add: dict) -> None:  # type: ignore[type-arg]
    spec = json.loads((ROOT / "results/adequacy/c2_zone_spec.json").read_text("utf-8"))
    for k, v in add["A9_zone_confirmation"].items():
        assert spec[k] == v
    assert spec["radius_km"] == 55.0
    assert spec["log_mu_ref_reduced"] == pytest.approx(3.99831, abs=5e-6)
    assert spec["sigma_year_reduced"] == pytest.approx(0.38896, abs=5e-6)


def test_gate_seed_is_derived_from_the_nachtrag(add: dict) -> None:  # type: ignore[type-arg]
    if add["status"] != "FROZEN":
        pytest.skip("draft: no seed yet")
    seed = add["A8_gate"]["seed"]
    doc = (ROOT / add["document"]).read_bytes()
    basis = doc.replace(f"**{seed}**".encode(), b"**SEED_PLATZHALTER**").replace(
        _sha(ADDENDUM).encode(), b"JSON_SHA256_PLATZHALTER"
    )
    h = hashlib.sha256(basis).hexdigest()
    assert h == add["document_sha256_seed_basis"]
    assert seed == int(h[:8], 16)
