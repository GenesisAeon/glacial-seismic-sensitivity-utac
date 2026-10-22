"""AP5: bias of C2 from the tail of the M6.8 sequence of 2025-12-06 (synthetic; data up to 2025).

The frozen ETAS underpredicts this sequence by far (direct aftershocks >= Mc in the first 25 days:
about 44 expected, 2,415 observed). Its continuation into the C2 window is therefore not taken
from the frozen model but from an empirical Omori-Utsu rate of the *whole* sequence (all
generations), fitted to days 2-25 after the mainshock (complete at Mc 2.1 from about day 2):

    rate(t) = A * (t - t_ms)^(-p)      events >= Mc per year, t in decimal years

with A in yr^(p-1) units. The scenario sets p; A is the profile MLE on days 2-25 for that p
(``calibration.json``, written by ``scripts/sequence_tail_c2.py calibrate``).

Injected sequence events get **no** frozen-model offspring (the empirical rate already contains
all generations), but they are part of the catalogue handed to C2, so the C2 estimator sees them
as triggers, exactly as with real data. Their magnitudes are resampled from the observed sequence
magnitudes of days 2-25.

Everything else is the frozen model: per region a warm-up, then one ``simulate_window`` per
calendar year 2026..2036, each with its own mixture draw of mu (independent yearly mu, as assumed
by the sigma_year^2 / T term of C2), with the previous year's frozen-model events as history. C2
is evaluated with ``confirmatory_v02.evaluate_pair`` at both preregistered looks, on events from
2026-01-01 on (the year before the window enters as triggers only, PREREGISTRATION_v0.2 sec. 5).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..confirmatory_v02 import LOOKS, evaluate_pair
from .forecast import simulate_window
from .frozen import Baseline

GLACIER = "SE_Alaska_AK"
CONTROL = "Interior_AK_ctrl"
M_MAX = 8.0
DM = 0.1
YEARS = tuple(range(2026, 2037))  # simulated calendar years; looks end 2030.0 and 2037.0
DATA_START = 2026.0  # C2 catalogues start with the year before the window
MAX_INJECTED = 200_000  # memory guard for the injected sequence


@dataclass(frozen=True)
class TailScenario:
    name: str
    p: float | None  # None: no sequence tail (size of C2 under the frozen model)


SCENARIOS: dict[str, TailScenario] = {
    s.name: s
    for s in (
        TailScenario("none", None),
        TailScenario("p10", 1.0),
        TailScenario("p11", 1.1),
        TailScenario("p12", 1.2),
        TailScenario("p13", 1.3),
    )
}


def omori_integral(lo: float, hi: float, p: float) -> float:
    """Integral of x^(-p) over [lo, hi], 0 < lo < hi."""
    if not 0.0 < lo < hi:
        raise ValueError("need 0 < lo < hi")
    if p == 1.0:
        return float(np.log(hi / lo))
    return float((lo ** (1.0 - p) - hi ** (1.0 - p)) / (p - 1.0))


def omori_times(rng: np.random.Generator, n: int, lo: float, hi: float, p: float) -> np.ndarray:
    """n times on [lo, hi] (time since mainshock) with density proportional to x^(-p)."""
    u = rng.uniform(0.0, 1.0, n)
    if p == 1.0:
        return np.asarray(lo * (hi / lo) ** u)
    a, b = lo ** (1.0 - p), hi ** (1.0 - p)
    return np.asarray((a + u * (b - a)) ** (1.0 / (1.0 - p)))


def inject_tail(
    rng: np.random.Generator,
    amp: float,
    p: float,
    t_ms: float,
    t0: float,
    t1: float,
    mag_values: np.ndarray,
    mag_weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Poisson process with rate amp * (t - t_ms)^(-p) on [t0, t1) (decimal years)."""
    lam = amp * omori_integral(t0 - t_ms, t1 - t_ms, p)
    n = int(rng.poisson(lam))
    if n > MAX_INJECTED:
        raise RuntimeError(f"injected sequence exceeds MAX_INJECTED = {MAX_INJECTED}")
    t = t_ms + omori_times(rng, n, t0 - t_ms, t1 - t_ms, p)
    m = rng.choice(mag_values, size=n, p=mag_weights / mag_weights.sum())
    o = np.argsort(t, kind="stable")
    return t[o], np.asarray(m, float)[o]


