# Global and regional baseline (exploratory, not preregistered)

Status: **exploratory**. This is the first-pass reality check of 2026-10-10 that preceded the
public write-up of v0.2.0. It is *not* part of the preregistered confirmatory test
(`PREREGISTRATION.md`, `PREREGISTRATION_v0.2_NACHTRAG.md`) and changes none of its rules or
frozen files. It is in the repository so that every global/regional number quoted in public
texts can be reproduced from GitHub.

## Reproduce

```bash
python scripts/global_baseline.py              # offline, archived snapshots, ~2 s
python scripts/global_baseline.py --fetch data/raw/global   # fresh download (not committed)
python scripts/global_baseline.py --snapshots data/raw/global --out /tmp/gb
```

- Inputs: `results/global/snapshots/` (USGS ComCat and Smithsonian GVP as retrieved on
  2026-10-10, reduced to the columns used; region boxes in `region_boxes.csv` and
  `control_boxes.csv`; SHA-256 sums in `SHA256SUMS`).
- Outputs: `results/global/*.csv` (listed below). `tests/test_global_baseline.py` re-runs the
  analysis and checks it against the committed tables and the numbers on this page.
- A fresh download gives slightly different numbers because the catalogues are revised.

## Methods (short)

- **Global:** ComCat M ≥ 6, 1975-01-01 to 2026-10-10. Counts per year; 2026 enters with an
  exposure of 283/365 years. Trend = Poisson GLM log(rate) ~ year with log-exposure offset (IRLS,
  Wald 95 % interval); `*_quasi` columns widen the interval by √dispersion when the Pearson
  dispersion is > 1. Decade ratio 2015–2024 vs 1995–2004: exact conditional binomial interval.
- **Declustering:** Gardner–Knopoff windows as given by van Stiphout et al. (2012), largest
  event first, fore- and aftershocks flagged; same windows as `robustness_mc.gk_windows`. Ties
  in magnitude are processed in time order (see "Tie order").
- **Ice vs control:** six glaciated boxes (SE Alaska/Yakutat/Fairweather, Iceland,
  Greenland/Baffin without the mid-Atlantic ridge part, West Antarctica/Amundsen, Patagonia/South
  Andes, Alps) and five tectonically active control boxes without significant ice (Philippines,
  Indonesia, Japan, Central America, Central Andes/N Chile). M ≥ 5, declustered, rate ratio
  2010–2024 vs 1995–2009 per box and pooled, exact 95 % interval; `mde_ratio_80pct` is the
  smallest ratio detectable with 80 % power (two-sided 5 %), exp((1.96+0.84)·√(2/n̄)).
- **Volcanoes:** GVP Volcanoes of the World, eruptions with `Activity_Type = Confirmed
  Eruption`, counted by start year (global, VEI ≥ 3, Iceland, Alaska/Aleutians) and per box.

## Results (archived snapshot)

Global trends 1990 to 10 Oct 2026 (`global_trends.csv`, percent per year, 95 % interval):

| Series | Trend | Poisson interval | Dispersion | Quasi-Poisson interval |
|---|---|---|---|---|
| M ≥ 6, all | −0.46 | −0.70 to −0.21 | 3.24 | −0.90 to −0.01 |
| M ≥ 6, declustered | −0.31 | −0.62 to +0.00 | 1.18 | −0.65 to +0.03 |
| M ≥ 7, all | −0.21 | −0.99 to +0.57 | 0.92 | same |
| M ≥ 7, declustered | −0.23 | −1.07 to +0.61 | 0.71 | same |

Reading: no global increase. Allowing for overdispersion, a rise of the declustered M ≥ 6 rate
of more than about 0.03 % per year since 1990 is not compatible with these data. The rise from
1975 (+0.49 %/yr) is a catalogue effect: before about 1983 few magnitudes are moment magnitudes
(`share_Mw_types` in `global_counts_per_year.csv`), and body-wave/surface-wave magnitudes
saturate for large events.

