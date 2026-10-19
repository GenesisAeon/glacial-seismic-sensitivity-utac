"""Exploratory adequacy diagnostics for the frozen v0.2 temporal ETAS null model (P133).

Read-only with respect to everything frozen: the module imports ``etas_nonstat`` and reads
``results/frozen_v02_baselines.json`` but never writes, re-fits or replaces them. Results are
exploratory unless an adequacy gate is frozen as a dated addendum (draft A8) before 2027-01-01.

Plan: see docs/adequacy/README.md. Work packages AP0-AP4 (this module) precede any use on real
data; no gate threshold is derived from the 2005-2025 catalogues.
"""

from .frozen import (
    BASELINES_PATH,
    BASELINES_SHA256,
    PRIMARY_PAIR,
    REGIONS,
    Baseline,
    FrozenFileError,
    load_baselines,
)

__all__ = [
    "BASELINES_PATH",
    "BASELINES_SHA256",
    "PRIMARY_PAIR",
    "REGIONS",
    "Baseline",
    "FrozenFileError",
    "load_baselines",
]
