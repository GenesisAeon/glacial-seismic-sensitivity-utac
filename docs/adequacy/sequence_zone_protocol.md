# AP6c protocol: C2 robustness check without the epicentral zone

Status: protocol, committed **before** the run. Decision: Johann, 2026-10-22, in chat ("Ja,
Option 1"), after AP6b (`sequence_level.md`).

Code:
- module `etas_adequacy/zone_check.py`;
- script `scripts/sequence_zone_c2.py`;
- tests `tests/test_zone_check.py`.

Calibration: `results/adequacy/sequence_zone/zone.json`, written before this commit from the frozen
2016–2025 snapshot and the AP6 2026 snapshot. No new data.

## What would be frozen (if accepted)

- **Zone:** a disc of radius **R = 55 km** around the 2025-12-06 M6.8 epicentre (60.3503° N,
  139.3591° W).
  - Rule: the 95 % quantile of the epicentral distances of the sequence events ≥ Mc from day 2
    to the end of 2025 (51.4 km), rounded up to the next 5 km.
  - The zone holds 4.1 % of the events of 2016 to November 2025 and 81 % of the 2026 events to
    the cutoff.
  - The 2017 epicentre is 159 km away and is not excluded.
- **Reduced baseline**, relative to the frozen one: log µ_ref,red = **3.998** (full 4.047),
  σ_y,red = **0.389** (full 0.358).
  - Both regions are computed with the same yearly method (`yearly_log_mu`).
  - Only the difference of the means and the ratio of the SDs are transferred, because the
    frozen baseline comes from smoothed fits with a longer history.
- **Reduced statistic:** C2 exactly as preregistered, with the glacier region without the zone and
  the reduced baseline. The control region is unchanged.
- **Confirmation rule:** a rejection of the preregistered C2 at a look counts as **confirmed** only
  if the reduced statistic also has a one-sided p below the confirmation level (section 4).
- The preregistered C2 statistic and its α stay unchanged.

## Simulation

The truth is as in AP6b:
- the real 2026 events with their **real zone label**;
- the frozen model from the cutoff on;
- a spike, and an excess level E(t) = e0·((t − t_ms)/0.5)^(−r).

Zone labels of the synthetic events:
- Frozen-model events are in the zone with probability π = 1 − exp(log µ_ref,red − log µ_ref,full)
  = 0.047, so the thinned background matches the reduced baseline.
- Spike and excess events are in the zone with probability 1 − leak.
- The signal (µ × 1.5 from 2027) acts uniformly over the region.

| Scenario | e0 | r | leak | Signal |
|---|---:|---:|---:|---|
| e0 | 0 | – | – | – |
| e75_r05_l05 | 75 | 0.5 | 0.05 | – |
| e75_r05_l30 | 75 | 0.5 | 0.30 | – |
| e150_r05_l05 | 150 | 0.5 | 0.05 | – |
| e150_r05_l30 | 150 | 0.5 | 0.30 | – |
| signal_e0 | 0 | – | – | × 1.5 |
| signal_e150_r05_l05 | 150 | 0.5 | 0.05 | × 1.5 |

Leak 0.05 corresponds to the radius rule (95 % of the sequence inside). Leak 0.30 is a stress
test. Run: 400 replicates each, seed 20261026 (pilot seed 995, time only), job object 2,500 MB,
half the CPUs, 2 workers, checkpoints.

## Rule (stated before the run)

**Joint false-alarm rate** = the share of replicates in which C2 rejects **and** the reduced
statistic confirms. Nominal is 0.01 at look 1 and 0.04 at look 2. The criterion is twice nominal:
**≤ 0.02 / ≤ 0.08**, for **e0, e75_r05_l05 and e150_r05_l05**.

There are two candidate confirmation levels:
- **B:** p_red < 0.05;
- **A:** p_red < α of the look (0.01 / 0.04).

The levels are chosen in this order:
1. If B meets the criterion, **B** is proposed (more power).
2. Otherwise A, if A meets it.
3. Otherwise neither; I report, and Johann decides.

The l30 scenarios are a stress test and are reported. Power is reported with the confirmation
rule (signal_e0, signal_e150_r05_l05); there is no threshold for it.

## Expectations

1. **e0:** joint rate ≤ nominal.
2. **l05 scenarios:** most of the excess is removed; the joint rate with B is near or below twice
   nominal.
3. **l30:** with e150 the joint rate may exceed the criterion at look 2.
4. **Power:** with B close to that of the full C2 (the reduced region holds ~95 % of the
   background); with A clearly lower.

## Limitations

- Zone labels of synthetic events are independent draws, so parent–child pairs are split at
  random across the zone border.
- The signal is assumed uniform in space.
- The zone is a disc around the mainshock epicentre, not the actual rupture geometry.

## Amendment 1 (2026-10-22, after run 1, before run 2): generator "separate"

Reason: deviation D1 (`sequence_zone_run1.md`). Independent zone labels orphan triggered events,
which biases the reduced statistic upward (e0: D_red +0.096 instead of ≈ 0).

Run 2 uses `run_zone_replicate(..., generator="separate")`:
- **Two frozen-model processes**, outside the zone (background µ_red = e^3.998) and inside it
  (µ_full − µ_red), each with the frozen K, α, c, p.
- A common annual draw z_y; µ_y = exp(log µ + σ_y,full·z_y), × 1.5 from 2027 in the signal
  scenarios.
- No triggering across the zone border.

Everything else is **unchanged**: scenarios, criterion, the order of the B → A choice, the real
2026 events with their real labels, spike and excess (leak). Run 2 uses its own seed
**20261027** (pilot 994) so it is not a re-draw of run 1. Both runs are reported. The decision
rule is applied to **run 2**, because run 1 is known to be biased. If run 2 fails as well, the
result stands as such.

Check before the run: run-1 replicates still reproduce bit-identically with
`generator="labels"` (checked for e0 rep 5 and e150_r05_l05 rep 5).
