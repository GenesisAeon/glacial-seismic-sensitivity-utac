"""AP1: intensity, compensator and transformed times of the frozen temporal ETAS."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import integrate, stats

from glacial_seismic_sensitivity_utac import etas_nonstat
from glacial_seismic_sensitivity_utac.etas_adequacy import Baseline, load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy.intensity import (
    compensator,
    intensity,
    transformed_times,
)


def _base(**kw: float) -> Baseline:
    p = dict(
        region="synthetic",
        mc_ref=2.0,
        K=0.045,
        alpha=1.0,
        c_yr=1e-3,
        p=1.05,
        tmax_yr=1.0,
        log_mu_ref=float(np.log(40.0)),
        sigma_year=0.2,
        n_ref_years=10,
    )
    p.update(kw)
    return Baseline(**p)  # type: ignore[arg-type]


HIST_T = np.array([2025.10, 2025.62, 2025.80, 2025.95, 2026.05, 2026.40, 2026.41, 2026.90])
HIST_M = np.array([3.4, 2.2, 4.1, 2.6, 2.0, 3.0, 2.3, 2.8])


def _quad_compensator(a: float, b: float, base: Baseline, mu: float) -> float:
    """Independent reference: integrate lambda piecewise between all kinks (event times and
    event times + tmax), with the substitution s = log(t - t_left + c) near each left kink."""
    kinks = np.concatenate([HIST_T, HIST_T + base.tmax_yr, [a, b]])
    kinks = np.unique(kinks[(kinks >= a) & (kinks <= b)])
    total = 0.0
    for lo, hi in zip(kinks[:-1], kinks[1:], strict=True):
        c = base.c_yr

        def f(s: float, lo: float = lo, c: float = c) -> float:
            x = lo + np.exp(s) - c
            return float(intensity(np.array([x]), HIST_T, HIST_M, base, mu)[0] * np.exp(s))

        val, _ = integrate.quad(
            f, np.log(c), np.log(hi - lo + c), epsabs=0, epsrel=1e-11, limit=400
        )
        total += val
    return total


@pytest.mark.parametrize("p,c", [(1.0001, 3.69e-5), (1.05, 1e-3), (1.3, 1e-2)])
def test_compensator_matches_quadrature(p: float, c: float) -> None:
    base = _base(p=p, c_yr=c)
    for a, b in [(2026.0, 2027.0), (2026.2, 2026.45), (2025.5, 2026.0)]:
        got = compensator(a, b, HIST_T, HIST_M, base, mu=40.0)
        ref = _quad_compensator(a, b, base, 40.0)
        assert got == pytest.approx(ref, rel=1e-6)


def test_frozen_baseline_compensator_matches_quadrature() -> None:
    base = load_baselines()["SE_Alaska_AK"]
    got = compensator(2026.0, 2027.0, HIST_T, HIST_M, base, mu=base.mu_ref)
    assert got == pytest.approx(_quad_compensator(2026.0, 2027.0, base, base.mu_ref), rel=1e-6)


def test_derivative_of_compensator_is_intensity() -> None:
    base = _base()
    h = 1e-7
    # not at a kink t_j + tmax (e.g. 2026.95 = 2025.95 + 1 yr), where Lambda is not differentiable
    for x in [2026.13, 2026.5, 2026.93]:
        num = (
            compensator(2026.0, x + h, HIST_T, HIST_M, base, 40.0)
            - compensator(2026.0, x - h, HIST_T, HIST_M, base, 40.0)
        ) / (2 * h)
        assert num == pytest.approx(
            intensity(np.array([x]), HIST_T, HIST_M, base, 40.0)[0], rel=1e-5
        )


def test_transformed_times_are_cumulative_compensator() -> None:
    base = _base()
    tau, total = transformed_times(HIST_T, HIST_M, (2026.0, 2027.0), base, 40.0)
    ev = HIST_T[HIST_T >= 2026.0]
    assert len(tau) == len(ev)
    for x, tx in zip(ev, tau, strict=True):
        assert tx == pytest.approx(compensator(2026.0, x, HIST_T, HIST_M, base, 40.0), rel=1e-12)
    assert total == pytest.approx(
        compensator(2026.0, 2027.0, HIST_T, HIST_M, base, 40.0), rel=1e-12
    )
    assert np.all(np.diff(tau) >= 0)


def test_no_triggering_beyond_tmax_and_none_from_later_events() -> None:
    base = _base()
    lam = intensity(np.array([2027.2]), np.array([2026.1]), np.array([5.0]), base, 3.0)
    assert lam[0] == 3.0  # 1.1 yr after the event: beyond tmax = 1 yr
    lam = intensity(np.array([2026.0]), np.array([2026.1]), np.array([5.0]), base, 3.0)
    assert lam[0] == 3.0  # a later event never triggers an earlier time


def _simulated(seed: int) -> tuple[np.ndarray, np.ndarray, Baseline]:
    base = _base()
    cat = etas_nonstat.simulate(
        lambda x: np.full_like(x, 40.0),
        0.0,
        12.0,
        base.K,
        base.alpha,
        base.c_yr,
        base.p,
        mc=base.mc_ref,
        b=1.0,
        tmax=base.tmax_yr,
        rng=np.random.default_rng(seed),
        dm=0.0,
    )
    return cat["t"].to_numpy(), cat["mag"].to_numpy(), base


def test_transformed_intervals_are_exp1_under_the_true_model() -> None:
    t, m, base = _simulated(11)
    tau, _ = transformed_times(t, m, (2.0, 12.0), base, 40.0)
    gaps = np.diff(np.concatenate([[0.0], tau]))
    assert len(gaps) > 300
    assert stats.kstest(gaps, "expon").pvalue > 0.01


def test_transformed_intervals_detect_wrong_productivity() -> None:
    """Power smoke test: evaluating with K/3 instead of the true K is rejected."""
    t, m, base = _simulated(11)
    wrong = _base(K=base.K / 3)
    tau, _ = transformed_times(t, m, (2.0, 12.0), wrong, 40.0)
    gaps = np.diff(np.concatenate([[0.0], tau]))
    assert stats.kstest(gaps, "expon").pvalue < 0.01


def test_mean_compensator_matches_mean_count() -> None:
    lam, n = [], []
    for seed in range(30):
        t, m, base = _simulated(100 + seed)
        _, total = transformed_times(t, m, (2.0, 12.0), base, 40.0)
        lam.append(total)
        n.append(int(np.sum((t >= 2.0) & (t < 12.0))))
    diff = np.array(n) - np.array(lam)
    assert abs(diff.mean()) < 3 * diff.std(ddof=1) / np.sqrt(len(diff))


@pytest.mark.parametrize(
    "bad",
    [
        dict(t_eval=np.array([1.0]), t=np.array([0.0, 1.0]), m=np.array([2.0]), mu=1.0),
        dict(t_eval=np.array([1.0]), t=np.array([np.nan]), m=np.array([2.0]), mu=1.0),
        dict(t_eval=np.array([1.0]), t=np.array([0.0]), m=np.array([2.0]), mu=-1.0),
    ],
)
def test_invalid_inputs_raise(bad: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        intensity(base=_base(), **bad)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        compensator(2027.0, 2026.0, np.array([0.0]), np.array([2.0]), _base(), 1.0)
