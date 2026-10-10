"""Lag-model sensitivity to the low-viscosity GIA rheologies of Sasgen et al. (2026) (v0.2, M4).

Source: Sasgen, I. et al. (2026), Commun. Earth Environ. 7:518, doi:10.1038/s43247-026-03738-y.
Values used (as stated in the paper): Alaska tomography-preferred asthenosphere viscosity
3e18 Pa s with lithosphere thickness 30 km; Iceland 1e18 Pa s, 30 km (GNSS fit: 40 km);
ensemble range 1e18 - 3e19 Pa s and 30 - 90 km.

Caveat: in a GIA earth model "lithosphere thickness" is an elastic-layer thickness and is used
here as Te of the thin-plate filter (lagmodel.compensation). The asthenosphere viscosity is used
as the half-space viscosity of lagmodel.relaxation_time_yr. Both are simplifications.

lagmodel.RHEOLOGIES (v0.1.0) is NOT modified; the alternative values live in
SENSITIVITY_RHEOLOGIES and are passed to tipping.run_scenarios(rheologies=...).
"""

from __future__ import annotations

import json
from dataclasses import replace

import numpy as np
import pandas as pd

from . import config as C
from . import lagmodel, tipping

SASGEN = "Sasgen et al. 2026 doi:10.1038/s43247-026-03738-y"

# variant name -> {rheology key: Rheology}
SENSITIVITY_RHEOLOGIES: dict[str, dict[str, lagmodel.Rheology]] = {
    "v0.1.0 (frozen)": {},
    "Sasgen2026_preferred": {
        "SE_Alaska": replace(
            lagmodel.RHEOLOGIES["SE_Alaska"],
            eta=3e18,
            eta_range=(1e18, 3e19),
            te_km=30.0,
            source=SASGEN + " (Alaska preferred, LT 30 km)",
        ),
        "Iceland": replace(
            lagmodel.RHEOLOGIES["Iceland"],
            eta=1e18,
            eta_range=(1e18, 3e19),
            te_km=30.0,
            source=SASGEN + " (Iceland, LT 30 km)",
        ),
    },
    "Sasgen2026_eta_TeV01": {  # only the viscosity changed, v0.1 Te kept
        "SE_Alaska": replace(
            lagmodel.RHEOLOGIES["SE_Alaska"],
            eta=3e18,
            source=SASGEN + " (eta only; Te 60 km from v0.1)",
        ),
        "Iceland": replace(
            lagmodel.RHEOLOGIES["Iceland"],
            eta=1e18,
            source=SASGEN + " (eta only; Te 15 km from v0.1)",
        ),
    },
    "Sasgen2026_Iceland_GNSS_LT40": {
        "Iceland": replace(
            lagmodel.RHEOLOGIES["Iceland"],
            eta=1e18,
            te_km=40.0,
            source=SASGEN + " (Iceland GNSS fit, LT 40 km)",
        ),
    },
    "Sasgen2026_ensemble_high": {
        "SE_Alaska": replace(
            lagmodel.RHEOLOGIES["SE_Alaska"],
            eta=3e19,
            te_km=90.0,
            source=SASGEN + " (ensemble upper end)",
        ),
        "Iceland": replace(
            lagmodel.RHEOLOGIES["Iceland"],
            eta=3e19,
            te_km=90.0,
            source=SASGEN + " (ensemble upper end)",
        ),
    },
}

ETA_SCAN = tuple(float(x) for x in np.logspace(18, 20, 9))
LAG_REGIONS = ("SE_Alaska_grace", "SE_Alaska_surface", "Iceland_grace", "Iceland_surface")


def _rheo(variant: dict[str, lagmodel.Rheology]) -> dict[str, lagmodel.Rheology]:
    return {**lagmodel.RHEOLOGIES, **variant}


def build_regions() -> list[tipping.TipRegion]:
    """Rebuild the v0.1.0 TipRegions from the v0.1.0 result files (no refit)."""
    acc = pd.read_csv(C.OUT / "precursors_grace_acceleration.csv")
    ldot = dict(zip(acc.box, acc.unloading_kPa_per_yr, strict=True))
    frozen = json.loads((C.OUT / "frozen_confirmatory_parameters.json").read_text(encoding="utf-8"))
    regs = tipping.default_regions(acc, ldot, frozen)
    f1_path = C.OUT / "F1_harmonic_growth.csv"
    if f1_path.exists():
        f1 = pd.read_csv(f1_path).set_index("region")
        cat = {
            "SE_Alaska": "SE_Alaska_AK",
            "Iceland": "Iceland_Vatnajokull_IMO",
            "Greenland_SE": "Greenland_GEUS",
        }
        out = []
        for r in regs:
            k = r.key.replace("_grace", "").replace("_surface", "")
            out.append(
                replace(r, phi=float(f1.loc[cat[k], "phi"]))
                if k in cat and cat[k] in f1.index
                else r
            )
        regs = out
    return [r for r in regs if r.key in LAG_REGIONS]


def run_variants() -> pd.DataFrame:
    regs = build_regions()
    rows = []
    for name, var in SENSITIVITY_RHEOLOGIES.items():
        summ, _ = tipping.run_scenarios(regs, rheologies=_rheo(var))
        rows.append(summ.assign(variant=name))
    return pd.concat(rows, ignore_index=True)


def run_eta_scan(te_values: tuple[float, ...] = (30.0, 60.0)) -> pd.DataFrame:
    regs = [r for r in build_regions() if r.key.startswith("SE_Alaska")]
    rows = []
    for te in te_values:
        for eta in ETA_SCAN:
            var = {"SE_Alaska": replace(lagmodel.RHEOLOGIES["SE_Alaska"], eta=eta, te_km=te)}
            summ, _ = tipping.run_scenarios(regs, kappas=(1.0,), rheologies=_rheo(var))
            rows.append(summ.assign(eta_Pa_s=eta, te_km=te))
    return pd.concat(rows, ignore_index=True)


def earliest(summ: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Earliest detection years (any trajectory / kappa / Sdot0 / shadow) per group."""
    cols = ["detect_quiet_year", "detect_increase_year", "detect_modulation_drop_year"]
    g = summ.groupby(by)
    out = g[cols].min().reset_index()
    out["tau_yr"] = g["tau_yr"].first().to_numpy()
    out["compensation"] = g["compensation"].first().to_numpy()
    out["earliest_any"] = out[cols].min(axis=1)
    return out
