"""AP8: descriptive table of the frozen stage-1 ETAS parameters vs. their fit bounds.

Reads ONLY ``results/frozen_v02_baselines.json`` (SHA-256 checked via ``etas_adequacy``) and the
optimiser box ``etas_nonstat.BOUNDS_TRIG``; nothing is refitted, no frozen file is written.
Usage: ``python scripts/ap8_bounds_table.py [--write]`` (``--write`` updates the table block in
``docs/adequacy/BOUNDS.md`` between the AP8 markers; otherwise prints the table).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from glacial_seismic_sensitivity_utac import etas_nonstat
from glacial_seismic_sensitivity_utac.etas_adequacy import frozen, load_baselines

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "adequacy" / "BOUNDS.md"
BEGIN, END = "<!-- AP8-TABLE-BEGIN -->", "<!-- AP8-TABLE-END -->"
#: distance as fraction of the box width below which a value counts as AT the bound
AT_TOL = 1e-6
#: distance as fraction of the box width (log10 width for c) below which a value is NEAR the bound
NEAR_FRAC = 0.05


def bounds() -> dict[str, tuple[float | None, float | None]]:
    """Bounds in natural units; BOUNDS_TRIG order is (log K, alpha, log c, p)."""
    (k_lo, k_hi), (a_lo, a_hi), (lc_lo, lc_hi), (p_lo, p_hi) = etas_nonstat.BOUNDS_TRIG

    def ex(v: float | None) -> float | None:
        return None if v is None else math.exp(v)

    return {
        "K": (ex(k_lo), ex(k_hi)),
        "alpha": (a_lo, a_hi),
        "c_yr": (ex(lc_lo), ex(lc_hi)),
        "p": (p_lo, p_hi),
    }


def classify(name: str, v: float, lo: float | None, hi: float | None) -> tuple[str, str, str, str]:
    """(nearest bound, abs distance, rel distance, flag) as formatted strings."""
    if lo is None and hi is None:
        return "none (unbounded)", "-", "-", "-"
    cands = [(b, abs(v - b)) for b in (lo, hi) if b is not None]
    b, d = min(cands, key=lambda t: t[1])
    rel = f"{d / abs(b):.3g}" if b != 0 else "n/a (bound 0)"
    if lo is not None and hi is not None:
        width = math.log10(hi / lo) if name == "c_yr" else hi - lo
        dist_w = abs(math.log10(v / b)) if name == "c_yr" else d
        frac = dist_w / width
    else:
        frac = math.inf
    flag = "AT" if frac < AT_TOL else ("NEAR" if frac < NEAR_FRAC else "ok")
    side = "lower" if b == lo else "upper"
    return f"{b:.6g} ({side})", f"{d:.3g}", rel, flag


def table() -> str:
    bl = load_baselines()
    bd = bounds()
    rows = [
        "| Region | Param | Value | Bound (nearest) | abs. dist. | rel. dist. | Flag |",
        "|---|---|---:|---|---:|---:|---|",
    ]
    for reg in frozen.REGIONS:
        b = bl[reg]
        vals = {"K": b.K, "alpha": b.alpha, "c_yr": b.c_yr, "p": b.p}
        for name, v in vals.items():
            nb, ad, rd, fl = classify(name, v, *bd[name])
            fl = f"**{fl}**" if fl in ("AT", "NEAR") else fl
            rows.append(f"| {reg} | {name} | {v:.6g} | {nb} | {ad} | {rd} | {fl} |")
        n = etas_nonstat.branching_ratio(b.K, b.alpha, b.c_yr, b.p, b.tmax_yr, 1.0)
        rows.append(
            f"| {reg} | n_br (derived, b=1) | {n:.4g} | none (not a fit bound) | - | - | - |"
        )
    return "\n".join(rows) + "\n"


def main(argv: list[str]) -> int:
    t = table()
    if "--write" in argv:
        txt = DOC.read_text(encoding="utf-8")
        pre, rest = txt.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        DOC.write_text(f"{pre}{BEGIN}\n{t}{END}{post}", encoding="utf-8")
    else:
        sys.stdout.write(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
