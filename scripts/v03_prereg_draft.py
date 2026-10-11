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
    "results/v03/MANIFEST_v03.sha256",
    "results/v03/s2_calibration.json",
    "results/v03/s2v_scores.csv",
    "drivers/registry.yaml",
    "drivers/verified_dois.tsv",
)


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def main() -> int:
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
            "positives": "all ComCat events typed landslide, mine collapse or collapse "
            "in the window (labels hidden for classification)",
            "negatives": "all ComCat earthquakes M>=5.0, depth<=40 km, in the window",
            "neighbourhood": "ComCat global M>=4.5 catalogue, window +-0.5 yr; "
            "30 km / +-400 d neighbourhood for positives",
            "primary_endpoint": "false-positive rate on negatives, mode catalogue_only",
            "primary_criterion": "upper 95% Clopper-Pearson bound of FP rate < 0.02",
            "secondary_endpoints": [
                "recall per class on positives (both modes), Clopper-Pearson 95% CI, "
                "descriptive (expected n ~5-8 per year)",
                "FP rate in mode no_labels",
                "sensitivity: control exclusion 50 km instead of 25 km around case centres",
            ],
            "reporting": "result reported regardless of outcome; no re-tuning of thresholds",
            "s2b_retrospective_check": "catalogue_only: FP 0/1594 (CP upper 0.23%); recall "
            "collapse 2/21, mass movement 1/55 (exploratory, thresholds unchanged)",
        },
        "decisions_open": [
            "Groningen forcing: production data route (else forcing test dropped)",
            "Koyna: keep as catalogue-only negative case",
            "optional cases Napoleonville 2012 / Kilauea 2018",
            "own MT inversion: skip in v0.3",
            "M8 window: 1 year (default) or 2 years",
            "archive raw S1/S1b snapshots (~77 MB) with the release on Zenodo",
            "M8 negatives: add a magnitude/network-matched negative set (ComCat earthquakes "
            "M2-4.5 from the same regional networks as the positives); S2b showed that "
            "M>=5 negatives are not comparable",
            "M8 primary endpoint: keep FP criterion only, or add a recall criterion "
            "(S2b recall catalogue_only: collapse 2/21, mass movement 1/55)",
        ],
        "sha256_frozen_v01_v02": {p: sha(p) for p in FROZEN_V01_V02},
        "sha256_v03_artefacts": {p: sha(p) for p in V03_ARTEFACTS},
    }
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUT, hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
