# AP6c results (run 2): C2 robustness check without the epicentral zone

Protocol `5c1ecb1`, amendment 1 `203a665` (separate inside/outside processes after deviation D1 of
run 1, `sequence_zone_run1.md`). Run 2 on 2026-10-22: 7 × 400 replicates, seed 20261027. Raw data
in `results/adequacy/sequence_zone/run2_20261022/`.

## Result

The joint false-alarm rate is the share of replicates in which C2 rejects **and** the reduced
statistic (glacier region without a 55 km disc around the 2025 epicentre) confirms (look 1 /
look 2). The criterion is ≤ 0.02 / ≤ 0.08.

| Scenario | Full C2 alone | Confirmed with **A** (p_red < α) | Confirmed with B (p_red < 0.05) |
|---|---|---|---|
| e0 | 0.007 / 0.028 | **0.007 / 0.018** | 0.007 / 0.025 |
| e75_r05_l05 | 0.037 / 0.138 | **0.007 / 0.018** | 0.037 / 0.022 |
| e150_r05_l05 | 0.147 / 0.465 | **0.007 / 0.007** | 0.048 / 0.020 |
| e75_r05_l30 (stress) | 0.033 / 0.147 | 0.015 / 0.033 | 0.033 / 0.048 |
| e150_r05_l30 (stress) | 0.172 / 0.497 | 0.037 / 0.095 | 0.147 / 0.110 |
| **Power** signal_e0 (µ × 1.5) | 0.145 / 0.695 | **0.130 / 0.677** | 0.145 / 0.693 |
| Power signal + e150_r05_l05 | 0.610 / 0.990 | 0.135 / 0.660 | 0.395 / 0.700 |

## Rule

- **B** fails at look 1 for e75_r05_l05 (0.037 > 0.02).
- **A** meets the criterion in all three rule scenarios, with a largest value of 0.018. **A is
  proposed.**

**Proposed for the C2 addendum (Johann decides):**
- A rejection of the preregistered C2 at a look counts as **confirmed** only if the reduced
  statistic also has a one-sided p < α of that look (0.01 / 0.04).
- The reduced statistic uses the glacier region without a 55 km disc around 60.3503° N, 139.3591° W
  and the baseline log µ_ref 3.998, σ_y 0.389.

What it costs and what it buys:
- **Power cost** without an excess: small, 0.145 → 0.130 at look 1 and 0.695 → 0.677 at look 2.
- **Protection:** a slowly decaying sequence excess of 75–150/yr no longer produces confirmed
  false rejections (0.007–0.018 instead of up to 0.47).

## Against the expectations

1. **e0:** joint rate at or below nominal. **Confirmed.**
2. **l05:** most of the excess is removed. **Confirmed**, more clearly with A than with B.
   - The expectation said "B near or below twice nominal". It holds at look 2 but not at look 1.
3. **l30, e150:** exceeds at look 2 (A 0.095). **Confirmed** (stress test).
4. **Power:** "with B close to the full C2, with A clearly lower".
   - B confirmed.
   - A is **not** clearly lower (−0.015 / −0.018). The expectation was too pessimistic.

## Remaining points (honest)

- **Small upward offset of the reduced statistic without excess:** e0 D_red = +0.061 at look 1
  (about 4 SE of the mean), +0.027 at look 2. The cause was not examined. Candidates are the real
  2026 events outside the zone as triggers, and the different σ_y.
  - It does not affect the rule (A 0.007 / 0.018).
- **Leak 30 % (stress):** if a large share of the excess lay outside 55 km, the protection would
  be incomplete (A 0.037 / 0.095). The radius rule (95 % of the sequence inside) makes this
  unlikely.
- **Simplifications:** no triggering across the zone border, a uniform signal in space, and a
  disc instead of the real rupture geometry.

## Run 1 for comparison

The biased run 1 (`sequence_zone_run1.md`) gives worse values for the same scenarios (A e150_l05
look 1: 0.030). The difference is consistent with the diagnosed artefact.
