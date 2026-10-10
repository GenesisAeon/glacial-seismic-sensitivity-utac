"""Prospective test C2 (PREREGISTRATION_v0.2.md sec. 5): background-rate change glacier vs.
control from 2027-01-01, with frozen triggering parameters and frozen baselines.

Usage at a look (not before 2030-01-01 for look 1):
    evaluate_pair(cat_glacier, cat_control, baselines, look_end=2030.0)
where each catalogue holds decimal-year times ``t`` and magnitudes ``mag`` of all events >= the
frozen Mc (including events from the year before the window as triggering history).
"""

from __future__ import annotations

import datetime as dt
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from . import etas_nonstat as E

WINDOW_START = 2027.0
LOOKS = ((2030.0, 0.01), (2037.0, 0.04))  # exclusive ends: data to 2029-12-31 / 2036-12-31
LOOK_DATES = {"2029-12-31": 2030.0, "2036-12-31": 2037.0}  # inclusive last data day (frozen JSON)
LOOK_TOL_YR = 0.01  # ~3.7 days: decimal-year renderings of 2029-12-31 (2029.997...) map to 2030.0


def resolve_look(look_end: float | str | dt.date) -> float:
    """Map a look specification to the exclusive window end used internally (2030.0 / 2037.0).

    Accepts the exclusive end (2030.0), a decimal year within LOOK_TOL_YR of it (e.g. 2029.997 for
    2029-12-31), the inclusive last data day as ISO string or date ('2029-12-31', as in the frozen
    JSON) or the first day after the window ('2030-01-01'). Anything else raises ValueError, so a
    look can never silently lose its alpha (review W2, Claude Code)."""
    if isinstance(look_end, str):
        look_end = dt.date.fromisoformat(look_end.strip()[:10])
    if isinstance(look_end, dt.date):
        iso = look_end.isoformat()
        if iso in LOOK_DATES:
            return LOOK_DATES[iso]
        nxt = (look_end - dt.timedelta(days=1)).isoformat()
        if nxt in LOOK_DATES:
            return LOOK_DATES[nxt]
        raise ValueError(f"{iso} is not a preregistered C2 look date {sorted(LOOK_DATES)}")
    x = float(look_end)
    for end, _ in LOOKS:
        if abs(x - end) <= LOOK_TOL_YR:
            return end
    raise ValueError(f"look_end {x} is not a preregistered C2 look {[e for e, _ in LOOKS]}")


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
    look_end: float | str | dt.date,
    glacier: str = "SE_Alaska_AK",
    control: str = "Interior_AK_ctrl",
    allow_unplanned: bool = False,
) -> dict[str, Any]:
    """C2 at a preregistered look. ``allow_unplanned=True`` evaluates any exclusive end
    (descriptive only: alpha NaN, never rejects), e.g. for yearly monitoring."""
    if allow_unplanned:
        try:
            look_end = resolve_look(look_end)
        except ValueError:
            look_end = float(look_end)  # type: ignore[arg-type]
    else:
        look_end = resolve_look(look_end)
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
