"""v0.3 exploratory: GRACE under-estimation (Sasgen et al. 2026) x rheology variants.

Writes results/v03/grace_bias_scenarios.csv and results/v03/grace_bias_earliest.csv.
EXPLORATORY - not pre-registered; frozen v0.1/v0.2 results are not modified.
"""

from __future__ import annotations

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import v03_grace_bias as G


def main() -> int:
    out = C.OUT / "v03"
    out.mkdir(parents=True, exist_ok=True)
    summ = G.run()
    summ.to_csv(out / "grace_bias_scenarios.csv", index=False)
    e = G.summarise(summ)
    e.to_csv(out / "grace_bias_earliest.csv", index=False)
    print(e.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
