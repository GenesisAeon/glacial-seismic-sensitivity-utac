# AP4 protocol: simulated size and power of the draft A8 gate

Status: **fixed before the main run** (this file is committed before any counted replicate is
computed). Exploratory; synthetic data only. No catalogue is read, no threshold is derived from
the 2005–2025 data. The A8 text itself is a draft and is not changed here.

## What is simulated

Code: `etas_adequacy/gate_sim.py`, driver `scripts/adequacy_gate_power.py`.

One replicate = both regions of the primary pair (SE_Alaska_AK = glacier, Interior_AK_ctrl =
control). For each region a warm-up (2 years) and a 2025 history are simulated from the
*data-generating* model, then the 2026 window. The gate tests always use the **frozen** baseline:

| Test | As in draft A8 | AP4 resolution (gate itself: 10,000 sims) |
|---|---|---|
| T1 | control-region count vs frozen model, log µ ~ N(log µ_ref, σ_year²), conditional on the history; two-sided quantile p | 1,000 simulations |
| T2 | Ogata KS of transformed intervals vs Exp(1), µ re-estimated (`mu_window_mle`); **parametric bootstrap re-estimating µ in every simulation**; per region | B = 399 (smallest p 0.0025) |
| T3 | two-sample KS, window magnitudes vs 10-year reference (2016–2025), per region | reference = 10 × expected annual count |

Gate rules, applied afterwards to the stored p-values:

- **S (strict):** inconclusive if any of T1, T2 (glacier, control), T3 (glacier, control) has p < 0.05.
- **L (lenient):** inconclusive if T1 or T2 of the control region has p < 0.005.

Assumptions not contained in the frozen baseline: b = 1.0, magnitudes binned to 0.1, m_max = 8.0.
Each data year draws its own µ from the frozen mixture.

## Scenarios

| Name | Data-generating deviation | Regions |
|---|---|---|
| null | true frozen model → **false-gate rate** | both |
| p12 | Omori p = 1.2; K rescaled so n is unchanged (at fixed K, n would become ~2.7) | both |
| alpha_half | α / 2; K rescaled so n is unchanged | both |
| cluster_plus | stronger clustering: K scaled to n = 0.95, µ frozen (count rises strongly) | both |
| cluster_plus_same_rate | n = 0.95, background lowered so the expected annual count is unchanged | both |
| swarm_ctrl | 30 extra events within 7 days in 2026 | control |
| swarm_glac | 30 extra events within 7 days in 2026 | glacier |
| mc_jump | 2026 window loses all events below Mc_ref + 0.3 | both |
| signal_glac | glacier background × 1.5 in 2026, model otherwise true (the sought signal; the gate should *not* fire) | glacier |

The two clustering scenarios answer Johann's question of which test reacts to clustering beyond
the model. AP3 showed the N-conditional likelihood test is blind in this direction; it is not
part of A8.

## Size, seeds, resources

- Seed 20261019; replicate r of scenario i uses `SeedSequence([20261019, i, r])`. The pilot used
  seed 999 and is not counted.
- **Stage 1:** null 500 replicates, every other scenario 100. **Stage 2** (only if stage 1 leaves
  the false-gate rate of L too uncertain, i.e. the upper 95 % Wilson bound above 0.02): null up to
  1,000 with the same command and seeds.
- 2 worker processes; Windows job object with affinity to 4 of 8 logical CPUs (half), below-normal
  priority, 2 GB memory cap for the whole tree. Each replicate is appended to `<scenario>.jsonl`
  immediately (resumable). Pilot: peak ≈ 0.5 GB, null ≈ 28 s per replicate, cluster_plus 70–145 s.

## Expectations (stated before the run)

- Aeon's draft: S ≈ 0.2 (1 − 0.95⁵ ≈ 0.23 if independent), L ≈ 0.01. Expected deviations: T3
  with binned magnitudes (ties) makes the KS conservative, and T1 is discrete. S should therefore
  come out somewhat **below** 0.23. L should be ≤ 0.01.
- signal_glac: S and L near their null rates (T2 re-estimates µ, T1 sees only the control).
- mc_jump: T3 and T1 fire almost always.
- cluster_plus: T1 fires (count). cluster_plus_same_rate: open question. T2 is the candidate,
  and the result is reported as measured, including "no test fires".

## Reported

`docs/adequacy/gate_power.md`: per scenario, the gate rate for S and L with Wilson 95 % interval,
and the rejection rate of every single test at 0.05 and 0.005, plus mean window counts and the
nominal T2 p for comparison. Raw replicates are in `results/adequacy/gate_power_ap4/`.
