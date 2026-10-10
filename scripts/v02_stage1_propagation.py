"""EXPLORATORY (review W3, Claude Code): propagate stage-1 (triggering-parameter) uncertainty into
the H2 statistics of the primary pair. The preregistered SE is conditional on the stage-1 point
estimate (the mu-block covariance with fixed K, alpha, c, p). Here: draw (log K, alpha, log c, p)
from the stage-1 normal approximation (clipped to the fit bounds), refit the yearly mu with each
draw fixed, and add the between-draw variance of the slope / window log-ratio to the conditional
variance. Crude (normal approximation at a boundary optimum p = 1.0001), descriptive only; the
frozen procedure is unchanged. Writes results/v02/stage1_propagation_<region>.csv (resumable)."""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import etas_nonstat as E
from glacial_seismic_sensitivity_utac import v02


def run(name: str, n_draw: int) -> None:
    out = v02.outdir() / f"stage1_propagation_{name}.csv"
    rows = pd.read_csv(out).to_dict("records") if os.path.exists(out) else []
    pr = v02.prereg()["H2"]
    p = v02._prep(name)
    assert p is not None
    t, m = v02.region_events(p)
    edges = np.arange(v02.FIT_T0, v02.FIT_T1 + 0.5, 1.0)
    d = E.ETASData.build(t, m, p.mc_ref, v02.FIT_T0, v02.FIT_T1, edges, pr["tmax_yr"])
    d1 = E.ETASData.build(
        t, m, p.mc_ref, v02.FIT_T0, v02.FIT_T1, np.array([v02.FIT_T0, v02.FIT_T1]), pr["tmax_yr"]
    )
    s1 = E.fit_nonstationary(
        t,
        m,
        p.mc_ref,
        v02.FIT_T0,
        v02.FIT_T1,
        edges=d1.edges,
        tmax=pr["tmax_yr"],
        rw_sd=pr["rw_sd"],
        data=d1,
    )
    x1 = np.array([np.log(s1.K), s1.alpha, np.log(s1.c_yr), s1.p])
    cov = s1.cov[1:5, 1:5]
    w, v = np.linalg.eigh(0.5 * (cov + cov.T))
    cov = (v * np.clip(w, 0, None)) @ v.T
    lo = np.array([-np.inf, 0.0, np.log(1e-6), 1.0001])
    hi = np.array([np.inf, 3.0, np.log(0.5), 2.5])
    rng = np.random.default_rng(20261010)
    draws = rng.multivariate_normal(x1, cov, size=n_draw)
    draws = np.clip(draws, lo, hi)
    todo = [(-1, x1)] + list(enumerate(draws))
    done = {int(r["draw"]) for r in rows}
    for k, x in todo:
        if k in done:
            continue
        f = E.fit_nonstationary(
            t,
            m,
            p.mc_ref,
            v02.FIT_T0,
            v02.FIT_T1,
            edges=edges,
            tmax=pr["tmax_yr"],
            rw_sd=pr["rw_sd"],
            data=d,
            fix_trig=(float(np.exp(x[0])), float(x[1]), float(np.exp(x[2])), float(x[3])),
        )
        tr = E.log_mu_trend(f, (v02.FIT_T0, v02.FIT_T1))
        wr = E.window_ratio(f, v02.WIN_A, v02.WIN_B)
        rows.append(
            dict(
                draw=k,
                K=np.exp(x[0]),
                alpha=x[1],
                c_yr=np.exp(x[2]),
                p=x[3],
                slope=tr["slope_per_decade"],
                se=tr["se"],
                log_wr=wr["log_ratio"],
                log_wr_se=wr["se"],
            )
        )
        pd.DataFrame(rows).to_csv(out, index=False)
        print(name, k, f"p={x[3]:.4f} slope={tr['slope_per_decade']:.3f}", flush=True)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    for reg in sys.argv[2:] or ["SE_Alaska_AK", "Interior_AK_ctrl"]:
        run(reg, n)
