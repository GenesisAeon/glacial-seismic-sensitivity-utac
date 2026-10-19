# AP4 result: simulated size and power of the draft A8 gate

Status: **stage 1 complete** (2026-10-19, 16:40–22:55, 1,300 replicates). Protocol fixed before
the run: `docs/adequacy/gate_power_protocol.md` (commit `fb2b394`). Exploratory, synthetic only;
no catalogue was read and no threshold was derived from real data. Raw replicates, run metadata
and `pip freeze`: `results/adequacy/gate_power_ap4/`.

**Stage 2 not run, per the pre-stated rule.** The rule was to raise null to 1,000 only if the
upper 95 % Wilson bound of the L false-gate rate exceeded 0.02. It is 0.017.

## Main table

Gate rate with Wilson 95 % interval; then the rejection rate of each test at 0.05.
glac = SE_Alaska_AK (glacier region), ctrl = Interior_AK_ctrl (control region).

| Scenario | Reps | Gate S | Gate L | T1 ctrl | T2 glac | T2 ctrl | T3 glac | T3 ctrl |
|---|---:|---|---|---:|---:|---:|---:|---:|
| **null** (true model) | 500 | **0.158** [0.129, 0.193] | **0.006** [0.002, 0.017] | 0.064 | 0.036 | 0.038 | 0.014 | 0.014 |
| **signal_glac** (glacier µ × 1.5) | 100 | 0.100 [0.055, 0.174] | 0.000 [0.000, 0.037] | 0.020 | 0.000 | 0.060 | 0.010 | 0.010 |
| p12 (Omori p = 1.2, same n) | 100 | 0.890 [0.814, 0.937] | 0.200 [0.133, 0.289] | 0.100 | 0.700 | 0.580 | 0.020 | 0.010 |
| alpha_half (α / 2, same n) | 100 | 0.180 [0.117, 0.267] | 0.010 [0.002, 0.054] | 0.030 | 0.040 | 0.090 | 0.040 | 0.000 |
| cluster_plus (n = 0.95, µ frozen) | 100 | 0.930 [0.863, 0.966] | 0.480 [0.385, 0.577] | 0.890 | 0.080 | 0.690 | 0.020 | 0.010 |
| cluster_plus_same_rate (n = 0.95, µ lowered) ¹ | 100 | 0.910 [0.838, 0.952] | 0.680 [0.583, 0.763] | 0.840 | 0.080 | 0.200 | 0.020 | 0.010 |
| swarm_ctrl (30 events / 7 days) | 100 | 0.360 [0.273, 0.458] | 0.000 [0.000, 0.037] | 0.090 | 0.060 | 0.230 | 0.010 | 0.010 |
| swarm_glac (30 events / 7 days) | 100 | 0.140 [0.085, 0.221] | 0.000 [0.000, 0.037] | 0.040 | 0.050 | 0.030 | 0.050 | 0.000 |
| mc_jump (Mc + 0.3 in 2026) | 100 | 1.000 [0.963, 1.000] | 0.650 [0.553, 0.736] | 0.830 | 0.550 | 0.350 | 1.000 | 1.000 |

Rejection rates at 0.005 (the level of variant L):

| Scenario | T1 ctrl | T2 glac | T2 ctrl | T3 glac | T3 ctrl |
|---|---:|---:|---:|---:|---:|
| null | 0.006 | 0.006 ² | 0.000 | 0.000 | 0.004 |
| p12 | 0.00 | 0.14 | 0.20 | 0.00 | 0.00 |
| cluster_plus | 0.42 | 0.00 | 0.26 | 0.00 | 0.00 |
| cluster_plus_same_rate ¹ | 0.67 | 0.00 | 0.02 | 0.00 | 0.01 |
| mc_jump | 0.64 | 0.09 | 0.04 | 1.00 | 1.00 |
| all other scenarios | ≤ 0.01 | ≤ 0.01 | ≤ 0.01 | ≤ 0.01 | 0.00 |

¹ See limitation 3: in the simulation, this scenario did not reach the model's annual count.
² 3 of 500 at the smallest p (k = 0); expected under the true model 1/400 = 0.0025 (1.25 of 500).
T2 ctrl reached k = 0 in 0 of 500. Neither glacier test enters L.

Mean window counts (null): glacier 308, control 228.

## Findings

1. **False-gate rate S = 0.158 [0.129, 0.193]**, below the independence value 0.23 and below the
   ≈ 0.2 of the draft, as expected. The KS of binned magnitudes (T3) is strongly conservative
   (0.014 at 0.05 instead of 0.05), and T2 is slightly conservative (0.036/0.038).
2. **False-gate rate L = 0.006 [0.002, 0.017]** (3 of 500, all from T1). The control T2
   (B = 399) never reached its smallest p (k = 0) under the true model (expected: 1.25 of 500). For the gate itself
   (10,000 simulations, T2 level ≈ 0.005) the expected rate is about **0.006 + 0.005 ≈ 0.011**
   (upper bound, overlap ignored). This matches the draft's "≈ 0.01". See limitation 1.
