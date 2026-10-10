"""v0.1.0 extensions: present-day precursors, tipping scenarios (A), quiescence (B), CSN Chile.

Run with ``glacial-sensitivity extensions`` after ``run`` (needs the frozen C1 file and F1
results). Does not change any output of the main analysis.
"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date

import numpy as np
import pandas as pd

from . import __version__, loads, precursors, quiescence, seasonal, sensitivity, tipping
from . import config as C
from .regionrun import prepare_region

# catalogue region -> (GRACE box for load acceleration, GNSS stations for uplift acceleration)
QUIESCENCE_LINKS: dict[str, tuple[str | None, tuple[str, ...]]] = {
    "Iceland_Vatnajokull_IMO": ("Vatnajokull", ("HOFN",)),
    "SE_Alaska_AK": ("SE_Alaska_box", ("AB50", "JNU1")),
    "Greenland_GEUS": ("Greenland_all", ("KULU", "QAQ1", "KELY", "SCOR", "THU2")),
    "Alps_SED": (None, ()),
    "NZ_Southern_Alps": (None, ()),
    "Himalaya_Karakoram": (None, ()),
    "Interior_AK_ctrl": (None, ("FAIR",)),
    "N_Switzerland_ctrl": (None, ()),
    "NZ_Wellington_ctrl": (None, ()),
}

# Pre-registered thresholds (docs/PREREGISTRATION.md section 6), frozen 2026-10-10
THRESHOLDS = dict(
    M1_xi_per_yr=0.02,  # GRACE normalised acceleration; lower 95 % bound must also be > 0
    M2_uplift_accel_z=3.0,  # GNSS uplift acceleration z (offsets modelled, AR(1) SE)
    M3_modulation_drop_z=2.487,  # = C1 one-sided MDE factor (alpha 0.05 / power 0.8)
    M4_b_value_drop=0.2,  # Delta b vs 2008-2019 with Mc unchanged (|Delta Mc| < 0.2)
    M5_quiet_habermann_z=-2.0,  # declustered rate change (Habermann z)
    M5_quiet_etas_z=-2.0,  # ETAS relative quiescence (flag; anti-conservative)
    artefact_ks_p=0.01,  # magnitude-distribution change between the periods ...
    artefact_dmag=0.1,  # ... with a mean-magnitude shift of at least this size
    artefact_dmc=0.2,  # or yearly-Mc median change of at least this size
)


def _out(df: pd.DataFrame, name: str) -> None:
    C.OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.OUT / name, index=False, float_format="%.6g")


def run_precursors() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, float]]:
    grace = loads.box_grace(C.EXTRA_GRACE_BOXES)
    acc = precursors.grace_acceleration(grace, list(C.EXTRA_GRACE_BOXES))
    ldot = {
        b: -loads.harmonic_fit(grace.t_yr.to_numpy(), grace[f"{b}_kPa"].to_numpy())["trend_per_yr"]
        for b in C.EXTRA_GRACE_BOXES
    }
    acc["unloading_kPa_per_yr"] = acc.box.map(ldot)
    lo = acc.xi_per_yr - 1.96 * acc.xi_se
    acc["M1_flag"] = (acc.xi_per_yr > THRESHOLDS["M1_xi_per_yr"]) & (lo > 0)
    _out(acc, "precursors_grace_acceleration.csv")
    gn = precursors.gnss_uplift()
    gn["M2_flag"] = gn.accel_z > THRESHOLDS["M2_uplift_accel_z"]
    _out(gn, "precursors_gnss_uplift.csv")
    return acc, gn, ldot


def run_tipping(acc: pd.DataFrame, ldot: dict[str, float]) -> pd.DataFrame:
    frozen = json.loads((C.OUT / "frozen_confirmatory_parameters.json").read_text(encoding="utf-8"))
    f1 = pd.read_csv(C.OUT / "F1_harmonic_growth.csv").set_index("region")
    regs = tipping.default_regions(acc, ldot, frozen)
    cat = {
        "Greenland_SE": "Greenland_GEUS",
        "SE_Alaska": "SE_Alaska_AK",
        "Iceland": "Iceland_Vatnajokull_IMO",
    }
    regs = [
        replace(r, phi=float(f1.loc[cat[k], "phi"]))
        if (k := r.key.replace("_grace", "").replace("_surface", "")) in cat and cat[k] in f1.index
        else r
        for r in regs
    ]
    summ, curves = tipping.run_scenarios(regs)
    _out(summ, "tipping_scenarios.csv")
    _out(curves, "tipping_curves.csv")
    _out(
        pd.DataFrame(
            [
                dict(
                    region=r.key,
                    trajectory=t.name,
                    onset=t.onset,
                    m2100=t.m2100,
                    xi_per_yr=t.accel_per_yr,
                    source=t.source,
                    load=r.load_label,
                    ldot_now_kPa_yr=r.ldot_now_kpa_yr,
                    n_per_yr=r.n_per_yr,
                    note=r.note,
                )
                for r in regs
                for t in r.trajectories
            ]
        ),
        "tipping_trajectories.csv",
    )
    return summ


def classify_quiescence(stats_: pd.DataFrame, acc: pd.DataFrame, gn: pd.DataFrame) -> pd.DataFrame:
    """Apply the pre-registered rule (PREREGISTRATION.md section 6) to per-region statistics.

    Quiet = Habermann z <= -2 AND the ETAS ratio of the latest window < 1 (both agree).
    An ETAS z <= -2 without Habermann support is only reported ('ETAS-only flag'): in the
    baseline run it fired in two of three control regions (Interior Alaska, Wellington) and in two
    of six glacier regions, largely from the extrapolated productivity of large earlier events,
    i.e. it has a high false-alarm rate.
    """
    accx = acc.set_index("box")
    gnx = gn.set_index("station")
    out = []
    for _, s in stats_.iterrows():
        box, stas = QUIESCENCE_LINKS.get(s.region, (None, ()))
        quiet = bool(
            s.habermann_z <= THRESHOLDS["M5_quiet_habermann_z"] and s.ratio_etas_2020_2026 < 1
        )
        etas_only = bool(not quiet and s.z_etas_2020_2026 <= THRESHOLDS["M5_quiet_etas_z"])
        dmag = s.mean_mag_b - s.mean_mag_a
        dmc = s.mc_median_b - s.mc_median_a
        artefact = bool(
            (s.ks_p_mag < THRESHOLDS["artefact_ks_p"] and abs(dmag) >= THRESHOLDS["artefact_dmag"])
            or dmc >= THRESHOLDS["artefact_dmc"]  # only a rise of Mc can fake quiet
        )
        load_acc = None if box is None else bool(accx.loc[box, "xi_per_yr"] > 0)
        upl = [x for x in stas if x in gnx.index]
        upl_acc = None if not upl else bool((gnx.loc[upl, "accel_z"] > 3).any())
        out.append(
            dict(
                delta_mean_mag=dmag,
                delta_mc_median=dmc,
                grace_box=box,
                grace_xi_per_yr=np.nan if box is None else float(accx.loc[box, "xi_per_yr"]),
                gnss=";".join(upl),
                gnss_accel_flag=upl_acc,
                quiet=quiet,
                etas_only_flag=etas_only,
                artefact_suspect=artefact,
                classification=quiescence.classify(quiet, artefact, load_acc, upl_acc),
            )
        )
    keep = [c for c in stats_.columns if c not in out[0]] if out else list(stats_.columns)
    return pd.concat([stats_[keep].reset_index(drop=True), pd.DataFrame(out)], axis=1)


def run_quiescence(acc: pd.DataFrame, gn: pd.DataFrame) -> pd.DataFrame:
    wins, rows = [], []
    for name in QUIESCENCE_LINKS:
        p = prepare_region(name)
        if p is None:
            continue
        print("quiescence", name, flush=True)
        w, s = quiescence.region_quiescence(name, p.dc, p.mc_ref, p.mc_yearly)
        wins.append(w)
        rows.append(
            dict(
                **s,
                z_etas_2016_2020=float(w.z_etas.iloc[0]),
                z_etas_2020_2026=float(w.z_etas.iloc[-1]),
                ratio_etas_2020_2026=float(w.ratio.iloc[-1]),
            )
        )
    _out(pd.concat(wins), "quiescence_etas_windows.csv")
    summ = classify_quiescence(pd.DataFrame(rows), acc, gn)
    _out(summ, "quiescence_summary.csv")
    return summ


def run_csn() -> pd.DataFrame:
    """Chilean relocated catalogue (control, ends mid-2020): F1 1990-2019 + seasonal checks."""
    name = "Central_Andes_CSN_ctrl"
    p = prepare_region(name)
    if p is None:
        return pd.DataFrame()
    last = C.REGIONS[name].last_year or C.TEST_END_YEAR
    p = replace(p, dc=p.dc[p.dc.year <= last].reset_index(drop=True))
    rng = np.random.default_rng(C.SEED + 7)
    h = sensitivity.harmonic_growth(p.decl, years=(1990, last), rng=rng)
    rows = [
        dict(
            region=name,
            catalogue="CSN relocated (Potin et al. 2024)",
            mc_ref=p.mc_ref,
            n_decl=len(p.decl),
            years=f"1990-{last}",
            **h,
        )
    ]
    f1 = pd.read_csv(C.OUT / "F1_harmonic_growth.csv")
    if "Central_Andes" in set(f1.region):
        ref = f1[f1.region == "Central_Andes"].iloc[0].to_dict()
        rows.append(dict(catalogue="ComCat (main run, 1990-2025)", **ref))
    out = pd.DataFrame(rows)
    _out(out, "csn_chile_F1.csv")
    rob = seasonal.robustness(p)
    _out(rob, "csn_chile_seasonal_robustness.csv")
    yearly = p.raw.groupby("year").size().rename("n_all").to_frame()
    yearly["mc_yearly"] = p.mc_yearly
    _out(yearly.reset_index(), "csn_chile_yearly_counts.csv")
    return out


def freeze_monitoring(acc: pd.DataFrame, gn: pd.DataFrame, q: pd.DataFrame) -> None:
    target = C.OUT / "frozen_monitoring_indicators.json"
    if target.exists():
        target = C.OUT / "frozen_monitoring_indicators_RECOMPUTED.json"
    doc = dict(
        frozen_on=str(date(2026, 10, 10)),
        package_version=__version__,
        review="annually, first review with GRACE-FO data to 2027-12 and catalogues to 2027-12",
        thresholds=THRESHOLDS,
        baseline_grace=acc.set_index("box")[["mass_rate", "mass_accel", "xi_per_yr", "xi_se"]]
        .round(5)
        .to_dict(orient="index"),
        baseline_gnss=gn.set_index("station")[["uplift_mm_yr_2015", "accel_mm_yr2", "accel_z"]]
        .round(4)
        .to_dict(orient="index"),
        baseline_quiescence=q.set_index("region")[
            ["habermann_z", "z_etas_2020_2026", "mc", "classification"]
        ].to_dict(orient="index"),
    )
    target.write_text(json.dumps(doc, indent=1, default=float))


def run_extensions(refit_quiescence: bool = True) -> None:
    acc, gn, ldot = run_precursors()
    run_tipping(acc, ldot)
    if refit_quiescence or not (C.OUT / "quiescence_summary.csv").exists():
        q = run_quiescence(acc, gn)
    else:  # re-classify the stored ETAS/Habermann statistics (ETAS fits take ~10 min)
        q = classify_quiescence(pd.read_csv(C.OUT / "quiescence_summary.csv"), acc, gn)
        _out(q, "quiescence_summary.csv")
    run_csn()
    freeze_monitoring(acc, gn, q)
