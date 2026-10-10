"""Nearest-neighbour cluster analysis.

Zaliapin & Ben-Zion 2013, JGR 118:2847, doi:10.1002/jgrb.50179.

eta_ij = t_ij * r_ij^df * 10^(-b m_i); threshold eta0 from a two-component Gaussian mixture
of log10(eta). Fallback -5 when the distribution is not bimodal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .catalog import haversine_km


def nearest_neighbour(
    df: pd.DataFrame, max_parents: int = C.NN_MAX_PARENTS
) -> tuple[np.ndarray, np.ndarray]:
    t = df.t_yr.to_numpy(float)
    la = df.latitude.to_numpy(float)
    lo = df.longitude.to_numpy(float)
    m = df.mag.to_numpy(float)
    n = len(df)
    eta = np.full(n, np.inf)
    parent = np.full(n, -1, dtype=int)
    for j in range(1, n):
        j0 = max(0, j - max_parents)
        dt = t[j] - t[j0:j]
        ok = dt > 0
        if not ok.any():
            continue
        idx = np.nonzero(ok)[0] + j0
        r = np.maximum(haversine_km(la[idx], lo[idx], la[j], lo[j]), 0.1)
        e = dt[ok] * r**C.NN_DF * 10 ** (-C.NN_B * m[idx])
        k = int(np.argmin(e))
        eta[j] = e[k]
        parent[j] = idx[k]
    return eta, parent


def gmm_threshold(logeta: np.ndarray) -> float:
    """Crossing point of a 2-Gaussian EM mixture; -5 if not bimodal; NaN if < 50 events."""
    x = logeta[np.isfinite(logeta)]
    if len(x) < 50:
        return float("nan")
    mu = np.quantile(x, [0.2, 0.8])
    sd = np.array([x.std(), x.std()]) / 2
    w = np.array([0.5, 0.5])
    for _ in range(300):
        p = np.vstack([w[k] * np.exp(-0.5 * ((x - mu[k]) / sd[k]) ** 2) / sd[k] for k in range(2)])
        p /= p.sum(0)
        w = p.mean(1)
        mu = (p * x).sum(1) / p.sum(1)
        sd = np.sqrt((p * (x - mu[:, None]) ** 2).sum(1) / p.sum(1)) + 1e-6
    lo_k, hi_k = np.argsort(mu)
    grid = np.linspace(mu[lo_k], mu[hi_k], 2000)

    def dens(k: int) -> np.ndarray:
        return np.asarray(w[k] * np.exp(-0.5 * ((grid - mu[k]) / sd[k]) ** 2) / sd[k])

    d = dens(int(lo_k)) - dens(int(hi_k))
    cross = np.nonzero(np.diff(np.sign(d)) != 0)[0]
    if abs(mu[hi_k] - mu[lo_k]) < 1.0 or not len(cross):
        return -5.0
    return float(grid[cross[0]])


def decluster(df: pd.DataFrame, threshold: float | None = None) -> tuple[pd.DataFrame, float]:
    """Adds log_eta, parent, triggered, cluster_id. Returns (df, log10 eta0).

    ``threshold``: use a fixed (frozen) log10 eta0 instead of fitting the mixture."""
    df = df.reset_index(drop=True).copy()
    eta, parent = nearest_neighbour(df)
    with np.errstate(divide="ignore"):
        le = np.log10(eta)
    thr = gmm_threshold(le) if threshold is None else float(threshold)
    trig = np.isfinite(le) & (le < thr)
    df["log_eta"] = le
    df["parent"] = np.where(trig, parent, -1)
    df["triggered"] = trig
    root = np.arange(len(df))
    par = df.parent.to_numpy()
    for j in range(len(df)):
        if par[j] >= 0:
            root[j] = root[par[j]]
    df["cluster_id"] = root
    return df, thr


def cluster_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cid, s in df.groupby("cluster_id"):
        if len(s) < 2:
            continue
        s = s.sort_values("time")
        i_max = int(np.argmax(s.mag.to_numpy()))
        rows.append(
            dict(
                cluster_id=cid,
                start=s.time.iloc[0],
                year=s.time.iloc[0].year,
                size=len(s),
                m_max=float(s.mag.max()),
                rank_of_max=i_max / len(s),
                n_after_main=len(s) - i_max - 1,
                duration_days=(s.time.iloc[-1] - s.time.iloc[0]).total_seconds() / 86400,
            )
        )
    cols = [
        "cluster_id",
        "start",
        "year",
        "size",
        "m_max",
        "rank_of_max",
        "n_after_main",
        "duration_days",
        "swarm_like",
    ]
    ct = pd.DataFrame(rows, columns=cols[:-1])
    ct["swarm_like"] = (ct["size"] >= C.SWARM_MIN_SIZE) & (ct.rank_of_max > 0.2)
    return ct[cols]
