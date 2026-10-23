# AP6 deviation D1: the term fit is degenerate; the AP5 premise does not hold for the real data

Date: 2026-10-22. Protocol `sequence_term_protocol.md` (`f164ce0`).

Data: 2026 snapshot of SE_Alaska_AK, 2026-01-01 to 2026-10-22, 4,240 rows (1,484 events ≥ Mc)
(`results/adequacy/sequence_term/snapshot_2026.json`, SHA-256 of the gz file `69bc800d…`). Fit:
`term_fit.json`. No simulation was run.

## What happened

The fit of section 3 does not give an interpretable term:
- µ_2026 and A end at their lower bounds (e^−10) and q at its lower bound 0.2;
- the covariance is meaningless (SE of q 125).

The reason is not numerical. Given the **observed** events (the December sequence and 2026), the
frozen triggering already predicts **more** events than occurred:

| 2026, ~1-month bins | Observed | Expected triggered (frozen model, given the observed history) |
|---|---:|---:|
| Jan | 831 | 636 |
| Feb | 204 | 245 |
| Mar | 154 | 181 |
| Apr | 48 | 120 |
| May | 70 | 106 |
| Jun | 43 | 84 |
| Jul | 34 | 74 |
| Aug | 28 | 61 |
| Sep | 41 | 62 |
| Oct (to 21st) | 31 | 54 |

So an additional positive term is not identifiable, and the background µ estimated on any 2026
window is 0. The same holds within the first year after the 2017 M6.2/6.3: µ̂ = 0 for windows in
2017. For the window starting 13 months after 2017, log µ̂ = 3.91 against log µ_ref = 4.05, i.e.
**no** inflation.

## What this means for AP5

AP5 extrapolated the tail from days 2–25 with p = 1.0–1.3. Its central scenario put about 516
extra events into 2027–2029.

The 2026 data decay much faster. Described without triggering (µ + A·x^(−q), descriptive only)
they give q ≈ 2.8 ± 0.1 and an extrapolated tail of only about 7 events in 2027–2029. On top of
that comes a level of about 475 events/yr in 2026, against a median of about 285/yr in 2016–2024.
Part of this level is the slow remainder of the sequence. Whether it persists into 2027 cannot be
seen from these data.

AP5's scenarios therefore overstate the tail by far. Its central result (72 % false rejections)
**does not describe the real situation**. AP5 remains correct as a statement about what C2 would
do *if* the tail decayed like 1/t.

## Consequence for the protocol

Section 5 (variant A or B) cannot be applied, because there is no term to freeze. Changing the
plan is Johann's decision. Proposal (not started):

- **AP6b:** the AP5 simulation with a truth calibrated to the 2026 data: the fast spike plus a
  slowly decaying excess level, with the level's decay varied. It measures the bias of the
  **preregistered** C2 (without a term). This gets its own protocol commit before the run.
- If the rejection rate stays ≤ twice nominal, **no C2 addendum is needed**; the sequence goes
  into the limitations. Otherwise the options of `sequence_tail.md` are reconsidered.
