"""EXPLORATORY simulations requested in the PR #1 review (2026-10-10), NOT preregistered.

(1) H2 null calibration in the boundary regime seen in the real data (p ~ 1.0001, branching
    0.84 / 0.64, Alaska-like parameters) instead of the benign p = 1.15 regime.
(2) Null behaviour of the frozen C2 procedure (as implemented in confirmatory_v02) when the true
    yearly background fluctuates log-normally (sigma_true) and nothing changes after 2026:
    false-positive rate at look 1 (alpha 0.01), mean offset of D (log-mean vs pooled-MLE
    asymmetry), sd(z).
Writes results/v02/review_sims_h2_boundary.csv and results/v02/review_sims_c2_null.csv
(resumable)."""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import confirmatory_v02 as C2
from glacial_seismic_sensitivity_utac import etas_nonstat as E

OUT = os.path.join(os.environ.get("GSS_OUT", "results"), "v02")
# frozen stage-1 values (results/frozen_v02_baselines.json), rounded
REG = {
    "glacier": dict(K=0.04536, alpha=1.0339, c=3.69e-5, p=1.0001, mu=57.0, sigma=0.30),
    "control": dict(K=0.02740, alpha=1.3735, c=8.03e-5, p=1.0001, mu=91.0, sigma=0.12),
}


def sim(r: dict[str, float], t0: float, t1: float, seed: int, sigma: float) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    years = np.arange(int(t0), int(np.ceil(t1)))
    lev = r["mu"] * np.exp(sigma * rng.standard_normal(len(years)) - 0.5 * sigma**2)

    def fn(t: np.ndarray) -> np.ndarray:
        i = np.clip(np.floor(np.asarray(t) - years[0]).astype(int), 0, len(years) - 1)
        return np.asarray(lev[i])

    return E.simulate(
        fn,
        t0,
        t1,
        K=r["K"],
        alpha=r["alpha"],
        c=r["c"],
        p=r["p"],
        rng=rng,
        mu_max=float(lev.max()) * 1.01,
    )


def h2_boundary(n: int) -> None:
    f = os.path.join(OUT, "review_sims_h2_boundary.csv")
    rows = pd.read_csv(f).to_dict("records") if os.path.exists(f) else []
    done = {(r["region"], r["seed"]) for r in rows}
    for seed in range(n):
        for name, r in REG.items():
            if (name, seed) in done:
                continue
            cat = sim(r, 1990.0, 2026.0, 100 + seed, 0.0)
            t, m = cat.t.to_numpy(), cat.mag.to_numpy()
            s1, fit = E.fit_two_stage(t, m, 2.0, 1995.0, 2026.0)
            tr = E.log_mu_trend(fit, (1995.0, 2026.0))
            rows.append(
                dict(
                    region=name,
                    seed=seed,
                    n=len(t),
                    p_hat=s1.p,
                    br_hat=s1.branching_ratio,
                    slope=tr["slope_per_decade"],
                    se=tr["se"],
                    se_cal=1.25 * tr["se"],
                )
            )
            pd.DataFrame(rows).to_csv(f, index=False)
            print(
                "h2",
                name,
                seed,
                f"p={s1.p:.3f} slope={tr['slope_per_decade']:.3f}±{tr['se']:.3f}",
                flush=True,
            )


def c2_null(n: int, sigma_scale: float = 1.0) -> None:
    f = os.path.join(OUT, "review_sims_c2_null.csv")
    rows = pd.read_csv(f).to_dict("records") if os.path.exists(f) else []
    done = {r["seed"] for r in rows}
    for seed in range(n):
        if seed in done:
            continue
        base: dict[str, dict[str, float]] = {}
        cats = {}
        for k, (name, r) in enumerate(REG.items()):
            cat = sim(r, 2011.0, 2030.0, 5000 + 10 * seed + k, r["sigma"] * sigma_scale)
            t, m = cat.t.to_numpy(), cat.mag.to_numpy()
            s1, fit = E.fit_two_stage(t, m, 2.0, 2016.0, 2026.0)
            tab = fit.table()
            base[name] = dict(
                mc_ref=2.0,
                K=s1.K,
                alpha=s1.alpha,
                c_yr=s1.c_yr,
                p=s1.p,
                tmax_yr=1.0,
                log_mu_ref=float(tab.log_mu.mean()),
                sigma_year=float(tab.log_mu.std(ddof=1)),
                n_ref_years=len(tab),
            )
            cats[name] = cat
        res = C2.evaluate_pair(
            cats["glacier"],
            cats["control"],
            {"regions": base},
            2030.0,
            glacier="glacier",
            control="control",
        )
        rows.append(
            dict(
                seed=seed,
                D=res["D"],
                se=res["se"],
                z=res["z"],
                p_one=res["p_one"],
                reject=res["reject"],
                z_m6_glacier=res["glacier"]["z_m6"],
                dlog_glacier=res["glacier"]["delta_log_mu"],
                dlog_control=res["control"]["delta_log_mu"],
                sigma_y_glacier=base["glacier"]["sigma_year"],
                sigma_y_control=base["control"]["sigma_year"],
            )
        )
        pd.DataFrame(rows).to_csv(f, index=False)
        print("c2", seed, f"D={res['D']:.3f} z={res['z']:.2f}", flush=True)


if __name__ == "__main__":
    which = sys.argv[1]
    n = int(sys.argv[2])
    h2_boundary(n) if which == "h2" else c2_null(n)
