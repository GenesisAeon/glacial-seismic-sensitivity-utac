"""EXPLORATORY (not preregistered) robustness of H2.1 for the primary pair, run after the
preregistered analysis: year subsets, joint estimator, relaxed lower bound on p, tmax 3 yr.
Writes results/v02/m2_exploratory_robustness.csv."""

from __future__ import annotations

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import etas_nonstat as E
from glacial_seismic_sensitivity_utac import v02

K_SE = 1.25
rows = []


def trend(f: E.NSFit, years: tuple[float, float]) -> tuple[float, float]:
    tr = E.log_mu_trend(f, years)
    return tr["slope_per_decade"], tr["se"] * K_SE


fits: dict[tuple[str, str], E.NSFit] = {}
for name in ("SE_Alaska_AK", "Interior_AK_ctrl"):
    p = v02.prepare_region(name)
    assert p is not None
    t, m = v02.region_events(p)
    edges = np.arange(1995.0, 2026.5, 1.0)
    _, fits[(name, "two_stage")] = E.fit_two_stage(t, m, p.mc_ref, 1995.0, 2026.0, edges=edges)
    fits[(name, "joint")] = E.fit_nonstationary(t, m, p.mc_ref, 1995.0, 2026.0, edges=edges)
    old = E.BOUNDS_TRIG[3]
    E.BOUNDS_TRIG[3] = (0.3, 2.5)
    _, fits[(name, "two_stage_p_free")] = E.fit_two_stage(
        t, m, p.mc_ref, 1995.0, 2026.0, edges=edges
    )
    E.BOUNDS_TRIG[3] = old
    t3, m3 = v02.region_events(p, t0=1990.0)
    _, fits[(name, "two_stage_tmax3")] = E.fit_two_stage(
        t3, m3, p.mc_ref, 1995.0, 2026.0, edges=edges, tmax=3.0
    )
    print(name, "fitted", flush=True)

for variant in ("two_stage", "joint", "two_stage_p_free", "two_stage_tmax3"):
    for years in ((1995.0, 2026.0), (2003.0, 2026.0), (1995.0, 2025.0), (2003.0, 2025.0)):
        g = trend(fits[("SE_Alaska_AK", variant)], years)
        c = trend(fits[("Interior_AK_ctrl", variant)], years)
        d = E.did_test(dict(slope_per_decade=g[0], se=g[1]), dict(slope_per_decade=c[0], se=c[1]))
        fg = fits[("SE_Alaska_AK", variant)]
        rows.append(
            dict(
                variant=variant,
                years=f"{years[0]:.0f}-{years[1] - 1:.0f}",
                slope_glacier=g[0],
                se_glacier=g[1],
                slope_control=c[0],
                se_control=c[1],
                p_glacier=fg.p,
                branching_glacier=fg.branching_ratio,
                **d,
            )
        )
out = pd.DataFrame(rows)
out.to_csv("results/v02/m2_exploratory_robustness.csv", index=False)
print(out.round(3).to_string())
