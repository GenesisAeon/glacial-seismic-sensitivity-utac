# Changelog

All notable changes to this project are documented here. Changes to the pre-registered confirmatory
test (see `PREREGISTRATION.md`) are listed under **Pre-registration amendments** with date and reason.

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
