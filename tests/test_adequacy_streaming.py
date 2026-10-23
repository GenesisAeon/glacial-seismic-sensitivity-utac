"""Streaming simulation (iter_window / simulate_counts): identical results, flat memory."""

from __future__ import annotations

import tracemalloc

import numpy as np
import pytest

from glacial_seismic_sensitivity_utac.etas_adequacy import gate_sim as G
from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy import stats as S
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import (
    iter_window,
    simulate_counts,
    simulate_window,
)
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values
from glacial_seismic_sensitivity_utac.etas_adequacy.stats import ogata_ks_bootstrap

NO = np.array([])


def _ctrl() -> G.Baseline:
    return load_baselines()[G.CONTROL]


def test_iter_window_matches_simulate_window() -> None:
    base = _ctrl()
    full = simulate_window(base, NO, NO, 0.0, 2.0, 5, mu_mode="mixture", seed=3)
    for k, (t, m, mu) in enumerate(iter_window(base, NO, NO, 0.0, 2.0, 5, mu_mode="mixture",
                                               seed=3)):  # fmt: skip
        assert np.array_equal(t, full.times[k]) and np.array_equal(m, full.mags[k])
        assert mu == full.mu[k]
    counts = simulate_counts(base, NO, NO, 0.0, 2.0, 5, mu_mode="mixture", seed=3)
    assert np.array_equal(counts, full.counts)


def test_iter_window_checks_arguments_at_creation() -> None:
    with pytest.raises(ValueError, match="mu_mode"):
        iter_window(_ctrl(), NO, NO, 0.0, 1.0, 3, mu_mode="bogus")  # no next() needed
    with pytest.raises(ValueError, match="history"):
        iter_window(_ctrl(), np.array([0.5]), np.array([3.0]), 0.0, 1.0, 1)


def test_gate_replicate_pinned_values() -> None:
    """Values of the pre-streaming code (4c25596), recomputed bit-identically after the change."""
    b = load_b_values()
    cfg = G.SimConfig(n_t1=300, n_boot=99, warmup_years=2.0, b_glac=b[G.GLACIER],
                      b_ctrl=b[G.CONTROL], n_dm=0.1)  # fmt: skip
    r = G.run_replicate(load_baselines(), G.SCENARIOS["null"], 0, 0, cfg, 4242)
    assert (r["n_win_glac"], r["n_win_ctrl"]) == (898, 275)
    assert r["T1_ctrl"] == pytest.approx(0.5133333333333333, abs=0)
    assert r["T2_glac"] == pytest.approx(0.73, abs=0)
    assert r["T2_ctrl"] == pytest.approx(0.44, abs=0)
    # T3 is an analytic scipy p-value: last-digit differences across scipy versions (CI minimum
    # versions: ...892 vs ...915), so a relative tolerance; the simulated values above are exact
    assert r["T3_ctrl"] == pytest.approx(0.17175453871705915, rel=1e-12)


def _held_at_first_bootstrap_catalogue(n_boot: int, monkeypatch: pytest.MonkeyPatch) -> int:
    """Traced memory when the first bootstrap catalogue is evaluated (call 2 of _ks_window)."""
    base = _ctrl()
    w = simulate_window(base, NO, NO, 0.0, 3.0, 1, mu_mode="ref", seed=1)
    orig, seen = S._ks_window, []

    def spy(*args: object) -> object:
        seen.append(tracemalloc.get_traced_memory()[0])
        return orig(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(S, "_ks_window", spy)
    tracemalloc.start()
    ogata_ks_bootstrap(NO, NO, w.times[0], w.mags[0], (0.0, 3.0), base, n_boot=n_boot, seed=2)
    tracemalloc.stop()
    return seen[1] - seen[0]


def test_bootstrap_holds_one_catalogue_at_a_time(monkeypatch: pytest.MonkeyPatch) -> None:
    # before streaming, all n_boot catalogues (~300 events each) existed before the first was used
    small = _held_at_first_bootstrap_catalogue(20, monkeypatch)
    large = _held_at_first_bootstrap_catalogue(400, monkeypatch)
    # measured: old code +4.3 MB, streamed +0.1 MB (the list of 400 seed sequences only)
    assert large - small < 1_000_000