Decade rates (`global_decade_rates.csv`, events per year): M ≥ 6 all 150.3 (1995–2004) vs
133.3 (2015–2024), ratio 0.89 (0.82 to 0.96); M ≥ 6 declustered 95.0 vs 86.4, ratio 0.91
(0.83 to 1.00); M ≥ 7 all 15.5 vs 13.7, ratio 0.88 (0.70 to 1.12) (`global_decade_ratio.csv`).

Ice vs control, M ≥ 5 declustered, 2010–2024 vs 1995–2009 (`ice_vs_control_rate_ratios.csv`):

| Group | Events | Ratio | 95 % interval | MDE (80 %) |
|---|---|---|---|---|
| Glaciated, pooled | 60 → 57 | 0.95 | 0.65 to 1.39 | 1.68 |
| Control, pooled | 2679 → 2814 | 1.05 | 1.00 to 1.11 | 1.08 |
| Glaciated, pooled, all events (not declustered) | 83 → 151 | 1.82 | 1.38 to 2.41 | |

The raw rise in the glaciated boxes comes almost entirely from swarms and aftershock sequences,
above all the 2014–2015 Bárðarbunga rifting in Iceland (Iceland all events 10 → 82,
declustered 6 → 15). Single glaciated boxes with usable counts (Alps, Iceland, Patagonia,
SE Alaska) can only detect ratios of about 2.4 to 3.5 (MDE); Greenland and West Antarctica have
almost no M ≥ 5 events. GVP eruption starts: pooled controls 223 → 235 (ratio 1.05, 0.87 to
1.27), pooled glaciated boxes 4 → 8 (ratio 2.0, 0.54 to 9.08; too few to say anything).

GVP confirmed eruption starts per year by decade (`gvp_decade_summary.csv`): 1950s 35.7,
1960s 34.1, 1970s 31.1, 1980s 31.8, 1990s 31.8, 2000s 39.2, 2010s 36.7, 2020–2025 30.3. No
upward trend; Iceland has 2–7 eruption starts per decade.

## Tie order

Window declustering depends on the order in which events of equal magnitude are processed. The
first-pass run on 2026-10-10 used an unstable sort and gave M ≥ 6 declustered −0.29 %/yr (−0.60
to +0.03) and a pooled glaciated ratio of 0.93 (60 → 56, 0.64 to 1.37). The committed script
processes ties in time order so that results are identical across numpy versions; this moves
the numbers to the values above. The differences are far inside the intervals and do not change
any conclusion, but they show that declustered counts carry a method uncertainty beyond the
Poisson interval.

## Caveats

- Exploratory and post hoc: boxes, periods and thresholds were chosen in the first pass, not
  preregistered. Treat the intervals as descriptive.
- Simple rectangular boxes; no completeness (Mc) analysis per box beyond the M ≥ 5 threshold;
  ComCat mixes magnitude types.
- Gardner–Knopoff is a coarse declustering (no ETAS); swarms are only partly removed.
- Low power in the glaciated boxes (see MDE): "no difference detected" is not "no effect".
- GVP counts depend on observation and reporting effort, which changed over the decades.

## Sources

- USGS ANSS Comprehensive Catalog (ComCat), FDSN event service:
  https://earthquake.usgs.gov/fdsnws/event/1/
- Smithsonian Institution Global Volcanism Program, Volcanoes of the World, WFS:
  https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows (https://volcano.si.edu/)
- Gardner, J. K. & Knopoff, L. (1974), BSSA 64(5), 1363–1367.
- van Stiphout, T., Zhuang, J. & Marsan, D. (2012), Seismicity declustering, CORSSA,
  https://doi.org/10.5078/corssa-52382934
- Shearer, P. M. & Stark, P. B. (2012), Global risk of big earthquakes has not recently
  increased, PNAS 109(3), 717–721, https://doi.org/10.1073/pnas.1118525109
