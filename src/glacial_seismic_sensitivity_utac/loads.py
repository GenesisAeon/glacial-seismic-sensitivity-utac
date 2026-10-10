"""Surface-load and precipitation covariates.

GRACE/GRACE-FO GSFC mascons RL06 v2.0
(Loomis, Luthcke & Sabaka 2019, doi:10.1007/s00190-019-01252-y;
data: https://earth.gsfc.nasa.gov/geo/data/grace-mascons). Regional mean surface-mass anomaly
over non-ocean mascons whose centres fall in the region box, converted to an equivalent
vertical surface load:  1 cm water equivalent = 10 kg/m^2  ->  0.0981 kPa.

The regional mean smears the load over the whole box; the load on glaciers themselves is larger.
"""

from __future__ import annotations

import glob

import h5py
import numpy as np
import pandas as pd

from . import config as C

KPA_PER_CMWE = 0.01 * C.RHO_WATER * C.G_ACC / 1000.0  # 0.0981 kPa per cm w.e.


def grace_file() -> str:
    files = sorted(glob.glob(str(C.RAW / "gsfc*.h5")))
    if not files:
        raise FileNotFoundError("GRACE mascon file missing - run `glacial-sensitivity fetch`")
    return files[-1]


def box_grace(
    boxes: dict[str, tuple[tuple[float, float, float, float], str | None]], fn: str | None = None
) -> pd.DataFrame:
    """Monthly mean load anomaly (kPa) and mass (Gt) for arbitrary boxes.

    boxes[name] = ((minlat, maxlat, minlon, maxlon), exclude_rule_or_None).
    Columns: t_yr, month (Timestamp), <name>_kPa, <name>_Gt, <name>_n_mascons.
    """
    fn = fn or grace_file()
    with h5py.File(fn, "r") as f:
        lat = f["mascon/lat_center"][0]
        lon = f["mascon/lon_center"][0]
        lon = np.where(lon > 180, lon - 360, lon)
        area = f["mascon/area_km2"][0]
        loc = f["mascon/location"][0]
        cm = f["solution/cmwe"][:]
        tyr = f["time/yyyy_doy_yrplot_middle"][2]
    out: dict[str, np.ndarray] = {"t_yr": np.asarray(tyr)}
    for name, (box, exclude) in boxes.items():
        a, b, c, d = box
        m = (lat >= a) & (lat <= b) & (lon >= c) & (lon <= d) & (loc != 90)
        if exclude == "lon>-36&lat<66":
            m &= ~((lon > -36) & (lat < 66))
        if m.sum() == 0:
            continue
        w = area[m]
        mean_cm = (cm[m] * w[:, None]).sum(0) / w.sum()
        out[f"{name}_kPa"] = mean_cm * KPA_PER_CMWE
        out[f"{name}_Gt"] = (cm[m] * w[:, None]).sum(0) * 1e-5
        out[f"{name}_n_mascons"] = np.full(len(tyr), int(m.sum()))
    df = pd.DataFrame(out)
    yr = np.floor(df.t_yr).astype(int)
    mon = np.clip(np.floor((df.t_yr - yr) * 12).astype(int) + 1, 1, 12)
    df["month"] = pd.to_datetime(dict(year=yr, month=mon, day=1))
    return df.drop_duplicates("month").reset_index(drop=True)


def regional_grace(fn: str | None = None) -> pd.DataFrame:
    """Monthly regional mean load anomaly (kPa) and mass (Gt) for every study region."""
    return box_grace({n: (r.box, r.exclude) for n, r in C.REGIONS.items() if r.grace}, fn)


def seasonal_anomaly(s: pd.Series, window: int = 13, min_periods: int = 9) -> pd.Series:
    """Remove the slow part with a centred running mean (keeps the seasonal/sub-annual cycle)."""
    slow = s.rolling(window, center=True, min_periods=min_periods).mean()
    return s - slow


def monthly_load(region: str, grace: pd.DataFrame | None = None) -> pd.DataFrame:
    """Regular monthly series 2002-04..2026-03 (NaN in gaps) with load L, seasonal anomaly and
    unloading U = -anomaly (positive when the surface mass is below its running annual mean)."""
    g = grace if grace is not None else regional_grace()
    col = f"{region}_kPa"
    if col not in g:
        raise KeyError(f"no GRACE mascons in region {region}")
    s = g.set_index("month")[col]
    idx = pd.date_range(s.index.min(), s.index.max(), freq="MS")
    s = s.reindex(idx)
    anom = seasonal_anomaly(s)
    return pd.DataFrame(
        {
            "month": idx,
            "load_kPa": s.values,
            "load_anom_kPa": anom.values,
            "unload_kPa": -anom.values,
        }
    )


def harmonic_fit(t_yr: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Linear trend + annual harmonic -> trend, amplitude, peak phase (fraction of year)."""
    ok = np.isfinite(y)
    t, v = t_yr[ok], y[ok]
    x = np.column_stack([np.ones(len(t)), t - 2014, np.cos(2 * np.pi * t), np.sin(2 * np.pi * t)])
    coef, *_ = np.linalg.lstsq(x, v, rcond=None)
    return dict(
        trend_per_yr=float(coef[1]),
        annual_amp=float(np.hypot(coef[2], coef[3])),
        peak_phase=float((np.arctan2(coef[3], coef[2]) / (2 * np.pi)) % 1.0),
    )


def precip_anomaly(region: str) -> pd.DataFrame:
    """Monthly ERA5 precipitation / rain / snowfall and their seasonal anomalies."""
    f = C.RAW / f"era5_precip_{region}.csv"
    p = pd.read_csv(f, parse_dates=["month"])
    for k in ("precip_mm", "rain_mm", "snowfall_cm"):
        p[f"{k}_anom"] = seasonal_anomaly(p[k])
    return p
