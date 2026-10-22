# AP5 protocol: bias of C2 from the M6.8 sequence of 2025-12-06 (synthetic)

Status: protocol, committed **before** any run with the main seed. Johann's decision of
2026-10-22 (via the A8 review, `agent-inbox/an-grokaeon/2026-10-22_Claude_Pruefung_A8-rev2_und_Probelauf.md`,
item 1). Code: `etas_adequacy/sequence_tail.py`, script `scripts/sequence_tail_c2.py`, tests
`tests/test_sequence_tail.py`. Data: the frozen snapshots up to 2025-12-31 only. **No 2026 data, no
held-out data.**

## Why

- On 2025-12-06 an M6.8 occurred in the glacier region SE_Alaska_AK (60.35° N, 139.36° W). In the
  25 days to the end of 2025 there were 2,415 events ≥ Mc 2.1 after it. The frozen ETAS
  (K 0.0454, α 1.034) predicts about 44 direct aftershocks ≥ Mc for an M6.8 in that time. It
  underpredicts this sequence by far.
- The C2 window starts on 2027-01-01, 13 months after the mainshock. The mainshock is not a trigger
  in C2: only events of 2026 are, and tmax = 1 yr. Whatever the frozen model does not explain of
  the sequence tail in 2027 and later is therefore assigned to the background µ_neu of the glacier
  region. That is the direction of the sought signal (D > 0).
- Long-term decay seen in the data:
  - The 2017 M6.2/6.3 sequence (radius 50 km, days 2 to end of 2025) has a long-term Omori exponent
    of **p̂ = 1.10** (fit with constant background; `calibration.json`, `analog_2017`).
  - The 2025 sequence on days 2–25 gives p̂ = 0.98.
  - Rate × time of the 2017 sequence stays at about 30–60 events from day 3 to year 6.5.
- The 2025 sequence is about 8–10 times as productive as the one in 2017 (rate × time on days
  2–25: about 620–690 against 60–80).

## Model

Per replicate, synthetic catalogues of both regions:

1. **Frozen part (both regions).** A 20-year warm-up, then one `forecast.simulate_window` per
   calendar year 2026–2036. Each year has its own mixture draw log µ ~ N(log µ_ref, σ_year²), as
   assumed by the σ_year²/T term of C2. The previous year's frozen-model events are the history.
   b-values are the frozen ones (`load_b_values`), dm 0.1, m_max 8.0.
2. **Sequence tail (glacier region only, scenarios p10–p13).**
   - An inhomogeneous Poisson process with rate A·(t − t_ms)^(−p) on 2026-01-01 to 2037-01-01,
     t in decimal years.
   - It represents the whole sequence (all generations). Injected events therefore get **no**
     frozen-model offspring, so nothing is counted twice. They are in the catalogue, so C2 sees
     them as triggers, as with real data.
   - Magnitudes are resampled from the observed sequence magnitudes of days 2–25 (mean 2.35;
     `calibration.json`).
3. **C2** exactly as preregistered:
   - `confirmatory_v02.evaluate_pair` on events from 2026-01-01 on, at the looks 2029-12-31
     (α 0.01) and 2036-12-31 (α 0.04);
   - frozen baselines; control region without a tail.

### Calibration (`results/adequacy/sequence_tail/calibration.json`, written by `calibrate`)

- Mainshock: 2025-12-06 20:41:51 UTC, M6.8, t_ms = 2025.93113.
- Fit window: day 2 to 2026-01-01. Completeness at Mc 2.1 from about day 2: the mean magnitude
  ≥ 2.1 falls from 3.6 to 2.4 over days 0–2 and is stable afterwards. n = 1,564 events.
- For each p, A is the profile MLE on that window: A = n / ∫ x^(−p) dx.

| Scenario | p | expected injected events 2026 | 2027–2029 (look 1) | 2027–2036 (look 2) |
|---|---|---:|---:|---:|
| none | – | 0 | 0 | 0 |
| p10 | 1.0 | 1,694 | 826 | 1,444 |
| **p11 (central, 2017 analog)** | 1.1 | 1,302 | **516** | **860** |
| p12 | 1.2 | 1,002 | 322 | 512 |
| p13 | 1.3 | 771 | 200 | 305 |