3. **The sought signal does not trigger the gate.** With a glacier background × 1.5, S = 0.10
   and L = 0.00, both not above their null rates. The separation principle works: T1 only sees
   the control region, and T2 re-estimates µ.
4. **Stronger clustering than the model (Johann's question):**
   - **T1 (count of the control region)** reacts most strongly in both variants (0.89 and 0.84 at
     0.05).
   - **T2 control** follows (0.69 with µ frozen, 0.20 at the lowered µ).
   - **T2 glacier** barely reacts (0.08). In the glacier region n only rises from 0.84 to 0.95;
     in the control region from 0.64 to 0.95.
   - **T3 does not react** (≈ 0.01–0.02), as expected since magnitudes are unchanged.
   - The N-conditional likelihood test is not part of A8. As shown in AP3, it is blind in this
     direction.
5. **A wrong Omori exponent (p = 1.2)** is found by T2 (0.70 / 0.58), not by T1 or T3. L
   detects it only in 20 % of cases, because only the control T2 enters L at 0.005.
6. **α / 2 at the same branching ratio is invisible** (S 0.18 ≈ null, L 0.01). A purely temporal
   gate cannot see how productivity depends on magnitude.
7. **A swarm of 30 events in 7 days** is hardly visible. In the control region S rises to 0.36
   through T2 (0.23), but L = 0. In the glacier region it is invisible (S 0.14 ≈ null).
8. **A completeness jump (Mc + 0.3)** is always found by S, through T3 (1.00). L catches it in
   65 % of cases, only indirectly through the count deficit (T1), because T3 is not part of L.

## What this means for the choice S vs L (descriptive, decision: Johann)

- **S:** about 1 in 6 years without any model error would end as "C2 inconclusive", even before
  any real model error. In exchange it reliably catches completeness problems (T3) and a wrong
  Omori exponent (T2).
- **L:** about 1 % false gates (≈ 0.6 % here, ≈ 1.1 % expected for the gate), and the sought
  signal stays untouched. But it is blind to Mc problems except through the count, sees a wrong p
  only in 20 % of cases, and does not see swarms.
- One option that AP4 suggests but did not test is variant L plus T3 (control) at 0.005. A
  completeness jump would then also be caught directly by L. Its size under the true model would
  be at most ≈ 0.006 + 0.004 = 0.010 in this simulation (T3 ctrl rejected 2 of 500 null
  replicates at 0.005), plus the T2 correction from finding 2. This is a suggestion only; it would
  need its own check before any freeze.

## Limitations (to be read with the numbers)

1. **T2 resolution (B = 399):** p = (1 + k)/400, smallest p = 0.0025. Variant L's threshold
   p < 0.005 is met only at k = 0, so T2's effective level in L is **0.0025, not 0.005**
   (pointed out by Johann). The simulated L rates are therefore **lower bounds** for a gate with
   10,000 simulations. Under the true model the bootstrap p is uniform, so for B → ∞ T2 adds at
   most ≈ 0.005 (finding 2). For alternatives no such correction is possible, so the L power
   values are lower bounds too. For S the effect is negligible (p < 0.05 ⇔ k ≤ 18, level 0.0475).
2. **T1 with 1,000 simulations:** discrete counts; ties count towards δ₁/δ₂. At 0.005 this is
   slightly conservative (smallest observed p-values 0, 0.002, 0.002, 0.006 …).
3. **Start-up transient (affects mainly ¹):**
   - Every replicate starts from an empty catalogue with a 2-year warm-up. That is too short for
     the cascade to reach equilibrium when n is high.
   - Measured mean window counts are below the stationary value µ e^{σ²/2}/(1 − n):
     null control 228 vs 254 (−10 %), null glacier 308 vs 382 (−19 %), cluster_plus control
     755 vs 1842 (−59 %).
   - In cluster_plus_same_rate the background is lowered to 14 % (control). The window then
     holds 122 instead of the intended ≈ 254 events.
   - **Its T1 result therefore partly measures a count deficit, not the clustering structure
     alone.** The scenario does *not* yet answer cleanly whether stronger clustering at the same
     rate is detected; this needs a longer warm-up (e.g. 20 years).
   - The size estimates (null) are not affected: T1 compares against model simulations from the
     same history, and T2/T3 are conditional on the window. Simulated histories are, however,
     somewhat lighter than a stationary 2025 would be.
4. **Assumptions:** b = 1.0, dm = 0.1 and m_max = 8.0 are not part of the frozen baseline.
   - The branching ratios used (SE-Alaska 0.84, Interior 0.64) hold for b = 1.0.
   - With a smaller real b, n would be larger. For Interior (α = 1.37) it could approach 1. In
     that case `simulate_window` refuses the model (supercritical) instead of simulating.
5. **Scenario choice** (30-event swarm, Mc + 0.3, factor 1.5) is ours, made before the run;
   other sizes give other power values. Each alternative has 100 replicates (± ≈ 0.05).
6. Three gate tests per region pair, not the full CSEP suite; no spatial model.
