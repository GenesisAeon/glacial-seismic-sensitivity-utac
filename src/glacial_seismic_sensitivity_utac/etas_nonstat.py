"""v0.2 milestone M2: temporal ETAS with a time-varying background rate mu(t).

Model (all times in decimal years, events >= Mc):

    lambda(t) = mu(t) + sum_{t_j < t, t - t_j <= tmax} K exp(alpha (m_j - Mc)) (t - t_j + c)^(-p)

with mu(t) piecewise constant on fixed bins (default: calendar years). This is a strongly
simplified variant *inspired by* the non-stationary ETAS of Kumazawa & Ogata 2013 (JGR 118:6165,
doi:10.1002/2013JB010259; see also Hainzl & Ogata 2005, doi:10.1029/2004JB003247, and Marsan et
al. 2013, doi:10.1785/0120110304), not a reimplementation: Kumazawa & Ogata estimate *both* a
time-dependent background mu(t) and a time-dependent productivity K0(t) as smoothly varying
functions, with the smoothness weights chosen objectively by ABIC and optional change points.
Here: one background level per fixed bin, a fixed weak random-walk penalty on log mu (keeps bins
without events finite, sd not tuned by ABIC), and triggering parameters (K, alpha, c, p) common
to the whole period (constant productivity). Joint maximum
likelihood with an analytic gradient; pair sums are evaluated in chunks so memory stays
bounded (shared machine).

Why: a stationary ETAS (v0.1.0 ``quiescence``) cannot separate a change of the background
from the decay of earlier aftershock sequences. mu(t) is the ETAS *residual* background: it
absorbs everything the temporal model does not explain as triggering (catalogue/network changes,
swarms, triggering beyond tmax, productivity changes, external stresses); it is not an identified
forcing rate. A falling total rate with a rising
mu(t) is the pattern behind the 'deceptive quiet' question (hypothesis H2.2 in
PREREGISTRATION_v0.2.md).

Limitations: purely temporal (no spatial kernel), Omori kernel truncated at ``tmax``,
overdispersion beyond ETAS (swarms) is handled by using the year-to-year scatter of
log mu in the trend statistics, not the likelihood standard errors alone.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats

DAY = 1.0 / 365.25
PAIR_CHUNK = 2_000_000  # pairs per chunk in the likelihood (memory bound)


# ---------------------------------------------------------------------------
# kernel helpers
# ---------------------------------------------------------------------------
def pairs(t: np.ndarray, tmax: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Index pairs (i, j) with j < i and 0 < t_i - t_j <= tmax, plus dt (int32/float64)."""
    t = np.asarray(t, float)
    lo = np.searchsorted(t, t - tmax, side="left")
    counts = np.arange(len(t)) - lo
    total = int(counts.sum())
    ii = np.repeat(np.arange(len(t), dtype=np.int32), counts)
    first = np.repeat((np.cumsum(counts) - counts).astype(np.int64), counts)
    start = np.repeat(lo.astype(np.int64), counts)
    jj = (start + (np.arange(total, dtype=np.int64) - first)).astype(np.int32)
    dt = t[ii] - t[jj]
    ok = dt > 0  # simultaneous events cannot trigger each other
    return ii[ok], jj[ok], dt[ok]


def n_pairs(t: np.ndarray, tmax: float) -> int:
    """Number of (i, j) pairs within tmax (for memory planning; no arrays allocated)."""
    t = np.asarray(t, float)
    lo = np.searchsorted(t, t - tmax, side="left")
    return int((np.arange(len(t)) - lo).sum())


def kint(d: np.ndarray, c: float, p: float, tmax: float) -> np.ndarray:
    """int_0^min(d, tmax) (s + c)^(-p) ds (0 for d <= 0)."""
    x = np.clip(np.asarray(d, float), 0.0, tmax)
    if abs(p - 1.0) < 1e-9:
        return np.asarray(np.log((x + c) / c))
    return np.asarray((c ** (1 - p) - (x + c) ** (1 - p)) / (p - 1))


