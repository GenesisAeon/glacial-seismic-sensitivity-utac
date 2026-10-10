"""Confirmatory 'Fruehstadium' test on data from 2026-11-01 onward (frozen design).

Run after a look date, e.g. for look 1:
    GSS_END=2029-10-31T23:59:59 glacial-sensitivity fetch --force --regions SE_Alaska_AK
    python -m glacial_seismic_sensitivity_utac.confirmatory 2029-10-31

Everything that could be tuned is read from ``results/frozen_confirmatory_parameters.json``
(written 2026-10-10): Mc, declustering threshold log10 eta0, seasonal phase, baseline modulation
b_ref and its SE, look dates and alpha levels. The new data are declustered together with the
1990+ history (so that early-new-period aftershocks find their parents) using the FROZEN eta0,
then only background events from 2026-11-01 to the look date enter the test.
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from scipy import stats

from . import config as C
from .catalog import load
from .decluster import decluster
from .glm import fit_poisson_fe


def frozen() -> dict[str, object]:
    return dict(json.loads((C.OUT / "frozen_confirmatory_parameters.json").read_text()))


def confirmatory_test(
    region: str,
    look_date: str,
    params: dict[str, object] | None = None,
    df: pd.DataFrame | None = None,
) -> dict[str, float | str]:
    fz = params or frozen()
    regs = fz["regions"]
    assert isinstance(regs, dict)
    p = regs[region]
    looks = fz["looks"]
    assert isinstance(looks, dict)
    key = next(k for k in looks if k.split("_")[-1] == look_date)
    alpha = float(looks[key]["alpha"])
    raw = df if df is not None else load(region)
    sub = raw[raw.mag >= float(p["mc"]) - 1e-9].reset_index(drop=True)
    dc, _ = decluster(sub, threshold=float(p["log_eta0"]))
    start = pd.Timestamp(str(fz["confirmatory_data_start"]), tz="UTC")
    end = pd.Timestamp(look_date, tz="UTC") + pd.Timedelta(days=1)
    new = dc[(~dc.triggered) & (dc.time >= start) & (dc.time < end)]
    months = pd.period_range(
        start.strftime("%Y-%m"), pd.Timestamp(look_date).strftime("%Y-%m"), freq="M"
    )
    cnt = new.groupby(new.time.dt.tz_localize(None).dt.to_period("M")).size()
    cnt = cnt.reindex(months, fill_value=0)
    m = months.month.to_numpy()
    ph = (float(p["phase_peak_month"]) - 1) / 12
    x = np.cos(2 * np.pi * ((m - 0.5) / 12 - ph))
    # 12-month blocks starting November as 'years' for the fixed effects
    block = np.arange(len(months)) // 12
    r = fit_poisson_fe(cnt.to_numpy(float), block, x[:, None])
    b_ref, se_ref = float(p["b_ref"]), float(p["b_ref_se"])
    z = (float(r.coef[0]) - b_ref) / float(np.hypot(r.se[0], se_ref))
    pval = float(stats.norm.sf(z))
    return dict(
        region=region,
        look=key,
        alpha=alpha,
        n_new_events=int(len(new)),
        b_new=float(r.coef[0]),
        se_new=float(r.se[0]),
        b_ref=b_ref,
        se_ref=se_ref,
        z=z,
        p_one_sided=pval,
        reject_H0=str(pval < alpha),
    )


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - needs future data
    args = argv if argv is not None else sys.argv[1:]
    look = args[0]
    fz = frozen()
    regs = fz["regions"]
    assert isinstance(regs, dict)
    rows = [confirmatory_test(r, look, fz) for r in regs]
    out = pd.DataFrame(rows)
    out.to_csv(C.OUT / f"confirmatory_result_{look}.csv", index=False)
    print(out.to_string())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
