"""AP6b: bias of the preregistered C2 under a truth calibrated to the 2026 glacier data.

Usage (from the repository root):

    python scripts/sequence_level_c2.py calibrate   # -> results/adequacy/sequence_level/calib.json
    python scripts/sequence_level_c2.py run --out results/adequacy/sequence_level/<run_id> [--pilot]
    python scripts/sequence_level_c2.py summarize --out ...

Uses only the frozen 2016-2025 snapshot and the AP6 2026 snapshot (to 2026-10-22, SHA-checked);
no new data. Resource limits and checkpoints as in ``adequacy_gate_power.py``.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adequacy_gate_power import _done_reps, _git_commit, limit_resources, peak_job_mb  # noqa: E402
from sequence_term_c2 import CALIB_AP5, GLACIER, _glacier_events, _wilson  # noqa: E402

from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import sequence_term as Q  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import (  # noqa: E402
    expected_cluster_moments,
)
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values  # noqa: E402

OUT = Path("results/adequacy/sequence_level")
DEFAULT_SEED = 20261025
PILOT_SEED = 996


def cmd_calibrate(_: argparse.Namespace) -> None:
    base = load_baselines()[GLACIER]
    bv = load_b_values()[GLACIER]
    ap5 = json.loads(CALIB_AP5.read_text(encoding="utf-8"))
    t, m, cut = _glacier_events()
    t_ms = float(ap5["t_mainshock"])
    # descriptive spike: mu + A x^-q without triggering (as in deviation D1)
    spike = Q.fit_sequence_term(t, m, dataclasses.replace(base, K=1e-15), t_ms, 2026.0, cut)
    n_br, _ = expected_cluster_moments(base, bv, 8.0, 0.1)
    real = (t >= 2026.0) & (t < cut)
    rates = {
        f"{a:.2f}": float(((t >= a) & (t < cut)).sum() / (cut - a))
        for a in (2026.25, 2026.4, 2026.5)
    }
    out = {
        "description": "AP6b calibration: real 2026 events, descriptive spike, observed rates",
        "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git_commit(),
        "t_ms": t_ms, "cutoff": cut,
        "spike_A": spike.A, "spike_q": spike.q, "spike_se_q": float(np.sqrt(spike.cov[1][1])),
        "spike_level_per_yr": float(np.exp(spike.log_mu)),
        "observed_rate_to_cutoff_per_yr": rates,
        "frozen_stationary_rate_per_yr": float(
            np.exp(base.log_mu_ref + 0.5 * base.sigma_year**2) / (1 - n_br)),
        "median_annual_2016_2024": 285,
        "real_t": t[real].tolist(), "real_m": m[real].tolist(),
        "mag_values": ap5["mag_values"], "mag_counts": ap5["mag_counts"],
    }  # fmt: skip
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "calib.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    keep = ("spike_A", "spike_q", "spike_se_q", "spike_level_per_yr",
            "observed_rate_to_cutoff_per_yr", "frozen_stationary_rate_per_yr")  # fmt: skip
    print(json.dumps({k: out[k] for k in keep}, indent=1), "n_real", int(real.sum()))


_CTX: dict[str, object] = {}


def _init() -> None:
    _CTX["models"] = dict(load_baselines())
    _CTX["b"] = load_b_values()
    _CTX["ctx"] = json.loads((OUT / "calib.json").read_text(encoding="utf-8"))


def _work(task: tuple[str, int, int, int, float]) -> dict[str, object]:
    name, idx, rep, seed, warmup = task
    return Q.run_level_replicate(
        _CTX["models"], _CTX["b"], _CTX["ctx"], Q.LEVEL_SCENARIOS[name], idx, rep, seed,  # type: ignore[arg-type]
        warmup_years=warmup,
    )  # fmt: skip


def cmd_run(a: argparse.Namespace) -> None:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = limit_resources(a.mem_mb)
    seed = PILOT_SEED if a.pilot else a.seed
    names = a.scenarios.split(",")
    meta = {"started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "commit": _git_commit(),
            "pilot": a.pilot, "seed": seed, "reps": a.reps, "workers": a.workers,
            "warmup_years": a.warmup_years, "resources": res, "python": sys.version}  # fmt: skip
    (out / f"run_{time.strftime('%Y%m%dT%H%M%S')}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    order = list(Q.LEVEL_SCENARIOS)
    tasks = []
    for n in names:
        done = _done_reps(out / f"{n}.jsonl")
        tasks += [(n, order.index(n), r, seed, a.warmup_years)
                  for r in range(a.reps) if r not in done]  # fmt: skip
    print(f"{len(tasks)} replicates to run ({res})", flush=True)
    files = {n: open(out / f"{n}.jsonl", "a", encoding="utf-8") for n in names}  # noqa: SIM115
    t0, k = time.time(), 0
    try:
        with Pool(a.workers, initializer=_init) as pool:
            for r in pool.imap_unordered(_work, tasks, chunksize=1):
                f = files[str(r["scenario"])]
                f.write(json.dumps(r) + "\n")
                f.flush()
                os.fsync(f.fileno())
                k += 1
                if k % a.progress == 0 or k == len(tasks):
                    el = time.time() - t0
                    left = el / k * (len(tasks) - k) / 60
                    print(f"{k}/{len(tasks)}  {el / 60:.1f} min  ~{left:.0f} min left"
                          f"  peak job RAM {peak_job_mb()} MB", flush=True)  # fmt: skip
    finally:
        for f in files.values():
            f.close()


def cmd_summarize(a: argparse.Namespace) -> None:
    out = Path(a.out)
    summary: dict[str, object] = {}
    print("| scenario | reps | level events 2027-29 | D 2029 | reject 2029 (a 0.01) | D 2036 "
          "| reject 2036 (a 0.04) | reject either |")  # fmt: skip
    print("|---|---:|---:|---:|---|---:|---|---|")
    for n in Q.LEVEL_SCENARIOS:
        path = out / f"{n}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        if not rows:
            continue
        m = len(rows)
        s: dict[str, object] = {
            "n_rep": m,
            "n_level_2029": float(np.mean([r["n_level_2029"] for r in rows])),
        }
        cells = []
        for tag in ("2029", "2036"):
            k = sum(bool(r[f"reject_{tag}"]) for r in rows)
            d = float(np.mean([r[f"D_{tag}"] for r in rows]))
            s[tag] = {"D_mean": d, "reject": k / m, "k": k, "ci95": _wilson(k, m)}
            lo, hi = _wilson(k, m)
            cells.append(f"{d:+.3f} | {k / m:.3f} [{lo:.3f}, {hi:.3f}]")
        e = sum(bool(r["reject_2029"]) or bool(r["reject_2036"]) for r in rows)
        s["reject_either"] = {"rate": e / m, "k": e, "ci95": _wilson(e, m)}
        lo, hi = _wilson(e, m)
        print(f"| {n} | {m} | {s['n_level_2029']:.0f} | {cells[0]} | {cells[1]} "
              f"| {e / m:.3f} [{lo:.3f}, {hi:.3f}] |")  # fmt: skip
        summary[n] = s
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("calibrate")
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--scenarios", default=",".join(Q.LEVEL_SCENARIOS))
    r.add_argument("--reps", type=int, default=400)
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--mem-mb", type=int, default=2500)
    r.add_argument("--seed", type=int, default=DEFAULT_SEED)
    r.add_argument("--warmup-years", type=float, default=20.0)
    r.add_argument("--progress", type=int, default=100)
    r.add_argument("--pilot", action="store_true")
    s = sub.add_parser("summarize")
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    {"calibrate": cmd_calibrate, "run": cmd_run, "summarize": cmd_summarize}[a.cmd](a)


if __name__ == "__main__":
    main()