def _kint_dc(d: np.ndarray, c: float, p: float, tmax: float) -> np.ndarray:
    x = np.clip(np.asarray(d, float), 0.0, tmax)
    return np.asarray((x + c) ** (-p) - c ** (-p))


def _kint_dp(d: np.ndarray, c: float, p: float, tmax: float) -> np.ndarray:
    x = np.clip(np.asarray(d, float), 0.0, tmax)
    if abs(p - 1.0) < 1e-6:
        p = 1.0 + 1e-6
    a = c ** (1 - p)
    b = (x + c) ** (1 - p)
    f = (a - b) / (p - 1)
    return np.asarray((-np.log(c) * a + np.log(x + c) * b) / (p - 1) - f / (p - 1))


# ---------------------------------------------------------------------------
# data container
# ---------------------------------------------------------------------------
@dataclass
class ETASData:
    t: np.ndarray
    m: np.ndarray
    mc: float
    t0: float
    t1: float
    edges: np.ndarray
    tmax: float
    ii: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0, np.int32))
    jj: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0, np.int32))
    dt: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0))
    target: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0, bool))
    bin_of: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0, int))
    bin_len: np.ndarray = field(repr=False, default_factory=lambda: np.zeros(0))

    @classmethod
    def build(
        cls,
        t: np.ndarray,
        m: np.ndarray,
        mc: float,
        t0: float,
        t1: float,
        edges: np.ndarray,
        tmax: float,
    ) -> ETASData:
        order = np.argsort(t, kind="stable")
        t = np.asarray(t, float)[order]
        m = np.asarray(m, float)[order]
        sel = t < t1
        t, m = t[sel], m[sel]
        edges = np.asarray(edges, float)
        if abs(edges[0] - t0) > 1e-9 or abs(edges[-1] - t1) > 1e-9:
            raise ValueError("edges must start at t0 and end at t1")
        ii, jj, dt = pairs(t, tmax)
        target = (t >= t0) & (t < t1)
        b = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, len(edges) - 2)
        return cls(
            t=t,
            m=m,
            mc=mc,
            t0=t0,
            t1=t1,
            edges=edges,
            tmax=tmax,
            ii=ii,
            jj=jj,
            dt=dt,
            target=target,
            bin_of=np.where(target, b, -1),
            bin_len=np.diff(edges),
        )

    @property
    def n_bins(self) -> int:
        return len(self.edges) - 1


def _trig_sums(
    d: ETASData, K: float, alpha: float, c: float, p: float, need_grad: bool
) -> tuple[np.ndarray, ...]:
    """Triggering intensity at each event (and its partial derivatives), chunked."""
    n = len(d.t)
    w = K * np.exp(alpha * (d.m - d.mc))
    dm = d.m - d.mc
    s0 = np.zeros(n)
    if need_grad:
        sa, sc, sp = np.zeros(n), np.zeros(n), np.zeros(n)
    for a in range(0, len(d.ii), PAIR_CHUNK):
        ii = d.ii[a : a + PAIR_CHUNK]
        jj = d.jj[a : a + PAIR_CHUNK]
        x = d.dt[a : a + PAIR_CHUNK] + c
        lx = np.log(x)
        k = np.exp(-p * lx) * w[jj]
        s0 += np.bincount(ii, weights=k, minlength=n)
        if need_grad:
            sa += np.bincount(ii, weights=k * dm[jj], minlength=n)
            sc += np.bincount(ii, weights=-p * k * c / x, minlength=n)
            sp += np.bincount(ii, weights=-k * lx, minlength=n)
    if need_grad:
        return s0, sa, sc, sp
    return (s0,)


def unpack(x: np.ndarray, n_bins: int) -> tuple[np.ndarray, float, float, float, float]:
    return (
        np.exp(x[:n_bins]),
        float(np.exp(x[n_bins])),
        float(x[n_bins + 1]),
        float(np.exp(x[n_bins + 2])),
        float(x[n_bins + 3]),
    )


