# AP6b protocol: bias of the preregistered C2 under a truth calibrated to the 2026 data

Status: protocol, committed **before** the run. Decision: Johann, 2026-10-22, 17:49, via Aeon
(`agent-inbox/an-claude/2026-10-22_Freigabe_AP6b_AP6push_AP8PR.md`). Background: AP6 deviation D1
(`sequence_term_deviation.md`): the term fit is degenerate and the real tail decays much faster
than assumed in AP5.

Code: `etas_adequacy/sequence_term.py` (`run_level_replicate`, `LEVEL_SCENARIOS`), script
`scripts/sequence_level_c2.py`, test `tests/test_sequence_term.py::test_level_replicate_*`.
No new data: the frozen 2016–2025 snapshot and the AP6 2026 snapshot (to 2026-10-22, SHA-checked).

## Calibration (`results/adequacy/sequence_level/calib.json`, written before this commit)

- Real glacier events ≥ Mc from 2026-01-01 to the cutoff 2026-10-22: 1,484.
- **Descriptive spike** (µ + A·x^(−q), no triggering): q = 2.82 ± 0.12, A = 15.6, level
  475 events/yr.
- **Observed rate:** 526 / 446 / 416 events/yr from 2026.25 / 2026.40 / 2026.50 to the cutoff.
- **Frozen model:** mean rate e^(log µ_ref + σ²/2)/(1 − n) = **453 events/yr** (binned n 0.865).
  Median annual count 2016–2024: **285**.
- **Reading:** Late 2026 is at the **mean** of the frozen model (no excess) but about 1.5 times a
  **typical quiet year**. The excess level is therefore bracketed between 0 and about 150/yr.

## Model (per replicate)

- **Glacier catalogue:**
  - the **real** events 2026-01-01 to the cutoff (triggers for C2, as they will be in reality);
  - from the cutoff on, a synthetic truth made of three parts:
    1. the frozen model (20-year warm-up, one mixture µ per year), started from a synthetic
       history, i.e. without frozen-model offspring of the real sequence;
    2. the spike A_s·(t − t_ms)^(−q_s) with the calibrated values, no offspring;
    3. an excess level E(t) = e0·((t − t_ms)/0.5)^(−r) per year, no offspring.

  Magnitudes of parts 2 and 3 are drawn from the sequence magnitude pool.
- **Control region:** the frozen model.
- **C2** exactly as preregistered (`evaluate_pair_with_term(..., fit=None)`, identical to
  `evaluate_pair`), at both looks.

| Scenario | e0 (events/yr at mid-2026) | r | Meaning |
|---|---:|---:|---|
| e0 | 0 | – | calibrated to the frozen mean (no excess) |
| e75_r10 | 75 | 1.0 | half the gap to a quiet year, decaying like 1/t |
| e75_r05 | 75 | 0.5 | same, decaying slowly |
| e150_r10 | 150 | 1.0 | full gap to a quiet year, 1/t |
| e150_r05 | 150 | 0.5 | full gap, slow (stress) |
| signal_e0 | 0 | – | e0 plus glacier background × 1.5 from 2027 (power) |

Run: 400 replicates each, main seed 20261025. A pilot (seed 996, 10 replicates each) is used for
time and memory only. Job object 2,500 MB, half the CPUs, 2 workers, checkpoints.

## Rule (Johann's criterion, stated before the run)

Nominal rejection rates are 0.01 at look 1 and 0.04 at look 2.

- If the rejection rate (point estimate) is **≤ 0.02 at look 1 and ≤ 0.08 at look 2** for **e0,
  e75_r10 and e75_r05**, **no C2 addendum is needed**. The sequence then goes into
  LIMITATIONS.md with the AP5/AP6/AP6b results.
- **e150_r10 and e150_r05** are reported:
  - if they also meet the criterion, the result is unconditional;
  - if not, the result is "no addendum, **provided** the excess stays below about 75/yr". Johann
    then decides whether that suffices or whether a check at the first look (e.g. a 2027 rate
    against the frozen mean) is added.
- Power: signal_e0 is reported and compared with AP5 `none` and AP6 `signal_notail` (not run);
  there is no threshold.

## Expectations (stated before the run)

1. **e0:** rejection at or below nominal. The real late-2026 events act as triggers; given D1
   (the frozen triggering over-explains after large sequences), µ_new tends to be slightly
   **low** early in 2027, so C2 is conservative.
2. **e75:** a small positive D, with rejection probably within the criterion. The excess of about
   75/yr in 2027, against a background of about 57/yr, is partly explained as triggered.
3. **e150_r05:** a clear positive bias; may exceed the criterion at look 2 (long, slow excess).
4. **Ordering:** bias grows with e0 and is larger for r = 0.5 than for r = 1.0.

## Limitations

- The truth from the cutoff on contains no frozen offspring of the real sequence. Its remaining
  activity is represented only by the spike and E(t).
- Real data end on 2026-10-21; November and December 2026 are synthetic.
- The level shape is a power law with r ∈ {0.5, 1}.
- Control-region 2026 data are not used (model truth).
