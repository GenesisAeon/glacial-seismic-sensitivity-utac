"""End-to-end analysis. Outputs go to ``config.OUT`` (CSV/JSON), charts to ``config.CHARTS``."""

from __future__ import annotations

import json
import warnings
from datetime import date

import numpy as np
import pandas as pd

from . import __version__, criticality, lagmodel, loads, power, seasonal, sensitivity
from . import config as C
from .regionrun import Prepared, prepare_region
from .stats_tests import bh

warnings.filterwarnings("ignore", category=RuntimeWarning)

# lag-model rheology key -> analysis region providing catalogue power and GRACE unloading rate
LAG_REGION_MAP = {
    "Patagonia": "Patagonia",
    "West_Antarctica": "West_Antarctica",
    "Iceland": "Iceland_Vatnajokull_IMO",
    "Greenland_SE": "Greenland_GEUS",
    "SE_Alaska": "SE_Alaska_AK",
    "Alps": "Alps_SED",
}
PRIMARY_REGION = "SE_Alaska_AK"


def _out(df: pd.DataFrame, name: str) -> None:
    C.OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.OUT / name, index=False, float_format="%.6g")


def prepare_all(regions: list[str] | None = None) -> dict[str, Prepared]:
    out = {}
    rows = []
    for name in regions or C.main_regions():
        p = prepare_region(name)
        r = C.REGIONS[name]
        if p is None:
            rows.append(dict(region=name, group=r.group, source=r.source, usable=False))
            continue
        out[name] = p
        rows.append(
            dict(
                region=name,
                group=r.group,
                source=r.source,
                tier=criticality.tier_of(name),
                usable=True,
                n_fetched=len(p.raw),
                first_year=int(p.raw.year.min()),
                mc_ref=p.mc_ref,
                n_ge_mc=len(p.dc),
                n_decl=len(p.decl),
                triggered_frac=float(p.dc.triggered.mean()),
                log_eta0=p.log_eta0,
                mc_1990s_median=float(p.mc_yearly.loc[:1999].median()),
                mc_2020s_median=float(p.mc_yearly.loc[2020:].median()),
            )
        )
        print(f"prepared {name}: Mc {p.mc_ref}, {len(p.decl)} declustered", flush=True)
    _out(pd.DataFrame(rows), "regions_meta.csv")
    return out


def run_criticality(preps: dict[str, Prepared]) -> None:
    rng = np.random.default_rng(C.SEED)
    cities = pd.read_csv(C.RAW / "geonames_cities_pop100k.csv")
    bins, trends, csds = [], [], []
    for name, p in preps.items():
        if len(p.decl) < 60:
            continue
        print("criticality", name, flush=True)
        b, t, c, ser = criticality.run_region(p, cities, rng)
        bins.append(b)
        trends.append(t)
        csds.append(c)
        (C.OUT / "series").mkdir(exist_ok=True)
        for var, s in ser.items():
            s.to_csv(C.OUT / "series" / f"csd_{name}_{var}.csv")
    tr, cs, gv = criticality.combine(pd.concat(trends), pd.concat(csds))
    _out(pd.concat(bins), "criticality_bin_indicators.csv")
    _out(tr, "criticality_trend_tests.csv")
    _out(cs, "criticality_csd_tests.csv")
    _out(gv, "criticality_group_tests.csv")


