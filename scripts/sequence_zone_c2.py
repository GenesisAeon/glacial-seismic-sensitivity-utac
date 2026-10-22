"""AP6c: C2 robustness check without the epicentral zone of the 2025-12-06 M6.8 (synthetic).

Usage (from the repository root):

    python scripts/sequence_zone_c2.py calibrate   # -> results/adequacy/sequence_zone/zone.json
    python scripts/sequence_zone_c2.py run --out results/adequacy/sequence_zone/<run_id> [--pilot]
    python scripts/sequence_zone_c2.py summarize --out ...

Radius rule (protocol): R = 95 % quantile of the epicentral distances of the sequence events
>= Mc on days 2 to the end of 2025 (frozen snapshot only), rounded up to the next 5 km.
The reduced baseline uses the frozen 2016-2025 snapshot only. Real 2026 events (AP6 snapshot,
SHA-checked) get their real zone label.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adequacy_gate_power import _done_reps, _git_commit, limit_resources, peak_job_mb  # noqa: E402
from sequence_term_c2 import CUTOFF, GLACIER, SNAP_2026, _wilson  # noqa: E402
from sequence_term_c2 import OUT as AP6  # noqa: E402

from glacial_seismic_sensitivity_utac import config as C  # noqa: E402
from glacial_seismic_sensitivity_utac.catalog import haversine_km, prepare  # noqa: E402
from glacial_seismic_sensitivity_utac.confirmatory_v02 import LOOKS  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import zone_check as Z  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values  # noqa: E402
from glacial_seismic_sensitivity_utac.quiescence import decimal_year  # noqa: E402

OUT = Path("results/adequacy/sequence_zone")
LEVEL_CALIB = Path("results/adequacy/sequence_level/calib.json")
SNAP_2025 = Path("results/adequacy/b_value/comcat_ak_SE_Alaska_AK_2016_2025.csv.gz")
DEFAULT_SEED = 20261026
PILOT_SEED = 995
CONFIRM_B = 0.05  # candidate B confirmation level (one-sided p of the reduced statistic)


def _prep(path: Path) -> pd.DataFrame:
    base = load_baselines()[GLACIER]
    p = prepare(pd.read_csv(path), C.REGIONS[GLACIER])
    return p[p.mag >= base.mc_ref - 1e-9].reset_index(drop=True)


def cmd_calibrate(_: argparse.Namespace) -> None:
    base = load_baselines()[GLACIER]
    old = _prep(SNAP_2025)
    if (old.time >= pd.Timestamp("2026-01-01", tz="UTC")).any():
        raise SystemExit("frozen snapshot contains 2026 events: refusing")
    dec = old[old.time >= pd.Timestamp("2025-12-01", tz="UTC")]
    ms = dec.loc[dec.mag.idxmax()]
    lat0, lon0 = float(ms.latitude), float(ms.longitude)
    d = haversine_km(old.latitude.to_numpy(), old.longitude.to_numpy(), lat0, lon0)
    seq = (old.time >= ms.time + pd.Timedelta(days=2)).to_numpy()
    q95 = float(np.quantile(d[seq], 0.95))
    r_km = 5.0 * math.ceil(q95 / 5.0)
    t = decimal_year(old.time)
    m = old.mag.to_numpy(float)
    outside = d >= r_km
    red, ly = Z.reduced_baseline(t, m, outside, base)
    # real 2026 events (AP6 snapshot) with their zone labels
    meta = json.loads((AP6 / "snapshot_2026.json").read_text(encoding="utf-8"))
    if hashlib.sha256(SNAP_2026.read_bytes()).hexdigest() != meta["snapshot_sha256_gz"]:
        raise SystemExit("2026 snapshot does not match its recorded SHA-256")
    new = _prep(SNAP_2026)
    new = new[new.time < pd.Timestamp(CUTOFF, tz="UTC")]
    d26 = haversine_km(new.latitude.to_numpy(), new.longitude.to_numpy(), lat0, lon0)
    lev = json.loads(LEVEL_CALIB.read_text(encoding="utf-8"))
    out = {
        "description": "AP6c zone calibration (radius rule, reduced baseline, 2026 zone labels)",
        "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git_commit(),
        "epicentre": {"lat": lat0, "lon": lon0, "time": str(ms.time), "mag": float(ms.mag)},
        "seq_distance_q95_km": q95, "radius_km": r_km,
        "share_2016_nov2025_inside": float(
            (d[old.time < pd.Timestamp("2025-12-01", tz="UTC")] < r_km).mean()),
        "share_2026_inside": float((d26 < r_km).mean()),
        "reduced_baseline": {"log_mu_ref": red.log_mu_ref, "sigma_year": red.sigma_year,
                             "n_ref_years": red.n_ref_years},
        "full_baseline": {"log_mu_ref": base.log_mu_ref, "sigma_year": base.sigma_year},
        "yearly_log_mu": ly,
        "t_ms": lev["t_ms"], "cutoff": lev["cutoff"], "spike_A": lev["spike_A"],
        "spike_q": lev["spike_q"], "mag_values": lev["mag_values"],
        "mag_counts": lev["mag_counts"],
        "real_t": decimal_year(new.time).tolist(), "real_m": new.mag.tolist(),
        "real_in_zone": (d26 < r_km).tolist(),
    }  # fmt: skip
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "zone.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    keep = ("seq_distance_q95_km", "radius_km", "share_2016_nov2025_inside", "share_2026_inside",
            "reduced_baseline", "full_baseline")  # fmt: skip
    print(json.dumps({k: out[k] for k in keep}, indent=1))


_CTX: dict[str, object] = {}


def _init() -> None:
    import dataclasses

    models = dict(load_baselines())
    z = json.loads((OUT / "zone.json").read_text(encoding="utf-8"))
    rb = z["reduced_baseline"]
    _CTX["models"] = models
    _CTX["reduced"] = dataclasses.replace(models[GLACIER], log_mu_ref=rb["log_mu_ref"],
                                          sigma_year=rb["sigma_year"])  # fmt: skip
    _CTX["b"] = load_b_values()
    _CTX["ctx"] = z


def _work(task: tuple[str, int, int, int, float, str]) -> dict[str, object]:
    name, idx, rep, seed, warmup, gen = task
    return Z.run_zone_replicate(
        _CTX["models"], _CTX["reduced"], _CTX["b"], _CTX["ctx"],  # type: ignore[arg-type]
        Z.ZONE_SCENARIOS[name], idx, rep, seed, warmup_years=warmup, generator=gen,
    )  # fmt: skip


def cmd_run(a: argparse.Namespace) -> None:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = limit_resources(a.mem_mb)
    seed = PILOT_SEED if a.pilot else a.seed
    names = a.scenarios.split(",")
    meta = {"started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "commit": _git_commit(),
            "pilot": a.pilot, "seed": seed, "reps": a.reps, "workers": a.workers,
            "warmup_years": a.warmup_years, "generator": a.generator, "resources": res,
            "python": sys.version}  # fmt: skip
    (out / f"run_{time.strftime('%Y%m%dT%H%M%S')}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    order = list(Z.ZONE_SCENARIOS)
    tasks = []
    for n in names:
        done = _done_reps(out / f"{n}.jsonl")
        tasks += [(n, order.index(n), r, seed, a.warmup_years, a.generator)
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
    alpha = {f"{int(e) - 1}": al for e, al in LOOKS}
    summary: dict[str, object] = {}
    print("| scenario | reps | look | full rejects | confirmed A (p_red < alpha) "
          "| confirmed B (p_red < 0.05) | D full | D red |")  # fmt: skip
    print("|---|---:|---|---|---|---|---:|---:|")
    for n in Z.ZONE_SCENARIOS:
        path = out / f"{n}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        if not rows:
            continue
        m = len(rows)
        s: dict[str, object] = {"n_rep": m}
        for tag, al in alpha.items():
            full = [bool(r[f"reject_full_{tag}"]) for r in rows]
            ca = [f and r[f"p_red_{tag}"] < al for f, r in zip(full, rows, strict=True)]
            cb = [f and r[f"p_red_{tag}"] < CONFIRM_B for f, r in zip(full, rows, strict=True)]
            cell = {}
            for key, v in (("full", full), ("A", ca), ("B", cb)):
                k = int(sum(v))
                cell[key] = {"rate": k / m, "k": k, "ci95": _wilson(k, m)}
            cell["D_full"] = float(np.mean([r[f"D_full_{tag}"] for r in rows]))
            cell["D_red"] = float(np.mean([r[f"D_red_{tag}"] for r in rows]))
            s[tag] = cell
            f3 = [f"{cell[x]['rate']:.3f} [{cell[x]['ci95'][0]:.3f}, {cell[x]['ci95'][1]:.3f}]"
                  for x in ("full", "A", "B")]  # type: ignore[index]  # fmt: skip
            print(f"| {n} | {m} | {tag} | {f3[0]} | {f3[1]} | {f3[2]} "
                  f"| {cell['D_full']:+.3f} | {cell['D_red']:+.3f} |")  # fmt: skip
        summary[n] = s
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("calibrate")
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--scenarios", default=",".join(Z.ZONE_SCENARIOS))
    r.add_argument("--reps", type=int, default=400)
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--mem-mb", type=int, default=2500)
    r.add_argument("--seed", type=int, default=DEFAULT_SEED)
    r.add_argument("--warmup-years", type=float, default=20.0)
    r.add_argument("--progress", type=int, default=200)
    r.add_argument("--pilot", action="store_true")
    r.add_argument("--generator", choices=("labels", "separate"), default="labels")
    s = sub.add_parser("summarize")
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    {"calibrate": cmd_calibrate, "run": cmd_run, "summarize": cmd_summarize}[a.cmd](a)


if __name__ == "__main__":
    main()
