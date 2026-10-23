"""AP6: C2 with a frozen Omori term for the 2025-12-06 sequence (fit on 2026 data).

Usage (from the repository root):

    python scripts/sequence_term_c2.py fetch      # 2026 glacier-region snapshot (SHA-256)
    python scripts/sequence_term_c2.py fit        # term fit on [2026-01-01, CUTOFF)
    python scripts/sequence_term_c2.py run --out results/adequacy/sequence_term/<run_id> [--pilot]
    python scripts/sequence_term_c2.py summarize --out ...

``fetch`` downloads ComCat (catalog=ak) with exactly the query of ``fetch.catalogs.fetch_comcat``
for **SE_Alaska_AK only** and **only 2026-01-01 up to and excluding CUTOFF**; it aborts if any event
lies outside. No control-region data and nothing from the C2 window (2027 on) are requested.
Triggers before 2026 come from the frozen 2016-2025 snapshot. Resource limits and resumable JSONL
checkpoints as in ``adequacy_gate_power.py``.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adequacy_gate_power import _done_reps, _git_commit, limit_resources, peak_job_mb  # noqa: E402

from glacial_seismic_sensitivity_utac import config as C  # noqa: E402
from glacial_seismic_sensitivity_utac.catalog import prepare  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import load_baselines  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy import sequence_term as Q  # noqa: E402
from glacial_seismic_sensitivity_utac.etas_adequacy.frozen import load_b_values  # noqa: E402
from glacial_seismic_sensitivity_utac.fetch.catalogs import COMCAT  # noqa: E402
from glacial_seismic_sensitivity_utac.fetch.common import UNIFIED_COLUMNS, http_get  # noqa: E402
from glacial_seismic_sensitivity_utac.quiescence import decimal_year  # noqa: E402

GLACIER = "SE_Alaska_AK"
START, CUTOFF = "2026-01-01", "2026-10-22"  # CUTOFF exclusive (00:00 UTC), fixed in the protocol
OUT = Path("results/adequacy/sequence_term")
SNAP_2026 = OUT / "comcat_ak_SE_Alaska_AK_2026_to_cutoff.csv.gz"
SNAP_2025 = Path("results/adequacy/b_value/comcat_ak_SE_Alaska_AK_2016_2025.csv.gz")
CALIB_AP5 = Path("results/adequacy/sequence_tail/calibration.json")
DEFAULT_SEED = 20261024
PILOT_SEED = 997


def _months() -> list[tuple[str, str]]:
    edges = pd.date_range(START, CUTOFF, freq="MS").strftime("%Y-%m-%d").tolist()
    if edges[-1] != CUTOFF:
        edges.append(CUTOFF)
    return list(zip(edges[:-1], edges[1:], strict=True))


def cmd_fetch(_: argparse.Namespace) -> None:
    region = C.REGIONS[GLACIER]
    a, b, c, d = region.box
    frames, queries = [], []
    for s, e in _months():
        q: dict[str, object] = dict(
            format="csv", starttime=s, endtime=e, minmagnitude=region.minmag,
            eventtype="earthquake", minlatitude=a, maxlatitude=b, minlongitude=c,
            maxlongitude=d, orderby="time-asc",
        )  # fmt: skip
        if region.maxdepth is not None:
            q["maxdepth"] = region.maxdepth
        if region.source == "comcat_ak":
            q["catalog"] = "ak"
        queries.append(q)
        txt = http_get(COMCAT, q)
        if txt.strip():
            x = pd.read_csv(io.StringIO(txt))
            frames.append(pd.DataFrame({
                "time": x["time"], "latitude": x["latitude"], "longitude": x["longitude"],
                "depth": x["depth"], "mag": x["mag"], "magType": x["magType"], "id": x["id"],
                "etype": x["type"],
            }))  # fmt: skip
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=UNIFIED_COLUMNS)
    df = df.drop_duplicates("id")[UNIFIED_COLUMNS]
    t = pd.to_datetime(df["time"], format="ISO8601", utc=True)
    if len(df) and (t.min() < pd.Timestamp(START, tz="UTC")
                    or t.max() >= pd.Timestamp(CUTOFF, tz="UTC")):  # fmt: skip
        raise SystemExit(f"ABORT: events outside [{START}, {CUTOFF})")
    df = df.sort_values("time").reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    raw = df.to_csv(index=False, lineterminator="\n").encode("utf-8")
    with gzip.GzipFile(SNAP_2026, "wb", mtime=0) as f:  # mtime 0: reproducible bytes
        f.write(raw)
    meta = {
        "purpose": "AP6: fit of the 2025-12-06 sequence term on 2026 data (Johann, 2026-10-22)",
        "region": GLACIER,
        "period": {"start": START, "stop_exclusive": CUTOFF},
        "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit": _git_commit(),
        "n_rows": len(df),
        "snapshot": SNAP_2026.name,
        "snapshot_sha256_gz": hashlib.sha256(SNAP_2026.read_bytes()).hexdigest(),
        "snapshot_sha256_csv": hashlib.sha256(raw).hexdigest(),
        "queries": queries,
    }
    (OUT / "snapshot_2026.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("n_rows", "snapshot_sha256_gz")}))


def _glacier_events() -> tuple[np.ndarray, np.ndarray, float]:
    base = load_baselines()[GLACIER]
    meta = json.loads((OUT / "snapshot_2026.json").read_text(encoding="utf-8"))
    if hashlib.sha256(SNAP_2026.read_bytes()).hexdigest() != meta["snapshot_sha256_gz"]:
        raise SystemExit("2026 snapshot does not match its recorded SHA-256")
    old = pd.read_csv(SNAP_2025)
    new = pd.read_csv(SNAP_2026)
    p = prepare(pd.concat([old, new], ignore_index=True).drop_duplicates("id"),
                C.REGIONS[GLACIER])  # fmt: skip
    p = p[(p.mag >= base.mc_ref - 1e-9) & (p.time >= pd.Timestamp("2025-01-01", tz="UTC"))]
    if (p.time >= pd.Timestamp(CUTOFF, tz="UTC")).any():
        raise SystemExit("events at or after CUTOFF: refusing")
    cut = float(decimal_year(pd.Series([pd.Timestamp(CUTOFF, tz="UTC")]))[0])
    return decimal_year(p.time), p.mag.to_numpy(float), cut


def cmd_fit(_: argparse.Namespace) -> None:
    base = load_baselines()[GLACIER]
    calib = json.loads(CALIB_AP5.read_text(encoding="utf-8"))
    t, m, cut = _glacier_events()
    t_ms = float(calib["t_mainshock"])
    f = Q.fit_sequence_term(t, m, base, t_ms, 2026.0, cut)
    dec = (t >= t_ms) & (t < 2026.0)
    n26 = int(((t >= 2026.0) & (t < cut)).sum())
    out = {
        "description": "AP6 fit of S(t) = A (t - t_ms)^(-q) with frozen triggering, mu nuisance",
        "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "commit": _git_commit(),
        "t_ms": t_ms, "cutoff": cut, "fit_window": list(f.window), "n_fit": f.n,
        "log_A": f.log_A, "A_per_yr": f.A, "q": f.q,
        "se_log_A": float(np.sqrt(f.cov[0][0])), "se_q": float(np.sqrt(f.cov[1][1])),
        "cov_logA_q": [list(r) for r in f.cov], "log_mu_2026": f.log_mu,
        "mu_2026_per_yr": float(np.exp(f.log_mu)), "log_mu_ref": base.log_mu_ref,
        "n_events_2026_to_cutoff": n26,
        "ap5_reference": {"p_hat_days_2_25": calib["p_hat_days_2_25"],
                          "p_hat_2017_analog": calib["analog_2017"]["p_hat"]},
        "dec_t": t[dec].tolist(), "dec_m": m[dec].tolist(),
        "mag_values": calib["mag_values"], "mag_counts": calib["mag_counts"],
    }  # fmt: skip
    for end in (2030.0, 2037.0):
        from glacial_seismic_sensitivity_utac.etas_adequacy.sequence_tail import omori_integral

        out[f"expected_term_events_2027_{int(end) - 1}"] = f.A * omori_integral(
            2027.0 - t_ms, end - t_ms, f.q
        )
    (OUT / "term_fit.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    keep = ("n_fit", "A_per_yr", "q", "se_q", "se_log_A", "mu_2026_per_yr", "log_mu_ref",
            "expected_term_events_2027_2029", "expected_term_events_2027_2036")  # fmt: skip
    print(json.dumps({k: out[k] for k in keep}, indent=1))


# ----------------------------------------------------------------------------- run
_CTX: dict[str, object] = {}


def _init() -> None:
    _CTX["models"] = dict(load_baselines())
    _CTX["b"] = load_b_values()
    _CTX["ctx"] = json.loads((OUT / "term_fit.json").read_text(encoding="utf-8"))


def _work(task: tuple[str, int, int, int, float]) -> dict[str, object]:
    name, idx, rep, seed, warmup = task
    return Q.run_term_replicate(
        _CTX["models"], _CTX["b"], _CTX["ctx"], Q.TERM_SCENARIOS[name], idx, rep, seed,  # type: ignore[arg-type]
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
    order = list(Q.TERM_SCENARIOS)
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


def _wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    ph = k / n
    d = 1 + z**2 / n
    c = (ph + z**2 / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2)) / d
    return [float(c - h), float(c + h)]


def cmd_summarize(a: argparse.Namespace) -> None:
    out = Path(a.out)
    summary: dict[str, object] = {}
    print("| scenario | reps | q_true | q_fit (mean, sd) | variant | D 2029 | reject 2029 "
          "| D 2036 | reject 2036 |")  # fmt: skip
    print("|---|---:|---:|---|---|---:|---|---:|---|")
    for n in Q.TERM_SCENARIOS:
        path = out / f"{n}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        if not rows:
            continue
        qf = np.array([r["q_fit"] for r in rows if "q_fit" in r])
        s: dict[str, object] = {"n_rep": len(rows), "q_true": rows[0]["q_true"],
                                "q_fit_mean": float(qf.mean()), "q_fit_sd": float(qf.std(ddof=1)),
                                "fit_errors": sum("fit_error" in r for r in rows)}  # fmt: skip
        for v in ("none", "A", "B"):
            sel = [r for r in rows if f"D_{v}_2029" in r]
            m = len(sel)
            for tag in ("2029", "2036"):
                k = sum(bool(r[f"reject_{v}_{tag}"]) for r in sel)
                s[f"{v}_{tag}"] = {"D_mean": float(np.mean([r[f"D_{v}_{tag}"] for r in sel])),
                                   "reject": k / m,
                                   "k": k, "n": m, "ci95": _wilson(k, m)}  # fmt: skip
            x9, x6 = s[f"{v}_2029"], s[f"{v}_2036"]
            print(f"| {n} | {m} | {s['q_true']:.3f} | {s['q_fit_mean']:.3f}, {s['q_fit_sd']:.3f} "
                  f"| {v} | {x9['D_mean']:+.3f} | {x9['reject']:.3f} [{x9['ci95'][0]:.3f}, "  # type: ignore[index]
                  f"{x9['ci95'][1]:.3f}] | {x6['D_mean']:+.3f} | {x6['reject']:.3f} "  # type: ignore[index]
                  f"[{x6['ci95'][0]:.3f}, {x6['ci95'][1]:.3f}] |")  # type: ignore[index]  # fmt: skip
        summary[n] = s
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch")
    sub.add_parser("fit")
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--scenarios", default=",".join(Q.TERM_SCENARIOS))
    r.add_argument("--reps", type=int, default=400)
    r.add_argument("--workers", type=int, default=2)
    r.add_argument("--mem-mb", type=int, default=2500)
    r.add_argument("--seed", type=int, default=DEFAULT_SEED)
    r.add_argument("--warmup-years", type=float, default=20.0)
    r.add_argument("--progress", type=int, default=50)
    r.add_argument("--pilot", action="store_true")
    s = sub.add_parser("summarize")
    s.add_argument("--out", required=True)
    a = ap.parse_args()
    {"fetch": cmd_fetch, "fit": cmd_fit, "run": cmd_run, "summarize": cmd_summarize}[a.cmd](a)


if __name__ == "__main__":
    main()
