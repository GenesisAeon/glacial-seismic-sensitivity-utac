"""'Fruehstadium' (early-stage) sensitivity tests -- the core of this package.

Idea (J. Roemer): if the crust under shrinking glaciers is drifting towards failure, the
*same* seasonal unloading should trigger *more* earthquakes over time, even while the mean
rate shows no trend. We therefore test the change of the seasonal response, not the trend.

F1 (harmonic, 1990-2025)
    log mu_t = alpha_year(t) + (b0 + b1 * tau_t) * cos(2 pi (m_t - phi) / 12)
    tau_t = (decimal year - 2008) / 10. b0: relative seasonal modulation (~amplitude),
    b1: change of that modulation per decade. H_F1: b1 > 0.
F2 (load-based, GRACE 2002-2025, lag 3 months pre-registered)
    log mu_t = alpha_year(t) + (g0 + g1 * tau_t) * U_{t-lag}
    U = seasonal unloading anomaly [kPa]. g0: fractional rate change per kPa ("sensitivity"),
    g1: its change per decade. H_F2: g1 > 0.
F3 (rain vs. load) -- quasi-AIC comparison of load-only, rain-only and joint models.

Year fixed effects absorb all year-to-year rate changes (network changes, aftershock-poor
years, ...); only within-year contrasts remain. Significance: quasi-Poisson Wald test and a
permutation test that shuffles the year -> tau assignment (keeps every year's 12 months intact).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from . import config as C
from .glm import GLMResult, fit_poisson_fe
from .indicators import schuster


def monthly_table(d: pd.DataFrame, y0: int, y1: int) -> pd.DataFrame:
    """Monthly counts of (declustered) events, calendar months y0-01 .. y1-12."""
    idx = pd.period_range(f"{y0}-01", f"{y1}-12", freq="M")
    if len(d):
        c = d.groupby(d.time.dt.tz_localize(None).dt.to_period("M")).size()
    else:
        c = pd.Series(dtype=float)
    c = c.reindex(idx, fill_value=0)
    out = pd.DataFrame({"period": idx, "count": c.to_numpy(float)})
    out["year"] = out.period.dt.year
    out["m"] = out.period.dt.month
    out["t_dec"] = out.year + (out.m - 0.5) / 12
    out["tau"] = (out.t_dec - C.SENS_REF_YEAR) / 10.0
    out["month"] = out.period.dt.to_timestamp()
    return out


def _perm_p(
    stat_fn: Callable[[np.ndarray], float],
    tab: pd.DataFrame,
    obs: float,
    rng: np.random.Generator,
    n: int,
) -> tuple[float, float]:
    years = np.unique(tab.year)
    tau_year = {y: (y + 0.5 - C.SENS_REF_YEAR) / 10.0 for y in years}
    within = tab.tau.to_numpy() - tab.year.map(tau_year).to_numpy()
    ge = absge = 0
    vals = np.array([tau_year[y] for y in years])
    for _ in range(n):
        perm = dict(zip(years, rng.permutation(vals), strict=True))
        tau_p = tab.year.map(perm).to_numpy() + within
        s = stat_fn(tau_p)
        ge += s >= obs
        absge += abs(s) >= abs(obs)
    return (ge + 1) / (n + 1), (absge + 1) / (n + 1)


def harmonic_growth(
    d: pd.DataFrame,
    years: tuple[int, int] = (1990, C.TEST_END_YEAR),
    rng: np.random.Generator | None = None,
    n_perm: int = C.SENS_N_PERM,
    phase: float | None = None,
) -> dict[str, float]:
    """F1: growth of seasonal modulation along the region's mean phase."""
    rng = rng or np.random.default_rng(C.SEED)
    sel = d[d.year.between(*years)]
    tab = monthly_table(sel, *years)
    amp, p_s, ph = schuster(sel.t_yr.to_numpy())
    ph = ph if phase is None else phase
    x = np.cos(2 * np.pi * ((tab.m.to_numpy() - 0.5) / 12 - ph))

    def fit(tau: np.ndarray) -> GLMResult:
        return fit_poisson_fe(
            tab["count"].to_numpy(), tab.year.to_numpy(), np.column_stack([x, x * tau])
        )

    res = fit(tab.tau.to_numpy())
    out = dict(
        n_events=float(len(sel)),
        schuster_amp=amp,
        schuster_p=p_s,
        peak_month=ph * 12 + 1,
        b0=float(res.coef[0]),
        b0_se=float(res.se[0]),
        b1_per_decade=float(res.coef[1]),
        b1_se=float(res.se[1]),
        b1_p_wald_one=res.p_one_sided(1),
        b1_p_wald_two=res.p_two_sided(1),
        phi=res.phi,
    )
    if n_perm > 0 and len(sel) >= 30:
        p1, p2 = _perm_p(
            lambda tau: float(fit(tau).coef[1]), tab, out["b1_per_decade"], rng, n_perm
        )
        out.update(b1_p_perm_one=p1, b1_p_perm_two=p2)
    return out


