# A8 – C2 adequacy gate (draft addendum, P133 etas_adequacy)

Status: **ENTWURF, nicht eingefroren.** This is a draft for Claude's review. Johann decides the
freeze. Nothing in this file is binding until the freeze steps at the end have been completed
(before 2027-01-01, the start of the C2 window, `PREREGISTRATION_v0.2.md` sec. 5). The variant
was chosen in `gate_decision.md` (Johann Römer, 2026-10-22), based on AP4b (`gate_power_ap4b.md`,
commit `7fb8e66`). Merge commit of the work: `4c25596`. A8 is frozen together with A9 (`A9_c2_zone_confirmation_draft.md`,
C2 confirmation without the 2025 epicentral zone) in one dated addendum.

## A8.1 Rule (variant L + T3)

> C2 is reported as **inconclusive** if, for the control region **Interior_AK_ctrl**, T1
> (number test) or T2 (Ogata KS with bootstrap re-estimation of µ) or T3 (magnitude test) has
> **p < 0.005**. Failures of T2 or T3 in the glacier region **SE_Alaska_AK** are reported as
> qualifications alongside the C2 result, which keeps its confirmatory status.

Code: `etas_adequacy/gate_sim.py`, `gate_lenient_t3` (= `gate_lenient` on T1_ctrl, T2_ctrl, plus
T3_ctrl, all at `level = 0.005`). The gate is evaluated at **each** C2 look (2029-12-31 and
2036-12-31), each time on the **whole** window [2027-01-01, end of the look); the combined
false-gate rate over both looks is at most ≈ 0.026 (see "False alarms over both looks"). The gate only applies to the primary pair. C1, C2's statistic,
the looks and the α levels (A1–A7) stay as they are.

A µ increase in the glacier region is the sought signal, not a model error. This is why only the
control region can make C2 inconclusive.

## A8.2 Tests

All tests use the **frozen** baseline (`results/frozen_v02_baselines.json`, SHA-checked in
`etas_adequacy/frozen.py`) and the frozen b-values (`results/adequacy/b_value/b_value_2016_2025.json`).

| Test | Definition | Resolution in the gate |
|---|---|---|
| T1 | control-region count vs frozen model, log µ ~ N(log µ_ref, σ_year²), conditional on the history; two-sided quantile p | 10,000 simulations, fixed frozen seed |
| T2 | Ogata KS of transformed intervals vs Exp(1), µ re-estimated (`mu_window_mle`); parametric bootstrap re-estimating µ in every simulation; per region | B = 10,000, fixed frozen seed |
| T3 | two-sample KS, window magnitudes vs reference magnitudes 2016–2025, per region (`stats.m_test_ks2`, `scipy.stats.ks_2samp`, `method="asymp"`) | analytic (asymptotic p) |

The T3 definition is the one already fixed in `gate_power_protocol.md` line 19 ("two-sample KS,
window magnitudes vs 10-year reference (2016–2025), per region") and in `gate_sim.py` (module
docstring line 11, call at line 222). It is not new in A8.

### T3 details

1. **Completeness threshold.** Window and reference magnitudes are taken at **Mc_ref = 2.1** for
   both regions of the primary pair. Source: `results/frozen_v02_baselines.json` lines 7
   (SE_Alaska_AK) and 18 (Interior_AK_ctrl). The frozen b-values were derived at the same value
   (`scripts/adequacy_b_value.py` line 119, `b_value(p.mag, model.mc_ref)`; recorded as
   `"mc_ref": 2.1` in `b_value_2016_2025.json` lines 15 and 313). The cut itself is
   `arr[arr >= mc - 1e-9]` in `catalog.b_value` (`catalog.py` line 59). In the simulation no
   events are removed: magnitudes are drawn from Mc_ref − dm/2 and clipped at Mc_ref
   (`forecast.py` lines 70–75).
