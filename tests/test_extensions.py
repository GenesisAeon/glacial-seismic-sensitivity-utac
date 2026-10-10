from pathlib import Path

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import precursors, quiescence, tipping
from glacial_seismic_sensitivity_utac.fetch.extra import parse_csn

FIX = Path(__file__).parent / "fixtures"


def test_exp_multiplier_integral():
    m = tipping.exp_multiplier_for_integral(2.0)
    assert abs((m - 1) / np.log(m) - 2.0) < 1e-6
    assert tipping.exp_multiplier_for_integral(0.9) == 1.0


def test_trajectory_shapes():
    tr = tipping.Trajectory("x", 2060.0, 10.0)
    m = tr.multiplier(np.array([2025.0, 2060.0, 2080.0, 2100.0, 2200.0]))
    assert np.allclose(m, [1, 1, np.sqrt(10), 10, 10])
    lin = tipping.Trajectory("g", 2025.0, 1.0, accel_per_yr=0.02)
    assert abs(lin.multiplier(np.array([2075.0]))[0] - np.exp(1.0)) < 1e-9


def test_response_promoted_only_equals_rate_ratio():
    t = tipping.YEARS
    ld = np.where(t >= 1995, 1.0, 0.0)
    r = tipping.response(t, ld, tau=10.0, comp=0.5, kappa=1.0, sdot0=10.0, shadow_frac=0.0)
    assert np.allclose(r.aggregate_rate, r.promoted)
    assert np.allclose(r.modulation_ratio * r.promoted, 1.0)


def test_deceptive_quiet_then_turnaround():
    t = tipping.YEARS
    m = tipping.Trajectory("x", 2025.0, 20.0).multiplier(t)
    ld = np.where(t >= 1995, m, 0.0)
    r = tipping.response(t, ld, tau=5.0, comp=0.5, kappa=1.0, sdot0=10.0, shadow_frac=0.6)
    a = r.aggregate_rate.to_numpy()
    after = t >= 2025
    i_min = np.argmin(np.where(after, a, np.inf))
    assert a[i_min] < 0.98  # apparent quiet while loading accelerates ...
    assert a[t >= 2100][0] > 1.0  # ... until the promoted faults dominate
    assert 2025 < t[i_min] < 2100


def test_fit_rate_accel_recovers_quadratic():
    t = np.arange(2002, 2026, 1 / 12)
    y = 3 - 100 * (t - 2015) - 0.5 * 2.0 * (t - 2015) ** 2 + 5 * np.cos(2 * np.pi * t)
    f = precursors.fit_rate_accel(t, y + np.random.default_rng(1).normal(0, 1, len(t)))
    assert abs(f["rate"] + 100) < 0.5 and abs(f["accel"] + 2.0) < 0.1


def test_habermann_and_classify():
    assert quiescence.habermann_z(np.array([10, 12, 11, 9]), np.array([10, 12, 11, 9])) == 0
    assert quiescence.habermann_z(np.array([10, 12, 11, 9]), np.array([3, 4, 5, 4])) < -2
    assert quiescence.classify(False, False, True, True) == "no quiescence"
    assert quiescence.classify(True, True, True, True).startswith("catalogue artefact")
    assert quiescence.classify(True, False, True, None).startswith("candidate deceptive")
    assert quiescence.classify(True, False, False, False).startswith("consistent with genuine")


def test_etas_on_poisson_background():
    rng = np.random.default_rng(3)
    t = np.sort(rng.uniform(1990, 2026, 1800))
    m = 2.0 + rng.exponential(1 / np.log(10), len(t))
    par = quiescence.fit_etas(t, m, 2.0, 1995.0, 2014.5)
    lam = quiescence.etas_expected(par, t, m, 2.0, 2016.0, 2026.0)
    n = ((t >= 2016) & (t < 2026)).sum()
    assert abs(n - lam) / np.sqrt(lam) < 3


def test_parse_csn_fixture():
    d = parse_csn(FIX / "csn_sample.csv")
    assert len(d) == 2  # event without magnitude dropped
    assert d.mag.tolist() == [8.8, 3.1]
    assert pd.to_datetime(d.time.iloc[1]).year == 2019
    assert d.id.iloc[0] == "csn1"
