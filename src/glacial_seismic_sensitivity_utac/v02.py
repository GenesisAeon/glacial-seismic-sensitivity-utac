"""v0.2 orchestrator (milestones M0-M4). Every stage writes its own files under results/v02/
and skips work whose output exists (resumable); per-region checkpoints for slow stages.

Stages
  m0   benchmark: events, pair counts and log-likelihood timing per region and tmax (no fits)
  m1   catalogue robustness: EMR Mc, Mc bootstrap, Gardner-Knopoff; F1 / Habermann z reruns
  m2   nonstationary-background ETAS: H2.1 trend, H2.2 classification (PREREGISTRATION_v0.2)
  m3   body-tide phase: Schuster test, b-value split, power (MDE)
  m4   lag sensitivity with Sasgen et al. 2026 rheologies
  base C2 baselines (frozen reference mu and scatter for the 2027+ window)
"""

from __future__ import annotations

import json
import time
import tracemalloc
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from . import config as C
from . import etas_nonstat as E
from .quiescence import decimal_year
from .regionrun import Prepared, prepare_region

V02_REGIONS = (
    "SE_Alaska_AK",
    "Interior_AK_ctrl",
    "NZ_Southern_Alps",
    "NZ_Wellington_ctrl",
    "Alps_SED",
    "N_Switzerland_ctrl",
    "Iceland_Vatnajokull_IMO",
    "Greenland_GEUS",
)
PAIRS = (  # glacier, control (network-internal); first = primary
    ("SE_Alaska_AK", "Interior_AK_ctrl"),
    ("NZ_Southern_Alps", "NZ_Wellington_ctrl"),
    ("Alps_SED", "N_Switzerland_ctrl"),
)
DESCRIPTIVE = ("Iceland_Vatnajokull_IMO", "Greenland_GEUS")
FIT_T0, FIT_T1 = 1995.0, 2026.0  # bins 1995 .. 2025 (last complete year = C.TEST_END_YEAR)
HISTORY_YEARS = 5.0  # events before FIT_T0 that may trigger (no likelihood contribution)
TMAX = 1.0
WIN_A, WIN_B = (2008.0, 2020.0), (2020.0, 2026.0)  # H2.2 windows (2008-2019 vs 2020-2025)


def outdir() -> Path:
    d = C.OUT / "v02"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(outdir() / "v02_run.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def region_events(
    p: Prepared, t0: float = FIT_T0 - HISTORY_YEARS, t1: float = FIT_T1
) -> tuple[np.ndarray, np.ndarray]:
    d = p.dc.sort_values("time")
    t = decimal_year(d.time)
    m = d.mag.to_numpy(float)
    sel = (t >= t0) & (t < t1)
    return t[sel], m[sel]


def _prep(name: str) -> Prepared | None:
    p = prepare_region(name)
    if p is None:
        log(f"{name}: no data")
    return p


# ---------------------------------------------------------------------------
# M0
# ---------------------------------------------------------------------------
def stage_m0(
    regions: tuple[str, ...] = V02_REGIONS, tmaxs: tuple[float, ...] = (1.0, 3.0, 5.0)
) -> pd.DataFrame:
    f = outdir() / "m0_benchmark.csv"
    if f.exists():
        return pd.read_csv(f)
    rows = []
    for name in regions:
        p = _prep(name)
        if p is None:
            continue
        t, m = region_events(p)
        edges = np.arange(FIT_T0, FIT_T1 + 0.5, 1.0)
        for tm in tmaxs:
            npairs = E.n_pairs(t, tm)
            row: dict[str, Any] = dict(
                region=name,
                mc=p.mc_ref,
                n_events=len(t),
                n_target=int(((t >= FIT_T0) & (t < FIT_T1)).sum()),
                tmax_yr=tm,
                n_pairs=npairs,
                pair_storage_mb=npairs * 16 / 1e6,
            )
            if npairs * 16 < 1.2e9:  # skip the build if the pair arrays alone exceed ~1.2 GB
                tracemalloc.start()
                tic = time.time()
                d = E.ETASData.build(t, m, p.mc_ref, FIT_T0, FIT_T1, edges, tm)
                row["build_s"] = time.time() - tic
                x = np.concatenate(
                    [np.full(d.n_bins, np.log(50.0)), [np.log(0.02), 1.0, np.log(0.002), 1.1]]
                )
                tic = time.time()
                E.loglik_grad(x, d, 1.0)
                row["loglik_grad_s"] = time.time() - tic
                row["peak_mb"] = tracemalloc.get_traced_memory()[1] / 1e6
                tracemalloc.stop()
                del d
            rows.append(row)
            log(f"m0 {name} tmax={tm}: {row}")
    out = pd.DataFrame(rows)
    out.to_csv(f, index=False)
    return out


