"""v0.3 S1b: snapshots for the pre-freeze retrospective check of the S2 discriminator.

Positives: every ComCat event typed 'landslide', 'mine collapse' or 'collapse' (2000-01-01 to
the S1 end date), outside the S0 case areas, with its event detail and a 30 km / +-400 d
neighbourhood catalogue.  Negatives: every ComCat 'earthquake' M>=5.0, depth <= 40 km, in
calendar year 2025 (global), with event detail; neighbourhood from a global M>=4.5 catalogue
2024-06-01..2026-07-01; details of cluster members only where the R4 count can reach 10.

Appends to results/v03/MANIFEST_v03.sha256 and s1_snapshots.json (same format as S1).
Thresholds are NOT re-tuned on these data.
"""

from __future__ import annotations

import sys
import urllib.parse
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import v03_fetch as S  # noqa: E402

from glacial_seismic_sensitivity_utac import v03_cases as V  # noqa: E402
from glacial_seismic_sensitivity_utac import v03_features as F  # noqa: E402
from glacial_seismic_sensitivity_utac.catalog import haversine_km  # noqa: E402

LABELS = ("landslide", "mine collapse", "collapse")
NEG_START, NEG_END = "2025-01-01", "2026-01-01"
GLOBAL_WINDOWS = (
    ("2024-06-01", "2025-04-01"),
    ("2025-04-01", "2026-01-01"),
    ("2026-01-01", "2026-07-01"),
)


def q(**p: object) -> str:
    return S.COMCAT + "?" + urllib.parse.urlencode({"format": "csv", "orderby": "time-asc", **p})


def fetch_csv(name: str, url: str) -> pd.DataFrame:
    p = S.RAW / name
    if p.exists():
        return pd.read_csv(p)
    body = S.get(url)
    n = S.n_rows(body)
    if n >= 19999:
        raise RuntimeError(f"{name}: row limit")
    S.save(name, url, body, n)
    return pd.read_csv(p)


def detail(eid: str) -> None:
    name = f"detail/{eid}.geojson"
    if (S.RAW / name).exists():
        return
    u = S.COMCAT + "?" + urllib.parse.urlencode(dict(eventid=eid, format="geojson"))
    S.save(name, u, S.get(u), None)


def main() -> int:
    (S.RAW / "val_nb").mkdir(parents=True, exist_ok=True)
    try:
        pos = []
        for lab in LABELS:
            d = fetch_csv(
                f"val_pos_{lab.replace(' ', '_')}.csv",
                q(eventtype=lab, starttime="2000-01-01", endtime=V.END),
            )
            pos.append(d)
        p = pd.concat(pos, ignore_index=True)
        near = pd.Series(False, index=p.index)
        for c in V.CASES:
            near |= pd.Series(
                haversine_km(p.latitude, p.longitude, c.lat, c.lon) <= 25.0, index=p.index
            )
        p = p[~near]
        print("positives:", len(p))
        for r in p.itertuples():
            t = pd.Timestamp(r.time)
            fetch_csv(
                f"val_nb/{r.id}.csv",
                q(
                    latitude=r.latitude,
                    longitude=r.longitude,
                    maxradiuskm=30,
                    starttime=(t - pd.Timedelta(days=400)).strftime("%Y-%m-%d"),
                    endtime=(t + pd.Timedelta(days=400)).strftime("%Y-%m-%d"),
                ),
            )
            detail(r.id)
        g = pd.concat(
            [
                fetch_csv(f"val_global_M4.5_{a}.csv", q(starttime=a, endtime=b, minmagnitude=4.5))
                for a, b in GLOBAL_WINDOWS
            ],
            ignore_index=True,
        ).drop_duplicates("id")
        neg = fetch_csv(
            "val_neg_global_M5_2025.csv",
            q(
                starttime=NEG_START,
                endtime=NEG_END,
                minmagnitude=5.0,
                maxdepth=40,
                eventtype="earthquake",
            ),
        )
        print("negatives:", len(neg))
        gc = F.load_comcat_frame(g)
        for r in neg.itertuples():
            detail(r.id)
            t0 = pd.Timestamp(r.time)
            s = F.sequence_features(gc, t0, r.latitude, r.longitude, float(r.mag), exclude_id=r.id)
            if float(s["n_m45_pm_half_year"]) >= 10:
                for cid in str(s["cluster_ids"]).split(","):
                    if cid:
                        detail(cid)
    finally:
        S.write_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
