"""v0.2 charts (18-23) from results/v02/. Each chart is skipped if its input is missing."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import config as C  # noqa: E402
from .plots import _save  # noqa: E402

V = "v02"


def _r(name: str) -> pd.DataFrame | None:
    f = C.OUT / V / name
    return pd.read_csv(f) if f.exists() else None


def chart_mu_series() -> None:
    pairs = (
        ("SE_Alaska_AK", "Interior_AK_ctrl"),
        ("NZ_Southern_Alps", "NZ_Wellington_ctrl"),
        ("Alps_SED", "N_Switzerland_ctrl"),
        ("Iceland_Vatnajokull_IMO", "Greenland_GEUS"),
    )
    fig, axs = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    any_ = False
    for ax, (g, c) in zip(axs.ravel(), pairs, strict=True):
        for name, col in ((g, "C0"), (c, "C3")):
            t = _r(f"m2_mu_{name}.csv")
            if t is None:
                continue
            any_ = True
            x = 0.5 * (t.t_start + t.t_end)
            k = np.exp(1.96 * t.log_mu_se * 1.25)
            ax.plot(x, t.mu_per_yr, "o-", color=col, ms=3, label=name)
            ax.fill_between(x, t.mu_per_yr / k, t.mu_per_yr * k, color=col, alpha=0.15)
        ax.set_yscale("log")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
        ax.set_ylabel("background mu [events/yr >= Mc]")
    if not any_:
        plt.close(fig)
        return
    fig.suptitle(
        "18  ETAS background rate per year (two-stage, tmax 1 yr), 95 % band incl. SE factor 1.25",
        fontsize=10,
    )
    _save(fig, "18_v02_etas_background_mu.png")


def chart_h22() -> None:
    d = _r("m2_etas_background.csv")
    if d is None:
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    for _, r in d.iterrows():
        col = "C3" if "ctrl" in r.region else "C0"
        ax.errorbar(
            r.total_ratio,
            r.mu_ratio,
            yerr=[[r.mu_ratio - r.mu_ratio_lo95], [r.mu_ratio_hi95 - r.mu_ratio]],
            fmt="o",
            color=col,
        )
        ax.annotate(
            r.region,
            (r.total_ratio, r.mu_ratio),
            fontsize=7,
            xytext=(4, 4),
            textcoords="offset points",
        )
    ax.axhline(1, color="k", lw=0.8)
    ax.axvline(1, color="k", lw=0.8)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.text(
        0.02,
        0.97,
        "masked rise\n(deceptive-quiet pattern)",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
        color="C1",
    )
    ax.set_xlabel("total-rate ratio 2020-25 / 2008-19 (all events >= Mc)")
    ax.set_ylabel("background mu ratio (95 % CI)")
    ax.set_title("19  H2.2: background vs total rate (blue glacier, red control)", fontsize=10)
    ax.grid(alpha=0.3, which="both")
    _save(fig, "19_v02_H22_masked_rise.png")


def chart_tides() -> None:
    d = _r("m3_tides.csv")
    if d is None:
        return
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    y = np.arange(len(d))
    axs[0].barh(y, d.schuster_a_hat, color="C0", alpha=0.7, label="observed a = 2R/N")
    axs[0].plot(d.mde_amplitude, y, "k|", ms=14, label="MDE (alpha 0.05, power 0.8)")
    axs[0].set_yticks(y)
    axs[0].set_yticklabels(
        [f"{r} (p={p:.2g})" for r, p in zip(d.region, d.schuster_p, strict=True)], fontsize=7
    )
    axs[0].set_xlabel("body-tide modulation amplitude")
    axs[0].legend(fontsize=7)
    axs[1].errorbar(
        d.bsplit_d_b, y, xerr=1.96 * np.hypot(d.bsplit_se_tens, d.bsplit_se_comp), fmt="o"
    )
    axs[1].plot(-d.mde_delta_b, y, "k|", ms=14, label="-MDE")
    axs[1].axvline(0, color="k", lw=0.8)
    axs[1].set_yticks(y)
    axs[1].set_yticklabels(d.region, fontsize=7)
    axs[1].set_xlabel("b(tensile) - b(compressive)")
    axs[1].legend(fontsize=7)
    fig.suptitle("20  H3: body tide (no ocean loading), declustered events 1995-2025", fontsize=10)
    _save(fig, "20_v02_tides.png")


def chart_lag() -> None:
    d = _r("m4_eta_scan_earliest.csv")
    if d is None:
        return
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for (te, reg), g in d.groupby(["te_km", "region"]):
        ax.plot(g.eta_Pa_s, g.earliest_any, "o-", ms=3, label=f"{reg}, Te {te:.0f} km")
    for x, lab in ((1.4e19, "v0.1.0 (Larsen et al.)"), (3e18, "Sasgen et al. 2026")):
        ax.axvline(x, color="k", ls=":", lw=1)
        ax.text(x, ax.get_ylim()[1], lab, rotation=90, va="top", ha="right", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlabel("mantle viscosity eta [Pa s]")
    ax.set_ylabel("earliest detection year (any scenario)")
    ax.set_title("21  M4: SE Alaska earliest detection year vs. viscosity", fontsize=10)
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    _save(fig, "21_v02_lag_viscosity.png")


def chart_m1() -> None:
    d = _r("m1_catalogue_robustness.csv")
    if d is None:
        return
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    y = np.arange(len(d))
    for k, (pre, col) in enumerate((("v01", "k"), ("gk", "C1"), ("emr", "C2"))):
        if f"{pre}_b1_per_decade" in d:
            axs[0].errorbar(
                d[f"{pre}_b1_per_decade"],
                y + 0.2 * (k - 1),
                xerr=1.96 * d[f"{pre}_b1_se"],
                fmt="o",
                color=col,
                label=pre,
            )
        if f"{pre}_habermann_z" in d:
            axs[1].plot(d[f"{pre}_habermann_z"], y + 0.2 * (k - 1), "o", color=col, label=pre)
    for ax in axs:
        ax.axvline(0, color="k", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(d.region, fontsize=7)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    axs[0].set_xlabel("F1 b1 per decade (95 % CI)")
    axs[1].axvline(-2, color="r", ls=":", lw=1)
    axs[1].set_xlabel("Habermann z (2020-25 vs 2008-19)")
    fig.suptitle("22  M1: v0.1 (MAXC+0.2, NN) vs Gardner-Knopoff vs EMR-Mc", fontsize=10)
    _save(fig, "22_v02_catalogue_robustness.png")


def chart_recovery() -> None:
    d = _r("recovery_study.csv")
    if d is None:
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    meths = ["joint_rw1", "joint_rw0.2", "two_stage"]
    for i, (_sc, g) in enumerate(d.groupby("scenario")):
        for j, m in enumerate(meths):
            h = g[g.method == m]
            x = i + 0.25 * (j - 1) + np.linspace(-0.05, 0.05, len(h))
            ax.errorbar(
                x,
                h.slope,
                yerr=1.96 * h.slope_se,
                fmt="o",
                ms=3,
                color=f"C{j}",
                label=m if i == 0 else None,
            )
        ax.hlines(g.slope_true.iloc[0], i - 0.4, i + 0.4, color="k")
    ax.set_xticks(range(d.scenario.nunique()))
    ax.set_xticklabels(sorted(d.scenario.unique()))
    ax.set_ylabel("log-mu slope per decade")
    ax.set_title("23  M2 synthetic recovery (black = truth)", fontsize=10)
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    _save(fig, "23_v02_recovery_study.png")


def all_charts() -> None:
    for fn in (chart_mu_series, chart_h22, chart_tides, chart_lag, chart_m1, chart_recovery):
        fn()
