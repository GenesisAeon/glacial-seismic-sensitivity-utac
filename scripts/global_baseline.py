"""EXPLORATORY baseline (not preregistered): global and regional earthquake/volcano counts.

First-pass reality check of 2026-10-10, moved into the repository so that every number quoted
in docs/BASELINE_GLOBAL.md (and in public write-ups) can be reproduced:

* global M>=6 / M>=7 counts per year (USGS ComCat), Gardner-Knopoff declustering, Poisson trends
  with exposure (2026 = 283/365 of a year) and decade rate ratios (exact conditional binomial);
* glaciated regions vs non-glaciated control regions: declustered M>=5 rate ratio
  2010-2024 / 1995-2009 with exact 95 % intervals, per region and pooled, plus Poisson MDEs;
* Smithsonian GVP confirmed eruption starts per year (global, Iceland, Alaska/Aleutians) and per
  box (same rate ratio).

By default the analysis runs offline on the archived snapshots in results/global/snapshots/
(ComCat and GVP as retrieved on 2026-10-10, reduced to the columns used; boxes in
region_boxes.csv / control_boxes.csv). ``--fetch DIR`` downloads fresh catalogues into DIR
(e.g. data/raw/global, not committed) and ``--snapshots DIR`` analyses them; results then differ
slightly because catalogues are revised. SHA-256 sums of the snapshots: snapshots/SHA256SUMS.

Declustering ties (events of equal magnitude) are processed in time order (stable sort). The
2026-10-10 first-pass run used an unstable sort; its declustered numbers differ by a few events
(see docs/BASELINE_GLOBAL.md, section "Tie order"), which illustrates the sensitivity of
window-based declustering.

Sources: USGS ComCat FDSN event service https://earthquake.usgs.gov/fdsnws/event/1/ ;
Smithsonian Global Volcanism Program, Volcanoes of the World (WFS)
https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows ; Gardner & Knopoff (1974) windows as
given by van Stiphout et al. (2012), CORSSA, https://doi.org/10.5078/corssa-52382934 .

Usage: python scripts/global_baseline.py [--snapshots DIR] [--out DIR] [--fetch DIR]
"""

from __future__ import annotations

import argparse
import io
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "results" / "global" / "snapshots"
OUT = ROOT / "results" / "global"
COMCAT = "https://earthquake.usgs.gov/fdsnws/event/1/query"
GVP_WFS = (
    "https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows?service=WFS&version=2.0.0"
    "&request=GetFeature&typeName=GVP-VOTW:Smithsonian_VOTW_Holocene_Eruptions&outputFormat=csv"
)
END = "2026-10-10T23:59:59"
FRAC_LAST = 283 / 365  # 2026-01-01 .. 2026-10-10
LAST_YEAR = 2026
GLACIATED = "glaciated"
CONTROL = "control (non-glaciated)"
P0, P1 = (1995, 2009), (2010, 2024)


# ----------------------------------------------------------------------------- statistics
def gardner_knopoff(df: pd.DataFrame) -> pd.DataFrame:
    """Flag events inside the space-time window of a larger event (column ``dependent``).

    Windows: L = 10^(0.1238 M + 0.983) km; T = 10^(0.032 M + 2.7389) d for M >= 6.5, else
    10^(0.5409 M - 0.547) d (van Stiphout et al. 2012). Largest events first; fore- and
    aftershocks (|dt| <= T) are both flagged. Same windows as ``robustness_mc.gk_windows``."""
    d = df.sort_values("time").reset_index(drop=True).copy()
    t = d.time.to_numpy().astype("datetime64[s]").astype(float) / 86400.0
    lat, lon = np.radians(d.latitude.to_numpy(float)), np.radians(d.longitude.to_numpy(float))
    m = d.mag.to_numpy(float)
    L = 10 ** (0.1238 * m + 0.983)
    T = np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))
    dep = np.zeros(len(d), bool)
    for i in np.argsort(-m, kind="stable"):  # deterministic tie order
        if dep[i]:
            continue
        idx = np.nonzero(np.abs(t - t[i]) <= T[i])[0]
        idx = idx[idx != i]
        if not len(idx):
            continue
        cosd = np.sin(lat[i]) * np.sin(lat[idx]) + np.cos(lat[i]) * np.cos(lat[idx]) * np.cos(
            lon[idx] - lon[i]
        )
        dist = 6371.0 * np.arccos(np.clip(cosd, -1, 1))
        dep[idx[(dist <= L[i]) & (m[idx] <= m[i])]] = True
    d["dependent"] = dep
    return d


