"""AP5: bias of C2 from the tail of the M6.8 sequence of 2025-12-06 (synthetic; data to 2025).

Usage (from the repository root):

    python scripts/sequence_tail_c2.py calibrate   # writes .../sequence_tail/calibration.json
    python scripts/sequence_tail_c2.py run --out results/adequacy/sequence_tail/<run_id> [--pilot]
    python scripts/sequence_tail_c2.py summarize --out ...

Only the frozen snapshots ``results/adequacy/b_value/comcat_ak_*_2016_2025.csv.gz`` are read;
``calibrate`` aborts if any event lies at or after 2026-01-01. Resource limits and resumable
JSONL checkpoints as in ``adequacy_gate_power.py`` (job object: memory cap, half of the logical
CPUs, below-normal priority).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import optimize  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adequacy_gate_power import _done_reps, _git_commit, limit_resources, peak_job_mb  # noqa: E402

from glacial_seismic_sensitivity_utac import config as C  # noqa: E402
from glacial_seismic_sensitivity_utac.catalog import haversine_km, prepare  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import sequence_tail as S  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values  # noqa: E402
from glacial_seismic_sensitivity_utac.quiescence import decimal_year  # noqa: E402

DEFAULT_SEED = 20261023
PILOT_SEED = 998
OUT = Path("results/adequacy/sequence_tail")
SNAP = "results/adequacy/b_value/comcat_ak_{}_2016_2025.csv.gz"
FIT_FROM_DAYS = 2.0  # completeness of the sequence at Mc 2.1 from about day 2 (mean magnitude)
P_GRID = (1.0, 1.1, 1.2, 1.3)
ANALOG_2017 = ("2017-05-01 12:31:53", 59.85, -136.68, 50.0)  # M6.2/6.3 doublet, radius km


def _events(region: str) -> pd.DataFrame:
    df = pd.read_csv(SNAP.format(region))
    p = prepare(df, C.REGIONS[region])
    if (p.time >= pd.Timestamp("2026-01-01", tz="UTC")).any():
        raise SystemExit("snapshot contains events from 2026 on: refusing (held-out data)")
    base = load_baselines()[region]
    return p[p.mag >= base.mc_ref - 1e-9].reset_index(drop=True)


def cmd_calibrate(_: argparse.Namespace) -> None:
    ev = _events(S.GLACIER)
    dec = ev[(ev.time >= pd.Timestamp("2025-12-01", tz="UTC"))]
    ms = dec.loc[dec.mag.idxmax()]
    t_ms = float(decimal_year(pd.Series([ms.time]))[0])
    t_y = decimal_year(ev.time)
    lo = float(decimal_year(pd.Series([ms.time + pd.Timedelta(days=FIT_FROM_DAYS)]))[0]) - t_ms
    hi = 2026.0 - t_ms
    x = t_y - t_ms
    sel = (x >= lo) & (x < hi)
    n = int(sel.sum())
    amp, ll = {}, {}
    for p in P_GRID:
        a = n / S.omori_integral(lo, hi, p)
        amp[f"{p:.1f}"] = a
        ll[f"{p:.1f}"] = float(-n + np.sum(np.log(a * x[sel] ** -p)))

    def nll(p: float) -> float:
        a = n / S.omori_integral(lo, hi, p)
        return float(-(-n + np.sum(np.log(a * x[sel] ** -p))))

    p_hat = float(optimize.minimize_scalar(nll, bounds=(0.5, 2.5), method="bounded").x)
    expected = {
        f"{p:.1f}": {
            "2026": amp[f"{p:.1f}"] * S.omori_integral(2026.0 - t_ms, 2027.0 - t_ms, p),
            "look_2029": amp[f"{p:.1f}"] * S.omori_integral(2027.0 - t_ms, 2030.0 - t_ms, p),
            "look_2036": amp[f"{p:.1f}"] * S.omori_integral(2027.0 - t_ms, 2037.0 - t_ms, p),
        }
        for p in P_GRID
    }
    mags = ev.mag[sel].round(1).value_counts().sort_index()

    # 2017 analog: long-term exponent of the M6.2/6.3 sequence (radius 50 km, days 2 .. 2025)
    t17 = pd.Timestamp(ANALOG_2017[0], tz="UTC")
    r = haversine_km(ev.latitude.to_numpy(), ev.longitude.to_numpy(), *ANALOG_2017[1:3])
    d17 = (ev.time - t17).dt.total_seconds().to_numpy() / 86400.0
    span = (pd.Timestamp("2026-01-01", tz="UTC") - t17).total_seconds() / 86400.0
    xs = d17[(r < ANALOG_2017[3]) & (d17 >= FIT_FROM_DAYS) & (d17 < span)]

    def nll17(v: np.ndarray) -> float:
        p, la, lb = float(v[0]), float(v[1]), float(v[2])
        a, bg = np.exp(la), np.exp(lb)
        lam = a * xs**-p + bg
        return float(-(np.sum(np.log(lam)) - a * S.omori_integral(FIT_FROM_DAYS, span, p)
                       - bg * (span - FIT_FROM_DAYS)))  # fmt: skip

    f17 = optimize.minimize(nll17, [1.1, np.log(100.0), np.log(0.003)], method="Nelder-Mead",
                            options={"xatol": 1e-6, "fatol": 1e-6, "maxiter": 4000})  # fmt: skip
    out = {
        "description": "AP5 calibration of the empirical Omori tail of the 2025-12-06 sequence "
        "(SE_Alaska_AK, events >= Mc, snapshots up to 2025-12-31 only)",
        "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git_commit(),
        "mainshock": {
            "time": str(ms.time),
            "mag": float(ms.mag),
            "lat": float(ms.latitude),
            "lon": float(ms.longitude),
        },  # fmt: skip
        "t_mainshock": t_ms,
        "fit_window_yr_since_mainshock": [lo, hi],
        "fit_window_days": [FIT_FROM_DAYS, hi * 365.0],
        "n_fit": n,
        "amp_per_yr": amp,
        "loglik": ll,
        "p_hat_days_2_25": p_hat,
        "expected_injected": expected,
        "mag_values": [float(v) for v in mags.index],
        "mag_counts": [int(c) for c in mags.to_numpy()],
        "mean_mag_fit": float(ev.mag[sel].mean()),
        "analog_2017": {
            "mainshock": ANALOG_2017[0],
            "radius_km": ANALOG_2017[3],
            "n": int(len(xs)),
            "p_hat": float(f17.x[0]),
            "background_per_day": float(np.exp(f17.x[2])),
        },  # fmt: skip
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "calibration.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    keys = ("mainshock", "n_fit", "p_hat_days_2_25", "expected_injected", "analog_2017")
    print(json.dumps({k: out[k] for k in keys}, indent=1))


# ----------------------------------------------------------------------------- run
_CTX: dict[str, object] = {}


def _init() -> None:
    _CTX["models"] = load_baselines()
    _CTX["b"] = load_b_values()
    _CTX["calib"] = json.loads((OUT / "calibration.json").read_text(encoding="utf-8"))


def _work(task: tuple[str, int, int, int, float]) -> dict[str, object]:
    name, idx, rep, seed, warmup = task
    return S.run_replicate(
        _CTX["models"], _CTX["b"], _CTX["calib"], S.SCENARIOS[name], idx, rep, seed,  # type: ignore[arg-type]
        warmup_years=warmup,
    )  # fmt: skip


def cmd_run(a: argparse.Namespace) -> None:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = limit_resources(a.mem_mb)
    seed = PILOT_SEED if a.pilot else a.seed
    names = a.scenarios.split(",")
    meta = {
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git_commit(),
        "pilot": a.pilot,
        "seed": seed,
        "reps": a.reps,
        "workers": a.workers,
        "warmup_years": a.warmup_years,
        "resources": res,
        "python": sys.version,
    }
    (out / f"run_{time.strftime('%Y%m%dT%H%M%S')}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    order = list(S.SCENARIOS)
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
                    print(
                        f"{k}/{len(tasks)}  {el / 60:.1f} min  ~{left:.0f} min left"
                        f"  peak job RAM {peak_job_mb()} MB",
                        flush=True,
                    )
    finally:
        for f in files.values():
            f.close()


def _wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    ph = k / n
    d = 1 + z**2 / n
    c = (ph + z**2 / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2)) / d
    return [float(c - h), float(c + h)]


def _rate(r: dict[str, object]) -> str:
    lo, hi = r["ci95"]  # type: ignore[misc]
    return f"{r['rate']:.3f} [{lo:.3f}, {hi:.3f}]"


def cmd_summarize(a: argparse.Namespace) -> None:
    out = Path(a.out)
    summary: dict[str, object] = {}
    for n in S.SCENARIOS:
        path = out / f"{n}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        if not rows:
            continue
        m = len(rows)
        s: dict[str, object] = {"n_rep": m}
        for tag in ("2029", "2036"):
            k = sum(bool(r[f"reject_{tag}"]) for r in rows)
            dv = np.array([r[f"D_{tag}"] for r in rows])
            s[tag] = {
                "reject": {"rate": k / m, "k": k, "ci95": _wilson(k, m)},
                "D_mean": float(dv.mean()), "D_sd": float(dv.std(ddof=1)),
                "z_mean": float(np.mean([r[f"z_{tag}"] for r in rows])),
                "dlog_glac_mean": float(np.mean([r[f"dlog_glac_{tag}"] for r in rows])),
                "dlog_ctrl_mean": float(np.mean([r[f"dlog_ctrl_{tag}"] for r in rows])),
                "n_glac_mean": float(np.mean([r[f"n_glac_{tag}"] for r in rows])),
                "n_injected_mean": float(np.mean([r[f"n_injected_{tag}"] for r in rows])),
            }  # fmt: skip
        either = sum(bool(r["reject_2029"]) or bool(r["reject_2036"]) for r in rows)
        s["reject_either"] = {"rate": either / m, "k": either, "ci95": _wilson(either, m)}
        s["mean_seconds"] = float(np.mean([r["seconds"] for r in rows]))
        summary[n] = s
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        "| scenario | reps | inj. 2027-29 | D 2029 | reject 2029 (a=0.01)"
        " | inj. 2027-36 | D 2036 | reject 2036 (a=0.04) | reject either |"
    )
    print("|---|---:|---:|---:|---|---:|---:|---|---|")
    for n, s in summary.items():
        a9, a6, e = s["2029"], s["2036"], s["reject_either"]  # type: ignore[index]
        print(
            f"| {n} | {s['n_rep']} | {a9['n_injected_mean']:.0f} | {a9['D_mean']:+.3f}"  # type: ignore[index]
            f" | {_rate(a9['reject'])} | {a6['n_injected_mean']:.0f} | {a6['D_mean']:+.3f}"  # type: ignore[index]
            f" | {_rate(a6['reject'])} | {_rate(e)} |"  # type: ignore[index]
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("calibrate")
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--scenarios", default=",".join(S.SCENARIOS))
    r.add_argument("--reps", type=int, default=400)
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--mem-mb", type=int, default=2500)
    r.add_argument("--seed", type=int, default=DEFAULT_SEED)
    r.add_argument("--warmup-years", type=float, default=20.0)
    r.add_argument("--progress", type=int, default=20)
    r.add_argument("--pilot", action="store_true", help="probe run with a separate seed")
    s = sub.add_parser("summarize")
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    {"calibrate": cmd_calibrate, "run": cmd_run, "summarize": cmd_summarize}[a.cmd](a)


if __name__ == "__main__":
    main()