def loglik_grad(
    x: np.ndarray, d: ETASData, rw_sd: float = 1.0, need_grad: bool = True
) -> tuple[float, np.ndarray]:
    """Penalised log-likelihood and gradient in x = (log mu_1..B, log K, alpha, log c, p)."""
    B = d.n_bins
    mu, K, alpha, c, p = unpack(x, B)
    sums = _trig_sums(d, K, alpha, c, p, need_grad)
    tg = d.target
    bins = d.bin_of[tg]
    lam = mu[bins] + sums[0][tg]
    w = K * np.exp(alpha * (d.m - d.mc))
    G = kint(d.t1 - d.t, c, p, d.tmax) - kint(d.t0 - d.t, c, p, d.tmax)
    lmu = x[:B]
    pen = 0.5 * float(np.sum(np.diff(lmu) ** 2)) / rw_sd**2
    ll = float(np.sum(np.log(lam)) - np.sum(mu * d.bin_len) - np.sum(w * G)) - pen
    if not need_grad:
        return ll, np.zeros_like(x)
    g = np.zeros_like(x)
    inv = 1.0 / lam
    g[:B] = mu * np.bincount(bins, weights=inv, minlength=B) - mu * d.bin_len
    dpen = np.zeros(B)
    dl = np.diff(lmu)
    dpen[:-1] -= dl
    dpen[1:] += dl
    g[:B] -= dpen / rw_sd**2
    _, sa, sc, sp = sums
    g[B] = float(np.sum(sums[0][tg] * inv) - np.sum(w * G))
    dm = d.m - d.mc
    g[B + 1] = float(np.sum(sa[tg] * inv) - np.sum(w * dm * G))
    Gc = _kint_dc(d.t1 - d.t, c, p, d.tmax) - _kint_dc(d.t0 - d.t, c, p, d.tmax)
    g[B + 2] = float(np.sum(sc[tg] * inv) - np.sum(w * Gc) * c)
    Gp = _kint_dp(d.t1 - d.t, c, p, d.tmax) - _kint_dp(d.t0 - d.t, c, p, d.tmax)
    g[B + 3] = float(np.sum(sp[tg] * inv) - np.sum(w * Gp))
    return ll, g


# ---------------------------------------------------------------------------
# fitting
# ---------------------------------------------------------------------------
@dataclass
class NSFit:
    edges: np.ndarray
    mu: np.ndarray  # events/yr per bin
    log_mu_se: np.ndarray  # likelihood-based SE of log mu per bin
    K: float
    alpha: float
    c_yr: float
    p: float
    loglik: float
    n_target: int
    n_per_bin: np.ndarray
    converged: bool
    branching_ratio: float
    cov: np.ndarray = field(repr=False)
    tmax: float = 1.0

    @property
    def mids(self) -> np.ndarray:
        return np.asarray(0.5 * (self.edges[1:] + self.edges[:-1]))

    def table(self) -> pd.DataFrame:
        return pd.DataFrame(
            dict(
                t_start=self.edges[:-1],
                t_end=self.edges[1:],
                mu_per_yr=self.mu,
                log_mu=np.log(self.mu),
                log_mu_se=self.log_mu_se,
                n_events=self.n_per_bin,
            )
        )

    def trig_params(self) -> dict[str, float]:
        return dict(K=self.K, alpha=self.alpha, c_yr=self.c_yr, p=self.p, tmax=self.tmax)


BOUNDS_TRIG = [(None, None), (0.0, 3.0), (np.log(1e-6), np.log(0.5)), (1.0001, 2.5)]


def branching_ratio(K: float, alpha: float, c: float, p: float, tmax: float, b: float) -> float:
    """Expected direct offspring per event, unbounded GR with b-value b (inf if alpha >= beta)."""
    beta = b * np.log(10)
    if alpha >= beta:
        return float("inf")
    return float(K * kint(np.array([tmax]), c, p, tmax)[0] * beta / (beta - alpha))


