# AP6c run 1 (protocol `5c1ecb1`): results and deviation D1

Run 2026-10-22, 7 × 400 replicates, seed 20261026. Raw data in
`results/adequacy/sequence_zone/main_20261022/`.

## Result as run

The joint false-alarm rate is the share of replicates in which C2 rejects **and** the reduced
statistic confirms (look 1 / look 2). The criterion is ≤ 0.02 / ≤ 0.08.

| Scenario | Full C2 alone | Confirmed with A (p_red < α) | Confirmed with B (p_red < 0.05) |
|---|---|---|---|
| e0 | 0.013 / 0.022 | 0.013 / 0.022 | 0.013 / 0.022 |
| e75_r05_l05 | 0.043 / 0.185 | 0.007 / 0.052 | **0.040** / 0.068 |
| e150_r05_l05 | 0.145 / 0.458 | **0.030** / 0.043 | **0.087** / 0.055 |
| e75_r05_l30 (stress) | 0.043 / 0.128 | 0.025 / 0.055 | 0.043 / 0.070 |
| e150_r05_l30 (stress) | 0.158 / 0.520 | 0.028 / 0.128 | 0.138 / 0.152 |
| signal_e0 (power) | 0.152 / 0.647 | 0.152 / 0.645 | 0.152 / 0.647 |
| signal_e150_r05_l05 | 0.570 / 0.993 | 0.158 / 0.725 | 0.455 / 0.775 |

**By the pre-stated rule neither level is accepted.**
- B fails at look 1 for e75 and e150 (l05).
- A fails only at look 1 for e150_r05_l05 (0.030 > 0.02; Wilson interval 0.017–0.052).
- In every scenario the confirmation removes most of the excess-driven rejections. Without an
  excess, the power is unchanged.

## Deviation D1: a simulation artefact biases the reduced statistic upward

In scenario e0 (no excess) the reduced statistic should be centred near 0. It averages
**D_red = +0.096** (look 1), against D_full = +0.022. The cause is in my simulation, not in the
method:
- Zone labels of synthetic frozen-model events are drawn **independently** (protocol, limitations).
- With a branching ratio n = 0.865 most events are triggered. Removing a random 4.7 % of all
  events (the zone) leaves about 4 % of the remaining events without their parent. The estimator
  then counts them as background.
- The upper bound of the resulting bias is log(1 + π·n/(1 − n)) = 0.27; observed is +0.10.

In reality aftershocks lie near their parents, so zone membership is clustered and this artefact
does not arise in that form. The joint false-alarm rates above are therefore **pessimistic**. How
pessimistic cannot be said without a corrected simulation.

**Correction (run 2, separate protocol amendment before the run):** two separate frozen-model
processes, one outside and one inside the zone. Background rates are µ_red and µ_full − µ_red,
with a common annual draw z_y, no cross-zone triggering, the same K, α, c, p. Everything else
(rule, scenarios, seeds of the remaining components, criterion) stays as in `5c1ecb1`. Both
runs are reported.
