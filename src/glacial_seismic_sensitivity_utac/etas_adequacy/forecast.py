"""AP2: simulation of the frozen temporal ETAS on a forecast window [t0, t1), given the history.

Unlike ``etas_nonstat.simulate`` (which regenerates *all* offspring of given mainshocks from their
own times), this simulator is conditional on the observed history: an event t_j < t0 only adds
offspring *inside* the window, with the Omori mass that is left there,

    E[direct offspring of j in [t0, t1)] = w_j [kint(t1 - t_j) - kint(t0 - t_j)],

and their times are drawn from the kernel truncated to [t0 - t_j, min(t1 - t_j, tmax)]. Window
events (background and offspring) then branch as in the frozen model. Offspring at or after t1 are
dropped. The history itself is never returned.

Background mu modes:
  * ``"ref"``     mu = exp(log_mu_ref) of the frozen baseline
  * ``"mixture"`` log mu ~ N(log_mu_ref, sigma_year^2), one draw per simulated catalogue
                  (gives the overdispersed, NBD-like number distribution)
  * ``"fixed"``   mu given explicitly (parametric bootstrap with a re-estimated mu)

Magnitudes: GR with b-value ``b`` above mc_ref, truncated at ``m_max``, drawn continuously from
``mc - dm/2`` and reported rounded to ``dm`` exactly as ``etas_nonstat.simulate`` (``dm = 0``:
continuous). The b-value is not part of the frozen baseline; it must be supplied.

Reproducibility: catalogue k uses its own stream ``SeedSequence(seed).spawn(n_sim)[k]``, so a
catalogue does not depend on how many others are drawn.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..etas_nonstat import kint
from .frozen import Baseline

MU_MODES = ("ref", "mixture", "fixed")


@dataclass(frozen=True)
class SimulatedWindows:
    """Simulated window catalogues (events in [t0, t1) only, sorted by time)."""

    t0: float
    t1: float
    times: tuple[np.ndarray, ...]
    mags: tuple[np.ndarray, ...]
    mu: np.ndarray

    @property
    def counts(self) -> np.ndarray:
        return np.array([len(x) for x in self.times])


def _kernel_inverse(
    u: np.ndarray, lo: np.ndarray, hi: np.ndarray, c: float, p: float
) -> np.ndarray:
    """Draw s in [lo, hi] with density proportional to (s + c)^(-p) (inverse CDF)."""
    if abs(p - 1.0) < 1e-9:
        a, b = np.log(lo + c), np.log(hi + c)
        return np.asarray(np.exp(a + u * (b - a)) - c)
    q = 1.0 - p
    a, b = (lo + c) ** q, (hi + c) ** q
    return np.asarray((a + u * (b - a)) ** (1.0 / q) - c)


def _magnitudes(
    rng: np.random.Generator, n: int, mc: float, b: float, m_max: float, dm: float
) -> np.ndarray:
    beta = b * np.log(10.0)
    m_lo = mc - 0.5 * dm
    trunc = 1.0 - np.exp(-beta * (m_max - m_lo))
    m = m_lo - np.log(1.0 - rng.uniform(0.0, 1.0, n) * trunc) / beta
    if dm > 0:
        m = np.round(np.round((m - mc) / dm) * dm + mc, 6)
    return np.asarray(np.maximum(m, mc))


def _one_window(
    rng: np.random.Generator,
    base: Baseline,
    mu: float,
    hist_t: np.ndarray,
    hist_m: np.ndarray,
    t0: float,
    t1: float,
    b: float,
    m_max: float,
    dm: float,
    max_events: int,
) -> tuple[np.ndarray, np.ndarray]:
    c, p, tmax = base.c_yr, base.p, base.tmax_yr
    norm = float(kint(np.array([tmax]), c, p, tmax)[0])

    # background
    nb = rng.poisson(mu * (t1 - t0))
    gen_t = rng.uniform(t0, t1, nb)
    gen_m = _magnitudes(rng, nb, base.mc_ref, b, m_max, dm)

    # direct offspring of the history, only the part of the kernel inside the window
    sel = (hist_t < t0) & (t0 - hist_t < tmax)
    if sel.any():
        ht, hm = hist_t[sel], hist_m[sel]
        lo = t0 - ht
        hi = np.minimum(t1 - ht, tmax)
        w = base.K * np.exp(base.alpha * (hm - base.mc_ref))
        mass = w * (kint(hi, c, p, tmax) - kint(lo, c, p, tmax))
        nk = rng.poisson(np.maximum(mass, 0.0))
        if nk.sum():
            u = rng.uniform(0.0, 1.0, int(nk.sum()))
            dt = _kernel_inverse(u, np.repeat(lo, nk), np.repeat(hi, nk), c, p)
            ct = np.repeat(ht, nk) + dt
            ok = (ct >= t0) & (ct < t1)
            gen_t = np.concatenate([gen_t, ct[ok]])
            gen_m = np.concatenate(
                [gen_m, _magnitudes(rng, int(ok.sum()), base.mc_ref, b, m_max, dm)]
            )

    # cascade of the window events (as in the frozen model; offspring >= t1 dropped)
    all_t, all_m = [gen_t], [gen_m]
    total = len(gen_t)
    while len(gen_t):
        if total > max_events:
            raise RuntimeError(f"catalogue exceeds max_events = {max_events} (runaway cascade)")
        nk = rng.poisson(base.K * np.exp(base.alpha * (gen_m - base.mc_ref)) * norm)
        if nk.sum() == 0:
            break
        if total + int(nk.sum()) > max_events:
            raise RuntimeError(f"catalogue exceeds max_events = {max_events} (runaway cascade)")
        u = rng.uniform(0.0, 1.0, int(nk.sum()))
        n = int(nk.sum())
        dt = _kernel_inverse(u, np.zeros(n), np.full(n, tmax), c, p)
        ct = np.repeat(gen_t, nk) + dt
        keep = ct < t1
        gen_t = ct[keep]
        gen_m = _magnitudes(rng, int(keep.sum()), base.mc_ref, b, m_max, dm)
        total += len(gen_t)
        all_t.append(gen_t)
        all_m.append(gen_m)
    t = np.concatenate(all_t)
    m = np.concatenate(all_m)
    o = np.argsort(t, kind="stable")
    return t[o], m[o]


def simulate_window(
    base: Baseline,
    hist_t: np.ndarray,
    hist_m: np.ndarray,
    t0: float,
    t1: float,
    n_sim: int,
    *,
    mu_mode: str = "ref",
    mu: float | None = None,
    b: float = 1.0,
    m_max: float = 8.0,
    dm: float = 0.1,
    seed: int = 0,
    max_events: int = 1_000_000,
) -> SimulatedWindows:
    """Simulate ``n_sim`` catalogues of the frozen model on [t0, t1) given the history.

    Raises ``ValueError`` for a supercritical model (n >= 1) and ``RuntimeError`` when one
    catalogue exceeds ``max_events`` (memory guard)."""
    if mu_mode not in MU_MODES:
        raise ValueError(f"mu_mode must be one of {MU_MODES}")
    if (mu_mode == "fixed") != (mu is not None):
        raise ValueError("mu is required exactly for mu_mode='fixed'")
    if mu is not None and not (np.isfinite(mu) and mu >= 0):
        raise ValueError("mu must be finite and >= 0")
    if not t0 < t1:
        raise ValueError("need t0 < t1")
    if n_sim < 1:
        raise ValueError("n_sim must be >= 1")
    if max_events < 1:
        raise ValueError("max_events must be >= 1")
    beta = b * np.log(10.0)
    if not base.alpha < beta:
        raise ValueError("alpha must be < b ln 10 (finite branching ratio)")
    n_branch, _ = expected_cluster_moments(base, b, m_max, dm)  # n of what is simulated
    if not n_branch < 1.0:
        # a supercritical cascade grows without bound and exhausts the machine's memory
        raise ValueError(f"supercritical: branching ratio n = {n_branch:.3f} >= 1")
    ht = np.asarray(hist_t, float)
    hm = np.asarray(hist_m, float)
    if ht.shape != hm.shape or not (np.all(np.isfinite(ht)) and np.all(np.isfinite(hm))):
        raise ValueError("history t and m must be finite arrays of equal length")
    if np.any(ht >= t0):
        raise ValueError("history must lie strictly before t0")
    streams = np.random.SeedSequence(seed).spawn(n_sim)
    times, mags, mus = [], [], []
    for ss in streams:
        rng = np.random.default_rng(ss)
        if mu_mode == "ref":
            mu_k = base.mu_ref
        elif mu_mode == "mixture":
            mu_k = float(np.exp(rng.normal(base.log_mu_ref, base.sigma_year)))
        else:
            mu_k = float(mu)  # type: ignore[arg-type]
        t, m = _one_window(rng, base, mu_k, ht, hm, t0, t1, b, m_max, dm, max_events)
        times.append(t)
        mags.append(m)
        mus.append(mu_k)
    return SimulatedWindows(t0, t1, tuple(times), tuple(mags), np.array(mus))


def expected_cluster_moments(
    base: Baseline, b: float = 1.0, m_max: float = 8.0, dm: float = 0.0
) -> tuple[float, float]:
    """(n, E[S^2]) of the Galton-Watson cluster:

    n = E[nu], nu(m) = K e^{alpha (m - mc)} kint(tmax); with n2 = E[nu^2],
    E[S] = 1/(1-n) and E[S^2] = (1 + 2n/(1-n) + n2/(1-n)^2) / (1-n).
    For a long window (T >> tmax) and no history: E[N] ~ mu T E[S], Var[N] ~ mu T E[S^2].

    ``dm = 0``: continuous GR above mc. ``dm > 0``: the binned magnitudes ``simulate_window``
    actually draws (continuous from mc - dm/2, rounded to dm), i.e. a geometric distribution on
    the bins. Its productivity mean is smaller, e.g. by a factor ~0.95 for alpha ~ 1, b ~ 0.9,
    dm = 0.1, so the simulator's effective n is below the continuous one (which therefore
    is a conservative upper bound; ``simulate_window`` checks the n of the magnitudes it draws)."""
    beta = b * np.log(10.0)
    delta = m_max - base.mc_ref
    norm = float(kint(np.array([base.tmax_yr]), base.c_yr, base.p, base.tmax_yr)[0])

    def mgf(k: float) -> float:  # E[e^{k alpha (m - mc)}] for GR truncated at m_max
        if dm > 0:
            lo = base.mc_ref - 0.5 * dm
            nb = int(np.floor((m_max - base.mc_ref) / dm + 0.5)) + 1
            j = np.arange(nb)
            a = np.maximum(base.mc_ref + (j - 0.5) * dm, lo)
            z = np.minimum(base.mc_ref + (j + 0.5) * dm, m_max)
            w = np.exp(-beta * (a - lo)) - np.exp(-beta * (z - lo))
            w = np.clip(w, 0.0, None) / (1 - np.exp(-beta * (m_max - lo)))
            return float(np.sum(w * np.exp(k * base.alpha * j * dm)))
        g = beta - k * base.alpha
        if g <= 0:
            return float("inf")
        return float(beta / g * (1 - np.exp(-g * delta)) / (1 - np.exp(-beta * delta)))

    n = base.K * norm * mgf(1.0)
    n2 = (base.K * norm) ** 2 * mgf(2.0)
    if n >= 1:
        return n, float("inf")
    es2 = (1 + 2 * n / (1 - n) + n2 / (1 - n) ** 2) / (1 - n)
    return float(n), float(es2)
