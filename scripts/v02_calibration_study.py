"""Null calibration of the H2 standard errors (v0.2, M2) with the PRODUCTION geometry of
``v02.m2_region``: stationary synthetic ETAS catalogues simulated from FIT_T0 - HISTORY_YEARS
(history only as triggers), two-stage fit on [FIT_T0, FIT_T1) with yearly bins, tmax and rw_sd as
preregistered, H2.2 windows WIN_A / WIN_B. All geometry constants are imported from ``v02`` so the
calibration cannot drift from production again (tests/test_v02_scripts.py checks this).

Erratum history (see docs/PREREG_v0.2_NACHTRAG_ENTWURF_2026-10-10.md, E1):
* first run (results/v02/calibration_study.csv): windows passed as (2008, 2019)/(2020, 2025) to the
  half-open ``window_ratio`` (= 2008-2018 vs 2020-2024), fit 1995-2024, no history, true p 1.15
  (Codex review; Claude Code review B1);
* calibration_study_v2.csv: windows and period fixed, still without history;
* this version: production geometry; true p via argv (1.15 and 1.02, the latter close to the
  lower-bound regime of the real fits). Output: calibration_prod_p<p>.csv.

Usage: python scripts/v02_calibration_study.py <n_seeds> [p_true]"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import etas_nonstat as E
from glacial_seismic_sensitivity_utac.v02 import FIT_T0, FIT_T1, HISTORY_YEARS, TMAX, WIN_A, WIN_B

RW_SD = 1.0
MU = 80.0


def geometry() -> dict[str, object]:
    return dict(
        t_sim0=FIT_T0 - HISTORY_YEARS, t0=FIT_T0, t1=FIT_T1, tmax=TMAX, win_a=WIN_A, win_b=WIN_B
    )


def main(n: int, p_true: float) -> None:
    out = os.path.join(
        os.environ.get("GSS_OUT", "results"), "v02", f"calibration_prod_p{p_true:.2f}.csv"
    )
    true = dict(K=0.0276, alpha=1.0, c=0.002, p=p_true)
    rows = pd.read_csv(out).to_dict("records") if os.path.exists(out) else []
    have = {r["seed"] for r in rows}
    edges = np.arange(FIT_T0, FIT_T1 + 0.5, 1.0)
    for seed in range(n):
        if seed in have:
            continue
        cat = E.simulate(
            lambda t: MU + 0 * t,
            FIT_T0 - HISTORY_YEARS,
            FIT_T1,
            tmax=TMAX,
            rng=np.random.default_rng(5000 + seed),
            **true,
        )
        t, m = cat.t.to_numpy(), cat.mag.to_numpy()
        s1, f = E.fit_two_stage(t, m, 2.0, FIT_T0, FIT_T1, edges=edges, tmax=TMAX, rw_sd=RW_SD)
        tr = E.log_mu_trend(f, (FIT_T0, FIT_T1))
        wr = E.window_ratio(f, WIN_A, WIN_B)
        rows.append(
            dict(
                seed=seed,
                p_true=p_true,
                p_hat=s1.p,
                n=len(t),
                rw_sd=RW_SD,
                slope=tr["slope_per_decade"],
                se=tr["se"],
                se_ols=tr["se_ols"],
                se_lik=tr["se_lik"],
                log_wr=wr["log_ratio"],
                log_wr_se=wr["se"],
            )
        )
        pd.DataFrame(rows).to_csv(out, index=False)
        print(seed, f"p_hat={s1.p:.3f} slope={tr['slope_per_decade']:.3f}", flush=True)


if __name__ == "__main__":
    main(
        int(sys.argv[1]) if len(sys.argv) > 1 else 48,
        float(sys.argv[2]) if len(sys.argv) > 2 else 1.15,
    )
