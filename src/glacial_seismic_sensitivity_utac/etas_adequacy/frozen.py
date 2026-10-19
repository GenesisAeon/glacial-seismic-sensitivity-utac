"""Read-only access to the frozen v0.2 ETAS baselines (C2 null model) for adequacy diagnostics.

The adequacy module only *diagnoses* whether the frozen temporal ETAS model reproduces data. It
never writes or re-fits anything frozen (``results/frozen_*.json``, the preregistration documents,
``etas_nonstat.py`` / ``confirmatory_v02.py`` at tag v0.2.0). :func:`load_baselines` checks the
SHA-256 of the baseline file against the value frozen in ``results/frozen_v03_preregistration.json``
before parsing it and returns immutable objects.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

REPO_ROOT = Path(__file__).resolve().parents[3]
BASELINES_PATH = REPO_ROOT / "results" / "frozen_v02_baselines.json"
#: SHA-256 of results/frozen_v02_baselines.json as frozen in frozen_v03_preregistration.json
#: (key ``sha256_frozen_v01_v02``) and frozen_v02_addendum_2026-10-10.json.
BASELINES_SHA256 = "e2fc568c93622c97607c122c210ed5fcccace0d2440b8cd420fddd931be9f401"

REGIONS = (
    "SE_Alaska_AK",
    "Interior_AK_ctrl",
    "NZ_Southern_Alps",
    "NZ_Wellington_ctrl",
    "Alps_SED",
    "N_Switzerland_ctrl",
    "Iceland_Vatnajokull_IMO",
    "Greenland_GEUS",
)
#: The pair the adequacy gate (draft addendum A8) is restricted to: glacier region, control region.
PRIMARY_PAIR = ("SE_Alaska_AK", "Interior_AK_ctrl")

_FIELDS = (
    "mc_ref",
    "K",
    "alpha",
    "c_yr",
    "p",
    "tmax_yr",
    "log_mu_ref",
    "sigma_year",
    "n_ref_years",
)


class FrozenFileError(ValueError):
    """A frozen input does not match its frozen SHA-256 or its expected structure."""


@dataclass(frozen=True)
class Baseline:
    """Frozen C2 baseline of one region (triggering parameters and reference background)."""

    region: str
    mc_ref: float
    K: float
    alpha: float
    c_yr: float
    p: float
    tmax_yr: float
    log_mu_ref: float
    sigma_year: float
    n_ref_years: int

    @property
    def mu_ref(self) -> float:
        """Reference background rate [events/yr above mc_ref]."""
        return math.exp(self.log_mu_ref)

    def trig(self) -> dict[str, float]:
        """Triggering parameters with the keys used by ``etas_nonstat.mu_window_mle``."""
        return dict(K=self.K, alpha=self.alpha, c_yr=self.c_yr, p=self.p, tmax=self.tmax_yr)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_baselines(
    path: str | Path = BASELINES_PATH, expected_sha256: str = BASELINES_SHA256
) -> Mapping[str, Baseline]:
    """Load the frozen v0.2 baselines read-only after verifying their SHA-256.

    Raises :class:`FrozenFileError` if the bytes differ from the frozen hash or the structure is
    not exactly the frozen one (8 regions, 9 numeric fields each, finite values)."""
    data = Path(path).read_bytes()
    got = sha256_bytes(data)
    if got != expected_sha256:
        raise FrozenFileError(f"{path}: SHA-256 {got} differs from the frozen {expected_sha256}")
    doc = json.loads(data.decode("utf-8"))
    regions = doc.get("regions")
    if not isinstance(regions, dict) or tuple(regions) != REGIONS:
        raise FrozenFileError(f"{path}: unexpected region set {list(regions or [])}")
    out: dict[str, Baseline] = {}
    for name, rec in regions.items():
        if not isinstance(rec, dict) or set(rec) != set(_FIELDS):
            raise FrozenFileError(f"{path}: {name} has fields {sorted(rec or [])}")
        vals = {k: rec[k] for k in _FIELDS}
        if not all(isinstance(v, int | float) and not isinstance(v, bool) for v in vals.values()):
            raise FrozenFileError(f"{path}: {name} has non-numeric values")
        if not all(math.isfinite(float(v)) for v in vals.values()):
            raise FrozenFileError(f"{path}: {name} has non-finite values")
        out[name] = Baseline(
            region=name,
            mc_ref=float(vals["mc_ref"]),
            K=float(vals["K"]),
            alpha=float(vals["alpha"]),
            c_yr=float(vals["c_yr"]),
            p=float(vals["p"]),
            tmax_yr=float(vals["tmax_yr"]),
            log_mu_ref=float(vals["log_mu_ref"]),
            sigma_year=float(vals["sigma_year"]),
            n_ref_years=int(vals["n_ref_years"]),
        )
    return MappingProxyType(out)
