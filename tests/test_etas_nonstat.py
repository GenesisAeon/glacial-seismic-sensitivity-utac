"""Synthetic-data recovery tests for the nonstationary-background ETAS (v0.2, M2)."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import integrate

from glacial_seismic_sensitivity_utac import etas_nonstat as E
from glacial_seismic_sensitivity_utac import quiescence as Q

TRUE = dict(K=0.0276, alpha=1.0, c=0.002, p=1.15)
T0, T1 = 1995.0, 2026.0
MASK_SHOCKS = ((2009.0, 8.0), (2012.0, 8.0), (2015.0, 7.8))


def _cat(fn, seed, mainshocks=()):  # type: ignore[no-untyped-def]
    c = E.simulate(fn, T0, T1, rng=np.random.default_rng(seed), mainshocks=mainshocks, **TRUE)
    return c.t.to_numpy(), c.mag.to_numpy()


def test_pairs_and_kernel_integral() -> None:
    t = np.array([0.0, 0.1, 0.1, 0.5, 2.0])
    ii, jj, dt = E.pairs(t, 1.0)
    assert set(zip(ii.tolist(), jj.tolist(), strict=True)) == {
        (1, 0),
        (2, 0),
        (3, 0),
        (3, 1),
        (3, 2),
    }
    assert np.all(dt > 0)
    assert E.n_pairs(t, 1.0) >= len(ii)  # n_pairs counts ties too (upper bound)
    num = integrate.quad(lambda s: (s + 0.002) ** -1.15, 0.0, 1.0, points=[0.01, 0.1])[0]
    assert E.kint(np.array([1.0]), 0.002, 1.15, 1.0)[0] == pytest.approx(num, rel=1e-3)
    assert E.kint(np.array([5.0]), 0.002, 1.15, 1.0)[0] == pytest.approx(num, rel=1e-3)


def test_gradient_matches_finite_differences() -> None:
    t, m = _cat(lambda x: 30.0 + 0 * x, 1)
    edges = np.arange(T0, T1 + 0.5, 5.0)
    edges[-1] = T1
    d = E.ETASData.build(t, m, 2.0, T0, T1, edges, 1.0)
    x = np.concatenate([np.log(np.full(d.n_bins, 25.0)), [np.log(0.02), 0.9, np.log(0.003), 1.2]])
    _, g = E.loglik_grad(x, d, 1.0)
    for k in range(len(x)):
        h = 1e-6
        xp, xm = x.copy(), x.copy()
        xp[k] += h
        xm[k] -= h
        num = (E.loglik_grad(xp, d, 1.0, False)[0] - E.loglik_grad(xm, d, 1.0, False)[0]) / (2 * h)
        assert g[k] == pytest.approx(num, rel=1e-4, abs=1e-3)


def test_single_bin_equals_v01_stationary_etas() -> None:
    t, m = _cat(lambda x: 40.0 + 0 * x, 2)
    f = E.fit_nonstationary(t, m, 2.0, T0, T1, edges=np.array([T0, T1]))
    v01 = Q.fit_etas(t, m, 2.0, T0, T1, tmax=1.0)
    assert f.mu[0] == pytest.approx(v01["mu_per_yr"], rel=1e-3)
    assert f.p == pytest.approx(v01["p"], abs=1e-3)
    assert f.loglik == pytest.approx(v01["loglik"], abs=1e-3)


@pytest.mark.parametrize("seed", [11, 12, 13])
def test_stationary_background_gives_no_false_trend(seed: int) -> None:
    t, m = _cat(lambda x: 40.0 + 0 * x, seed)
    s1, f = E.fit_two_stage(t, m, 2.0, T0, T1)
    tr = E.log_mu_trend(f, (T0, T1))
    assert abs(tr["slope_per_decade"]) < 3 * tr["se"]
    assert 0.25 < s1.branching_ratio < 0.8  # true ~0.5


def test_linear_rise_is_recovered() -> None:
    fn = lambda x: 30.0 + 30.0 * (x - T0) / (T1 - T0)  # noqa: E731  ln 2 over 31 yr
    true = np.log(2) / 3.1  # ~0.22 per decade (approx. for a linear rise)
    hits = 0
    for seed in (21, 22, 23):
        t, m = _cat(fn, seed)
        _, f = E.fit_two_stage(t, m, 2.0, T0, T1)
        tr = E.log_mu_trend(f, (T0, T1))
        assert abs(tr["slope_per_decade"] - true) < 3 * tr["se"]
        hits += tr["slope_per_decade"] / tr["se"] > 1.645
    assert hits >= 2


def test_masked_background_rise_is_classified() -> None:
    fn = lambda x: np.where(x < 2016, 40.0, 60.0)  # noqa: E731
    t, m = _cat(fn, 0, MASK_SHOCKS)
    na = ((t >= 2008) & (t < 2020)).sum()
    nb = ((t >= 2020) & (t < 2026)).sum()
    total = (nb / 6) / (na / 12)
    assert total < 1.0  # the total rate falls: a stationary analysis would see 'quiet'
    _, f = E.fit_two_stage(t, m, 2.0, T0, T1)
    wr = E.window_ratio(f, (2008, 2020), (2020, 2026))
    assert E.classify_background(total, wr["lo95"], wr["hi95"]).startswith("masked")


def test_aftershock_decay_alone_is_not_a_background_rise() -> None:
    t, m = _cat(lambda x: 40.0 + 0 * x, 0, MASK_SHOCKS)
    na = ((t >= 2008) & (t < 2020)).sum()
    nb = ((t >= 2020) & (t < 2026)).sum()
    _, f = E.fit_two_stage(t, m, 2.0, T0, T1)
    wr = E.window_ratio(f, (2008, 2020), (2020, 2026))
    cls = E.classify_background((nb / 6) / (na / 12), wr["lo95"], wr["hi95"])
    assert not cls.startswith("masked") and not cls.startswith("background rise")


def test_mu_window_mle_recovers_rate_with_frozen_trig() -> None:
    t, m = _cat(lambda x: 50.0 + 0 * x, 5)
    trig = dict(K=TRUE["K"], alpha=TRUE["alpha"], c_yr=TRUE["c"], p=TRUE["p"], tmax=1.0)
    r = E.mu_window_mle(t, m, 2.0, trig, 2016.0, 2026.0)
    assert abs(r["log_mu"] - np.log(50.0)) < 3 * r["log_mu_se"] + 0.05
    assert r["n"] > 0


def test_did_and_bh() -> None:
    r = E.did_test(dict(slope_per_decade=0.3, se=0.1), dict(slope_per_decade=0.0, se=0.1))
    assert r["z"] == pytest.approx(0.3 / np.hypot(0.1, 0.1))
    assert 0 < r["p_one"] < 0.05
    adj = E.bh_adjust(np.array([0.01, 0.04, 0.03]))
    assert adj.tolist() == pytest.approx([0.03, 0.04, 0.04])


def test_classification_rules() -> None:
    assert E.classify_background(0.8, 1.1, 1.5).startswith("masked")
    assert E.classify_background(1.2, 1.1, 1.5).startswith("background rise")
    assert E.classify_background(0.8, 0.5, 0.9).startswith("background decrease")
    assert E.classify_background(1.0, 0.8, 1.2).startswith("no resolvable")


def test_window_ratio_uses_half_open_windows() -> None:
    # Regression for the Codex review on PR #1: (2008, 2020) must mean calendar years 2008-2019.
    edges = np.arange(1995.0, 2027.0)
    B = len(edges) - 1
    log_mu = np.where(edges[:-1] >= 2020, np.log(2.0), 0.0)
    f = E.NSFit(
        edges=edges,
        mu=np.exp(log_mu),
        log_mu_se=np.full(B, 0.1),
        K=0.0,
        alpha=1.0,
        c_yr=0.01,
        p=1.1,
        loglik=0.0,
        n_target=0,
        n_per_bin=np.zeros(B, int),
        converged=True,
        branching_ratio=0.0,
        cov=np.eye(B + 4),
    )
    tab = f.table()
    sel_a = (tab.t_start >= 2008.0) & (tab.t_end <= 2020.0)
    sel_b = (tab.t_start >= 2020.0) & (tab.t_end <= 2026.0)
    assert sel_a.sum() == 12 and sel_b.sum() == 6
    jitter = np.random.default_rng(0).normal(0, 1e-3, B)
    f.mu = np.exp(log_mu + jitter)
    wr = E.window_ratio(f, (2008.0, 2020.0), (2020.0, 2026.0))
    assert wr["ratio"] == pytest.approx(2.0, rel=0.01)
    # the old call (2008, 2019), (2020, 2025) silently dropped 2019 and 2025
    old = E.window_ratio(f, (2008, 2019), (2020, 2025))
    assert np.isfinite(old["ratio"])


def test_simulate_handles_p_equal_one_and_boundary() -> None:
    # p at the fit's lower bound (1.0001) occurs in 7 of 8 real regions; p = 1 exactly must not
    # divide by zero in the inverse CDF, and offspring delays must stay within (0, tmax].
    for p in (1.0, 1.0001):
        cat = E.simulate(
            lambda x: 50.0 + 0 * x,
            0.0,
            20.0,
            K=0.04,
            alpha=1.0,
            c=1e-4,
            p=p,
            rng=np.random.default_rng(1),
        )
        assert np.isfinite(cat.t).all() and len(cat) > 1000
        assert (cat.t >= 0).all() and (cat.t < 20.0).all()
    # Omori inverse CDF at p = 1 matches the analytic CDF log((x+c)/c)/log((tmax+c)/c)
    c, tmax = 1e-3, 1.0
    u = np.random.default_rng(2).uniform(0, 1, 200_000)
    dt = c * ((tmax + c) / c) ** u - c
    q = 0.1
    assert (dt <= q).mean() == pytest.approx(
        np.log((q + c) / c) / np.log((tmax + c) / c), abs=0.005
    )
