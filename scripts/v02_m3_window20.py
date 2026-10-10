"""EXPLORATORY (review K1, Claude Code): H3 with a +-20 h extremum search window instead of the
+-14 h code default used for the published H3 run. With +-14 h, 1-3 % of events get no phase
(one-sided extremum missing), preferentially near strain extrema. The search window is not part of
the frozen preregistration JSON (only the Tanaka convention is); the published H3 stays as run.
Writes results/v02/m3_tides_window20.csv."""

from __future__ import annotations

import numpy as np
import pandas as pd

from glacial_seismic_sensitivity_utac import etas_nonstat as E
from glacial_seismic_sensitivity_utac import tides as T
from glacial_seismic_sensitivity_utac import v02
from glacial_seismic_sensitivity_utac.quiescence import decimal_year


def main() -> None:
    pr = v02.prereg()["H3"]
    rows = []
    for name in v02.V02_REGIONS:
        p = v02._prep(name)
        if p is None:
            continue
        d = p.decl
        d = d[d.year.between(pr["years"][0], pr["years"][1])]
        t = decimal_year(d.time)
        lat, lon = d.latitude.to_numpy(float), d.longitude.to_numpy(float)
        mag = d.mag.to_numpy(float)
        row: dict[str, object] = dict(region=name, n_events=len(t))
        for hw in (14.0, 20.0):
            ph, _ = T.tidal_phase(t, lat, lon, half_window_h=hw)
            sch = T.schuster(ph)
            bs = T.b_split_test(mag, ph, p.mc_ref)
            k = f"{int(hw)}h"
            row.update(
                {
                    f"nan_frac_{k}": float(np.mean(~np.isfinite(ph))),
                    f"n_{k}": int(np.isfinite(ph).sum()),
                    f"schuster_p_{k}": sch["p"],
                    f"a_hat_{k}": sch["a_hat"],
                    f"db_{k}": bs.get("d_b", np.nan),
                    f"bsplit_p_{k}": bs.get("p_one", np.nan),
                }
            )
        rows.append(row)
        print(row, flush=True)
    df = pd.DataFrame(rows)
    glac = df.region.isin(pr["test_regions"])
    for k in ("14h", "20h"):
        for col in ("schuster_p", "bsplit_p"):
            df[f"{col}_bh_{k}"] = np.nan
            df.loc[glac, f"{col}_bh_{k}"] = E.bh_adjust(df.loc[glac, f"{col}_{k}"].to_numpy())
    df.to_csv(v02.outdir() / "m3_tides_window20.csv", index=False)


if __name__ == "__main__":
    main()
