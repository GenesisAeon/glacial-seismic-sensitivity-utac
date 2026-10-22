# A8 – C2 adequacy gate (draft addendum, P133 etas_adequacy)

Status: **ENTWURF, nicht eingefroren.** This is a draft for Claude's review. Johann decides the
freeze. Nothing in this file is binding until the freeze steps at the end have been completed
(before 2027-01-01, the start of the C2 window, `PREREGISTRATION_v0.2.md` sec. 5). The variant
was chosen in `gate_decision.md` (Johann Römer, 2026-10-22), based on AP4b (`gate_power_ap4b.md`,
commit `7fb8e66`). Merge commit of the work: `4c25596`.

## A8.1 Rule (variant L + T3)

> C2 is reported as **inconclusive** if, for the control region **Interior_AK_ctrl**, T1
> (number test) or T2 (Ogata KS with bootstrap re-estimation of µ) or T3 (magnitude test) has
> **p < 0.005**. Failures of T2 or T3 in the glacier region **SE_Alaska_AK** are reported as
> qualifications alongside the C2 result, which keeps its confirmatory status.

Code: `etas_adequacy/gate_sim.py`, `gate_lenient_t3` (= `gate_lenient` on T1_ctrl, T2_ctrl, plus
T3_ctrl, all at `level = 0.005`). The gate only applies to the primary pair. C1, C2's statistic,
the looks and the α levels (A1–A7) stay as they are.

A µ increase in the glacier region is the sought signal, not a model error. This is why only the
control region can make C2 inconclusive.

## A8.2 Tests

All tests use the **frozen** baseline (`results/frozen_v02_baselines.json`, SHA-checked in
`etas_adequacy/frozen.py`) and the frozen b-values (`results/adequacy/b_value/b_value_2016_2025.json`).

| Test | Definition | Resolution in the gate |
|---|---|---|
| T1 | control-region count vs frozen model, log µ ~ N(log µ_ref, σ_year²), conditional on the history; two-sided quantile p | 10,000 simulations |
| T2 | Ogata KS of transformed intervals vs Exp(1), µ re-estimated (`mu_window_mle`); parametric bootstrap re-estimating µ in every simulation; per region | 10,000 simulations |
| T3 | two-sample KS, window magnitudes vs reference magnitudes 2016–2025, per region (`stats.m_test_ks2`, `scipy.stats.ks_2samp`, `method="asymp"`) | analytic (asymptotic p) |

The T3 definition is the one already fixed in `gate_power_protocol.md` line 19 ("two-sample KS,
window magnitudes vs 10-year reference (2016–2025), per region") and in `gate_sim.py` (module
docstring line 11, call at line 222). It is not new in A8.

### T3 details

1. **Completeness threshold.** Window and reference magnitudes are taken at **Mc_ref = 2.1** for
   both regions of the primary pair. Source: `results/frozen_v02_baselines.json` lines 7
   (SE_Alaska_AK) and 18 (Interior_AK_ctrl). The frozen b-values were derived at the same value
   (`scripts/adequacy_b_value.py` line 119, `b_value(p.mag, model.mc_ref)`; recorded as
   `"mc_ref": 2.1` in `b_value_2016_2025.json` lines 15 and 313). In the simulation, window events
   below Mc_ref are dropped (`gate_sim.py` line 186).
2. **Reference years.** 2016-01-01 ≤ t < 2026-01-01, the same years as the frozen b-values
   (`b_value_2016_2025.json`, `period`; snapshots `comcat_ak_*_2016_2025.csv.gz`) and as µ_ref.
3. **Binning and ties.** Magnitudes are binned to **dm = 0.1** (`gate_sim.py` `DM = 0.1`). Binned
   magnitudes create ties, so the asymptotic KS p is conservative (size ≤ α; docstring of
   `m_test_ks2`). AP4b shows this under null (1,000 replicates): T3 rejects at 0.05 in 0.016
   (glacier) and 0.020 (control) of cases instead of 0.05, and at 0.005 in 0.000 and 0.002
   (`gate_power_ap4b.md`, main table and the line on rates at 0.005). AP4 found the same (0.014 at
   0.05, `gate_power.md` finding 1). The power against a completeness jump is not affected:
   Mc + 0.3 is caught by T3 of the control region in 100 % of cases.
4. **Test window.** T3 uses **the same test window as C2**: [2027-01-01, end of the look), with
   the looks 2029-12-31 and 2036-12-31 (`PREREGISTRATION_v0.2.md` sec. 5). Events of the year
   before only enter T1/T2 as triggers; they are not in the T3 window sample.

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

## A8.5 Open points (for review)

- **OPEN:** the T3 reference sample for the real gate. Planned: all events ≥ Mc_ref 2016–2025 of the
  frozen snapshots `results/adequacy/b_value/comcat_ak_*_2016_2025.csv.gz`, after
  `catalog.prepare`, as in the b-value derivation. To be confirmed; AP4b used a synthetic sample
  of 10 × the expected annual count.
- **OPEN:** whether T3 is evaluated with the full window at each look (proposed: yes, as C2).
- **OPEN:** the final number of simulations for T1/T2 (10,000 as in the draft) and the seed rule.

## Still needed for the freeze (to do, only after Johann's decision)

- [ ] Freeze the b-values: SHA-256 of `b_value_2016_2025.json` confirmed in `frozen.py`
      (`B_VALUE_SHA256`) and referenced in the addendum JSON.
- [ ] Code tag of `etas_adequacy`.
- [ ] Dated addendum JSON with SHA-256 values, following `results/frozen_v02_addendum_2026-10-10.json`.
- [ ] Final A8 text (this file without the status ENTWURF and with A8.5 resolved).
