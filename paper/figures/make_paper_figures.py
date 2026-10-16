"""Figures for the P133 preprint (paper/P133_preprint.tex).

Every panel is drawn from committed result files under results/ (no recomputation, no typed-in
numbers except the fixed M1 threshold 0.02/yr from PREREGISTRATION.md section 6).
Usage: python paper/figures/make_paper_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results"
OUT = Path(__file__).resolve().parent
ICE, CTL, GREY, ACC = "#1f6fa8", "#d9822b", "#6b7682", "#b23a48"
plt.rcParams.update(
    {
        "font.size": 8.5,
        "axes.titlesize": 9,
        "axes.labelsize": 8.5,
        "legend.fontsize": 7.5,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": "#e6e6e6",
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
    }
)
W = 6.6  # inches, text width

NICE = {
    "SE_Alaska_AK": "SE Alaska (AEC)",
    "Interior_AK_ctrl": "Interior Alaska (AEC, control)",
    "NZ_Southern_Alps": "NZ Southern Alps",
    "NZ_Wellington_ctrl": "NZ Wellington (control)",
    "Alps_SED": "Alps (SED)",
    "N_Switzerland_ctrl": "N Switzerland (control)",
    "Iceland_Vatnajokull_IMO": "Iceland, Vatnaj\u00f6kull (IMO)",
    "Greenland_GEUS": "Greenland (GEUS)",
    "SE_Alaska": "SE Alaska (ComCat)",
    "Himalaya_Karakoram": "Himalaya-Karakoram (ComCat)",
    "Philippines": "Philippines",
    "Indonesia": "Indonesia",
    "Japan": "Japan",
    "Central_America": "Central America",
    "Central_Andes": "Central Andes",
    "Central_Andes_N_Chile": "Central Andes / N Chile",
    "Patagonia_South_Andes": "Patagonia / S Andes",
    "Alps": "Alps",
    "Greenland_Baffin": "Greenland + Baffin Bay",
    "Iceland": "Iceland",
    "SE_Alaska_Yakutat_Fairweather": "SE Alaska",
}
CONTROLS = {
    "Interior_AK_ctrl",
    "NZ_Wellington_ctrl",
    "N_Switzerland_ctrl",
    "Philippines",
    "Indonesia",
    "Japan",
    "Central_America",
    "Central_Andes",
}


def _save(fig: plt.Figure, name: str) -> None:
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=200)
    plt.close(fig)


def fig_global() -> None:
    g = pd.read_csv(RES / "global" / "global_counts_per_year.csv")
    g = g[g.year <= 2025]
    rr = pd.read_csv(RES / "global" / "ice_vs_control_rate_ratios.csv")
    rr = rr[rr.series == "M>=5 declustered"]
    fig, ax = plt.subplots(
        1, 2, figsize=(W, 2.9), gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.75)
    )
    a = ax[0]
    a.plot(g.year, g.M6_all, color=GREY, lw=1.1, label="M$\\geq$6, all")
    a.plot(g.year, g.M6_declustered, color=ICE, lw=1.4, label="M$\\geq$6, declustered")
    a.plot(g.year, g.M7_all, color=CTL, lw=1.4, label="M$\\geq$7, all")
    a.axvspan(1975, 1983, color="#f2f2f2", zorder=0)
    a.text(1975.6, 160, "few M$_w$\nbefore\n~1983", fontsize=6.3, color=GREY)
    a.set_xlim(1975, 2025)
    a.set_ylim(0, None)
    a.set_ylabel("events per year (global)")
    a.set_title("(a) Global ComCat counts, 1975-2025", loc="left")
    a.legend(loc="upper right", ncol=1, frameon=False, fontsize=6.6)
    a.set_ylim(0, 260)
    b = ax[1]
    rows = [
        r for r in rr.itertuples() if np.isfinite(r.ratio) and r.n_1995_2009 + r.n_2010_2024 >= 5
    ]
    order = [r for r in rows if r.group == "glaciated" and not r.region.startswith("POOLED")]
    order += [r for r in rows if r.region == "POOLED glaciated"]
    order += [r for r in rows if r.group != "glaciated" and not r.region.startswith("POOLED")]
    order += [r for r in rows if r.region.startswith("POOLED control")]
    n = len(order)
    for i, r in enumerate(order):
        y = n - i
        c = ICE if r.group == "glaciated" else CTL
        pooled = r.region.startswith("POOLED")
        b.plot(
            [max(r.ci_low, 0.12), min(r.ci_high, 20)], [y, y], color=c, lw=2.2 if pooled else 1.2
        )
        b.plot(r.ratio, y, "D" if pooled else "o", color=c, ms=5 if pooled else 3.5)
    labels = [
        ("Glaciated, pooled" if r.region == "POOLED glaciated" else "Controls, pooled")
        if r.region.startswith("POOLED")
        else NICE.get(r.region, r.region)
        for r in order
    ]
    b.set_yticks(range(n, 0, -1), labels)
    b.set_xscale("log")
    b.set_xticks([0.2, 0.5, 1, 2, 5, 10], ["0.2", "0.5", "1", "2", "5", "10"])
    b.set_xlim(0.12, 20)
    b.axvline(1, color="k", lw=0.6, ls="--")
    b.set_xlabel("rate ratio 2010-24 / 1995-2009")
    b.set_title("(b) M$\\geq$5 declustered, ice vs control", loc="left")
    _save(fig, "fig01_global_baseline")


def fig_seasonal() -> None:
    c = pd.read_csv(RES / "seasonal_climatology.csv")
    f1 = pd.read_csv(RES / "F1_harmonic_growth.csv").set_index("region")
    y = pd.read_csv(RES / "F1_per_year_modulation.csv")
    fig, ax = plt.subplots(1, 2, figsize=(W, 2.9), gridspec_kw=dict(wspace=0.3))
    a = ax[0]
    for reg, col in (("SE_Alaska_AK", ICE), ("Interior_AK_ctrl", CTL)):
        d = c[c.region == reg].sort_values("month")
        a.plot(
            d.month, d["count"] / d["count"].mean(), "o-", color=col, lw=1.3, ms=3, label=NICE[reg]
        )
    a.axhline(1, color="k", lw=0.6)
    a.set_xticks(range(1, 13))
    a.set_xlabel("calendar month")
    a.set_ylabel("declustered events / monthly mean")
    a.set_title("(a) Monthly climatology 1990-2025", loc="left")
    a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1, fontsize=6.8)
    b = ax[1]
    for reg, col, dx in (("SE_Alaska_AK", ICE, -0.15), ("Interior_AK_ctrl", CTL, 0.15)):
        d = y[y.region == reg]
        b.errorbar(d.year + dx, d.b, yerr=d.se, fmt="o", ms=2.5, lw=0.7, color=col, alpha=0.8)
        r = f1.loc[reg]
        xx = np.array([1990, 2025])
        b.plot(
            xx,
            r.b0 + r.b1_per_decade * (xx - 2008) / 10,
            color=col,
            lw=1.5,
            label=f"{NICE[reg].split(' (')[0]}: $\\beta_1$ = {r.b1_per_decade:+.3f}/decade",
        )
    b.axhline(0, color="k", lw=0.6)
    b.set_ylim(-0.9, 0.9)
    b.set_xlabel("year")
    b.set_ylabel("yearly modulation $b_y$ ($\\pm$1 SE)")
    b.set_title("(b) Seasonal modulation per year (F1)", loc="left")
    b.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1, fontsize=6.8)
    _save(fig, "fig02_seasonal_se_alaska")


def _forest(
    ax: plt.Axes,
    df: pd.DataFrame,
    est: str,
    se: str,
    scale: float,
    xlabel: str,
    title: str,
    order: list[str] | None = None,
) -> None:
    order = list(df.region) if order is None else order
    n = len(order)
    for r in df.itertuples():
        yv = n - order.index(r.region)
        col = CTL if r.region in CONTROLS else ICE
        m, s = getattr(r, est) * scale, getattr(r, se) * scale
        ax.plot([m - 1.96 * s, m + 1.96 * s], [yv, yv], color=col, lw=1.2)
        ax.plot(m, yv, "o", color=col, ms=3.2)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_yticks(range(n, 0, -1), [NICE.get(r, r) for r in order])
    ax.set_ylim(0.4, n + 0.6)
    ax.set_xlabel(xlabel)
    ax.set_title(title, loc="left")


def fig_growth() -> None:
    f1 = pd.read_csv(RES / "F1_harmonic_growth.csv")
    f2 = pd.read_csv(RES / "F2_load_sensitivity_growth.csv")
    nat = [
        "SE_Alaska_AK",
        "Alps_SED",
        "NZ_Southern_Alps",
        "Iceland_Vatnajokull_IMO",
        "Greenland_GEUS",
        "Interior_AK_ctrl",
        "N_Switzerland_ctrl",
        "NZ_Wellington_ctrl",
    ]
    f1 = f1.set_index("region").loc[nat].reset_index()
    nat2 = [r for r in nat if r in set(f2.region)]
    f2 = f2.set_index("region").loc[nat2].reset_index()
    fig, ax = plt.subplots(1, 3, figsize=(W, 2.7), sharey=False, gridspec_kw=dict(wspace=0.15))
    _forest(
        ax[0], f1, "b1_per_decade", "b1_se", 1.0, "$\\beta_1$ (per decade)", "(a) F1: growth", nat
    )
    _forest(
        ax[1],
        f2,
        "g0_per_kPa",
        "g0_se",
        100.0,
        "$\\gamma_0$ (% per kPa)",
        "(b) F2: sensitivity",
        nat,
    )
    _forest(
        ax[2],
        f2,
        "g1_per_kPa_decade",
        "g1_se",
        100.0,
        "$\\gamma_1$ (% per kPa per decade)",
        "(c) F2: growth",
        nat,
    )
    for a in ax[1:]:
        a.set_yticklabels([""] * len(nat))
    ax[2].set_xlim(-60, 60)
    ax[1].set_xlim(-30, 45)
    _save(fig, "fig03_growth_tests")


def fig_h21() -> None:
    fig, ax = plt.subplots(
        1, 2, figsize=(W, 2.8), gridspec_kw=dict(width_ratios=[1.1, 1], wspace=0.95)
    )
    a = ax[0]
    for reg, col in (("SE_Alaska_AK", ICE), ("Interior_AK_ctrl", CTL)):
        d = pd.read_csv(RES / "v02" / f"m2_mu_{reg}.csv")
        t = (d.t_start + d.t_end) / 2
        lo = np.exp(d.log_mu - 1.96 * 1.25 * d.log_mu_se)
        hi = np.exp(d.log_mu + 1.96 * 1.25 * d.log_mu_se)
        a.fill_between(t, lo, hi, color=col, alpha=0.18, lw=0)
        a.plot(t, d.mu_per_yr, "o-", color=col, ms=2.5, lw=1.2, label=NICE[reg].split(" (")[0])
    a.axvspan(1995, 2003, color="#f2f2f2", zorder=0)
    a.set_yscale("log")
    a.set_xlim(1995, 2026)
    a.set_ylabel("ETAS background $\\mu_y$ (events/yr $\\geq M_c$)")
    a.set_title("(a) Yearly ETAS background, 95% band", loc="left")
    a.set_ylim(2, 600)
    a.legend(frameon=False, loc="lower right", ncol=1, fontsize=6.8)
    b = ax[1]
    r = pd.read_csv(RES / "v02" / "m2_exploratory_robustness.csv").set_index(["variant", "years"])
    nm = pd.read_csv(RES / "v02" / "h21_network_models.csv").set_index("model")
    rows = [
        ("Preregistered (1995-2025)", r.loc[("two_stage", "1995-2025")], True),
        ("Start 2003", r.loc[("two_stage", "2003-2025")], False),
        ("Without 2025", r.loc[("two_stage", "1995-2024")], False),
        ("Joint estimator", r.loc[("joint", "1995-2025")], False),
        ("Joint, start 2003", r.loc[("joint", "2003-2025")], False),
        ("Omori p free", r.loc[("two_stage_p_free", "1995-2025")], False),
        ("tmax 3 yr", r.loc[("two_stage_tmax3", "1995-2025")], False),
    ]
    n = len(rows) + 2
    for i, (_lab, x, pre) in enumerate(rows):
        yv = n - i
        col = "k" if pre else GREY
        b.plot(
            [x.diff_per_decade - 1.96 * x.se, x.diff_per_decade + 1.96 * x.se],
            [yv, yv],
            color=col,
            lw=1.3,
        )
        b.plot(x.diff_per_decade, yv, "D" if pre else "o", color=col, ms=4 if pre else 3)
    netrows = [
        ("+ stations, all networks (OLS)", nm.loc["+ delta log(1+N_sta), all networks"]),
        ("+ stations, permanent (OLS)", nm.loc["+ delta log(1+N_sta), permanent"]),
    ]
    for j, (_lab, x) in enumerate(netrows):
        yv = n - len(rows) - j
        b.plot(
            [x.slope_per_decade - 1.96 * x.se_ols, x.slope_per_decade + 1.96 * x.se_ols],
            [yv, yv],
            color=GREY,
            lw=1.3,
        )
        b.plot(x.slope_per_decade, yv, "s", color=GREY, ms=3)
    b.set_yticks(range(n, 0, -1), [x[0] for x in rows] + [x[0] for x in netrows])
    b.axvline(0, color="k", lw=0.6)
    b.set_xlabel("SE minus Interior Alaska, $\\Delta$ log $\\mu$ per decade")
    b.set_title("(b) H2.1 and exploratory variants", loc="left")
    _save(fig, "fig04_h21_background")


def fig_tides() -> None:
    t = pd.read_csv(RES / "v02" / "m3_tides.csv").set_index("region")
    o = pd.read_csv(RES / "v02" / "m3_tides_ocean_load.csv").set_index("region")
    regs = [
        "SE_Alaska_AK",
        "NZ_Southern_Alps",
        "Alps_SED",
        "Iceland_Vatnajokull_IMO",
        "Greenland_GEUS",
        "Interior_AK_ctrl",
        "NZ_Wellington_ctrl",
        "N_Switzerland_ctrl",
    ]
    fig, ax = plt.subplots(1, 2, figsize=(W, 2.7), gridspec_kw=dict(wspace=0.12))
    y = np.arange(len(regs), 0, -1)
    a = ax[0]
    a.barh(
        y,
        t.loc[regs, "mde_amplitude"],
        color="#eeeeee",
        edgecolor="#bbbbbb",
        height=0.6,
        label="MDE (80% power)",
    )
    a.plot(
        t.loc[regs, "schuster_a_hat"],
        y + 0.12,
        "o",
        color="k",
        ms=3.5,
        label="body tide (preregistered H3.1)",
    )
    a.plot(
        o.loc[regs, "nullcorr_a_hat_total20h"],
        y - 0.12,
        "^",
        color=ACC,
        ms=3.5,
        label="body + ocean load vs random times (exploratory)",
    )
    a.set_yticks(y, [NICE[r] for r in regs])
    a.set_xlabel("modulation amplitude $a$")
    a.set_title("(a) Tidal-phase modulation", loc="left")
    b = ax[1]
    b.plot(-np.log10(t.loc[regs, "schuster_p"]), y + 0.12, "o", color="k", ms=3.5, label="_body")
    b.plot(
        -np.log10(o.loc[regs, "nullcorr_p_total20h"]),
        y - 0.12,
        "^",
        color=ACC,
        ms=3.5,
        label="_ocean",
    )
    b.axvline(-np.log10(0.05), color=GREY, lw=0.8, ls="--")
    b.text(-np.log10(0.05) + 0.03, 0.6, "p = 0.05\n(uncorrected)", fontsize=6.5, color=GREY)
    b.set_yticks(y, [""] * len(regs))
    b.set_xlabel("$-\\log_{10} p$")
    b.set_title("(b) Significance (before BH)", loc="left")
    h, lab = a.get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.16))
    _save(fig, "fig05_tides")


def fig_tipping() -> None:
    c = pd.read_csv(RES / "tipping_curves.csv")
    c = c[(c.t <= 2150)]
    regs = [
        ("Greenland_SE", "SE Greenland\n(GRACE box load)"),
        ("Amundsen_WAIS", "Amundsen Sea\n(GRACE box load)"),
        ("SE_Alaska_surface", "SE Alaska\n(glacier-surface load)"),
        ("Iceland_surface", "Iceland\n(glacier-surface load)"),
    ]
    lab = {
        "continuation": "today's rate held",
        "grace_accel": "GRACE acceleration continued",
        "edwards_ssp585_median": "Edwards 2021 SSP5-8.5 median",
        "edwards_ssp585_p95": "Edwards 2021 SSP5-8.5 95th pct.",
        "deconto_3C": "DeConto 2021 ~3 \u00b0C (from 2060)",
        "deconto_3C_early": "DeConto 2021, early (from 2040)",
        "edwards_glaciers_ssp585_median": "glaciers SSP5-8.5 median",
    }
    sty = {
        "continuation": ("k", "-"),
        "grace_accel": (GREY, "--"),
        "edwards_ssp585_median": (ICE, "-"),
        "edwards_ssp585_p95": (ACC, "-"),
        "deconto_3C": ("#2a9d8f", "-"),
        "deconto_3C_early": ("#7b2cbf", "-"),
        "edwards_glaciers_ssp585_median": ("#e76f51", "-"),
    }
    fig, ax = plt.subplots(
        2, 4, figsize=(W, 4.3), sharex=True, gridspec_kw=dict(hspace=0.18, wspace=0.42)
    )
    for j, (reg, title) in enumerate(regs):
        for sf, row in ((0.0, 0), (0.6, 1)):
            x = c[(c.region == reg) & (c.shadow_frac == sf)]
            for tr, g in x.groupby("trajectory"):
                col, ls = sty[tr]
                yv = g.promoted if sf == 0.0 else g.aggregate_rate
                ax[row, j].plot(g.t, yv, color=col, ls=ls, lw=1.1, label=lab[tr])
            ax[row, j].axhline(1, color="k", lw=0.5)
            ax[row, j].axvline(2025, color=GREY, lw=0.5, ls=":")
        ax[1, j].axhline(0.98, color=GREY, lw=0.6, ls="--")
        ax[0, j].set_title(title, fontsize=7.8)
        ax[1, j].set_xlabel("year")
    seen: dict[str, object] = {}
    for a in ax.ravel():
        for h, lb in zip(*a.get_legend_handles_labels(), strict=True):
            seen.setdefault(lb, h)
    fig.legend(
        list(seen.values()),
        list(seen),
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, -0.1),
        fontsize=6.8,
    )
    ax[0, 0].set_ylabel("rate / 2025\n(promoted faults)")
    ax[1, 0].set_ylabel("catalogue rate / 2025\n(60% shadowed faults)")
    _save(fig, "fig06_tipping_quiet")


def fig_precursors() -> None:
    a = pd.read_csv(RES / "precursors_grace_acceleration.csv")
    g = pd.read_csv(RES / "precursors_gnss_uplift.csv")
    nm = {
        "Amundsen_ASE": "Amundsen Sea",
        "Greenland_all": "Greenland (all)",
        "Greenland_SE_box": "SE Greenland",
        "Greenland_W_box": "W Greenland",
        "SE_Alaska_box": "SE Alaska",
        "Vatnajokull": "Vatnaj\u00f6kull",
        "Patagonia_box": "Patagonia",
    }
    fig, ax = plt.subplots(1, 2, figsize=(W, 2.6), gridspec_kw=dict(wspace=0.55))
    y = np.arange(len(a), 0, -1)
    b = ax[0]
    for yi, r in zip(y, a.itertuples(), strict=True):
        col = ACC if r.M1_flag else ICE
        b.plot(
            [r.xi_per_yr - 1.96 * r.xi_se, r.xi_per_yr + 1.96 * r.xi_se],
            [yi, yi],
            color=col,
            lw=1.2,
        )
        b.plot(r.xi_per_yr, yi, "o", color=col, ms=3.5)
    b.axvline(0, color="k", lw=0.6)
    b.axvline(0.02, color=ACC, lw=0.8, ls="--")
    b.text(0.0215, 0.45, "M1", color=ACC, fontsize=6.5)
    b.set_ylim(0.3, len(a) + 0.5)
    b.set_yticks(y, [nm.get(x, x) for x in a.box])
    b.set_xlabel("$\\xi$ = acceleration of loss / |rate| (1/yr)")
    b.set_title("(a) GRACE/GRACE-FO 2002-2026", loc="left")
    c = ax[1]
    g = g.sort_values("accel_z")
    yy = np.arange(len(g), 0, -1)[::-1]
    cols = [
        ACC if f else (CTL if role == "control" else ICE)
        for f, role in zip(g.M2_flag, g.role, strict=True)
    ]
    c.barh(yy, g.accel_z, color=cols, height=0.6)
    c.axvline(3, color=ACC, lw=0.8, ls="--")
    c.axvline(0, color="k", lw=0.6)
    c.set_yticks(yy, g.station)
    c.set_xlabel("uplift acceleration, z-score")
    c.set_title("(b) GNSS stations (NGL IGS20)", loc="left")
    _save(fig, "fig07_precursors")


def main() -> None:
    fig_global()
    fig_seasonal()
    fig_growth()
    fig_h21()
    fig_tides()
    fig_tipping()
    fig_precursors()


if __name__ == "__main__":
    main()
