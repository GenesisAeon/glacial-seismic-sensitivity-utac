"""Offline test setup: point all data paths to a temp directory before importing the package."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_TMP = Path(tempfile.mkdtemp(prefix="gss_test_"))
os.environ.setdefault("GSS_RAW", str(_TMP / "raw"))
os.environ.setdefault("GSS_OUT", str(_TMP / "out"))
os.environ.setdefault("GSS_CHARTS", str(_TMP / "charts"))
os.environ.setdefault("GSS_N_PERM_SENS", "60")
os.environ.setdefault("GSS_N_SURROGATES", "20")
os.environ.setdefault("GSS_N_PERM", "50")

FIXTURES = Path(__file__).parent / "fixtures"


def synthetic_catalog(
    n_years: int = 36,
    rate: float = 120.0,
    b0: float = 0.15,
    b1: float = 0.0,
    peak_month: float = 11.0,
    seed: int = 1,
    step_year: int | None = None,
) -> pd.DataFrame:
    """Background-only Poisson catalogue with a (possibly growing) annual modulation.

    b1: change of the log-modulation per decade (relative to 2008)."""
    rng = np.random.default_rng(seed)
    rows = []
    ph = (peak_month - 1) / 12
    for y in range(1990, 1990 + n_years):
        for m in range(1, 13):
            tau = (y + (m - 0.5) / 12 - 2008) / 10
            mult = 2.0 if step_year is not None and y >= step_year else 1.0
            mu = (
                rate
                / 12
                * mult
                * np.exp((b0 + b1 * tau) * np.cos(2 * np.pi * ((m - 0.5) / 12 - ph)))
            )
            k = rng.poisson(mu)
            days = rng.uniform(0, 28, k)
            for d in days:
                rows.append(
                    dict(
                        time=pd.Timestamp(year=y, month=m, day=1, tz="UTC")
                        + pd.Timedelta(days=float(d)),
                        latitude=rng.uniform(58, 60),
                        longitude=rng.uniform(-140, -136),
                        depth=rng.uniform(1, 30),
                        mag=2.0 + rng.exponential(1 / np.log(10)),
                        magType="ml",
                        id=f"e{len(rows)}",
                        etype="earthquake",
                    )
                )
    return pd.DataFrame(rows)


@pytest.fixture
def make_catalog():
    return synthetic_catalog
