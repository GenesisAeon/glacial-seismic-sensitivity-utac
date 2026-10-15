"""v0.3 S3 DRAFT: write results/v03/prereg_v03_DRAFT.json (NOT frozen).

The draft records the S2 thresholds, rule order, data definitions and the SHA-256 of all frozen
v0.1/v0.2 files and of the S0/S1/S2 artefacts.  Freezing (renaming to frozen_v03_
preregistration.json, committing, recording the hash in PREREGISTRATION_v0.3.md) happens ONLY
after review by J. Römer, and before 2026-11-01.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = RES / "v03" / "prereg_v03_DRAFT.json"

FROZEN_V01_V02 = (
    "results/frozen_confirmatory_parameters.json",
    "results/frozen_monitoring_indicators.json",
    "results/frozen_v02_preregistration.json",
    "results/frozen_v02_addendum_2026-10-10.json",
    "results/frozen_v02_baselines.json",
)
V03_ARTEFACTS = (
    "results/v03/s0_case_list.json",
    "results/v03/s0_amendment_A1.json",
    "results/v03/MANIFEST_v03.sha256",
    "results/v03/s2_calibration.json",
    "results/v03/s2v_scores.csv",
    "drivers/registry.yaml",
    "drivers/verified_dois.tsv",
)


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


KNOWN_WEAKNESSES = {
    "a_R2_false_alarm_risk": "S2b retrospective (exploratory, thresholds unchanged): matched "
    "M2-4.5 negatives FP 5/900, Clopper-Pearson upper bound 1.29% vs criterion 2%; all 5 via "
    "R2 (shallow and preceded by a larger event within 1 h); 3 of 5 in the St. Elias region "
    "(ak, ~60.5N 140W), 1 The Geysers (nc), 1 South Carolina (se). M8 may realistically fail.",
    "b_R4_not_transferable": "R4 (cluster median DC <= 46%) is effectively tuned to "
    "Bardarbunga 2014 and does not transfer: Kilauea 2018 0/64 detected as caldera_collapse "
    "(ComCat cluster median DC 70.5%, n=62).",
    "c_Napoleonville_by_design": "Napoleonville 2012 not detected by design: published MT shows "
    "volume increase (not a collapse MT class) and the event is not in ComCat.",
    "consequence": "rule improvements are deferred to v0.4 and will not touch M8; M8 runs "
    "with the frozen rules and thresholds and is reported regardless of outcome.",
}


def build_doc() -> dict:
    s2 = json.loads((RES / "v03" / "s2_calibration.json").read_text(encoding="utf-8"))
    doc = {
        "status": "DRAFT - NOT FROZEN (awaiting review by J. Roemer; freeze before 2026-11-01)",
        "document": "PREREGISTRATION_v0.3_ENTWURF.md",
        "scope": "v0.3 mass-change / collapse module; does not modify C1, C2, M1-M7, A1-A7, E1",
        "categories": {
            "exploratory": [
                "S2 discriminator calibration",
                "S2b retrospective check",
                "GRACE under-estimation sensitivity (Sasgen 2026)",
                "Groningen sequence description",
            ],
            "prespecified_data_touched": ["discriminator thresholds and rule order (from S2)"],
            "prospective": ["M8 (window 2026-11-01 .. 2027-10-31)"],
        },
        "discriminator": {
            "rule_order": ["L0 (full mode only)", "R1", "R2", "R4", "tectonic"],
            "thresholds": s2["thresholds"],
            "modes": ["no_labels", "catalogue_only"],
            "code": "src/glacial_seismic_sensitivity_utac/v03_discriminator.py",
        },
        "M8": {
            "window_utc": ["2026-11-01T00:00:00", "2027-10-31T23:59:59"],
            "data_pull_not_before": "2027-11-15",
            "extension_descriptive": {
                "window_utc": ["2027-11-01T00:00:00", "2028-10-31T23:59:59"],
                "data_pull_not_before": "2028-11-15",
                "role": "descriptive only; no criterion",
            },
            "positives": "all ComCat events typed landslide, mine collapse or collapse "
            "in the window (labels hidden for classification)",
            "negatives": {
                "global_M5": "all ComCat earthquakes M>=5.0, depth<=40 km, in the window",
                "matched_M2_4.5": "ComCat earthquakes 2.0<=M<=4.5 from the networks that "
                "contributed positives in the same window; random sample of at most 150 per "
                "network, numpy default_rng(20271115), without replacement",
            },
            "neighbourhood": "positives and matched negatives: 30 km / +-400 d ComCat "
            "(end capped at data pull); global_M5: ComCat global M>=4.5 +-0.5 yr",
            "primary_endpoint": "false-positive rate, mode catalogue_only, on BOTH negative sets",
            "primary_criterion": "upper 95% Clopper-Pearson bound < 0.02 for each negative set "
            "(conjunction; both must pass)",
            "secondary_endpoints": [
                "recall per class on positives (both modes; all and M2-4.5 subset), "
                "Clopper-Pearson 95% CI, DESCRIPTIVE ONLY (approved 2026-10-11)",
                "FP rates in mode no_labels",
                "sensitivity: control exclusion 50 km instead of 25 km around case centres",
            ],
            "reporting": "result reported regardless of outcome; no re-tuning of thresholds",
            "criterion_history": "global_M5 criterion written 2026-10-11 before S2b (32e3159); "
            "matched-set criterion added 2026-10-11 before the matched S2b result was computed",
        },
        "not_tested": [
            "forcing coupling (Groningen: no forcing test; optional later manual NLOG export "
            "by J. Roemer; Koyna: catalogue-only negative case)",
            "own moment-tensor inversion (not in v0.3)",
            "InSAR (later version)",
            "GRACE under-estimation (exploratory only)",
        ],
        "decisions_resolved_2026-10-11": [
            "matched negatives M2-4.5 added",
            "hit rates descriptive only",
            "Groningen without forcing test",
            "Koyna kept as negative case",
            "Napoleonville 2012 and Kilauea 2018 added (S0 amendment A1)",
            "no own MT inversion",
            "M8 1 year primary + descriptive 2nd year",
            "raw S1 snapshots archived on Zenodo with the v0.3 release",
        ],
        "decisions_open": ["final review and freeze date (before 2026-11-01)"],
        "sha256_frozen_v01_v02": {p: sha(p) for p in FROZEN_V01_V02},
        "sha256_v03_artefacts": {p: sha(p) for p in V03_ARTEFACTS},
        "known_weaknesses": KNOWN_WEAKNESSES,
    }
    return doc


def main() -> int:
    doc = build_doc()
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUT, hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
