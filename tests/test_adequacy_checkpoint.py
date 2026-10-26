"""Checkpointed bootstrap: a resumed run is bit-identical to an uninterrupted one."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from glacial_seismic_sensitivity_utac.etas_adequacy import gate_sim as G
from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy import stats as S
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import iter_window, simulate_window
from glacial_seismic_sensitivity_utac.etas_adequacy.stats import ogata_ks_bootstrap

NO = np.array([])
WIN = (0.0, 3.0)
N_BOOT = 25  # last block (20..25) is partial with block = 10


def _setup() -> tuple[G.Baseline, np.ndarray, np.ndarray]:
    base = load_baselines()[G.CONTROL]
    w = simulate_window(base, NO, NO, *WIN, 1, mu_mode="ref", seed=1)
    return base, w.times[0], w.mags[0]


def _boot(path: Path | None, seed: int = 2) -> S.OgataKS:
    base, wt, wm = _setup()
    return ogata_ks_bootstrap(NO, NO, wt, wm, WIN, base, n_boot=N_BOOT, seed=seed,
                              checkpoint=path, block=10)  # fmt: skip


def _d_b(path: Path) -> list[float]:
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
    return [d for r in rows[1:] for d in r["d_b"]]


def test_iter_window_start_skips_without_changing_streams() -> None:
    base = _setup()[0]
    full = list(iter_window(base, NO, NO, *WIN, 6, mu_mode="mixture", seed=4))
    tail = list(iter_window(base, NO, NO, *WIN, 6, mu_mode="mixture", seed=4, start=4))
    assert len(tail) == 2
    for (t, m, mu), (t2, m2, mu2) in zip(full[4:], tail, strict=True):
        assert np.array_equal(t, t2) and np.array_equal(m, m2) and mu == mu2
    with pytest.raises(ValueError, match="start"):
        iter_window(base, NO, NO, *WIN, 6, start=7)


def test_checkpoint_gives_the_uninterrupted_result(tmp_path: Path) -> None:
    plain, ck = _boot(None), _boot(tmp_path / "ck.jsonl")
    assert ck == plain
    lines = (tmp_path / "ck.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 + 3  # identity + blocks 0, 10, 20
    assert json.loads(lines[-1])["k1"] == N_BOOT


def test_resume_after_crash_is_bit_identical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ck.jsonl"
    plain = _boot(None)
    _boot(path)
    reference_d = _d_b(path)
    path.unlink()

    orig, calls = S._ks_window, [0]

    def crash_in_third_block(*args: object) -> object:
        calls[0] += 1
        if calls[0] == 1 + 20 + 3:  # observed window + two full blocks + 3 of the third
            raise KeyboardInterrupt
        return orig(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(S, "_ks_window", crash_in_third_block)
    with pytest.raises(KeyboardInterrupt):
        _boot(path)
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1 + 2

    calls[0] = -10**9  # no crash on the resumed run; count what it simulates
    counted = [0]

    def count(*args: object) -> object:
        counted[0] += 1
        return orig(*args)  # type: ignore[arg-type]

    monkeypatch.setattr(S, "_ks_window", count)
    resumed = _boot(path)
    assert counted[0] == 1 + 5  # observed window + only the 5 missing catalogues
    assert resumed == plain
    assert _d_b(path) == reference_d


def test_truncated_last_line_is_dropped_and_redone(tmp_path: Path) -> None:
    path = tmp_path / "ck.jsonl"
    plain = _boot(path)
    text = path.read_text(encoding="utf-8")
    path.write_text(text[: text.rindex('{"k0": 20')] + '{"k0": 20, "k1": 2', encoding="utf-8")
    assert _boot(path) == plain
    assert len(path.read_text(encoding="utf-8").splitlines()) == 1 + 3


def test_checkpoint_of_another_run_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "ck.jsonl"
    _boot(path, seed=2)
    before = path.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="different run"):
        _boot(path, seed=3)
    assert path.read_text(encoding="utf-8") == before


def test_block_must_be_positive(tmp_path: Path) -> None:
    base, wt, wm = _setup()
    with pytest.raises(ValueError, match="block"):
        ogata_ks_bootstrap(NO, NO, wt, wm, WIN, base, n_boot=5, checkpoint=tmp_path / "c", block=0)