def _frozen_years(
    rng_seeds: list[int], base: Baseline, b: float, warmup_years: float
) -> tuple[np.ndarray, np.ndarray]:
    """Frozen-model catalogue 2026..2036, one mixture draw of mu per calendar year."""
    no = np.array([])
    warm = simulate_window(
        base, no, no, DATA_START - warmup_years, DATA_START, 1, mu_mode="mixture",
        b=b, m_max=M_MAX, dm=DM, seed=rng_seeds[0],
    )  # fmt: skip
    ht, hm = warm.times[0], warm.mags[0]
    out_t, out_m = [], []
    for k, y in enumerate(YEARS):
        w = simulate_window(
            base, ht, hm, float(y), float(y + 1), 1, mu_mode="mixture",
            b=b, m_max=M_MAX, dm=DM, seed=rng_seeds[1 + k],
        )  # fmt: skip
        ht, hm = w.times[0], w.mags[0]
        out_t.append(ht)
        out_m.append(hm)
    return np.concatenate(out_t), np.concatenate(out_m)


def _seeds(seed: int, scenario_index: int, rep: int, k: int) -> list[int]:
    ss = np.random.SeedSequence([seed, scenario_index, rep])
    return [int(x) for x in ss.generate_state(k, dtype=np.uint32)]


def run_replicate(
    models: dict[str, Baseline],
    b_values: dict[str, float],
    calib: dict[str, object],
    scenario: TailScenario,
    scenario_index: int,
    rep: int,
    seed: int,
    warmup_years: float = 20.0,
) -> dict[str, float | int | str | bool]:
    t_start = time.time()
    n_seed = 1 + len(YEARS)
    s = _seeds(seed, scenario_index, rep, 2 * n_seed + 1)
    tg, mg = _frozen_years(s[:n_seed], models[GLACIER], b_values[GLACIER], warmup_years)
    tc, mc = _frozen_years(s[n_seed : 2 * n_seed], models[CONTROL], b_values[CONTROL], warmup_years)
    n_inj = 0
    n_inj_look = {2030.0: 0, 2037.0: 0}
    if scenario.p is not None:
        amp = float(calib["amp_per_yr"][f"{scenario.p:.1f}"])  # type: ignore[index]
        vals = np.asarray(calib["mag_values"], float)
        wts = np.asarray(calib["mag_counts"], float)
        rng = np.random.default_rng(s[-1])
        it, im = inject_tail(
            rng, amp, scenario.p, float(calib["t_mainshock"]),  # type: ignore[arg-type]
            DATA_START, float(YEARS[-1] + 1), vals, wts,
        )  # fmt: skip
        n_inj = len(it)
        for end in n_inj_look:
            n_inj_look[end] = int(((it >= 2027.0) & (it < end)).sum())
        tg, mg = np.concatenate([tg, it]), np.concatenate([mg, im])
        o = np.argsort(tg, kind="stable")
        tg, mg = tg[o], mg[o]
    cg = pd.DataFrame({"t": tg, "mag": mg})
    cc = pd.DataFrame({"t": tc, "mag": mc})
    baselines = {"regions": {r: _as_dict(models[r]) for r in (GLACIER, CONTROL)}}
    row: dict[str, float | int | str | bool] = {
        "scenario": scenario.name,
        "rep": rep,
        "n_injected_2026_2036": n_inj,
    }
    for end, _alpha in LOOKS:
        r = evaluate_pair(cg, cc, baselines, end)
        tag = f"{int(end) - 1}"  # 2029 / 2036 (last data year)
        row[f"D_{tag}"] = float(r["D"])
        row[f"z_{tag}"] = float(r["z"])
        row[f"p_{tag}"] = float(r["p_one"])
        row[f"reject_{tag}"] = bool(r["reject"])
        row[f"dlog_glac_{tag}"] = float(r["glacier"]["delta_log_mu"])
        row[f"dlog_ctrl_{tag}"] = float(r["control"]["delta_log_mu"])
        row[f"n_glac_{tag}"] = int(r["glacier"]["n_new"])
        row[f"n_ctrl_{tag}"] = int(r["control"]["n_new"])
        row[f"n_injected_{tag}"] = n_inj_look[end]
    row["seconds"] = round(time.time() - t_start, 2)
    return row


def _as_dict(b: Baseline) -> dict[str, float]:
    return {
        "mc_ref": b.mc_ref,
        "K": b.K,
        "alpha": b.alpha,
        "c_yr": b.c_yr,
        "p": b.p,
        "tmax_yr": b.tmax_yr,
        "log_mu_ref": b.log_mu_ref,
        "sigma_year": b.sigma_year,
        "n_ref_years": b.n_ref_years,
    }
