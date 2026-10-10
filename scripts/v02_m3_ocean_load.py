"""EXPLORATORY (review DR item 11 / open item a): H3 with ocean-tide loading added to the body tide.

The preregistered H3 uses the degree-2 body tide only (frozen; "NO ocean loading"). Here the
areal strain of the ocean load tide is computed with SPOTL (Agnew 1996, 1997; NLOADF,
https://igppweb.ucsd.edu/~agnew/Spotl/spotlmain.html) from the global ocean model TPXO 7.2 (as
shipped with SPOTL) for the eight main constituents (M2 S2 N2 K2 K1 O1 P1 Q1), Gutenberg-Bullen
Green functions (gr.gbaver.wef.p02.ce), and predicted in time with SPOTL ``hartid`` (which infers
the minor constituents by admittance interpolation). Load areal strain = 1.5 x SPOTL volume strain
(free surface, Poisson ratio 0.25). Events are assigned to load sites = event centroids of 0.5 deg
cells. The body tide is the unchanged ``tides.areal_strain``; phase on body + load, +-20 h window.
Because the total waveform is not time-symmetric, phases are also tested against the empirical
phase distribution at random times (``null_test``); the plain Schuster p is reported as well.

Not part of any preregistered test. Requires a local SPOTL build: env SPOTL_HOME (default
/workspace/spotl_build/spotl) with bin/ and working/ prepared as in SPOTL's install.rest
(only the TPXO 7.2 files of the eight constituents are needed).
Writes results/v02/m3_tides_ocean_load.csv and m3_ocean_load_sites.csv; also a body-tide
consistency check SPOTL vs ``tides.areal_strain`` (m3_ocean_load_bodycheck.csv)."""

from __future__ import annotations

import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

from glacial_seismic_sensitivity_utac import etas_nonstat as E
from glacial_seismic_sensitivity_utac import tides as T
from glacial_seismic_sensitivity_utac import v02
from glacial_seismic_sensitivity_utac.quiescence import decimal_year

SPOTL = Path(os.environ.get("SPOTL_HOME", "/workspace/spotl_build/spotl"))
BIN, WORK = SPOTL / "bin", SPOTL / "working"
CONST = ("m2", "s2", "n2", "k2", "k1", "o1", "p1", "q1")
MODEL = "osu.tpxo72.2010"
GREEN = "gr.gbaver.wef.p02.ce"
DT_S = 1800  # sample interval of the predicted load series (cubic-spline interpolated)
CHUNK = 90_000  # hartid writes at most 100 000 values per call
CELL = 0.5
POOL_FACTOR, POOL_MIN = 3, 60  # random-time null pool per cell
JD_UNIX0 = 2440587.5


def _run(args: list[str], stdin: str | None = None) -> str:
    r = subprocess.run(args, input=stdin, capture_output=True, text=True, cwd=WORK, check=True)
    return r.stdout


def harmonics(lat: float, lon: float, body: bool = False) -> str:
    """hartid input for areal strain (nanostrain) at a site: ocean load or (body=True) SPOTL's
    own body tide (loadcomb b; Love numbers h 0.6114, l 0.0832) for the consistency check."""
    loads = []
    for c in CONST:
        ld = _run(
            [
                str(BIN / "nloadf"),
                "SITE",
                f"{lat:.4f}",
                f"{lon:.4f}",
                "0",
                f"{c}.{MODEL}",
                GREEN,
                "l",
            ]
        )
        if body:
            ld = _run([str(BIN / "loadcomb"), "b"], ld)
        loads.append(ld)
    h = _run([str(BIN / "harprp"), "v"], "".join(loads)).splitlines()
    out = h[:2]
    for line in h[2:]:
        code, rest = line[:12], line[12:].split()  # Cartwright-Tayler code: 6 fields of width 2
        if code.split()[0] == "-1" or len(rest) < 2:
            out.append(line)
            continue
        amp = 1.5 * float(rest[0])  # volume -> areal strain at the free surface (nu = 0.25)
        ph = float(rest[1])
        if body and lat < 0 and code[:2].strip() == "1":
            # loadcomb b gives phases relative to the signed local potential, hartid uses the
            # latitude-free Cartwright-Tayler argument: the diurnal potential changes sign south
            # of the equator (P21). Ocean-load phases (from the ocean model's Greenwich phases)
            # are latitude-free already and need no correction.
            ph += 180.0
        out.append(f"{code}{amp:9.4f}{ph:9.2f}")
    return "\n".join(out) + "\n"


