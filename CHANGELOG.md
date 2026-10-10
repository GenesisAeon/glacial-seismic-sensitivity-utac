# Changelog

All notable changes to this project are documented here. Changes to the pre-registered confirmatory
test (see `PREREGISTRATION.md`) are listed under **Pre-registration amendments** with date and reason.

## [Unreleased] – 0.2.0.dev0 (branch `v0.2-dev`)

### Review round 1 (2026-10-10; see docs/reviews/REVIEW_RESPONSE_v0.2.md)

- Wording: mu_y is the ETAS *residual* background (not an identified forcing rate); H2.1
  conclusion, H2.2 "criterion not met" with per-region 80 %-power ratios, H3 named as correlation
  with the degree-2 body-tide areal-strain phase (ocean loading, Tsuruoka et al. 1995), M4 as
  thin-plate/half-space sensitivity informed by Sasgen et al. 2026; Kumazawa & Ogata 2013
  described faithfully (inspired by, not a reimplementation).
- Erratum (Codex P2; Claude Code B1): H2.2 windows in the null-calibration/recovery scripts were
  off by one year (half-open `window_ratio`), and the calibration catalogues lacked the 5-yr
  history and the 2025 bin. The calibration script now takes the production geometry from `v02`;
  production-faithful re-runs (`calibration_prod_p*.csv`; Claude Code independently): trend sd(z)
  <= 1.11 (1.25 sufficient), window ratio 1.18-1.30 (90 % upper bounds up to 1.42). H2.1 still
  rejected; no H2.2 class changes below a factor of 1.56. Frozen value 1.25 unchanged.
- `etas_nonstat.simulate`: p = 1 handled in the Omori inverse CDF.
- `etas_nonstat.simulate`: magnitudes drawn from Mc - dm/2 and rounded to the dm grid (lowest bin
  was half-width, b 0.90 instead of 1; Claude Code K2). Older simulation CSVs used the old simulator.
- `confirmatory_v02`: robust C2 look-date matching (`resolve_look`: decimal-year tolerance, ISO
  dates; unknown looks raise instead of silently returning alpha = NaN; Claude Code W2). Frozen
  looks/alphas unchanged.
- UTF-8 everywhere for text reads (`read_text(encoding="utf-8")`; Windows cp1252; Claude Code K4);
  `.gitattributes` extended to `results/*.json` and `PREREGISTRATION*.md`.
- CI: new job `test-min-deps` (Python 3.11 with numpy 1.26, pandas 2.1, scipy 1.11, matplotlib 3.8;
  Claude Code K5).
- `tides`: IERS 2010 nominal Love numbers as reference constants (frozen H3 values unchanged).
- `.gitattributes`: frozen JSON files are never line-ending converted (Windows CRLF hash failures).
- Tests: half-open windows, simulator at p = 1 and binned GR, IERS rescaling, C2 SE formula pinned to
  frozen JSON, C2 look resolution, calibration-script geometry, gradient at the p bound with history
  events, Gardner-Knopoff foreshocks/ties, tidal phase without gaps at +-20 h (79 tests).
- Exploratory (not preregistered): H2 null calibration in the p ≈ 1 regime; null simulation of the
  frozen C2 procedure; H3 with a +-20 h phase search window (no H3 conclusion changes;
  `m3_tides_window20.csv`); stage-1 uncertainty propagation for the H2.1 primary pair
  (`stage1_propagation_*.csv`). Draft addendum (not in force): docs/PREREG_v0.2_NACHTRAG_ENTWURF_2026-10-10.md.

### Added
- `etas_nonstat`: temporal ETAS with piecewise-constant yearly background (two-stage estimator,
  analytic gradient, chunked pair sums), DiD/BH helpers, H2.2 classification, `mu_window_mle` for C2,
  branching simulator; synthetic recovery and null-calibration studies (`scripts/v02_*_study.py`).