2. **Reference sample.** All events with M ≥ 2.1 in 2016-01-01 ≤ t < 2026-01-01 from the frozen
   snapshots `results/adequacy/b_value/comcat_ak_SE_Alaska_AK_2016_2025.csv.gz` and
   `comcat_ak_Interior_AK_ctrl_2016_2025.csv.gz`, after `catalog.prepare` with the region
   definition. These are **5,442 events (SE_Alaska_AK)** and **2,098 events (Interior_AK_ctrl)**,
   identical to `n_events_ge_mc` in `b_value_2016_2025.json` (recomputed by Claude and again on 2026-10-22 from the snapshots). The
   reference years are the same as for the frozen b-values and µ_ref. AP4b used a synthetic
   reference sample of 10 × the expected annual count instead.
3. **Same pipeline for the window.** The test-window catalogue must be prepared by **exactly the
   same pipeline** as the reference: the same ComCat query (`fetch.catalogs.fetch_comcat`,
   catalog=ak), `catalog.prepare` with the same region, the same Mc cut (≥ 2.1, tolerance 1e-9)
   and the same binning to 0.1. Any difference in processing changes the magnitude distribution
   and makes T3 fire because of processing, not because of the catalogue.
4. **Binning and ties.** Magnitudes are binned to **dm = 0.1** (`catalog.prepare`, `C.DM`;
   `gate_sim.py` `DM = 0.1`). Binned magnitudes create ties, so the asymptotic KS p is
   conservative (size ≤ α; docstring of `m_test_ks2`). AP4b shows this under null (1,000
   replicates): T3 rejects at 0.05 in 0.016 (glacier) and 0.020 (control) of cases instead of
   0.05, and at 0.005 in 0.000 and 0.002 (`gate_power_ap4b.md`, main table and the line on rates
   at 0.005). AP4 found the same (0.014 at 0.05, `gate_power.md` finding 1). The power against a
   completeness jump is not affected: Mc + 0.3 is caught by T3 of the control region in 100 % of
   cases.
5. **Test window and looks.** T3 uses **the same test window as C2**: [2027-01-01, end of the
   look), with the looks 2029-12-31 and 2036-12-31 (`PREREGISTRATION_v0.2.md` sec. 5). At each
   look the gate (T1, T2, T3) is evaluated on the **full** window up to that look. Events of the
   year before only enter T1/T2 as triggers; they are not in the T3 window sample.

### Resolution and seed (closed, Johann 2026-10-22)

- T1 uses **10,000** simulated catalogues, T2 a parametric bootstrap with **B = 10,000**, at both
  looks and in both regions.
- **One** fixed integer seed is used for the whole gate. It is chosen before 2027-01-01 and
  recorded in the dated addendum JSON together with A8 (the value is set in the addendum, not in
  this text). The per-test streams are derived from it with
  `np.random.SeedSequence(seed).generate_state(...)` as in `scripts/a8_dryrun_2023_2025.py`.
- There is **no rerun with another seed** and no increase of the number of simulations after
  data are seen. If a p-value lies close to 0.005, the result stands as computed.
- With B = 10,000 the smallest possible T2 p is 1/10,001 ≈ 0.0001, far below the level 0.005.

### False alarms over both looks

