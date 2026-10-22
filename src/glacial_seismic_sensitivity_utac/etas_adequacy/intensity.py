"""AP1: conditional intensity, compensator and transformed times of the frozen temporal ETAS.

Model (decimal years, events >= mc, exactly the C2 null model of ``etas_nonstat``):

    lambda(t) = mu + sum_{t_j < t, t - t_j <= tmax} K exp(alpha (m_j - mc)) (t - t_j + c)^(-p)

with a *constant* mu on the evaluation window. Events before the window (history) act only as
triggers. The Omori integral uses the unchanged ``etas_nonstat.kint`` (truncated at tmax), so this
module and the frozen fit share one definition of the kernel.

Compensator: Lambda(a, b) = mu (b - a) + sum_{t_j < b} w_j [kint(b - t_j) - kint(a - t_j)],
w_j = K exp(alpha (m_j - mc)); kint(d) = 0 for d <= 0, so events after a contribute only from t_j.
Under the model, the transformed inter-event times Lambda(t_{i-1}, t_i) of the window events are
i.i.d. Exp(1) (random time change, Ogata 1988).
"""

from __future__ import annotations

import numpy as np

from ..etas_nonstat import kint
from .frozen import Baseline


def _sorted(t: np.ndarray, m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(t, float)
    m = np.asarray(m, float)
    if t.shape != m.shape or t.ndim != 1:
        raise ValueError("t and m must be 1-D arrays of equal length")
    if not (np.all(np.isfinite(t)) and np.all(np.isfinite(m))):
        raise ValueError("t and m must be finite")
    o = np.argsort(t, kind="stable")
    return t[o], m[o]


def weights(m: np.ndarray, base: Baseline) -> np.ndarray:
    """Productivity w_j = K exp(alpha (m_j - mc_ref))."""
    return np.asarray(base.K * np.exp(base.alpha * (np.asarray(m, float) - base.mc_ref)))


def intensity(
    t_eval: np.ndarray, t: np.ndarray, m: np.ndarray, base: Baseline, mu: float
) -> np.ndarray:
    """lambda(t) at each evaluation time from all events strictly earlier (within tmax).

    Simultaneous events do not trigger each other (dt > 0), as in ``etas_nonstat.pairs``."""
    if mu < 0:
        raise ValueError("mu must be >= 0")
    t, m = _sorted(t, m)
    te = np.atleast_1d(np.asarray(t_eval, float))
    w = weights(m, base)
    out = np.full(te.shape, float(mu))
    for k, x in enumerate(te):
        dt = x - t
        sel = (dt > 0) & (dt <= base.tmax_yr)
        if sel.any():
            out[k] += float(np.sum(w[sel] * (dt[sel] + base.c_yr) ** (-base.p)))
    return out


def compensator(
    a: float, b: float, t: np.ndarray, m: np.ndarray, base: Baseline, mu: float
) -> float:
    """Lambda(a, b): expected number of events >= mc on [a, b), given the earlier history."""
    if b < a:
        raise ValueError("need a <= b")
    if mu < 0:
        raise ValueError("mu must be >= 0")
    t, m = _sorted(t, m)
    sel = t < b
    t, m = t[sel], m[sel]
    w = weights(m, base)
    trig = w * (
        kint(b - t, base.c_yr, base.p, base.tmax_yr) - kint(a - t, base.c_yr, base.p, base.tmax_yr)
    )
    return float(mu * (b - a) + np.sum(trig))


def transformed_times(
    t: np.ndarray, m: np.ndarray, window: tuple[float, float], base: Baseline, mu: float
) -> tuple[np.ndarray, float]:
    """Transformed times tau_i = Lambda(t0, t_i) of the window events, and Lambda(t0, t1).

    ``t, m`` contain the history (before t0) and the window events; events at or after t1 are
    ignored. Under the model, diff([0, tau]) are i.i.d. Exp(1) and Lambda(t0, t1) is the expected
    count (the number of events is Poisson-like only for mu-dominated windows)."""
    t0, t1 = window
    if not t0 < t1:
        raise ValueError("window must satisfy t0 < t1")
    if mu < 0:
        raise ValueError("mu must be >= 0")
    t, m = _sorted(t, m)
    keep = t < t1
    t, m = t[keep], m[keep]
    w = weights(m, base)
    ev = t[t >= t0]
    k0 = kint(t0 - t, base.c_yr, base.p, base.tmax_yr)
    tau = np.empty(len(ev))
    for i, x in enumerate(ev):
        tau[i] = mu * (x - t0) + np.sum(w * (kint(x - t, base.c_yr, base.p, base.tmax_yr) - k0))
    total = float(mu * (t1 - t0) + np.sum(w * (kint(t1 - t, base.c_yr, base.p, base.tmax_yr) - k0)))
    return tau, total
