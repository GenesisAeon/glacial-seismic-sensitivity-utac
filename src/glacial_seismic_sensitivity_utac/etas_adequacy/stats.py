"""AP3: test statistics for the adequacy of the frozen temporal ETAS on a window [t0, t1).

Conventions follow the CSEP catalogue-based tests (Savran et al. 2020, pyCSEP) where they exist:

* N-test: delta1 = P(N >= n_obs), delta2 = P(N <= n_obs); a two-sided p = min(1, 2 min(d1, d2)).
  Analytic Poisson and lognormal-Poisson mixture versions, and an empirical version from simulated
  catalogues (which includes the ETAS clustering).
* M-test (catalogue-based): statistic
  D = sum_bins (log(n_obs + 1) - log(n_union * N_obs/N_union + 1))^2, quantile
  kappa = P(D_sim >= D_obs), each simulation scored against the union of the others.
  ``m_test_ks2`` is the two-sample KS used by draft addendum T3 (window vs. reference years).
* Pseudo-likelihood (temporal): L = sum_i log lambda(t_i) - Lambda(t0, t1); N-conditional
  L_c = sum_i log lambda(t_i) - N log Lambda(t0, t1). gamma = P(L_sim <= L_obs) (low = misfit).
  One-sided: data that cluster *more* than the model score high (gamma near 1), so this test
  cannot detect under-predicted clustering (see tests/test_adequacy_stats.py).
* Ogata (1988) residual test: KS of the transformed inter-event times against Exp(1), with mu
  re-estimated on the window (``etas_nonstat.mu_window_mle``, triggering parameters frozen).
  Because mu is estimated from the same data, the nominal KS p-value is too large (Lilliefors
  problem). ``ogata_ks_bootstrap`` calibrates it by a parametric bootstrap that re-estimates mu in
  every simulated catalogue exactly as in the real procedure (only mu; frozen trigger parameters).
* Information gain per event against a constant-rate Poisson benchmark, and a paired t-test
  across windows (e.g. years).

All p-values here are diagnostic quantities of an exploratory module; the gate (if frozen) is
decided by the addendum, with sizes established by simulation in AP4.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import special, stats

from ..etas_nonstat import mu_window_mle, pairs
from .forecast import simulate_window
from .frozen import Baseline
from .intensity import transformed_times, weights


# ---------------------------------------------------------------------------
# N-test
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class NTest:
    n_obs: int
    delta1: float  # P(N >= n_obs)
    delta2: float  # P(N <= n_obs)

    @property
    def p_two_sided(self) -> float:
        return float(min(1.0, 2.0 * min(self.delta1, self.delta2)))


def _check_count(n_obs: int) -> int:
    if isinstance(n_obs, bool) or int(n_obs) != n_obs or n_obs < 0:
        raise ValueError("n_obs must be a non-negative integer")
    return int(n_obs)


def n_test_poisson(n_obs: int, expected: float) -> NTest:
    n = _check_count(n_obs)
    if not (np.isfinite(expected) and expected > 0):
        raise ValueError("expected must be finite and > 0")
    d1 = float(stats.poisson.sf(n - 1, expected))
    d2 = float(stats.poisson.cdf(n, expected))
    return NTest(n, d1, d2)


def n_test_mixture(n_obs: int, expected_ref: float, sigma: float, n_nodes: int = 80) -> NTest:
    """N ~ Poisson(expected_ref * exp(Z)), Z ~ N(0, sigma^2) (log mu scatter, sigma_year).

    Gauss-Hermite quadrature over Z; sigma -> 0 recovers ``n_test_poisson``."""
    n = _check_count(n_obs)
    if not (np.isfinite(expected_ref) and expected_ref > 0) or sigma < 0:
        raise ValueError("expected_ref must be > 0 and sigma >= 0")
    if sigma == 0:
        return n_test_poisson(n, expected_ref)
    x, w = special.roots_hermite(n_nodes)
    lam = expected_ref * np.exp(np.sqrt(2.0) * sigma * x)
    w = w / np.sqrt(np.pi)
    d1 = float(np.sum(w * stats.poisson.sf(n - 1, lam)))
    d2 = float(np.sum(w * stats.poisson.cdf(n, lam)))
    return NTest(n, min(1.0, d1), min(1.0, d2))


def n_test_empirical(n_obs: int, sim_counts: np.ndarray) -> NTest:
    """Catalogue-based N-test against simulated counts (includes clustering)."""
    n = _check_count(n_obs)
    c = np.asarray(sim_counts)
    if c.ndim != 1 or len(c) == 0:
        raise ValueError("need at least one simulated count")
    return NTest(n, float(np.mean(c >= n)), float(np.mean(c <= n)))


# ---------------------------------------------------------------------------
# M-test
# ---------------------------------------------------------------------------
def _m_stat(obs: np.ndarray, union: np.ndarray, edges: np.ndarray) -> float:
    ho = np.histogram(obs, edges)[0].astype(float)
    hu = np.histogram(union, edges)[0].astype(float)
    if len(union) == 0:
        return float("inf")
    scaled = hu * len(obs) / len(union)
    return float(np.sum((np.log(ho + 1.0) - np.log(scaled + 1.0)) ** 2))


def m_test_catalog(
    obs_m: np.ndarray, sim_m: list[np.ndarray] | tuple[np.ndarray, ...], dm: float = 0.1
) -> float:
    """Catalogue-based M-test quantile kappa = P(D_sim >= D_obs) (small = misfit).

    Each simulated catalogue is compared with the union of the *other* simulations; catalogues
    with no events are skipped (their D is undefined)."""
    obs = np.asarray(obs_m, float)
    sims = [np.asarray(s, float) for s in sim_m if len(s) > 0]
    if len(obs) == 0 or len(sims) < 2:
        raise ValueError("need observed magnitudes and >= 2 non-empty simulations")
    allm = np.concatenate([obs, *sims])
    edges = np.arange(np.floor(allm.min() / dm) * dm - dm / 2, allm.max() + dm, dm)
    union = np.concatenate(sims)
    d_obs = _m_stat(obs, union, edges)
    d_sim = []
    for k, s in enumerate(sims):
        rest = np.concatenate(sims[:k] + sims[k + 1 :])
        d_sim.append(_m_stat(s, rest, edges))
    return float(np.mean(np.array(d_sim) >= d_obs))


def m_test_ks2(window_m: np.ndarray, reference_m: np.ndarray) -> float:
    """Two-sample KS p-value of window vs. reference magnitudes (draft addendum T3).

    Binned magnitudes create ties; scipy's asymptotic p is then conservative (size <= alpha)."""
    a, b = np.asarray(window_m, float), np.asarray(reference_m, float)
    if len(a) == 0 or len(b) == 0:
        raise ValueError("both samples must be non-empty")
    return float(stats.ks_2samp(a, b, method="asymp").pvalue)


