"""AP4: simulated size and power of the draft A8 adequacy gate (variants S and L).

One *replicate* generates a synthetic 2025 history and a 2026 window for both regions of the primary
pair from a data-generating scenario, then computes the three gate tests exactly as draft A8 states
them, always against the *frozen* model:

* T1  number test of the control region: simulated counts of the frozen model with
      log mu ~ N(log_mu_ref, sigma_year^2), conditional on the history; two-sided quantile p.
* T2  Ogata KS of transformed intervals vs Exp(1), mu re-estimated on the window, p from the
      parametric bootstrap that re-estimates mu in every simulation (per region).
* T3  two-sample KS of window magnitudes vs a 10-year reference sample (per region).

Only p-values are stored; the gate rules are applied afterwards (``gate_strict``, ``gate_lenient``),
so the raw replicates do not depend on the rule. Everything here is synthetic: no catalogue data
are read, and no threshold is derived from real data.

Assumptions (not part of the frozen baseline): b = 1.0, magnitudes binned to 0.1, m_max = 8.0.
The data years are independent mixture draws of mu (sigma_year), as in the frozen model.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, replace

import numpy as np

from .forecast import _magnitudes, expected_cluster_moments, simulate_window
from .frozen import PRIMARY_PAIR, Baseline
from .stats import m_test_ks2, n_test_empirical, ogata_ks_bootstrap

B_VALUE = 1.0
M_MAX = 8.0
DM = 0.1
WINDOW = (0.0, 1.0)
REF_YEARS = 10
GLACIER, CONTROL = PRIMARY_PAIR

TEST_KEYS = ("T1_ctrl", "T2_glac", "T2_ctrl", "T3_glac", "T3_ctrl")


@dataclass(frozen=True)
class Scenario:
    """Data-generating deviation from the frozen model (applied to ``regions``)."""

    name: str
    description: str
    regions: tuple[str, ...] = PRIMARY_PAIR
    p: float | None = None  # data Omori exponent (all years)
    alpha_factor: float = 1.0  # data alpha = factor * frozen alpha (all years)
    target_n: float | None = None  # data K scaled so the branching ratio becomes target_n
    keep_rate: bool = False  # with target_n: lower mu so the expected annual count is unchanged
    mu_factor: float = 1.0  # window (2026) background multiplied
    swarm_events: int = 0  # extra events in the window, uniform within swarm_days
    swarm_days: float = 7.0
    mc_shift: float = 0.0  # window events below mc_ref + mc_shift are lost

    def data_baseline(self, base: Baseline) -> Baseline:
        if base.region not in self.regions:
            return base
        # A shape change (p, alpha) keeps the frozen branching ratio: with the frozen c ~ 4e-5,
        # p = 1.2 at fixed K would multiply n by ~3 (supercritical). K is rescaled instead, so
        # the scenario tests the kernel shape, not a hidden productivity change.
        n_model, _ = expected_cluster_moments(base, B_VALUE, M_MAX)
        target = self.target_n if self.target_n is not None else n_model
        b = base
        if self.p is not None:
            b = replace(b, p=self.p)
        if self.alpha_factor != 1.0:
            b = replace(b, alpha=b.alpha * self.alpha_factor)
        if b != base or self.target_n is not None:
            n0, _ = expected_cluster_moments(b, B_VALUE, M_MAX)
            b = replace(b, K=b.K * target / n0)
        if self.keep_rate:  # background lowered so that mu / (1 - n) stays as in the model
            b = replace(b, log_mu_ref=b.log_mu_ref + float(np.log((1 - target) / (1 - n_model))))
        return b


SCENARIOS: dict[str, Scenario] = {
    s.name: s
    for s in (
        Scenario("null", "true frozen model (size of the gate)"),
        Scenario("p12", "data Omori exponent p = 1.2 (frozen 1.0001), same n", p=1.2),
        Scenario("alpha_half", "data productivity exponent alpha / 2, same n", alpha_factor=0.5),
        Scenario(
            "cluster_plus",
            "stronger clustering than the model: data K scaled to branching ratio n = 0.95",
            target_n=0.95,
        ),
        Scenario(
            "cluster_plus_same_rate",
            "stronger clustering (n = 0.95) at the model's annual count: background lowered",
            target_n=0.95,
            keep_rate=True,
        ),
        Scenario(
            "swarm_ctrl",
            "30 extra events within 7 days in the control region (2026)",
            regions=(CONTROL,),
            swarm_events=30,
        ),
        Scenario(
            "swarm_glac",
            "30 extra events within 7 days in the glacier region (2026)",
            regions=(GLACIER,),
            swarm_events=30,
        ),
        Scenario("mc_jump", "completeness worsens by +0.3 in 2026 (both regions)", mc_shift=0.3),
        Scenario(
            "signal_glac",
            "the sought signal: glacier-region background x 1.5 in 2026, model otherwise true",
            regions=(GLACIER,),
            mu_factor=1.5,
        ),
    )
}


@dataclass(frozen=True)
class SimConfig:
    n_t1: int = 1000  # frozen-model simulations for T1 (gate: 10,000)
    n_boot: int = 399  # bootstrap simulations for T2 (gate: 10,000)
    warmup_years: float = 2.0


@dataclass
class RegionData:
    hist_t: np.ndarray
    hist_m: np.ndarray
    win_t: np.ndarray
    win_m: np.ndarray
    ref_m: np.ndarray = field(default_factory=lambda: np.array([]))


def _seeds(seed: int, scenario_index: int, rep: int, k: int) -> list[int]:
    ss = np.random.SeedSequence([seed, scenario_index, rep])
    return [int(x) for x in ss.generate_state(k, dtype=np.uint32)]


def generate_region(
    model: Baseline, scenario: Scenario, cfg: SimConfig, seeds: list[int]
) -> RegionData:
    """Synthetic warm-up, 2025 history and 2026 window of one region under ``scenario``."""
    data = scenario.data_baseline(model)
    affected = model.region in scenario.regions
    no = np.array([])
    warm = simulate_window(
        data, no, no, -1.0 - cfg.warmup_years, -1.0, 1, mu_mode="mixture",
        b=B_VALUE, m_max=M_MAX, dm=DM, seed=seeds[0],
    )  # fmt: skip
    hist = simulate_window(
        data, warm.times[0], warm.mags[0], -1.0, 0.0, 1, mu_mode="mixture",
        b=B_VALUE, m_max=M_MAX, dm=DM, seed=seeds[1],
    )  # fmt: skip
    ht, hm = hist.times[0], hist.mags[0]
    rng = np.random.default_rng(seeds[2])
    if affected and scenario.mu_factor != 1.0:
        mu = scenario.mu_factor * float(np.exp(rng.normal(data.log_mu_ref, data.sigma_year)))
        win = simulate_window(
            data, ht, hm, *WINDOW, 1, mu_mode="fixed", mu=mu,
            b=B_VALUE, m_max=M_MAX, dm=DM, seed=seeds[3],
        )  # fmt: skip
    else:
        win = simulate_window(
            data, ht, hm, *WINDOW, 1, mu_mode="mixture",
            b=B_VALUE, m_max=M_MAX, dm=DM, seed=seeds[3],
        )  # fmt: skip
    wt, wm = win.times[0], win.mags[0]
    if affected and scenario.swarm_events:
        start = rng.uniform(WINDOW[0], WINDOW[1] - scenario.swarm_days / 365.25)
        st = start + rng.uniform(0.0, scenario.swarm_days / 365.25, scenario.swarm_events)
        sm = _magnitudes(rng, scenario.swarm_events, model.mc_ref, B_VALUE, M_MAX, DM)
        wt, wm = np.concatenate([wt, st]), np.concatenate([wm, sm])
        o = np.argsort(wt, kind="stable")
        wt, wm = wt[o], wm[o]
    if affected and scenario.mc_shift:
        keep = wm >= np.round(model.mc_ref + scenario.mc_shift, 6) - 1e-9
        wt, wm = wt[keep], wm[keep]
    # reference magnitudes 2016-2025: GR above mc_ref (scenarios never change b)
    n_br, _ = expected_cluster_moments(data, B_VALUE, M_MAX)
    annual = np.exp(data.log_mu_ref + 0.5 * data.sigma_year**2) / (1.0 - n_br)
    ref_m = _magnitudes(rng, int(round(REF_YEARS * annual)), model.mc_ref, B_VALUE, M_MAX, DM)
    return RegionData(ht, hm, wt, wm, ref_m)


def run_replicate(
    models: dict[str, Baseline], scenario: Scenario, scenario_index: int, rep: int,
    cfg: SimConfig, seed: int,
) -> dict[str, float | int | str]:  # fmt: skip
    """All gate p-values of one replicate (plus counts and timing)."""
    t_start = time.perf_counter()
    s = _seeds(seed, scenario_index, rep, 16)
    out: dict[str, float | int | str] = {"scenario": scenario.name, "rep": rep}
    for j, region in enumerate(PRIMARY_PAIR):
        key = "glac" if region == GLACIER else "ctrl"
        model = models[region]
        d = generate_region(model, scenario, cfg, s[6 * j : 6 * j + 4])
        out[f"n_hist_{key}"] = len(d.hist_t)
        out[f"n_win_{key}"] = len(d.win_t)
        if region == CONTROL:
            sims = simulate_window(
                model, d.hist_t, d.hist_m, *WINDOW, cfg.n_t1, mu_mode="mixture",
                b=B_VALUE, m_max=M_MAX, dm=DM, seed=s[12],
            )  # fmt: skip
            out["T1_ctrl"] = n_test_empirical(len(d.win_t), sims.counts).p_two_sided
        o = ogata_ks_bootstrap(
            d.hist_t, d.hist_m, d.win_t, d.win_m, WINDOW, model,
            n_boot=cfg.n_boot, b=B_VALUE, seed=s[13 + j],
        )  # fmt: skip
        out[f"T2_{key}"] = float("nan") if o.p_bootstrap is None else o.p_bootstrap
        out[f"T2nom_{key}"] = o.p_nominal
        out[f"T3_{key}"] = m_test_ks2(d.win_m, d.ref_m) if len(d.win_m) else float("nan")
    out["seconds"] = round(time.perf_counter() - t_start, 3)
    return out


def _rej(p: float, level: float) -> bool:
    return bool(np.isfinite(p) and p < level)


def gate_strict(r: dict[str, float], level: float = 0.05) -> bool:
    """Variant S: inconclusive if any of T1, T2 (either region), T3 (either region) has p < 0.05."""
    return any(_rej(float(r[k]), level) for k in TEST_KEYS)


def gate_lenient(r: dict[str, float], level: float = 0.005) -> bool:
    """Variant L: inconclusive only if T1 or T2 of the control region has p < 0.005."""
    return _rej(float(r["T1_ctrl"]), level) or _rej(float(r["T2_ctrl"]), level)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95 % interval for a binomial rate."""
    if n == 0:
        return float("nan"), float("nan")
    ph = k / n
    den = 1 + z * z / n
    mid = (ph + z * z / (2 * n)) / den
    half = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return float(mid - half), float(mid + half)
