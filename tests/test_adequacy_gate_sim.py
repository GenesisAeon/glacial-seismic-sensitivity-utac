"""AP4: gate simulation building blocks (rules, scenarios, determinism)."""

from __future__ import annotations

import math

import numpy as np
import pytest

from glacial_seismic_sensitivity_utac.etas_adequacy import PRIMARY_PAIR, load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy import gate_sim as G
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import expected_cluster_moments

MODELS = load_baselines()
NAN = float("nan")


def _r(**p: float) -> dict[str, float]:
    r = dict.fromkeys(G.TEST_KEYS, 0.5)
    r.update(p)
    return r


def test_strict_rule_fires_on_any_of_five_tests_at_005() -> None:
    assert not G.gate_strict(_r())
    for k in G.TEST_KEYS:
        assert G.gate_strict(_r(**{k: 0.049}))
        assert not G.gate_strict(_r(**{k: 0.05}))
    assert not G.gate_strict(_r(T2_glac=NAN))  # a missing test does not fire


def test_lenient_rule_uses_only_control_t1_t2_at_0005() -> None:
    assert G.gate_lenient(_r(T1_ctrl=0.004)) and G.gate_lenient(_r(T2_ctrl=0.0049))
    assert not G.gate_lenient(_r(T1_ctrl=0.005, T2_ctrl=0.01))
    assert not G.gate_lenient(_r(T2_glac=0.0, T3_glac=0.0, T3_ctrl=0.0))


def test_wilson_interval() -> None:
    lo, hi = G.wilson(10, 100)
    assert lo == pytest.approx(0.0552, abs=1e-3) and hi == pytest.approx(0.1744, abs=1e-3)
    assert all(math.isnan(x) for x in G.wilson(0, 0))


@pytest.mark.parametrize("name", ["p12", "alpha_half"])
def test_shape_scenarios_keep_the_frozen_branching_ratio(name: str) -> None:
    for region in PRIMARY_PAIR:
        m = MODELS[region]
        d = G.SCENARIOS[name].data_baseline(m)
        assert d != m
        assert expected_cluster_moments(d)[0] == pytest.approx(expected_cluster_moments(m)[0])


def test_cluster_scenarios_raise_n_and_same_rate_keeps_the_count() -> None:
    for region in PRIMARY_PAIR:
        m = MODELS[region]
        n0 = expected_cluster_moments(m)[0]
        for name in ("cluster_plus", "cluster_plus_same_rate"):
            d = G.SCENARIOS[name].data_baseline(m)
            assert expected_cluster_moments(d)[0] == pytest.approx(0.95)
        d = G.SCENARIOS["cluster_plus_same_rate"].data_baseline(m)
        assert np.exp(d.log_mu_ref) / 0.05 == pytest.approx(np.exp(m.log_mu_ref) / (1 - n0))


def test_region_restricted_scenarios_leave_the_other_region_untouched() -> None:
    glac, ctrl = PRIMARY_PAIR
    assert G.SCENARIOS["swarm_ctrl"].regions == (ctrl,)
    assert G.SCENARIOS["signal_glac"].data_baseline(MODELS[ctrl]) == MODELS[ctrl]


def test_mc_jump_removes_window_events_below_the_new_threshold() -> None:
    m = MODELS[PRIMARY_PAIR[1]]
    cfg = G.SimConfig(n_t1=10, n_boot=9)
    d = G.generate_region(m, G.SCENARIOS["mc_jump"], cfg, [1, 2, 3, 4])
    assert d.win_m.min() >= m.mc_ref + 0.3 - 1e-9
    assert d.hist_m.min() < m.mc_ref + 0.3  # history is not affected


def test_replicate_is_deterministic_and_complete() -> None:
    cfg = G.SimConfig(n_t1=20, n_boot=9)
    a = G.run_replicate(MODELS, G.SCENARIOS["swarm_glac"], 5, 0, cfg, seed=7)
    b = G.run_replicate(MODELS, G.SCENARIOS["swarm_glac"], 5, 0, cfg, seed=7)
    a.pop("seconds"), b.pop("seconds")
    assert a == b
    assert set(G.TEST_KEYS) <= set(a)
    assert all(0.0 <= float(a[k]) <= 1.0 for k in G.TEST_KEYS)


def test_lenient_t3_rule_adds_only_the_control_t3() -> None:
    assert G.gate_lenient_t3(_r(T3_ctrl=0.0049))
    assert not G.gate_lenient_t3(_r(T3_ctrl=0.005, T3_glac=0.0))
    assert G.gate_lenient_t3(_r(T1_ctrl=0.001)) and G.gate_lenient_t3(_r(T2_ctrl=0.0025))


def test_config_uses_the_region_specific_b() -> None:
    cfg = G.SimConfig(b_glac=0.91, b_ctrl=0.95)
    assert cfg.b_for(PRIMARY_PAIR[0]) == 0.91 and cfg.b_for(PRIMARY_PAIR[1]) == 0.95
    assert G.SimConfig().b_for(PRIMARY_PAIR[0]) == 1.0  # AP4 default unchanged


def test_binned_target_n_is_met_with_the_binned_analytics() -> None:
    m = MODELS[PRIMARY_PAIR[1]]
    d = G.SCENARIOS["cluster_plus"].data_baseline(m, 0.945, 0.1)
    assert expected_cluster_moments(d, 0.945, 8.0, 0.1)[0] == pytest.approx(0.95)
