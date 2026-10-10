"""Experiment B: seismic quiescence and its classification (apparent vs genuine relaxation).

Two standard quiescence statistics, computed on the same declustering/completeness as the main
analysis:

* Relative quiescence against a temporal ETAS model (Ogata 1988, JASA,
  doi:10.1080/01621459.1988.10478560; Ogata 1992, JGR 97:19845, doi:10.1029/92JB00708):
  ETAS is fitted by maximum likelihood to all events >= Mc in a fit window, then extrapolated
  over a test window (triggering from the observed events included). z = (N - L)/sqrt(L), with
  L the predicted number. Overdispersion beyond ETAS makes |z| anti-conservative: z < -2 is
  treated as a flag, not as a p-value.
* Habermann's z for the change of the declustered annual rate between two periods
  (Habermann 1988, doi:10.1007/BF00879000; Wyss & Habermann 1988, doi:10.1007/BF00879001).

Catalogue checks before a quiescence is interpreted (Habermann 1991, Tectonophysics,
doi:10.1016/0040-1951(91)90337-R): change of the yearly completeness Mc and a two-sample KS
test of the magnitudes >= Mc between the periods.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats

DAY = 1.0 / 365.25


def _pairs(t: np.ndarray, tmax: float) -> tuple[np.ndarray, np.ndarray]:
    """Index pairs (i, j), j < i, with 0 < t_i - t_j <= tmax (years)."""
    lo = np.searchsorted(t, t - tmax, side="left")
    counts = np.arange(len(t)) - lo
    ii = np.repeat(np.arange(len(t)), counts)
    start = np.repeat(lo, counts)
    first = np.repeat(np.cumsum(counts) - counts, counts)
    jj = start + (np.arange(len(ii)) - first)
    return ii, jj.astype(int)


def _int_kernel(dt: np.ndarray, c: float, p: float, tmax: float) -> np.ndarray:
    d = np.clip(dt, 0.0, tmax)
    if abs(p - 1.0) < 1e-6:
        return np.asarray(np.log((d + c) / c))
    return np.asarray((c ** (1 - p) - (d + c) ** (1 - p)) / (p - 1))


def etas_loglik(
    theta: np.ndarray,
    t: np.ndarray,
    m: np.ndarray,
    mc: float,
    t0: float,
    t1: float,
    pairs: tuple[np.ndarray, np.ndarray],
    tmax: float,
) -> float:
    mu, k, alpha, c, p = np.exp(theta[0]), np.exp(theta[1]), theta[2], np.exp(theta[3]), theta[4]
    ii, jj = pairs
    dt_pairs = t[ii] - t[jj]
    prod = k * np.exp(alpha * (m - mc))
    trig = np.bincount(ii, weights=prod[jj] * (dt_pairs + c) ** (-p), minlength=len(t))
    target = (t >= t0) & (t < t1)
    lam = mu + trig[target]
    integral = mu * (t1 - t0) + np.sum(
        prod * (_int_kernel(t1 - t, c, p, tmax) - _int_kernel(t0 - t, c, p, tmax))
    )
    return float(np.sum(np.log(lam)) - integral)


def fit_etas(
    t: np.ndarray, m: np.ndarray, mc: float, t0: float, t1: float, tmax: float = 1.0
) -> dict[str, float]:
    """Temporal ETAS MLE on [t0, t1) (years); events before t0 act only as triggers."""
    sel = t < t1
    t, m = t[sel], m[sel]
    pairs = _pairs(t, tmax)
    n = int(((t >= t0) & (t < t1)).sum())
    x0 = np.array([np.log(0.5 * n / (t1 - t0)), np.log(0.02), 1.0, np.log(0.01 * 1.0), 1.1])
    bounds = [(None, None), (None, None), (0.0, 3.0), (np.log(1e-5), np.log(0.5)), (1.0001, 2.0)]

    def nll(th: np.ndarray) -> float:
        v = -etas_loglik(th, t, m, mc, t0, t1, pairs, tmax)
        return v if np.isfinite(v) else 1e12

    best = None
    for a0 in (0.5, 1.5):
        x0[2] = a0
        r = optimize.minimize(nll, x0, method="L-BFGS-B", bounds=bounds)
        if best is None or r.fun < best.fun:
            best = r
    assert best is not None
    th = best.x
    return dict(
        mu_per_yr=float(np.exp(th[0])),
        K=float(np.exp(th[1])),
        alpha=float(th[2]),
        c_days=float(np.exp(th[3]) / DAY),
        p=float(th[4]),
        loglik=float(-best.fun),
        n_fit=n,
        converged=bool(best.success),
    )


def etas_expected(
    par: dict[str, float],
    t: np.ndarray,
    m: np.ndarray,
    mc: float,
    a: float,
    b: float,
    tmax: float = 1.0,
) -> float:
    """Expected number of events >= Mc in [a, b) given all observed events before them."""
    c = par["c_days"] * DAY
    prod = par["K"] * np.exp(par["alpha"] * (m - mc))
    sel = t < b
    return float(
        par["mu_per_yr"] * (b - a)
        + np.sum(
            prod[sel]
            * (
                _int_kernel(b - t[sel], c, par["p"], tmax)
                - _int_kernel(a - t[sel], c, par["p"], tmax)
            )
        )
    )


def habermann_z(counts_a: np.ndarray, counts_b: np.ndarray) -> float:
    """z = (mean_b - mean_a) / sqrt(var_a/n_a + var_b/n_b) of annual counts (b = later)."""
    a, b = np.asarray(counts_a, float), np.asarray(counts_b, float)
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return float((b.mean() - a.mean()) / se) if se > 0 else float("nan")


def decimal_year(time: pd.Series) -> np.ndarray:
    tt = pd.to_datetime(time, utc=True)
    y = tt.dt.year.to_numpy()
    start = pd.to_datetime(pd.Series(y.astype(str)) + "-01-01", utc=True)
    end = pd.to_datetime(pd.Series((y + 1).astype(str)) + "-01-01", utc=True)
    frac = (tt.reset_index(drop=True) - start) / (end - start)
    return np.asarray(y + frac.to_numpy(float), dtype=float)


def region_quiescence(
    name: str,
    dc: pd.DataFrame,
    mc: float,
    mc_yearly: pd.Series,
    fit: tuple[float, float] = (1995.0, 2014.5),
    tests: tuple[tuple[float, float], ...] = ((2016.0, 2020.0), (2020.0, 2026.0)),
    hab: tuple[tuple[int, int], tuple[int, int]] = ((2008, 2019), (2020, 2025)),
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """ETAS relative-quiescence z per test window + Habermann z + catalogue checks."""
    d = dc.sort_values("time")
    t = decimal_year(d.time)
    m = d.mag.to_numpy(float)
    par = fit_etas(t, m, mc, *fit)
    rows = []
    for a, b in tests:
        lam = etas_expected(par, t, m, mc, a, b)
        n = int(((t >= a) & (t < b)).sum())
        rows.append(
            dict(
                region=name,
                window=f"{a:.0f}-{b:.0f}",
                n_obs=n,
                n_etas_expected=lam,
                ratio=n / lam if lam > 0 else np.nan,
                z_etas=(n - lam) / np.sqrt(lam) if lam > 0 else np.nan,
            )
        )
    decl = d[~d.triggered]
    yrs = decl.time.dt.year
    (a0, a1), (b0, b1) = hab
    ca = yrs.value_counts().reindex(range(a0, a1 + 1), fill_value=0).to_numpy()
    cb = yrs.value_counts().reindex(range(b0, b1 + 1), fill_value=0).to_numpy()
    ma = d.mag[d.time.dt.year.between(a0, a1)].to_numpy()
    mb = d.mag[d.time.dt.year.between(b0, b1)].to_numpy()
    ks = stats.ks_2samp(ma, mb) if len(ma) > 10 and len(mb) > 10 else None
    summ = dict(
        region=name,
        mc=mc,
        **{f"etas_{k}": v for k, v in par.items()},
        habermann_z=habermann_z(ca, cb),
        decl_rate_a=float(ca.mean()),
        decl_rate_b=float(cb.mean()),
        mc_median_a=float(mc_yearly.loc[a0:a1].median()),
        mc_median_b=float(mc_yearly.loc[b0:b1].median()),
        mean_mag_a=float(ma.mean()) if len(ma) else np.nan,
        mean_mag_b=float(mb.mean()) if len(mb) else np.nan,
        ks_p_mag=float(ks.pvalue) if ks is not None else np.nan,
    )
    return pd.DataFrame(rows), summ


def classify(
    quiet: bool, artefact: bool, load_accelerating: bool | None, uplift_accelerating: bool | None
) -> str:
    """Pre-registered decision rule (docs/PREREGISTRATION.md section 6, hypothesis B)."""
    if not quiet:
        return "no quiescence"
    if artefact:
        return "catalogue artefact suspected"
    if load_accelerating is None:
        return "quiescence, load trend unknown"
    if load_accelerating or uplift_accelerating:
        return "candidate deceptive (pre-tipping) quiet"
    return "consistent with genuine relaxation / decelerating load"
