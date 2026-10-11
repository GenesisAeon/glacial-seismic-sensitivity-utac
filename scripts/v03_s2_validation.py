"""v0.3 S2b (EXPLORATORY, pre-freeze): retrospective check of the S2 discriminator with
FROZEN-in-S2 thresholds (no re-tuning) on events outside the S0 case list.

Positives: ComCat-labelled landslide / mine collapse / collapse events 2000-2026 (labels hidden).
Negatives: global ComCat earthquakes M>=5, depth <= 40 km, 2025.
Writes results/v03/s2v_predictions.csv and results/v03/s2v_scores.csv.
"""

from __future__ import annotations

import json

import pandas as pd
from scipy.stats import beta

from glacial_seismic_sensitivity_utac import config as C
from glacial_seismic_sensitivity_utac import v03_discriminator as D
from glacial_seismic_sensitivity_utac import v03_features as F

RAW = F.RAW
OUT = C.OUT / "v03"
CLASS_OF = {"landslide": "mass_movement", "mine collapse": "collapse", "collapse": "collapse"}


def cp(k: int, n: int) -> tuple[float, float]:
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return lo, hi


def add_cluster(r: dict) -> dict:
    ids = [i for i in str(r.get("cluster_ids", "")).split(",") if i]
    if r["mag"] >= 4.5:
        ids.append(r["event_id"])
    r["cluster_median_dc"], r["cluster_n_mt"] = F.cluster_median_dc(ids)
    return r


def rows() -> pd.DataFrame:
    out = []
    pos = pd.concat(
        [pd.read_csv(RAW / f"val_pos_{x}.csv") for x in ("landslide", "mine_collapse", "collapse")]
    )
    for r in pos.itertuples():
        nb = RAW / "val_nb" / f"{r.id}.csv"
        if not nb.exists():
            continue
        cat = F.load_comcat(nb)
        if r.id not in set(cat.id):
            cat = pd.concat([cat, F.load_comcat_frame(pd.DataFrame([r._asdict()]))])
        lab = str(r.type).lower()
        row = add_cluster(F.event_row(r.id, cat, f"val_{lab}", CLASS_OF[lab]))
        row.update(is_control=0, in_catalogue=True)
        out.append(row)
    g = pd.concat(
        [F.load_comcat(p) for p in sorted(RAW.glob("val_global_M4.5_*.csv"))]
    ).drop_duplicates("id")
    neg = pd.read_csv(RAW / "val_neg_global_M5_2025.csv")
    for eid in neg.id:
        row = add_cluster(F.event_row(eid, g, "val_global_2025", "tectonic"))
        row.update(is_control=1, in_catalogue=True)
        out.append(row)
    return pd.DataFrame(out)


def main() -> int:
    th = D.Thresholds(**json.loads((OUT / "s2_calibration.json").read_text())["thresholds"])
    df = D.apply(rows(), th)
    df.drop(columns=["cluster_ids"]).to_csv(OUT / "s2v_predictions.csv", index=False)
    res = []
    for mode in ("no_labels", "catalogue_only"):
        p = f"pred_{mode}"
        for cls, g in df[df.is_control == 0].groupby("expected_class"):
            k, n = int((g[p] == cls).sum()), len(g)
            res.append(
                dict(
                    mode=mode,
                    set=f"positives_{cls}",
                    n=n,
                    hits=k,
                    rate=k / n,
                    ci_lo=cp(k, n)[0],
                    ci_hi=cp(k, n)[1],
                )
            )
        g = df[df.is_control == 1]
        k, n = int((g[p] != "tectonic").sum()), len(g)
        res.append(
            dict(
                mode=mode,
                set="negatives_false_positive",
                n=n,
                hits=k,
                rate=k / n,
                ci_lo=cp(k, n)[0],
                ci_hi=cp(k, n)[1],
            )
        )
    sc = pd.DataFrame(res)
    sc.to_csv(OUT / "s2v_scores.csv", index=False)
    pd.set_option("display.width", 200)
    print(sc.round(4).to_string())
    fp = df[(df.is_control == 1) & (df.pred_catalogue_only != "tectonic")]
    print(
        fp[
            [
                "event_id",
                "time_utc",
                "lat",
                "lon",
                "mag",
                "depth_km",
                "dm_long_short",
                "mt_iso_fraction",
                "n_m45_pm_half_year",
                "cluster_median_dc",
                "pred_catalogue_only",
                "rule_catalogue_only",
            ]
        ].to_string()
    )
    hit = df[df.is_control == 0]
    print(hit.groupby(["expected_class", "rule_catalogue_only"]).size())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
