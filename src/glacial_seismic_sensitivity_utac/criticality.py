"""Phase-2 criticality battery (ported from the exploratory ``glacial_crit`` code).

Per region: 2-year-bin indicators (rate, b-value, clustering, inter-event statistics, seasonal
amplitude, near-city fraction, ...) with block-permutation Kendall trend tests, and
critical-slowing-down (CSD) indicators on monthly counts tested against IAAFT surrogates.
Afterwards Benjamini-Hochberg over all tests and an ice-vs-control group permutation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as C
from .indicators import b_event_windows, bin_indicators, monthly_counts
from .regionrun import Prepared
from .stats_tests import bh, block_perm_test, csd_surrogate_test, group_perm

BIN_INDICATORS = [
    "rate_raw",
    "rate_decl",
    "triggered_frac",
    "cv_raw",
    "burst_raw",
    "cv_decl",
    "burst_decl",
    "dispersion_monthly_decl",
    "b_raw",
    "b_decl",
    "n_clusters_ge5",
    "mean_cluster_size",
    "swarm_frac",
    "productivity_resid",
    "seasonal_amp_decl",
    "frac_near_city_raw",
    "frac_near_city_decl",
    "mag_q95_raw",
    "mc_bin",
    "frac_mb",
]
CSD_INDICATORS = ["variance", "ar1", "skewness", "kurtosis", "recovery_rate"]


def tier_of(name: str) -> str:
    """'comcat': global ComCat M>=3 boxes; 'national': national / regional network catalogues.
    Regions of different tiers overlap and are never pooled in one group test."""
    return "comcat" if C.REGIONS[name].source == "comcat" else "national"


def run_region(
    p: Prepared, cities: pd.DataFrame, rng: np.random.Generator
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    group = C.REGIONS[p.name].group
    bins = bin_indicators(p.raw, p.dc, p.clusters, p.mc_ref, cities)
    bins.insert(0, "region", p.name)
    trend_rows = []
    bt = bins[bins.bin_end <= C.TEST_END_YEAR]
    for k in BIN_INDICATORS:
        tau, pv = block_perm_test(bt[k].to_numpy(float), rng)
        trend_rows.append(
            dict(
                region=p.name,
                group=group,
                indicator=k,
                tau=tau,
                p=pv,
                n_bins=int(bt[k].notna().sum()),
            )
        )
    for variant, d in (("raw", p.dc), ("decl", p.decl)):
        bw = b_event_windows(d, p.mc_ref)
        bw = bw[bw.year_mid <= C.TEST_END_YEAR]
        tau, pv = block_perm_test(bw.b.to_numpy(float), rng) if len(bw) >= 6 else (np.nan, np.nan)
        trend_rows.append(
            dict(
                region=p.name,
                group=group,
                indicator=f"b_eventwin100_{variant}",
                tau=tau,
                p=pv,
                n_bins=len(bw),
            )
        )
    csd_rows, series = [], {}
    for variant, d in (("decl", p.decl), ("raw", p.dc)):
        x = monthly_counts(d, "1990-01", f"{C.TEST_END_YEAR}-12")
        if x.sum() < 60:
            continue
        res, ser = csd_surrogate_test(x.to_numpy(), rng)
        ser.index = x.index.to_timestamp()
        series[variant] = ser.assign(count=x.to_numpy())
        for k, (tau, pv) in res.items():
            csd_rows.append(
                dict(region=p.name, group=group, variant=variant, indicator=k, tau=tau, p=pv)
            )
    return bins, pd.DataFrame(trend_rows), pd.DataFrame(csd_rows), series


def combine(
    trends: pd.DataFrame, csds: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """BH over all trend and CSD tests jointly + group permutations (ice groups vs control)."""
    allp = np.concatenate([trends.p.to_numpy(float), csds.p.to_numpy(float)])
    q, sig = bh(allp)
    trends = trends.assign(q_BH=q[: len(trends)], sig_BH=sig[: len(trends)])
    csds = csds.assign(q_BH=q[len(trends) :], sig_BH=sig[len(trends) :])
    rows = []
    for tier, target in [
        (t, g) for t in ("comcat", "national") for g in ("mountain", "icesheet", "ice_any")
    ]:
        in_tier = {r for r in C.REGIONS if tier_of(r) == tier}
        is_t = {
            r: (C.REGIONS[r].group != "control")
            if target == "ice_any"
            else (C.REGIONS[r].group == target)
            for r in in_tier
        }
        keep = {r for r in in_tier if C.REGIONS[r].group == "control" or is_t[r]}
        for k in BIN_INDICATORS:
            v = trends[(trends.indicator == k) & trends.region.isin(keep)].set_index("region").tau
            d, pv, n = group_perm(v.to_dict(), is_t)
            rows.append(
                dict(
                    tier=tier,
                    target=target,
                    family="bin",
                    indicator=k,
                    variant="",
                    diff_mean_tau=d,
                    p_perm=pv,
                    n_regions=n,
                )
            )
        for var in ("decl", "raw"):
            for k in CSD_INDICATORS:
                v = (
                    csds[(csds.indicator == k) & (csds.variant == var) & csds.region.isin(keep)]
                    .set_index("region")
                    .tau
                )
                d, pv, n = group_perm(v.to_dict(), is_t)
                rows.append(
                    dict(
                        tier=tier,
                        target=target,
                        family="csd",
                        indicator=k,
                        variant=var,
                        diff_mean_tau=d,
                        p_perm=pv,
                        n_regions=n,
                    )
                )
    gv = pd.DataFrame(rows)
    gq, gs = bh(gv.p_perm.to_numpy(float))
    return trends, csds, gv.assign(q_BH=gq, sig_BH=gs)