def per_year_modulation(d: pd.DataFrame, phase: float, years: tuple[int, int]) -> pd.DataFrame:
    """Seasonal modulation b_y fitted separately per year (12 months) along a fixed phase."""
    rows = []
    for y in range(years[0], years[1] + 1):
        tab = monthly_table(d[d.year == y], y, y)
        if tab["count"].sum() < 10:
            rows.append(dict(year=y, b=np.nan, se=np.nan, n=int(tab["count"].sum())))
            continue
        x = np.cos(2 * np.pi * ((tab.m.to_numpy() - 0.5) / 12 - phase))
        r = fit_poisson_fe(tab["count"].to_numpy(), tab.year.to_numpy(), x[:, None])
        rows.append(dict(year=y, b=float(r.coef[0]), se=float(r.se[0]), n=int(tab["count"].sum())))
    return pd.DataFrame(rows)


def _join_covariates(
    tab: pd.DataFrame, load: pd.DataFrame | None, precip: pd.DataFrame | None, lag: int
) -> pd.DataFrame:
    t = tab.copy()
    if load is not None:
        lo = load.set_index("month")["unload_kPa"]
        t["U"] = t.month.map(lo.shift(lag, freq="MS"))
    if precip is not None:
        pr = precip.set_index("month")
        for k in ("rain_mm_anom", "snowfall_cm_anom", "precip_mm_anom"):
            if k in pr:
                t[k] = t.month.map(pr[k].shift(lag, freq="MS"))
    return t


def load_growth(
    d: pd.DataFrame,
    load: pd.DataFrame,
    lag: int = C.SENS_LAG_MONTHS_PRIMARY,
    years: tuple[int, int] = (2002, C.TEST_END_YEAR),
    rng: np.random.Generator | None = None,
    n_perm: int = C.SENS_N_PERM,
) -> dict[str, float]:
    """F2: sensitivity per kPa of seasonal unloading and its change per decade."""
    rng = rng or np.random.default_rng(C.SEED + 2)
    sel = d[d.year.between(*years)]
    tab = _join_covariates(monthly_table(sel, *years), load, None, lag).dropna(subset=["U"])

    def fit(tau: np.ndarray) -> GLMResult:
        u = tab.U.to_numpy()
        return fit_poisson_fe(
            tab["count"].to_numpy(), tab.year.to_numpy(), np.column_stack([u, u * tau])
        )

    res = fit(tab.tau.to_numpy())
    out = dict(
        lag_months=float(lag),
        n_months=float(len(tab)),
        n_events=float(tab["count"].sum()),
        U_sd_kPa=float(tab.U.std()),
        g0_per_kPa=float(res.coef[0]),
        g0_se=float(res.se[0]),
        g0_p_wald_one=res.p_one_sided(0),
        g1_per_kPa_decade=float(res.coef[1]),
        g1_se=float(res.se[1]),
        g1_p_wald_one=res.p_one_sided(1),
        g1_p_wald_two=res.p_two_sided(1),
        phi=res.phi,
    )
    if n_perm > 0 and len(tab) >= 24:
        p1, p2 = _perm_p(
            lambda tau: float(fit(tau).coef[1]), tab, out["g1_per_kPa_decade"], rng, n_perm
        )
        out.update(g1_p_perm_one=p1, g1_p_perm_two=p2)
    return out