def run_sensitivity(preps: dict[str, Prepared]) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(C.SEED + 1)
    grace = loads.regional_grace()
    _out(grace, "grace_regional_monthly.csv")
    f1, f2, peryear, lags, f3, ldots = [], [], [], [], [], []
    for name, p in preps.items():
        r = C.REGIONS[name]
        d = p.decl
        n_test = int(d.year.between(1990, C.TEST_END_YEAR).sum())
        base = dict(region=name, group=r.group, tier=criticality.tier_of(name), mc_ref=p.mc_ref)
        if n_test >= C.SENS_MIN_EVENTS:
            print("F1", name, flush=True)
            h = sensitivity.harmonic_growth(d, rng=rng)
            f1.append({**base, **h})
            ph = (h["peak_month"] - 1) / 12
            peryear.append(
                sensitivity.per_year_modulation(d, ph, (1990, C.TEST_END_YEAR)).assign(
                    region=name, group=r.group
                )
            )
        if f"{name}_kPa" in grace:
            lo = loads.monthly_load(name, grace)
            hf = loads.harmonic_fit(
                (lo.month.dt.year + (lo.month.dt.month - 0.5) / 12).to_numpy(),
                lo.load_kPa.to_numpy(),
            )
            ldots.append(
                dict(
                    region=name,
                    load_trend_kPa_per_yr=hf["trend_per_yr"],
                    load_annual_amp_kPa=hf["annual_amp"],
                    load_peak_month=hf["peak_phase"] * 12 + 1,
                    n_mascons=int(grace[f"{name}_n_mascons"].iloc[0]),
                    mass_trend_Gt_per_yr=loads.harmonic_fit(
                        grace.t_yr.to_numpy(), grace[f"{name}_Gt"].to_numpy()
                    )["trend_per_yr"],
                )
            )
            n02 = int(d.year.between(2002, C.TEST_END_YEAR).sum())
            if n02 >= C.SENS_MIN_EVENTS:
                print("F2", name, flush=True)
                f2.append({**base, **sensitivity.load_growth(d, lo, rng=rng)})
                lags.append(sensitivity.lag_scan(d, lo).assign(region=name, group=r.group))
        n02 = int(d.year.between(2002, C.TEST_END_YEAR).sum())
        if name in C.PRECIP_POINTS and n02 >= C.SENS_MIN_EVENTS:
            lo_or_none = loads.monthly_load(name, grace) if f"{name}_kPa" in grace else None
            pr = loads.precip_anomaly(name)
            for lag in (0, C.SENS_LAG_MONTHS_PRIMARY):
                x = sensitivity.rain_vs_load(d, lo_or_none, pr, lag=lag)
                if len(x):
                    f3.append(x.assign(region=name, group=r.group))
    res = dict(
        f1=pd.DataFrame(f1),
        f2=pd.DataFrame(f2),
        peryear=pd.concat(peryear),
        lags=pd.concat(lags),
        f3=pd.concat(f3),
        loads=pd.DataFrame(ldots),
    )
    for key, pcol in (("f1", "b1_p_perm_one"), ("f2", "g1_p_perm_one")):
        df = res[key]
        if len(df):
            q, s = bh(df[pcol].to_numpy(float))
            res[key] = df.assign(q_BH_all_regions=q, sig_BH=s)
    # group meta-analysis of the growth coefficients, per tier
    meta = []
    for key, coef, se in (
        ("f1", "b1_per_decade", "b1_se"),
        ("f2", "g1_per_kPa_decade", "g1_se"),
        ("f2", "g0_per_kPa", "g0_se"),
        ("f1", "b0", "b0_se"),
    ):
        df = res[key]
        for (tier, grp), x in df.groupby(["tier", "group"]):
            meta.append(
                dict(
                    test=key,
                    coefficient=coef,
                    tier=tier,
                    group=grp,
                    regions=";".join(x.region),
                    **sensitivity.meta_group(x, coef, se),
                )
            )
    res["meta"] = pd.DataFrame(meta)
    names = dict(
        f1="F1_harmonic_growth.csv",
        f2="F2_load_sensitivity_growth.csv",
        peryear="F1_per_year_modulation.csv",
        lags="F2_lag_scan_exploratory.csv",
        f3="F3_rain_vs_load.csv",
        loads="grace_load_summary.csv",
        meta="F_group_meta.csv",
    )
    for k, fn in names.items():
        _out(res[k], fn)
    return res


def run_seasonal(preps: dict[str, Prepared]) -> None:
    rob, mon, clim, win, grid = [], [], [], [], []
    for name, p in preps.items():
        if criticality.tier_of(name) != "national" and name != "SE_Alaska":
            continue
        rob.append(seasonal.robustness(p))
        mon.append(seasonal.monthly_mc(p))
        clim.append(seasonal.climatology(p))
        win.append(seasonal.amplitude_windows(p))
        grid.append(seasonal.grid_map(p))
    _out(pd.concat(rob), "seasonal_robustness.csv")
    _out(pd.concat(mon), "seasonal_mc_by_month.csv")
    _out(pd.concat(clim), "seasonal_climatology.csv")
    _out(pd.concat(win), "seasonal_amplitude_windows.csv")
    _out(pd.concat(grid), "seasonal_grid_map.csv")
    if "Interior_AK_ctrl" in preps:
        _out(seasonal.kantishna_split(preps["Interior_AK_ctrl"]), "seasonal_kantishna_split.csv")


