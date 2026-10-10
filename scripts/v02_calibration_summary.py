"""Summarise the H2 null calibration (sd of z for slope and window log-ratio, bootstrap 90 %
upper bound). Compares the original run (calibration_study.csv, window bug) with the corrected
run (calibration_study_v2.csv). Exploratory bookkeeping for the 2026-10-10 erratum."""

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
    )


if __name__ == "__main__":
    out = pd.DataFrame(
        {f: summ(f) for f in ("calibration_study.csv", "calibration_study_v2.csv")}
    ).T
    print(out.round(3).to_string())
    out.to_csv(os.path.join(D, "calibration_summary.csv"))