def _checkpoint(stage: str, name: str) -> Path:
    d = outdir() / f"{stage}_regions"
    d.mkdir(exist_ok=True)
    return d / f"{name}.json"


def _jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def _per_region(stage: str, fn: Any, regions: tuple[str, ...]) -> list[dict[str, Any]]:
    rows = []
    for name in regions:
        ck = _checkpoint(stage, name)
        if ck.exists():
            rows.append(json.loads(ck.read_text(encoding="utf-8")))
            continue
        tic = time.time()
        res = fn(name)
        if res is None:
            continue
        res = _jsonable(dict(region=name, **res, runtime_s=time.time() - tic))
        ck.write_text(json.dumps(res, indent=1))
        log(f"{stage} {name} done in {time.time() - tic:.0f}s")
        rows.append(res)
    return rows


# ---------------------------------------------------------------------------
# M1 catalogue robustness
# ---------------------------------------------------------------------------
def _habermann(decl: pd.DataFrame) -> float:
    from .quiescence import habermann_z

    yrs = decl.time.dt.year
    ca = yrs.value_counts().reindex(range(2008, 2020), fill_value=0).to_numpy()
    cb = yrs.value_counts().reindex(range(2020, 2026), fill_value=0).to_numpy()
    return habermann_z(ca, cb)


def _f1(decl: pd.DataFrame, n_perm: int) -> dict[str, float]:
    from . import sensitivity

    if int(decl.year.between(1990, C.TEST_END_YEAR).sum()) < C.SENS_MIN_EVENTS:
        return dict(b1_per_decade=np.nan, b1_se=np.nan, b1_p_perm_one=np.nan, n_events=len(decl))
    h = sensitivity.harmonic_growth(decl, rng=np.random.default_rng(C.SEED + 1), n_perm=n_perm)
    return {
        k: h.get(k, np.nan)
        for k in ("n_events", "b0", "b1_per_decade", "b1_se", "b1_p_wald_one", "b1_p_perm_one")
    }


M1_N_PERM = 500
M1_N_BOOT = 200


