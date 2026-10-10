"""M4: alternative rheologies must not modify v0.1.0 and must change tau as expected."""

from __future__ import annotations

import numpy as np
import pytest

from glacial_seismic_sensitivity_utac import lag_sensitivity as L
from glacial_seismic_sensitivity_utac import lagmodel, tipping


def test_v01_rheologies_untouched() -> None:
    assert lagmodel.RHEOLOGIES["SE_Alaska"].eta == 1.4e19
    assert lagmodel.RHEOLOGIES["SE_Alaska"].te_km == 60.0
    assert lagmodel.RHEOLOGIES["Iceland"].eta == 8e18


def test_sasgen_values() -> None:
    v = L.SENSITIVITY_RHEOLOGIES["Sasgen2026_preferred"]
    assert v["SE_Alaska"].eta == 3e18 and v["SE_Alaska"].te_km == 30.0
    assert v["Iceland"].eta == 1e18 and v["Iceland"].te_km == 30.0


def test_relaxation_time_scales_linearly_with_eta() -> None:
    a = lagmodel.relaxation_time_yr(3e18, 300.0, 60.0)
    b = lagmodel.relaxation_time_yr(1.4e19, 300.0, 60.0)
    assert b / a == pytest.approx(1.4e19 / 3e18)


def test_run_scenarios_default_equals_explicit_v01() -> None:
    reg = tipping.TipRegion(
        "X",
        "SE_Alaska",
        300.0,
        1.0,
        "test",
        100.0,
        0.2,
        0.05,
        trajectories=[tipping.Trajectory("continuation", 2025.0, 1.0)],
    )
    a, _ = tipping.run_scenarios([reg], kappas=(1.0,), sdot0s=(10.0,), shadow_fracs=(0.0,))
    b, _ = tipping.run_scenarios(
        [reg],
        kappas=(1.0,),
        sdot0s=(10.0,),
        shadow_fracs=(0.0,),
        rheologies=dict(lagmodel.RHEOLOGIES),
    )
    assert np.allclose(
        a.select_dtypes("number").to_numpy(), b.select_dtypes("number").to_numpy(), equal_nan=True
    )
    c, _ = tipping.run_scenarios(
        [reg],
        kappas=(1.0,),
        sdot0s=(10.0,),
        shadow_fracs=(0.0,),
        rheologies=L._rheo(L.SENSITIVITY_RHEOLOGIES["Sasgen2026_preferred"]),
    )
    assert c.tau_yr.iloc[0] != pytest.approx(a.tau_yr.iloc[0])
