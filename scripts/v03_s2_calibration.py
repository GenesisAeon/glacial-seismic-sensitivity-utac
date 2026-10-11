"""v0.3 S2 (EXPLORATORY): features, threshold calibration on tectonic controls, rule-based
source discriminator, evaluation on the S0 cases; Groningen sequence description.

Reads the S1 snapshots (data/raw/v03, verified against results/v03/MANIFEST_v03.sha256) and
writes results/v03/s2_*.  Data-touched: the thresholds are chosen on these data.
"""

from __future__ import annotations

import hashlib
import json
import math

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import v03_cases as V
from glacial_seismic_sensitivity_utac import v03_discriminator as D
from glacial_seismic_sensitivity_utac import v03_features as F
from glacial_seismic_sensitivity_utac.catalog import b_value, haversine_km, mc_maxc

RAW = F.RAW
OUT = C.OUT / "v03"


def verify_manifest() -> int:
    n = 0
    for line in (OUT / "MANIFEST_v03.sha256").read_text(encoding="utf-8").splitlines():
        sha, name = line.split("  ", 1)
        if hashlib.sha256((RAW / name).read_bytes()).hexdigest() != sha:
            raise RuntimeError(f"snapshot changed: {name}")
        n += 1
    return n


def cat_for(case: V.Case) -> pd.DataFrame:
    q = case.queries[0]
    if q.service == "comcat":
        return F.load_comcat(RAW / f"{q.name}.csv")
    return F.load_fdsn_text(RAW / f"{q.name}.txt")


def add_cluster(row: dict, raw=RAW) -> dict:
    ids = [i for i in str(row.get("cluster_ids", "")).split(",") if i]
    if row["mag"] >= 4.5:
        ids.append(row["event_id"])
    med, n = F.cluster_median_dc(ids, raw)
    row["cluster_median_dc"], row["cluster_n_mt"] = med, n
    return row


def pub(case: V.Case, key: str):
    for p in case.published:
        if p.key == key:
            return p.value
    return None


def case_rows() -> list[dict]:
    rows: list[dict] = []
    for case in V.CASES:
        if case.status == "watchlist":
            continue
        cat = cat_for(case)
        ids = list(case.key_event_ids)
        if case.case_id == "bardarbunga_2014":
            t = cat.time
            sel = (
                (cat.mag >= 5.0)
                & (t >= pd.Timestamp("2014-08-16", tz="UTC"))
                & (t < pd.Timestamp("2015-02-28", tz="UTC"))
                & (haversine_km(cat.lat, cat.lon, case.lat, case.lon) <= 15.0)
            )
            ids = list(cat.loc[sel, "id"])
        if case.case_id == "groningen":
            ids = [str(cat.loc[cat.mag.idxmax(), "id"])]
        for eid in ids:
            r = F.event_row(eid, cat, case.case_id, case.expected_class)
            r = add_cluster(r)
            r["in_catalogue"] = True
            rows.append(r)
        if case.case_id == "bingham_2013":
            for t, ml in zip(pub(case, "origin_times_utc"), pub(case, "ML"), strict=True):
                rows.append(
                    dict(
                        case_id=case.case_id,
                        event_id=f"published_{t}",
                        expected_class=case.expected_class,
                        time_utc=t,
                        mag=ml,
                        magtype="ml",
                        catalog_type="",
                        in_catalogue=False,
                        feature_source="published (10.1130/gsatg191a.1)",
                    )
                )
    for r in rows:
        case = V.case_by_id(r["case_id"])
        r["is_control"] = 0
        r["pub_mt_class"] = pub(case, "mt_class") or ""
        r["pub_lp_force"] = bool(pub(case, "lp_force_history"))
        r["pub_surface_source"] = case.expected_class == "mass_movement" and bool(
            pub(case, "md_min")
        )
        if case.case_id == "bingham_2013":
            r["pub_dm"] = float(pub(case, "md_min")) - float(r["mag"])
        elif case.case_id == "crandall_2007":
            r["pub_dm"] = float(pub(case, "Mw")) - float(pub(case, "ML"))
        else:
            r["pub_dm"] = float("nan")
    return rows


def control_rows() -> list[dict]:
    rows: list[dict] = []
    centres = [(c.lat, c.lon) for c in V.CASES]
    for reg in V.CONTROL_REGIONS:
        cat = F.load_comcat(RAW / f"control_{reg}.csv")
        ms = cat[(cat.type == "earthquake") & (cat.mag >= V.CONTROL_MAINSHOCK_MIN)]
        near = np.zeros(len(ms), bool)
        for la, lo in centres:
            near |= haversine_km(ms.lat, ms.lon, la, lo) <= V.CONTROL_EXCLUDE_KM
        for eid in ms.loc[~near, "id"]:
            if F.detail(eid) is None:
                continue
            r = add_cluster(F.event_row(eid, cat, f"control_{reg}", "tectonic"))
            r.update(is_control=1, in_catalogue=True, pub_mt_class="", pub_lp_force=False)
            r.update(pub_surface_source=False, pub_dm=float("nan"))
            rows.append(r)
    return rows


