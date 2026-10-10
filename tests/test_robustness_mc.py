"""Catalogue-robustness helpers (v0.2, M1)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from glacial_seismic_sensitivity_utac import robustness_mc as R


def _incomplete(n: int, mu: float, sig: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    m = rng.exponential(1 / np.log(10), n)
    keep = rng.uniform(size=n) < stats.norm.cdf((m - mu) / sig)
    return np.asarray(np.round(m[keep] / 0.1) * 0.1)


def test_emr_recovers_detection_function() -> None:
    r = R.mc_emr(_incomplete(200_000, 1.5, 0.2, 0))
    assert r["mu"] == pytest.approx(1.5, abs=0.05)
    assert r["sigma"] == pytest.approx(0.2, abs=0.05)
    assert r["b"] == pytest.approx(1.0, abs=0.08)
    assert r["mc"] == pytest.approx(1.9, abs=0.15)


def test_mc_bootstrap_is_narrow_for_large_sample() -> None:
    m = _incomplete(100_000, 1.5, 0.2, 1)
    b = R.mc_bootstrap(m, "maxc", n_boot=50)
    assert b["sd"] <= 0.1
    assert b["q025"] <= b["mean"] <= b["q975"]


def test_gk_windows_match_published_table() -> None:
    L, T = R.gk_windows(np.array([5.0, 7.0]))
    # Gardner & Knopoff 1974 table: M5 ~ 40 km / 155 d, M7 ~ 70 km / 915 d
    assert L[0] == pytest.approx(40, rel=0.05) and T[0] == pytest.approx(155, rel=0.1)
    assert L[1] == pytest.approx(70, rel=0.05) and T[1] == pytest.approx(915, rel=0.05)


def test_gardner_knopoff_removes_aftershocks_only() -> None:
    t0 = pd.Timestamp("2000-01-01", tz="UTC")
    rows = [dict(time=t0, latitude=60.0, longitude=-140.0, mag=6.0)]
    for k in range(1, 21):  # aftershocks within 10 km / 20 days
        rows.append(dict(time=t0 + pd.Timedelta(days=k), latitude=60.05, longitude=-140.0, mag=3.0))
    rows.append(dict(time=t0 + pd.Timedelta(days=5), latitude=63.0, longitude=-140.0, mag=3.0))
    rows.append(dict(time=t0 + pd.Timedelta(days=2000), latitude=60.0, longitude=-140.0, mag=3.0))
    d = pd.DataFrame(rows)
    d["t_yr"] = (d.time - t0).dt.total_seconds() / (365.25 * 86400)
    out = R.gardner_knopoff(d)
    assert out.triggered.sum() == 20
    assert not out.loc[out.mag == 6.0, "triggered"].any()


def test_gardner_knopoff_foreshocks_and_precedence() -> None:
    # review K3: foreshocks inside the window of a later, larger event are removed; the larger
    # event takes precedence; for equal magnitudes the earlier event is kept
    t0 = pd.Timestamp("2000-01-01", tz="UTC")
    rows = [
        dict(time=t0, latitude=60.0, longitude=-140.0, mag=4.0),  # foreshock
        dict(time=t0 + pd.Timedelta(days=3), latitude=60.02, longitude=-140.0, mag=6.0),
        dict(time=t0 + pd.Timedelta(days=400), latitude=50.0, longitude=-140.0, mag=5.0),
        dict(time=t0 + pd.Timedelta(days=401), latitude=50.01, longitude=-140.0, mag=5.0),
    ]
    d = pd.DataFrame(rows)
    d["t_yr"] = (d.time - t0).dt.total_seconds() / (365.25 * 86400)
    out = R.gardner_knopoff(d).sort_values("time").reset_index(drop=True)
    assert out.triggered.tolist() == [True, False, False, True]