Hand check H1 (done before the script, with the same formula): p 1.0 → 826, p 1.1 → 517,
p 1.2 → 322, p 1.3 → 200 for look 1. `calibrate` reproduces these values.

## Hand-derived checks (tests)

- H1: ∫ x^(−p) agrees with quadrature; ∫₁^e x⁻¹ = 1 and ∫₁² x⁻² = 1/2.
- H2: the inverse transform has the right medians: the geometric mean √(lo·hi) for p = 1, the
  harmonic mean for p = 2.
- H3: an injected count with rate 100·x⁻¹ on [1, e) has mean 100 (400 draws, within 3 SE). Times
  lie in the interval, magnitudes come only from the pool, and the guard holds (MAX_INJECTED).
- H4: the `none` scenario injects nothing and is reproducible. With identical seeds, p11 changes
  only the glacier region, and its window count grows by exactly the injected events.

## Run

- Scenarios none, p10, p11, p12, p13; **400 replicates each** (Wilson 95 % interval of a rate near
  0.5 is ± 0.05).
- Main seed 20261023, seeds per (seed, scenario index, rep).
- Resource limits as in AP4:
  - a job object with 2,500 MB;
  - half of the logical CPUs, 2 workers, below-normal priority;
  - JSONL checkpoints after every replicate, so the run can be resumed.
- First a **pilot** with its own seed (998, 10 replicates each), for time and memory only. If the
  projection exceeds 3 hours, the number of replicates is reduced to 200 and this is recorded as a
  deviation.

## Metrics

For each scenario and look:
- the mean of D, z, Δlog µ glacier, Δlog µ control;
- the mean number of injected events in the window;
- the rejection rate of C2 with its Wilson 95 % interval;
- the rejection rate at either look ("reject either").

## Expectations (stated before the run)

1. **none** (size of C2 under the frozen model):
   - rejection ≈ 0.01 (look 1) and ≈ 0.04 (look 2);
   - mean D between 0 and about +0.05: µ_neu over several years of lognormal µ_y estimates the log
     of the mean, µ_ref is the mean of the logs (Jensen; σ²/2 = 0.064 glacier, 0.012 control).
   - A clear deviation is a finding about C2 itself and will be reported as such.
2. **p11** (central):
   - The background of the glacier region is about e^4.05 ≈ 57 events/yr, so about 170 in look 1.
     The tail adds about 516 events.
   - If most of them are assigned to the background, Δlog µ_glac ≈ log(1 + 516/180) ≈ 1.3 and z
     is well above the critical value. If the frozen triggering explains a large part, the bias is
     smaller.
   - **Expectation:** clearly positive D at look 1 and a rejection rate well above 0.01, most
     likely above 0.3. The size is uncertain because of that share.
3. **Ordering:** the bias and the rejection rate fall from p10 to p13. At look 2 the bias is
   smaller than at look 1 relative to the background (longer window, tail decays), but not zero.

## Decision rule (for reporting, the decision stays Johann's)

- If the rejection rate under **p11** at look 1 exceeds **0.05** (5 × nominal), C2 as frozen is
  **not interpretable at look 1** without handling the sequence. In that case I report options,
  without choosing:
  - model the sequence explicitly as an additional Omori term in µ_neu;
  - exclude events within a radius around the epicentre;
  - drop look 1 or move it later;
  - require control-region and glacier-region consistency checks.

  Any change to C2 is a separate addendum, not part of A8.
- If it is ≤ 0.05 even under p10, the sequence is reported as a limitation only.

## Not covered (limitations stated in advance)

- Spatial structure: the C2 statistic is regional, so space does not enter. The exclusion-radius
  option would need its own check.
- 2026 data: they would show the real decay over 10 months, but they are not used here. That
  needs Johann's decision; C2 uses 2026 as trigger history only.
- Large aftershocks (M ≥ 6) in the tail with their own sequences, and changes of completeness
  after 2025, are not modelled.
- The tail parameters come from 23 days of data plus one analog. p is therefore varied, not
  estimated.
