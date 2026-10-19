"""AP2: window simulation of the frozen temporal ETAS, conditional on the history."""

from __future__ import annotations

import time

import numpy as np
import pytest

from glacial_seismic_sensitivity_utac.etas_adequacy import Baseline, load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import (
    expected_cluster_moments,
    simulate_window,
)
from glacial_seismic_sensitivity_utac.etas_adequacy.intensity import compensator

NO_HIST = (np.array([]), np.array([]))


def _base(**kw: float) -> Baseline:
    p = dict(
        region="synthetic",
        mc_ref=2.0,
        K=0.045,
        alpha=0.5,
        c_yr=1e-3,
        p=1.05,
        tmax_yr=1.0,
        log_mu_ref=float(np.log(20.0)),
        sigma_year=0.3,
        n_ref_years=10,
    )
    p.update(kw)
    return Baseline(**p)  # type: ignore[arg-type]


def test_long_window_mean_and_variance_match_branching_analytics() -> None:
    """No history, T = 100 yr >> tmax: E[N] = mu T/(1-n), Var[N] = mu T E[S^2] (edge effects
    shrink with T: measured Var/analytic 0.91 at T = 5, 0.97 at T = 20, 1.02 +- 0.03 at T = 100)."""
    base = _base()
    n, es2 = expected_cluster_moments(base)
    assert 0.4 < n < 0.55
    s = simulate_window(base, *NO_HIST, 0.0, 100.0, 600, dm=0.0, seed=7)
    N = s.counts
    mu, T = base.mu_ref, 100.0
    assert N.mean() == pytest.approx(mu * T / (1 - n), rel=0.02)
    assert N.var(ddof=1) == pytest.approx(mu * T * es2, rel=0.15)


def test_martingale_identity_with_history_on_short_window() -> None:
    """E[N(window)] = E[Lambda(window)] exactly (no edge approximation), including the history."""
    base = _base(alpha=1.0)
    ht = np.array([-0.95, -0.5, -0.2, -0.05])
    hm = np.array([4.5, 3.0, 5.0, 3.5])
    s = simulate_window(base, ht, hm, 0.0, 1.0, 800, dm=0.0, seed=2)
    lam = np.array(
        [
            compensator(
                0.0, 1.0, np.concatenate([ht, t]), np.concatenate([hm, m]), base, base.mu_ref
            )
            for t, m in zip(s.times, s.mags, strict=True)
        ]
    )
    d = s.counts - lam
    assert abs(d.mean()) < 3 * d.std(ddof=1) / np.sqrt(len(d))


def test_history_adds_its_window_offspring_and_their_cascades() -> None:
    base = _base(alpha=1.0)
    ht, hm = np.array([-0.3]), np.array([5.5])
    with_h = simulate_window(base, ht, hm, 0.0, 30.0, 400, dm=0.0, seed=3).counts
    without = simulate_window(base, *NO_HIST, 0.0, 30.0, 400, dm=0.0, seed=3).counts
    n, _ = expected_cluster_moments(base)
    w = base.K * np.exp(base.alpha * (5.5 - base.mc_ref))
    from glacial_seismic_sensitivity_utac.etas_nonstat import kint

    direct = w * float(
        kint(np.array([0.7]), base.c_yr, base.p, 1.0)[0]
        - kint(np.array([0.3]), base.c_yr, base.p, 1.0)[0]
    )
    extra = with_h.mean() - without.mean()
    se = np.sqrt(with_h.var(ddof=1) / len(with_h) + without.var(ddof=1) / len(without))
    assert abs(extra - direct / (1 - n)) < 4 * se


def test_history_offspring_only_inside_the_window_and_history_not_returned() -> None:
    base = _base(alpha=1.0)
    ht, hm = np.array([-0.1, -0.02]), np.array([6.0, 5.0])
    s = simulate_window(base, ht, hm, 0.0, 0.5, 50, seed=4)
    for t in s.times:
        assert np.all((t >= 0.0) & (t < 0.5))
        assert np.all(np.diff(t) >= 0)
    assert s.counts.mean() > base.mu_ref * 0.5  # strong history: many window offspring


