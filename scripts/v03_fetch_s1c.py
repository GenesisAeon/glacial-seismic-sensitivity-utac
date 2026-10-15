"""v0.3 S1c: snapshots for S0 amendment A1 and for magnitude/network-matched negatives.

Design (fixed before any download, approved 2026-10-11):
  * A1 cases: catalogue queries from v03_cases.CASES_A1; event details for Kilauea M>=4.5
    within 15 km, 2018-05-01..2018-08-06 (key events and their cluster members).
  * Matched negatives: ComCat 'earthquake', 2.0 <= M <= 4.5, from the same contributing
    networks as the S2b positives (ak, us, nc, se, uu, nm), 2025-01-01 .. 2026-10-01 (data end).
    Per network a random sample of at most N_PER_NET events (numpy default_rng(SEED), without
    replacement); for each: event detail and a 30 km / -400 d .. +400 d neighbourhood catalogue
    (end capped at 2026-10-01), i.e. the same neighbourhood definition as for the positives.
Appends to results/v03/MANIFEST_v03.sha256 and s1_snapshots.json.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v03_fetch as S  # noqa: E402
import v03_fetch_validation as SV  # noqa: E402

from glacial_seismic_sensitivity_utac import v03_cases as V  # noqa: E402
from glacial_seismic_sensitivity_utac.catalog import haversine_km  # noqa: E402

NETS = ("ak", "us", "nc", "se", "uu", "nm")
N_PER_NET = 150
SEED = 20261011
WINDOWS = (
    ("2025-01-01", "2025-04-01"),
    ("2025-04-01", "2025-07-01"),
    ("2025-07-01", "2025-10-01"),
    ("2025-10-01", "2026-01-01"),
    ("2026-01-01", "2026-04-01"),
    ("2026-04-01", "2026-07-01"),
    ("2026-07-01", "2026-10-01"),
)
DATA_END = pd.Timestamp("2026-10-01")


def a1() -> None:
    for c in V.CASES_A1:
        for q in c.queries:
            SV.fetch_csv(f"{q.name}.csv", S.url_for(q))
    k = pd.read_csv(S.RAW / "kilauea_comcat.csv", parse_dates=["time"])
    sel = (
        (k.mag >= 4.5)
        & (k.time >= "2018-05-01")
        & (k.time < "2018-08-07")
        & (haversine_km(k.latitude, k.longitude, 19.405, -155.28) <= 15.0)
    )
    print("kilauea key events:", int(sel.sum()))
    for eid in k.loc[sel, "id"]:
        SV.detail(eid)


def sample_negatives() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    out = []
    for net in NETS:
        parts = [
            SV.fetch_csv(
                f"neg_list_{net}_{a}.csv",
                SV.q(
                    starttime=a,
                    endtime=b,
                    minmagnitude=2.0,
                    maxmagnitude=4.5,
                    eventtype="earthquake",
                    catalog=net,
                ),
            )
            for a, b in WINDOWS
        ]
        d = pd.concat(parts, ignore_index=True).drop_duplicates("id")
        d = d[d.mag.between(2.0, 4.5)].sort_values("id").reset_index(drop=True)
        n = min(N_PER_NET, len(d))
        idx = np.sort(rng.choice(len(d), size=n, replace=False))
        out.append(d.iloc[idx].assign(sample_net=net))
        print(net, len(d), "->", n)
    return pd.concat(out, ignore_index=True)


def main() -> int:
    (S.RAW / "neg_nb").mkdir(parents=True, exist_ok=True)
    try:
        a1()
        neg = sample_negatives()
        path = S.RAW / "neg_matched_sample.csv"
        body = neg.to_csv(index=False).encode("utf-8")
        S.save(
            "neg_matched_sample.csv", f"derived: seed {SEED}, n<= {N_PER_NET}/net", body, len(neg)
        )
        assert path.exists()
        for r in neg.itertuples():
            t = pd.Timestamp(r.time).tz_localize(None)
            end = min(t + pd.Timedelta(days=400), DATA_END)
            p = dict(
                latitude=r.latitude,
                longitude=r.longitude,
                maxradiuskm=30,
                starttime=(t - pd.Timedelta(days=400)).strftime("%Y-%m-%d"),
                endtime=end.strftime("%Y-%m-%dT%H:%M:%S"),
            )
            try:
                SV.fetch_csv(f"neg_nb/{r.id}.csv", SV.q(**p))
            except requests.HTTPError:
                # > 20000 rows (e.g. The Geysers): restrict to M >= mag - 2, which keeps every
                # event the S2 features/rules use (larger-preceding, M>=4.5 cluster, n >= m-2,
                # Bath dm); recorded in the URL in s1_snapshots.json
                SV.fetch_csv(
                    f"neg_nb/{r.id}.csv",
                    SV.q(**p, minmagnitude=round(float(r.mag) - 2.0, 2)),
                )
            SV.detail(r.id)
    finally:
        S.write_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
