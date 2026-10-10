"""Experiment A (tipping trajectories) and B (apparent pre-tipping quiet) - scenario model.

Nothing here is fitted to seismicity; every parameter is exposed and varied. The model joins
three published ingredients:

1. Load-rate trajectories L'(t) [kPa/yr of unloading] for an ice mass, relative to today's
   GRACE rate (2002-2026 fit), with multipliers m(t) = L'(t)/L'(2025):
   - ``continuation``: m = 1.
   - ``grace_accel``: today's normalised GRACE acceleration xi = -A/|v| continued as
     m = exp(xi (t - 2025)) until 2100 (xi < 0 = today's loss is slowing).
   - ``edwards_ssp585_median`` / ``_p95`` (Greenland): exponential growth from 2015 whose
     2015-2100 integral equals the Greenland SSP5-8.5 contribution of Edwards et al. 2021
     (Nature 593:74, doi:10.1038/s41586-021-03302-y, Table 1: 10 [5-95 %: 2, 20] cm SLE) given
     the 2002-2026 GRACE rate. *Derived by us*, not a number from the paper.
   - ``edwards_glaciers_ssp585_median`` (mountain glaciers): same construction with the global
     glacier SSP5-8.5 median (16 cm) and the 2000-2019 global glacier loss of
     Hugonnet et al. 2021 (267 Gt/yr). Mountain glaciers run out of ice; m is capped at 2100.
   - ``deconto_3C`` (Amundsen/WAIS): constant until 2060, then exponential to x10 in 2100
     ("abrupt jump in the pace of Antarctic ice loss after around 2060 ... an order of
     magnitude faster than today" for ~3 degC, DeConto et al. 2021, doi:10.1038/s41586-021-03427-0).
   - ``deconto_3C_early``: same shape with onset 2040 (sensitivity case, not from the paper).
   After 2100 m is held constant (no projection beyond 2100 is implied).
2. Response of the solid Earth: elastic share (1 - C) immediately, viscous share C relaxing with
   tau (``lagmodel``: half-space + plate, published viscosities, assumed wavelengths):
       Sdot_gia(t) = kappa [ (1 - C) L'(t) + C int L'(s) exp(-(t-s)/tau)/tau ds ]
   kappa = Coulomb stress on seismogenic faults per unit surface unloading, NOT constrained.
3. Seismicity, rate-and-state (Dieterich 1994):
   - promoted faults (kappa > 0): R/R_2025 = (Sdot0 + Sdot_gia(t)) / (Sdot0 + Sdot_gia(2025));
   - shadowed faults (same |kappa|, opposite sign - fault orientation / position relative to
     the load, Hampel et al. 2010 doi:10.1098/rsta.2010.0031; stress shadows, Harris 1998
     doi:10.1029/98JB01576): exact Dieterich ODE (rate cannot go below zero, it decays);
   - a catalogue mixes both with shadow fraction f;
   - seasonal modulation of promoted faults ~ 1/(Sdot0 + Sdot_gia) (T >> t_a), i.e. it *drops*
     when the background stressing rate rises.

Detection: log-linear trend of the aggregate rate from 2026-11 (both directions), and a
one-sided drop of the seasonal modulation versus the frozen baseline b_ref (same statistics
as the confirmatory test C1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats

from . import lagmodel
from .power import se_harmonic

GT_PER_MM_SLE = 362.0  # Gt of ice per mm global mean sea level
HUGONNET_GLACIER_GT_YR = 267.0  # Hugonnet et al. 2021, 2000-2019 global glacier mass loss
EDWARDS_2100_CM = {  # Edwards et al. 2021 Table 1, SSP5-8.5, 2015-2100, cm SLE
    "greenland_median": 10.0,
    "greenland_p95": 20.0,
    "glaciers_median": 16.0,
}
T_START = 2026 + 10 / 12  # first month of new data (Nov 2026)
YEARS = np.arange(1900.0, 2300.0 + 1e-9, 1.0 / 12.0)


def exp_multiplier_for_integral(ratio_to_constant: float) -> float:
    """m such that int_0^1 m^x dx = (m - 1)/ln m equals the requested ratio (>= 1)."""
    if ratio_to_constant <= 1.0:
        return 1.0
    return float(optimize.brentq(lambda m: (m - 1) / np.log(m) - ratio_to_constant, 1.0001, 1e4))


@dataclass(frozen=True)
class Trajectory:
    name: str
    onset: float  # year growth starts
    m2100: float  # multiplier reached in 2100 relative to the rate at onset
    accel_per_yr: float = 0.0  # for linear 'grace_accel': dm/dt
    source: str = ""

    def multiplier(self, t: np.ndarray) -> np.ndarray:
        t = np.asarray(t, float)
        if self.accel_per_yr:  # exponential with today's normalised GRACE acceleration xi
            return np.asarray(np.exp(self.accel_per_yr * (np.clip(t, 2025.0, 2100.0) - 2025.0)))
        x = np.clip((np.minimum(t, 2100.0) - self.onset) / (2100.0 - self.onset), 0.0, None)
        return np.asarray(self.m2100**x)


@dataclass(frozen=True)
class TipRegion:
    key: str
    rheology: str
    lambda_km: float
    ldot_now_kpa_yr: float  # unloading rate today (positive = unloading)
    load_label: str
    n_per_yr: float  # declustered events/yr >= Mc (catalogue power); NaN -> hypothetical
    b_ref: float  # current seasonal modulation (NaN if none)
    b_ref_se: float
    phi: float = 1.3
    trajectories: list[Trajectory] = field(default_factory=list)
    note: str = ""


def gia_stressing(
    t: np.ndarray, ldot: np.ndarray, tau: float, comp: float, kappa: float
) -> np.ndarray:
    """kappa [(1-C) L' + C (L' * exp(-t/tau)/tau)] on a regular grid (kPa/yr)."""
    dt = float(t[1] - t[0])
    a = np.exp(-dt / tau)
    v = np.zeros_like(ldot)
    for i in range(1, len(t)):  # exact for piecewise-constant L'
        v[i] = v[i - 1] * a + ldot[i - 1] * (1 - a)
    return kappa * ((1 - comp) * ldot + comp * v)


def response(
    t: np.ndarray,
    ldot: np.ndarray,
    tau: float,
    comp: float,
    kappa: float,
    sdot0: float,
    shadow_frac: float,
    a_sigma: float = 1.5,
) -> pd.DataFrame:
    sg = gia_stressing(t, ldot, tau, comp, kappa)
    i25 = int(np.searchsorted(t, 2025.0))
    promoted = (sdot0 + sg) / (sdot0 + sg[i25])
    dt = float(t[1] - t[0])
    s_shadow = np.concatenate([[0.0], np.cumsum((sdot0 - sg)[:-1] * dt)])
    with np.errstate(over="ignore"):
        r_sh = np.nan_to_num(lagmodel.rsm_rate(t, s_shadow, a_sigma, sdot0), nan=0.0)
    shadow = r_sh / r_sh[i25]
    agg_raw = (1 - shadow_frac) * (sdot0 + sg) / sdot0 + shadow_frac * r_sh
    agg = agg_raw / agg_raw[i25]
    modulation = (sdot0 + sg[i25]) / (sdot0 + sg)
    return pd.DataFrame(
        dict(
            t=t,
            sdot_gia=sg,
            promoted=promoted,
            shadow=shadow,
            aggregate_rate=agg,
            modulation_ratio=modulation,
        )
    )


def _trend_detect(
    t: np.ndarray, ratio: np.ndarray, n_per_yr: float, phi: float, sign: int
) -> float:
    """First year Y (>= T_START+2) with log-trend over [T_START, Y] beyond the MDE in `sign`."""
    if not np.isfinite(n_per_yr) or n_per_yr <= 0:
        return float("nan")
    m0 = t >= T_START
    tt, rr = t[m0], np.log(np.clip(ratio[m0], 1e-6, None))
    for k in range(24, len(tt), 6):
        slope = np.polyfit(tt[:k], rr[:k], 1)[0]
        mde = lagmodel.mde_slope(n_per_yr, T_START, float(tt[k - 1]), phi)
        if sign * slope >= mde:
            return float(tt[k - 1])
    return float("nan")


def _modulation_drop_z(
    t: np.ndarray, mod_ratio: np.ndarray, rate_ratio: np.ndarray, reg: TipRegion, year: float
) -> float:
    """z of the drop b_ref - b_new(T_START..year) (one-sided; NaN without catalogue)."""
    if not (np.isfinite(reg.b_ref) and np.isfinite(reg.n_per_yr)):
        return float("nan")
    m0 = (t >= T_START) & (t <= year)
    n_new = reg.n_per_yr * float(np.mean(rate_ratio[m0])) * float(m0.sum() / 12)
    b_new = reg.b_ref * float(np.mean(mod_ratio[m0]))
    return float((reg.b_ref - b_new) / np.hypot(se_harmonic(n_new, reg.phi), reg.b_ref_se))


def _modulation_drop_detect(
    t: np.ndarray, mod_ratio: np.ndarray, rate_ratio: np.ndarray, reg: TipRegion
) -> float:
    """First year Y at which b_ref - b_new(T_START..Y) exceeds the one-sided 5 %/80 % MDE."""
    if not (np.isfinite(reg.b_ref) and reg.b_ref > 0 and np.isfinite(reg.n_per_yr)):
        return float("nan")
    z = stats.norm.isf(0.05) + stats.norm.isf(0.2)
    m0 = t >= T_START
    tt, mr, rr = t[m0], mod_ratio[m0], rate_ratio[m0]
    for k in range(24, len(tt), 6):
        n_new = reg.n_per_yr * float(np.mean(rr[:k])) * (k / 12)
        b_new = reg.b_ref * float(np.mean(mr[:k]))
        if reg.b_ref - b_new >= z * np.hypot(se_harmonic(n_new, reg.phi), reg.b_ref_se):
            return float(tt[k - 1])
    return float("nan")


def run_scenarios(
    regions: list[TipRegion],
    kappas: tuple[float, ...] = (0.3, 1.0),
    sdot0s: tuple[float, ...] = (10.0, 30.0),
    shadow_fracs: tuple[float, ...] = (0.0, 0.6),
    a_sigma: float = 1.5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summary table (one row per scenario) and yearly curves (for charts)."""
    rows, curves = [], []
    t = YEARS
    for reg in regions:
        rh = lagmodel.RHEOLOGIES[reg.rheology]
        tau = lagmodel.relaxation_time_yr(rh.eta, reg.lambda_km, rh.te_km)
        comp = lagmodel.compensation(reg.lambda_km, rh.te_km)
        for tr in reg.trajectories:
            ldot = np.where(t >= 1995.0, reg.ldot_now_kpa_yr * tr.multiplier(t), 0.0)
            ldot = ldot / max(tr.multiplier(np.array([2025.0]))[0], 1e-9)  # = L'_now in 2025
            for kappa in kappas:
                for sdot0 in sdot0s:
                    for f in shadow_fracs:
                        r = response(t, ldot, tau, comp, kappa, sdot0, f, a_sigma)
                        at = {y: int(np.searchsorted(t, y)) for y in (2050.0, 2075.0, 2100.0)}
                        after = t >= 2025.0
                        agg = r["aggregate_rate"].to_numpy()
                        i_min = int(np.argmin(np.where(after, agg, np.inf)))
                        q_year = _trend_detect(t, agg, reg.n_per_yr, reg.phi, -1)
                        up_year = _trend_detect(t, agg, reg.n_per_yr, reg.phi, +1)
                        mod_year = _modulation_drop_detect(
                            t, r.modulation_ratio.to_numpy(), r.promoted.to_numpy(), reg
                        )
                        below = after & (agg < 0.98)
                        quiet_onset = float(t[np.argmax(below)]) if below.any() else np.nan
                        rec = (t > t[i_min]) & (agg >= 1.0)
                        turnaround = (
                            float(t[np.argmax(rec)])
                            if np.isfinite(quiet_onset) and rec.any()
                            else np.nan
                        )
                        rows.append(
                            dict(
                                region=reg.key,
                                trajectory=tr.name,
                                onset=tr.onset,
                                load_m_2100_vs_2025=float(tr.multiplier(np.array([2100.0]))[0])
                                / float(tr.multiplier(np.array([2025.0]))[0]),
                                ldot_now_kpa_yr=reg.ldot_now_kpa_yr,
                                load=reg.load_label,
                                tau_yr=tau,
                                compensation=comp,
                                kappa=kappa,
                                sdot0_kpa_yr=sdot0,
                                shadow_frac=f,
                                n_per_yr=reg.n_per_yr,
                                promoted_2050=r.promoted.iloc[at[2050.0]],
                                promoted_2100=r.promoted.iloc[at[2100.0]],
                                aggregate_2050=agg[at[2050.0]],
                                aggregate_2075=agg[at[2075.0]],
                                aggregate_2100=agg[at[2100.0]],
                                aggregate_min=float(agg[i_min]),
                                aggregate_min_year=float(t[i_min]),
                                modulation_2050=r.modulation_ratio.iloc[at[2050.0]],
                                modulation_2100=r.modulation_ratio.iloc[at[2100.0]],
                                detect_quiet_year=q_year,
                                detect_increase_year=up_year,
                                detect_modulation_drop_year=mod_year,
                                modulation_drop_z_2100=_modulation_drop_z(
                                    t,
                                    r.modulation_ratio.to_numpy(),
                                    r.promoted.to_numpy(),
                                    reg,
                                    2100.0,
                                ),
                                quiet_2pct_year=quiet_onset,
                                quiet_end_year=turnaround,
                                quiet_2pct_minus_onset=quiet_onset - max(tr.onset, 2025.0),
                                detect_quiet_minus_onset=q_year - max(tr.onset, 2025.0),
                                quiet_before_increase=bool(
                                    np.isfinite(q_year)
                                    and (not np.isfinite(up_year) or q_year < up_year)
                                ),
                            )
                        )
                        if kappa == 1.0 and sdot0 == 10.0:
                            idx = np.arange(0, len(t), 12)  # whole years
                            sub = r.iloc[idx[t[idx] >= 1999.5]].copy()
                            sub["t"] = np.round(sub.t)
                            curves.append(
                                sub.assign(
                                    region=reg.key,
                                    trajectory=tr.name,
                                    shadow_frac=f,
                                    ldot=np.interp(sub.t, t, ldot),
                                )
                            )
    return pd.DataFrame(rows), pd.concat(curves, ignore_index=True)


