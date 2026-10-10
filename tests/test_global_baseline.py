"""Exploratory global/regional baseline (scripts/global_baseline.py): statistics helpers and the
archived snapshot reproduce the numbers quoted in docs/BASELINE_GLOBAL.md."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "global_baseline", ROOT / "scripts" / "global_baseline.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GB = _load()


def test_poisson_trend_recovers_known_rate_change() -> None:
    years = np.arange(1990, 2027)
    expo = np.ones(len(years))
    rate = 100 * 1.01 ** (years - 2000)  # +1 %/yr, noise-free expected counts
    r = GB.poisson_trend(years, rate, expo)
    assert r["trend_pct_per_yr"] == pytest.approx(1.0, abs=1e-6)
    assert r["ci_low"] < 1.0 < r["ci_high"]


def test_rate_ratio_exact_interval() -> None:
    r, lo, hi, p = GB.rate_ratio(56, 60)
    assert r == pytest.approx(56 / 60)
    assert lo < r < hi
    assert p > 0.5
    assert np.isnan(GB.rate_ratio(0, 0)[0])


def test_gardner_knopoff_flags_aftershock_not_distant_event() -> None:
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2020-01-01", "2020-01-05", "2020-01-06"]),
            "latitude": [0.0, 0.1, 40.0],
            "longitude": [0.0, 0.1, 40.0],
            "mag": [7.0, 5.0, 5.0],
        }
    )
    d = GB.gardner_knopoff(df)
    assert d.dependent.tolist() == [False, True, False]


def test_committed_tables_reproduce_quoted_numbers() -> None:
    g = pd.read_csv(ROOT / "results" / "global" / "global_counts_per_year.csv")
    s = g[g.year >= 1990]
    m6 = GB.poisson_trend(s.year, s.M6_all, s.exposure_years)
    m6d = GB.poisson_trend(s.year, s.M6_declustered, s.exposure_years)
    m7 = GB.poisson_trend(s.year, s.M7_all, s.exposure_years)
    assert round(m6["trend_pct_per_yr"], 2) == -0.46
    assert round(m6d["trend_pct_per_yr"], 2) == -0.31
    assert round(m6d["ci_high"], 2) == 0.0
    assert round(m6d["ci_high_quasi"], 2) == 0.03
    assert round(m7["trend_pct_per_yr"], 2) == -0.21
    rr = pd.read_csv(ROOT / "results" / "global" / "ice_vs_control_rate_ratios.csv")
    pooled = rr[rr.region.str.startswith("POOLED") & (rr.series == "M>=5 declustered")]
    vals = dict(zip(pooled.group, pooled.ratio.round(2), strict=True))
    assert vals == {"glaciated": 0.95, "control (non-glaciated)": 1.05}


def test_snapshot_analysis_matches_committed_results(tmp_path: Path) -> None:
    res = GB.analyse(GB.SNAP, tmp_path)
    for name in ("global_counts_per_year", "ice_vs_control_rate_ratios"):
        committed = pd.read_csv(ROOT / "results" / "global" / f"{name}.csv")
        fresh = pd.read_csv(tmp_path / f"{name}.csv")
        pd.testing.assert_frame_equal(committed, fresh)
    assert len(res["gvp_eruption_starts_per_year"]) == 2026 - 1900 + 1


def test_snapshot_checksums() -> None:
    import hashlib

    snap = ROOT / "results" / "global" / "snapshots"
    lines = (snap / "SHA256SUMS").read_text().split("\n")
    sums = dict(reversed(line.split()) for line in lines if line.strip())
    assert len(sums) == 15
    for name, digest in sums.items():
        assert hashlib.sha256((snap / name).read_bytes()).hexdigest() == digest
