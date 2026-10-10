"""Catalogue loading and basic statistics.

- Mc by maximum curvature + 0.2 (Woessner & Wiemer 2005, BSSA 95:684, doi:10.1785/0120040007)
- b-value: Aki (1965) maximum likelihood with Utsu binning correction; uncertainty after
  Shi & Bolt (1982, BSSA 72:1677)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import config as C

T0 = pd.Timestamp("1990-01-01", tz="UTC")


def prepare(df: pd.DataFrame, region: C.Region | None = None) -> pd.DataFrame:
    """Normalise a unified-schema catalogue: parse time, filter, bin magnitudes, add helpers."""
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], format="ISO8601", utc=True, errors="coerce")
    df = df.dropna(subset=["time", "mag", "latitude", "longitude"])
    if region is not None:
        a, b, c, d = region.box
        df = df[df.latitude.between(a, b) & df.longitude.between(c, d)]
        if region.exclude == "lon>-36&lat<66":
            df = df[~((df.longitude > -36) & (df.latitude < 66))]
        if region.maxdepth is not None and "depth" in df:
            df = df[(df.depth.isna()) | (df.depth <= region.maxdepth)]
    df = df[df.time >= T0]
    df = df.sort_values("time").reset_index(drop=True)
    df["mag"] = (df["mag"].astype(float) / C.DM).round() * C.DM
    df["t_yr"] = (df.time - T0).dt.total_seconds() / (365.25 * 86400)
    df["year"] = df.time.dt.year
    df["month"] = df.time.dt.month
    df["is_mb"] = df.get("magType", pd.Series("", index=df.index)).astype(str).str.lower().eq("mb")
    return df


def load(name: str, path: Path | None = None) -> pd.DataFrame:
    r = C.REGIONS[name]
    return prepare(pd.read_csv(path or r.raw_file), r)


def mc_maxc(m: np.ndarray | pd.Series, correction: float = C.MC_CORRECTION) -> float:
    """Maximum-curvature completeness magnitude (+ correction). NaN for < 20 events."""
    arr = np.round(np.asarray(m, dtype=float), 1)
    if len(arr) < 20:
        return float("nan")
    vals, counts = np.unique(arr, return_counts=True)
    return float(vals[int(np.argmax(counts))] + correction)


def b_value(m: np.ndarray | pd.Series, mc: float) -> tuple[float, float, int]:
    """Aki-Utsu b-value, Shi-Bolt sigma and number of events >= mc."""
    arr = np.asarray(m, dtype=float)
    arr = arr[arr >= mc - 1e-9]
    n = len(arr)
    if n < C.B_MIN_EVENTS or not np.isfinite(mc):
        return float("nan"), float("nan"), n
    mean = float(arr.mean())
    b = float(np.log10(np.e) / (mean - (mc - C.DM / 2)))
    sb = float(2.3 * b**2 * np.sqrt(np.sum((arr - mean) ** 2) / (n * (n - 1))))
    return b, sb, n


def haversine_km(
    lat1: np.ndarray | float,
    lon1: np.ndarray | float,
    lat2: np.ndarray | float,
    lon2: np.ndarray | float,
) -> np.ndarray:
    la1, lo1, la2, lo2 = (np.radians(np.asarray(x, dtype=float)) for x in (lat1, lon1, lat2, lon2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return np.asarray(6371.0 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1))))


def reference_mc(df: pd.DataFrame, years: tuple[int, int] | None = None) -> tuple[float, pd.Series]:
    """Reference Mc = 90th percentile of yearly MAXC+0.2 (one homogeneous threshold over time)."""
    d = df if years is None else df[df.year.between(*years)]
    ym = d.groupby("year").mag.apply(mc_maxc).dropna()
    if not len(ym):
        return float("nan"), ym
    return float(np.round(np.nanquantile(ym.values, C.MC_REF_QUANTILE), 1)), ym
