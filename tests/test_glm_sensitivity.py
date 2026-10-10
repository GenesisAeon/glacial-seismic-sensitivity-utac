from __future__ import annotations

import numpy as np

from glacial_seismic_sensitivity_utac import sensitivity
from glacial_seismic_sensitivity_utac.catalog import prepare
from glacial_seismic_sensitivity_utac.glm import fit_poisson_fe


def test_glm_recovers_coefficient_with_year_fixed_effects():
    rng = np.random.default_rng(5)
    years = np.repeat(np.arange(30), 12)
    m = np.tile(np.arange(1, 13), 30)
    x = np.cos(2 * np.pi * (m - 0.5) / 12)
    level = rng.normal(3, 0.8, 30)[years]  # arbitrary year-to-year rate changes
    y = rng.poisson(np.exp(level + 0.2 * x))
    r = fit_poisson_fe(y, years, x[:, None])
    assert abs(r.coef[0] - 0.2) < 3 * r.se[0]
    assert r.se[0] < 0.05


def test_harmonic_growth_detects_growth(make_catalog):
    df = prepare(make_catalog(rate=400, b0=0.15, b1=0.15, seed=2))
    res = sensitivity.harmonic_growth(df, n_perm=60)
    assert res["b1_per_decade"] > 0.05
    assert res["b1_p_wald_one"] < 0.01
    assert res["b1_p_perm_one"] < 0.05
    assert 9.5 < res["peak_month"] < 12.5


def test_harmonic_growth_null_and_step_robust(make_catalog):
    # a doubling of the overall rate in 2008 (e.g. network change) must not create b1
    df = prepare(make_catalog(rate=300, b0=0.15, b1=0.0, seed=4, step_year=2008))
    res = sensitivity.harmonic_growth(df, n_perm=0)
    assert abs(res["b1_per_decade"]) < 3 * res["b1_se"]
    assert abs(res["b0"] - 0.15) < 3 * res["b0_se"]


def test_per_year_and_meta(make_catalog):
    df = prepare(make_catalog(n_years=5, rate=600, b0=0.3, seed=7))
    py = sensitivity.per_year_modulation(df, (11 - 1) / 12, (1990, 1994))
    assert len(py) == 5 and (py.b > 0).all()
    meta = sensitivity.meta_group(py.rename(columns={"b": "c"}), "c", "se")
    assert meta["n"] == 5 and meta["pooled"] > 0


def test_load_growth_recovers_sensitivity(make_catalog):
    import pandas as pd

    rng = np.random.default_rng(11)
    months = pd.date_range("2002-01-01", "2025-12-01", freq="MS")
    u = 2.0 * np.cos(2 * np.pi * (months.month - 10.5) / 12) + rng.normal(0, 0.3, len(months))
    load = pd.DataFrame({"month": months, "unload_kPa": u})
    lag_u = pd.Series(u, index=months).shift(3, freq="MS")
    rows = []
    for t, uu in lag_u.items():
        if t > months[-1]:
            continue
        k = rng.poisson(30 * np.exp(0.05 * uu))
        for d in rng.uniform(0, 27, k):
            rows.append(
                dict(
                    time=pd.Timestamp(t, tz="UTC") + pd.Timedelta(days=float(d)),
                    latitude=59,
                    longitude=-138,
                    depth=5,
                    mag=2.5,
                    magType="ml",
                    id=str(len(rows)),
                    etype="earthquake",
                )
            )
    df = prepare(pd.DataFrame(rows))
    r = sensitivity.load_growth(df, load, lag=3, n_perm=0)
    assert abs(r["g0_per_kPa"] - 0.05) < 3 * r["g0_se"]
    ls = sensitivity.lag_scan(df, load, lags=(0, 3, 6))
    assert ls.loc[ls.z.idxmax(), "lag_months"] == 3