def fit_nonstationary(
    t: np.ndarray,
    m: np.ndarray,
    mc: float,
    t0: float,
    t1: float,
    edges: np.ndarray | None = None,
    tmax: float = 1.0,
    rw_sd: float = 1.0,
    x0_trig: tuple[float, float, float, float] | None = None,
    b_value: float = 1.0,
    data: ETASData | None = None,
    maxiter: int = 2000,
    fix_trig: tuple[float, float, float, float] | None = None,
) -> NSFit:
    """Joint MLE of piecewise-constant mu (bins ``edges``) and common triggering parameters.

    ``fix_trig`` = (K, alpha, c_yr, p) fixes the triggering parameters (two-stage estimator):
    only the bin rates are fitted and the covariance is that of the mu block alone, i.e. the
    covariance *conditional* on the fixed triggering parameters (inverse negative Hessian of the
    penalised log-likelihood; the random-walk penalty lowers it by ~1 %). Stage-1 uncertainty is
    not propagated (review W3, Claude Code); see ``scripts/v02_stage1_propagation.py`` for an
    exploratory propagation. The frozen H2 procedure is unchanged."""
    if edges is None:
        edges = np.arange(t0, t1, 1.0)
        edges = np.append(edges, t1) if edges[-1] < t1 else edges
    d = data or ETASData.build(t, m, mc, t0, t1, np.asarray(edges, float), tmax)
    B = d.n_bins
    nb = np.bincount(d.bin_of[d.target], minlength=B).astype(float)
    lmu0 = np.log(np.maximum(0.5 * nb, 0.5) / d.bin_len)
    best: Any = None
    starts = (
        [x0_trig]
        if x0_trig is not None
        else [(np.log(0.02), a0, np.log(0.002), 1.1) for a0 in (0.6, 1.4)]
    )
    if fix_trig is not None:
        K_f, a_f, c_f, p_f = fix_trig
        starts = [(float(np.log(K_f)), a_f, float(np.log(c_f)), p_f)]
    nfree = B if fix_trig is not None else B + 4
    for st in starts:
        tail = np.asarray(st, float)
        x0 = np.concatenate([lmu0, tail])[:nfree]
        bounds = ([(None, None)] * B + BOUNDS_TRIG)[:nfree]

        def f(xf: np.ndarray, tail: np.ndarray = tail) -> tuple[float, np.ndarray]:
            x = np.concatenate([xf, tail[: B + 4 - len(xf)]]) if len(xf) < B + 4 else xf
            ll, g = loglik_grad(x, d, rw_sd)
            if not np.isfinite(ll):
                return 1e12, np.zeros_like(xf)
            return -ll, -g[: len(xf)]

        r = optimize.minimize(
            f, x0, jac=True, method="L-BFGS-B", bounds=bounds, options=dict(maxiter=maxiter)
        )
        if best is None or r.fun < best.fun:
            best = r
    assert best is not None
    x = best.x if fix_trig is None else np.concatenate([best.x, np.asarray(starts[0], float)])
    cov = _covariance(x, d, rw_sd, n_free=nfree)
    mu, K, alpha, c, p = unpack(x, B)
    se = np.sqrt(np.clip(np.diag(cov)[:B], 0, None))
    return NSFit(
        edges=d.edges,
        mu=mu,
        log_mu_se=se,
        K=K,
        alpha=alpha,
        c_yr=c,
        p=p,
        loglik=float(-best.fun),
        n_target=int(d.target.sum()),
        n_per_bin=nb.astype(int),
        converged=bool(best.success),
        branching_ratio=branching_ratio(K, alpha, c, p, d.tmax, b_value),
        cov=cov,
        tmax=d.tmax,
    )


