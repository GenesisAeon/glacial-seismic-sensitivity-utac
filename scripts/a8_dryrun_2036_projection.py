"""A8 dry run, projected 2036 look (FUNCTIONAL TEST ONLY, no statement about C2).

Purpose: measure (not estimate) runtime and peak memory of the gate L + T3 for the 10-year window
[2027-01-01, 2037-01-01) of the 2036-12-31 look, using the streaming code path
(``forecast.simulate_counts`` for T1, streamed ``stats.ogata_ks_bootstrap`` for T2).

No real 2026+ data exist or are read. Stand-ins, from the frozen snapshots only:
  * history (triggers only): the real 2025 events (stand-in for 2026), shifted to t < 0;
  * "observed" window: ONE synthetic 10-year catalogue per region drawn from the frozen model
    (mu mixture, frozen b, dm 0.1), seed below;
  * T3 reference: all real events 2016-01-01 <= t < 2026-01-01 with M >= Mc_ref (5,442 / 2,098),
    exactly the A8 reference sample.
T1: 10,000 simulations; T2 control: B = 10,000; T2 glacier: B = --n-boot-glac (default 500),
because one glacier bootstrap catalogue costs ~1.7 s here (B = 10,000 would take ~4.6 h on the
box). With streaming, memory does not grow with B (only the float array D_b, 80 kB at 10,000),
so the memory peak is representative; runtime for B = 10,000 is extrapolated, not measured.
One fixed dry-run seed (not the A8 seed).
Memory: tracemalloc peak (Python + NumPy heap) and ru_maxrss (process peak RSS).
"""

from __future__ import annotations

import argparse
import json
import resource
import time
import tracemalloc
from pathlib import Path

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac.catalog import prepare
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import (
    simulate_counts,
    simulate_window,
)
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
SEED = 20261023
N_SIM = 10_000
M_MAX, DM = 8.0, 0.1
YR = 365.25 * 86400
R0, R1 = pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
H0 = pd.Timestamp("2025-01-01", tz="UTC")
WINDOW = (0.0, (pd.Timestamp("2037-01-01") - pd.Timestamp("2027-01-01")).total_seconds() / YR)


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot-glac", type=int, default=500)
    a = ap.parse_args()
    tracemalloc.start()
    t_all = time.perf_counter()
    models, bvals = load_baselines(), load_b_values()
    ss = np.random.SeedSequence(SEED).generate_state(6, dtype=np.uint32)
    res: dict = {"label": "FUNCTIONAL TEST ONLY - synthetic window, no statement about C2",
                 "seed": SEED, "n_sim": N_SIM, "n_boot_glac": a.n_boot_glac,
                 "window_years": WINDOW[1],
                 "code_path": "streaming (simulate_counts, streamed ogata_ks_bootstrap)",
                 "regions": {}}  # fmt: skip
    p: dict[str, float] = {}
    for j, name in enumerate(PRIMARY_PAIR):
        key = "glac" if j == 0 else "ctrl"
        base, b = models[name], bvals[name]
        df = prepare(pd.read_csv(SNAP / f"comcat_ak_{name}_2016_2025.csv.gz"), C.REGIONS[name])
        if (df.time >= R1).any():
            raise SystemExit("event at/after 2026-01-01 in snapshot - abort")
        df = df[(df.time >= R0) & (df.time < R1) & (df.mag >= base.mc_ref - 1e-9)]
        # catalog.prepare bins as (m / 0.1).round() * 0.1 (e.g. 2.3000000000000003), the simulator
        # as np.round(..., 6) (2.3). Real-vs-synthetic KS then breaks ties systematically, so the
        # reference is put on the simulator's representation. Not needed in the real gate, where
        # window and reference both come from catalog.prepare. See a8_dryrun_2036_projection.md.
        ref_m = np.round(df.mag.to_numpy(), 6)
        h = df[df.time >= H0]
        ht = ((h.time - R1).dt.total_seconds() / YR).to_numpy() - 1e-9
        hm = h.mag.to_numpy()
        obs = simulate_window(base, ht, hm, *WINDOW, 1, mu_mode="mixture", b=b,
                              m_max=M_MAX, dm=DM, seed=int(ss[4 + j]))  # fmt: skip
        wt, wm = obs.times[0], obs.mags[0]
        del obs
        r = {"n_ref": len(ref_m), "n_hist": len(ht), "n_win_synthetic": len(wt), "b": b}
        if j == 1:
            t0 = time.perf_counter()
            counts = simulate_counts(base, ht, hm, *WINDOW, N_SIM, mu_mode="mixture", b=b,
                                     m_max=M_MAX, dm=DM, seed=int(ss[0]))  # fmt: skip
            p["T1_ctrl"] = n_test_empirical(len(wt), counts).p_two_sided
            r.update(T1_sim_count_median=float(np.median(counts)),
                     T1_sim_count_max=int(counts.max()),
                     T1_seconds=round(time.perf_counter() - t0, 1))  # fmt: skip
        t0 = time.perf_counter()
        o = ogata_ks_bootstrap(
            ht,
            hm,
            wt,
            wm,
            WINDOW,
            base,
            n_boot=N_SIM if j else a.n_boot_glac,
            b=b,
            seed=int(ss[1 + j]),
        )
        p[f"T2_{key}"] = float("nan") if o.p_bootstrap is None else o.p_bootstrap
        r.update(T2_B=N_SIM if j else a.n_boot_glac, T2_seconds=round(time.perf_counter() - t0, 1))
        p[f"T3_{key}"] = m_test_ks2(wm, ref_m)
        r["tracemalloc_peak_mb_so_far"] = round(tracemalloc.get_traced_memory()[1] / 2**20, 1)
        r["peak_rss_mb_so_far"] = round(rss_mb(), 1)
        res["regions"][name] = r
        print(name, r, flush=True)
    res["p"] = p
    res["gate"] = {"L+T3": gate_lenient_t3(p), "L": gate_lenient(p), "S": gate_strict(p)}
    res["seconds_total"] = round(time.perf_counter() - t_all, 1)
    res["tracemalloc_peak_mb"] = round(tracemalloc.get_traced_memory()[1] / 2**20, 1)
    res["peak_rss_mb"] = round(rss_mb(), 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dryrun_2036_projection.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