def predict(harm: str, t0: dt.datetime, n: int) -> tuple[np.ndarray, np.ndarray]:
    """Predicted series (dimensionless strain) and its Julian dates, from t0 (UTC) every DT_S."""
    vals = []
    k = 0
    while k < n:
        m = min(CHUNK, n - k)
        t = t0 + dt.timedelta(seconds=k * DT_S)
        doy = t.timetuple().tm_yday
        o = _run(
            [
                str(BIN / "hartid"),
                str(t.year),
                str(doy),
                str(t.hour),
                str(t.minute),
                str(t.second),
                str(m),
                str(DT_S),
            ],
            harm,
        )
        vals.append(np.array(o.split(), float))
        k += m
    jd0 = (t0 - dt.datetime(1970, 1, 1)).total_seconds() / 86400 + JD_UNIX0
    return jd0 + np.arange(n) * DT_S / 86400, np.concatenate(vals) * 1e-9


def body_check() -> pd.DataFrame:
    rows = []
    t0 = dt.datetime(2010, 1, 1)
    for name, lat, lon in (
        ("SE_Alaska", 59.5, -139.0),
        ("NZ", -43.5, 170.5),
        ("Alps", 46.5, 8.5),
        ("Iceland", 64.4, -17.0),
        ("Greenland", 72.0, -40.0),
    ):
        jd, s = predict(harmonics(lat, lon, body=True), t0, 30 * 288)
        ours = T.areal_strain(jd, lat, lon)
        a, b = s - s.mean(), ours - ours.mean()
        rows.append(
            dict(
                site=name,
                corr=float(np.corrcoef(a, b)[0, 1]),
                rms_ratio_spotl_over_ours=float(a.std() / b.std()),
                lag_min=float(DT_S / 60 * (np.argmax(np.correlate(a, b, "full")) - len(a) + 1)),
            )
        )
    return pd.DataFrame(rows)


def _phases(
    jd: np.ndarray, la: np.ndarray, lo: np.ndarray, spl: CubicSpline
) -> dict[str, np.ndarray]:
    """Tanaka phases (+-20 h window, 5-min grid) on the body tide and on body + ocean load."""
    off = np.arange(-20 * 60, 20 * 60 + 5, 5) / 1440.0
    k0 = int(np.argmin(np.abs(off)))
    out = {"body20h": np.full(len(jd), np.nan), "total20h": np.full(len(jd), np.nan)}
    for s in range(0, len(jd), 2000):
        sl = slice(s, s + 2000)
        J = jd[sl, None] + off[None, :]
        eb = T.areal_strain(J, la[sl, None], lo[sl, None])
        out["body20h"][sl] = T.phase_from_series(eb, off, k0)
        out["total20h"][sl] = T.phase_from_series(eb + spl(J), off, k0)
    return out


def null_test(ph: np.ndarray, ph_null: np.ndarray) -> dict[str, float]:
    """Schuster-type test against the empirical phase distribution at random times.

    The Tanaka phase (linear in time between extrema) is uniform at random times only for a
    time-symmetric waveform. The body tide is close to that; adding the ocean load (other phase
    lags per constituent) skews the waveform (e.g. longer rise than fall), so the plain Schuster
    test would flag random times. Statistic: n (zbar - mu0)' S0^-1 (zbar - mu0) ~ chi2(2) with
    mu0, S0 = mean and covariance of (cos, sin) of the null pool (inflated by 1 + n/n_pool);
    reduces to the Schuster p = exp(-R^2/n) for a uniform null."""
    th = np.deg2rad(ph[np.isfinite(ph)])
    th0 = np.deg2rad(ph_null[np.isfinite(ph_null)])
    x = np.column_stack([np.cos(th), np.sin(th)])
    x0 = np.column_stack([np.cos(th0), np.sin(th0)])
    mu0, s0 = x0.mean(0), np.cov(x0.T) * (1 + len(x) / len(x0))
    dz = x.mean(0) - mu0
    stat = len(x) * float(dz @ np.linalg.solve(s0, dz))
    return dict(
        p=float(np.exp(-stat / 2)),
        a_hat=float(2 * np.hypot(*dz)),
        null_a_hat=float(2 * np.hypot(*mu0)),
        null_mean_phase_deg=float(np.degrees(np.arctan2(mu0[1], mu0[0]))),
    )


