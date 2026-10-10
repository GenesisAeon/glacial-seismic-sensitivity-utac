"""Synthetic recovery study for the nonstationary-background ETAS (v0.2, M2).

Compares the joint MLE (rw_sd 1.0 and 0.2) with the two-stage estimator on three scenarios.
Writes results/v02/recovery_study.csv (resumable: finished rows are skipped)."""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import etas_nonstat as E

OUT = os.path.join(os.environ.get("GSS_OUT", "results"), "v02", "recovery_study.csv")
TRUE = dict(K=0.0276, alpha=1.0, c=0.002, p=1.15)
T0, T1 = 1995.0, 2025.0
SCEN = {
    "stationary": (lambda t: 80.0 + 0 * t, ()),
    "linear_rise": (lambda t: 50.0 + 50.0 * (t - T0) / (T1 - T0), ()),
    "masked_rise": (
        lambda t: np.where(t < 2015, 60.0, 60.0 * np.exp(0.5 * (t - 2015) / 10)),
        ((2010.3, 7.0),),
    ),
}


def true_slope(fn) -> float:  # type: ignore[no-untyped-def]
    mids = np.arange(T0, T1) + 0.5
    y = np.log([np.mean(fn(np.linspace(a - 0.5, a + 0.5, 101))) for a in mids])
    return float(np.polyfit((mids - mids.mean()) / 10, y, 1)[0])


def main(seeds: int) -> None:
    done = pd.read_csv(OUT) if os.path.exists(OUT) else pd.DataFrame()
    rows = done.to_dict("records")
    keys = {(r["scenario"], r["seed"], r["method"]) for r in rows}
    for name, (fn, ms) in SCEN.items():
        ts = true_slope(fn)
        for seed in range(seeds):
            cat = None
            for method in ("joint_rw1", "joint_rw0.2", "two_stage"):
                if (name, seed, method) in keys:
                    continue
                if cat is None:
                    cat = E.simulate(
                        fn, T0, T1, rng=np.random.default_rng(1000 + seed), mainshocks=ms, **TRUE
                    )
                t, m = cat.t.to_numpy(), cat.mag.to_numpy()
                tic = time.time()
                if method == "two_stage":
                    _, f = E.fit_two_stage(t, m, 2.0, T0, T1)
                else:
                    f = E.fit_nonstationary(
                        t, m, 2.0, T0, T1, rw_sd=1.0 if method == "joint_rw1" else 0.2
                    )
                tr = E.log_mu_trend(f, (T0, T1))
                wr = E.window_ratio(f, (2008, 2019), (2020, 2025))
                true_wr = float(
                    np.log(np.mean(fn(np.linspace(2020, 2025, 501))))
                    - np.log(np.mean(fn(np.linspace(2008, 2019, 501))))
                )
                mu_true = np.array(
                    [np.mean(fn(np.linspace(a, a + 1, 101))) for a in np.arange(T0, T1)]
                )
                rows.append(
                    dict(
                        scenario=name,
                        seed=seed,
                        method=method,
                        n=len(t),
                        K=f.K,
                        alpha=f.alpha,
                        c_days=f.c_yr * 365.25,
                        p=f.p,
                        br=f.branching_ratio,
                        mu_bias=float(np.exp(np.mean(np.log(f.mu) - np.log(mu_true))) - 1),
                        slope=tr["slope_per_decade"],
                        slope_se=tr["se"],
                        slope_true=ts,
                        log_wr=wr["log_ratio"],
                        log_wr_se=wr["se"],
                        log_wr_true=true_wr,
                        secs=time.time() - tic,
                    )
                )
                pd.DataFrame(rows).to_csv(OUT, index=False)
                print(
                    name,
                    seed,
                    method,
                    f"n={len(t)} p={f.p:.2f} br={f.branching_ratio:.2f} "
                    f"slope={tr['slope_per_decade']:.3f}±{tr['se']:.3f} true={ts:.3f}",
                    flush=True,
                )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