def poisson_trend(year: np.ndarray, count: np.ndarray, exposure: np.ndarray) -> dict[str, float]:
    """Poisson GLM log(rate) = a + b (year - 2000) with log-exposure offset (IRLS).

    Returns the trend in % per year with a Wald 95 % interval, p, and the Pearson dispersion
    (chi2 / df); ``ci_*_quasi`` scale the interval by sqrt(max(dispersion, 1))."""
    x = np.column_stack([np.ones(len(year)), np.asarray(year, float) - 2000.0])
    y = np.asarray(count, float)
    off = np.log(np.asarray(exposure, float))
    beta = np.array([np.log(max(float(y.sum()), 1.0) / float(np.exp(off).sum())), 0.0])
    for _ in range(100):
        mu = np.exp(x @ beta + off)
        step = np.linalg.solve(x.T @ (mu[:, None] * x), x.T @ (y - mu))
        beta = beta + step
        if np.max(np.abs(step)) < 1e-12:
            break
    mu = np.exp(x @ beta + off)
    cov = np.linalg.inv(x.T @ (mu[:, None] * x))
    b, se = beta[1], float(np.sqrt(cov[1, 1]))
    disp = float(np.sum((y - mu) ** 2 / mu) / (len(y) - 2))
    sq = np.sqrt(max(disp, 1.0))

    def pct(v: float) -> float:
        return float(100 * (np.exp(v) - 1))

    return dict(
        trend_pct_per_yr=pct(b),
        ci_low=pct(b - 1.96 * se),
        ci_high=pct(b + 1.96 * se),
        p=float(2 * stats.norm.sf(abs(b / se))),
        dispersion=disp,
        ci_low_quasi=pct(b - 1.96 * se * sq),
        ci_high_quasi=pct(b + 1.96 * se * sq),
    )


def rate_ratio(n1: int, n0: int) -> tuple[float, float, float, float]:
    """Rate ratio n1/n0 for equal exposure with exact conditional binomial 95 % CI and p."""
    if n1 + n0 == 0:
        return np.nan, np.nan, np.nan, np.nan
    bt = stats.binomtest(int(n1), int(n1 + n0), 0.5)
    ci = bt.proportion_ci()
    lo = ci.low / (1 - ci.low) if ci.low < 1 else np.inf
    hi = ci.high / (1 - ci.high) if ci.high < 1 else np.inf
    return (n1 / n0 if n0 else np.inf), float(lo), float(hi), float(bt.pvalue)


def mde_rate_ratio(n0: int, n1: int) -> float:
    """Poisson minimal detectable rate ratio (80 % power, two-sided alpha 0.05, equal periods)."""
    nbar = (n0 + n1) / 2
    return float(np.exp((1.96 + 0.84) * np.sqrt(2 / nbar))) if nbar > 0 else np.nan


# ----------------------------------------------------------------------------- data
def _get(url: str, params: dict[str, Any] | None = None) -> str:
    import requests

    for _ in range(4):
        r = requests.get(url, params=params, timeout=300)
        if r.status_code == 200:
            return r.text
        time.sleep(5)
    r.raise_for_status()
    return r.text


def _comcat(params: dict[str, Any], chunks: list[tuple[str, str]]) -> pd.DataFrame:
    frames = []
    for s, e in chunks:
        p = dict(format="csv", starttime=s, endtime=e, eventtype="earthquake", **params)
        txt = _get(COMCAT, p)
        if txt.strip():
            frames.append(pd.read_csv(io.StringIO(txt)))
    df = pd.concat(frames, ignore_index=True).drop_duplicates("id")
    return df[["id", "time", "latitude", "longitude", "depth", "mag", "magType", "place"]]


def fetch(dest: Path) -> None:
    """Download fresh ComCat/GVP catalogues into ``dest`` (same layout as the snapshots)."""
    dest.mkdir(parents=True, exist_ok=True)
    for f in ("region_boxes.csv", "control_boxes.csv"):
        (dest / f).write_text((SNAP / f).read_text(encoding="utf-8"), encoding="utf-8")
    five = [(f"{y}-01-01", f"{y + 5}-01-01") for y in range(1975, 2026, 5)]
    five[-1] = (five[-1][0], END)
    _comcat(dict(minmagnitude=6), five).to_csv(
        dest / "comcat_global_M6plus_1975_2026.csv.gz", index=False
    )
    for r in pd.read_csv(SNAP / "region_boxes.csv").itertuples():
        mm = 4.0 if r.region == "Alps" else 4.5
        box = dict(
            minlatitude=r.minlat, maxlatitude=r.maxlat, minlongitude=r.minlon, maxlongitude=r.maxlon
        )
        d = _comcat(dict(minmagnitude=mm, **box), [("1975-01-01", END)]).assign(region=r.region)
        d.to_csv(dest / f"comcat_region_{r.region}_M{mm}plus.csv.gz", index=False)
    chunks = [("1975-01-01", "2000-01-01"), ("2000-01-01", "2013-01-01"), ("2013-01-01", END)]
    for r in pd.read_csv(SNAP / "control_boxes.csv").itertuples():
        box = dict(
            minlatitude=r.minlat, maxlatitude=r.maxlat, minlongitude=r.minlon, maxlongitude=r.maxlon
        )
        d = _comcat(dict(minmagnitude=5.0, **box), chunks).assign(region=r.region)
        d.to_csv(dest / f"comcat_control_{r.region}_M5plus.csv.gz", index=False)
    v = pd.read_csv(io.StringIO(_get(GVP_WFS)))
    xy = v.GeoLocation.str.extract(r"POINT \(([-\d.]+) ([-\d.]+)\)").astype(float)
    v["lat"], v["lon"] = xy[0], xy[1]
    keep = [
        "Volcano_Number", "Volcano_Name", "Eruption_Number", "Activity_Type", "StartDateYear",
        "StartDateMonth", "ExplosivityIndexMax", "lat", "lon",
    ]  # fmt: skip
    v[keep].to_csv(dest / "gvp_eruptions.csv.gz", index=False)