def calibrate(ctrl: pd.DataFrame) -> tuple[D.Thresholds, dict]:
    """Exploratory: thresholds just outside the tectonic-control distributions."""
    dm = ctrl.dm_long_short.dropna()
    q99_dm = float(dm.quantile(0.99)) if len(dm) else float("nan")
    dm_min = max(0.8, math.ceil(q99_dm * 10 + 1e-9) / 10 + 0.1) if np.isfinite(q99_dm) else 0.8
    n_ok = ctrl[(ctrl.cluster_n_mt >= 3)]
    q01_dc = float(n_ok.cluster_median_dc.quantile(0.01)) if len(n_ok) else float("nan")
    dc_max = min(50.0, math.floor(q01_dc) - 1) if np.isfinite(q01_dc) else 50.0
    n45 = ctrl.n_m45_pm_half_year
    th = D.Thresholds(dm_min=round(dm_min, 2), n_m45_min=10, dc_max=float(dc_max))
    info = dict(
        controls=len(ctrl),
        controls_with_dm=int(len(dm)),
        control_dm_q50=float(dm.median()) if len(dm) else None,
        control_dm_q99=q99_dm,
        control_dm_max=float(dm.max()) if len(dm) else None,
        controls_with_cluster_mt=int(len(n_ok)),
        control_cluster_dc_q01=q01_dc,
        control_cluster_dc_q50=float(n_ok.cluster_median_dc.median()) if len(n_ok) else None,
        control_n_m45_q99=float(n45.quantile(0.99)),
        control_n_m45_max=float(n45.max()),
        control_depth_le_1km=int((ctrl.depth_km <= 1.0).sum()),
        control_preceded_by_larger_1h=int((ctrl.preceded_by_larger_1h == 1).sum()),
        control_full_mt=int((ctrl.mt_iso_fraction.abs() > 0).sum()),
        control_single_dc_lt10=int((ctrl.mt_percent_dc < 10).sum()),
        control_single_dc_n=int(ctrl.mt_percent_dc.notna().sum()),
    )
    return th, info


def groningen_sequence() -> tuple[pd.DataFrame, dict]:
    g = F.load_fdsn_text(RAW / "groningen_knmi.txt")
    g = g[g.time < pd.Timestamp(V.END, tz="UTC")]
    g["year"] = g.time.dt.year
    ann = g.groupby("year").agg(
        n_all=("mag", "size"),
        n_ml_ge_1_5=("mag", lambda m: int((m >= 1.5).sum())),
        mmax=("mag", "max"),
    )
    info: dict = {"event_types": g.type.value_counts().to_dict()}
    info["depth_values_km"] = g.depth.round(1).value_counts().head(5).to_dict()
    for a, b in ((1995, 2013), (2014, 2022), (2023, 2026)):
        m = g[(g.year >= a) & (g.year <= b)].mag
        mc = mc_maxc(m)
        mc = float(np.nanmax([mc, 1.5]))
        bb, sb, n = b_value(m, mc)
        info[f"b_{a}_{b}"] = dict(mc=mc, b=bb, sigma=sb, n=n)
    info["largest"] = g.loc[g.mag.idxmax(), ["id", "time", "mag", "type"]].astype(str).to_dict()
    return ann.reset_index(), info


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n_files = verify_manifest()
    cases = pd.DataFrame(case_rows())
    ctrl = pd.DataFrame(control_rows())
    th, info = calibrate(ctrl)
    df = pd.concat([cases, ctrl], ignore_index=True)
    pred = D.apply(df, th)
    keep = [c for c in pred.columns if c != "cluster_ids"]
    pred[keep].to_csv(OUT / "s2_predictions.csv", index=False)
    sc = D.scores(pred)
    sc.to_csv(OUT / "s2_scores.csv", index=False)
    for m in D.MODES:
        D.confusion(pred, m).to_csv(OUT / f"s2_confusion_{m}.csv")
    ann, ginfo = groningen_sequence()
    ann.to_csv(OUT / "s2_groningen_annual.csv", index=False)
    meta = dict(
        status="EXPLORATORY (S2, data-touched)",
        manifest_files_verified=n_files,
        thresholds=th.to_dict(),
        calibration=info,
        groningen=ginfo,
    )
    (OUT / "s2_calibration.json").write_text(
        json.dumps(meta, indent=1, default=str) + "\n", encoding="utf-8"
    )
    pd.set_option("display.width", 220)
    print(json.dumps(meta, indent=1, default=str))
    print(sc.to_string())
    cols = [
        "case_id",
        "event_id",
        "mag",
        "depth_km",
        "catalog_type",
        "dm_long_short",
        "mt_percent_dc",
        "n_m45_pm_half_year",
        "cluster_median_dc",
        "cluster_n_mt",
        "preceded_by_larger_1h",
        "pred_full",
        "pred_no_labels",
        "pred_catalogue_only",
    ]
    print(pred[pred.is_control == 0][cols].to_string())
    print(pred[(pred.is_control == 1) & (pred.pred_catalogue_only != "tectonic")][cols].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
