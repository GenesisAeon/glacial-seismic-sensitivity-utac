# AP6b results: bias of the preregistered C2 under a truth calibrated to the 2026 data

Protocol `sequence_level_protocol.md` (`0094832`). Run 2026-10-22: 6 scenarios × 400 replicates,
seed 20261025, 31.9 min, peak 1,207 MB. Raw data: `results/adequacy/sequence_level/main_20261022/`;
pilot (seed 996, time only): `.../pilot/`. Real glacier events 2026-01-01..2026-10-21 serve as
triggers; everything later is synthetic.

## Result

| Scenario | Excess level events 2027–29 | D (look 1) | C2 rejects, look 1 (α 0.01) | D (look 2) | C2 rejects, look 2 (α 0.04) | Rejects at either look |
|---|---:|---:|---|---:|---|---|
| e0 (no excess) | 0 | −0.004 | 0.005 [0.001, 0.018] | −0.001 | 0.018 [0.009, 0.036] | 0.020 [0.010, 0.039] |
| e75_r10 | 50 | +0.137 | 0.018 [0.009, 0.036] | +0.087 | 0.060 [0.041, 0.088] | 0.070 [0.049, 0.099] |
| **e75_r05** | 105 | +0.244 | **0.028** [0.015, 0.049] | +0.189 | **0.138** [0.107, 0.175] | 0.158 [0.125, 0.196] |
| e150_r10 | 100 | +0.222 | 0.030 [0.017, 0.052] | +0.121 | 0.062 [0.043, 0.091] | 0.085 [0.061, 0.116] |
| e150_r05 | 208 | +0.474 | 0.170 [0.136, 0.210] | +0.342 | 0.500 [0.451, 0.549] | 0.542 [0.494, 0.591] |
| signal_e0 (µ × 1.5 from 2027) | 0 | +0.430 | 0.155 [0.123, 0.194] | +0.417 | 0.675 [0.628, 0.719] | 0.685 [0.638, 0.729] |

## Rule (stated before the run)

Criterion: ≤ 0.02 at look 1 and ≤ 0.08 at look 2, for e0, e75_r10 and e75_r05.

| Scenario | Look 1 | Look 2 | Meets the criterion? |
|---|---:|---:|---|
| e0 | 0.005 | 0.018 | ✔ |
| e75_r10 | 0.018 | 0.060 | ✔ |
| e75_r05 | **0.028** | **0.138** | ✘ |

**The criterion is not met.** The reason is a single scenario: an excess of 75 events/yr at
mid-2026 that decays slowly (r = 0.5). Without excess, or with an excess that decays like 1/t, C2
stays within twice nominal.

## Against the expectations

1. **e0:** the expectation was rejection at or below nominal, possibly conservative.
   - Result: 0.005 / 0.018, mean D ≈ 0. **Confirmed.** C2 is at nominal or below.
   - The real 2026 triggers do not make it noticeably conservative; D is −0.004, not clearly
     negative.
2. **e75:** the expectation was a small positive D, probably within the criterion.
   - For r = 1.0 it is within the criterion.
   - For r = 0.5 it is not (0.028 / 0.138). **Partly refuted.**
3. **e150_r05:** the expectation was a clear bias. **Confirmed:** 0.17 / 0.50.
4. **Ordering:** **confirmed.** The bias grows with e0 and is larger for r = 0.5.

## What this means

- A slowly decaying excess of about 100–200 events in 2027–2029 produces a D of the same size as
  the sought signal (e150_r05 +0.47 against signal +0.43). **C2 cannot tell them apart.** That is
  the residual risk from the 2025 sequence.
- Whether such an excess exists cannot be decided from 2026 data:
  - late 2026 runs at about 416–446/yr;
  - that is the mean of the frozen model (453/yr), which fits e0;
  - it is also about 1.5 times a quiet year (median 285), which fits e75–e150.
- Compared with AP5 (72 % false rejections at look 1 under p = 1.1), the risk is much smaller.
  It is not zero.

## Options (for Johann; I do not choose)

1. **Robustness check without the epicentral zone, frozen before 2027.**
   - Compute a second baseline (µ_ref, σ_y from 2016–2025) for the glacier region without a
     radius around the 2025 epicentre (and the 2017 one?).
   - Pre-register: a C2 rejection only counts as confirmed if it also shows outside that zone.
   - If the signal is glacier-driven, it should not sit only around the epicentre.
   - This needs a new freeze of these baselines before 2027-01-01.
2. **Limitation only.** No addendum; C2 is reported with a note that a slowly decaying sequence
   excess (AP6b e75_r05 / e150) can mimic the signal. That is honest but weakens any rejection.
3. **Refit in December** with data to mid-December 2026: a better estimate of the late-2026 level.
   It does not decide the question by itself, because e0 and e75–150 differ only by ~10–30 % in
   rate.

My recommendation: option 1. It makes a rejection interpretable without touching the frozen C2
statistic. Option 3 can be added.

## Limitations

As in the protocol. In particular, the truth after the cutoff contains no frozen offspring of the
real sequence, so the remaining sequence activity is only the spike plus E(t). The level shape is
a power law with r ∈ {0.5, 1}.