def _read(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    d["time"] = pd.to_datetime(d.time, format="ISO8601", utc=True).dt.tz_localize(None)
    d["year"] = d.time.dt.year
    return d


def _drop_ridge(d: pd.DataFrame, lat: str = "latitude", lon: str = "longitude") -> pd.DataFrame:
    """Greenland box: exclude Reykjanes Ridge / SW Iceland (plate boundary)."""
    return d[~((d[lon] > -36) & (d[lat] < 66))]


# ----------------------------------------------------------------------------- analysis
def analyse(snap: Path, out: Path) -> dict[str, pd.DataFrame]:
    out.mkdir(parents=True, exist_ok=True)
    years = np.arange(1975, LAST_YEAR + 1)
    expo = np.where(years == LAST_YEAR, FRAC_LAST, 1.0)
    res: dict[str, pd.DataFrame] = {}

    # global
    g = gardner_knopoff(_read(snap / "comcat_global_M6plus_1975_2026.csv.gz"))
    g["year"] = g.time.dt.year
    mw = g.magType.str.lower().str.startswith("mw")
    cnt = pd.DataFrame({"year": years})
    sel = {
        "M6_all": g.mag >= 6,
        "M7_all": g.mag >= 7,
        "M6_declustered": (g.mag >= 6) & ~g.dependent,
        "M7_declustered": (g.mag >= 7) & ~g.dependent,
    }
    for k, s in sel.items():
        cnt[k] = cnt.year.map(g[s].groupby("year").size()).fillna(0).astype(int)
    cnt["exposure_years"] = expo
    cnt["share_Mw_types"] = cnt.year.map(mw.groupby(g.year).mean()).round(3)
    res["global_counts_per_year"] = cnt

    rows: list[dict[str, Any]] = []
    for k in sel:
        for y0 in (1975, 1990, 2000, 2010):
            s = cnt[cnt.year >= y0]
            rows.append(
                dict(
                    series=k,
                    start=y0,
                    end="2026-10-10",
                    **poisson_trend(s.year, s[k], s.exposure_years),
                )
            )
    res["global_trends"] = pd.DataFrame(rows)

    rows = []
    for a, b in [
        (1975, 1984),
        (1985, 1994),
        (1995, 2004),
        (2005, 2014),
        (2015, 2024),
        (2025, 2026),
    ]:
        s = cnt[cnt.year.between(a, b)]
        e = s.exposure_years.sum()
        row: dict[str, Any] = dict(period=f"{a}-{b}", years_exposure=round(e, 3))
        for k in sel:
            row[f"{k}_per_yr"] = round(s[k].sum() / e, 1)
        rows.append(row)
    res["global_decade_rates"] = pd.DataFrame(rows)

    rows = []
    for k in sel:
        n1 = int(cnt[cnt.year.between(2015, 2024)][k].sum())
        n0 = int(cnt[cnt.year.between(1995, 2004)][k].sum())
        r, lo, hi, p = rate_ratio(n1, n0)
        rows.append(
            dict(series=k, n_1995_2004=n0, n_2015_2024=n1, ratio=r, ci_low=lo, ci_high=hi, p=p)
        )
    res["global_decade_ratio"] = pd.DataFrame(rows)

    # regional counts (glaciated boxes, M>=4.5 / Alps M>=4 and M>=5)
    regs = {}
    for f in sorted(snap.glob("comcat_region_*.csv.gz")):
        d = _read(f)
        name = str(d.region.iloc[0])
        regs[name] = _drop_ridge(d) if name == "Greenland_Baffin" else d
    rows = []
    for name, d in regs.items():
        for thr in (4.0 if name == "Alps" else 4.5, 5.0):
            yc = d[d.mag >= thr].groupby("year").size()
            for y, e in zip(years, expo, strict=True):
                rows.append(
                    dict(
                        region=name,
                        Mmin=thr,
                        year=int(y),
                        count=int(yc.get(y, 0)),
                        exposure_years=e,
                    )
                )
    res["regional_counts_per_year"] = pd.DataFrame(rows)

    # ice vs control: declustered M>=5 rate ratio, GVP eruption starts per box
    groups: dict[str, tuple[str, pd.DataFrame]] = {
        n: (GLACIATED, d[d.mag >= 5.0]) for n, d in regs.items()
    }
    for f in sorted(snap.glob("comcat_control_*.csv.gz")):
        d = _read(f)
        groups[str(d.region.iloc[0])] = (CONTROL, d)
    v = pd.read_csv(snap / "gvp_eruptions.csv.gz")
    v = v[v.Activity_Type == "Confirmed Eruption"]
    boxes = pd.concat(
        [pd.read_csv(snap / "region_boxes.csv"), pd.read_csv(snap / "control_boxes.csv")]
    ).set_index("region")
    rows = []
    for name, (grp, d) in groups.items():
        d = gardner_knopoff(d) if len(d) > 1 else d.assign(dependent=False)
        d["year"] = d.time.dt.year
        for lab, s in (("all", d), ("declustered", d[~d.dependent])):
            n0 = int(s.year.between(*P0).sum())
            n1 = int(s.year.between(*P1).sum())
            rows.append(
                dict(region=name, group=grp, series=f"M>=5 {lab}", n_1995_2009=n0, n_2010_2024=n1)
            )
        b = boxes.loc[name]
        ve = v[v.lat.between(b.minlat, b.maxlat) & v.lon.between(b.minlon, b.maxlon)]
        if name == "Greenland_Baffin":
            ve = _drop_ridge(ve, "lat", "lon")
        rows.append(
            dict(
                region=name,
                group=grp,
                series="GVP eruption starts",
                n_1995_2009=int(ve.StartDateYear.between(*P0).sum()),
                n_2010_2024=int(ve.StartDateYear.between(*P1).sum()),
            )
        )
    rr = pd.DataFrame(rows)
    pooled = (
        rr.groupby(["group", "series"], as_index=False)[["n_1995_2009", "n_2010_2024"]]
        .sum()
        .assign(region=lambda x: "POOLED " + x.group)
    )
    rr = pd.concat([rr, pooled[rr.columns]], ignore_index=True)
    stats_ = [rate_ratio(a, b) for a, b in zip(rr.n_2010_2024, rr.n_1995_2009, strict=True)]
    rr["ratio"], rr["ci_low"], rr["ci_high"], rr["p"] = (list(x) for x in zip(*stats_, strict=True))
    rr["mde_ratio_80pct"] = [
        mde_rate_ratio(a, b) for a, b in zip(rr.n_1995_2009, rr.n_2010_2024, strict=True)
    ]
    res["ice_vs_control_rate_ratios"] = rr

    # GVP global per year and per decade
    yv = np.arange(1900, LAST_YEAR + 1)
    vv = v[v.StartDateYear >= 1900]
    isl = vv.lat.between(63, 67) & vv.lon.between(-25, -13)
    ak = vv.lat.between(51, 62) & ((vv.lon <= -130) | (vv.lon >= 170))
    vt = pd.DataFrame({"year": yv})
    for k, s in {
        "confirmed_all": vv.index == vv.index,
        "confirmed_VEI_ge3": vv.ExplosivityIndexMax >= 3,
        "Iceland": isl,
        "Alaska_Aleutians": ak,
    }.items():
        vt[k] = vt.year.map(vv[s].groupby("StartDateYear").size()).fillna(0).astype(int)
    res["gvp_eruption_starts_per_year"] = vt
    rows = []
    for a in range(1950, 2030, 10):
        s = vt[vt.year.between(a, min(a + 9, 2025))]
        rows.append(
            dict(
                period=f"{a}-{min(a + 9, 2025)}",
                all_per_yr=round(s.confirmed_all.mean(), 1),
                VEI_ge3_per_yr=round(s.confirmed_VEI_ge3.mean(), 1),
                Iceland_total=int(s.Iceland.sum()),
                Alaska_Aleutians_total=int(s.Alaska_Aleutians.sum()),
            )
        )
    res["gvp_decade_summary"] = pd.DataFrame(rows)

    for k, df in res.items():
        df.to_csv(out / f"{k}.csv", index=False, float_format="%.6g")
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--snapshots", type=Path, default=SNAP)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--fetch", type=Path, default=None, help="download fresh catalogues here")
    a = ap.parse_args()
    if a.fetch:
        fetch(a.fetch)
        return
    res = analyse(a.snapshots, a.out)
    t = res["global_trends"]
    print(t[t.start == 1990].round(3).to_string(index=False))
    r = res["ice_vs_control_rate_ratios"]
    print(r[r.region.str.startswith("POOLED")].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