def _covariance(x: np.ndarray, d: ETASData, rw_sd: float, n_free: int | None = None) -> np.ndarray:
    """Inverse of the numerically differentiated (analytic-gradient) negative Hessian.

    With ``n_free`` < len(x) only the leading block (the free parameters) is used; the
    returned matrix is then padded with zeros for the fixed parameters."""
    n_all = len(x)
    n = n_all if n_free is None else n_free
    H = np.zeros((n, n))
    for k in range(n):
        h = 1e-5 * max(1.0, abs(x[k]))
        xp, xm = x.copy(), x.copy()
        xp[k] += h
        xm[k] -= h
        H[:, k] = (loglik_grad(xp, d, rw_sd)[1][:n] - loglik_grad(xm, d, rw_sd)[1][:n]) / (2 * h)
    if n < n_all:
        H = 0.5 * (H + H.T)
        try:
            C = np.linalg.inv(-H)
        except np.linalg.LinAlgError:
            C = np.linalg.pinv(-H)
        out = np.zeros((n_all, n_all))
        out[:n, :n] = C
        return out
    H = 0.5 * (H + H.T)
    try:
        return np.asarray(np.linalg.inv(-H))
    except np.linalg.LinAlgError:
        return np.asarray(np.linalg.pinv(-H))


# ---------------------------------------------------------------------------
# statistics on mu(t) (pre-registered in PREREGISTRATION_v0.2.md, H2.1 / H2.2)
# ---------------------------------------------------------------------------
def log_mu_trend(fit: NSFit, years: tuple[float, float]) -> dict[str, float]:
    """OLS slope of log mu over full bins within ``years`` (per decade).

    SE = max(residual-based OLS SE, likelihood-based GLS SE): the residual scatter carries
    overdispersion beyond ETAS, the likelihood SE is the floor."""
    tab = fit.table()
    sel = (tab.t_start >= years[0] - 1e-9) & (tab.t_end <= years[1] + 1e-9)
    x = (
        tab.loc[sel, "t_start"].to_numpy()
        + 0.5 * (tab.loc[sel, "t_end"] - tab.loc[sel, "t_start"]).to_numpy()
    )
    y = tab.loc[sel, "log_mu"].to_numpy()
    idx = np.nonzero(sel.to_numpy())[0]
    if len(x) < 4:
        return dict(slope_per_decade=np.nan, se=np.nan, n_bins=float(len(x)))
    X = np.column_stack([np.ones_like(x), (x - x.mean()) / 10.0])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    s2 = float(res @ res / (len(x) - 2))
    xtx_inv = np.linalg.inv(X.T @ X)
    se_ols = float(np.sqrt(s2 * xtx_inv[1, 1]))
    V = fit.cov[np.ix_(idx, idx)]
    a = (xtx_inv @ X.T)[1]
    se_lik = float(np.sqrt(max(a @ V @ a, 0.0)))
    return dict(
        slope_per_decade=float(beta[1]),
        se=max(se_ols, se_lik),
        se_ols=se_ols,
        se_lik=se_lik,
        resid_sd=float(np.sqrt(s2)),
        n_bins=float(len(x)),
    )


def did_test(g: dict[str, float], c: dict[str, float]) -> dict[str, float]:
    """Difference of log-mu slopes glacier - control, one-sided p for > 0."""
    diff = g["slope_per_decade"] - c["slope_per_decade"]
    se = float(np.hypot(g["se"], c["se"]))
    z = diff / se if se > 0 else np.nan
    return dict(diff_per_decade=diff, se=se, z=z, p_one=float(stats.norm.sf(z)))


