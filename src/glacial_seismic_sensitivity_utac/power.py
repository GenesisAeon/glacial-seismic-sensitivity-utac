"""Power / minimal detectable effects for the pre-registered confirmatory test (data from
2026-11-01 onward) and the frozen parameters it will use.

Confirmatory statistic (frozen 2026-10-10): seasonal modulation b_new, fitted with the year-FE
harmonic model along the *frozen* 1990-2025 phase on declustered events >= the frozen Mc in the
new data only, compared with the 1990-2025 baseline b_ref:  z = (b_new - b_ref)/sqrt(se_new^2 +
se_ref^2), one-sided (b_new > b_ref).  Looks: 2029-10-31 (alpha 0.01) and 2036-10-31 (alpha 0.04);
Bonferroni-style split, total alpha 0.05 per region; the primary region is SE_Alaska_AK.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from . import config as C
from .glm import fit_poisson_fe

LOOKS = (
    ("look1_2029-10-31", 3.0, C.CONFIRM_ALPHA_INTERIM),
    ("final_2036-10-31", 10.0, C.CONFIRM_ALPHA_FINAL),
)


def se_harmonic(n_events: float, phi: float = 1.0) -> float:
    """Approximate SE of a cosine-regressor coefficient in a Poisson model (Var(cos) = 1/2)."""
    return float(np.sqrt(2 * max(phi, 1.0) / max(n_events, 1e-9)))


def mde_difference(
    n_new: float, se_ref: float, alpha: float, phi: float = 1.0, power: float = 0.8
) -> float:
    z = stats.norm.isf(alpha) + stats.norm.isf(1 - power)
    return float(z * np.hypot(se_harmonic(n_new, phi), se_ref))


def power_table(baselines: pd.DataFrame) -> pd.DataFrame:
    """baselines: region, rate_per_yr (declustered >= Mc), b_ref, b_ref_se, phi."""
    rows = []
    for _, r in baselines.iterrows():
        for look, years, alpha in LOOKS:
            n_new = r.rate_per_yr * years
            mde = mde_difference(n_new, r.b_ref_se, alpha, r.phi)
            rows.append(
                dict(
                    region=r.region,
                    look=look,
                    years_new=years,
                    alpha=alpha,
                    n_new_expected=n_new,
                    b_ref=r.b_ref,
                    se_new=se_harmonic(n_new, r.phi),
                    mde_b_diff=mde,
                    mde_relative_to_b_ref=mde / r.b_ref if r.b_ref > 0 else np.nan,
                    years_new_mid_minus_2008=2026.83 + years / 2 - C.SENS_REF_YEAR,
                )
            )
    return pd.DataFrame(rows)


def simulate_power(
    rate_per_yr: float,
    b_ref: float,
    b_diff: float,
    years: float,
    alpha: float,
    se_ref: float,
    n_sim: int = 500,
    seed: int = C.SEED,
) -> float:
    """Monte-Carlo check of the analytic MDE (Poisson, no overdispersion)."""
    rng = np.random.default_rng(seed)
    n_m = int(round(years * 12))
    m = (np.arange(n_m) % 12) + 1
    yr = np.arange(n_m) // 12
    x = np.cos(2 * np.pi * (m - 0.5) / 12)
    hits = 0
    for _ in range(n_sim):
        b_r = b_ref + rng.normal(0, se_ref)
        mu = rate_per_yr / 12 * np.exp((b_ref + b_diff) * x)
        y = rng.poisson(mu)
        res = fit_poisson_fe(y, yr, x[:, None])
        z = (res.coef[0] - b_r) / np.hypot(res.se[0], se_ref)
        hits += z > stats.norm.isf(alpha)
    return hits / n_sim