- `tides`: low-precision Moon/Sun ephemeris (Meeus), degree-2 body-tide areal strain, Tanaka phase,
  Schuster test, tidal b-value split, simulation MDEs.
- `robustness_mc`: Ogata–Katsura (EMR-type) Mc, Mc bootstrap, Gardner–Knopoff declustering.
- `lag_sensitivity`: Sasgen et al. 2026 rheologies as a separate sensitivity set; η scan.
- `confirmatory_v02` (C2), `v02` orchestrator (resumable, per-region checkpoints), `plots_v02`
  (charts 18–23), CLI `glacial-sensitivity v02`.
- Docs: `PREREGISTRATION_v0.2.md`, `docs/METHODS_v02.md`, `docs/v02_benchmarks.md`, v0.2 section in
  `docs/RESULTS.md`, `docs/REVIEW_PROMPTS.md`; README v0.2 sections (EN/DE).
- Tests: 30 new offline tests (ETAS recovery incl. masked-rise scenario, ephemeris against Meeus
  examples, EMR/GK, lag variants, preregistration hashes).

### Changed
- `tipping.run_scenarios` accepts an optional `rheologies` mapping (default reproduces v0.1.0 exactly).
- Version 0.2.0.dev0.

### Pre-registration amendments
- 2026-10-10 (before the v0.2 analyses and before any prospective data): **additions only**.
  H2.1/H2.2/H3 (retrospective), prospective test C2 with its own window from 2027-01-01, monitoring
  M6/M7; frozen in `results/frozen_v02_preregistration.json` (SHA-256 af7a5d02…d927d3). C2 baselines
  frozen in `results/frozen_v02_baselines.json` (SHA-256 e2fc568c…be9f401). C1, M1–M5 and all v0.1.0
  frozen parameters unchanged (hashes tested).

## [0.1.0] – 2026-10-10

### Added
- Data fetchers for USGS ComCat (incl. `catalog=ak`), SED, GeoNet, IMO (SIL), GEUS, CSN FDSN (unusable,
  HTTP 204), GRACE/GRACE-FO GSFC mascons, ERA5 via Open-Meteo, GeoNames cities.
- Relocated Chilean CSN catalogue 1982–mid-2020 (Potin et al. 2024, Zenodo 10.5281/zenodo.13146436,
  CC BY 4.0) as control `Central_Andes_CSN_ctrl` (1990–2019, outside the main run); NGL GNSS
  time series (14 stations) and step file.
- `precursors` (GRACE loss acceleration ξ, GNSS uplift acceleration), `tipping` (experiment A:
  accelerating-loss trajectories → rate-and-state seismicity ratios and detection years;
  experiment B: deceptive pre-tipping quiet with shadowed faults), `quiescence` (temporal ETAS
  relative quiescence, Habermann z, catalogue-artefact checks, classification), `extensions`
  runner and CLI command `glacial-sensitivity extensions`.
- Charts 14–17; honesty functions for the new experiments; 8 new offline tests.
- Package registered as GenesisAeon P133, class KLIMA-KRYO-13 (no longer provisional).
- F1 (growing seasonal modulation), F2 (sensitivity per kPa), F3 (rain vs load), group meta-analysis,
  lag/detection model (F5), power analysis, criticality battery from phase 2.
- Pre-registration of confirmatory test C1; frozen parameters in
  `results/frozen_confirmatory_parameters.json`.
- Charts 01–13, docs (German) and READMEs (EN/DE), whitepaper (DE).

### Pre-registration amendments
- 2026-10-10 (before any prospective data): **additions only**, confirmatory test C1 unchanged.
  Monitoring indicators M1–M5 and the hypothesis-B decision rule (PREREGISTRATION.md §6), frozen
  in `results/frozen_monitoring_indicators.json`. The M5 quiet criterion (Habermann z ≤ −2 *and*
  ETAS ratio < 1; ETAS-only flags reported, not interpreted) was fixed after the retrospective
  baseline run showed ETAS-only flags in two of three control regions.
