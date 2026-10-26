"""Write the machine-readable A9 spec (zone, reduced baseline, rule) from the AP6c calibration.

Usage (from the repository root):

    python scripts/c2_zone_spec.py                      # DRAFT -> c2_zone_spec.json
    python scripts/c2_zone_spec.py --freeze YYYY-MM-DD  # FROZEN (Johann's decision, F3)

Draft until frozen by a dated addendum; the values are copied from
``results/adequacy/sequence_zone/zone.json`` (AP6c, protocol 5c1ecb1) with their provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ZONE = Path("results/adequacy/sequence_zone/zone.json")
OUT = Path("results/adequacy/c2_zone_spec.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freeze", metavar="YYYY-MM-DD")
    a = ap.parse_args()
    z = json.loads(ZONE.read_text(encoding="utf-8"))
    spec = {
        "status": f"FROZEN {a.freeze}" if a.freeze else "DRAFT (not frozen)",
        "item": "A9: C2 confirmation without the epicentral zone of the 2025-12-06 M6.8",
        "decision": "Johann Roemer, 2026-10-23 (chat), after AP6c run 2 (99ef046)",
        "epicentre_lat": z["epicentre"]["lat"],
        "epicentre_lon": z["epicentre"]["lon"],
        "epicentre_event": {"time": z["epicentre"]["time"], "mag": z["epicentre"]["mag"],
                            "catalog": "ComCat ak"},  # fmt: skip
        "radius_km": z["radius_km"],
        "radius_rule": "95 % quantile of epicentral distances of sequence events >= Mc, day 2 to "
        "2025-12-31, rounded up to 5 km (51.44 km -> 55 km)",
        "distance": "great circle, catalog.haversine_km (R = 6371 km)",
        "glacier_region": "SE_Alaska_AK",
        "log_mu_ref_reduced": z["reduced_baseline"]["log_mu_ref"],
        "sigma_year_reduced": z["reduced_baseline"]["sigma_year"],
        "reduced_baseline_rule": "relative to the frozen baseline: log mu_ref + mean(ly_red) - "
        "mean(ly_full); sigma_y * sd(ly_red) / sd(ly_full); ly = yearly log mu 2016-2025 "
        "(zone_check.yearly_log_mu) on the frozen 2016-2025 snapshot",
        "confirmation": "p_reduced_below_alpha",
        "confirmation_text": "a C2 rejection at a look counts as confirmed only if the reduced "
        "statistic (glacier region outside the zone, reduced baseline, control unchanged) has a "
        "one-sided p below the alpha of that look (0.01 / 0.04)",
        "source_zone_json_sha256": hashlib.sha256(ZONE.read_bytes()).hexdigest(),
        "evidence": ["docs/adequacy/sequence_tail.md", "docs/adequacy/sequence_term_deviation.md",
                     "docs/adequacy/sequence_level.md", "docs/adequacy/sequence_zone.md"],
    }  # fmt: skip
    OUT.write_bytes((json.dumps(spec, indent=1) + "\n").encode("utf-8"))  # LF on every OS
    print(OUT, hashlib.sha256(OUT.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
