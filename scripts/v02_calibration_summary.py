"""Summarise the H2 null calibration (sd of z for slope and window log-ratio, bootstrap 90 %
upper bound). Compares the original run (calibration_study.csv, window bug) with the corrected
run (calibration_study_v2.csv) and the production-geometry runs (calibration_prod_p*.csv,
re-run with the K2-corrected simulator). Exploratory bookkeeping for the 2026-10-10 erratum."""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

D = os.path.join(os.environ.get("GSS_OUT", "results"), "v02")


def summ(f: str) -> dict[str, float]:
    d = pd.read_csv(os.path.join(D, f))
    d = d[d.rw_sd == 1.0]
    zs = (d.slope / d.se).to_numpy()
    zw = (d.log_wr / d.log_wr_se).to_numpy()
    rng = np.random.default_rng(0)
    bs = [np.std(rng.choice(zs, len(zs)), ddof=1) for _ in range(4000)]
    bw = [np.std(rng.choice(zw, len(zw)), ddof=1) for _ in range(4000)]
    return dict(
        n=len(d),
        sd_z_slope=float(np.std(zs, ddof=1)),
        sd_z_slope_u90=float(np.quantile(bs, 0.9)),
        sd_z_wr=float(np.std(zw, ddof=1)),
        sd_z_wr_u90=float(np.quantile(bw, 0.9)),
        mean_z_wr=float(zw.mean()),
        p_hat_median=float(d.p_hat.median()) if "p_hat" in d else float("nan"),
        frac_p_hat_le_1001=float((d.p_hat <= 1.001).mean()) if "p_hat" in d else float("nan"),
    )


if __name__ == "__main__":
    out = pd.DataFrame(
        {
            f: summ(f)
            for f in (
                "calibration_study.csv",
                "calibration_study_v2.csv",
                "calibration_prod_p1.15.csv",
                "calibration_prod_p1.02.csv",
            )
            if os.path.exists(os.path.join(D, f))
        }
    ).T
    print(out.round(3).to_string())
    out.to_csv(os.path.join(D, "calibration_summary.csv"))
