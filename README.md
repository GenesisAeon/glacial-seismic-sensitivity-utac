# glacial-seismic-sensitivity-utac

GenesisAeon Package **133** (registry class KLIMA-KRYO-13) – companion to
[`glacial-seismicity-utac`](https://github.com/GenesisAeon/glacial-seismicity-utac) (P101).
Tests whether earthquake catalogues near melting glaciers show an **early stage** of a delayed
response to ice unloading – not via rate trends, but via a growing **sensitivity** to the seasonal
load. **Deliberately has no UTAC/CREP/AFET bridge** – see [DISCLAIMER.md](DISCLAIMER.md).

*Deutsche Fassung: [README.de.md](README.de.md). Plain-language German summary:
[WHITEPAPER.md](WHITEPAPER.md).*

## Question

If the mantle answers ice loss with a delay (decades to millennia), a flat trend in earthquake rates
today is no reassurance. A more sensitive test is whether the *same* seasonal unloading triggers *more*
earthquakes over time. This package tests that with real catalogues (USGS ComCat, Alaska Earthquake
Center, Swiss Seismological Service, GeoNet, Icelandic Met Office, GEUS), GRACE/GRACE-FO mass loads
and ERA5 precipitation, and pre-registers a confirmatory test on data from **November 2026** on.

## Key results (data 1990–2025; details in [docs/RESULTS.md](docs/RESULTS.md))

| Test | Result |
|---|---|
| F1 growing seasonal modulation | No region significant after Benjamini–Hochberg. SE Alaska (AEC, primary): +0.035 ± 0.023 per decade, one-sided permutation p = 0.10. Iceland: *decreasing*. Greenland: p = 0.006 uncorrected, likely a network artefact. |
| F2 sensitivity per kPa (GRACE) | SE Alaska: 4.0 ± 1.1 % per kPa of seasonal unloading (close to Johnson et al. 2020: 3.5 %/kPa), but **no growth** (−1.3 ± 1.1 % per kPa per decade). |
| F3 rain vs load | SE Alaska: not separable (r = 0.68). Southern Alps (NZ): load preferred over rain (exploratory). |
| Lag model (scenarios) | Relaxation times 23 yr (Patagonia) to ~2000 yr (Alps). Narrow mountain loads respond mostly elastically. A delayed viscous rate increase would not be detectable as a trend before ~2155 in any of 126 scenarios. |
| Criticality battery | 16 of 544 single tests significant after BH, mostly network/Mc, b-value and variance effects (4 in control regions); 0 of 180 glacier-vs-control group tests; no rising autocorrelation anywhere. |
| Confirmatory test C1 | Frozen 2026-10-10. Looks 2029-10-31 (α 0.01) and 2036-10-31 (α 0.04). Detects ~doubling of SE Alaska modulation by 2036. |
| A Tipping scenarios (v0.1.0) | Accelerating ice loss scaled to published ranges (Edwards 2021, DeConto 2021). Promoted-fault seismicity in 2100: SE Greenland 1.0–1.24×, Amundsen (DeConto 3 °C) 1.1–1.9×, SE Alaska 1.05–2.35×. An increase becomes detectable at the earliest in 2046 (SE Alaska, steepest path, κ = 1); Greenland only after 2100. The drop in seasonal modulation stays undetectable through 2100. |
| B Deceptive pre-tipping quiet | Possible in the model if > 50 % of faults sit in the stress shadow. It starts 7–60 yr after the acceleration begins, is 4–16 % deep and is statistically detectable around 2083 at the earliest. The geodetic indicators respond earlier. |
| Present-day precursors M1–M5 | GRACE: only Patagonia accelerates (ξ = 0.039 ± 0.007/yr); Greenland and Vatnajökull decelerate. GNSS: uplift accelerates at TOMO/BACK (Amundsen), AB50 (SE Alaska) and KELY (W Greenland). Rule-based quiescence only in the NZ Southern Alps (the control in the same network shows a similar drop). Iceland: no quiescence. |
| CSN Chile (Potin et al. 2024) | Control 1990–2019: no growing seasonal modulation (−0.070 ± 0.041 per decade). The catalogue does not cover Patagonia. |

**What this excludes and what stays open:** see [docs/LIMITATIONS.md](docs/LIMITATIONS.md). In short:
a strong increase of seasonal sensitivity of small earthquakes since 1990 is unlikely in SE Alaska;
delayed viscous responses, single large ruptures and volcanic effects are *not* excluded.

## Quickstart

```bash
pip install -e ".[dev]"
glacial-sensitivity info          # regions, paths
glacial-sensitivity fetch         # ~200 MB raw data into data/raw/ (not in git), ~15-30 min
glacial-sensitivity run           # all analyses -> results/ (~30 min; GSS_N_PERM / GSS_N_SURROGATES to tune)
glacial-sensitivity extensions    # precursors, tipping scenarios, quiescence, CSN Chile (~10 min, after run)
glacial-sensitivity plot          # charts -> charts/
glacial-sensitivity lag           # GIA relaxation-time table (no data needed)
pytest                            # offline tests on synthetic data and fixtures
```

Confirmatory run (after 2029-10-31 + 30 days):

```bash
GSS_END=2029-12-01 glacial-sensitivity fetch --force
python -m glacial_seismic_sensitivity_utac.confirmatory 2029-10-31
```

## Layout

| Path | Content |
|---|---|
| `src/glacial_seismic_sensitivity_utac/` | `fetch/` (data), `catalog`, `decluster`, `glm`, `loads`, `sensitivity` (F1–F3), `lagmodel` (F5), `seasonal`, `power`, `criticality`, `confirmatory`, `precursors`, `tipping`, `quiescence`, `extensions`, `honesty`, `plots`, `cli` |
| `results/` | all result tables, `frozen_confirmatory_parameters.json`, `frozen_monitoring_indicators.json` |
| `charts/` | 19 charts (01–17) |
| `PREREGISTRATION.md` | experiment series and pre-registration (German, English summary) |
| `docs/` | `METHODS`, `RESULTS`, `LAG_MODEL`, `ANALOGIES`, `DATA`, `LIMITATIONS`, `SOURCES`, `RELEASE_CHECKLIST` (German) |
| `scripts/verify_dois.py` | resolves every DOI in `constants.py` and `docs/SOURCES.md` via Crossref/DataCite |

## Honesty layer

`honesty.py` contains functions that return `False` by design, e.g.
`does_flat_trend_exclude_delayed_response()`, `are_retrospective_1990_2025_tests_preregistered()`,
`is_growing_sensitivity_the_generic_rate_state_expectation()`. They document what this package does
**not** show.

## Citation and licence

See [CITATION.cff](CITATION.cff). MIT licence. Data remain under their providers' terms
([docs/DATA.md](docs/DATA.md)). Package 133 is entered in the GenesisAeon package registry as
KLIMA-KRYO-13.
