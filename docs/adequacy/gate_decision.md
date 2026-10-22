# Decision: adequacy gate variant for draft addendum A8

**Decision (Johann Römer, 2026-10-22):** the C2 adequacy gate uses **variant L + T3**.

> C2 is reported as **inconclusive** if, for the control region Interior_AK_ctrl, T1 (number test)
> or T2 (Ogata KS with bootstrap re-estimation of µ) or **T3 (magnitude test)** has **p < 0.005**.
> Failures in the glacier region are reported as qualifications alongside the C2 result, which
> keeps its confirmatory status.

The decision was conveyed by Aeon (`agent-inbox/an-claude/2026-10-22_Aeon_Entscheidung_Gate_L+T3.md`)
and recorded here by Claude.

## Basis (AP4b, commit `7fb8e66`, `gate_power_ap4b.md`)

| | S | L | **L + T3** |
|---|---|---|---|
| False-gate rate (simulated, 1,000 null replicates) | 0.153 | 0.007 | **0.009** [0.005, 0.017] |
| Expected for the gate with 10,000 simulations | ≈ 0.15 | ≈ 0.011 | **≈ 0.013** |
| Sought signal (glacier µ × 1.5) triggers the gate | not distinguishable from null | 0.01 | **0.01** |
| Completeness jump Mc + 0.3 | 1.00 | 0.34 | **1.00** |
| Stronger clustering at the same rate | 0.85 | 0.68 | 0.68 |
| Wrong Omori exponent p = 1.2 | 0.96 | 0.19 | 0.19 |

Main reason: L + T3 detects completeness problems in every simulated case instead of 34 %, at a
cost of about 0.002–0.004 more false gates. The sought signal does not trigger it.

## What this does and does not do

- This document records the **choice of variant**. It is **not yet the frozen A8 addendum**.
- **Still needed for the freeze, before 2027-01-01:**
  - the final A8 text with L + T3;
  - the frozen b-values (`results/adequacy/b_value/`, SHA in `frozen.py`) and the method for T3's
    reference period;
  - a code tag of `etas_adequacy`;
  - a dated addendum JSON with SHA-256 values, following the pattern of
    `frozen_v02_addendum_2026-10-10.json`.

  Johann decides that freeze separately.
- Known limitation, carried into A8: with B = 399 the AP4b T2 level was 0.0025. The gate itself
  must use the 10,000 simulations stated in the draft.
