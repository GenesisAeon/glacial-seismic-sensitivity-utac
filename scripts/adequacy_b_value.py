"""b-value of the primary pair from 2016-2025, to be frozen before any look at 2026 data.

Usage (from the repository root):

    python scripts/adequacy_b_value.py --out results/adequacy/b_value

Downloads ComCat (catalog=ak) with exactly the query of ``fetch.catalogs.fetch_comcat`` (box,
max depth, min magnitude of the frozen region definition), but **only for 2016-01-01 up to and
excluding 2026-01-01**. If any returned event lies at or after 2026-01-01 the script aborts
before anything is written or evaluated. Magnitudes are prepared with ``catalog.prepare`` and the
b-value is ``catalog.b_value`` (Aki 1965 maximum likelihood with Utsu binning correction,
Shi & Bolt 1982 uncertainty) above the frozen Mc_ref, i.e. the same functions the frozen v0.2
pipeline uses. The branching ratio of each frozen baseline is then recomputed with that b.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac.catalog import b_value, prepare
from glacial_seismic_sensitivity_utac.etas_adequacy import PRIMARY_PAIR, load_baselines
from glacial_seismic_sensitivity_utac.etas_adequacy.forecast import expected_cluster_moments
from glacial_seismic_sensitivity_utac.fetch.catalogs import COMCAT
from glacial_seismic_sensitivity_utac.fetch.common import UNIFIED_COLUMNS, http_get

START, STOP = "2016-01-01", "2026-01-01"  # STOP exclusive
M_MAX = 8.0


def _chunks() -> list[tuple[str, str]]:
    out = []
    for y in range(2016, 2026):
        out.append((f"{y}-01-01", f"{y}-07-01"))
        out.append((f"{y}-07-01", f"{y}-12-31T23:59:59.999" if y == 2025 else f"{y + 1}-01-01"))
    return out


def fetch(region: C.Region) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    a, b, c, d = region.box
    frames, queries = [], []
    for s, e in _chunks():
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
            frames.append(
                pd.DataFrame(
                    {
                        "time": x["time"],
                        "latitude": x["latitude"],
                        "longitude": x["longitude"],
                        "depth": x["depth"],
                        "mag": x["mag"],
                        "magType": x["magType"],
                        "id": x["id"],
                        "etype": x["type"],
                    }
                )  # fmt: skip
            )
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=UNIFIED_COLUMNS)
    df = df.drop_duplicates("id")[UNIFIED_COLUMNS]
    t = pd.to_datetime(df["time"], format="ISO8601", utc=True)
    if len(df) and (
        t.max() >= pd.Timestamp(STOP, tz="UTC") or t.min() < pd.Timestamp(START, tz="UTC")
    ):
        raise SystemExit(f"ABORT: {region.name} returned events outside [{START}, {STOP})")
    return df.sort_values("time").reset_index(drop=True), queries


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    models = load_baselines()
    result: dict[str, object] = {
        "purpose": "b-value for P133 etas_adequacy (draft A8), frozen before any look at 2026",
        "period": {"start": START, "stop_exclusive": STOP},
        "retrieved_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": COMCAT,
        "method": "catalog.prepare + catalog.b_value (Aki-Utsu ML, Shi-Bolt) at frozen Mc_ref",
        "data_2026_or_later_retrieved": False,
        "code_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
        ).stdout.strip(),
        "python": sys.version.split()[0],
        "regions": {},
    }
    for name in PRIMARY_PAIR:
        region, model = C.REGIONS[name], models[name]
        df, queries = fetch(region)
        raw = df.to_csv(index=False, lineterminator="\n").encode("utf-8")
        snap = out / f"comcat_ak_{name}_2016_2025.csv.gz"
        with gzip.GzipFile(snap, "wb", mtime=0) as f:  # mtime 0: reproducible bytes
            f.write(raw)
        p = prepare(df, region)
        p = p[(p.time >= pd.Timestamp(START, tz="UTC")) & (p.time < pd.Timestamp(STOP, tz="UTC"))]
        b, sb, n = b_value(p.mag.to_numpy(), model.mc_ref)
        n_b1, _ = expected_cluster_moments(model, 1.0, M_MAX)
        n_b, _ = expected_cluster_moments(model, b, M_MAX) if model.alpha < b * 2.302585 else (
            float("inf"), 0.0)  # fmt: skip
        result["regions"][name] = {  # type: ignore[index]
            "mc_ref": model.mc_ref,
            "b": b,
            "b_sigma_shi_bolt": sb,
            "n_events_ge_mc": n,
            "n_events_downloaded": len(df),
            "first_event": str(p.time.min()),
            "last_event": str(p.time.max()),
            "snapshot": snap.name,
            "snapshot_sha256_gz": hashlib.sha256(snap.read_bytes()).hexdigest(),
            "snapshot_sha256_csv": hashlib.sha256(raw).hexdigest(),
            "queries": queries,
            "alpha": model.alpha,
            "branching_ratio_b1": n_b1,
            "branching_ratio_b_hat": n_b,
            "subcritical_at_b_hat": bool(n_b < 1.0),
        }
        print(f"{name}: N>=Mc {n}, b = {b:.3f} +- {sb:.3f}, n(b=1) {n_b1:.3f} -> n(b) {n_b:.3f}",
              flush=True)  # fmt: skip
    (out / "b_value_2016_2025.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
