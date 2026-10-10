"""Lag / response model: when could a seismic response to *today's* melt become detectable?

Three deliberately simple, separable pieces (every parameter is exposed; nothing is fitted):

1. Mantle relaxation (GIA). Viscous half-space under an elastic plate, single load wavelength
   lambda (Turcotte & Schubert 2002, Geodynamics, sec. 6-10; derivation e.g.
   http://topex.ucsd.edu/geodynamics/glacial_rebound.pdf):
       tau = 4 pi eta / (rho_m g lambda) * 1 / (1 + D k^4 / (rho_m g)),   k = 2 pi / lambda
   with the relaxed (equilibrium) deflection reduced by C = 1 / (1 + D k^4/(rho_m g)).
   Check: Fennoscandia, lambda = 3000 km, eta = 1.1e21 Pa s -> tau ~ 4400 yr (Sandwell lecture).
2. Stress. The viscous part of the Coulomb stressing rate on faults is modelled as
       Sdot_gia(t) = kappa * C * Ldot * (1 - exp(-(t - t0)/tau))
   for unloading at a constant rate Ldot [kPa/yr] since t0. kappa (surface load -> Coulomb
   stress on seismogenic faults) is NOT constrained by data here and is varied as a scenario.
3. Seismicity. Rate-and-state (Dieterich 1994, doi:10.1029/93JB02581). For slow changes the rate
   follows R/r = (Sdot0 + Sdot_gia)/Sdot0; the nucleation time t_a = a sigma / Sdot0 is < ~1 yr
   (Sirorattanakul & Avouac 2026, doi:10.1126/sciadv.adz5711), so the mantle sets the lag.
   ``rsm_rate`` integrates the full Dieterich ODE for arbitrary stress histories (seasonal tests).

Detectability: a log-linear Poisson trend fitted to N events/yr over T years has
SE(slope) ~ sqrt(phi / sum_i n_i (t_i - tbar)^2) ~ sqrt(12 phi / (N T^3)); one-sided alpha = 0.05
with 80 % power needs slope >= 2.487 SE.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import config as C

SEC_PER_YR = 365.25 * 86400.0
RHO_MANTLE = 3300.0
YOUNG = 70e9  # Pa, Turcotte & Schubert typical lithosphere value
POISSON = 0.25
Z_ALPHA_BETA = 1.6449 + 0.8416  # one-sided 5 %, power 80 %


@dataclass(frozen=True)
class Rheology:
    region: str
    eta: float  # Pa s
    eta_range: tuple[float, float]
    te_km: float  # elastic thickness
    source: str
    lambda_km: tuple[float, float, float]  # assumed load wavelength (low, central, high)
    note: str = ""


# Viscosities are published values; the load wavelengths are OUR rough assumptions (~2x the
# width of the shrinking ice mass) and are varied over the given range.
RHEOLOGIES: dict[str, Rheology] = {
    "Patagonia": Rheology(
        "Patagonia",
        1.6e18,
        (1.6e18, 8.0e18),
        36.5,
        "Lange et al. 2014 doi:10.1002/2013GL058419; Richter et al. 2016",
        (150, 300, 600),
    ),
    "West_Antarctica": Rheology(
        "West_Antarctica",
        4e18,
        (4e18, 4e18),
        55.0,
        "Barletta et al. 2018 doi:10.1126/science.aao1447",
        (300, 500, 1000),
    ),
    "Iceland": Rheology(
        "Iceland",
        8e18,
        (4e18, 1e19),
        15.0,
        "Pagli et al. 2007 doi:10.1029/2006JB004421 (preferred 8-10e18)",
        (100, 200, 400),
    ),
    "Greenland_SE": Rheology(
        "Greenland_SE",
        1e19,
        (1e19, 1e19),
        60.0,
        "Khan et al. 2016 doi:10.1126/sciadv.1600931 (SE Greenland, ~1e19)",
        (300, 1000, 2000),
        "Te assumed (not from Khan et al.)",
    ),
    "SE_Alaska": Rheology(
        "SE_Alaska",
        1.4e19,
        (1.4e19, 3.7e19),
        60.0,
        "Larsen et al. 2004 doi:10.1111/j.1365-246X.2004.02356.x; "
        "Larsen et al. 2005 doi:10.1016/j.epsl.2005.06.032",
        (150, 300, 600),
    ),
    "Alps": Rheology(
        "Alps",
        2.2e20,
        (1.4e20, 2.8e20),
        50.0,
        "Mey et al. 2016 doi:10.1038/ncomms13382",
        (150, 300, 600),
    ),
    "Fennoscandia_ref": Rheology(
        "Fennoscandia_ref",
        1.1e21,
        (1.1e21, 1.1e21),
        0.0,
        "Turcotte & Schubert 2002 sec. 6-10 / Sandwell lecture",
        (3000, 3000, 3000),
        "reference value, no plate",
    ),
}


def maxwell_time_yr(eta: float, mu: float = 6.5e10) -> float:
    """Maxwell relaxation time eta/mu in years (mu: shear modulus)."""
    return eta / mu / SEC_PER_YR


def flexural_rigidity(te_km: float) -> float:
    h = te_km * 1e3
    return YOUNG * h**3 / (12 * (1 - POISSON**2))


def compensation(lambda_km: float, te_km: float) -> float:
    """Fraction of the full isostatic response reached in equilibrium (elastic-plate filter)."""
    k = 2 * np.pi / (lambda_km * 1e3)
    return float(1.0 / (1.0 + flexural_rigidity(te_km) * k**4 / (RHO_MANTLE * C.G_ACC)))


def relaxation_time_yr(eta: float, lambda_km: float, te_km: float = 0.0) -> float:
    """Relaxation time of a load of wavelength lambda on a viscous half-space (+ elastic plate)."""
    tau = 4 * np.pi * eta / (RHO_MANTLE * C.G_ACC * lambda_km * 1e3) / SEC_PER_YR
    return float(tau * compensation(lambda_km, te_km))


def relaxation_table() -> pd.DataFrame:
    rows = []
    for r in RHEOLOGIES.values():
        for eta in sorted(set(r.eta_range) | {r.eta}):
            for lam in r.lambda_km:
                rows.append(
                    dict(
                        region=r.region,
                        eta_Pa_s=eta,
                        lambda_km=lam,
                        te_km=r.te_km,
                        tau_yr=relaxation_time_yr(eta, lam, r.te_km),
                        tau_halfspace_yr=relaxation_time_yr(eta, lam, 0.0),
                        compensation=compensation(lam, r.te_km),
                        maxwell_yr=maxwell_time_yr(eta),
                        source=r.source,
                    )
                )
    return pd.DataFrame(rows)


def viscous_fraction(t: np.ndarray, t0: float, tau: float) -> np.ndarray:
    """Fraction of the equilibrium viscous stressing rate reached (constant unloading since t0)."""
    dt = np.clip(np.asarray(t, float) - t0, 0, None)
    return np.asarray(1 - np.exp(-dt / tau))


def rate_ratio(
    t: np.ndarray,
    t0: float,
    tau: float,
    ldot_kpa_yr: float,
    kappa: float,
    comp: float,
    sdot0_kpa_yr: float,
) -> np.ndarray:
    """Steady-state RSM rate ratio R/r = 1 + Sdot_gia / Sdot0."""
    sg = kappa * comp * ldot_kpa_yr * viscous_fraction(t, t0, tau)
    return np.asarray(1 + sg / sdot0_kpa_yr)


def mde_slope(n_per_yr: float, t_start: float, t_end: float, phi: float = 1.0) -> float:
    """Minimal detectable log-rate slope (per yr), monthly bins, alpha 5 % one-sided, power 80 %."""
    t = np.arange(t_start, t_end, 1 / 12) + 1 / 24
    if len(t) < 3:
        return float("inf")
    w = np.full(len(t), n_per_yr / 12)
    tb = float(np.sum(w * t) / np.sum(w))
    return float(Z_ALPHA_BETA * np.sqrt(phi / np.sum(w * (t - tb) ** 2)))


def detection_year(
    n_per_yr: float,
    phi: float,
    t0: float,
    tau: float,
    ldot: float,
    kappa: float,
    comp: float,
    sdot0: float,
    t_start: float = 2026 + 10 / 12,
    horizon: float = 2526.0,
) -> float:
    """First year Y at which the log-linear trend of R/r over [t_start, Y] exceeds the MDE slope."""
    for y in np.arange(t_start + 2, horizon, 0.5):
        tt = np.arange(t_start, y, 1 / 12) + 1 / 24
        lr = np.log(rate_ratio(tt, t0, tau, ldot, kappa, comp, sdot0))
        slope = np.polyfit(tt, lr, 1)[0]
        if slope >= mde_slope(n_per_yr, t_start, y, phi):
            return float(y)
    return float("nan")


def rsm_rate(
    t_yr: np.ndarray, stress_kpa: np.ndarray, a_sigma_kpa: float, sdot0_kpa_yr: float
) -> np.ndarray:
    """Dieterich (1994) seismicity rate R/r for a stress history S(t) (exact step integration).

    gamma' = (1 - gamma dS/dt) / a sigma,  R/r = 1 / (gamma Sdot0); starts at steady state.
    Within each step the stressing rate is constant, for which the ODE has a closed form.
    """
    t = np.asarray(t_yr, float)
    s = np.asarray(stress_kpa, float)
    g = 1.0 / sdot0_kpa_yr
    out = np.empty(len(t))
    out[0] = 1.0
    for i in range(1, len(t)):
        dt = t[i] - t[i - 1]
        sd = (s[i] - s[i - 1]) / dt
        if abs(sd) < 1e-12:
            g = g + dt / a_sigma_kpa
        else:
            e = np.exp(-sd * dt / a_sigma_kpa)
            g = g * e + (1 - e) / sd
        out[i] = 1.0 / (g * sdot0_kpa_yr)
    return out


def seasonal_modulation(
    ds_kpa: float,
    a_sigma_kpa: float,
    sdot0_kpa_yr: float,
    sdot_extra_kpa_yr: float = 0.0,
    period_yr: float = 1.0,
    n_cycles: int = 30,
) -> float:
    """Relative amplitude (max-min)/(max+min) of the RSM rate for S = (Sdot0+extra) t + dS sin.

    For period >> t_a the answer approaches 2 pi dS / (period * Sdot_total) -- independent of
    a sigma and *smaller* when a background (e.g. GIA) stressing rate is added.
    """
    sdot = sdot0_kpa_yr + sdot_extra_kpa_yr
    t = np.linspace(0, n_cycles * period_yr, n_cycles * 2000 + 1)
    s = sdot * t + ds_kpa * np.sin(2 * np.pi * t / period_yr)
    r = rsm_rate(t, s, a_sigma_kpa, sdot)
    last = r[t >= (n_cycles - 2) * period_yr]
    return float((last.max() - last.min()) / (last.max() + last.min()))


# Glacier-surface unloading rates (specific mass change, 2000-2019, Hugonnet et al. 2021,
# Nature 592:726, doi:10.1038/s41586-021-03436-z; values quoted in the main text):
# 1 m w.e./yr = 9.81 kPa/yr. Alaska is only given as part of the southern Arctic belt.
SPECIFIC_MASS_CHANGE_MWE = {
    "Iceland": (-0.88, "Iceland, Hugonnet et al. 2021"),
    "Patagonia": (-0.67, "Southern Andes, Hugonnet et al. 2021"),
    "SE_Alaska": (-0.74, "southern Arctic belt incl. Alaska (belt mean), Hugonnet et al. 2021"),
    "Alps": (-0.69, "non-polar mean (Central Europe not quoted in text), Hugonnet et al. 2021"),
}


def scenario_grid(
    region_stats: dict[str, dict[str, float]],
    kappas: tuple[float, ...] = (0.1, 0.3, 1.0),
    sdot0s: tuple[float, ...] = (10.0, 30.0),
    t0: float = 1995.0,
) -> pd.DataFrame:
    """Detection-year scenarios.

    region_stats[rheology_key] = dict(n_per_yr, phi, ldot_kpa_yr) - catalogue power and the
    smeared GRACE unloading rate of the matching analysis region. Where a published glacier
    specific mass change exists, a second 'glacier-surface' load-rate scenario is added.
    """
    rows = []
    for key, st in region_stats.items():
        rh = RHEOLOGIES[key]
        ldots = {"grace_box_mean": st["ldot_kpa_yr"]}
        if key in SPECIFIC_MASS_CHANGE_MWE:
            ldots["glacier_surface"] = -SPECIFIC_MASS_CHANGE_MWE[key][0] * C.G_ACC
        for lname, ldot in ldots.items():
            for eta in sorted(set(rh.eta_range) | {rh.eta}):
                lam = rh.lambda_km[1]
                tau = relaxation_time_yr(eta, lam, rh.te_km)
                comp = compensation(lam, rh.te_km)
                for kappa in kappas:
                    for sdot0 in sdot0s:
                        y = detection_year(
                            st["n_per_yr"], st["phi"], t0, tau, ldot, kappa, comp, sdot0
                        )

                        def rr(
                            year: float,
                            kappa: float = kappa,
                            sdot0: float = sdot0,
                            ldot: float = ldot,
                            tau: float = tau,
                            comp: float = comp,
                        ) -> float:
                            return float(
                                rate_ratio(np.array([year]), t0, tau, ldot, kappa, comp, sdot0)[0]
                            )

                        rows.append(
                            dict(
                                region=key,
                                load_rate_scenario=lname,
                                eta_Pa_s=eta,
                                lambda_km=lam,
                                tau_yr=tau,
                                compensation=comp,
                                kappa=kappa,
                                sdot0_kpa_yr=sdot0,
                                ldot_kpa_yr=ldot,
                                n_per_yr=st["n_per_yr"],
                                phi=st["phi"],
                                rate_ratio_2026=rr(2026.0),
                                rate_ratio_2036=rr(2036.0),
                                rate_ratio_2100=rr(2100.0),
                                rate_ratio_equilibrium=1 + kappa * comp * ldot / sdot0,
                                detect_year=y,
                                mde_slope_2036=mde_slope(
                                    st["n_per_yr"], 2026 + 10 / 12, 2036 + 10 / 12, st["phi"]
                                ),
                            )
                        )
    return pd.DataFrame(rows)
