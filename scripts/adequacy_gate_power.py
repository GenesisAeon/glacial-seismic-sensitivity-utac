"""AP4: size and power of the draft A8 adequacy gate by simulation (synthetic only).

Usage (from the repository root):

    python scripts/adequacy_gate_power.py run --out results/adequacy/gate_power/<run_id>
    python scripts/adequacy_gate_power.py run --out ... --pilot        # timing/memory probe
    python scripts/adequacy_gate_power.py summarize --out ...

Resource limits (Windows): the whole process tree is put into a job object with a hard memory
cap (--mem-mb), CPU affinity to half of the logical processors and below-normal priority; the
number of worker processes defaults to 2. Each finished replicate is appended to
``<scenario>.jsonl`` (flushed and fsynced), so an interrupted run resumes with the same command.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import subprocess
import sys
import time
from collections.abc import Iterator
from multiprocessing import Pool
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402

from glacial_seismic_sensitivity_utac.etas_adequacy import gate_sim as G  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values  # noqa: E402

DEFAULT_SEED = 20261019
PILOT_SEED = 999


# ----------------------------------------------------------------------------- Windows job
class _BasicLimit(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", ctypes.c_uint32),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", ctypes.c_uint32),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", ctypes.c_uint32),
        ("SchedulingClass", ctypes.c_uint32),
    ]


class _ExtLimit(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimit),
        ("IoInfo", ctypes.c_uint64 * 6),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


_JOB: int | None = None


def limit_resources(mem_mb: int) -> dict[str, object]:
    """Job object: memory cap for the whole tree, half the logical CPUs, below-normal priority."""
    global _JOB
    n_cpu = os.cpu_count() or 2
    half = max(1, n_cpu // 2)
    info: dict[str, object] = {"logical_cpus": n_cpu, "affinity_cpus": half, "mem_mb": mem_mb}
    if platform.system() != "Windows":
        os.nice(10)
        info["job_object"] = False
        return info
    k32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    k32.CreateJobObjectW.restype = ctypes.c_void_p
    job = k32.CreateJobObjectW(None, None)
    lim = _ExtLimit()
    lim.BasicLimitInformation.LimitFlags = 0x200 | 0x10 | 0x20  # JOB_MEMORY|AFFINITY|PRIORITY
    lim.BasicLimitInformation.Affinity = (1 << half) - 1
    lim.BasicLimitInformation.PriorityClass = 0x4000  # BELOW_NORMAL_PRIORITY_CLASS
    lim.JobMemoryLimit = mem_mb * 1024 * 1024
    ok = k32.SetInformationJobObject(ctypes.c_void_p(job), 9, ctypes.byref(lim), ctypes.sizeof(lim))
    k32.GetCurrentProcess.restype = ctypes.c_void_p
    ok2 = k32.AssignProcessToJobObject(
        ctypes.c_void_p(job), ctypes.c_void_p(k32.GetCurrentProcess())
    )
    if not (ok and ok2):
        raise OSError(f"job object setup failed (set={ok}, assign={ok2})")
    k32.SetThreadExecutionState(0x80000000 | 0x00000001)  # ES_CONTINUOUS|ES_SYSTEM_REQUIRED
    _JOB = job
    info["job_object"] = True
    return info


def peak_job_mb() -> float | None:
    if _JOB is None:
        return None
    lim = _ExtLimit()
    k32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
    k32.QueryInformationJobObject(
        ctypes.c_void_p(_JOB), 9, ctypes.byref(lim), ctypes.sizeof(lim), None
    )
    return round(lim.PeakJobMemoryUsed / 2**20, 1)


# ----------------------------------------------------------------------------- workers
_MODELS: dict[str, G.Baseline] = {}


def _init() -> None:
    _MODELS.update(load_baselines())


Task = tuple[str, int, int, int, int, int, float, float, float, float]


def _cfg(
    n_t1: int, n_boot: int, b_glac: float, b_ctrl: float, warmup: float, n_dm: float
) -> G.SimConfig:
    return G.SimConfig(
        n_t1=n_t1, n_boot=n_boot, warmup_years=warmup, b_glac=b_glac, b_ctrl=b_ctrl, n_dm=n_dm
    )


def _work(task: Task) -> dict[str, float | int | str]:
    name, idx, rep, n_t1, n_boot, seed, b_glac, b_ctrl, warmup, n_dm = task
    cfg = _cfg(n_t1, n_boot, b_glac, b_ctrl, warmup, n_dm)
    return G.run_replicate(_MODELS, G.SCENARIOS[name], idx, rep, cfg, seed)


def _done_reps(path: Path) -> set[int]:
    if not path.exists():
        return set()
    reps = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            reps.add(int(json.loads(line)["rep"]))
    return reps


def _git_commit() -> str:
    r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    return r.stdout.strip()


def cmd_run(a: argparse.Namespace) -> None:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = limit_resources(a.mem_mb)
    seed = PILOT_SEED if a.pilot else a.seed
    names = a.scenarios.split(",")
    reps = {n: (a.reps_null if n == "null" else a.reps_alt) for n in names}
    meta = {
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git_commit(),
        "pilot": a.pilot,
        "seed": seed,
        "n_t1": a.n_t1,
        "n_boot": a.n_boot,
        "workers": a.workers,
        "reps": reps,
        "resources": res,
        "assumptions": {
            "b_glac": a.b[0],
            "b_ctrl": a.b[1],
            "b_source": "frozen 2016-2025 (load_b_values)" if a.b_frozen else "assumed 1.0",
            "warmup_years": a.warmup_years,
            "n_dm": a.n_dm,
            "dm": G.DM,
            "m_max": G.M_MAX,
            "ref_years": G.REF_YEARS,
        },
        "scenarios": {n: G.SCENARIOS[n].description for n in names},
        "python": sys.version,
    }
    (out / f"run_{time.strftime('%Y%m%dT%H%M%S')}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=False
    )
    (out / "pip_freeze.txt").write_text(freeze.stdout, encoding="utf-8")
    order = list(G.SCENARIOS)
    tasks = []
    for n in names:
        done = _done_reps(out / f"{n}.jsonl")
        tasks += [
            (n, order.index(n), r, a.n_t1, a.n_boot, seed, *a.b, a.warmup_years, a.n_dm)
            for r in range(reps[n])
            if r not in done
        ]
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
                    print(
                        f"{k}/{len(tasks)}  {el / 60:.1f} min"
                        f"  ~{el / k * (len(tasks) - k) / 60:.0f} min left"
                        f"  peak job RAM {peak_job_mb()} MB",
                        flush=True,
                    )
    finally:
        for f in files.values():
            f.close()


# ----------------------------------------------------------------------------- precheck
def _count(task: Task) -> tuple[str, int, int]:
    name, idx, rep, _, _, seed, b_glac, b_ctrl, warmup, n_dm = task
    cfg = _cfg(10, 9, b_glac, b_ctrl, warmup, n_dm)
    s = G._seeds(seed, idx, rep, 16)
    n = [
        len(G.generate_region(_MODELS[r], G.SCENARIOS[name], cfg, s[6 * j : 6 * j + 4]).win_t)
        for j, r in enumerate(G.PRIMARY_PAIR)
    ]
    return name, n[0], n[1]


def cmd_precheck(a: argparse.Namespace) -> None:
    """Mean simulated 2026 window count vs the stationary mu e^(sigma^2/2) / (1 - n)."""
    limit_resources(a.mem_mb)
    models = load_baselines()
    names = a.scenarios.split(",")
    order = list(G.SCENARIOS)
    tasks = [
        (n, order.index(n), r, 0, 0, PILOT_SEED, *a.b, a.warmup_years, a.n_dm)
        for n in names
        for r in range(a.reps)
    ]
    counts: dict[str, list[tuple[int, int]]] = {n: [] for n in names}
    with Pool(a.workers, initializer=_init) as pool:
        for name, ng, nc in pool.imap_unordered(_count, tasks, chunksize=4):
            counts[name].append((ng, nc))
    print(f"warm-up {a.warmup_years} yr, b = {a.b}, {a.reps} reps per scenario")
    for n in names:
        arr = np.array(counts[n], float)
        for j, r in enumerate(G.PRIMARY_PAIR):
            cfg = _cfg(10, 9, *a.b, a.warmup_years, a.n_dm)
            d = G.SCENARIOS[n].data_baseline(models[r], cfg.b_for(r), a.n_dm)
            nb, _ = G.expected_cluster_moments(d, cfg.b_for(r), G.M_MAX, G.DM)
            stat = float(np.exp(d.log_mu_ref + 0.5 * d.sigma_year**2) / (1 - nb))
            m, se = arr[:, j].mean(), arr[:, j].std(ddof=1) / np.sqrt(len(arr))
            print(f"{n:24s} {r:18s} n={nb:.3f}  mean {m:7.1f} +- {se:5.1f}  stationary {stat:7.1f}"
                  f"  ratio {m / stat:.3f}")  # fmt: skip


# ----------------------------------------------------------------------------- summary
def _rows(path: Path) -> Iterator[dict[str, float]]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def cmd_summarize(a: argparse.Namespace) -> None:
    out = Path(a.out)
    summary: dict[str, dict[str, object]] = {}
    for n in G.SCENARIOS:
        p = out / f"{n}.jsonl"
        if not p.exists():
            continue
        rows = sorted(_rows(p), key=lambda r: r["rep"])
        m = len(rows)
        s: dict[str, object] = {"n_rep": m, "description": G.SCENARIOS[n].description}
        for name, fn in (
            ("gate_S", G.gate_strict),
            ("gate_L", G.gate_lenient),
            ("gate_LT3", G.gate_lenient_t3),
        ):
            k = sum(fn(r) for r in rows)
            s[name] = {"rate": k / m, "k": k, "ci95": G.wilson(k, m)}
        for key in (*G.TEST_KEYS, "T2nom_glac", "T2nom_ctrl"):
            v = np.array([float(r[key]) for r in rows])
            fin = np.isfinite(v)
            s[key] = {
                "rej_0.05": float(np.mean(v[fin] < 0.05)) if fin.any() else None,
                "rej_0.005": float(np.mean(v[fin] < 0.005)) if fin.any() else None,
                "nan": int((~fin).sum()),
            }
        s["mean_n_win"] = {
            "glac": float(np.mean([r["n_win_glac"] for r in rows])),
            "ctrl": float(np.mean([r["n_win_ctrl"] for r in rows])),
        }
        s["mean_seconds"] = float(np.mean([r["seconds"] for r in rows]))
        summary[n] = s
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    hdr = "| scenario | reps | gate S | gate L | gate L+T3 | " + " | ".join(G.TEST_KEYS) + " |"
    print(hdr)
    print("|" + "---|" * (5 + len(G.TEST_KEYS)))
    for n, s in summary.items():
        gs, gl, g3 = s["gate_S"], s["gate_L"], s["gate_LT3"]
        cells = [f"{s[k]['rej_0.05']:.3f}" if s[k]["rej_0.05"] is not None else "-"
                 for k in G.TEST_KEYS]  # type: ignore[index]  # fmt: skip
        print(
            f"| {n} | {s['n_rep']} | {gs['rate']:.3f} [{gs['ci95'][0]:.3f}, {gs['ci95'][1]:.3f}]"  # type: ignore[index]
            f" | {gl['rate']:.3f} [{gl['ci95'][0]:.3f}, {gl['ci95'][1]:.3f}]"  # type: ignore[index]
            f" | {g3['rate']:.3f} [{g3['ci95'][0]:.3f}, {g3['ci95'][1]:.3f}] | "  # type: ignore[index]
            + " | ".join(cells)
            + " |"
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--scenarios", default=",".join(G.SCENARIOS))
    r.add_argument("--reps-null", type=int, default=1000)
    r.add_argument("--reps-alt", type=int, default=200)
    r.add_argument("--n-t1", type=int, default=1000)
    r.add_argument("--n-boot", type=int, default=399)
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--mem-mb", type=int, default=2048)
    r.add_argument("--seed", type=int, default=DEFAULT_SEED)
    r.add_argument("--progress", type=int, default=10)
    r.add_argument("--pilot", action="store_true", help="probe run with a separate seed")
    r.add_argument("--warmup-years", type=float, default=2.0)
    r.add_argument("--b-frozen", action="store_true", help="use the frozen 2016-2025 b-values")
    r.add_argument("--n-dm", type=float, default=0.0, help="bin width for analytic n (AP4b: 0.1)")
    c = sub.add_parser("precheck", help="window counts only (no tests) vs stationary rate")
    c.add_argument("--scenarios", default="null,cluster_plus,cluster_plus_same_rate")
    c.add_argument("--reps", type=int, default=200)
    c.add_argument("--warmup-years", type=float, default=20.0)
    c.add_argument("--b-frozen", action="store_true")
    c.add_argument("--n-dm", type=float, default=0.0)
    c.add_argument("--workers", type=int, default=2)
    c.add_argument("--mem-mb", type=int, default=2048)
    s = sub.add_parser("summarize")
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd in ("run", "precheck"):
        b = load_b_values() if a.b_frozen else None
        a.b = (b[G.GLACIER], b[G.CONTROL]) if b else (G.B_VALUE, G.B_VALUE)
    {"run": cmd_run, "summarize": cmd_summarize, "precheck": cmd_precheck}[a.cmd](a)


if __name__ == "__main__":
    main()
