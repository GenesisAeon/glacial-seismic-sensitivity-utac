"""AP6: C2 with a frozen Omori term for the M6.8 sequence of 2025-12-06 (Johann, 2026-10-22).

AP5 showed that the tail of this sequence makes C2 report a glacier-region increase that is not
there. The remedy decided by Johann adds a known rate to the glacier-region intensity,

    lambda(t) = mu + sum_j g_j(t) + S(t),      S(t) = A * (t - t_ms)^(-q),

with g the frozen ETAS triggering (unchanged) and (A, q) fitted on 2026 data, before the C2 window
opens, and then frozen. ``fit_sequence_term`` estimates (mu_2026, A, q) by maximum likelihood on a
window of 2026 (mu_2026 is a nuisance parameter). ``evaluate_pair_with_term`` is
``confirmatory_v02.evaluate_pair`` with S added to the glacier region only:

  * variant ``"A"``: the preregistered SE (fit uncertainty of S ignored);
  * variant ``"B"``: the preregistered variance plus the delta-method variance of log mu_new from
    the covariance of (log A, q).

Without a term (``fit=None``) the functions reproduce ``mu_window_mle`` / ``evaluate_pair``
exactly. Which variant is used is decided by the AP6 rule
(``docs/adequacy/sequence_term_protocol.md``).
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats

from ..confirmatory_v02 import LOOKS, WINDOW_START, resolve_look
from ..etas_nonstat import pairs
from .frozen import Baseline
from .sequence_tail import omori_integral


@dataclass(frozen=True)
class TermFit:
    """Fitted Omori term S(t) = A (t - t_ms)^(-q) (decimal years) with covariance of (log A, q)."""

    t_ms: float
    log_A: float
    q: float
    cov: tuple[tuple[float, float], tuple[float, float]]  # of (log A, q)
    log_mu: float  # nuisance: background in the fit window
    n: int
    window: tuple[float, float]

    @property
    def A(self) -> float:
        return float(np.exp(self.log_A))

    def rate(self, t: np.ndarray) -> np.ndarray:
        return self.A * (np.asarray(t, float) - self.t_ms) ** (-self.q)

    def with_params(self, log_A: float, q: float) -> TermFit:
        return TermFit(self.t_ms, log_A, q, self.cov, self.log_mu, self.n, self.window)


def trig_rates(t: np.ndarray, m: np.ndarray, base: Baseline) -> np.ndarray:
    """Frozen-ETAS triggered intensity at each event from earlier events within tmax (t sorted)."""
    ii, jj, d = pairs(t, base.tmax_yr)
    w = base.K * np.exp(base.alpha * (m - base.mc_ref))
    return np.bincount(ii, weights=w[jj] * (d + base.c_yr) ** (-base.p), minlength=len(t))


def _prep(t: np.ndarray, m: np.ndarray, b: float) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(t, float)
    o = np.argsort(t, kind="stable")
    t, m = t[o], np.asarray(m, float)[o]
    keep = t < b
    return t[keep], m[keep]


def fit_sequence_term(
    t: np.ndarray, m: np.ndarray, base: Baseline, t_ms: float, a: float, b: float
) -> TermFit:
    """MLE of (log mu, log A, q) on [a, b) with frozen triggering; events before a are triggers.

    The triggered compensator does not depend on the parameters and is dropped. Covariance from
    the numerical Hessian of the negative log-likelihood (central differences)."""
    if not t_ms < a < b:
        raise ValueError("need t_ms < a < b")
    t, m = _prep(t, m, b)
    trig = trig_rates(t, m, base)
    sel = t >= a
    x, g = t[sel] - t_ms, trig[sel]
    n = int(sel.sum())
    if n < 10:
        raise ValueError("too few events in the fit window")
    T = b - a

    def nll(th: np.ndarray) -> float:
        lmu, la, q = th
        mu, A = np.exp(lmu), np.exp(la)
        lam = mu + g + A * x ** (-q)
        return float(-(np.sum(np.log(lam)) - mu * T - A * omori_integral(a - t_ms, b - t_ms, q)))

    best = None
    for q0 in (0.8, 1.1, 1.5):
        a0 = np.log(max(n / 2, 1.0) / omori_integral(a - t_ms, b - t_ms, q0))
        th0 = np.array([np.log(max(n / (2 * T), 1e-3)), a0, q0])
        r = optimize.minimize(nll, th0, method="L-BFGS-B",
                              bounds=[(-10.0, 15.0), (-10.0, 25.0), (0.2, 3.0)])  # fmt: skip
        if best is None or r.fun < best.fun:
            best = r
    assert best is not None
    th = best.x
    h = np.array([1e-4, 1e-4, 1e-4])
    H = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            ei, ej = np.eye(3)[i] * h[i], np.eye(3)[j] * h[j]
            H[i, j] = (nll(th + ei + ej) - nll(th + ei - ej) - nll(th - ei + ej)
                       + nll(th - ei - ej)) / (4 * h[i] * h[j])  # fmt: skip
    cov3 = np.linalg.inv(H)
    c = cov3[1:, 1:]
    return TermFit(
        t_ms=float(t_ms), log_A=float(th[1]), q=float(th[2]),
        cov=((float(c[0, 0]), float(c[0, 1])), (float(c[1, 0]), float(c[1, 1]))),
        log_mu=float(th[0]), n=n, window=(float(a), float(b)),
    )  # fmt: skip


def mu_mle_with_term(
    t: np.ndarray, m: np.ndarray, base: Baseline, a: float, b: float, fit: TermFit | None
) -> dict[str, float]:
    """``mu_window_mle`` with the known rate S(t) added (identical to it for ``fit=None``)."""
    t, m = _prep(t, m, b)
    trig = trig_rates(t, m, base)
    tg = (t >= a) & (t < b)
    extra = trig[tg] + (fit.rate(t[tg]) if fit is not None else 0.0)
    n = int(tg.sum())
    T = b - a
    if n == 0:
        return dict(mu=0.0, log_mu=-np.inf, log_mu_se=np.inf, n=0.0)

    def score(mu: float) -> float:
        return float(np.sum(1.0 / (mu + extra)) - T)

    hi = n / T + 1.0
    mu = float(optimize.brentq(score, 1e-9, hi)) if score(1e-9) > 0 else 1e-9
    info = float(np.sum(1.0 / (mu + extra) ** 2))
    se_log = float(1.0 / (mu * np.sqrt(info))) if info > 0 else np.inf
    return dict(mu=mu, log_mu=float(np.log(mu)), log_mu_se=se_log, n=float(n))


def _term_var(cat: pd.DataFrame, base: Baseline, look_end: float, fit: TermFit) -> float:
    """Delta-method variance of log mu_new from the covariance of (log A, q)."""
    t, m = cat.t.to_numpy(float), cat.mag.to_numpy(float)
    cov = np.array(fit.cov)
    sd = np.sqrt(np.diag(cov))
    grad = np.zeros(2)
    for k in range(2):
        h = 1e-3 * sd[k]
        d = np.eye(2)[k] * h
        up = fit.with_params(fit.log_A + d[0], fit.q + d[1])
        dn = fit.with_params(fit.log_A - d[0], fit.q - d[1])
        lu = mu_mle_with_term(t, m, base, WINDOW_START, look_end, up)["log_mu"]
        ld = mu_mle_with_term(t, m, base, WINDOW_START, look_end, dn)["log_mu"]
        grad[k] = (lu - ld) / (2 * h)
    return float(grad @ cov @ grad)


def _region(
    cat: pd.DataFrame, base: Baseline, look_end: float, fit: TermFit | None, variant: str
) -> dict[str, float]:
    c = cat[cat.mag >= base.mc_ref - 1e-9]
    r = mu_mle_with_term(c.t.to_numpy(float), c.mag.to_numpy(float), base, WINDOW_START,
                         look_end, fit)  # fmt: skip
    T = look_end - WINDOW_START
    var = r["log_mu_se"] ** 2 + base.sigma_year**2 / T + base.sigma_year**2 / base.n_ref_years
    v_term = _term_var(c, base, look_end, fit) if (fit is not None and variant == "B") else 0.0
    var += v_term
    delta = r["log_mu"] - base.log_mu_ref
    return dict(mu_new=r["mu"], n_new=r["n"], delta_log_mu=delta, se=float(np.sqrt(var)),
                var_term=v_term)  # fmt: skip


def evaluate_pair_with_term(
    cat_g: pd.DataFrame,
    cat_c: pd.DataFrame,
    models: dict[str, Baseline],
    look_end: float | str | dt.date,
    fit: TermFit | None,
    variant: str = "A",
    glacier: str = "SE_Alaska_AK",
    control: str = "Interior_AK_ctrl",
) -> dict[str, Any]:
    """C2 at a preregistered look with the frozen sequence term in the glacier region."""
    if variant not in ("A", "B"):
        raise ValueError("variant must be 'A' or 'B'")
    end = resolve_look(look_end)
    g = _region(cat_g, models[glacier], end, fit, variant)
    c = _region(cat_c, models[control], end, None, variant)
    D = g["delta_log_mu"] - c["delta_log_mu"]
    se = float(np.hypot(g["se"], c["se"]))
    z = D / se
    alpha = dict(LOOKS)[end]
    p = float(stats.norm.sf(z))
    return dict(glacier=g, control=c, D=D, se=se, z=z, p_one=p, alpha=alpha,
                reject=bool(p < alpha))  # fmt: skip


# ---------------------------------------------------------------------------
# AP6 simulation: residual bias of C2 with the fitted term
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TermScenario:
    name: str
    dq: float  # true decay exponent = q_hat + dq (tail amplitude matched in the fit window)
    tail: bool = True
    mu_factor: float = 1.0  # glacier background multiplied from 2027 on (the sought signal)


TERM_SCENARIOS: dict[str, TermScenario] = {
    s.name: s
    for s in (
        TermScenario("dq-0.2", -0.2),
        TermScenario("dq-0.1", -0.1),
        TermScenario("dq0", 0.0),
        TermScenario("dq+0.1", 0.1),
        TermScenario("dq+0.2", 0.2),
        TermScenario("signal_dq0", 0.0, mu_factor=1.5),
        TermScenario("signal_notail", 0.0, tail=False, mu_factor=1.5),
    )
}

YEARS_SIM = tuple(range(2025, 2037))  # 2025 = last warm-up year (triggers for the 2026 fit)


def _frozen_catalogue(
    seeds: list[int], base: Baseline, b: float, warmup_years: float, mu_factor: float
) -> tuple[np.ndarray, np.ndarray]:
    """Frozen-model events 2025..2036, one mixture draw of mu per year (x mu_factor from 2027)."""
    from .forecast import simulate_window

    no = np.array([])
    w = simulate_window(base, no, no, 2025.0 - warmup_years, 2025.0, 1, mu_mode="mixture",
                        b=b, m_max=8.0, dm=0.1, seed=seeds[0])  # fmt: skip
    ht, hm = w.times[0], w.mags[0]
    out_t, out_m = [], []
    rng = np.random.default_rng(seeds[-1])
    for k, y in enumerate(YEARS_SIM):
        if y >= 2027 and mu_factor != 1.0:
            mu = mu_factor * float(np.exp(rng.normal(base.log_mu_ref, base.sigma_year)))
            kw: dict[str, Any] = dict(mu_mode="fixed", mu=mu)
        else:
            kw = dict(mu_mode="mixture")
        w = simulate_window(base, ht, hm, float(y), float(y + 1), 1, b=b, m_max=8.0, dm=0.1,
                            seed=seeds[1 + k], **kw)  # fmt: skip
        ht, hm = w.times[0], w.mags[0]
        out_t.append(ht)
        out_m.append(hm)
    return np.concatenate(out_t), np.concatenate(out_m)


def _term_seeds(seed: int, idx: int, rep: int, k: int) -> list[int]:
    ss = np.random.SeedSequence([seed, idx, rep])
    return [int(x) for x in ss.generate_state(k, dtype=np.uint32)]


def run_term_replicate(
    models: dict[str, Baseline],
    b_values: dict[str, float],
    ctx: dict[str, Any],
    scenario: TermScenario,
    idx: int,
    rep: int,
    seed: int,
    warmup_years: float = 20.0,
) -> dict[str, Any]:
    """One AP6 replicate: synthetic truth -> fit of the term on 2026 -> C2 (none / A / B).

    ``ctx`` holds the real fit (``t_ms``, ``log_A``, ``q``, ``cutoff``), the real Dec-2025 sequence
    events (``dec_t``, ``dec_m``; triggers only, no offspring) and the magnitude pool."""
    import time

    from .sequence_tail import inject_tail

    t0 = time.time()
    n_s = 2 + len(YEARS_SIM)
    s = _term_seeds(seed, idx, rep, 2 * n_s + 1)
    gl, ct = "SE_Alaska_AK", "Interior_AK_ctrl"
    tg, mg = _frozen_catalogue(s[:n_s], models[gl], b_values[gl], warmup_years,
                               scenario.mu_factor)  # fmt: skip
    tc, mc = _frozen_catalogue(s[n_s : 2 * n_s], models[ct], b_values[ct], warmup_years, 1.0)
    t_ms, cut = float(ctx["t_ms"]), float(ctx["cutoff"])
    q_true = float(ctx["q"]) + scenario.dq
    i_hat = omori_integral(2026.0 - t_ms, cut - t_ms, float(ctx["q"]))
    i_true = omori_integral(2026.0 - t_ms, cut - t_ms, q_true)
    a_true = float(np.exp(ctx["log_A"])) * i_hat / i_true  # same expected tail count in the fit
    n_inj = 0
    if scenario.tail:
        it, im = inject_tail(np.random.default_rng(s[-1]), a_true, q_true, t_ms, 2026.0, 2037.0,
                             np.asarray(ctx["mag_values"], float),
                             np.asarray(ctx["mag_counts"], float))  # fmt: skip
        n_inj = int(((it >= 2027.0) & (it < 2030.0)).sum())
        tg, mg = np.concatenate([tg, it]), np.concatenate([mg, im])
    # the real December 2025 sequence events are triggers in the fit (as with real data)
    tg = np.concatenate([tg, np.asarray(ctx["dec_t"], float)])
    mg = np.concatenate([mg, np.asarray(ctx["dec_m"], float)])
    o = np.argsort(tg, kind="stable")
    tg, mg = tg[o], mg[o]
    row: dict[str, Any] = {"scenario": scenario.name, "rep": rep, "q_true": q_true,
                           "n_injected_2029": n_inj}  # fmt: skip
    fit: TermFit | None
    try:
        f0 = fit_sequence_term(tg, mg, models[gl], t_ms, 2026.0, cut)
        row.update(q_fit=f0.q, log_A_fit=f0.log_A, se_q_fit=float(np.sqrt(f0.cov[1][1])))
        fit = f0
    except (ValueError, np.linalg.LinAlgError) as e:
        fit = None
        row.update(fit_error=str(e))
    cg = pd.DataFrame({"t": tg, "mag": mg})
    cg = cg[cg.t >= 2026.0]
    cc = pd.DataFrame({"t": tc, "mag": mc})
    cc = cc[cc.t >= 2026.0]
    for end, _ in LOOKS:
        tag = f"{int(end) - 1}"
        for name, f, var in (("none", None, "A"), ("A", fit, "A"), ("B", fit, "B")):
            if name != "none" and f is None:
                continue
            r = evaluate_pair_with_term(cg, cc, models, end, f, var)
            row[f"D_{name}_{tag}"] = float(r["D"])
            row[f"z_{name}_{tag}"] = float(r["z"])
            row[f"reject_{name}_{tag}"] = bool(r["reject"])
    row["seconds"] = round(time.time() - t0, 2)
    return row


# ---------------------------------------------------------------------------
# AP6b: bias of the preregistered C2 under a truth calibrated to the 2026 data
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LevelScenario:
    """Excess level E(t) = e0 * ((t - t_ms) / 0.5)^(-r) per yr on top of the frozen model."""

    name: str
    e0: float
    r: float = 1.0
    mu_factor: float = 1.0  # glacier background x factor from 2027 on (the sought signal)


LEVEL_SCENARIOS: dict[str, LevelScenario] = {
    s.name: s
    for s in (
        LevelScenario("e0", 0.0),
        LevelScenario("e75_r10", 75.0, 1.0),
        LevelScenario("e75_r05", 75.0, 0.5),
        LevelScenario("e150_r10", 150.0, 1.0),
        LevelScenario("e150_r05", 150.0, 0.5),
        LevelScenario("signal_e0", 0.0, mu_factor=1.5),
    )
}


def run_level_replicate(
    models: dict[str, Baseline],
    b_values: dict[str, float],
    ctx: dict[str, Any],
    scenario: LevelScenario,
    idx: int,
    rep: int,
    seed: int,
    warmup_years: float = 20.0,
) -> dict[str, Any]:
    """One AP6b replicate. Glacier catalogue = **real** events 2026-01-01..cutoff (``real_t``,
    ``real_m``) + synthetic truth from the cutoff on: frozen model (from a synthetic history, so
    without frozen offspring of the real sequence) + fast spike A_s (t - t_ms)^(-q_s) + excess
    level E(t), the last two without offspring. Control: frozen model. C2 as preregistered."""
    import time

    from .sequence_tail import inject_tail

    t0 = time.time()
    n_s = 2 + len(YEARS_SIM)
    s = _term_seeds(seed, idx, rep, 2 * n_s + 2)
    gl, ct = "SE_Alaska_AK", "Interior_AK_ctrl"
    cut, t_ms = float(ctx["cutoff"]), float(ctx["t_ms"])
    tg, mg = _frozen_catalogue(s[:n_s], models[gl], b_values[gl], warmup_years,
                               scenario.mu_factor)  # fmt: skip
    keep = tg >= cut
    tg, mg = tg[keep], mg[keep]
    tc, mc = _frozen_catalogue(s[n_s : 2 * n_s], models[ct], b_values[ct], warmup_years, 1.0)
    vals = np.asarray(ctx["mag_values"], float)
    wts = np.asarray(ctx["mag_counts"], float)
    st, sm = inject_tail(np.random.default_rng(s[-2]), float(ctx["spike_A"]),
                         float(ctx["spike_q"]), t_ms, cut, 2037.0, vals, wts)  # fmt: skip
    n_level = 0
    parts_t = [tg, st, np.asarray(ctx["real_t"], float)]
    parts_m = [mg, sm, np.asarray(ctx["real_m"], float)]
    if scenario.e0 > 0:
        amp = scenario.e0 * 0.5**scenario.r  # e0 at t - t_ms = 0.5 yr
        lt, lm = inject_tail(np.random.default_rng(s[-1]), amp, scenario.r, t_ms, cut, 2037.0,
                             vals, wts)  # fmt: skip
        n_level = int(((lt >= 2027.0) & (lt < 2030.0)).sum())
        parts_t.append(lt)
        parts_m.append(lm)
    tg, mg = np.concatenate(parts_t), np.concatenate(parts_m)
    o = np.argsort(tg, kind="stable")
    cg = pd.DataFrame({"t": tg[o], "mag": mg[o]})
    cg = cg[cg.t >= 2026.0]
    cc = pd.DataFrame({"t": tc, "mag": mc})
    cc = cc[cc.t >= 2026.0]
    row: dict[str, Any] = {"scenario": scenario.name, "rep": rep, "n_level_2029": n_level,
                           "n_spike_2029": int(((st >= 2027.0) & (st < 2030.0)).sum())}  # fmt: skip
    for end, _ in LOOKS:
        tag = f"{int(end) - 1}"
        r = evaluate_pair_with_term(cg, cc, models, end, None)
        row[f"D_{tag}"] = float(r["D"])
        row[f"z_{tag}"] = float(r["z"])
        row[f"reject_{tag}"] = bool(r["reject"])
        row[f"dlog_glac_{tag}"] = float(r["glacier"]["delta_log_mu"])
        row[f"n_glac_{tag}"] = int(r["glacier"]["n_new"])
    row["seconds"] = round(time.time() - t0, 2)
    return row
