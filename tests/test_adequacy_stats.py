"""AP3: adequacy test statistics (correctness, size, power smoke tests)."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from glacial_seismic_sensitivity_utac.etas_adequacy import Baseline
from glacial_seismic_sensitivity_utac.etas_adequacy import stats as S
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import simulate_window
from glacial_seismic_sensitivity_utac.etas_adequacy.intensity import compensator, intensity

NO = (np.array([]), np.array([]))


def _base(**kw: float) -> Baseline:
    p = dict(
        region="synthetic",
        mc_ref=2.0,
        K=0.045,
        alpha=1.0,
        c_yr=1e-3,
        p=1.05,
        tmax_yr=1.0,
        log_mu_ref=float(np.log(60.0)),
        sigma_year=0.2,
        n_ref_years=10,
    )
    p.update(kw)
    return Baseline(**p)  # type: ignore[arg-type]


def _history(base: Baseline, seed: int = 1) -> tuple[np.ndarray, np.ndarray]:
    h = simulate_window(base, *NO, -1.0, 0.0, 1, seed=seed)
    return h.times[0], h.mags[0]


# ----------------------------------------------------------------------------- N-test
def test_n_test_poisson_matches_scipy() -> None:
    r = S.n_test_poisson(12, 9.5)
    assert r.delta1 == pytest.approx(1 - stats.poisson.cdf(11, 9.5))
    assert r.delta2 == pytest.approx(stats.poisson.cdf(12, 9.5))
    assert r.delta1 + r.delta2 == pytest.approx(1 + stats.poisson.pmf(12, 9.5))
    assert r.p_two_sided == pytest.approx(2 * min(r.delta1, r.delta2))


def test_n_test_mixture_reduces_to_poisson_and_widens() -> None:
    for n in (3, 10, 20):
        a, b = S.n_test_mixture(n, 10.0, 1e-6), S.n_test_poisson(n, 10.0)
        assert a.delta1 == pytest.approx(b.delta1, abs=1e-6)
        assert a.delta2 == pytest.approx(b.delta2, abs=1e-6)
    tight, wide = S.n_test_poisson(25, 10.0), S.n_test_mixture(25, 10.0, 0.5)
    assert wide.delta1 > tight.delta1  # overdispersion makes a high count less extreme


def test_n_test_mixture_matches_monte_carlo() -> None:
    rng = np.random.default_rng(3)
    lam = 40.0 * np.exp(rng.normal(0, 0.4, 400_000))
    n = rng.poisson(lam)
    r = S.n_test_mixture(55, 40.0, 0.4)
    assert r.delta1 == pytest.approx(np.mean(n >= 55), abs=3e-3)
    assert r.delta2 == pytest.approx(np.mean(n <= 55), abs=3e-3)


def test_n_test_empirical_quantiles() -> None:
    r = S.n_test_empirical(5, np.array([3, 4, 5, 6, 7]))
    assert (r.delta1, r.delta2) == (0.6, 0.6)


@pytest.mark.parametrize("bad", [-1, 2.5, True])
def test_n_test_rejects_invalid_counts(bad: object) -> None:
    with pytest.raises(ValueError):
        S.n_test_poisson(bad, 3.0)  # type: ignore[arg-type]


# ----------------------------------------------------------------------------- M-test
def test_m_test_size_and_power() -> None:
    base = _base(log_mu_ref=float(np.log(150.0)))
    sims = simulate_window(base, *NO, 0.0, 1.0, 60, seed=4)
    obs = simulate_window(base, *NO, 0.0, 1.0, 20, seed=5)
    kappas = [S.m_test_catalog(m, sims.mags) for m in obs.mags]
    assert np.mean(np.array(kappas) < 0.05) <= 0.2  # size (CI-sized check)
    shifted = [np.round(m + 0.3, 6) for m in obs.mags[:10]]  # Mc jump +0.3: lowest bins vanish
    assert np.mean([S.m_test_catalog(m, sims.mags) < 0.05 for m in shifted]) >= 0.8


def test_m_test_ks2_size_and_power() -> None:
    rng = np.random.default_rng(6)
    gr = lambda n, mc: np.round(mc - 0.05 - np.log(1 - rng.uniform(0, 1, n)) / np.log(10), 1)  # noqa: E731
    ref = gr(2000, 2.0)
    same = [S.m_test_ks2(gr(150, 2.0), ref) for _ in range(40)]
    assert np.mean(np.array(same) < 0.05) <= 0.2
    assert S.m_test_ks2(gr(150, 2.3), ref) < 0.01


# ----------------------------------------------------------------------------- pseudo-LL
def test_window_loglik_matches_intensity_and_compensator() -> None:
    base = _base()
    ht, hm = _history(base)
    w = simulate_window(base, ht, hm, 0.0, 1.0, 1, seed=7)
    wt, wm = w.times[0], w.mags[0]
    sum_log, total, n = S.window_loglik(ht, hm, wt, wm, (0.0, 1.0), base, base.mu_ref)
    allt, allm = np.concatenate([ht, wt]), np.concatenate([hm, wm])
    lam = intensity(wt, allt, allm, base, base.mu_ref)
    assert n == len(wt)
    assert sum_log == pytest.approx(float(np.sum(np.log(lam))), rel=1e-10)
    assert total == pytest.approx(compensator(0.0, 1.0, allt, allm, base, base.mu_ref), rel=1e-12)
    assert S.pseudo_loglik(sum_log, total, n, conditional=True) == pytest.approx(
        sum_log - n * np.log(total)
    )


def _ll_gamma(base: Baseline, data_base: Baseline, seed: int, conditional: bool) -> float:
    ht, hm = _history(data_base, seed)
    obs = simulate_window(data_base, ht, hm, 0.0, 1.0, 1, seed=seed + 1)
    sims = simulate_window(base, ht, hm, 0.0, 1.0, 60, seed=seed + 2)
    ll = lambda t, m: S.pseudo_loglik(  # noqa: E731
        *S.window_loglik(ht, hm, t, m, (0.0, 1.0), base, base.mu_ref), conditional=conditional
    )
    l_sim = np.array([ll(t, m) for t, m in zip(sims.times, sims.mags, strict=True)])
    return S.ll_test(ll(obs.times[0], obs.mags[0]), l_sim)


def test_ll_test_size_under_true_model() -> None:
    base = _base()
    g = [_ll_gamma(base, base, 100 + 10 * r, conditional=True) for r in range(25)]
    assert np.mean(np.array(g) < 0.05) <= 0.2


def test_ll_test_is_blind_to_data_clustering_more_than_the_model() -> None:
    """One-sided by construction: data clustering *more* than the model (K x 2.4) put their
    events into the model's intensity peaks and score *higher* than the model's own
    simulations, so gamma is pushed *up* and the test cannot reject. Model n = 0.66, data n = 0.95;
    measured gamma 0.52-0.95 (mean 0.73), none < 0.05. With a supercritical K x 2.4 (n = 1.14,
    no longer allowed) gamma was 1.0 in 10/10."""
    base = _base()
    data = _base(K=0.09, alpha=0.5)
    g = np.array([_ll_gamma(base, data, 300 + 10 * r, conditional=True) for r in range(6)])
    assert np.all(g >= 0.05) and g.mean() > 0.6


def test_ll_test_power_against_a_model_clustering_more_than_the_data() -> None:
    """The direction the L-test does detect: the model's peaks after data events stay empty.
    Model n = 0.95, data n = 0.29. (Against data with n = 0.66 it rejected only 4/8.)"""
    model = _base(K=0.09, alpha=0.5)
    data = _base(K=0.02)
    g = [_ll_gamma(model, data, 300 + 10 * r, conditional=True) for r in range(8)]
    assert np.mean(np.array(g) < 0.05) >= 0.7


# ----------------------------------------------------------------------------- Ogata KS
def test_ogata_ks_reestimates_mu_like_the_frozen_mle() -> None:
    from glacial_seismic_sensitivity_utac.etas_nonstat import mu_window_mle

    base = _base()
    ht, hm = _history(base)
    w = simulate_window(base, ht, hm, 0.0, 1.0, 1, seed=8)
    r = S.ogata_ks(ht, hm, w.times[0], w.mags[0], (0.0, 1.0), base)
    ref = mu_window_mle(
        np.concatenate([ht, w.times[0]]),
        np.concatenate([hm, w.mags[0]]),
        2.0,
        base.trig(),
        0.0,
        1.0,
    )
    assert r.mu_hat == pytest.approx(ref["mu"], rel=1e-12) and r.n == len(w.times[0])


def test_nominal_ogata_ks_is_conservative_and_bootstrap_restores_size() -> None:
    """Lilliefors effect: with mu re-estimated, nominal KS p-values are too large. Measured over
    40 replicates: nominal reject rate 0.000 (mean p 0.62), bootstrap 0.075 (mean p 0.54).
    CI-sized check with 20 replicates and B = 49."""
    base = _base()
    ht, hm = _history(base)
    nom, boo = [], []
    for r in range(20):
        w = simulate_window(base, ht, hm, 0.0, 1.0, 1, seed=1000 + r)
        o = S.ogata_ks_bootstrap(
            ht, hm, w.times[0], w.mags[0], (0.0, 1.0), base, n_boot=49, seed=5000 + r
        )
        nom.append(o.p_nominal)
        boo.append(o.p_bootstrap)
    assert np.mean(nom) > 0.55  # inflated p-values
    assert 0.35 < float(np.mean(boo)) < 0.65  # roughly uniform after calibration
    assert np.mean(np.array(boo) < 0.05) <= 0.2


def test_ogata_ks_power_against_wrong_omori_exponent() -> None:
    """Data with p = 1.3 (faster decay) evaluated under the frozen p = 1.0001. Both subcritical
    (n = 0.73 model, 0.79 data); an earlier K = 0.25 gave n = 4.4 and a runaway cascade."""
    model = _base(p=1.0001, c_yr=1e-4)
    data = _base(p=1.3, c_yr=1e-2, K=0.045, log_mu_ref=float(np.log(30.0)))
    hits = 0
    for r in range(6):
        ht, hm = _history(data, 40 + r)
        w = simulate_window(data, ht, hm, 0.0, 2.0, 1, seed=60 + r)
        o = S.ogata_ks_bootstrap(
            ht, hm, w.times[0], w.mags[0], (0.0, 2.0), model, n_boot=49, seed=r
        )
        hits += o.p_bootstrap is not None and o.p_bootstrap < 0.05
    assert hits >= 4


# ----------------------------------------------------------------------------- IG, t-test
def test_information_gain_zero_for_poisson_model_and_positive_for_true_etas() -> None:
    pois = _base(K=0.0)
    w = simulate_window(pois, *NO, 0.0, 1.0, 1, seed=9)
    sl, tot, n = S.window_loglik(*NO, w.times[0], w.mags[0], (0.0, 1.0), pois, 60.0)
    assert S.ig_per_event(S.pseudo_loglik(sl, tot, n), n, 60.0, 1.0) == pytest.approx(
        0.0, abs=1e-12
    )
    base = _base()
    gains = []
    for r in range(12):
        ht, hm = _history(base, 200 + r)
        w = simulate_window(base, ht, hm, 0.0, 1.0, 1, seed=220 + r)
        sl, tot, n = S.window_loglik(ht, hm, w.times[0], w.mags[0], (0.0, 1.0), base, base.mu_ref)
        gains.append(S.ig_per_event(S.pseudo_loglik(sl, tot, n), n, n / 1.0, 1.0))
    t, p = S.paired_t_test(np.array(gains))
    assert t > 0 and p < 0.01


def test_paired_t_test_matches_scipy() -> None:
    g = np.array([0.1, -0.05, 0.2, 0.15, 0.0])
    t, p = S.paired_t_test(g)
    ref = stats.ttest_1samp(g, 0.0)
    assert (t, p) == pytest.approx((ref.statistic, ref.pvalue))


def test_m_test_ks2_ignores_float_representation_of_binned_magnitudes() -> None:
    # F1 (freeze v0.4.0): the same binned magnitudes in two float representations, as produced
    # by catalog.prepare ((m / 0.1).round() * 0.1 -> 2.3000000000000003) and by the simulator
    # (np.round(..., 6) -> 2.3). Identical distributions must give p = 1. Before the guard the
    # KS statistic broke every tie in one direction and returned a tiny p.
    grid = np.arange(20, 45) / 10.0
    rng = np.random.default_rng(7)
    m = rng.choice(grid, size=2_000, p=np.r_[np.full(24, 0.04), 0.04])
    as_prepared = (m / 0.1).round() * 0.1
    as_simulated = np.round(m, 6)
    assert not np.array_equal(as_prepared, as_simulated)  # the representations really differ
    assert S.m_test_ks2(as_simulated, as_prepared) == pytest.approx(1.0)
