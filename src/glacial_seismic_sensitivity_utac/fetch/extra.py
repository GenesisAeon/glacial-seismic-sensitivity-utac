"""Downloads added in v0.1.0 for the CSN Chile catalogue and NGL GNSS time series.

- Chilean CSN relocated catalogue 1982-mid-2020 (Potin et al. 2024, Seismol. Res. Lett. 96(1),
  484-498, doi:10.1785/0220240047; data: Potin, Aden-Antoniow & Ruiz, Zenodo,
  doi:10.5281/zenodo.13146436, licence CC BY 4.0). One zip (~4.6 MB); md5 checked.
- Nevada Geodetic Laboratory daily GNSS positions, IGS20 frame (Blewitt, Hammond & Kreemer
  2018, Eos 99, doi:10.1029/2018EO104623) plus the NGL step (offset) database.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from .. import config as C
from .common import UNIFIED_COLUMNS, USER_AGENT, http_get

CSN_CSV = "CHILE_SEISMICITY_RELOCATED.csv"


def _csn_dir() -> Path:
    return C.RAW / "csn_zenodo"


def csn_csv_path() -> Path:
    hits = sorted(_csn_dir().rglob(CSN_CSV))
    return hits[0] if hits else _csn_dir() / CSN_CSV


def download_csn(force: bool = False) -> Path:
    """Download and unpack the Zenodo archive (md5-verified)."""
    p = csn_csv_path()
    if p.exists() and not force:
        return p
    _csn_dir().mkdir(parents=True, exist_ok=True)
    r = requests.get(C.CSN_ZENODO_ZIP, timeout=(30, 300), headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    md5 = hashlib.md5(r.content).hexdigest()
    if md5 != C.CSN_ZENODO_MD5:
        raise RuntimeError(f"CSN zip md5 mismatch: {md5}")
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(_csn_dir())
    return csn_csv_path()


def parse_csn(path: Path) -> pd.DataFrame:
    """CSN relocated CSV -> unified schema (events without magnitude are dropped)."""
    d = pd.read_csv(path)
    d.columns = [c.strip() for c in d.columns]
    sec = d["seconds"].astype(float)
    t = pd.to_datetime(
        dict(
            year=d.year,
            month=d.month,
            day=d.day,
            hour=d.hour,
            minute=d.minute,
            second=np.floor(sec).astype(int).clip(0, 59),
        ),
        utc=True,
    ) + pd.to_timedelta((sec - np.floor(sec)).to_numpy(), unit="s")
    out = pd.DataFrame(
        dict(
            time=t.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            latitude=d.latitude,
            longitude=d.longitude,
            depth=d.depth,
            mag=pd.to_numeric(d.magnitude, errors="coerce"),
            magType=d.magnitude_type.astype(str).str.strip(),
            id="csn" + d["#"].astype(str),
            etype="earthquake",
        )
    )
    return out.dropna(subset=["mag"])[UNIFIED_COLUMNS]


def fetch_csn(r: C.Region) -> pd.DataFrame:
    df = parse_csn(download_csn())
    a, b, c, d = r.box
    m = df.latitude.between(a, b) & df.longitude.between(c, d) & (df.mag >= r.minmag)
    if r.maxdepth is not None:
        m &= df.depth <= r.maxdepth
    df = df[m]
    return df[pd.to_datetime(df.time, utc=True) >= pd.Timestamp(C.START, tz="UTC")]


def gnss_path(sta: str) -> Path:
    return C.RAW / "gnss" / f"{sta}.tenv3"


def fetch_gnss(force: bool = False) -> dict[str, str]:
    (C.RAW / "gnss").mkdir(parents=True, exist_ok=True)
    status = {}
    steps = C.RAW / "gnss" / "steps.txt"
    if force or not steps.exists():
        steps.write_text(http_get(C.NGL_STEPS))
    for sta in C.GNSS_STATIONS:
        f = gnss_path(sta)
        if f.exists() and not force:
            status[sta] = "cached"
            continue
        txt = http_get(C.NGL_TENV3.format(sta=sta))
        f.write_text(txt)
        status[sta] = f"ok ({txt.count(chr(10))} lines)"
    return status
