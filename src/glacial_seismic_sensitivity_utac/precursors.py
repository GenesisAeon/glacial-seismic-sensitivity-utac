"""Present-day observables that a trajectory towards the tipping regime would change first.

Two independent geodetic data sets, both fitted with the same transparent model

    y(t) = a + v (t - 2015) + (A/2) (t - 2015)^2 + annual + semi-annual [+ offsets]

- GRACE/GRACE-FO mass (Gt) per box -> mass-change rate v (Gt/yr) and acceleration A (Gt/yr^2).
  The normalised acceleration xi = -A / |v| (1/yr; > 0 = accelerating *loss*) is directly
  comparable with exponential trajectories: an e-folding time T_e gives xi = 1/T_e.
- NGL GNSS vertical positions (m) per station (offsets at all NGL-listed equipment changes and
  earthquakes) -> uplift rate (mm/yr) and uplift acceleration (mm/yr^2).

Standard errors: OLS on monthly means, inflated by sqrt((1+rho)/(1-rho)) with rho the lag-1
autocorrelation of the residuals (crude but conservative for red noise).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .fetch.extra import gnss_path

T_REF = 2015.0


def _design(t: np.ndarray, offsets: list[float] | None = None) -> np.ndarray:
    tt = t - T_REF
    cols = [
        np.ones_like(t),
        tt,
        0.5 * tt**2,
        np.cos(2 * np.pi * t),
        np.sin(2 * np.pi * t),
        np.cos(4 * np.pi * t),
        np.sin(4 * np.pi * t),
    ]
    for o in offsets or []:
        h = (t >= o).astype(float)
        if 3 <= h.sum() <= len(t) - 3:
            cols.append(h)
    return np.column_stack(cols)


def fit_rate_accel(
    t: np.ndarray, y: np.ndarray, offsets: list[float] | None = None
) -> dict[str, float]:
    """Rate (at T_REF) and acceleration with AR(1)-inflated standard errors."""
    ok = np.isfinite(y)
    t, y = np.asarray(t, float)[ok], np.asarray(y, float)[ok]
    x = _design(t, offsets)
    coef, *_ = np.linalg.lstsq(x, y, rcond=None)
    res = y - x @ coef
    dof = max(len(y) - x.shape[1], 1)
    s2 = float(res @ res / dof)
    cov = s2 * np.linalg.pinv(x.T @ x)
    rho = float(np.corrcoef(res[:-1], res[1:])[0, 1]) if len(res) > 3 else 0.0
    rho = min(max(rho, 0.0), 0.95)
    infl = np.sqrt((1 + rho) / (1 - rho))
    se = np.sqrt(np.diag(cov)) * infl
    return dict(
        n=len(y),
        t0=float(t.min()),
        t1=float(t.max()),
        rate=float(coef[1]),
        rate_se=float(se[1]),
        accel=float(coef[2]),
        accel_se=float(se[2]),
        rho=rho,
    )


def _piecewise_rates(t: np.ndarray, y: np.ndarray, split: float) -> tuple[float, float]:
    out: list[float] = []
    for m in (t < split, t >= split):
        if m.sum() < 24:
            out.append(np.nan)
            continue
        tt = t[m]
        x = np.column_stack(
            [np.ones(m.sum()), tt - tt.mean(), np.cos(2 * np.pi * tt), np.sin(2 * np.pi * tt)]
        )
        out.append(float(np.linalg.lstsq(x, y[m], rcond=None)[0][1]))
    return out[0], out[1]


def grace_acceleration(grace: pd.DataFrame, boxes: list[str]) -> pd.DataFrame:
    rows = []
    for b in boxes:
        col = f"{b}_Gt"
        if col not in grace:
            continue
        t, y = grace.t_yr.to_numpy(), grace[col].to_numpy()
        f = fit_rate_accel(t, y)
        r1, r2 = _piecewise_rates(t, y, 2014.0)
        xi = -f["accel"] / abs(f["rate"]) if f["rate"] < 0 else np.nan
        rows.append(
            dict(
                box=b,
                n_mascons=int(grace[f"{b}_n_mascons"].iloc[0]),
                **{f"mass_{k}": v for k, v in f.items()},
                rate_2002_2013_Gt_yr=r1,
                rate_2014_2026_Gt_yr=r2,
                xi_per_yr=xi,
                xi_se=f["accel_se"] / abs(f["rate"]) if f["rate"] < 0 else np.nan,
                e_folding_yr=1 / xi if xi and xi > 0 else np.nan,
            )
        )
    return pd.DataFrame(rows)


def read_tenv3(sta: str) -> pd.DataFrame:
    d = pd.read_csv(gnss_path(sta), sep=r"\s+")
    up = d["u0(m)"] + d["____up(m)"]
    return pd.DataFrame({"t": d["yyyy.yyyy"].to_numpy(), "up_m": up.to_numpy()})


def ngl_steps(sta: str) -> list[float]:
    f = C.RAW / "gnss" / "steps.txt"
    out: list[float] = []
    if not f.exists():
        return out
    with open(f) as fh:
        for line in fh:
            if not line.startswith(sta + " "):
                continue
            tok = line.split()
            dt = pd.to_datetime(tok[1], format="%y%b%d")
            out.append(dt.year + (dt.dayofyear - 0.5) / 365.25)
    return sorted(set(out))


def gnss_uplift(stations: list[str] | None = None) -> pd.DataFrame:
    rows = []
    for sta in stations or list(C.GNSS_STATIONS):
        if not gnss_path(sta).exists():
            continue
        d = read_tenv3(sta)
        mon = (
            d.assign(m=np.floor(d.t * 12)).groupby("m").agg(t=("t", "mean"), up=("up_m", "median"))
        )
        if len(mon) < 60:
            continue
        steps = ngl_steps(sta)
        f = fit_rate_accel(mon.t.to_numpy(), mon.up.to_numpy() * 1000.0, steps)
        r1, r2 = np.nan, np.nan
        mid = float(np.median(mon.t))
        for k, m in enumerate((mon.t < mid, mon.t >= mid)):
            sub = mon[m]
            ff = fit_rate_accel(
                sub.t.to_numpy(), sub.up.to_numpy() * 1000.0, [s for s in steps if s > sub.t.min()]
            )
            if k == 0:
                r1 = ff["rate"] + ff["accel"] * (sub.t.mean() - T_REF)
            else:
                r2 = ff["rate"] + ff["accel"] * (sub.t.mean() - T_REF)
        region, role = C.GNSS_STATIONS[sta]
        rows.append(
            dict(
                station=sta,
                region=region,
                role=role,
                n_months=f["n"],
                t0=round(f["t0"], 2),
                t1=round(f["t1"], 2),
                n_offsets=len(steps),
                uplift_mm_yr_2015=f["rate"],
                uplift_se=f["rate_se"],
                accel_mm_yr2=f["accel"],
                accel_se=f["accel_se"],
                accel_z=f["accel"] / f["accel_se"] if f["accel_se"] > 0 else np.nan,
                split_year=round(mid, 1),
                rate_first_half=r1,
                rate_second_half=r2,
                rho=f["rho"],
            )
        )
    return pd.DataFrame(rows)