# ---------------------------------------------------------------------------
# temporal pseudo-likelihood
# ---------------------------------------------------------------------------
def _split(t: np.ndarray, m: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    t, m = np.asarray(t, float), np.asarray(m, float)
    o = np.argsort(t, kind="stable")
    return t[o], m[o]


def window_loglik(
    hist_t: np.ndarray,
    hist_m: np.ndarray,
    win_t: np.ndarray,
    win_m: np.ndarray,
    window: tuple[float, float],
    base: Baseline,
    mu: float,
) -> tuple[float, float, int]:
    """(sum_i log lambda(t_i), Lambda(t0, t1), N) for the window events given the history."""
    t0, t1 = window
    t, m = _split(np.concatenate([hist_t, win_t]), np.concatenate([hist_m, win_m]))
    keep = t < t1
    t, m = t[keep], m[keep]
    ii, jj, dt = pairs(t, base.tmax_yr)
    w = weights(m, base)
    s = np.bincount(ii, weights=w[jj] * (dt + base.c_yr) ** (-base.p), minlength=len(t))
    inwin = t >= t0
    lam = mu + s[inwin]
    _, total = transformed_times(t, m, window, base, mu)
    if np.any(lam <= 0):
        return float("-inf"), total, int(inwin.sum())
    return float(np.sum(np.log(lam))), total, int(inwin.sum())


def pseudo_loglik(sum_log: float, total: float, n: int, conditional: bool = False) -> float:
    if conditional:
        return float(sum_log - n * np.log(total)) if n else 0.0
    return float(sum_log - total)


def ll_test(l_obs: float, l_sim: np.ndarray) -> float:
    """gamma = P(L_sim <= L_obs); small = observed catalogue unusually unlikely."""
    ls = np.asarray(l_sim, float)
    if len(ls) == 0:
        raise ValueError("need simulated likelihoods")
    return float(np.mean(ls <= l_obs))


# ---------------------------------------------------------------------------
# Ogata residual KS
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class OgataKS:
    mu_hat: float
    n: int
    ks_stat: float
    p_nominal: float  # KS p ignoring that mu was estimated (too large)
    p_bootstrap: float | None = None
    n_boot: int = 0


def _ks_window(
    t: np.ndarray, m: np.ndarray, window: tuple[float, float], base: Baseline, mu: float | None
) -> tuple[float, int, float, float]:
    t0, t1 = window
    if mu is None:
        r = mu_window_mle(t, m, base.mc_ref, base.trig(), t0, t1)
        mu = float(r["mu"])
    tau, _ = transformed_times(t, m, window, base, mu)
    n = len(tau)
    if n < 2:
        return mu, n, float("nan"), float("nan")
    gaps = np.diff(np.concatenate([[0.0], tau]))
    res = stats.kstest(gaps, "expon")
    return mu, n, float(res.statistic), float(res.pvalue)


def ogata_ks(
    hist_t: np.ndarray,
    hist_m: np.ndarray,
    win_t: np.ndarray,
    win_m: np.ndarray,
    window: tuple[float, float],
    base: Baseline,
    mu: float | None = None,
) -> OgataKS:
    """KS of transformed intervals vs Exp(1); mu re-estimated on the window unless given."""
    t = np.concatenate([hist_t, win_t])
    m = np.concatenate([hist_m, win_m])
    mu_hat, n, d, p = _ks_window(t, m, window, base, mu)
    return OgataKS(mu_hat, n, d, p)


def ogata_ks_bootstrap(
    hist_t: np.ndarray,
    hist_m: np.ndarray,
    win_t: np.ndarray,
    win_m: np.ndarray,
    window: tuple[float, float],
    base: Baseline,
    n_boot: int = 200,
    b: float = 1.0,
    seed: int = 0,
) -> OgataKS:
    """Parametric-bootstrap calibrated Ogata KS with mu re-estimated (Lilliefors-correct).

    Simulates ``n_boot`` window catalogues from the fitted model (frozen triggering, mu = mu_hat,
    same history), re-estimates mu in each exactly like for the data, and returns
    p = (1 + #{D_b >= D_obs}) / (1 + B). Catalogues with < 2 events are counted as D_b = 0."""
    obs = ogata_ks(hist_t, hist_m, win_t, win_m, window, base)
    if not np.isfinite(obs.ks_stat):
        return obs
    sims = simulate_window(
        base,
        hist_t,
        hist_m,
        window[0],
        window[1],
        n_boot,
        mu_mode="fixed",
        mu=obs.mu_hat,
        b=b,
        seed=seed,
    )
    d_b = np.zeros(n_boot)
    for k, (st, sm) in enumerate(zip(sims.times, sims.mags, strict=True)):
        _, n, d, _ = _ks_window(
            np.concatenate([hist_t, st]), np.concatenate([hist_m, sm]), window, base, None
        )
        d_b[k] = d if n >= 2 else 0.0
    p = (1.0 + float(np.sum(d_b >= obs.ks_stat))) / (1.0 + n_boot)
    return OgataKS(obs.mu_hat, obs.n, obs.ks_stat, obs.p_nominal, p, n_boot)


# ---------------------------------------------------------------------------
# information gain against a Poisson benchmark, paired t-test
# ---------------------------------------------------------------------------
def ig_per_event(model_loglik: float, n: int, rate: float, duration: float) -> float:
    """(L_model - L_poisson) / N with L_poisson = N log(rate) - rate * duration."""
    if n <= 0:
        return float("nan")
    if not (rate > 0 and duration > 0):
        raise ValueError("rate and duration must be > 0")
    l_bench = n * np.log(rate) - rate * duration
    return float((model_loglik - l_bench) / n)


def paired_t_test(gains: np.ndarray) -> tuple[float, float]:
    """One-sample t-test of per-window information gains against 0: (t, two-sided p)."""
    g = np.asarray(gains, float)
    g = g[np.isfinite(g)]
    if len(g) < 2:
        raise ValueError("need >= 2 finite gains")
    res = stats.ttest_1samp(g, 0.0)
    return float(res.statistic), float(res.pvalue)