def window_ratio(fit: NSFit, a: tuple[float, float], b: tuple[float, float]) -> dict[str, float]:
    """mu ratio (later window b vs earlier window a) from yearly log mu, Welch-type SE.

    Windows are half-open [start, end): full bins with t_start >= start and t_end <= end are
    used, so calendar years 2008-2019 are passed as (2008.0, 2020.0)."""
    tab = fit.table()

    def pick(w: tuple[float, float]) -> np.ndarray:
        s = (tab.t_start >= w[0] - 1e-9) & (tab.t_end <= w[1] + 1e-9)
        return np.asarray(tab.loc[s, "log_mu"].to_numpy(float))

    la, lb = pick(a), pick(b)
    if len(la) < 2 or len(lb) < 2:
        return dict(log_ratio=np.nan, se=np.nan, lo95=np.nan, hi95=np.nan)
    lr = float(lb.mean() - la.mean())
    se = float(np.sqrt(la.var(ddof=1) / len(la) + lb.var(ddof=1) / len(lb)))
    return dict(
        log_ratio=lr,
        se=se,
        ratio=float(np.exp(lr)),
        lo95=float(np.exp(lr - 1.96 * se)),
        hi95=float(np.exp(lr + 1.96 * se)),
    )


def classify_background(total_ratio: float, lo95: float, hi95: float) -> str:
    """Pre-registered H2.2 classes (PREREGISTRATION_v0.2.md section 3)."""
    if not np.isfinite(lo95):
        return "not estimable"
    if lo95 > 1.0 and total_ratio < 1.0:
        return "masked background rise (deceptive-quiet pattern)"
    if lo95 > 1.0:
        return "background rise (not masked)"
    if hi95 < 1.0:
        return "background decrease (genuine quiet)"
    return "no resolvable background change"


# ---------------------------------------------------------------------------
# prospective statistic (C2, data window from 2027-01-01)
# ---------------------------------------------------------------------------
def mu_window_mle(
    t: np.ndarray, m: np.ndarray, mc: float, trig: dict[str, float], a: float, b: float
) -> dict[str, float]:
    """MLE of a constant mu on [a, b) with *frozen* triggering parameters; Fisher SE of log mu."""
    t = np.asarray(t, float)
    order = np.argsort(t, kind="stable")
    t, m = t[order], np.asarray(m, float)[order]
    sel = t < b
    t, m = t[sel], m[sel]
    ii, jj, dt = pairs(t, trig["tmax"])
    w = trig["K"] * np.exp(trig["alpha"] * (m - mc))
    s = np.bincount(ii, weights=w[jj] * (dt + trig["c_yr"]) ** (-trig["p"]), minlength=len(t))
    tg = (t >= a) & (t < b)
    trig_i = s[tg]
    n = int(tg.sum())
    T = b - a
    if n == 0:
        return dict(mu=0.0, log_mu=-np.inf, log_mu_se=np.inf, n=0.0)

    def score(mu: float) -> float:
        return float(np.sum(1.0 / (mu + trig_i)) - T)

    hi = n / T + 1.0
    mu = float(optimize.brentq(score, 1e-9, hi)) if score(1e-9) > 0 else 1e-9
    info = float(np.sum(1.0 / (mu + trig_i) ** 2))
    se_log = float(1.0 / (mu * np.sqrt(info))) if info > 0 else np.inf
    return dict(mu=mu, log_mu=float(np.log(mu)), log_mu_se=se_log, n=float(n))


