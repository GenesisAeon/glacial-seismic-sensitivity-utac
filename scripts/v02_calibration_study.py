"""Null calibration of the H2.1 slope SE (v0.2, M2): stationary synthetic ETAS catalogues,
two-stage estimator with/without random-walk penalty. Resumable CSV in results/v02/.

Erratum 2026-10-10 (Codex review on PR #1): the first run passed the H2.2 windows as
(2008, 2019), (2020, 2025); window_ratio() uses exclusive upper ends, so it compared 2008-2018 with
2020-2024, and the catalogues/fit ended at 2025.0 (30 instead of 31 bins). That run is kept as
results/v02/calibration_study.csv. This corrected version simulates and fits
1995-2025 (end 2026.0) with the preregistered windows and writes calibration_study_v2.csv."""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import etas_nonstat as E

T1 = 2026.0
OUT = os.path.join(os.environ.get("GSS_OUT", "results"), "v02", "calibration_study_v2.csv")
RWS = tuple(float(x) for x in os.environ.get("GSS_CAL_RW", "1.0").split(","))
TRUE = dict(K=0.0276, alpha=1.0, c=0.002, p=1.15)


def main(n: int) -> None:
    rows = pd.read_csv(OUT).to_dict("records") if os.path.exists(OUT) else []
    have = {(r["seed"], r["rw_sd"]) for r in rows}
    for seed in range(n):
        cat = None
        for rw in RWS:
            if (seed, rw) in have:
                continue
            if cat is None:
                cat = E.simulate(
                    lambda t: 80.0 + 0 * t,
                    1995.0,
                    T1,
                    rng=np.random.default_rng(5000 + seed),
                    **TRUE,
                )
            _, f = E.fit_two_stage(cat.t.to_numpy(), cat.mag.to_numpy(), 2.0, 1995.0, T1, rw_sd=rw)
            tr = E.log_mu_trend(f, (1995.0, T1))
            wr = E.window_ratio(
                f, (2008.0, 2020.0), (2020.0, 2026.0)
            )  # exclusive ends = 2008-2019 vs 2020-2025
            rows.append(
                dict(
                    seed=seed,
                    rw_sd=rw,
                    slope=tr["slope_per_decade"],
                    se=tr["se"],
                    se_ols=tr["se_ols"],
                    se_lik=tr["se_lik"],
                    log_wr=wr["log_ratio"],
                    log_wr_se=wr["se"],
                )
            )
            pd.DataFrame(rows).to_csv(OUT, index=False)
            print(
                seed,
                rw,
                f"{tr['slope_per_decade']:.3f} {tr['se_ols']:.3f} {tr['se_lik']:.3f}",
                flush=True,
            )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
