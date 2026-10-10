"""Catalogue-robustness checks for v0.2 (M1): alternative Mc estimator, Mc bootstrap,
alternative declustering. None of these changes a v0.1.0 frozen parameter; they quantify how
much the v0.1.0 results (F1, Habermann z) depend on the Mc / declustering choices.

* EMR-type completeness after Ogata & Katsura (1993, GJI 113:727,
  doi:10.1111/j.1365-246X.1993.tb04663.x): f(m) ~ 10^(-b m) * Phi((m - mu)/sigma) over all
  magnitudes; Mc := mu + 2 sigma (detection probability 97.7 %). (Woessner & Wiemer 2005,
  BSSA 95:684, doi:10.1785/0120040007, use the related EMR method.)
* Bootstrap of Mc (MAXC+0.2 and EMR), 200 resamples by default.
* Gardner & Knopoff (1974, BSSA 64:1363) window declustering with the windows as tabulated in
  van Stiphout, Zhuang & Marsan (2012, CORSSA, doi:10.5078/corssa-52382934):
  L = 10^(0.1238 M + 0.983) km, T = 10^(0.032 M + 2.7389) d (M >= 6.5) else 10^(0.5409 M - 0.547) d.
  Implementation: events processed by decreasing magnitude; every not-yet-assigned smaller
  event within L and within T after (aftershocks) or before (foreshocks) is removed.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, stats

from .catalog import haversine_km, mc_maxc


def _emr_negll(theta: np.ndarray, counts: np.ndarray, grid: np.ndarray) -> float:
    """Binned (multinomial) negative log-likelihood; counts per magnitude bin of ``grid``."""
    b, mu, lsig = theta
    if not (0.3 < b < 3.0):
        return 1e12
    sig = np.exp(lsig)
    beta = b * np.log(10)
    lg = -beta * grid + stats.norm.logcdf((grid - mu) / sig)
    lnorm = float(np.log(np.sum(np.exp(lg - lg.max()))) + lg.max())
    return float(-(np.sum(counts * lg) - counts.sum() * lnorm))


def mc_emr(m: np.ndarray, dm: float = 0.1) -> dict[str, float]:
    """Ogata-Katsura detection-function fit; returns Mc = mu + 2 sigma (rounded to dm)."""
    m = np.round(np.asarray(m, float) / dm) * dm
    m = m[np.isfinite(m)]
    if len(m) < 50:
        return dict(mc=np.nan, b=np.nan, mu=np.nan, sigma=np.nan, n=float(len(m)))
    grid = np.round(np.arange(float(np.min(m)) - 1.0, float(np.max(m)) + dm / 2, dm), 6)
    idx = np.clip(np.round((m - grid[0]) / dm).astype(int), 0, len(grid) - 1)
    counts = np.bincount(idx, minlength=len(grid)).astype(float)
    mc0 = mc_maxc(m, 0.0)
    best = None
    for s0 in (0.1, 0.3):
        r = optimize.minimize(
            _emr_negll,
            np.array([1.0, mc0, np.log(s0)]),
            args=(counts, grid),
            method="Nelder-Mead",
            options=dict(xatol=1e-4, fatol=1e-6, maxiter=4000),
        )
        if best is None or r.fun < best.fun:
            best = r
    assert best is not None
    b, mu, lsig = best.x
    sig = float(np.exp(lsig))
    mc = float(np.round((mu + 2 * sig) / dm) * dm)
    return dict(mc=mc, b=float(b), mu=float(mu), sigma=sig, n=float(len(m)))


def mc_bootstrap(
    m: np.ndarray, method: str = "maxc", n_boot: int = 200, rng: np.random.Generator | None = None
) -> dict[str, float]:
    """Bootstrap distribution of Mc ('maxc' = MAXC+0.2, 'emr')."""
    rng = rng or np.random.default_rng(20261010)
    m = np.asarray(m, float)

    def f(x: np.ndarray) -> float:
        return mc_maxc(x) if method == "maxc" else float(mc_emr(x)["mc"])

    vals = np.array([f(rng.choice(m, len(m), replace=True)) for _ in range(n_boot)])
    vals = vals[np.isfinite(vals)]
    if not len(vals):
        return dict(mean=np.nan, sd=np.nan, q025=np.nan, q975=np.nan, n_boot=0.0)
    return dict(
        mean=float(vals.mean()),
        sd=float(vals.std(ddof=1)) if len(vals) > 1 else 0.0,
        q025=float(np.quantile(vals, 0.025)),
        q975=float(np.quantile(vals, 0.975)),
        n_boot=float(len(vals)),
    )


def reference_mc_emr(df: pd.DataFrame, quantile: float = 0.9) -> tuple[float, pd.Series]:
    """As catalog.reference_mc (90 % quantile of yearly Mc), with EMR instead of MAXC+0.2."""
    ym = df.groupby("year").mag.apply(lambda x: mc_emr(x.to_numpy())["mc"]).dropna()
    if not len(ym):
        return float("nan"), ym
    return float(np.round(np.nanquantile(ym.values, quantile), 1)), ym


def gk_windows(m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Gardner-Knopoff distance [km] and time [days] windows."""
    m = np.asarray(m, float)
    L = 10 ** (0.1238 * m + 0.983)
    T = np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))
    return L, T


def gardner_knopoff(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with boolean column 'triggered' (True = removed by the GK windows)."""
    d = df.sort_values("time").reset_index(drop=True).copy()
    t = d.t_yr.to_numpy(float) * 365.25
    la, lo, m = (d[c].to_numpy(float) for c in ("latitude", "longitude", "mag"))
    L, T = gk_windows(m)
    removed = np.zeros(len(d), bool)
    for i in np.argsort(-m, kind="stable"):
        if removed[i]:
            continue
        a = int(np.searchsorted(t, t[i] - T[i], "left"))
        b = int(np.searchsorted(t, t[i] + T[i], "right"))
        idx = np.arange(a, b)
        idx = idx[(idx != i) & ~removed[idx] & (m[idx] <= m[i])]
        if not len(idx):
            continue
        r = haversine_km(la[idx], lo[idx], la[i], lo[i])
        removed[idx[r <= L[i]]] = True
    d["triggered"] = removed
    return d
