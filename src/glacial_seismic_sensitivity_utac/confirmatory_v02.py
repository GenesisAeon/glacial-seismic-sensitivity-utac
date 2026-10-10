"""Prospective test C2 (PREREGISTRATION_v0.2.md sec. 5): background-rate change glacier vs.
control from 2027-01-01, with frozen triggering parameters and frozen baselines.

Usage at a look (not before 2030-01-01 for look 1):
    evaluate_pair(cat_glacier, cat_control, baselines, look_end=2030.0)
where each catalogue holds decimal-year times ``t`` and magnitudes ``mag`` of all events >= the
frozen Mc (including events from the year before the window as triggering history).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from . import etas_nonstat as E

WINDOW_START = 2027.0
LOOKS = ((2030.0, 0.01), (2037.0, 0.04))  # exclusive ends: data to 2029-12-31 / 2036-12-31


def region_change(cat: pd.DataFrame, base: dict[str, Any], look_end: float) -> dict[str, float]:
    trig = dict(
        K=base["K"], alpha=base["alpha"], c_yr=base["c_yr"], p=base["p"], tmax=base["tmax_yr"]
    )
    c = cat[cat.mag >= base["mc_ref"] - 1e-9]
    r = E.mu_window_mle(
        c.t.to_numpy(float), c.mag.to_numpy(float), base["mc_ref"], trig, WINDOW_START, look_end
    )
    T = look_end - WINDOW_START
    var = (
        r["log_mu_se"] ** 2
        + base["sigma_year"] ** 2 / T
        + base["sigma_year"] ** 2 / base["n_ref_years"]
    )
    delta = r["log_mu"] - base["log_mu_ref"]
    return dict(
        mu_new=r["mu"],
        n_new=r["n"],
        delta_log_mu=delta,
        se=float(np.sqrt(var)),
        z_m6=float(delta / np.sqrt(var)),
    )


def evaluate_pair(
    cat_g: pd.DataFrame,
    cat_c: pd.DataFrame,
    baselines: dict[str, Any],
    look_end: float,
    glacier: str = "SE_Alaska_AK",
    control: str = "Interior_AK_ctrl",
) -> dict[str, Any]:
    g = region_change(cat_g, baselines["regions"][glacier], look_end)
    c = region_change(cat_c, baselines["regions"][control], look_end)
    D = g["delta_log_mu"] - c["delta_log_mu"]
    se = float(np.hypot(g["se"], c["se"]))
    z = D / se
    alpha = dict(LOOKS).get(look_end, np.nan)
    p = float(stats.norm.sf(z))
    return dict(
        glacier=g,
        control=c,
        D=D,
        se=se,
        z=z,
        p_one=p,
        alpha=alpha,
        reject=bool(np.isfinite(alpha) and p < alpha),
    )
