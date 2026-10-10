"""Charts (PNG) from the CSV results in ``config.OUT``."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from . import config as C  # noqa: E402
from . import lagmodel  # noqa: E402

GROUP_COLOR = {"mountain": "C0", "icesheet": "C2", "control": "C3"}


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(C.OUT / name)


def _save(fig: Figure, name: str) -> None:
    C.CHARTS.mkdir(parents=True, exist_ok=True)
    fig.savefig(C.CHARTS / name, dpi=140, bbox_inches="tight")
    plt.close(fig)


def forest(df: pd.DataFrame, coef: str, se: str, title: str, xlabel: str, fname: str) -> None:
    df = df.sort_values(["group", "tier", "region"]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.5, 0.38 * len(df) + 1.5))
    for i, r in df.iterrows():
        c = GROUP_COLOR.get(r.group, "k")
        ax.errorbar(
            r[coef],
            i,
            xerr=1.96 * r[se],
            fmt="o",
            color=c,
            mfc=c if r.tier == "national" else "white",
        )
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([f"{r.region} ({r.group})" for _, r in df.iterrows()], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_title(
        title + "\nfilled: national/regional network, open: ComCat M>=Mc; bars 95 % CI", fontsize=9
    )
    ax.grid(alpha=0.3)
    _save(fig, fname)


def chart_mc() -> None:
    meta = _read("regions_meta.csv")
    fig, ax = plt.subplots(figsize=(9, 4))
    for _, r in meta[meta.usable & (meta.tier == "national")].iterrows():
        ax.plot(
            [1995, 2023],
            [r.mc_1990s_median, r.mc_2020s_median],
            "o-",
            color=GROUP_COLOR[r.group],
            label=r.region,
        )
        ax.text(2023.3, r.mc_2020s_median, r.region, fontsize=7, va="center")
    ax.set_xlim(1993, 2033)
    ax.set_ylabel("median yearly Mc (MAXC+0.2)")
    ax.set_title(
        "Completeness 1990s vs 2020s (national networks) - year fixed effects absorb this",
        fontsize=9,
    )
    ax.grid(alpha=0.3)
    _save(fig, "01_completeness_change.png")


def chart_climatology() -> None:
    cl = _read("seasonal_climatology.csv")
    regs = list(dict.fromkeys(cl.region))
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for r in regs:
        s = cl[cl.region == r]
        y = s["count"] / s["count"].mean()
        grp = C.REGIONS[r].group
        ax.plot(
            s.month,
            y,
            "-o",
            ms=3,
            color=GROUP_COLOR[grp],
            lw=2.2 if r in ("SE_Alaska_AK", "Interior_AK_ctrl") else 0.9,
            alpha=1 if r in ("SE_Alaska_AK", "Interior_AK_ctrl") else 0.5,
            label=r,
        )
    ax.axhline(1, color="k", lw=0.6)
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("calendar month")
    ax.set_ylabel("declustered events / monthly mean")
    ax.set_title("Monthly climatology 1990-2025 (declustered, >= Mc)", fontsize=9)
    ax.legend(fontsize=6, ncol=3)
    ax.grid(alpha=0.3)
    _save(fig, "02_monthly_climatology.png")


def chart_peryear() -> None:
    py = _read("F1_per_year_modulation.csv")
    f1 = _read("F1_harmonic_growth.csv").set_index("region")
    regs = [
        r
        for r in (
            "SE_Alaska_AK",
            "Interior_AK_ctrl",
            "Iceland_Vatnajokull_IMO",
            "NZ_Southern_Alps",
            "Alps_SED",
            "Greenland_GEUS",
        )
        if r in f1.index
    ]
    fig, axs = plt.subplots(2, 3, figsize=(14, 7), sharex=True)
    for ax, r in zip(axs.ravel(), regs, strict=False):
        s = py[py.region == r]
        ax.errorbar(
            s.year, s.b, yerr=s.se, fmt="o", ms=3, color=GROUP_COLOR[C.REGIONS[r].group], alpha=0.7
        )
        t = np.arange(1990, 2026)
        fr = f1.loc[r]
        ax.plot(
            t,
            fr.b0 + fr.b1_per_decade * (t + 0.5 - C.SENS_REF_YEAR) / 10,
            "k-",
            label=f"b1 = {fr.b1_per_decade:+.3f}/decade (perm p={fr.b1_p_perm_one:.2f})",
        )
        ax.axhline(0, color="gray", lw=0.6)
        ax.set_ylim(-1.2, 1.5)
        ax.set_title(r, fontsize=9)
        ax.legend(fontsize=7, loc="upper left")
        ax.grid(alpha=0.3)
    fig.suptitle(
        "F1 'Fruehstadium': yearly seasonal modulation b_y along the 1990-2025 mean phase "
        "(+-1 SE) and the fitted growth model",
        fontsize=10,
    )
    _save(fig, "03_F1_per_year_modulation.png")


def chart_load_series() -> None:
    from . import loads, sensitivity
    from .regionrun import prepare_region

    p = prepare_region("SE_Alaska_AK")
    if p is None:
        return
    g = _read("grace_regional_monthly.csv")
    g["month"] = pd.to_datetime(g.month)
    lo = loads.monthly_load("SE_Alaska_AK", g)
    tab = sensitivity.monthly_table(p.decl, 2002, C.TEST_END_YEAR)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(lo.month, lo.unload_kPa, color="C0", lw=1, label="GRACE seasonal unloading U [kPa]")
    ax.set_ylabel("U [kPa] (regional mean)", color="C0")
    ax2 = ax.twinx()
    ax2.plot(
        tab.month,
        tab["count"].rolling(3, center=True).mean(),
        color="C3",
        lw=1,
        label="declustered events / month (3-mo mean)",
    )
    ax2.set_ylabel("events per month", color="C3")
    ax.set_title(
        "SE Alaska (AEC catalogue, M>=Mc, <=40 km): seasonal unloading vs seismicity", fontsize=9
    )
    ax.grid(alpha=0.3)
    _save(fig, "05_SE_Alaska_load_vs_rate.png")


def chart_lagscan() -> None:
    ls = _read("F2_lag_scan_exploratory.csv")
    regs = [
        r
        for r in (
            "SE_Alaska_AK",
            "Interior_AK_ctrl",
            "Iceland_Vatnajokull_IMO",
            "NZ_Southern_Alps",
            "Alps_SED",
            "NZ_Wellington_ctrl",
        )
        if r in set(ls.region)
    ]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, r in enumerate(regs):
        s = ls[ls.region == r]
        ax.errorbar(
            s.lag_months + (i - len(regs) / 2) * 0.07,
            s.g0_per_kPa * 100,
            yerr=196 * s.g0_se,
            fmt="-o",
            ms=3,
            label=f"{r} ({C.REGIONS[r].group})",
            color=f"C{i}",
            lw=2.2 if r == "SE_Alaska_AK" else 1.0,
        )
    ax.axhline(0, color="k", lw=0.6)
    ax.axhline(3.5, color="gray", ls="--", lw=0.8)
    ax.text(5.2, 4.5, "Johnson et al. 2020: 3.5 %/kPa", fontsize=7, color="gray")
    ax.axvline(3, color="k", ls=":", lw=0.8)
    ax.set_xlabel("lag of seismicity behind unloading [months] (dotted: pre-registered lag 3)")
    ax.set_ylabel("rate change per kPa (regional-mean GRACE) [%]")
    ax.set_title("F2 exploratory lag scan, 2002-2025, 95 % CI", fontsize=9)
    ax.set_ylim(-35, 40)
    ax.legend(fontsize=7, ncol=2)
    ax.grid(alpha=0.3)
    _save(fig, "06_F2_lag_scan.png")


def chart_f3() -> None:
    f3 = _read("F3_rain_vs_load.csv")
    regs = list(dict.fromkeys(f3.region))
    fig, axs = plt.subplots(1, len(regs), figsize=(3.0 * len(regs), 3.6), sharey=True)
    for ax, r in zip(np.atleast_1d(axs), regs, strict=False):
        s = f3[(f3.region == r) & (f3.lag_months == C.SENS_LAG_MONTHS_PRIMARY)]
        s = s[s.model != "null(year FE only)"]
        ax.barh(s.model, s.dQAIC_vs_null, color="C0")
        ax.axvline(-2, color="gray", ls="--", lw=0.8)
        ax.set_title(f"{r}\nlag 3 mo", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.3)
    fig.suptitle(
        "F3 rain vs load: Delta QAIC against year-FE-only model (more negative = better)",
        fontsize=9,
    )
    _save(fig, "07_F3_rain_vs_load.png")


def chart_relaxation() -> None:
    lam = np.logspace(np.log10(50), np.log10(3000), 100)
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, r in enumerate(lagmodel.RHEOLOGIES.values()):
        tau = [lagmodel.relaxation_time_yr(r.eta, x, r.te_km) for x in lam]
        tau0 = [lagmodel.relaxation_time_yr(r.eta, x, 0.0) for x in lam]
        ax.loglog(
            lam, tau, color=f"C{i}", label=f"{r.region}: eta={r.eta:.1e} Pa s, Te={r.te_km:g} km"
        )
        ax.loglog(lam, tau0, color=f"C{i}", ls=":", lw=0.8)
    ax.set_xlabel("load wavelength lambda [km]")
    ax.set_ylabel("relaxation time tau [yr]")
    ax.set_title(
        "GIA relaxation time (solid: with elastic plate; dotted: half-space)\n"
        "tau = 4 pi eta / (rho g lambda) x 1/(1 + D k^4 / rho g)",
        fontsize=9,
    )
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3, which="both")
    _save(fig, "08_lag_relaxation_times.png")


def chart_rate_ratio() -> None:
    g = _read("lag_detection_scenarios.csv")
    g = g[(g.kappa == 1.0) & (g.sdot0_kpa_yr == 10.0)]
    t = np.arange(1990, 2301)
    fig, ax = plt.subplots(figsize=(9, 5))
    rcol = {reg: f"C{k}" for k, reg in enumerate(dict.fromkeys(g.region))}
    for _, r in g.iterrows():
        rr = lagmodel.rate_ratio(
            t, 1995.0, r.tau_yr, r.ldot_kpa_yr, r.kappa, r.compensation, r.sdot0_kpa_yr
        )
        ls = "-" if r.load_rate_scenario == "glacier_surface" else ":"
        ax.plot(
            t,
            (rr - 1) * 100,
            ls,
            color=rcol[r.region],
            lw=1.6 if r.load_rate_scenario == "glacier_surface" else 1.0,
            label=f"{r.region} eta={r.eta_Pa_s:.1e} ({r.load_rate_scenario})",
        )
    ax.set_xlabel("year")
    ax.set_ylabel("GIA-induced rate increase [%]")
    ax.set_title(
        "Upper-end scenario (kappa=1, Sdot0=10 kPa/yr): delayed (viscous) part of the rate\n"
        "response to constant unloading since 1995. Not a forecast. "
        "(colour = region; solid = glacier-surface load, dotted = GRACE box mean)",
        fontsize=9,
    )
    ax.legend(fontsize=5.5, ncol=2)
    ax.grid(alpha=0.3)
    _save(fig, "09_lag_rate_ratio_scenarios.png")


def chart_rsm() -> None:
    r = _read("lag_rsm_seasonal_modulation.csv")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for (ds, a, s0), x in r.groupby(["dS_kPa", "a_sigma_kPa", "sdot0_kPa_yr"]):
        ax.plot(
            x.sdot_gia_kPa_yr,
            x.rsm_modulation,
            "-o",
            ms=3,
            label=f"dS={ds:g} kPa, a sigma={a:g}, Sdot0={s0:g}",
        )
    ax.set_xlabel("added (GIA) stressing rate [kPa/yr]")
    ax.set_ylabel("relative seasonal modulation")
    ax.set_yscale("log")
    ax.set_title(
        "Rate-and-state: seasonal modulation *falls* when background stressing rate rises",
        fontsize=9,
    )
    ax.legend(fontsize=6)
    ax.grid(alpha=0.3, which="both")
    _save(fig, "10_rsm_modulation_vs_stressing_rate.png")


def chart_power() -> None:
    pw = _read("confirmatory_power.csv")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for look, m in (("look1_2029-10-31", "o"), ("final_2036-10-31", "s")):
        s = pw[pw.look == look].sort_values("region")
        ax.scatter(s.mde_b_diff, s.region, marker=m, label=look)
        ax.scatter(s.b_ref, s.region, marker="|", color="k", s=80)
    ax.set_xlabel("minimal detectable increase of seasonal modulation (b_new - b_ref), power 80 %")
    ax.set_title("Confirmatory test power (|: current modulation b_ref 1990-2025)", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.tick_params(labelsize=7)
    _save(fig, "11_confirmatory_power.png")


def chart_heatmap() -> None:
    f = C.OUT / "criticality_trend_tests.csv"
    if not f.exists():
        return
    t = _read("criticality_trend_tests.csv")
    c = _read("criticality_csd_tests.csv")
    c = c.assign(indicator="csd_" + c.indicator + "_" + c.variant)
    a = pd.concat(
        [
            t[["region", "indicator", "tau", "p", "sig_BH"]],
            c[["region", "indicator", "tau", "p", "sig_BH"]],
        ]
    )
    order = {"mountain": 0, "icesheet": 1, "control": 2}
    regs = sorted(set(a.region), key=lambda r: (order[C.REGIONS[r].group], r))
    inds = list(dict.fromkeys(a.indicator))
    m = a.pivot(index="indicator", columns="region", values="tau").reindex(index=inds, columns=regs)
    p = a.pivot(index="indicator", columns="region", values="p").reindex(index=inds, columns=regs)
    s = a.pivot(index="indicator", columns="region", values="sig_BH").reindex(
        index=inds, columns=regs
    )
    fig, ax = plt.subplots(figsize=(13, 12))
    im = ax.imshow(m.to_numpy(float), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            v = m.iat[i, j]
            if not np.isfinite(v):
                continue
            mark = (
                "**"
                if s.iat[i, j] is True or s.iat[i, j] == 1
                else ("*" if p.iat[i, j] < 0.05 else "")
            )
            ax.text(j, i, f"{v:+.2f}{mark}", ha="center", va="center", fontsize=5.5)
    ax.set_xticks(range(len(regs)))
    ax.set_xticklabels([f"{r} ({C.REGIONS[r].group[:4]})" for r in regs], rotation=70, fontsize=7)
    ax.set_yticks(range(len(inds)))
    ax.set_yticklabels(inds, fontsize=7)
    plt.colorbar(im, ax=ax, shrink=0.5, label="Kendall tau, trend 1990-2025")
    ax.set_title(
        "Criticality battery: * p<0.05 uncorrected, ** significant after BH (FDR 5 %)", fontsize=9
    )
    _save(fig, "12_criticality_heatmap.png")


def chart_gridmap() -> None:
    gm = _read("seasonal_grid_map.csv")
    gm = gm[gm.region.isin(["SE_Alaska_AK", "Interior_AK_ctrl"])]
    if not len(gm):
        return
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sc = ax.scatter(
        gm.lon0 + 0.5,
        gm.lat0 + 0.5,
        c=gm.peak_month,
        cmap="twilight",
        vmin=1,
        vmax=13,
        s=40 + 1500 * gm.amp,
        edgecolors=["k" if pv < 0.05 else "none" for pv in gm.p],
        linewidths=1.5,
    )
    for _, x in gm.iterrows():
        ax.text(x.lon0 + 0.5, x.lat0 + 0.5, f"{x.n:.0f}", fontsize=5.5, ha="center", va="center")
    plt.colorbar(sc, ax=ax, label="peak month (1 = 1 Jan)")
    ax.add_patch(Rectangle((-152, 62.8), 2, 1, fill=False, ls="--", color="gray", lw=0.8))
    ax.text(-152, 62.6, "Kantishna (approx.)", fontsize=7, color="gray")
    ax.set_xlabel("lon")
    ax.set_ylabel("lat")
    ax.set_title(
        "Seasonal peak month per 1 deg cell, declustered AEC events 1990-2025 (size ~ amplitude,"
        "\nblack edge: p<0.05 uncorrected; number = events)",
        fontsize=9,
    )
    ax.grid(alpha=0.3)
    _save(fig, "13_alaska_phase_map.png")


def all_charts() -> None:
    f1 = _read("F1_harmonic_growth.csv")
    f2 = _read("F2_load_sensitivity_growth.csv")
    for fn in (chart_mc, chart_climatology, chart_peryear):
        fn()
    forest(
        f1,
        "b1_per_decade",
        "b1_se",
        "F1: change of seasonal modulation per decade (1990-2025)",
        "b1 [per decade]",
        "04a_F1_forest_b1.png",
    )
    forest(
        f2.assign(g0_pct=f2.g0_per_kPa * 100, g0_se_pct=f2.g0_se * 100),
        "g0_pct",
        "g0_se_pct",
        "F2: seismicity change per kPa seasonal unloading (lag 3 mo, 2002-2025)",
        "% per kPa",
        "04b_F2_forest_g0.png",
    )
    forest(
        f2,
        "g1_per_kPa_decade",
        "g1_se",
        "F2: change of the per-kPa sensitivity per decade",
        "g1 [per kPa per decade]",
        "04c_F2_forest_g1.png",
    )
    for fn in (
        chart_load_series,
        chart_lagscan,
        chart_f3,
        chart_relaxation,
        chart_rate_ratio,
        chart_rsm,
        chart_power,
        chart_heatmap,
        chart_gridmap,
    ):
        fn()