def default_regions(
    grace_acc: pd.DataFrame,
    ldot_kpa: dict[str, float],
    frozen: dict[str, Any],
    hypothetical_n_per_yr: float = 100.0,
) -> list[TipRegion]:
    """TipRegions from today's GRACE fits and the frozen C1 catalogue values.

    ldot_kpa[box] = today's regional-mean unloading rate (kPa/yr, positive = unloading).
    """
    gl = grace_acc.set_index("box")

    def acc_rel(box: str) -> float:
        r = gl.loc[box]
        return float(-r.mass_accel / abs(r.mass_rate)) if r.mass_rate < 0 else 0.0

    regs = frozen.get("regions", {})

    def cat(name: str) -> tuple[float, float, float]:
        x = regs.get(name, {})
        return (
            float(x.get("rate_decl_per_yr_2016_2025", np.nan)),
            float(x.get("b_ref", np.nan)),
            float(x.get("b_ref_se", np.nan)),
        )

    def edwards(cm: float, gt_per_yr_now: float) -> float:
        const_mm = gt_per_yr_now / GT_PER_MM_SLE * 85.0
        return exp_multiplier_for_integral(cm * 10.0 / const_mm)

    gr_now = -float(gl.loc["Greenland_all"].mass_rate)
    m_gr_med = edwards(EDWARDS_2100_CM["greenland_median"], gr_now)
    m_gr_p95 = edwards(EDWARDS_2100_CM["greenland_p95"], gr_now)
    m_gla = edwards(EDWARDS_2100_CM["glaciers_median"], HUGONNET_GLACIER_GT_YR)

    def base(box: str) -> list[Trajectory]:
        a = acc_rel(box)
        return [
            Trajectory("continuation", 2025.0, 1.0, source="today's GRACE rate held constant"),
            Trajectory(
                "grace_accel",
                2025.0,
                1.0,
                accel_per_yr=a if a != 0 else 1e-12,
                source=f"today's GRACE acceleration continued (xi = {a:+.4f}/yr)",
            ),
        ]

    gla = Trajectory(
        "edwards_glaciers_ssp585_median", 2015.0, m_gla, source="Edwards et al. 2021 (derived)"
    )
    gr_tr = base("Greenland_SE_box") + [
        Trajectory("edwards_ssp585_median", 2015.0, m_gr_med, source="Edwards 2021 (derived)"),
        Trajectory("edwards_ssp585_p95", 2015.0, m_gr_p95, source="Edwards 2021 (derived)"),
    ]
    wa_tr = base("Amundsen_ASE") + [
        Trajectory("deconto_3C", 2060.0, 10.0, source="DeConto et al. 2021 (~3 degC)"),
        Trajectory("deconto_3C_early", 2040.0, 10.0, source="sensitivity case: onset 2040"),
    ]
    n_g, b_g, se_g = cat("Greenland_GEUS")
    n_a, b_a, se_a = cat("SE_Alaska_AK")
    n_i, b_i, se_i = cat("Iceland_Vatnajokull_IMO")
    surf = lagmodel.SPECIFIC_MASS_CHANGE_MWE
    out = [
        TipRegion(
            "Greenland_SE",
            "Greenland_SE",
            1000.0,
            ldot_kpa["Greenland_SE_box"],
            "GRACE box mean",
            n_g,
            b_g,
            se_g,
            trajectories=gr_tr,
        ),
        TipRegion(
            "Amundsen_WAIS",
            "West_Antarctica",
            500.0,
            ldot_kpa["Amundsen_ASE"],
            "GRACE box mean",
            hypothetical_n_per_yr,
            np.nan,
            np.nan,
            trajectories=wa_tr,
            note="no usable catalogue (3 ComCat events): n/yr is hypothetical",
        ),
    ]
    for key, box, rh, lam, (n, b, se) in (
        ("SE_Alaska", "SE_Alaska_box", "SE_Alaska", 300.0, (n_a, b_a, se_a)),
        ("Iceland", "Vatnajokull", "Iceland", 200.0, (n_i, b_i, se_i)),
    ):
        tr = base(box) + [gla]
        out.append(
            TipRegion(
                f"{key}_grace", rh, lam, ldot_kpa[box], "GRACE box mean", n, b, se, trajectories=tr
            )
        )
        out.append(
            TipRegion(
                f"{key}_surface",
                rh,
                lam,
                -surf[rh][0] * 9.81,
                "glacier surface (Hugonnet 2021)",
                n,
                b,
                se,
                trajectories=tr,
            )
        )
    return out
