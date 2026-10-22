# AP4b result: gate size and power with the frozen b, binned n and a 20-year warm-up

Status: **complete** (2026-10-21; part 1 07:45–13:21, part 2 13:22–21:20). Protocol
`gate_power_ap4b_protocol.md` (`d71f0a3`), deviations `gate_power_ap4b_deviation.md` (`1558299`).
Exploratory and synthetic only; no catalogue data except the frozen 2016–2025 b-values.
Raw replicates: `results/adequacy/gate_power_ap4b/`.

**Stage rule.** After 500 null replicates the upper Wilson bounds were 0.023 (L) and 0.026
(L + T3), so null was raised to 1,000 as pre-stated. Final upper bounds: 0.014 and 0.017.

**Rate check.** Mean window counts under null are 438 (glacier) and 266 (control); in
cluster_plus_same_rate they are 440 and 259. The same-rate scenario now matches the model's
annual count, as intended. AP4's version did not, see the correction in `gate_power.md`.

## Main table

Gate rate with Wilson 95 % interval, then the rejection rate of each test at 0.05.
glac = SE_Alaska_AK (glacier region), ctrl = Interior_AK_ctrl (control region).

| Scenario | Reps | Gate S | Gate L | **Gate L + T3** | T1 ctrl | T2 glac | T2 ctrl | T3 glac | T3 ctrl |
|---|---:|---|---|---|---:|---:|---:|---:|---:|
| **null** | 1000 | **0.153** [0.132, 0.177] | **0.007** [0.003, 0.014] | **0.009** [0.005, 0.017] | 0.052 | 0.036 | 0.042 | 0.016 | 0.020 |
| **signal_glac** (µ × 1.5) | 100 | 0.21 [0.14, 0.30] | 0.01 [0.00, 0.05] | 0.01 [0.00, 0.05] | 0.06 | 0.04 | 0.08 | 0.01 | 0.02 |
| p12 (same n) | 100 | 0.96 [0.90, 0.98] | 0.19 [0.13, 0.28] | 0.19 [0.13, 0.28] | 0.06 | 0.76 | 0.71 | 0.01 | 0.02 |
| alpha_half (same n) | 100 | 0.17 [0.11, 0.26] | 0.01 [0.00, 0.05] | 0.01 [0.00, 0.05] | 0.00 | 0.08 | 0.07 | 0.02 | 0.01 |
| **cluster_plus_same_rate** (n_eff 0.95, same count) | 100 | 0.85 [0.77, 0.91] | 0.68 [0.58, 0.76] | 0.68 [0.58, 0.76] | **0.72** | 0.06 | **0.26** | 0.03 | 0.05 |
| cluster_plus (n_eff 0.95, µ frozen) ¹ | 11 | 1.00 [0.74, 1.00] | 0.36 [0.15, 0.65] | 0.36 [0.15, 0.65] | 1.00 | 0.09 | 0.64 | 0.00 | 0.00 |
| swarm_ctrl | 100 | 0.23 [0.16, 0.32] | 0.00 [0.00, 0.04] | 0.00 [0.00, 0.04] | 0.02 | 0.02 | 0.17 | 0.01 | 0.02 |
| swarm_glac | 100 | 0.21 [0.14, 0.30] | 0.02 [0.01, 0.07] | 0.02 [0.01, 0.07] | 0.06 | 0.06 | 0.04 | 0.04 | 0.02 |
| **mc_jump** (Mc + 0.3) | 100 | 1.00 [0.96, 1.00] | **0.34** [0.26, 0.44] | **1.00** [0.96, 1.00] | 0.68 | 0.63 | 0.32 | 1.00 | 1.00 |

¹ Stopped at 11 replicates (deviation D1, Johann's decision). These may under-represent the
heaviest catalogues; not used for conclusions.

Rejection rates at 0.005 (the level of L and L + T3), null: T1 ctrl 0.006, T2 glac 0.004, T2 ctrl
0.001, T3 glac 0.000, T3 ctrl 0.002. For cluster_plus_same_rate: T1 ctrl 0.60, T2 ctrl 0.11. For
mc_jump: T1 ctrl 0.33, T3 ctrl 1.00.

## Findings

1. **False-gate rates** with the frozen b and a realistic warm-up:
   - S = **0.153** [0.132, 0.177];
   - L = **0.007** [0.003, 0.014];
   - L + T3 = **0.009** [0.005, 0.017].

   Adding T3 of the control region costs about +0.002 in false gates. This confirms AP4 (S 0.158,
   L 0.006).
2. **T2 resolution correction (as in AP4):**
   - With B = 399 the control T2 reached its smallest p (k = 0) in 1 of 1,000 null replicates;
     1/400 = 2.5 were expected.
   - For the gate with 10,000 simulations (T2 level ≈ 0.005) the expected rates are about
     **L ≈ 0.011** and **L + T3 ≈ 0.013**. These are upper bounds: overlap is ignored, the
     simulated T2-only share is replaced by 0.005.
3. **The sought signal does not trigger the gate.**
   - L and L + T3: 0.01, at the null rate.
   - S: 0.21 [0.14, 0.30], an interval that contains the null rate 0.153. With 100 replicates
     neither a difference nor its absence is established.
4. **Stronger clustering at the same rate (Johann's and Aeon's question, now answered cleanly):**
   - **T1 of the control region** reacts most strongly: 0.72 at 0.05 and 0.60 at 0.005. Over-
     clustering at the same mean count widens the year-to-year count distribution, so observed
     counts often fall outside the frozen model's predictive range, in either direction.
   - **T2 control** follows: 0.26 at 0.05, 0.11 at 0.005.
   - **T2 glacier barely reacts** (0.06). In the glacier region the effective n only rises from
     0.865 to 0.95.
   - **T3 does not react**, as expected.
   - L and L + T3: 0.68.
5. **Completeness jump (Mc + 0.3):** L catches it in 34 % of cases, **L + T3 in 100 %**, through
   the control T3. This is the main argument for L + T3: a large gain in power for about 0.002–0.004
   more false gates.
6. **Wrong Omori exponent (p = 1.2):** S 0.96, L / L + T3 0.19. At the 0.005 level only the
   control T2 enters L.
7. **α / 2 at the same n:** invisible, as in AP4.
8. **Swarms of 30 events in 7 days:** barely visible. S 0.21–0.23, L 0.00–0.02.

## Comparison of the variants (descriptive; decision: Johann)

| | S | L | L + T3 |
|---|---|---|---|
| False-gate rate (simulated / expected for the gate) | 0.153 / ≈ 0.15 | 0.007 / ≈ 0.011 | 0.009 / ≈ 0.013 |
| Sought signal triggers the gate | no (not distinguishable from null) | no | no |
| Completeness jump | 1.00 | 0.34 | **1.00** |
| Stronger clustering, same rate | 0.85 | 0.68 | 0.68 |
| Wrong Omori p | 0.96 | 0.19 | 0.19 |

## Limitations

- **Resolution:** T2 with B = 399 (smallest p 0.0025) and T1 with 1,000 simulations; the L-type
  rates are therefore lower bounds, see finding 2.
- **cluster_plus** has only 11 replicates (D1).
- **Assumptions:** dm = 0.1, m_max = 8.0, synthetic histories with a 20-year warm-up. The b-values
  are frozen from real 2016–2025 data; nothing else comes from real data.
- **Sampling error:** each alternative has 100 replicates (± ≈ 0.05).
- **Scenario sizes** (30-event swarm, Mc + 0.3, µ × 1.5, n_eff 0.95) were chosen before the run.
  Other sizes give other power values.
