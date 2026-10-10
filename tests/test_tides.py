"""Ephemeris validation against Meeus (Astronomical Algorithms, 2nd ed.) examples, tidal
period/amplitude sanity checks, Schuster test and b-value split (v0.2, M3)."""

from __future__ import annotations

import numpy as np
import pytest

from glacial_seismic_sensitivity_utac import tides as T


def test_moon_meeus_example_47a() -> None:
    # 1992-04-12 0h TD: lambda = 133.162655 deg incl. nutation (+0.004610), beta = -3.229126,
    # distance 368409.7 km
    lon, lat, r = T.moon_ecliptic(np.array([2448724.5]))
    assert lon[0] == pytest.approx(133.162655 - 0.004610, abs=0.02)
    assert lat[0] == pytest.approx(-3.229126, abs=0.02)
    assert r[0] == pytest.approx(368409.7, abs=60.0)


def test_sun_meeus_example_25a() -> None:
    # 1992-10-13 0h TD: true longitude 199.90988 deg, R = 0.99766 AU
    lon, r = T.sun_ecliptic(np.array([2448908.5]))
    assert lon[0] == pytest.approx(199.90988, abs=0.002)
    assert r[0] == pytest.approx(0.99766, abs=2e-5)


def test_decimal_year_to_jd() -> None:
    assert T.decyear_to_jd(np.array([2000.0]))[0] == pytest.approx(2451544.5)
    assert T.decyear_to_jd(np.array([2001.0]))[0] == pytest.approx(2451544.5 + 366)


def test_equatorial_strain_dominated_by_m2_and_ten_nanostrain_scale() -> None:
    jd = 2451545.0 + np.arange(0, 120, 1 / 96)
    e = T.areal_strain(jd, 0.0, 10.0)
    f = np.fft.rfftfreq(len(e), 1 / 96)
    P = np.abs(np.fft.rfft(e - e.mean()))
    assert 24 / f[np.argmax(P)] == pytest.approx(12.42, abs=0.1)
    assert 1e-8 < np.abs(e).max() < 1e-7


def test_phase_convention() -> None:
    jd = 2451545.0 + np.arange(0, 3, 1 / 1440)
    e = T.areal_strain(jd, 45.0, 0.0)
    k = int(np.argmax(e[:1500]))
    t_dec = 2000.0 + (jd[k] - 2451544.5) / 366.0
    ph, _ = T.tidal_phase(np.array([t_dec]), 45.0, 0.0, step_min=1.0)
    assert abs(ph[0]) < 3.0  # strain maximum -> phase ~0


def test_schuster_uniform_and_modulated() -> None:
    rng = np.random.default_rng(0)
    u = T.schuster(rng.uniform(-180, 180, 3000))
    assert u["p"] > 0.001
    s = T.schuster(T.sample_modulated_phases(3000, 0.2, rng))
    assert s["p"] < 1e-6
    assert s["a_hat"] == pytest.approx(0.2, abs=0.06)
    assert abs(s["mean_phase_deg"]) < 20


def test_schuster_mde_scales_like_inverse_sqrt_n() -> None:
    rng = np.random.default_rng(1)
    a1 = T.schuster_mde(400, n_sim=150, rng=rng)
    a2 = T.schuster_mde(1600, n_sim=150, rng=rng)
    assert a1 / a2 == pytest.approx(2.0, rel=0.25)


def test_b_split_detects_lower_b_in_tensile_half() -> None:
    rng = np.random.default_rng(2)
    n = 4000
    m1 = 1.95 + rng.exponential(1 / (0.8 * np.log(10)), n)
    m2 = 1.95 + rng.exponential(1 / (1.0 * np.log(10)), n)
    m = np.round(np.concatenate([m1, m2]) / 0.1) * 0.1
    ph = np.concatenate([np.zeros(n), np.full(n, 180.0)])
    r = T.b_split_test(m, ph, 2.0)
    assert r["b_tens"] < r["b_comp"]
    assert r["p_one"] < 0.01 and r["p_two"] < 0.01
    r0 = T.b_split_test(np.round(m2 / 0.1) * 0.1, rng.uniform(-180, 180, n), 2.0)
    assert r0["p_two"] > 0.001


def test_iers2010_love_numbers_only_rescale_the_strain() -> None:
    # IERS Conventions 2010 (TN 36, ch. 7) nominal h2 = 0.6078, l2 = 0.0847: positive factor, so
    # the Tanaka phases (and hence Schuster / b-value split) are identical to the frozen values.
    assert T.STRAIN_FACTOR_IERS2010 == pytest.approx(0.7074, abs=1e-4)
    assert T.STRAIN_FACTOR == pytest.approx(0.7236, abs=1e-4)
    ratio = T.STRAIN_FACTOR_IERS2010 / T.STRAIN_FACTOR
    assert 0.97 < ratio < 0.98


def test_tidal_phase_has_no_gaps_with_20h_window() -> None:
    # review K1 (Claude Code): +-14 h leaves 1-3 % of events without a phase; +-20 h none
    rng = np.random.default_rng(11)
    t = 1995 + 31 * rng.uniform(0, 1, 600)
    ph14, _ = T.tidal_phase(t, 64.4, -17.0)
    ph20, _ = T.tidal_phase(t, 64.4, -17.0, half_window_h=20.0)
    assert np.isfinite(ph20).all()
    assert np.mean(~np.isfinite(ph14)) < 0.06
    ok = np.isfinite(ph14)
    assert np.allclose(ph14[ok], ph20[ok], atol=1e-6)
