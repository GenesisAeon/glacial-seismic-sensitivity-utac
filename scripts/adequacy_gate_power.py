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


def _work(task: tuple[str, int, int, int, int, int]) -> dict[str, float | int | str]:
    name, idx, rep, n_t1, n_boot, seed = task
    cfg = G.SimConfig(n_t1=n_t1, n_boot=n_boot)
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
        "assumptions": {"b": G.B_VALUE, "dm": G.DM, "m_max": G.M_MAX, "ref_years": G.REF_YEARS},
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
            (n, order.index(n), r, a.n_t1, a.n_boot, seed) for r in range(reps[n]) if r not in done
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
        for name, fn in (("gate_S", G.gate_strict), ("gate_L", G.gate_lenient)):
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
    hdr = "| scenario | reps | gate S | gate L | " + " | ".join(G.TEST_KEYS) + " |"
    print(hdr)
    print("|" + "---|" * (4 + len(G.TEST_KEYS)))
    for n, s in summary.items():
        gs, gl = s["gate_S"], s["gate_L"]
        cells = [f"{s[k]['rej_0.05']:.3f}" if s[k]["rej_0.05"] is not None else "-"
                 for k in G.TEST_KEYS]  # type: ignore[index]  # fmt: skip
        print(
            f"| {n} | {s['n_rep']} | {gs['rate']:.3f} [{gs['ci95'][0]:.3f}, {gs['ci95'][1]:.3f}]"  # type: ignore[index]
            f" | {gl['rate']:.3f} [{gl['ci95'][0]:.3f}, {gl['ci95'][1]:.3f}] | "  # type: ignore[index]
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
    s = sub.add_parser("summarize")
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    cmd_run(a) if a.cmd == "run" else cmd_summarize(a)


if __name__ == "__main__":
    main()
