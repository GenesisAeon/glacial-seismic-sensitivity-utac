"""v0.3 S1: catalogue snapshots for the frozen S0 case list.

Writes raw files to data/raw/v03/ (git-ignored like all raw data) and commits-able metadata:
  results/v03/MANIFEST_v03.sha256   sha256sum-compatible, paths relative to data/raw/v03/
  results/v03/s1_snapshots.json     per file: query URL, fetch time (UTC), bytes, rows

Services: USGS ComCat FDSN (csv; event details geojson), KNMI FDSN (text), EMSC FDSN (text).
Usage: python scripts/v03_fetch.py [--details-only]
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import time
import urllib.parse
from datetime import UTC, datetime

import numpy as np
import pandas as pd
import requests

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import v03_cases as V
from glacial_seismic_sensitivity_utac.catalog import haversine_km

RAW = C.RAW / "v03"
OUTD = C.OUT / "v03"
UA = {"User-Agent": "glacial-seismic-sensitivity-utac v0.3-dev (joberoemer@gmail.com)"}
COMCAT = "https://earthquake.usgs.gov/fdsnws/event/1/query"
KNMI = "https://rdsa.knmi.nl/fdsnws/event/1/query"
EMSC = "https://www.seismicportal.eu/fdsnws/event/1/query"
KM_PER_DEG = 111.19


def url_for(q: V.Query) -> str:
    if q.service == "comcat":
        p = dict(
            format="csv",
            orderby="time-asc",
            starttime=q.start,
            endtime=q.end,
            latitude=q.lat,
            longitude=q.lon,
            maxradiuskm=q.radius_km,
        )
        base = COMCAT
    else:
        p = dict(
            format="text",
            starttime=q.start,
            endtime=q.end,
            latitude=q.lat,
            longitude=q.lon,
            maxradius=round(q.radius_km / KM_PER_DEG, 4),
        )
        base = KNMI if q.service == "knmi" else EMSC
        if q.service == "emsc":
            p["limit"] = 20000
    if q.minmag is not None:
        p["minmagnitude"] = q.minmag
    return base + "?" + urllib.parse.urlencode(p)


def box_url(box: tuple[float, float, float, float], minmag: float) -> str:
    p = dict(
        format="csv",
        orderby="time-asc",
        starttime=V.CONTROL_START,
        endtime=V.END,
        minlatitude=box[0],
        maxlatitude=box[1],
        minlongitude=box[2],
        maxlongitude=box[3],
        minmagnitude=minmag,
    )
    return COMCAT + "?" + urllib.parse.urlencode(p)


def get(url: str) -> bytes:
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=180)
            if r.status_code == 204:
                return b""
            r.raise_for_status()
            return r.content
        except requests.RequestException as e:
            if attempt == 3:
                raise
            print("  retry", attempt + 1, e, file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


META: dict[str, dict[str, object]] = {}


def save(name: str, url: str, body: bytes, rows: int | None) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / name).write_bytes(body)
    META[name] = dict(
        url=url,
        fetched_utc=datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        bytes=len(body),
        rows=rows,
        sha256=hashlib.sha256(body).hexdigest(),
    )
    print(f"  {name}: {rows} rows, {len(body)} B")
    time.sleep(0.4)


def n_rows(body: bytes) -> int:
    lines = [ln for ln in body.decode("utf-8", "replace").splitlines() if ln.strip()]
    return max(len(lines) - 1, 0)


def fetch_catalogues() -> None:
    for c in V.CASES:
        for q in c.queries:
            u = url_for(q)
            body = get(u)
            n = n_rows(body)
            if n >= 19999:
                raise RuntimeError(f"{q.name}: hit the 20000-row limit, split the query")
            save(f"{q.name}.{'csv' if q.service == 'comcat' else 'txt'}", u, body, n)
    for reg, box in V.CONTROL_REGIONS.items():
        u = box_url(box, V.CONTROL_MINMAG_FETCH)
        body = get(u)
        n = n_rows(body)
        if n >= 19999:
            raise RuntimeError(f"control {reg}: row limit")
        save(f"control_{reg}.csv", u, body, n)


def detail_ids() -> list[str]:
    ids: list[str] = []
    for c in V.CASES:
        ids += list(c.key_event_ids)
    ids += ["us2000aert", "usp000j1ea", *V.NAMED_CONTROLS.values()]
    b = pd.read_csv(RAW / "bardarbunga_comcat.csv", parse_dates=["time"])
    sel = (
        (b.mag >= 5.0)
        & (b.time >= "2014-08-16")
        & (b.time < "2015-02-28")
        & (haversine_km(b.latitude, b.longitude, 64.64, -17.53) <= 15.0)
    )
    ids += list(b.loc[sel, "id"])
    centres = np.array([[c.lat, c.lon] for c in V.CASES])
    for reg in V.CONTROL_REGIONS:
        d = pd.read_csv(RAW / f"control_{reg}.csv")
        d = d[(d.type == "earthquake") & (d.mag >= V.CONTROL_MAINSHOCK_MIN)]
        near = np.zeros(len(d), bool)
        for la, lo in centres:
            near |= haversine_km(d.latitude, d.longitude, la, lo) <= V.CONTROL_EXCLUDE_KM
        ids += list(d.loc[~near, "id"])
    return list(dict.fromkeys(ids))


def fetch_details() -> None:
    ids = detail_ids()
    print(f"details: {len(ids)} events")
    for eid in ids:
        u = COMCAT + "?" + urllib.parse.urlencode(dict(eventid=eid, format="geojson"))
        body = get(u)
        save(f"detail/{eid}.geojson", u, body, None)


def write_manifest() -> None:
    OUTD.mkdir(parents=True, exist_ok=True)
    meta_path = OUTD / "s1_snapshots.json"
    old = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    old.update(META)
    meta_path.write_text(json.dumps(old, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    buf = io.StringIO()
    for name in sorted(old):
        buf.write(f"{old[name]['sha256']}  {name}\n")
    (OUTD / "MANIFEST_v03.sha256").write_text(buf.getvalue(), encoding="utf-8")


def main() -> int:
    (RAW / "detail").mkdir(parents=True, exist_ok=True)
    try:
        if "--details-only" not in sys.argv:
            fetch_catalogues()
        fetch_details()
    finally:
        write_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
