"""Seasonal-modulation robustness (Schuster test) and the Kantishna phase-cancellation check.

The Schuster test (Schuster 1897; usage as in Ader & Avouac 2013, doi:10.1016/j.epsl.2013.06.032)
returns the relative amplitude 2R/N of the annual harmonic, p = exp(-R^2/N) and the peak phase.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .catalog import mc_maxc
from .regionrun import Prepared

# Kantishna seismic cluster, central Alaska (Johnson, Fu & Buergmann 2020,
# doi:10.1016/j.epsl.2019.115904, report > 25 % seasonal modulation there, with opposite phases
# north and south of the Denali fault). Box used here is our own approximation.
KANTISHNA_BOX = (62.8, 63.8, -152.0, -150.0)


def schuster_full(t_yr: np.ndarray, period: float = 1.0) -> dict[str, float]:
    ph = 2 * np.pi * (np.asarray(t_yr, float) % period) / period
    n = len(ph)
    if n < 20:
        return dict(n=n, amp=np.nan, p=np.nan, peak_month=np.nan)
    cs, sn = np.cos(ph).sum(), np.sin(ph).sum()
    r = float(np.hypot(cs, sn))
    return dict(
        n=n,
        amp=2 * r / n,
        p=float(np.exp(-(r**2) / n)),
        peak_month=float(((np.arctan2(sn, cs) / (2 * np.pi)) % 1.0) * 12 + 1),
    )


def robustness(p: Prepared) -> pd.DataFrame:
    d = p.decl[p.decl.year <= C.TEST_END_YEAR]
    raw = p.dc[p.dc.year <= C.TEST_END_YEAR]
    mc = p.mc_ref
    variants = {
        "decl_all": d,
        f"decl_M>={mc + 0.4:.1f}": d[d.mag >= mc + 0.4 - 1e-9],
        f"decl_M>={mc + 0.9:.1f}": d[d.mag >= mc + 0.9 - 1e-9],
        "decl_depth<5km": d[d.depth < 5],
        "decl_depth>=5km": d[d.depth >= 5],
        "decl_1990-2007": d[d.year <= 2007],
        "decl_2008-2025": d[d.year >= 2008],
        "raw_all": raw,
    }
    rows = [
        dict(region=p.name, variant=v, mc_ref=mc, **schuster_full(s.t_yr.to_numpy()))
        for v, s in variants.items()
    ]
    return pd.DataFrame(rows)


def monthly_mc(p: Prepared) -> pd.DataFrame:
    """Completeness by calendar month - a seasonal detection artefact would show up here."""
    a = p.raw[p.raw.year <= C.TEST_END_YEAR]
    rows = []
    for m in range(1, 13):
        s = a[a.month == m]
        rows.append(dict(region=p.name, month=m, mc_maxc=mc_maxc(s.mag.to_numpy()), n=len(s)))
    return pd.DataFrame(rows)


def climatology(p: Prepared) -> pd.DataFrame:
    d = p.decl[p.decl.year <= C.TEST_END_YEAR]
    cl = d.groupby(d.time.dt.month).size().reindex(range(1, 13), fill_value=0)
    return pd.DataFrame({"region": p.name, "month": range(1, 13), "count": cl.to_numpy()})


def amplitude_windows(p: Prepared, width: int = 6) -> pd.DataFrame:
    d = p.decl
    rows = []
    for s in range(1990, C.TEST_END_YEAR + 1, width):
        e = min(s + width - 1, C.TEST_END_YEAR)
        x = d[d.year.between(s, e)]
        rows.append(dict(region=p.name, window=f"{s}-{e}", **schuster_full(x.t_yr.to_numpy())))
    return pd.DataFrame(rows)


def kantishna_split(p: Prepared) -> pd.DataFrame:
    """Interior-Alaska control with and without the Kantishna cluster, and Kantishna alone."""
    d = p.decl[p.decl.year <= C.TEST_END_YEAR]
    a, b, c, e = KANTISHNA_BOX
    k = d.latitude.between(a, b) & d.longitude.between(c, e)
    rows = []
    for name, s in (("all", d), ("kantishna", d[k]), ("without_kantishna", d[~k])):
        rows.append(dict(region=p.name, subset=name, **schuster_full(s.t_yr.to_numpy())))
    return pd.DataFrame(rows)


def grid_map(p: Prepared, cell_deg: float = 1.0, min_n: int = 50) -> pd.DataFrame:
    """Schuster amplitude/phase per grid cell (exposes spatial phase differences that cancel
    in a regional sum, as reported for Kantishna by Johnson et al. 2020)."""
    d = p.decl[p.decl.year <= C.TEST_END_YEAR]
    gi = np.floor(d.latitude / cell_deg) * cell_deg
    gj = np.floor(d.longitude / cell_deg) * cell_deg
    rows = []
    for (la, lo), s in d.groupby([gi, gj]):
        if len(s) < min_n:
            continue
        rows.append(dict(region=p.name, lat0=la, lon0=lo, **schuster_full(s.t_yr.to_numpy())))
    return pd.DataFrame(rows)
