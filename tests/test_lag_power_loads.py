from __future__ import annotations

import h5py
import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import lagmodel as L
from glacial_seismic_sensitivity_utac import loads, power


def test_relaxation_time_reference_values():
    # Fennoscandia (Turcotte & Schubert / Sandwell lecture): lambda 3000 km, 1.1e21 Pa s -> ~4400 yr
    assert 4300 < L.relaxation_time_yr(1.1e21, 3000) < 4600
    # Amundsen Sea (Barletta et al. 2018: 4e18 Pa s) at 500 km: ~a century (half-space)
    assert 90 < L.relaxation_time_yr(4e18, 500) < 105
    assert L.compensation(5000, 50) > 0.99
    assert L.compensation(50, 50) < 0.01
    assert abs(L.maxwell_time_yr(6.5e10 * 3.15576e7) - 1.0) < 1e-6


def test_rsm_rate_steady_state_and_limits():
    t = np.linspace(0, 5, 5001)
    r = L.rsm_rate(t, 30.0 * t, 1.5, 30.0)
    assert np.allclose(r, 1.0, atol=1e-6)
    # slow-period limit: modulation ~ 2 pi dS / Sdot
    mod = L.seasonal_modulation(1.0, 1.0, 30.0)
    assert abs(mod - 2 * np.pi / 30) / (2 * np.pi / 30) < 0.15
    # extra background stressing reduces modulation
    assert L.seasonal_modulation(1.0, 1.0, 30.0, 10.0) < mod


def test_detection_and_scenarios():
    assert L.mde_slope(100, 2026, 2036) > L.mde_slope(1000, 2026, 2036)
    y = L.detection_year(500, 1.0, 2000, 20, 50.0, 1.0, 1.0, 10.0)
    assert np.isfinite(y)
    g = L.scenario_grid(
        {"SE_Alaska": dict(n_per_yr=100, phi=1.2, ldot_kpa_yr=1.0)}, kappas=(1.0,), sdot0s=(10.0,)
    )
    assert set(g.load_rate_scenario) == {"grace_box_mean", "glacier_surface"}
    assert (g.rate_ratio_equilibrium >= 1).all()
    assert len(L.relaxation_table()) > 10


def test_power_mde():
    a = power.mde_difference(100, 0.03, 0.01)
    b = power.mde_difference(1000, 0.03, 0.01)
    assert a > b > 0
    pt = power.power_table(
        pd.DataFrame([dict(region="X", rate_per_yr=200, b_ref=0.1, b_ref_se=0.02, phi=1.0)])
    )
    assert len(pt) == 2 and (pt.mde_b_diff > 0).all()
    p = power.simulate_power(
        300, 0.1, power.mde_difference(900, 0.02, 0.05), 3, 0.05, 0.02, n_sim=150
    )
    assert 0.6 < p < 0.95


def test_load_conversion_and_anomaly():
    assert abs(loads.KPA_PER_CMWE - 0.0981) < 1e-3
    s = pd.Series(np.arange(48, dtype=float) + 3 * np.cos(2 * np.pi * np.arange(48) / 12))
    a = loads.seasonal_anomaly(s)
    assert abs(a.iloc[12:36].mean()) < 0.3
    hf = loads.harmonic_fit(
        2010 + np.arange(48) / 12,
        -0.5 * np.arange(48) / 12 + np.cos(2 * np.pi * np.arange(48) / 12),
    )
    assert abs(hf["trend_per_yr"] + 0.5) < 1e-6 and abs(hf["annual_amp"] - 1) < 1e-6


def test_regional_grace_from_tiny_h5(tmp_path):
    fn = tmp_path / "gsfc_test.h5"
    n, t = 4, 24
    with h5py.File(fn, "w") as f:
        f["mascon/lat_center"] = np.array([[59.0, 60.0, 10.0, 59.5]])
        f["mascon/lon_center"] = np.array([[220.0, 221.0, 0.0, 222.0]])  # 0-360 convention
        f["mascon/area_km2"] = np.ones((1, n)) * 10000
        f["mascon/location"] = np.array([[1, 1, 1, 90]])  # last one ocean
        f["solution/cmwe"] = np.tile(np.arange(t, dtype=float), (n, 1))
        tt = 2003 + (np.arange(t) + 0.5) / 12
        f["time/yyyy_doy_yrplot_middle"] = np.vstack([np.zeros(t), np.zeros(t), tt])
    g = loads.regional_grace(str(fn))
    assert "SE_Alaska_AK_kPa" in g
    assert int(g["SE_Alaska_AK_n_mascons"].iloc[0]) == 2
    assert abs(g["SE_Alaska_AK_kPa"].iloc[10] - 10 * 0.0981) < 1e-3
    lo = loads.monthly_load("SE_Alaska_AK", g)
    assert len(lo) == t
    assert C.REGIONS["SE_Alaska_AK"].group == "mountain"
