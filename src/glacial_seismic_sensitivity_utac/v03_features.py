"""v0.3 exploratory (S2): source-type features for key events of the collapse module.

Inputs are the S1 snapshots in data/raw/v03 (ComCat csv + event-detail geojson, KNMI/EMSC
FDSN text). Every feature is computed from the catalogue snapshot or taken from a publication
(``v03_cases.Published``, with DOI); the column ``feature_source`` says which.

ComCat moment tensors are deviatoric (trace = 0): an isotropic share cannot be read from them,
only the double-couple percentage (``percent-double-couple``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from . import config as C
from .catalog import haversine_km

RAW = C.RAW / "v03"

LONG_PERIOD_TYPES = ("mww", "mwc", "mwb", "mwr", "mw", "ms", "ms_20", "ms_vx", "md")
SHORT_PERIOD_TYPES = ("ml", "mb", "mlg", "mb_lg", "mblg", "mln", "mlnq")
NONTECTONIC_LABELS = {
    "landslide": "mass_movement",
    "mine collapse": "collapse",
    "collapse": "collapse",
}
FIXED_DEPTHS = (0.0, 1.0, 5.0, 10.0, 33.0)


def load_comcat(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    if d.empty:
        return pd.DataFrame(columns=["time", "lat", "lon", "depth", "mag", "magtype", "type", "id"])
    d["time"] = pd.to_datetime(d["time"], utc=True, format="ISO8601")
    return d.rename(columns={"latitude": "lat", "longitude": "lon", "magType": "magtype"})[
        ["time", "lat", "lon", "depth", "mag", "magtype", "type", "id"]
    ].assign(magtype=lambda x: x.magtype.astype(str).str.lower())


def load_fdsn_text(path: Path) -> pd.DataFrame:
    """FDSN 'text' format (KNMI, EMSC). EventType column is optional."""
    d = pd.read_csv(path, sep="|")
    d.columns = [c.lstrip("#").strip() for c in d.columns]
    out = pd.DataFrame(
        {
            "time": pd.to_datetime(d["Time"], utc=True, format="ISO8601"),
            "lat": d["Latitude"].astype(float),
            "lon": d["Longitude"].astype(float),
            "depth": pd.to_numeric(d["Depth/km"], errors="coerce"),
            "mag": pd.to_numeric(d["Magnitude"], errors="coerce"),
            "magtype": d["MagType"].astype(str).str.lower(),
            "type": d["EventType"] if "EventType" in d else "earthquake",
            "id": d["EventID"].astype(str),
        }
    )
    return out.sort_values("time").reset_index(drop=True)


def detail(eid: str, raw: Path = RAW) -> dict[str, Any] | None:
    p = raw / "detail" / f"{eid}.geojson"
    if not p.exists():
        return None
    return dict(json.loads(p.read_text(encoding="utf-8")))


def magnitudes_from_detail(j: dict[str, Any]) -> dict[str, float]:
    """All magnitude types listed in origin and moment-tensor products (first value wins)."""
    out: dict[str, float] = {}
    prods = j["properties"].get("products", {})
    for o in prods.get("origin", []):
        pr = o.get("properties", {})
        mt, m = pr.get("magnitude-type"), pr.get("magnitude")
        if mt and m not in (None, ""):
            out.setdefault(str(mt).lower(), float(m))
    for o in prods.get("moment-tensor", []):
        pr = o.get("properties", {})
        mt, m = pr.get("derived-magnitude-type"), pr.get("derived-magnitude")
        if mt and m not in (None, ""):
            out.setdefault(str(mt).lower(), float(m))
    return out


def mt_percent_dc(j: dict[str, Any]) -> float:
    """Double-couple % (0-100) of the preferred (first listed) ComCat moment tensor.

    ComCat mostly stores a fraction (0.06); a few products store a percentage (89.07).
    Values > 1 are therefore read as percent."""
    for o in j["properties"].get("products", {}).get("moment-tensor", []):
        v = o.get("properties", {}).get("percent-double-couple")
        if v not in (None, ""):
            x = float(v)
            return x if x > 1.0 else 100.0 * x
    return float("nan")


def mt_iso_fraction(j: dict[str, Any]) -> float:
    """Signed isotropic fraction (trace/3) / scalar moment of the first ComCat moment tensor
    that has a non-zero trace (full MT).  0.0 if only deviatoric tensors, NaN if none.
    Negative = volume decrease (implosive)."""
    seen = False
    for o in j["properties"].get("products", {}).get("moment-tensor", []):
        pr = o.get("properties", {})
        try:
            tr = sum(float(pr[k]) for k in ("tensor-mrr", "tensor-mtt", "tensor-mpp"))
            m0 = float(pr["scalar-moment"])
        except (KeyError, TypeError, ValueError):
            continue
        seen = True
        if m0 > 0 and abs(tr) > 1e-3 * m0:
            return tr / 3.0 / m0
    return 0.0 if seen else float("nan")


def long_short(mags: dict[str, float]) -> tuple[float, float, str, str]:
    lo = next(((k, mags[k]) for k in LONG_PERIOD_TYPES if k in mags), None)
    sh = next(((k, mags[k]) for k in SHORT_PERIOD_TYPES if k in mags), None)
    return (
        lo[1] if lo else float("nan"),
        sh[1] if sh else float("nan"),
        lo[0] if lo else "",
        sh[0] if sh else "",
    )


def sequence_features(
    cat: pd.DataFrame,
    t0: pd.Timestamp,
    lat: float,
    lon: float,
    mag: float,
    radius_km: float = 15.0,
    exclude_id: str | None = None,
) -> dict[str, float | str]:
    """Neighbourhood features of a key event in a catalogue snapshot."""
    if cat.empty:
        dist = np.array([])
        c = cat
    else:
        dist = haversine_km(cat.lat.to_numpy(), cat.lon.to_numpy(), lat, lon)
        c = (
            cat[(dist <= radius_km) & (cat.id != exclude_id)]
            if exclude_id
            else cat[dist <= radius_km]
        )
    dt_d = (c.time - t0).dt.total_seconds() / 86400.0 if len(c) else pd.Series(dtype=float)
    after = c[(dt_d > 0) & (dt_d <= 30)]
    before_1h = c[(dt_d < 0) & (dt_d >= -1 / 24) & (c.mag > mag)]
    ann = c[(dt_d.abs() <= 182.5) & (c.mag >= 4.5)]
    big_after = after[after.mag >= mag - 2.0]
    return {
        "n_after_30d_ge_m_minus2": float(len(big_after)),
        "bath_dm": float(mag - after.mag.max()) if len(after) else float("nan"),
        "preceded_by_larger_1h": float(len(before_1h) > 0),
        "trigger_type": (str(before_1h.sort_values("mag").iloc[-1].type) if len(before_1h) else ""),
        "n_m45_pm_half_year": float(len(ann) + (1 if mag >= 4.5 else 0)),
        "cluster_ids": ",".join(ann.id.astype(str)),
    }


def event_row(
    eid: str,
    cat: pd.DataFrame,
    case_id: str,
    expected: str,
    radius_km: float = 15.0,
    raw: Path = RAW,
) -> dict[str, Any]:
    """Feature row for one catalogue key event (row taken from ``cat``; details if present)."""
    r = cat.loc[cat.id == eid]
    if r.empty:
        raise KeyError(f"{eid} not in catalogue snapshot for {case_id}")
    e = r.iloc[0]
    j = detail(eid, raw)
    mags = magnitudes_from_detail(j) if j else {}
    mags.setdefault(str(e.magtype), float(e.mag))
    m_long, m_short, t_long, t_short = long_short(mags)
    seq = sequence_features(cat, e.time, e.lat, e.lon, float(e.mag), radius_km, exclude_id=eid)
    depth = float(e.depth)
    return {
        "case_id": case_id,
        "event_id": eid,
        "expected_class": expected,
        "time_utc": e.time.strftime("%Y-%m-%dT%H:%M:%S"),
        "lat": float(e.lat),
        "lon": float(e.lon),
        "mag": float(e.mag),
        "magtype": str(e.magtype),
        "catalog_type": str(e.type),
        "depth_km": depth,
        "depth_le_1km": float(depth <= 1.0),
        "depth_fixed_value": float(depth in FIXED_DEPTHS),
        "m_long": m_long,
        "m_short": m_short,
        "m_long_type": t_long,
        "m_short_type": t_short,
        "dm_long_short": m_long - m_short,
        "mt_percent_dc": mt_percent_dc(j) if j else float("nan"),
        "mt_iso_fraction": mt_iso_fraction(j) if j else float("nan"),
        "feature_source": "catalogue",
        **seq,
    }


def cluster_median_dc(ids: list[str], raw: Path = RAW) -> tuple[float, int]:
    vals = []
    for i in ids:
        j = detail(i, raw)
        if j is not None:
            v = mt_percent_dc(j)
            if np.isfinite(v):
                vals.append(v)
    return (float(np.median(vals)) if vals else float("nan"), len(vals))