The gate is evaluated twice. Per look, AP4b gives an expected false-gate rate of about 0.013 for
L + T3 with 10,000 simulations (an upper bound, `gate_power_ap4b.md` finding 2). By the union
bound, the probability that the gate fires at least once over both looks is at most
2 × 0.013 ≈ **0.026**. This is an upper-bound estimate (Claude's figure, derived as above): the
two looks share the 2027–2029 data and are positively correlated, so the true rate lies between
≈ 0.013 and 0.026. It was not simulated.

## A8.3 Basis: size and power (AP4b, synthetic)

| | S | L | **L + T3** |
|---|---|---|---|
| False-gate rate (simulated, 1,000 null replicates) | 0.153 | 0.007 | **0.009** [0.005, 0.017] |
| Expected for the gate with 10,000 simulations | ≈ 0.15 | ≈ 0.011 | **≈ 0.013** |
| Sought signal (glacier µ × 1.5) triggers the gate | not distinguishable from null | 0.01 | **0.01** |
| Completeness jump Mc + 0.3 | 1.00 | 0.34 | **1.00** |
| Stronger clustering at the same rate | 0.85 | 0.68 | 0.68 |
| Wrong Omori exponent p = 1.2 | 0.96 | 0.19 | 0.19 |

Source: `gate_power_ap4b.md` (complete 2026-10-21), protocol `gate_power_ap4b_protocol.md`
(`d71f0a3`), deviations `gate_power_ap4b_deviation.md` (`1558299`).

## A8.4 Known limitations

- In AP4b T2 used B = 399 (smallest p 0.0025, T2 level 0.0025). The gate itself uses 10,000
  simulations; the expected L + T3 rate ≈ 0.013 is an upper bound (finding 2).
- cluster_plus has only 11 replicates (D1); not used for conclusions.
- Simulation assumptions: dm = 0.1, m_max = 8.0, synthetic histories with a 20-year warm-up.
  Only the b-values come from real data. Each alternative has 100 replicates (± ≈ 0.05).
- L + T3 was proposed after AP4's results had been seen (`gate_power_ap4b_protocol.md`); its
  size and power were estimated on fresh replicates (seed 20261020).

- **The 2025-12-06 M6.8 sequence (glacier region) is not handled by the gate; it is handled by
  A9.** The frozen ETAS cannot describe this sequence (AP5 `sequence_tail.md`; AP6 deviation D1
  `sequence_term_deviation.md`: an extra Omori term is not identifiable from the 2026 data). Its
  remaining excess in 2027+ lies in SE_Alaska_AK, so under A8 it can at most make glacier T2/T3
  fail, which are qualifications only; it cannot make C2 inconclusive. The gate therefore does
  **not** protect C2 against a false rejection caused by that excess. This risk is caught by the
  C2 zone confirmation of A9 (rejection counts only if the reduced statistic without the 55 km
  zone also rejects; AP6c `sequence_zone.md`). A8 and A9 are complementary and frozen together.
- The T3 reference sample of the glacier region (5,442 events, 2016–2025) contains the first
  weeks of that sequence (A9.2: 2,415 events ≥ Mc in its first 25 days, i.e. most of December
  2025). The glacier reference magnitude distribution is therefore strongly weighted by one
  aftershock sequence. This only affects glacier T3, which is a qualification; the control
  reference (2,098 events) is not affected. Kept as decided (reference = frozen b-value sample).
- Memory and runtime were **measured** for the projected 2036 look with the streaming code path
  (`forecast.iter_window` / `simulate_counts`, streamed `ogata_ks_bootstrap`, merged with #7):
  see `a8_dryrun_2036_projection.md`. Memory does not grow with the number of simulations.

## A8.5 Open points

- None of content. Seed rule and simulation count are closed (see "Resolution and seed"); the
  T3 reference sample is fixed in A8.2. A functional dry run of the real code path on legacy data (2023–2025 pseudo
  window) is documented in `a8_dryrun_2023_2025.md`, and a measured dry run of the projected
  2036 look (10-year synthetic window, streaming path) in `a8_dryrun_2036_projection.md`; both
  are tests of the pipeline only.

## Still needed for the freeze (to do, only after Johann's decision)

- [ ] Freeze the b-values: SHA-256 of `b_value_2016_2025.json` confirmed in `frozen.py`
      (`B_VALUE_SHA256`) and referenced in the addendum JSON.
- [ ] Code tag of `etas_adequacy`.
- [ ] Dated addendum JSON with SHA-256 values, following `results/frozen_v02_addendum_2026-10-10.json`.
- [ ] Record the value of the one T1/T2 seed in the addendum JSON (rule fixed above; Claude).
- [ ] Final A8 text (this file without the status ENTWURF).