def m1_region(name: str) -> dict[str, Any] | None:
    from . import robustness_mc as R
    from .catalog import mc_maxc
    from .decluster import decluster
    from .regionrun import derived_dir

    p = _prep(name)
    if p is None:
        return None
    raw = p.raw
    rec = raw[raw.year.between(2008, C.TEST_END_YEAR)].mag.to_numpy()
    out: dict[str, Any] = dict(mc_ref_maxc=p.mc_ref)
    mc_e, ym_e = R.reference_mc_emr(raw)
    out["mc_ref_emr"] = mc_e
    out["mc_maxc_2008_2025"] = mc_maxc(rec)
    out["mc_emr_2008_2025"] = R.mc_emr(rec)["mc"]
    for meth in ("maxc", "emr"):
        bs = R.mc_bootstrap(rec, meth, M1_N_BOOT, np.random.default_rng(C.SEED + 11))
        out.update({f"boot_{meth}_{k}": v for k, v in bs.items()})
    # v0.1 baseline (MAXC Mc, NN declustering)
    base = _f1(p.decl, M1_N_PERM)
    out.update({f"v01_{k}": v for k, v in base.items()})
    out["v01_habermann_z"] = _habermann(p.decl)
    out["v01_n_decl"] = len(p.decl)
    # Gardner-Knopoff at the v0.1 Mc
    gk = R.gardner_knopoff(p.dc.drop(columns=["triggered"], errors="ignore"))
    gk_decl = gk[~gk.triggered]
    out.update({f"gk_{k}": v for k, v in _f1(gk_decl, M1_N_PERM).items()})
    out["gk_habermann_z"] = _habermann(gk_decl)
    out["gk_n_decl"] = len(gk_decl)
    # EMR Mc with NN declustering
    if np.isfinite(mc_e) and abs(mc_e - p.mc_ref) > 1e-9:
        cache = derived_dir() / f"decl_{name}_Mc{mc_e:.1f}.csv.gz"
        if cache.exists():
            dc = pd.read_csv(cache)
            dc["time"] = pd.to_datetime(dc["time"], format="ISO8601", utc=True)
        else:
            sub = raw[raw.mag >= mc_e - 1e-9].reset_index(drop=True)
            if len(sub) > C.MAX_EVENTS_DECLUSTER or len(sub) < 30:
                dc = None
            else:
                dc, thr = decluster(sub)
                dc.to_csv(cache, index=False)
                cache.with_suffix(".thr").write_text(str(thr))
        if dc is not None:
            e_decl = dc[~dc.triggered]
            out.update({f"emr_{k}": v for k, v in _f1(e_decl, M1_N_PERM).items()})
            out["emr_habermann_z"] = _habermann(e_decl)
            out["emr_n_decl"] = len(e_decl)
    else:
        out.update({f"emr_{k}": out[f"v01_{k}"] for k in base})
        out["emr_habermann_z"] = out["v01_habermann_z"]
        out["emr_n_decl"] = out["v01_n_decl"]
    return out


def stage_m1(regions: tuple[str, ...] = V02_REGIONS) -> pd.DataFrame:
    df = pd.DataFrame(_per_region("m1", m1_region, regions))
    df.to_csv(outdir() / "m1_catalogue_robustness.csv", index=False)
    return df


# ---------------------------------------------------------------------------
# M2 nonstationary-background ETAS (PREREGISTRATION_v0.2 H2.1 / H2.2)
# ---------------------------------------------------------------------------
def prereg() -> dict[str, Any]:
    return dict(json.loads((C.OUT / "frozen_v02_preregistration.json").read_text(encoding="utf-8")))


