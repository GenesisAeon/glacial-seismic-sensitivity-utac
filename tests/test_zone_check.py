"""AP6c zone check: distance cut, relative reduced baseline, replicate (hand-derived values)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy import zone_check as Z
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values

MODELS = dict(load_baselines())
GL = MODELS["SE_Alaska_AK"]


def test_outside_zone_hand_values() -> None:
    # 1 degree of latitude = 111.19 km on the 6371-km sphere
    lat = np.array([60.0, 60.4, 61.0, 61.1])
    out = Z.outside_zone(lat, np.full(4, -139.0), 60.0, -139.0, 100.0)
    assert out.tolist() == [False, False, True, True]
    assert Z.outside_zone(np.array([60.0]), np.array([-139.0]), 60.0, -139.0, 0.0).tolist() == [
        True
    ]


def _cat(seed: int, n: int = 3000) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(2015.0, 2026.0, n))
    return t, np.round(rng.exponential(0.47, n) + 2.1, 1)


def test_reduced_baseline_equals_frozen_without_cut() -> None:
    t, m = _cat(1)
    red, ly = Z.reduced_baseline(t, m, np.ones(len(t), bool), GL)
    assert red.log_mu_ref == pytest.approx(GL.log_mu_ref, abs=1e-12)
    assert red.sigma_year == pytest.approx(GL.sigma_year, rel=1e-12)
    assert ly["ly_full"] == ly["ly_red"] and len(ly["ly_full"]) == 10


def test_reduced_baseline_thinning_lowers_mu_by_log_share() -> None:
    # without triggering mu_y = n_y / 1 yr, so dropping a random 20 % lowers log mu by ~log(0.8)
    import dataclasses

    quiet = dataclasses.replace(GL, K=1e-15)
    t, m = _cat(2, 20000)
    keep = np.random.default_rng(3).uniform(size=len(t)) >= 0.2
    red, _ = Z.reduced_baseline(t, m, keep, quiet)
    assert red.log_mu_ref - quiet.log_mu_ref == pytest.approx(np.log(0.8), abs=0.01)


def _ctx() -> dict[str, object]:
    return {"t_ms": 2025.93113, "cutoff": 2026.8, "spike_A": 15.0, "spike_q": 2.8,
            "real_t": list(np.linspace(2026.0, 2026.79, 200)), "real_m": [2.3] * 200,
            "real_in_zone": [True] * 150 + [False] * 50,
            "mag_values": [2.1, 2.3], "mag_counts": [3, 1]}  # fmt: skip


def test_zone_replicate_excess_mostly_in_zone() -> None:
    import dataclasses

    b = load_b_values()
    red = dataclasses.replace(GL, log_mu_ref=GL.log_mu_ref - 0.05)
    e0 = Z.run_zone_replicate(MODELS, red, b, _ctx(), Z.ZONE_SCENARIOS["e0"], 0, 4, 9, 2.0)
    e1 = Z.run_zone_replicate(MODELS, red, b, _ctx(), Z.ZONE_SCENARIOS["e150_r05_l05"], 0, 4, 9,
                              2.0)  # fmt: skip
    assert e0["pi_zone"] == pytest.approx(1 - np.exp(-0.05))
    assert e1["n_level_2029"] > 0
    # the excess raises the full statistic much more than the reduced one (95 % in the zone)
    assert e1["D_full_2029"] - e0["D_full_2029"] > 3 * (e1["D_red_2029"] - e0["D_red_2029"])


def test_separate_generator_zone_events_and_reproducible() -> None:
    import dataclasses

    b = load_b_values()
    red = dataclasses.replace(GL, log_mu_ref=GL.log_mu_ref - 0.05)
    sc = Z.ZONE_SCENARIOS["e0"]
    r1 = Z.run_zone_replicate(MODELS, red, b, _ctx(), sc, 0, 7, 9, 2.0, generator="separate")
    r2 = Z.run_zone_replicate(MODELS, red, b, _ctx(), sc, 0, 7, 9, 2.0, generator="separate")
    r1.pop("seconds"), r2.pop("seconds")
    assert r1 == r2 and np.isfinite(r1["D_red_2029"])
    with pytest.raises(ValueError, match="generator"):
        Z.run_zone_replicate(MODELS, red, b, _ctx(), sc, 0, 7, 9, 2.0, generator="x")


def test_fixed_mu_catalogue_rate_hand_value() -> None:
    # without triggering the yearly count is Poisson(exp(log_mu + sigma z)); z = 0 -> e^log_mu
    import dataclasses

    quiet = dataclasses.replace(GL, K=1e-15)
    t, _ = Z._fixed_mu_catalogue(list(range(20)), quiet, np.log(500.0),
                                 np.zeros(len(Z.YEARS_SIM)), 1.0, 1.0, 1.0)  # fmt: skip
    n_years = len(Z.YEARS_SIM)
    assert abs(len(t) / n_years - 500.0) < 3 * np.sqrt(500.0 / n_years)


SPEC = {"epicentre_lat": 60.35, "epicentre_lon": -139.36, "radius_km": 55.0,
        "log_mu_ref_reduced": GL.log_mu_ref, "sigma_year_reduced": GL.sigma_year,
        "confirmation": "p_reduced_below_alpha"}  # fmt: skip


def _cats_geo(extra_in_zone: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(8)
    n = 1500
    g = pd.DataFrame({"t": np.sort(rng.uniform(2026.0, 2030.0, n)),
                      "mag": np.round(rng.exponential(0.47, n) + 2.1, 1),
                      "latitude": rng.uniform(57.5, 59.0, n),  # > 150 km from the epicentre
                      "longitude": rng.uniform(-137.0, -134.0, n)})  # fmt: skip
    if extra_in_zone:
        x = pd.DataFrame({"t": rng.uniform(2027.0, 2030.0, extra_in_zone),
                          "mag": np.full(extra_in_zone, 2.2),
                          "latitude": np.full(extra_in_zone, 60.36),
                          "longitude": np.full(extra_in_zone, -139.30)})  # fmt: skip
        g = pd.concat([g, x]).sort_values("t", kind="stable").reset_index(drop=True)
    c = pd.DataFrame({"t": np.sort(rng.uniform(2026.0, 2030.0, 500)),
                      "mag": np.round(rng.exponential(0.46, 500) + 2.1, 1)})  # fmt: skip
    return g, c


def test_confirm_c2_without_zone_events_mirrors_c2() -> None:
    g, c = _cats_geo(0)
    r = Z.confirm_c2(g, c, MODELS, "2029-12-31", SPEC)
    assert r["reduced"]["D"] == pytest.approx(r["c2"]["D"], rel=1e-12)
    assert r["confirmed"] == r["c2"]["reject"]


def test_confirm_c2_zone_cluster_moves_c2_but_not_reduced() -> None:
    g0, c = _cats_geo(0)
    g1, _ = _cats_geo(3000)
    r0 = Z.confirm_c2(g0, c, MODELS, "2029-12-31", SPEC)
    r1 = Z.confirm_c2(g1, c, MODELS, "2029-12-31", SPEC)
    assert r1["c2"]["D"] > r0["c2"]["D"] + 0.5 and r1["c2"]["reject"]
    assert r1["reduced"]["D"] == pytest.approx(r0["reduced"]["D"], rel=1e-12)
    assert r1["confirmed"] == (r1["reduced"]["p_one"] < 0.01)


def test_confirm_c2_rejects_incomplete_or_unknown_spec() -> None:
    g, c = _cats_geo(0)
    with pytest.raises(ValueError, match="lacks"):
        Z.confirm_c2(g, c, MODELS, "2029-12-31", {"radius_km": 55.0})
    with pytest.raises(ValueError, match="confirmation rule"):
        Z.confirm_c2(g, c, MODELS, "2029-12-31", {**SPEC, "confirmation": "p<0.05"})
