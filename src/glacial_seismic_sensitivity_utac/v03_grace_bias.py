"""v0.3 exploratory: lag-model sensitivity to the GRACE mass-loss under-estimation of
Sasgen et al. (2026), Commun. Earth Environ., doi:10.1038/s43247-026-03738-y.

Sasgen et al. report that a GIA correction for low-viscosity rheologies adds 7 +/- 1 Gt/yr
(Alaska) and 3 +/- 1 Gt/yr (Iceland) of mass loss (2002-2025), i.e. about 9 % (Alaska) and
about one third (Iceland) more than the standard GRACE estimate. Here the GRACE-based
unloading rates of the *_grace lag regions are scaled by these relative factors (central and
the range implied by +/- 1 Gt/yr) and the v0.2 rheology variants are re-run.

Assumptions (exploratory, not pre-registered; v0.1/v0.2 frozen results are not touched):
  * the correction is a constant trend: mass_rate and unloading rate scale by the factor,
    mass_accel is unchanged (so the relative acceleration xi shrinks by 1/factor);
  * the regional relative factor is applied to our GRACE boxes (SE_Alaska_box, 17 mascons;
    Vatnajokull, 1 mascon) although Sasgen's regions are not identical to these boxes;
  * *_surface regions (Hugonnet 2021 DEM rates) do not depend on GRACE and stay unchanged;
    they serve as the reference.
"""

from __future__ import annotations

import pandas as pd

from . import config as C
from . import lag_sensitivity as LS
from . import tipping

SASGEN = "Sasgen et al. 2026 doi:10.1038/s43247-026-03738-y"
BOX_OF = {"SE_Alaska": "SE_Alaska_box", "Iceland": "Vatnajokull"}
# relative GRACE under-estimation factors: (central, low, high)
FACTORS: dict[str, tuple[float, float, float]] = {
    "SE_Alaska": (1.09, 1.077, 1.103),
    "Iceland": (1.32, 1.21, 1.43),
}
FACTOR_SETS = ("none_v02", "low", "central", "high")


def factor(region: str, which: str) -> float:
    if which == "none_v02":
        return 1.0
    c, lo, hi = FACTORS[region]
    return {"central": c, "low": lo, "high": hi}[which]


def scaled_acc(acc: pd.DataFrame, which: str) -> pd.DataFrame:
    out = acc.copy()
    for region, box in BOX_OF.items():
        f = factor(region, which)
        m = out.box == box
        if not m.any():
            raise KeyError(box)
        for col in (
            "mass_rate",
            "unloading_kPa_per_yr",
            "rate_2002_2013_Gt_yr",
            "rate_2014_2026_Gt_yr",
        ):
            out.loc[m, col] = out.loc[m, col] * f
        out.loc[m, "mass_rate_se"] = out.loc[m, "mass_rate_se"] * f
    return out


def run(variants: tuple[str, ...] | None = None) -> pd.DataFrame:
    acc = pd.read_csv(C.OUT / "precursors_grace_acceleration.csv")
    names = variants or tuple(LS.SENSITIVITY_RHEOLOGIES)
    rows = []
    for which in FACTOR_SETS:
        regs = LS.build_regions(scaled_acc(acc, which))
        for name in names:
            var = LS.SENSITIVITY_RHEOLOGIES[name]
            summ, _ = tipping.run_scenarios(regs, rheologies=LS._rheo(var))
            rows.append(summ.assign(variant=name, grace_factor=which))
    return pd.concat(rows, ignore_index=True)


def summarise(summ: pd.DataFrame) -> pd.DataFrame:
    """Earliest detection year per variant x factor set x region, plus shift vs. none_v02."""
    e = LS.earliest(summ, ["variant", "grace_factor", "region"])
    ld = summ.groupby(["variant", "grace_factor", "region"]).ldot_now_kpa_yr.first()
    e = e.merge(ld.reset_index(), on=["variant", "grace_factor", "region"])
    cols = [
        "detect_quiet_year",
        "detect_increase_year",
        "detect_modulation_drop_year",
        "earliest_any",
    ]
    base = e.loc[e.grace_factor == "none_v02", ["variant", "region", *cols]]
    e = e.merge(base, on=["variant", "region"], suffixes=("", "_v02"))
    for col in cols:
        e[f"shift_{col}"] = e[col] - e[f"{col}_v02"]
    e = e.drop(columns=[f"{c}_v02" for c in cols])
    e["exploratory"] = True
    e["source"] = SASGEN
    return e