def main() -> None:
    out = v02.outdir()
    bc = body_check()
    bc.to_csv(out / "m3_ocean_load_bodycheck.csv", index=False)
    print(bc.round(4).to_string(), flush=True)
    pr = v02.prereg()["H3"]
    rows, site_rows = [], []
    regions = sys.argv[1:] or list(v02.V02_REGIONS)
    for name in regions:
        p = v02._prep(name)
        if p is None:
            continue
        d = p.decl
        d = d[d.year.between(pr["years"][0], pr["years"][1])].reset_index(drop=True)
        t = decimal_year(d.time)
        jd_ev = T.decyear_to_jd(t)
        lat, lon = d.latitude.to_numpy(float), d.longitude.to_numpy(float)
        mag = d.mag.to_numpy(float)
        cell = pd.Series(list(zip(np.floor(lat / CELL), np.floor(lon / CELL), strict=True)))
        codes, uniq = pd.factorize(cell)
        start = dt.datetime(pr["years"][0] - 1, 12, 30)
        n = int(((dt.datetime(pr["years"][1] + 1, 1, 3) - start).total_seconds()) // DT_S)
        load_amp = np.full(len(t), np.nan)
        ph = {k: np.full(len(t), np.nan) for k in ("body20h", "total20h")}
        null: dict[str, list[np.ndarray]] = {"body20h": [], "total20h": []}
        rng = np.random.default_rng(20261010)
        for c in range(len(uniq)):
            sel = np.nonzero(codes == c)[0]
            slat, slon = float(lat[sel].mean()), float(lon[sel].mean())
            jd_s, s_s = predict(harmonics(slat, slon), start, n)
            spl = CubicSpline(jd_s, s_s)
            load_amp[sel] = spl(jd_ev[sel])
            site_rows.append(
                dict(
                    region=name,
                    site=c,
                    lat=slat,
                    lon=slon,
                    n_events=len(sel),
                    load_rms_nstrain=float(s_s.std() * 1e9),
                )
            )
            for k, v in _phases(jd_ev[sel], lat[sel], lon[sel], spl).items():
                ph[k][sel] = v
            # null pool: uniform random times in the H3 years at resampled event locations
            m = max(POOL_FACTOR * len(sel), POOL_MIN)
            pick = rng.choice(sel, m)
            jd_r = T.decyear_to_jd(rng.uniform(pr["years"][0], pr["years"][1] + 1, m))
            for k, v in _phases(jd_r, lat[pick], lon[pick], spl).items():
                null[k].append(v)
        body_amp = T.areal_strain(jd_ev, lat, lon)
        row: dict[str, object] = dict(
            region=name,
            n_events=len(t),
            n_sites=len(uniq),
            rms_body_nstrain=float(body_amp.std() * 1e9),
            rms_load_nstrain=float(load_amp.std() * 1e9),
        )
        for k in ("body20h", "total20h"):
            sch = T.schuster(ph[k])
            nt = null_test(ph[k], np.concatenate(null[k]))
            bs = T.b_split_test(mag, ph[k], p.mc_ref)
            row.update(
                {
                    f"nan_frac_{k}": float(np.mean(~np.isfinite(ph[k]))),
                    f"schuster_p_{k}": sch["p"],
                    f"a_hat_{k}": sch["a_hat"],
                    f"mean_phase_{k}": sch["mean_phase_deg"],
                    f"null_a_hat_{k}": nt["null_a_hat"],
                    f"null_mean_phase_{k}": nt["null_mean_phase_deg"],
                    f"nullcorr_p_{k}": nt["p"],
                    f"nullcorr_a_hat_{k}": nt["a_hat"],
                    f"db_{k}": bs.get("d_b", np.nan),
                    f"bsplit_p_{k}": bs.get("p_one", np.nan),
                }
            )
        dphi = np.angle(np.exp(1j * np.deg2rad(ph["total20h"] - ph["body20h"])), deg=True)
        row["median_abs_phase_shift_deg"] = float(np.nanmedian(np.abs(dphi)))
        row["frac_half_swapped"] = float(
            np.nanmean((np.abs(ph["total20h"]) < 90) != (np.abs(ph["body20h"]) < 90))
        )
        rows.append(row)
        print(row, flush=True)
    df = pd.DataFrame(rows)
    glac = df.region.isin(pr["test_regions"])
    for k in ("body20h", "total20h"):
        for col in ("schuster_p", "nullcorr_p", "bsplit_p"):
            df[f"{col}_bh_{k}"] = np.nan
            df.loc[glac, f"{col}_bh_{k}"] = E.bh_adjust(df.loc[glac, f"{col}_{k}"].to_numpy())
    df.to_csv(out / "m3_tides_ocean_load.csv", index=False)
    pd.DataFrame(site_rows).to_csv(out / "m3_ocean_load_sites.csv", index=False)


if __name__ == "__main__":
    main()
