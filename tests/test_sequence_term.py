"""AP6 sequence term: MLE with a known Omori rate, term fit, C2 variants (hand-derived values)."""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest

from glacial_seismic_sensitivity_utac.confirmatory_v02 import evaluate_pair
from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy import sequence_term as Q
from glacial_seismic_sensitivity_utac.etas_adequacy.sequence_tail import omori_times
from glacial_seismic_sensitivity_utac.etas_nonstat import mu_window_mle

MODELS = load_baselines()
GL = MODELS["SE_Alaska_AK"]


def _quiet(base: Q.Baseline) -> Q.Baseline:
    """Same baseline without triggering (K tiny): a pure Poisson process."""
    return dataclasses.replace(base, K=1e-15)


def _fit(log_A: float, q: float, t_ms: float = -0.1) -> Q.TermFit:
    return Q.TermFit(t_ms, log_A, q, ((0.01, 0.0), (0.0, 0.0025)), 0.0, 100, (0.0, 1.0))


def test_no_term_reproduces_mu_window_mle() -> None:
    rng = np.random.default_rng(0)
    t = np.sort(rng.uniform(2026.0, 2030.0, 900))
    m = np.round(rng.exponential(0.45, 900) + 2.1, 1)
    a = Q.mu_mle_with_term(t, m, GL, 2027.0, 2030.0, None)
    b = mu_window_mle(t, m, GL.mc_ref, GL.trig(), 2027.0, 2030.0)
    assert a == pytest.approx(b, rel=1e-12)


def test_constant_term_hand_value() -> None:
    # q = 0 makes S constant = A; without triggering mu_hat = n / T - A exactly
    t = np.linspace(0.05, 9.95, 50)
    r = Q.mu_mle_with_term(t, np.full(50, 2.5), _quiet(GL), 0.0, 10.0, _fit(np.log(2.0), 0.0))
    assert r["mu"] == pytest.approx(50 / 10 - 2.0, rel=1e-9)


def test_term_lowers_mu_and_zero_term_does_nothing() -> None:
    rng = np.random.default_rng(1)
    t = np.sort(rng.uniform(0.0, 1.0, 400))
    m = np.full(400, 2.3)
    base = Q.mu_mle_with_term(t, m, GL, 0.0, 1.0, None)["mu"]
    tiny = Q.mu_mle_with_term(t, m, GL, 0.0, 1.0, _fit(-30.0, 1.1))["mu"]
    big = Q.mu_mle_with_term(t, m, GL, 0.0, 1.0, _fit(np.log(100.0), 1.1))["mu"]
    assert tiny == pytest.approx(base, rel=1e-9) and big < base


def test_fit_recovers_parameters() -> None:
    # pure Poisson: mu = 60 / yr plus A x^-q with A = 150, q = 1.2, t_ms = -0.07, window [0, 0.8)
    rng = np.random.default_rng(5)
    base = _quiet(GL)
    t_ms, A, q = -0.07, 150.0, 1.2
    lo, hi = 0.0 - t_ms, 0.8 - t_ms
    n_tail = rng.poisson(A * ((lo ** (1 - q) - hi ** (1 - q)) / (q - 1)))
    tt = t_ms + omori_times(rng, n_tail, lo, hi, q)
    tb = rng.uniform(0.0, 0.8, rng.poisson(60 * 0.8))
    t = np.sort(np.concatenate([tt, tb]))
    f = Q.fit_sequence_term(t, np.full(len(t), 2.2), base, t_ms, 0.0, 0.8)
    se_q, se_a = np.sqrt(f.cov[1][1]), np.sqrt(f.cov[0][0])
    assert abs(f.q - q) < 4 * se_q and abs(f.log_A - np.log(A)) < 4 * se_a
    assert np.all(np.linalg.eigvalsh(np.array(f.cov)) > 0)


@pytest.mark.parametrize("args", [(0.0, 0.0, 1.0), (0.5, 0.0, 1.0), (-0.1, 1.0, 0.5)])
def test_fit_rejects_bad_window(args: tuple[float, float, float]) -> None:
    t = np.linspace(0, 1, 100)
    with pytest.raises(ValueError):
        Q.fit_sequence_term(t, np.full(100, 2.2), GL, *args)


def _cats() -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(3)
    tg = np.sort(rng.uniform(2026.0, 2030.0, 1200))
    tc = np.sort(rng.uniform(2026.0, 2030.0, 400))
    mg = np.round(rng.exponential(0.47, 1200) + 2.1, 1)
    mc = np.round(rng.exponential(0.46, 400) + 2.1, 1)
    return pd.DataFrame({"t": tg, "mag": mg}), pd.DataFrame({"t": tc, "mag": mc})


def test_evaluate_without_term_equals_preregistered_c2() -> None:
    cg, cc = _cats()
    base_json = {"regions": {r: dataclasses.asdict(MODELS[r]) for r in MODELS}}
    a = evaluate_pair(cg, cc, base_json, "2029-12-31")
    b = Q.evaluate_pair_with_term(cg, cc, dict(MODELS), "2029-12-31", None)
    assert b["D"] == pytest.approx(a["D"], rel=1e-12)
    assert b["se"] == pytest.approx(a["se"], rel=1e-12)
    assert b["reject"] == a["reject"]


def test_variant_b_widens_se_and_term_lowers_d() -> None:
    cg, cc = _cats()
    f = _fit(np.log(80.0), 1.1, t_ms=2025.93)
    n = Q.evaluate_pair_with_term(cg, cc, dict(MODELS), "2029-12-31", None)
    a = Q.evaluate_pair_with_term(cg, cc, dict(MODELS), "2029-12-31", f, "A")
    b = Q.evaluate_pair_with_term(cg, cc, dict(MODELS), "2029-12-31", f, "B")
    assert a["D"] < n["D"] and b["D"] == a["D"]
    assert b["se"] > a["se"] and b["glacier"]["var_term"] > 0
    with pytest.raises(ValueError):
        Q.evaluate_pair_with_term(cg, cc, dict(MODELS), "2029-12-31", f, "C")


def _ctx() -> dict[str, object]:
    return {"t_ms": 2025.93113, "log_A": float(np.log(400.0)), "q": 1.1, "cutoff": 2026.8,
            "dec_t": [2025.95, 2025.97], "dec_m": [3.0, 2.5],
            "mag_values": [2.1, 2.3], "mag_counts": [3, 1]}  # fmt: skip


def test_term_replicate_runs_and_is_reproducible() -> None:
    from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values

    b = load_b_values()
    s = Q.TERM_SCENARIOS["dq0"]
    r1 = Q.run_term_replicate(dict(MODELS), b, _ctx(), s, 2, 0, 11, warmup_years=2.0)
    r2 = Q.run_term_replicate(dict(MODELS), b, _ctx(), s, 2, 0, 11, warmup_years=2.0)
    r1.pop("seconds"), r2.pop("seconds")
    assert r1 == r2 and r1["n_injected_2029"] > 0 and "q_fit" in r1
    for k in ("none", "A", "B"):
        assert np.isfinite(r1[f"D_{k}_2029"]) and np.isfinite(r1[f"D_{k}_2036"])
    # the term removes most of the tail bias that the preregistered C2 shows
    assert r1["D_A_2029"] < r1["D_none_2029"]
    n = Q.run_term_replicate(dict(MODELS), b, _ctx(), Q.TERM_SCENARIOS["signal_notail"], 6, 0,
                             11, warmup_years=2.0)  # fmt: skip
    assert n["n_injected_2029"] == 0
