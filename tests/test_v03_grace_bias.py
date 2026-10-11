"""v0.3 exploratory GRACE under-estimation sensitivity (Sasgen et al. 2026)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import lag_sensitivity as LS
from glacial_seismic_sensitivity_utac import v03_grace_bias as G

# conftest points C.OUT to a temp dir; these tests read the committed repo results.
RESULTS = Path(__file__).resolve().parents[1] / "results"


@pytest.fixture(autouse=True)
def _repo_results(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(C, "OUT", RESULTS)


@pytest.fixture()
def acc() -> pd.DataFrame:
    return pd.read_csv(RESULTS / "precursors_grace_acceleration.csv")


def test_factors_bracket_central() -> None:
    for c, lo, hi in G.FACTORS.values():
        assert lo < c < hi
    assert G.factor("Iceland", "none_v02") == 1.0
    assert G.factor("Iceland", "central") == pytest.approx(1.32)
    assert G.factor("SE_Alaska", "high") == pytest.approx(1.103)


def test_scaled_acc_only_touches_two_boxes(acc: pd.DataFrame) -> None:
    s = G.scaled_acc(acc, "central")
    for _, r in s.iterrows():
        o = acc.loc[acc.box == r.box].iloc[0]
        f = {"SE_Alaska_box": 1.09, "Vatnajokull": 1.32}.get(r.box, 1.0)
        assert r.mass_rate == pytest.approx(o.mass_rate * f)
        assert r.unloading_kPa_per_yr == pytest.approx(o.unloading_kPa_per_yr * f)
        assert r.mass_accel == pytest.approx(o.mass_accel)  # constant-trend correction
    assert G.scaled_acc(acc, "none_v02").equals(acc)


def test_regions_scale_grace_only(acc: pd.DataFrame) -> None:
    base = {r.key: r for r in LS.build_regions()}
    same = {r.key: r for r in LS.build_regions(acc)}
    hi = {r.key: r for r in LS.build_regions(G.scaled_acc(acc, "high"))}
    assert base.keys() == same.keys() == hi.keys()
    for k in base:
        assert same[k].ldot_now_kpa_yr == base[k].ldot_now_kpa_yr
        f = 1.0
        if k == "SE_Alaska_grace":
            f = 1.103
        elif k == "Iceland_grace":
            f = 1.43
        assert hi[k].ldot_now_kpa_yr == pytest.approx(base[k].ldot_now_kpa_yr * f)


def test_committed_results_reproduce_v02_and_are_labelled() -> None:
    path = RESULTS / "v03" / "grace_bias_earliest.csv"
    e = pd.read_csv(path)
    assert e.exploratory.all()
    m4 = pd.read_csv(RESULTS / "v02" / "m4_lag_earliest.csv")
    x = e[e.grace_factor == "none_v02"].merge(m4, on=["variant", "region"], suffixes=("", "_m4"))
    assert len(x) == len(m4)
    for col in ("earliest_any", "detect_increase_year", "tau_yr"):
        assert np.allclose(x[col], x[f"{col}_m4"], equal_nan=True)
    surf = e[e.region.str.endswith("_surface")]
    assert np.allclose(surf.shift_earliest_any.fillna(0.0), 0.0)
