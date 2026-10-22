"""AP6c: C2 robustness check without the epicentral zone of the 2025-12-06 M6.8.

AP6b showed that a slowly decaying excess of the 2025 sequence can mimic the sought signal in C2.
The remedy: a second, pre-registered C2 statistic on the glacier region **without** a disc of
radius R around the 2025 epicentre, with its own baseline (log mu_ref, sigma_y) from 2016-2025,
computed exactly like the frozen one (yearly mu_window_mle with the frozen triggering parameters,
one year of history as triggers). A C2 rejection of the preregistered statistic then only counts
as *confirmed* if the reduced statistic also rejects at the confirmation level (AP6c rule).

The C2 statistic itself is unchanged; the reduced statistic only adds a confirmation condition.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from ..catalog import haversine_km
from ..confirmatory_v02 import LOOKS
from ..etas_nonstat import mu_window_mle
from .frozen import Baseline
from .sequence_term import (
    YEARS_SIM,
    _frozen_catalogue,
    _term_seeds,
    evaluate_pair_with_term,
)


def outside_zone(
    lat: np.ndarray, lon: np.ndarray, lat0: float, lon0: float, r_km: float
) -> np.ndarray:
    """True for events at least ``r_km`` from the epicentre (great-circle distance)."""
    return np.asarray(
        haversine_km(np.asarray(lat, float), np.asarray(lon, float), lat0, lon0) >= r_km
    )


def yearly_log_mu(
    t: np.ndarray, m: np.ndarray, base: Baseline, years: range = range(2016, 2026)
) -> np.ndarray:
    """log mu_y per calendar year with the frozen triggering, one year of history as triggers."""
    out = []
    for y in years:
        s = (t >= y - 1) & (t < y + 1)
        out.append(
            mu_window_mle(t[s], m[s], base.mc_ref, base.trig(), float(y), float(y + 1))["log_mu"]
        )
    return np.array(out)


def reduced_baseline(
    t: np.ndarray, m: np.ndarray, outside: np.ndarray, base: Baseline
) -> tuple[Baseline, dict[str, list[float]]]:
    """Baseline of the reduced region, **relative to the frozen one**.

    The frozen baseline comes from smoothed two-stage fits with a long history (``v02``); the
    2016-2025 snapshot lacks the history before 2016. Both regions are therefore computed with
    the same method here (``yearly_log_mu``) and only the difference of the means and the ratio of
    the SDs are transferred:

        log mu_ref,red = log mu_ref,full + mean(ly_red) - mean(ly_full)
        sigma_y,red    = sigma_y,full * sd(ly_red) / sd(ly_full)
    """
    ly_full = yearly_log_mu(t, m, base)
    ly_red = yearly_log_mu(t[outside], m[outside], base)
    if not (np.all(np.isfinite(ly_full)) and np.all(np.isfinite(ly_red))):
        raise ValueError("a yearly log mu is not finite")
    red = dataclasses.replace(
        base,
        log_mu_ref=float(base.log_mu_ref + ly_red.mean() - ly_full.mean()),
        sigma_year=float(base.sigma_year * ly_red.std(ddof=1) / ly_full.std(ddof=1)),
    )
    return red, {"ly_full": ly_full.tolist(), "ly_red": ly_red.tolist()}


@dataclass(frozen=True)
class ZoneScenario:
    name: str
    e0: float = 0.0  # excess level at mid-2026 (events/yr), whole region, as AP6b
    r: float = 0.5
    leak: float = 0.05  # share of the excess (and spike) outside the zone
    mu_factor: float = 1.0  # glacier background x factor from 2027 (uniform over the region)


ZONE_SCENARIOS: dict[str, ZoneScenario] = {
    s.name: s
    for s in (
        ZoneScenario("e0"),
        ZoneScenario("e75_r05_l05", 75.0, 0.5, 0.05),
        ZoneScenario("e75_r05_l30", 75.0, 0.5, 0.30),
        ZoneScenario("e150_r05_l05", 150.0, 0.5, 0.05),
        ZoneScenario("e150_r05_l30", 150.0, 0.5, 0.30),
        ZoneScenario("signal_e0", mu_factor=1.5),
        ZoneScenario("signal_e150_r05_l05", 150.0, 0.5, 0.05, mu_factor=1.5),
    )
}


def run_zone_replicate(
    models: dict[str, Baseline],
    reduced: Baseline,
    b_values: dict[str, float],
    ctx: dict[str, Any],
    scenario: ZoneScenario,
    idx: int,
    rep: int,
    seed: int,
    warmup_years: float = 20.0,
) -> dict[str, Any]:
    """One AP6c replicate (AP6b truth + zone labels).

    Real 2026 events keep their real zone label. Synthetic frozen-model events are in the zone
    with probability ``pi_zone`` = 1 - exp(log mu_ref_reduced - log mu_ref_full) (so the thinned
    background matches the reduced baseline); spike and excess are in the zone with probability
    1 - leak. Full region = preregistered C2; reduced region = C2 with the reduced baseline."""
    import time

    from .sequence_tail import inject_tail

    t0 = time.time()
    gl, ct = "SE_Alaska_AK", "Interior_AK_ctrl"
    n_s = 2 + len(YEARS_SIM)
    s = _term_seeds(seed, idx, rep, 2 * n_s + 4)
    cut, t_ms = float(ctx["cutoff"]), float(ctx["t_ms"])
    pi_zone = 1.0 - float(np.exp(reduced.log_mu_ref - models[gl].log_mu_ref))
    lab = np.random.default_rng(s[-4])
    tg, mg = _frozen_catalogue(s[:n_s], models[gl], b_values[gl], warmup_years, scenario.mu_factor)
    keep = tg >= cut
    tg, mg = tg[keep], mg[keep]
    zg = lab.uniform(size=len(tg)) < pi_zone
    tc, mc = _frozen_catalogue(s[n_s : 2 * n_s], models[ct], b_values[ct], warmup_years, 1.0)
    vals, wts = np.asarray(ctx["mag_values"], float), np.asarray(ctx["mag_counts"], float)
    st, sm = inject_tail(np.random.default_rng(s[-3]), float(ctx["spike_A"]),
                         float(ctx["spike_q"]), t_ms, cut, 2037.0, vals, wts)  # fmt: skip
    zs = lab.uniform(size=len(st)) >= scenario.leak
    parts = [(tg, mg, zg), (st, sm, zs),
             (np.asarray(ctx["real_t"], float), np.asarray(ctx["real_m"], float),
              np.asarray(ctx["real_in_zone"], bool))]  # fmt: skip
    n_level = 0
    if scenario.e0 > 0:
        amp = scenario.e0 * 0.5**scenario.r
        lt, lm = inject_tail(np.random.default_rng(s[-2]), amp, scenario.r, t_ms, cut, 2037.0,
                             vals, wts)  # fmt: skip
        n_level = int(((lt >= 2027.0) & (lt < 2030.0)).sum())
        parts.append((lt, lm, lab.uniform(size=len(lt)) >= scenario.leak))
    t = np.concatenate([p[0] for p in parts])
    m = np.concatenate([p[1] for p in parts])
    z = np.concatenate([p[2] for p in parts])
    o = np.argsort(t, kind="stable")
    t, m, z = t[o], m[o], z[o]
    full = pd.DataFrame({"t": t, "mag": m})
    red = pd.DataFrame({"t": t[~z], "mag": m[~z]})
    full, red = full[full.t >= 2026.0], red[red.t >= 2026.0]
    cc = pd.DataFrame({"t": tc, "mag": mc})
    cc = cc[cc.t >= 2026.0]
    models_red = {**models, gl: reduced}
    row: dict[str, Any] = {"scenario": scenario.name, "rep": rep, "n_level_2029": n_level,
                           "pi_zone": pi_zone}  # fmt: skip
    for end, _ in LOOKS:
        tag = f"{int(end) - 1}"
        rf = evaluate_pair_with_term(full, cc, models, end, None)
        rr = evaluate_pair_with_term(red, cc, models_red, end, None)
        row[f"D_full_{tag}"], row[f"p_full_{tag}"] = float(rf["D"]), float(rf["p_one"])
        row[f"reject_full_{tag}"] = bool(rf["reject"])
        row[f"D_red_{tag}"], row[f"p_red_{tag}"] = float(rr["D"]), float(rr["p_one"])
    row["seconds"] = round(time.time() - t0, 2)
    return row
