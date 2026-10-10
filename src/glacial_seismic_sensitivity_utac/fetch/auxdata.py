"""Auxiliary data: GeoNames cities, GRACE/GRACE-FO GSFC mascons, ERA5 precipitation.

- GeoNames cities15000 (CC BY 4.0): https://download.geonames.org/export/dump/cities15000.zip
- GSFC mascons RL06 v2.0 (Loomis et al.): https://earth.gsfc.nasa.gov/geo/data/grace-mascons
- ERA5 reanalysis (Hersbach et al. 2020, doi:10.1002/qj.3803) via the Open-Meteo archive API
  https://archive-api.open-meteo.com/v1/archive (no key; data CC BY 4.0)
"""

from __future__ import annotations

import io
import json
import time
import zipfile

import numpy as np
import pandas as pd
import requests

from .. import config as C
from .common import USER_AGENT, http_get

GEONAMES = "https://download.geonames.org/export/dump/cities15000.zip"
GRACE_URL = (
    "https://earth.gsfc.nasa.gov/sites/default/files/geo/"
    "gsfc.glb_.200204_202603_rl06v2.0_obp-ice6gd.h5"
)
OPEN_METEO = "https://archive-api.open-meteo.com/v1/archive"


def fetch_cities(force: bool = False) -> pd.DataFrame:
    f = C.RAW / "geonames_cities_pop100k.csv"
    if f.exists() and not force:
        return pd.read_csv(f)
    C.RAW.mkdir(parents=True, exist_ok=True)
    r = requests.get(GEONAMES, timeout=300, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    cols = [
        "geonameid",
        "name",
        "asciiname",
        "alternatenames",
        "latitude",
        "longitude",
        "fclass",
        "fcode",
        "country",
        "cc2",
        "admin1",
        "admin2",
        "admin3",
        "admin4",
        "population",
        "elevation",
        "dem",
        "timezone",
        "moddate",
    ]
    df = pd.read_csv(
        z.open("cities15000.txt"),
        sep="\t",
        header=None,
        names=cols,
        usecols=["geonameid", "name", "latitude", "longitude", "country", "population"],
        quoting=3,
        low_memory=False,
    )
    df = df[df.population >= C.CITY_POP]
    df.to_csv(f, index=False)
    return df


def fetch_grace(force: bool = False) -> str:
    f = C.RAW / GRACE_URL.rsplit("/", 1)[-1]
    if f.exists() and not force:
        return str(f)
    C.RAW.mkdir(parents=True, exist_ok=True)
    with requests.get(GRACE_URL, stream=True, timeout=600, headers={"User-Agent": USER_AGENT}) as r:
        r.raise_for_status()
        with open(f, "wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    return str(f)


def fetch_precip(region: str, force: bool = False) -> pd.DataFrame:
    """Monthly regional-mean ERA5 precipitation, rain and snowfall (mean over sample points)."""
    f = C.RAW / f"era5_precip_{region}.csv"
    if f.exists() and not force:
        return pd.read_csv(f, parse_dates=["month"])
    C.RAW.mkdir(parents=True, exist_ok=True)
    frames = []
    for lat, lon in C.PRECIP_POINTS[region]:
        q: dict[str, object] = dict(
            latitude=lat,
            longitude=lon,
            start_date=C.START[:10],
            end_date="2026-09-30",
            models="era5",
            daily="precipitation_sum,rain_sum,snowfall_sum",
            timezone="GMT",
        )
        js = json.loads(http_get(OPEN_METEO, q, ok_empty=()))
        d = pd.DataFrame(js["daily"])
        d["time"] = pd.to_datetime(d["time"])
        d["pt"] = f"{lat},{lon}"
        frames.append(d)
        time.sleep(2)
    d = pd.concat(frames)
    d["month"] = d.time.dt.to_period("M").dt.to_timestamp()
    # snowfall_sum is cm of snow (Open-Meteo: ~7 cm snow per 1 cm water); kept raw
    m = d.groupby(["month", "pt"])[["precipitation_sum", "rain_sum", "snowfall_sum"]].sum(
        min_count=20
    )
    m = m.groupby("month").mean().reset_index()
    m = m.rename(
        columns={
            "precipitation_sum": "precip_mm",
            "rain_sum": "rain_mm",
            "snowfall_sum": "snowfall_cm",
        }
    )
    m["n_points"] = len(C.PRECIP_POINTS[region])
    m.loc[m.precip_mm.isna(), ["rain_mm", "snowfall_cm"]] = np.nan
    m.to_csv(f, index=False)
    return m