def test_mixture_mode_mean_and_overdispersion() -> None:
    base = _base(sigma_year=0.5)
    n, _ = expected_cluster_moments(base)
    ref = simulate_window(base, *NO_HIST, 0.0, 30.0, 600, mu_mode="ref", dm=0.0, seed=5)
    mix = simulate_window(base, *NO_HIST, 0.0, 30.0, 600, mu_mode="mixture", dm=0.0, seed=5)
    expected = np.exp(base.log_mu_ref + 0.5 * base.sigma_year**2) * 30.0 / (1 - n)
    assert mix.counts.mean() == pytest.approx(expected, rel=0.08)
    assert mix.counts.var() > 3 * ref.counts.var()
    assert np.all(ref.mu == base.mu_ref) and np.std(np.log(mix.mu)) == pytest.approx(0.5, rel=0.1)


def test_reproducible_and_independent_of_n_sim() -> None:
    base = _base()
    a = simulate_window(base, *NO_HIST, 0.0, 1.0, 3, seed=11)
    b = simulate_window(base, *NO_HIST, 0.0, 1.0, 6, seed=11)
    c = simulate_window(base, *NO_HIST, 0.0, 1.0, 3, seed=12)
    for k in range(3):
        assert np.array_equal(a.times[k], b.times[k]) and np.array_equal(a.mags[k], b.mags[k])
    assert not np.array_equal(a.times[0], c.times[0])


def test_magnitudes_binned_like_frozen_simulator() -> None:
    s = simulate_window(_base(), *NO_HIST, 0.0, 5.0, 5, dm=0.1, seed=13)
    m = np.concatenate(s.mags)
    assert m.min() >= 2.0 and np.allclose(np.round(m * 10), m * 10)


def test_fixed_mode_uses_given_mu() -> None:
    s = simulate_window(_base(), *NO_HIST, 0.0, 1.0, 4, mu_mode="fixed", mu=7.5, seed=1)
    assert np.all(s.mu == 7.5)


@pytest.mark.parametrize(
    "kw",
    [
        dict(mu_mode="nope"),
        dict(mu_mode="fixed"),
        dict(mu_mode="ref", mu=3.0),
        dict(mu_mode="fixed", mu=-1.0),
        dict(n_sim=0),
    ],
)
def test_invalid_arguments_raise(kw: dict[str, object]) -> None:
    args = dict(n_sim=2)
    args.update(kw)
    with pytest.raises(ValueError):
        simulate_window(_base(), *NO_HIST, 0.0, 1.0, **args)  # type: ignore[arg-type]


def test_history_after_t0_and_infinite_branching_are_rejected() -> None:
    with pytest.raises(ValueError, match="before t0"):
        simulate_window(_base(), np.array([0.5]), np.array([3.0]), 0.0, 1.0, 1)
    with pytest.raises(ValueError, match="branching"):
        simulate_window(_base(alpha=2.5), *NO_HIST, 0.0, 1.0, 1)


def test_supercritical_model_is_rejected_before_simulating() -> None:
    """n >= 1 would grow without bound (an n = 4.4 test case once exhausted the machine)."""
    hot = _base(alpha=1.0, K=0.25, p=1.3, c_yr=1e-2)
    assert expected_cluster_moments(hot)[0] > 1
    with pytest.raises(ValueError, match="supercritical"):
        simulate_window(hot, *NO_HIST, 0.0, 1.0, 1)


def test_max_events_guard_stops_a_large_catalogue() -> None:
    with pytest.raises(RuntimeError, match="max_events"):
        simulate_window(_base(), *NO_HIST, 0.0, 10.0, 1, max_events=50)
    with pytest.raises(ValueError, match="max_events"):
        simulate_window(_base(), *NO_HIST, 0.0, 1.0, 1, max_events=0)


def test_frozen_se_alaska_1000_windows_fast_enough() -> None:
    """Plan acceptance: 1000 one-year SE-Alaska windows in < 20 s (measured ~1 s)."""
    se = load_baselines()["SE_Alaska_AK"]
    t = time.perf_counter()
    s = simulate_window(
        se, np.array([2025.3, 2025.8]), np.array([3.0, 2.5]), 2026.0, 2027.0, 1000, seed=3
    )
    assert time.perf_counter() - t < 20.0
    assert len(s.times) == 1000
