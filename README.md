# glacial-seismic-sensitivity-utac

GenesisAeon Package **133 (provisional)** – companion to
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

**What this excludes and what stays open:** see [docs/LIMITATIONS.md](docs/LIMITATIONS.md). In short:
a strong increase of seasonal sensitivity of small earthquakes since 1990 is unlikely in SE Alaska;
delayed viscous responses, single large ruptures and volcanic effects are *not* excluded.

## Quickstart

```bash
pip install -e ".[dev]"
glacial-sensitivity info          # regions, paths
glacial-sensitivity fetch         # ~200 MB raw data into data/raw/ (not in git), ~15-30 min
glacial-sensitivity run           # all analyses -> results/ (~30 min; GSS_N_PERM / GSS_N_SURROGATES to tune)
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
| `src/glacial_seismic_sensitivity_utac/` | `fetch/` (data), `catalog`, `decluster`, `glm`, `loads`, `sensitivity` (F1–F3), `lagmodel` (F5), `seasonal`, `power`, `criticality`, `confirmatory`, `honesty`, `plots`, `cli` |
| `results/` | all result tables, `frozen_confirmatory_parameters.json` |
| `charts/` | 15 charts (01–13) |
| `PREREGISTRATION.md` | experiment series and pre-registration (German, English summary) |
| `docs/` | `METHODS`, `RESULTS`, `LAG_MODEL`, `ANALOGIES`, `DATA`, `LIMITATIONS`, `SOURCES`, `RELEASE_CHECKLIST` (German) |
| `scripts/verify_dois.py` | resolves every DOI in `constants.py` via Crossref |

## Honesty layer

`honesty.py` contains functions that return `False` by design, e.g.
`does_flat_trend_exclude_delayed_response()`, `are_retrospective_1990_2025_tests_preregistered()`,
`is_growing_sensitivity_the_generic_rate_state_expectation()`. They document what this package does
**not** show.

## Citation and licence

See [CITATION.cff](CITATION.cff). MIT licence. Data remain under their providers' terms
([docs/DATA.md](docs/DATA.md)). Package number 133 is provisional until entered in the GenesisAeon
package registry.
