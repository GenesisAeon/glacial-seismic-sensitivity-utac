from __future__ import annotations

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac.catalog import b_value, haversine_km, mc_maxc, prepare
from glacial_seismic_sensitivity_utac.decluster import decluster, gmm_threshold


def test_prepare_filters_box_depth_and_bins(make_catalog):
    df = make_catalog(n_years=3, rate=60)
    df.loc[0, "latitude"] = 10.0  # outside SE_Alaska_AK box
    df.loc[1, "depth"] = 100.0  # deeper than maxdepth 40
    out = prepare(df, C.REGIONS["SE_Alaska_AK"])
    assert len(out) == len(df) - 2
    assert np.allclose(out.mag * 10, np.round(out.mag * 10))
    assert {"t_yr", "year", "month", "is_mb"} <= set(out.columns)


def test_b_value_recovers_gutenberg_richter():
    rng = np.random.default_rng(0)
    m = np.round((1.0 + rng.exponential(1 / np.log(10), 20000)) / 0.1) * 0.1
    b, sb, n = b_value(m, 1.5)
    assert abs(b - 1.0) < 0.05
    assert sb > 0 and n > 1000
    assert 0.9 <= mc_maxc(m) <= 1.4


def test_haversine():
    assert abs(float(haversine_km(0, 0, 0, 1)) - 111.19) < 0.1


def test_decluster_flags_aftershocks():
    rng = np.random.default_rng(3)
    bg = pd.DataFrame(
        dict(
            t_yr=np.sort(rng.uniform(0, 20, 400)),
            latitude=rng.uniform(58, 62, 400),
            longitude=rng.uniform(-145, -135, 400),
            mag=2.0 + rng.exponential(0.43, 400),
        )
    )
    after = []
    for _k in range(10):
        t0, la, lo = rng.uniform(0, 20), rng.uniform(58, 62), rng.uniform(-145, -135)
        after.append(dict(t_yr=t0, latitude=la, longitude=lo, mag=5.0))
        for _ in range(40):
            after.append(
                dict(
                    t_yr=t0 + rng.exponential(0.01),
                    latitude=la + rng.normal(0, 0.02),
                    longitude=lo + rng.normal(0, 0.02),
                    mag=2.0 + rng.exponential(0.43),
                )
            )
    df = pd.concat([bg, pd.DataFrame(after)]).sort_values("t_yr").reset_index(drop=True)
    dc, thr = decluster(df)
    assert np.isfinite(thr)
    assert dc.triggered.mean() > 0.3  # ~400 of 810 events are aftershocks
    assert dc.triggered.mean() < 0.8
    assert len(dc) == len(df)


def test_gmm_threshold_nan_for_tiny_input():
    assert np.isnan(gmm_threshold(np.array([1.0, 2.0])))
