"""v0.3 exploratory (S2): rule-based source-type discriminator for the collapse module.

Classes: mass_movement, collapse, caldera_collapse, tectonic (see v03_cases).  Rules are
applied in order; the first that fires wins.

  L0  catalogue label (landslide / mine collapse / collapse)          [mode 'full' only]
  R1  mass_movement: published long-period single-force inversion, or a magnitude
      discrepancy M_long - M_short >= dm_min (catalogue or published) at depth <= 1 km
  R2  collapse: published MT class 'implosive_dominant' or 'closing_crack_plus_vertical_force',
      or a catalogue full MT with isotropic fraction <= iso_max at depth <= 1 km,
      or depth <= 1 km and a LARGER event within 15 km in the preceding hour
  R4  caldera_collapse: >= n_m45_min events M>=4.5 within 15 km and +/-0.5 yr AND median ComCat
      double-couple share of their moment tensors <= dc_max (>= 3 tensors)
  else tectonic

Modes: 'full' (labels + catalogue + published), 'no_labels' (catalogue + published),
'catalogue_only' (no labels, no published values).  Thresholds are calibrated on the tectonic
controls in S2 and are therefore data-touched; S3 freezes them for prospective use only.

NOTE: the ISO sign is deliberately NOT a rule: Punggye-ri's collapse is not a pure implosion
(Chiang et al. 2018) and the Napoleonville sinkhole events show volume INCREASE (Nayak &
Dreger 2014).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

from .v03_features import NONTECTONIC_LABELS

MODES = ("full", "no_labels", "catalogue_only")
COLLAPSE_MT = ("implosive_dominant", "closing_crack_plus_vertical_force")


@dataclass(frozen=True)
class Thresholds:
    dm_min: float = 0.8
    shallow_km: float = 1.0
    n_m45_min: int = 10
    dc_max: float = 50.0
    min_mts: int = 3
    iso_max: float = -0.3

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _f(x: Any) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float("nan")
    return v


def classify(row: dict[str, Any], th: Thresholds, mode: str = "full") -> tuple[str, str]:
    """Return (class, rule) for one feature row."""
    if mode not in MODES:
        raise ValueError(mode)
    if row.get("in_catalogue", True) is False and mode == "catalogue_only":
        return "not_in_catalogue", "-"
    use_pub = mode != "catalogue_only"
    label = str(row.get("catalog_type", "")).lower()
    if mode == "full" and label in NONTECTONIC_LABELS:
        return NONTECTONIC_LABELS[label], "L0"
    depth = _f(row.get("depth_km"))
    shallow = bool(np.isfinite(depth) and depth <= th.shallow_km)
    if use_pub and row.get("pub_lp_force"):
        return "mass_movement", "R1-pub"
    dm = _f(row.get("dm_long_short"))
    if use_pub and np.isfinite(_f(row.get("pub_dm"))):
        dm = np.nanmax([dm, _f(row.get("pub_dm"))])
        shallow = shallow or bool(row.get("pub_surface_source"))
    if shallow and np.isfinite(dm) and dm >= th.dm_min:
        return "mass_movement", "R1"
    if use_pub and row.get("pub_mt_class") in COLLAPSE_MT:
        return "collapse", "R2-pub"
    iso = _f(row.get("mt_iso_fraction"))
    if shallow and np.isfinite(iso) and iso <= th.iso_max:
        return "collapse", "R2-mt"
    if shallow and _f(row.get("preceded_by_larger_1h")) == 1.0:
        return "collapse", "R2"
    n = _f(row.get("n_m45_pm_half_year"))
    dc = _f(row.get("cluster_median_dc"))
    nmt = _f(row.get("cluster_n_mt"))
    if (
        np.isfinite(n)
        and n >= th.n_m45_min
        and np.isfinite(dc)
        and dc <= th.dc_max
        and nmt >= th.min_mts
    ):
        return "caldera_collapse", "R4"
    return "tectonic", "-"


def apply(df: pd.DataFrame, th: Thresholds) -> pd.DataFrame:
    out = df.copy()
    for m in MODES:
        res = [classify(r, th, m) for r in out.to_dict("records")]
        out[f"pred_{m}"] = [c for c, _ in res]
        out[f"rule_{m}"] = [r for _, r in res]
    return out


def confusion(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    return pd.crosstab(df.expected_class, df[f"pred_{mode}"], dropna=False)


def scores(df: pd.DataFrame, group: str = "case_id") -> pd.DataFrame:
    """Per mode: event-level hits; case-level (majority vote per case) hits; FP on controls."""
    rows = []
    cases = df[df.is_control == 0]
    ctrl = df[df.is_control == 1]
    for m in MODES:
        p = f"pred_{m}"
        maj = cases.groupby(group).apply(
            lambda g, p=p: g[p].value_counts().idxmax() == g.expected_class.iloc[0],
            include_groups=False,
        )
        nonte = cases[cases.expected_class != "tectonic"]
        rows.append(
            dict(
                mode=m,
                case_events=len(cases),
                case_event_hits=int((cases[p] == cases.expected_class).sum()),
                cases=int(maj.size),
                case_hits=int(maj.sum()),
                nontectonic_cases_detected=int(
                    nonte.groupby(group)
                    .apply(
                        lambda g, p=p: (g[p] == g.expected_class).any(),
                        include_groups=False,
                    )
                    .sum()
                ),
                nontectonic_cases=int(nonte[group].nunique()),
                controls=len(ctrl),
                control_false_positives=int((ctrl[p] != "tectonic").sum()),
            )
        )
    return pd.DataFrame(rows)