def m2_region(name: str) -> dict[str, Any] | None:
    pr = prereg()["H2"]
    p = _prep(name)
    if p is None:
        return None
    t, m = region_events(p)
    edges = np.arange(FIT_T0, FIT_T1 + 0.5, 1.0)
    s1, f = E.fit_two_stage(
        t, m, p.mc_ref, FIT_T0, FIT_T1, edges=edges, tmax=pr["tmax_yr"], rw_sd=pr["rw_sd"]
    )
    tab = f.table()
    tab.to_csv(outdir() / f"m2_mu_{name}.csv", index=False)
    tr = E.log_mu_trend(f, (FIT_T0, FIT_T1))
    tr["se_calibrated"] = tr["se"] * pr["se_calibration_factor"]
    wr = E.window_ratio(f, WIN_A, WIN_B)
    k = pr["se_calibration_factor"]
    if np.isfinite(wr["se"]):
        wr["se_calibrated"] = wr["se"] * k
        wr["lo95_cal"] = float(np.exp(wr["log_ratio"] - 1.96 * wr["se"] * k))
        wr["hi95_cal"] = float(np.exp(wr["log_ratio"] + 1.96 * wr["se"] * k))
    tg = (t >= FIT_T0) & (t < FIT_T1)
    na = int(((t >= WIN_A[0]) & (t < WIN_A[1])).sum())
    nb = int(((t >= WIN_B[0]) & (t < WIN_B[1])).sum())
    total_ratio = (nb / (WIN_B[1] - WIN_B[0])) / (na / (WIN_A[1] - WIN_A[0])) if na else np.nan
    cls = E.classify_background(total_ratio, wr.get("lo95_cal", np.nan), wr.get("hi95_cal", np.nan))
    # stationary v0.1-style stage-1 fit for reference
    return dict(
        mc=p.mc_ref,
        n_target=int(tg.sum()),
        K=s1.K,
        alpha=s1.alpha,
        c_days=s1.c_yr * 365.25,
        p=s1.p,
        branching_ratio=s1.branching_ratio,
        mu_stationary=float(s1.mu[0]),
        converged=bool(s1.converged and f.converged),
        slope_per_decade=tr["slope_per_decade"],
        slope_se=tr["se_calibrated"],
        slope_se_ols=tr["se_ols"],
        slope_se_lik=tr["se_lik"],
        resid_sd=tr["resid_sd"],
        mu_ratio=wr.get("ratio", np.nan),
        mu_log_ratio=wr["log_ratio"],
        mu_log_ratio_se=wr.get("se_calibrated", np.nan),
        mu_ratio_lo95=wr.get("lo95_cal", np.nan),
        mu_ratio_hi95=wr.get("hi95_cal", np.nan),
        total_ratio=total_ratio,
        n_2008_2019=na,
        n_2020_2025=nb,
        classification=cls,
        bg_fraction=float(np.sum(f.mu * f.table().t_end.sub(f.table().t_start)) / max(tg.sum(), 1)),
    )


def stage_m2(regions: tuple[str, ...] = V02_REGIONS) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame(_per_region("m2", m2_region, regions))
    df.to_csv(outdir() / "m2_etas_background.csv", index=False)
    s = df.set_index("region")
    rows = []
    for g, c in PAIRS:
        if g not in s.index or c not in s.index:
            continue
        r = E.did_test(
            dict(slope_per_decade=s.loc[g, "slope_per_decade"], se=s.loc[g, "slope_se"]),
            dict(slope_per_decade=s.loc[c, "slope_per_decade"], se=s.loc[c, "slope_se"]),
        )
        rows.append(dict(glacier=g, control=c, primary=(g, c) == PAIRS[0], **r))
    did = pd.DataFrame(rows)
    if len(did):
        did["p_bh"] = E.bh_adjust(did.p_one.to_numpy())
        did["reject_bh_0.05"] = did.p_bh < 0.05
    did.to_csv(outdir() / "m2_H21_did.csv", index=False)
    return df, did


# ---------------------------------------------------------------------------
# M3 tides
# ---------------------------------------------------------------------------
def m3_region(name: str) -> dict[str, Any] | None:
    from . import tides as T

    pr = prereg()["H3"]
    p = _prep(name)
    if p is None:
        return None
    d = p.decl
    d = d[d.year.between(pr["years"][0], pr["years"][1])]
    t = decimal_year(d.time)
    ph, amp = T.tidal_phase(t, d.latitude.to_numpy(float), d.longitude.to_numpy(float))
    pd.DataFrame(
        dict(time=d.time.astype(str).to_numpy(), mag=d.mag.to_numpy(), phase_deg=ph, strain=amp)
    ).to_csv(outdir() / f"m3_phases_{name}.csv.gz", index=False)
    sch = T.schuster(ph)
    bs = T.b_split_test(d.mag.to_numpy(float), ph, p.mc_ref)
    n = int(np.isfinite(ph).sum())
    rng = np.random.default_rng(C.SEED + 3)
    return dict(
        mc=p.mc_ref,
        n_decl=n,
        **{f"schuster_{k}": v for k, v in sch.items()},
        **{f"bsplit_{k}": v for k, v in bs.items()},
        mde_amplitude=T.schuster_mde(n, 0.05, 0.8, 300, rng),
        mde_delta_b=T.db_mde(
            n,
            b=bs["b_comp"] if np.isfinite(bs.get("b_comp", np.nan)) else 1.0,
            n_sim=200,
            rng=rng,
            mc=p.mc_ref,
        ),
        strain_rms=float(np.nanstd(amp)),
    )


