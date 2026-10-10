"""EXPLORATORY (open item b): network changes as a confounder of H2.1 (SE Alaska minus Interior
Alaska, yearly ETAS residual background log mu_y, 1995-2025).

Covariates per region and year:
* ``mc_y``: yearly completeness magnitude of the catalogue (MAXC + 0.2, as in v0.1.0), from the
  same events as the H2 fit;
* ``n_sta``: number of seismic stations (channels BH?/HH?/EH?/SH?) open on 1 July inside the region
  box, from the EarthScope (formerly IRIS) FDSN station service
  (https://service.earthscope.org/fdsnws/station/1/), all networks and permanent networks only
  (AK, AT, AV, US, IU, II, CN). Caveat: the FDSN metadata do not contain all historical short-period
  stations of the Alaska Earthquake Center, and temporary networks did not necessarily feed the
  catalogue - station counts are a rough proxy, especially before 2000.

Models (OLS over years, slope per decade of the glacier-minus-control difference d_y):
d_y ~ t; d_y ~ t + delta_mc; d_y ~ t + delta_log_nsta; d_y ~ t + both; and d_y ~ t on years with
both catalogues complete at Mc_ref (mc_y <= Mc_ref). Not preregistered; the H2.1 decision stands.
Writes results/v02/h21_network_covariates.csv (yearly data) and h21_network_models.csv."""

from __future__ import annotations

import io
import urllib.request

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import v02
from glacial_seismic_sensitivity_utac.config import REGIONS

PAIR = ("SE_Alaska_AK", "Interior_AK_ctrl")
PERMANENT = {"AK", "AT", "AV", "US", "IU", "II", "CN"}
FDSN = (
    "https://service.earthscope.org/fdsnws/station/1/query?minlat={0}&maxlat={1}&minlon={2}"
    "&maxlon={3}&level=channel&channel=BH?,HH?,EH?,SH?&format=text&nodata=404"
)
YEARS = np.arange(1995, 2026)


def stations(name: str) -> pd.DataFrame:
    url = FDSN.format(*REGIONS[name].box)
    with urllib.request.urlopen(url, timeout=300) as r:  # noqa: S310 (fixed https URL)
        txt = r.read().decode("utf-8")
    d = pd.read_csv(io.StringIO(txt), sep="|")
    d.columns = [c.strip().lstrip("#").strip() for c in d.columns]
    d["s"] = pd.to_datetime(d.StartTime.str[:19])
    d["e"] = pd.to_datetime(d.EndTime.str[:19], errors="coerce").fillna(pd.Timestamp("2262-01-01"))
    return d.groupby(["Network", "Station"]).agg(s=("s", "min"), e=("e", "max")).reset_index()


def yearly(name: str) -> pd.DataFrame:
    st = stations(name)
    p = v02._prep(name)
    assert p is not None
    mu = pd.read_csv(v02.outdir() / f"m2_mu_{name}.csv")
    rows = []
    for y in YEARS:
        on = (st.s <= pd.Timestamp(f"{y}-07-01")) & (st.e >= pd.Timestamp(f"{y}-07-01"))
        rows.append(
            dict(
                region=name,
                year=int(y),
                log_mu=float(mu.loc[mu.t_start == y, "log_mu"].iloc[0]),
                mc_y=float(p.mc_yearly.get(y, np.nan)),
                mc_ref=p.mc_ref,
                n_sta_all=int(on.sum()),
                n_sta_perm=int((on & st.Network.isin(PERMANENT)).sum()),
            )
        )
    return pd.DataFrame(rows)


def ols(y: np.ndarray, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    s2 = r @ r / (len(y) - X.shape[1])
    return beta, np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))


def main() -> None:
    g, c = (yearly(n) for n in PAIR)
    yd = pd.concat([g, c])
    yd.to_csv(v02.outdir() / "h21_network_covariates.csv", index=False)
    d = g.merge(c, on="year", suffixes=("_g", "_c"))
    d["dy"] = d.log_mu_g - d.log_mu_c
    d["dmc"] = d.mc_y_g - d.mc_y_c
    d["dlogn_all"] = np.log1p(d.n_sta_all_g) - np.log1p(d.n_sta_all_c)
    d["dlogn_perm"] = np.log1p(d.n_sta_perm_g) - np.log1p(d.n_sta_perm_c)
    t = (d.year.to_numpy() + 0.5 - 2010.5) / 10
    models = {
        "trend only": [],
        "+ delta Mc_y": ["dmc"],
        "+ delta log(1+N_sta), all networks": ["dlogn_all"],
        "+ delta log(1+N_sta), permanent": ["dlogn_perm"],
        "+ delta Mc_y + delta log N (permanent)": ["dmc", "dlogn_perm"],
    }
    rows = []
    for lab, cov in models.items():
        X = np.column_stack([np.ones(len(d)), t] + [d[k].to_numpy() for k in cov])
        b, se = ols(d.dy.to_numpy(), X)
        row = dict(model=lab, n_years=len(d), slope_per_decade=b[1], se_ols=se[1])
        for k, bb, ss in zip(cov, b[2:], se[2:], strict=True):
            row[f"coef_{k}"], row[f"se_{k}"] = bb, ss
        rows.append(row)
    ok = (d.mc_y_g <= d.mc_ref_g) & (d.mc_y_c <= d.mc_ref_c)
    X = np.column_stack([np.ones(ok.sum()), t[ok]])
    b, se = ols(d.dy.to_numpy()[ok], X)
    rows.append(
        dict(
            model="trend only, years with Mc_y <= Mc_ref in both",
            n_years=int(ok.sum()),
            slope_per_decade=b[1],
            se_ols=se[1],
        )
    )
    out = pd.DataFrame(rows)
    out["z_ols"] = out.slope_per_decade / out.se_ols
    out.to_csv(v02.outdir() / "h21_network_models.csv", index=False)
    print(out.round(3).to_string())
    print(d[["year", "dy", "mc_y_g", "mc_y_c", "n_sta_perm_g", "n_sta_perm_c"]].to_string())


if __name__ == "__main__":
    main()