def run_lag(preps: dict[str, Prepared], sens: dict[str, pd.DataFrame]) -> pd.DataFrame:
    _out(lagmodel.relaxation_table(), "lag_relaxation_times.csv")
    f1 = sens["f1"].set_index("region") if len(sens["f1"]) else pd.DataFrame()
    ld = sens["loads"].set_index("region")
    stats_ = {}
    notes = []
    for key, reg in LAG_REGION_MAP.items():
        if reg not in preps or reg not in ld.index:
            notes.append(dict(rheology=key, region=reg, note="no usable catalogue or GRACE series"))
            continue
        d = preps[reg].decl
        n_per_yr = float(d.year.between(2016, C.TEST_END_YEAR).sum() / 10.0)
        phi = float(f1.loc[reg, "phi"]) if reg in f1.index else 1.5
        ldot = max(-float(ld.loc[reg, "load_trend_kPa_per_yr"]), 0.0)
        if n_per_yr < 1:
            notes.append(
                dict(rheology=key, region=reg, note=f"catalogue too sparse ({n_per_yr}/yr)")
            )
            continue
        stats_[key] = dict(n_per_yr=n_per_yr, phi=phi, ldot_kpa_yr=ldot)
    grid = lagmodel.scenario_grid(stats_)
    _out(grid, "lag_detection_scenarios.csv")
    _out(pd.DataFrame(notes), "lag_notes.csv")
    rows = []
    for ds in (1.0, 2.0, 10.0):
        for a_sig in (1.5, 10.0):
            for sdot0 in (10.0, 30.0):
                for extra in (0.0, 1.0, 3.0):
                    rows.append(
                        dict(
                            dS_kPa=ds,
                            a_sigma_kPa=a_sig,
                            sdot0_kPa_yr=sdot0,
                            sdot_gia_kPa_yr=extra,
                            t_a_yr=a_sig / sdot0,
                            rsm_modulation=lagmodel.seasonal_modulation(ds, a_sig, sdot0, extra),
                            approx_2piDS_over_Sdot=2 * np.pi * ds / (sdot0 + extra),
                        )
                    )
    _out(pd.DataFrame(rows), "lag_rsm_seasonal_modulation.csv")
    return grid


def run_power(preps: dict[str, Prepared], sens: dict[str, pd.DataFrame]) -> pd.DataFrame:
    f1 = sens["f1"]
    base = []
    frozen: dict[str, object] = dict(
        frozen_on=str(date(2026, 10, 10)),
        package_version=__version__,
        confirmatory_data_start=C.CONFIRMATORY_START,
        looks={k: dict(years=y, alpha=a) for k, y, a in power.LOOKS},
        primary_region=PRIMARY_REGION,
        ref_year=C.SENS_REF_YEAR,
        primary_load_lag_months=C.SENS_LAG_MONTHS_PRIMARY,
        declustering=dict(df=C.NN_DF, b=C.NN_B, max_parents=C.NN_MAX_PARENTS),
        regions={},
    )
    regs: dict[str, object] = {}
    for _, r in f1.iterrows():
        p = preps[r.region]
        rate = float(p.decl.year.between(2016, C.TEST_END_YEAR).sum() / 10.0)
        base.append(
            dict(region=r.region, rate_per_yr=rate, b_ref=r.b0, b_ref_se=r.b0_se, phi=r.phi)
        )
        regs[r.region] = dict(
            mc=p.mc_ref,
            log_eta0=p.log_eta0,
            phase_peak_month=r.peak_month,
            b_ref=r.b0,
            b_ref_se=r.b0_se,
            b1_per_decade=r.b1_per_decade,
            rate_decl_per_yr_2016_2025=rate,
            box=list(C.REGIONS[r.region].box),
            source=C.REGIONS[r.region].source,
            maxdepth=C.REGIONS[r.region].maxdepth,
        )
    frozen["regions"] = regs
    # never overwrite the frozen file: later runs write a separate copy for comparison
    target = C.OUT / "frozen_confirmatory_parameters.json"
    if target.exists():
        target = C.OUT / "frozen_confirmatory_parameters_RECOMPUTED.json"
    target.write_text(json.dumps(frozen, indent=1, default=float))
    pt = power.power_table(pd.DataFrame(base))
    _out(pt, "confirmatory_power.csv")
    return pt


def run_all(regions: list[str] | None = None, criticality_battery: bool = True) -> None:
    C.OUT.mkdir(parents=True, exist_ok=True)
    preps = prepare_all(regions)
    sens = run_sensitivity(preps)
    run_seasonal(preps)
    run_lag(preps, sens)
    run_power(preps, sens)
    if criticality_battery:
        run_criticality(preps)
    cfg = {k: getattr(C, k) for k in dir(C) if k.isupper() and k not in ("REGIONS",)}
    (C.OUT / "run_config.json").write_text(
        json.dumps(
            dict(
                version=__version__, config=cfg, regions={k: vars(v) for k, v in C.REGIONS.items()}
            ),
            indent=1,
            default=str,
        )
    )
