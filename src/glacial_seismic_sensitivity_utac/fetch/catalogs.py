"""Earthquake catalogue downloads into the unified schema.

Sources (all public, no login):
- USGS ComCat FDSN event service  https://earthquake.usgs.gov/fdsnws/event/1/
  (``comcat_ak`` restricts to Alaska Earthquake Center contributions, ``catalog=ak``)
- Swiss Seismological Service FDSN https://eida.ethz.ch/fdsnws/event/1/
- GeoNet (New Zealand) FDSN         https://service.geonet.org.nz/fdsnws/event/1/
- Icelandic Met Office quakes API   https://api.vedur.is/quakes/events
- GEUS Greenland/Denmark GeoJSON    https://seismologi.geus.dk/geojson/GeoJSON-eqs.json
- CSN Chile relocated 1982-2020     Zenodo doi:10.5281/zenodo.13146436 (see fetch/extra.py)
"""

from __future__ import annotations

import io
import json

import pandas as pd

from .. import config as C
from .common import UNIFIED_COLUMNS, http_get

COMCAT = "https://earthquake.usgs.gov/fdsnws/event/1/query"
SED = "https://eida.ethz.ch/fdsnws/event/1/query"
GEONET = "https://service.geonet.org.nz/fdsnws/event/1/query"
IMO = "https://api.vedur.is/quakes/events"
GEUS = "https://seismologi.geus.dk/geojson/GeoJSON-eqs.json"


def _chunks(step_months: int = 6) -> list[tuple[str, str]]:
    out = []
    y0, y1 = int(C.START[:4]), int(C.END[:4])
    for y in range(y0, y1 + 1):
        for m in range(1, 13, step_months):
            s = f"{y}-{m:02d}-01"
            m2 = m + step_months
            e = f"{y + 1}-01-01" if m2 > 12 else f"{y}-{m2:02d}-01"
            if s > C.END:
                continue
            out.append((s, min(e, C.END)))
    return out


def _fdsn_text(text: str) -> pd.DataFrame:
    if not text.strip():
        return pd.DataFrame(columns=UNIFIED_COLUMNS)
    df = pd.read_csv(io.StringIO(text), sep="|")
    df.columns = [c.strip().lstrip("#").strip() for c in df.columns]
    out = pd.DataFrame(
        {
            "time": df["Time"],
            "latitude": df["Latitude"],
            "longitude": df["Longitude"],
            "depth": df["Depth/km"],
            "mag": df["Magnitude"],
            "magType": df["MagType"],
            "id": df["EventID"],
            "etype": df.get("EventType", "earthquake"),
        }
    )
    return out


def fetch_comcat(r: C.Region) -> pd.DataFrame:
    a, b, c, d = r.box
    frames = []
    for s, e in _chunks(6):
        q: dict[str, object] = dict(
            format="csv",
            starttime=s,
            endtime=e,
            minmagnitude=r.minmag,
            eventtype="earthquake",
            minlatitude=a,
            maxlatitude=b,
            minlongitude=c,
            maxlongitude=d,
            orderby="time-asc",
        )
        if r.maxdepth is not None:
            q["maxdepth"] = r.maxdepth
        if r.source == "comcat_ak":
            q["catalog"] = "ak"
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
                )
            )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=UNIFIED_COLUMNS)


def fetch_fdsn(r: C.Region, base: str, step_months: int = 3) -> pd.DataFrame:
    a, b, c, d = r.box
    frames = []
    for s, e in _chunks(step_months):
        q: dict[str, object] = dict(
            format="text",
            starttime=s,
            endtime=e,
            minmagnitude=r.minmag,
            minlatitude=a,
            maxlatitude=b,
            minlongitude=c,
            maxlongitude=d,
        )
        if r.maxdepth is not None:
            q["maxdepth"] = r.maxdepth
        frames.append(_fdsn_text(http_get(base, q)))
    df = pd.concat(frames, ignore_index=True)
    return df[df.etype.astype(str).str.contains("earthquake", case=False, na=True)]


def fetch_imo(r: C.Region) -> pd.DataFrame:
    """IMO quakes API, legacy SIL system (homogeneous since 1991; the SeisComP system is recent)."""
    a, b, c, d = r.box
    poly = f"POLYGON(({c} {b}, {c} {a}, {d} {a}, {d} {b}, {c} {b}))"
    frames = []
    for s, e in _chunks(3):
        q: dict[str, object] = dict(
            format="csv",
            system="sil",
            start_time=f"{s}T00:00:00",
            end_time=f"{e[:10]}T00:00:00",
            size_min=r.minmag,
            polygon=poly,
        )
        if r.maxdepth is not None:
            q["depth_max"] = min(r.maxdepth, 50.0)
        txt = http_get(IMO, q)
        if txt.strip():
            x = pd.read_csv(io.StringIO(txt))
            if len(x):
                frames.append(
                    pd.DataFrame(
                        {
                            "time": x["time"],
                            "latitude": x["latitude"],
                            "longitude": x["longitude"],
                            "depth": x["depth"],
                            "mag": x["magnitude"],
                            "magType": "ML_SIL",
                            "id": x["event_id"],
                            "etype": x["type"],
                        }
                    )
                )
    if not frames:
        return pd.DataFrame(columns=UNIFIED_COLUMNS)
    df = pd.concat(frames, ignore_index=True)
    m = df.latitude.between(a, b) & df.longitude.between(c, d) & (df.mag >= r.minmag)
    return df[m & df.etype.astype(str).str.contains("earthquake", case=False, na=True)]


def fetch_geus(r: C.Region) -> pd.DataFrame:
    js = json.loads(http_get(GEUS))
    rows = []
    for f in js["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"][:2]
        rows.append(
            dict(
                time=p.get("timeofevent"),
                latitude=lat,
                longitude=lon,
                depth=pd.to_numeric(str(p.get("depth", "")).strip(), errors="coerce"),
                mag=p.get("mag"),
                magType=p.get("magType"),
                id=f.get("id", ""),
                etype=p.get("event_type"),
            )
        )
    df = pd.DataFrame(rows)
    a, b, c, d = r.box
    m = df.latitude.between(a, b) & df.longitude.between(c, d)
    df = df[m & df.etype.astype(str).str.contains("earthquake", case=False, na=False)]
    return df[pd.to_datetime(df.time, utc=True, errors="coerce") >= pd.Timestamp(C.START, tz="UTC")]


def fetch_region(name: str, force: bool = False) -> pd.DataFrame:
    r = C.REGIONS[name]
    f = r.raw_file
    if f.exists() and not force:
        return pd.read_csv(f)
    C.RAW.mkdir(parents=True, exist_ok=True)
    if r.source in ("comcat", "comcat_ak"):
        df = fetch_comcat(r)
    elif r.source == "sed":
        df = fetch_fdsn(r, SED)
    elif r.source == "geonet":
        df = fetch_fdsn(r, GEONET)
    elif r.source == "imo":
        df = fetch_imo(r)
    elif r.source == "geus":
        df = fetch_geus(r)
    elif r.source == "csn_zenodo":
        from .extra import fetch_csn

        df = fetch_csn(r)
    else:  # pragma: no cover
        raise ValueError(r.source)
    df = df.drop_duplicates("id")[UNIFIED_COLUMNS]
    df.to_csv(f, index=False)
    print(f"{name}: {len(df)} events -> {f}", flush=True)
    return df