def stage_m3(regions: tuple[str, ...] = V02_REGIONS) -> pd.DataFrame:
    df = pd.DataFrame(_per_region("m3", m3_region, regions))
    glac = df.region.isin(prereg()["H3"]["test_regions"])
    for col, out in (("schuster_p", "schuster_p_bh"), ("bsplit_p_one", "bsplit_p_bh")):
        df[out] = np.nan
        ok = glac & df[col].notna()
        if ok.any():
            df.loc[ok, out] = E.bh_adjust(df.loc[ok, col].to_numpy())
    df.to_csv(outdir() / "m3_tides.csv", index=False)
    return df


# ---------------------------------------------------------------------------
# M4 lag sensitivity
# ---------------------------------------------------------------------------
def stage_m4() -> None:
    from . import lag_sensitivity as L

    f1 = outdir() / "m4_lag_variants.csv"
    if not f1.exists():
        v = L.run_variants()
        v.to_csv(f1, index=False)
        L.earliest(v, ["variant", "region"]).to_csv(outdir() / "m4_lag_earliest.csv", index=False)
    f2 = outdir() / "m4_eta_scan.csv"
    if not f2.exists():
        s = L.run_eta_scan()
        s.to_csv(f2, index=False)
        L.earliest(s, ["te_km", "eta_Pa_s", "region"]).to_csv(
            outdir() / "m4_eta_scan_earliest.csv", index=False
        )


# ---------------------------------------------------------------------------
# C2 baselines (frozen before 2027-01-01)
# ---------------------------------------------------------------------------
def stage_base() -> dict[str, Any]:
    import hashlib

    f = C.OUT / "frozen_v02_baselines.json"
    if f.exists():
        return dict(json.loads(f.read_text(encoding="utf-8")))
    pr = prereg()["C2"]
    regs: dict[str, Any] = {}
    for name in V02_REGIONS:
        ck = _checkpoint("m2", name)
        tabf = outdir() / f"m2_mu_{name}.csv"
        if not ck.exists() or not tabf.exists():
            continue
        r = json.loads(ck.read_text(encoding="utf-8"))
        tab = pd.read_csv(tabf)
        a, b = pr["reference_years"]
        sel = tab[(tab.t_start >= a) & (tab.t_end <= b + 1)]
        regs[name] = dict(
            mc_ref=r["mc"],
            K=r["K"],
            alpha=r["alpha"],
            c_yr=r["c_days"] / 365.25,
            p=r["p"],
            tmax_yr=prereg()["H2"]["tmax_yr"],
            log_mu_ref=float(sel.log_mu.mean()),
            sigma_year=float(sel.log_mu.std(ddof=1)),
            n_ref_years=len(sel),
        )
    out = dict(
        description="Frozen C2 baselines (PREREGISTRATION_v0.2.md sec. 5); computed from data "
        "up to 2025-12-31 before the C2 window opens on 2027-01-01.",
        created=time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        prereg_sha256=hashlib.sha256(
            (C.OUT / "frozen_v02_preregistration.json").read_bytes()
        ).hexdigest(),
        regions=regs,
    )
    f.write_text(json.dumps(out, indent=1) + "\n")
    return out


def stage_plot() -> None:
    from . import plots_v02

    plots_v02.all_charts()


def main(stages: list[str]) -> None:
    for s in stages:
        log(f"stage {s} start")
        fn = globals().get(f"stage_{s}")
        if fn is None:
            raise SystemExit(f"unknown v0.2 stage: {s}")
        fn()
        log(f"stage {s} done")
