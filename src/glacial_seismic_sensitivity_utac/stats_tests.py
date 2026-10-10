"""Significance machinery.

- IAAFT surrogates (Schreiber & Schmitz 1996, PRL 77:635) for CSD trend statistics
- block permutation for binned-indicator trends
- Benjamini & Hochberg (1995) false discovery rate
- exact label-permutation test for group differences
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from . import config as C
from .indicators import detrend, kendall, rolling_from_resid

CSD_KEYS = ("variance", "ar1", "skewness", "kurtosis", "recovery_rate")


def iaaft(x: np.ndarray, rng: np.random.Generator, n_iter: int = 30) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    amp = np.abs(np.fft.rfft(x))
    sorted_x = np.sort(x)
    y = rng.permutation(x)
    for _ in range(n_iter):
        spec = np.fft.rfft(y)
        y = np.fft.irfft(amp * np.exp(1j * np.angle(spec)), n=len(x))
        y = sorted_x[np.argsort(np.argsort(y))]
    return np.asarray(y)


def csd_surrogate_test(
    x: np.ndarray, rng: np.random.Generator, n: int = C.N_SURROGATES
) -> tuple[dict[str, tuple[float, float]], pd.DataFrame]:
    resid = detrend(np.asarray(x, dtype=float))
    obs = rolling_from_resid(resid)
    tau_obs = {k: kendall(obs[k]) for k in CSD_KEYS}
    taus: dict[str, list[float]] = {k: [] for k in CSD_KEYS}
    for _ in range(n):
        ind = rolling_from_resid(iaaft(resid, rng))
        for k in CSD_KEYS:
            taus[k].append(kendall(ind[k]))
    out: dict[str, tuple[float, float]] = {}
    for k in CSD_KEYS:
        t = np.array(taus[k])
        t = t[np.isfinite(t)]
        if np.isfinite(tau_obs[k]) and len(t):
            p = float((np.sum(np.abs(t) >= abs(tau_obs[k])) + 1) / (len(t) + 1))
        else:
            p = float("nan")
        out[k] = (tau_obs[k], p)
    return out, obs


def block_perm_test(
    y: np.ndarray | pd.Series,
    rng: np.random.Generator,
    n: int = C.N_BLOCK_PERM,
    block: int = C.BLOCK_LEN,
) -> tuple[float, float]:
    v = pd.Series(y).dropna().to_numpy(float)
    if len(v) < 6:
        return float("nan"), float("nan")
    t_obs = kendall(v)
    if not np.isfinite(t_obs):
        return float("nan"), float("nan")
    blocks = [v[i : i + block] for i in range(0, len(v), block)]
    cnt = 0
    for _ in range(n):
        perm = np.concatenate([blocks[i] for i in rng.permutation(len(blocks))])
        if abs(kendall(perm)) >= abs(t_obs):
            cnt += 1
    return t_obs, (cnt + 1) / (n + 1)


def bh(p: np.ndarray | list[float], alpha: float = C.ALPHA) -> tuple[np.ndarray, np.ndarray]:
    pa = np.asarray(p, dtype=float)
    ok = np.isfinite(pa)
    q = np.full(len(pa), np.nan)
    pv = pa[ok]
    m = len(pv)
    if m == 0:
        return q, np.zeros(len(pa), dtype=bool)
    o = np.argsort(pv)
    ranked = pv[o] * m / np.arange(1, m + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    qq = np.empty(m)
    qq[o] = np.minimum(ranked, 1)
    q[ok] = qq
    return q, np.asarray(q <= alpha)


def group_perm(values: dict[str, float], is_target: dict[str, bool]) -> tuple[float, float, int]:
    """Exact permutation test of mean(target) - mean(rest) over all label assignments."""
    regs = [r for r in values if np.isfinite(values[r]) and r in is_target]
    v = np.array([values[r] for r in regs])
    g = np.array([is_target[r] for r in regs])
    if g.sum() < 2 or (~g).sum() < 2:
        return float("nan"), float("nan"), len(regs)
    obs = float(v[g].mean() - v[~g].mean())
    k = int(g.sum())
    cnt = tot = 0
    for comb in itertools.combinations(range(len(v)), k):
        mask = np.zeros(len(v), dtype=bool)
        mask[list(comb)] = True
        tot += 1
        if abs(v[mask].mean() - v[~mask].mean()) >= abs(obs) - 1e-12:
            cnt += 1
    return obs, cnt / tot, len(regs)
