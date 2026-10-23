"""AP5 sequence tail: Omori integral, inverse transform, injection, replicate (hand values)."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import integrate

from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy import sequence_tail as S
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values


@pytest.mark.parametrize("p", [0.8, 1.0, 1.1, 1.3, 2.0])
def test_omori_integral_matches_quadrature(p: float) -> None:
    ref, _ = integrate.quad(lambda x: x**-p, 0.07, 11.0)
    assert S.omori_integral(0.07, 11.0, p) == pytest.approx(ref, rel=1e-10)


def test_omori_integral_hand_values() -> None:
    assert S.omori_integral(1.0, math.e, 1.0) == pytest.approx(1.0)  # ln e
    assert S.omori_integral(1.0, 2.0, 2.0) == pytest.approx(0.5)  # 1 - 1/2


@pytest.mark.parametrize("lo,hi", [(0.0, 1.0), (-1.0, 1.0), (2.0, 1.0), (1.0, 1.0)])
def test_omori_integral_rejects_bad_bounds(lo: float, hi: float) -> None:
    with pytest.raises(ValueError):
        S.omori_integral(lo, hi, 1.1)


def test_omori_times_medians() -> None:
    rng = np.random.default_rng(1)
    t1 = S.omori_times(rng, 200_000, 2.0, 50.0, 1.0)
    assert np.median(t1) == pytest.approx(math.sqrt(2.0 * 50.0), rel=0.01)  # geometric mean
    t2 = S.omori_times(rng, 200_000, 2.0, 50.0, 2.0)
    assert np.median(t2) == pytest.approx(2.0 / (1.0 / 2.0 + 1.0 / 50.0), rel=0.01)  # harmonic
    assert t1.min() >= 2.0 and t1.max() <= 50.0


def test_inject_tail_count_and_support() -> None:
    vals, wts = np.array([2.1, 2.5, 3.0]), np.array([5.0, 3.0, 2.0])
    counts = []
    for k in range(400):
        t, m = S.inject_tail(np.random.default_rng(k), 100.0, 1.0, 0.0, 1.0, math.e, vals, wts)
        counts.append(len(t))
        assert np.all((t >= 1.0) & (t < math.e)) and np.all(np.diff(t) >= 0)
        assert set(np.unique(m)) <= set(vals)
    # E[N] = 100 * ln(e / 1) = 100 (hand); 3 standard errors of the mean of 400 Poisson(100)
    assert abs(np.mean(counts) - 100.0) < 3 * math.sqrt(100.0 / 400)


def test_inject_tail_memory_guard() -> None:
    with pytest.raises(RuntimeError, match="MAX_INJECTED"):
        S.inject_tail(
            np.random.default_rng(0), 1e9, 1.0, 0.0, 1.0, 2.0, np.array([2.1]), np.array([1.0])
        )


def _calib() -> dict[str, object]:
    return {
        "t_mainshock": 2025.93113,
        "amp_per_yr": {"1.1": 300.0},
        "mag_values": [2.1, 2.3],
        "mag_counts": [3, 1],
    }


def test_replicate_none_has_no_injection_and_is_reproducible() -> None:
    models, b = load_baselines(), load_b_values()
    r1 = S.run_replicate(models, b, _calib(), S.SCENARIOS["none"], 0, 3, 7, warmup_years=2.0)
    r2 = S.run_replicate(models, b, _calib(), S.SCENARIOS["none"], 0, 3, 7, warmup_years=2.0)
    assert r1["n_injected_2026_2036"] == 0 and r1["n_injected_2029"] == 0
    r1.pop("seconds"), r2.pop("seconds")
    assert r1 == r2
    assert np.isfinite(r1["D_2029"]) and np.isfinite(r1["D_2036"])


def test_replicate_tail_raises_glacier_count_only() -> None:
    models, b = load_baselines(), load_b_values()
    s = S.SCENARIOS["p11"]
    r0 = S.run_replicate(models, b, _calib(), S.SCENARIOS["none"], 2, 5, 7, warmup_years=2.0)
    r1 = S.run_replicate(models, b, _calib(), s, 2, 5, 7, warmup_years=2.0)
    # same seeds for the frozen part: control identical, glacier gains exactly the injected events
    assert r1["n_ctrl_2029"] == r0["n_ctrl_2029"] and r1["D_2029"] != r0["D_2029"]
    assert r1["n_glac_2029"] == r0["n_glac_2029"] + r1["n_injected_2029"]
    assert r1["n_injected_2029"] > 0
