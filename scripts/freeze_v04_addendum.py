"""Write the machine-readable second addendum (A8 + A9) with SHA-256 values (freeze v0.4.0, F4).

Usage (from the repository root):

    python scripts/freeze_v04_addendum.py
        # DRAFT  -> results/frozen_v04_addendum_draft.json
    python scripts/freeze_v04_addendum.py --freeze 2026-11-xx --seed N
        # FROZEN -> results/frozen_v04_addendum_<date>.json

Freezing is Johann's decision; the DRAFT only shows what will be fixed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

UNCHANGED = [
    "PREREGISTRATION_v0.2.md",
    "results/frozen_v02_preregistration.json",
    "results/frozen_v02_baselines.json",
    "results/frozen_v02_addendum_2026-10-10.json",
    "results/frozen_v03_preregistration.json",
    "results/frozen_confirmatory_parameters.json",
    "results/frozen_monitoring_indicators.json",
    "results/adequacy/b_value/b_value_2016_2025.json",
    "results/adequacy/b_value/comcat_ak_SE_Alaska_AK_2016_2025.csv.gz",
    "results/adequacy/b_value/comcat_ak_Interior_AK_ctrl_2016_2025.csv.gz",
]
NEW_FROZEN = [
    "PREREGISTRATION_v0.2_NACHTRAG_2.md",
    "docs/adequacy/A8_addendum_draft.md",
    "docs/adequacy/A9_c2_zone_confirmation_draft.md",
    "results/adequacy/c2_zone_spec.json",
    "results/adequacy/sequence_term/comcat_ak_SE_Alaska_AK_2026_to_cutoff.csv.gz",
    "results/adequacy/sequence_term/snapshot_2026.json",
]
CODE = [
    "src/glacial_seismic_sensitivity_utac/etas_adequacy/frozen.py",
    "src/glacial_seismic_sensitivity_utac/etas_adequacy/forecast.py",
    "src/glacial_seismic_sensitivity_utac/etas_adequacy/stats.py",
    "src/glacial_seismic_sensitivity_utac/etas_adequacy/gate_sim.py",
    "src/glacial_seismic_sensitivity_utac/etas_adequacy/zone_check.py",
]


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def build(freeze_date: str | None, seed: int | None) -> dict[str, object]:
    spec = json.loads((ROOT / "results/adequacy/c2_zone_spec.json").read_text(encoding="utf-8"))
    bval = json.loads((ROOT / UNCHANGED[7]).read_text(encoding="utf-8"))
    looks = json.loads((ROOT / UNCHANGED[1]).read_text(encoding="utf-8"))["C2"]["looks"]
    n_ref = {r: v["n_events_ge_mc"] for r, v in bval["regions"].items()}
    return {
        "status": "FROZEN" if freeze_date else "DRAFT",
        "frozen_on": freeze_date,
        "type": "second dated addendum to the v0.2 preregistration "
        "(PREREGISTRATION_v0.2.md sec. 8)",
        "document": "PREREGISTRATION_v0.2_NACHTRAG_2.md",
        "decided_by": "J. Roemer (GenesisAeon); gate variant 2026-10-22, A9 2026-10-23",
        "package_version": "0.4.0",
        "code_tag": "v0.4.0",
        "amends_files_sha256_unchanged": {f: sha(f) for f in UNCHANGED},
        "new_frozen_files_sha256": {f: sha(f) for f in NEW_FROZEN},
        "code_sha256": {f: sha(f) for f in CODE},
        "A8_gate": {
            "variant": "L+T3",
            "control_region": "Interior_AK_ctrl",
            "glacier_region": "SE_Alaska_AK",
            "level": 0.005,
            "inconclusive_if": "any of T1_ctrl, T2_ctrl, T3_ctrl has p < level",
            "glacier_T2_T3": "reported as qualifications; C2 keeps its confirmatory status",
            "T1_n_sim": 10_000,
            "T2_bootstrap_B": 10_000,
            "T3": "two-sample KS (asymptotic p), window vs reference magnitudes, both rounded to "
            "6 decimals",
            "mc_ref": 2.1,
            "reference_window": ["2016-01-01", "2026-01-01"],
            "reference_n": n_ref,
            "looks": looks,
            "window_start": "2027-01-01",
            "seed": seed,
            "seed_rule": "one fixed integer seed for the whole gate; per-test streams via "
            "np.random.SeedSequence(seed).generate_state(...); no rerun with another seed, no "
            "increase of simulations after data are seen",
            "bootstrap": "resumable (checkpoint=...), bit-identical to an uninterrupted run",
        },
        "A9_zone_confirmation": {
            k: spec[k]
            for k in ("epicentre_lat", "epicentre_lon", "epicentre_event", "radius_km",
                      "distance", "glacier_region", "log_mu_ref_reduced", "sigma_year_reduced",
                      "confirmation", "confirmation_text")  # fmt: skip
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", metavar="YYYY-MM-DD")
    ap.add_argument("--seed", type=int)
    a = ap.parse_args()
    if bool(a.freeze) != (a.seed is not None):
        raise SystemExit("--freeze and --seed go together (Johann's decision)")
    out = ROOT / "results" / (f"frozen_v04_addendum_{a.freeze}.json" if a.freeze
                              else "frozen_v04_addendum_draft.json")  # fmt: skip
    out.write_text(json.dumps(build(a.freeze, a.seed), indent=1) + "\n", encoding="utf-8")
    print(out, hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