# ---------------------------------------------------------------------------
# simulation (synthetic recovery tests, power)
# ---------------------------------------------------------------------------
def simulate(
    mu_fn: Callable[[np.ndarray], np.ndarray],
    t0: float,
    t1: float,
    K: float,
    alpha: float,
    c: float,
    p: float,
    mc: float = 2.0,
    b: float = 1.0,
    tmax: float = 1.0,
    rng: np.random.Generator | None = None,
    mu_max: float | None = None,
    mainshocks: tuple[tuple[float, float], ...] = (),
    m_max: float = 8.0,
    dm: float = 0.1,
) -> pd.DataFrame:
    """Simulate a temporal ETAS catalogue (branching) with background rate mu_fn(t) [1/yr].

    Magnitudes are drawn continuously from GR above ``mc - dm/2`` and reported rounded to ``dm``,
    so every reported bin (including the lowest, labelled ``mc``) has full width and the binned
    catalogue follows GR with the nominal b (review K2, Claude Code: drawing from ``mc`` and
    rounding afterwards gave the lowest bin half width and b ~ 0.9). ``dm = 0`` returns
    continuous magnitudes >= mc."""
    rng = rng or np.random.default_rng(0)
    beta = b * np.log(10)
    grid = np.linspace(t0, t1, 2001)
    mmax = mu_max or float(np.max(mu_fn(grid))) * 1.05
    n0 = rng.poisson(mmax * (t1 - t0))
    tb = np.sort(rng.uniform(t0, t1, n0))
    tb = tb[rng.uniform(0, mmax, n0) < mu_fn(tb)]

    m_lo = mc - 0.5 * dm

    def mags(n: int) -> np.ndarray:
        u = rng.uniform(0, 1, n)
        trunc = 1 - np.exp(-beta * (m_max - m_lo))
        return np.asarray(m_lo - np.log(1 - u * trunc) / beta)

    t_all = [tb, np.array([x[0] for x in mainshocks])]
    m_all = [mags(len(tb)), np.array([x[1] for x in mainshocks])]
    gen_t, gen_m = np.concatenate(t_all), np.concatenate(m_all)
    norm = float(kint(np.array([tmax]), c, p, tmax)[0])
    a1 = c ** (1 - p)
    a2 = (tmax + c) ** (1 - p)
    while len(gen_t):
        nk = rng.poisson(K * np.exp(alpha * (gen_m - mc)) * norm)
        if nk.sum() == 0:
            break
        parent_t = np.repeat(gen_t, nk)
        u = rng.uniform(0, 1, int(nk.sum()))
        if abs(p - 1.0) < 1e-9:  # p = 1: inverse CDF of a log-uniform shifted variable
            dt = c * ((tmax + c) / c) ** u - c
        else:
            dt = (a1 - u * (a1 - a2)) ** (1 / (1 - p)) - c
        ct = parent_t + dt
        cm = mags(len(ct))
        keep = ct < t1
        gen_t, gen_m = ct[keep], cm[keep]
        t_all.append(gen_t)
        m_all.append(gen_m)
    t = np.concatenate(t_all)
    m = np.concatenate(m_all)
    o = np.argsort(t)
    m = m[o]
    if dm > 0:
        m = np.round(np.round((m - mc) / dm) * dm + mc, 6)
    return pd.DataFrame(dict(t=t[o], mag=np.maximum(m, mc)))


def fit_two_stage(
    t: np.ndarray,
    m: np.ndarray,
    mc: float,
    t0: float,
    t1: float,
    edges: np.ndarray | None = None,
    tmax: float = 1.0,
    rw_sd: float = 1.0,
    b_value: float = 1.0,
) -> tuple[NSFit, NSFit]:
    """Two-stage estimator: (1) stationary ETAS (one bin) for the triggering parameters,
    (2) yearly mu with those triggering parameters fixed.

    Rationale (see docs/v02_benchmarks.md): with free yearly mu the joint MLE trades the
    long Omori tail against the bin rates (p inflated, branching ratio and mu biased).
    Returns (stage1, stage2)."""
    s1 = fit_nonstationary(
        t, m, mc, t0, t1, edges=np.array([t0, t1]), tmax=tmax, rw_sd=rw_sd, b_value=b_value
    )
    s2 = fit_nonstationary(
        t,
        m,
        mc,
        t0,
        t1,
        edges=edges,
        tmax=tmax,
        rw_sd=rw_sd,
        b_value=b_value,
        fix_trig=(s1.K, s1.alpha, s1.c_yr, s1.p),
    )
    return s1, s2


def bh_adjust(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values."""
    p = np.asarray(p, float)
    n = len(p)
    if n == 0:
        return p
    o = np.argsort(p)
    adj = p[o] * n / np.arange(1, n + 1)
    adj = np.minimum.accumulate(adj[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.clip(adj, 0, 1)
    return out
