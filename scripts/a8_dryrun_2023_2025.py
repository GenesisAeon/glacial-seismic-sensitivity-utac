"""A8 dry run (FUNCTIONAL TEST ONLY, no statement about C2): gate L + T3 on legacy data.

Pseudo test window 2023-01-01 <= t < 2026-01-01 (3 years), reference magnitudes 2016-2022,
history (triggers only) = 2022 events, as C2 uses the year before its window. Data come only from
the frozen snapshots results/adequacy/b_value/comcat_ak_*_2016_2025.csv.gz (nothing from 2026 on is
read; the script aborts if any event lies at or after 2026-01-01). Real code path: frozen
baselines + b-values (SHA-checked), catalog.prepare, Mc cut at mc_ref, T1 (10,000 simulations),
T2 (Ogata KS, parametric bootstrap B = 10,000), T3 (two-sample KS), rule gate_lenient_t3.
One fixed seed, no rerun with another seed.
"""

from __future__ import annotations

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac.catalog import prepare
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import simulate_window
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import (
    PRIMARY_PAIR,
    load_b_values,
    load_baselines,
)
from glacial_seismic_sensitivity_utac.etas_adequacy.gate_sim import (
    gate_lenient,
    gate_lenient_t3,
    gate_strict,
)
from glacial_seismic_sensitivity_utac.etas_adequacy.stats import (
    m_test_ks2,
    n_test_empirical,
    ogata_ks_bootstrap,
)

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "results" / "adequacy" / "b_value"
OUT = ROOT / "results" / "adequacy" / "a8_dryrun"
SEED = 20261022
M_MAX, DM = 8.0, 0.1
YR = 365.25 * 86400
W0, W1 = pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
H0 = pd.Timestamp("2022-01-01", tz="UTC")
R0 = pd.Timestamp("2016-01-01", tz="UTC")


def peak_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def load_region(name: str, mc: float) -> pd.DataFrame:
    raw = pd.read_csv(SNAP / f"comcat_ak_{name}_2016_2025.csv.gz")
    p = prepare(raw, C.REGIONS[name])
    if (p.time >= W1).any():
        raise SystemExit(f"{name}: event at or after 2026-01-01 in snapshot - abort")
    p = p[(p.time >= R0) & (p.time < W1)]
    return p[p.mag >= mc - 1e-9]  # Mc cut as catalog.b_value


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-sim", type=int, default=10_000)
    a = ap.parse_args()
    t_all = time.perf_counter()
    models, bvals = load_baselines(), load_b_values()
    ss = np.random.SeedSequence(SEED).generate_state(4, dtype=np.uint32)
    res: dict = {"label": "FUNCTIONAL TEST ONLY - no statement about C2", "seed": SEED,
                 "n_sim": a.n_sim, "window": "2023-01-01..2025-12-31", "history": "2022",
                 "reference": "2016-01-01..2022-12-31", "regions": {}}  # fmt: skip
    p: dict[str, float] = {}
    for j, name in enumerate(PRIMARY_PAIR):
        key = "glac" if j == 0 else "ctrl"
        base, b = models[name], bvals[name]
        df = load_region(name, base.mc_ref)
        t = ((df.time - W0).dt.total_seconds() / YR).to_numpy()
        m = df.mag.to_numpy()
        ref = (df.time >= R0) & (df.time < W0)
        hist = (df.time >= H0) & (df.time < W0)
        win = (df.time >= W0) & (df.time < W1)
        ht, hm, wt, wm = (
            t[hist.to_numpy()],
            m[hist.to_numpy()],
            t[win.to_numpy()],
            m[win.to_numpy()],
        )
        window = (0.0, (W1 - W0).total_seconds() / YR)
        r = {"n_ref": int(ref.sum()), "n_hist": int(hist.sum()), "n_win": int(win.sum()),
             "b": b, "mc_ref": base.mc_ref}  # fmt: skip
        if j == 1:
            t0 = time.perf_counter()
            sims = simulate_window(
                base,
                ht,
                hm,
                *window,
                a.n_sim,
                mu_mode="mixture",
                b=b,
                m_max=M_MAX,
                dm=DM,
                seed=int(ss[0]),
            )
            p["T1_ctrl"] = n_test_empirical(len(wt), sims.counts).p_two_sided
            r["T1_sim_count_median"] = float(np.median(sims.counts))
            r["T1_seconds"] = round(time.perf_counter() - t0, 1)
            del sims
        t0 = time.perf_counter()
        o = ogata_ks_bootstrap(
            ht, hm, wt, wm, window, base, n_boot=a.n_sim, b=b, seed=int(ss[1 + j])
        )
        p[f"T2_{key}"] = float("nan") if o.p_bootstrap is None else o.p_bootstrap
        r.update(
            T2_mu_hat=o.mu_hat,
            T2_ks=o.ks_stat,
            T2_p_nominal=o.p_nominal,
            T2_seconds=round(time.perf_counter() - t0, 1),
        )
        p[f"T3_{key}"] = m_test_ks2(wm, m[ref.to_numpy()])
        r["peak_rss_mb_after"] = round(peak_mb(), 1)
        res["regions"][name] = r
        print(name, r, flush=True)
    res["p"] = p
    res["gate"] = {"L+T3": gate_lenient_t3(p), "L": gate_lenient(p), "S": gate_strict(p)}
    res["seconds_total"] = round(time.perf_counter() - t_all, 1)
    res["peak_rss_mb"] = round(peak_mb(), 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dryrun_2023_2025.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
