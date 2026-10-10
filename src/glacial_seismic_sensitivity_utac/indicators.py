"""Distribution/dynamics indicators per non-overlapping time bin and critical-slowing-down
indicators on monthly counts.

- Burstiness: Goh & Barabasi (2008, EPL 81:48002, doi:10.1209/0295-5075/81/48002)
- CSD: Dakos et al. (2012, PLoS ONE 7:e41010, doi:10.1371/journal.pone.0041010)
- Schuster test: Schuster (1897); Ader & Avouac (2013, EPSL 377:97, doi:10.1016/j.epsl.2013.06.032)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.ndimage import gaussian_filter1d

from . import config as C
from .catalog import b_value, haversine_km, mc_maxc


def interevent_stats(t_days: np.ndarray) -> tuple[float, float]:
    t = np.sort(np.asarray(t_days, dtype=float))
    if len(t) < 10:
        return float("nan"), float("nan")
    dt = np.diff(t)
    mu, sd = float(dt.mean()), float(dt.std(ddof=1))
    cv = sd / mu if mu > 0 else float("nan")
    burst = (sd - mu) / (sd + mu) if (sd + mu) > 0 else float("nan")
    return cv, burst


def schuster(t_yr: np.ndarray, period: float = 1.0) -> tuple[float, float, float]:
    """Relative amplitude 2R/N, Schuster p = exp(-R^2/N) and peak phase (fraction of period)."""
    ph = 2 * np.pi * (np.asarray(t_yr, dtype=float) % period) / period
    n = len(ph)
    if n < 10:
        return float("nan"), float("nan"), float("nan")
    cs, sn = float(np.cos(ph).sum()), float(np.sin(ph).sum())
    r = float(np.hypot(cs, sn))
    return 2 * r / n, float(np.exp(-(r**2) / n)), float((np.arctan2(sn, cs) / (2 * np.pi)) % 1.0)


def near_city_flag(
    df: pd.DataFrame, cities: pd.DataFrame, radius_km: float = C.CITY_RADIUS_KM
) -> np.ndarray:
    if not len(df) or not len(cities):
        return np.zeros(len(df), dtype=bool)
    a = df.latitude.to_numpy(float)
    o = df.longitude.to_numpy(float)
    cc = cities[cities.latitude.between(a.min() - 2, a.max() + 2)]
    flag = np.zeros(len(df), dtype=bool)
    for k in range(0, len(cc), 500):
        c = cc.iloc[k : k + 500]
        d = haversine_km(
            a[:, None], o[:, None], c.latitude.to_numpy()[None, :], c.longitude.to_numpy()[None, :]
        )
        flag |= (d <= radius_km).any(1)
    return flag


def monthly_counts(df: pd.DataFrame, start: str = "1990-01", end: str = "2026-09") -> pd.Series:
    if len(df):
        s = df.groupby(df.time.dt.tz_localize(None).dt.to_period("M")).size()
    else:
        s = pd.Series(dtype=float)
    return s.reindex(pd.period_range(start, end, freq="M"), fill_value=0).astype(float)


def bin_indicators(
    df_all: pd.DataFrame,
    dc: pd.DataFrame,
    ct: pd.DataFrame,
    mc_ref: float,
    cities: pd.DataFrame,
    last_full_year: int = C.TEST_END_YEAR,
) -> pd.DataFrame:
    """Indicators in non-overlapping BIN_YEARS bins. ``dc``: events >= mc_ref with 'triggered'."""
    raw = dc.assign(near_city=near_city_flag(dc, cities))
    rows = []
    for s in range(1990, last_full_year + 1, C.BIN_YEARS):
        e = s + C.BIN_YEARS - 1
        span = float(min(e, last_full_year) - s + 1)
        a = df_all[df_all.year.between(s, e)]
        r = raw[raw.year.between(s, e)]
        d = r[~r.triggered]
        mc_b = mc_maxc(a.mag.to_numpy())
        b, sb, nb = b_value(a.mag.to_numpy(), max(mc_b, mc_ref) if np.isfinite(mc_b) else mc_ref)
        bd, sbd, _ = b_value(d.mag.to_numpy(), mc_ref)
        cv_r, b_r = interevent_stats(r.t_yr.to_numpy() * 365.25)
        cv_d, b_d = interevent_stats(d.t_yr.to_numpy() * 365.25)
        amp, p_s, _ = schuster(d.t_yr.to_numpy())
        c = ct[ct.year.between(s, e)] if len(ct) else ct
        big = c[c["size"] >= C.SWARM_MIN_SIZE] if len(c) else c
        prod = float("nan")
        if len(c):
            ms = c[c.m_max >= mc_ref + 1.0]
            if len(ms):
                prod = float(np.mean(np.log10(ms.n_after_main + 1) - (ms.m_max - mc_ref)))
        mon = monthly_counts(d, f"{s}-01", f"{min(e, last_full_year)}-12")
        rows.append(
            dict(
                bin_start=s,
                bin_end=e,
                years=span,
                mc_bin=mc_b,
                n_raw=len(r),
                n_decl=len(d),
                rate_raw=len(r) / span,
                rate_decl=len(d) / span,
                triggered_frac=float(r.triggered.mean()) if len(r) else np.nan,
                cv_raw=cv_r,
                burst_raw=b_r,
                cv_decl=cv_d,
                burst_decl=b_d,
                dispersion_monthly_decl=float(mon.var() / mon.mean()) if mon.mean() > 0 else np.nan,
                b_raw=b,
                b_raw_sigma=sb,
                b_raw_n=nb,
                b_decl=bd,
                b_decl_sigma=sbd,
                n_clusters_ge5=len(big),
                mean_cluster_size=float(c["size"].mean()) if len(c) else np.nan,
                swarm_frac=float(big.swarm_like.mean()) if len(big) else np.nan,
                productivity_resid=prod,
                seasonal_amp_decl=amp,
                seasonal_p_decl=p_s,
                frac_near_city_raw=float(r.near_city.mean()) if len(r) else np.nan,
                frac_near_city_decl=float(d.near_city.mean()) if len(d) else np.nan,
                mag_q95_raw=float(np.quantile(r.mag, 0.95)) if len(r) >= 20 else np.nan,
                frac_mb=float(a.is_mb.mean()) if len(a) else np.nan,
            )
        )
    return pd.DataFrame(rows)


def rolling_from_resid(resid: np.ndarray, frac: float = C.ROLL_FRACTION) -> pd.DataFrame:
    w = int(len(resid) * frac)
    s = pd.Series(resid)
    ar1 = s.rolling(w).corr(s.shift(1))
    lam = -np.log(ar1.where((ar1 > 0) & (ar1 < 1)))
    return pd.DataFrame(
        dict(
            variance=s.rolling(w).var(),
            ar1=ar1,
            skewness=s.rolling(w).skew(),
            kurtosis=s.rolling(w).kurt(),
            recovery_rate=lam,
        )
    )


def detrend(x: np.ndarray, bw: int = C.DETREND_BANDWIDTH_MONTHS) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return np.asarray(x - gaussian_filter1d(x, bw, mode="nearest"))


def csd_indicators(
    x: np.ndarray, bw: int = C.DETREND_BANDWIDTH_MONTHS, frac: float = C.ROLL_FRACTION
) -> pd.DataFrame:
    return rolling_from_resid(detrend(x, bw), frac)


def kendall(y: np.ndarray | pd.Series) -> float:
    v = pd.Series(y).dropna().to_numpy(float)
    if len(v) < 5 or np.all(v == v[0]):
        return float("nan")
    return float(stats.kendalltau(np.arange(len(v)), v).statistic)


def b_event_windows(d: pd.DataFrame, mc: float, n_win: int = 100) -> pd.DataFrame:
    """b-value in consecutive non-overlapping windows of n_win events."""
    d = d[d.mag >= mc - 1e-9].sort_values("time")
    rows = []
    for k in range(0, len(d) - n_win + 1, n_win):
        s = d.iloc[k : k + n_win]
        b, sb, n = b_value(s.mag.to_numpy(), mc)
        rows.append(
            dict(
                t_mid=s.time.iloc[n_win // 2],
                year_mid=float(s.t_yr.iloc[n_win // 2]) + 1990,
                b=b,
                b_sigma=sb,
                n=n,
            )
        )
    return pd.DataFrame(rows, columns=["t_mid", "year_mid", "b", "b_sigma", "n"])