def rain_vs_load(
    d: pd.DataFrame,
    load: pd.DataFrame | None,
    precip: pd.DataFrame,
    lag: int = C.SENS_LAG_MONTHS_PRIMARY,
    years: tuple[int, int] = (2002, C.TEST_END_YEAR),
) -> pd.DataFrame:
    """F3: compare seasonal regressors (common months) by quasi-AIC; dQAIC < -2 favours a model."""
    sel = d[d.year.between(*years)]
    tab = _join_covariates(monthly_table(sel, *years), load, precip, lag)
    cols = [c for c in ("U", "rain_mm_anom", "snowfall_cm_anom") if c in tab]
    tab = tab.dropna(subset=cols)
    if len(tab) < 24:
        return pd.DataFrame()
    y, g = tab["count"].to_numpy(), tab.year.to_numpy()
    specs: dict[str, list[str]] = {"null(year FE only)": []}
    for c in cols:
        specs[c] = [c]
    if "U" in cols and "rain_mm_anom" in cols:
        specs["U + rain"] = ["U", "rain_mm_anom"]
    if len(cols) == 3:
        specs["U + rain + snowfall"] = cols
    std = {c: float(tab[c].std()) for c in cols}
    full = fit_poisson_fe(y, g, tab[cols].to_numpy() / np.array([std[c] for c in cols]))
    rows = []
    for name, cs in specs.items():
        xr = (tab[cs].to_numpy() / np.array([std[c] for c in cs])) if cs else np.zeros((len(y), 0))
        r = fit_poisson_fe(y, g, xr)
        row: dict[str, float | str] = dict(model=name, k=r.k, qaic=r.qaic(full.phi), phi=r.phi)
        for i, c in enumerate(cs):
            row[f"coef_per_sd_{c}"] = float(r.coef[i])
            row[f"z_{c}"] = float(r.z()[i])
        rows.append(row)
    df = pd.DataFrame(rows)
    df["dQAIC_vs_null"] = df.qaic - float(df.loc[df.model == "null(year FE only)", "qaic"].iloc[0])
    corr = tab[cols].corr()
    df["lag_months"] = lag
    df["n_months"] = len(tab)
    if "U" in cols and "rain_mm_anom" in cols:
        df["corr_U_rain"] = float(corr.loc["U", "rain_mm_anom"])
    return df


def lag_scan(
    d: pd.DataFrame,
    load: pd.DataFrame,
    lags: range | tuple[int, ...] = range(0, 9),
    years: tuple[int, int] = (2002, C.TEST_END_YEAR),
) -> pd.DataFrame:
    """Exploratory: sensitivity g0 for a range of lags (no permutation)."""
    rows = []
    for lag in lags:
        r = load_growth(d, load, lag=lag, years=years, n_perm=0)
        rows.append(
            dict(
                lag_months=lag,
                g0_per_kPa=r["g0_per_kPa"],
                g0_se=r["g0_se"],
                z=r["g0_per_kPa"] / r["g0_se"],
            )
        )
    return pd.DataFrame(rows)


def meta_group(df: pd.DataFrame, coef: str, se: str) -> dict[str, float]:
    """Inverse-variance pooled estimate (fixed effect) with Cochran's Q heterogeneity."""
    x = df[[coef, se]].dropna()
    if not len(x):
        return dict(pooled=np.nan, pooled_se=np.nan, z=np.nan, n=0, Q=np.nan)
    w = 1 / x[se] ** 2
    est = float((w * x[coef]).sum() / w.sum())
    s = float(np.sqrt(1 / w.sum()))
    q = float((w * (x[coef] - est) ** 2).sum())
    return dict(pooled=est, pooled_se=s, z=est / s, n=len(x), Q=q)
