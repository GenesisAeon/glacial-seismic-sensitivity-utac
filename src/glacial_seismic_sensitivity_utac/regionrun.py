"""Per-region preparation: load, completeness, declustering (cached in data/derived)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import config as C
from .catalog import load, reference_mc
from .decluster import cluster_table, decluster


@dataclass
class Prepared:
    name: str
    raw: pd.DataFrame  # all fetched events (after region filter)
    dc: pd.DataFrame  # events >= Mc with triggered / cluster_id
    clusters: pd.DataFrame
    mc_ref: float
    mc_yearly: pd.Series
    log_eta0: float

    @property
    def decl(self) -> pd.DataFrame:
        return self.dc[~self.dc.triggered]


def derived_dir() -> Path:
    d = C.ROOT / "data" / "derived"
    d.mkdir(parents=True, exist_ok=True)
    return d


def prepare_region(name: str, use_cache: bool = True) -> Prepared | None:
    r = C.REGIONS[name]
    if not r.raw_file.exists():
        return None
    raw = load(name)
    if len(raw) < 30:
        return None
    mc_ref, ym = reference_mc(raw)
    cache = derived_dir() / f"decl_{name}_Mc{mc_ref:.1f}.csv.gz"
    if use_cache and cache.exists() and cache.stat().st_mtime > r.raw_file.stat().st_mtime:
        dc = pd.read_csv(cache)
        dc["time"] = pd.to_datetime(dc["time"], format="ISO8601", utc=True)
        thr_f = cache.with_suffix(".thr")
        thr = float(thr_f.read_text()) if thr_f.exists() else float("nan")
    else:
        sub = raw[raw.mag >= mc_ref - 1e-9].reset_index(drop=True)
        if len(sub) > C.MAX_EVENTS_DECLUSTER:
            raise RuntimeError(f"{name}: {len(sub)} events >= Mc exceed MAX_EVENTS_DECLUSTER")
        if len(sub) < 30:
            return None
        dc, thr = decluster(sub)
        dc.to_csv(cache, index=False)
        cache.with_suffix(".thr").write_text(str(thr))
    return Prepared(name, raw, dc, cluster_table(dc), mc_ref, ym, thr)
