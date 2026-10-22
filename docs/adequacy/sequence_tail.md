# AP5 results: bias of C2 from the M6.8 sequence of 2025-12-06 (synthetic)

Protocol `sequence_tail_protocol.md` (`0263aca`), calibration `6bc41db`; run on 2026-10-22,
12:21–12:46. Raw data: `results/adequacy/sequence_tail/main_20261022/` (`<scenario>.jsonl`,
`summary.json`, run metadata). Pilot (seed 998, 10 replicates each, timing only, results not
used): `results/adequacy/sequence_tail/pilot/`. **Synthetic only; data up to 2025-12-31; no 2026
or held-out data.**

## Main result

**With the sequence tail, C2 as preregistered would very likely report a glacier-region increase
that is not there.** Under the central scenario (p = 1.1, the long-term exponent of the 2017
analog), C2 rejects at look 1 in **72 %** of replicates, against a nominal 1 %. It rejects at
either look in 95 %. Even the fastest decay considered (p = 1.3) rejects at look 1 in 9 %.

| Scenario | Reps | Injected 2027–29 | D (look 1) | **C2 rejects, look 1 (α 0.01)** | Injected 2027–36 | D (look 2) | C2 rejects, look 2 (α 0.04) | Rejects at either look |
|---|---:|---:|---:|---|---:|---:|---|---|
| none (frozen model) | 400 | 0 | −0.006 | 0.005 [0.001, 0.018] | 0 | +0.017 | 0.020 [0.010, 0.039] | 0.025 [0.014, 0.045] |
| p10 (p = 1.0) | 400 | 826 | +1.038 | **0.980** [0.961, 0.990] | 1,447 | +0.682 | 0.998 [0.986, 1.000] | 1.000 [0.990, 1.000] |
| **p11 (p = 1.1, central)** | 400 | 517 | **+0.780** | **0.715** [0.669, 0.757] | 859 | +0.469 | 0.853 [0.814, 0.884] | 0.948 [0.921, 0.965] |
| p12 (p = 1.2) | 400 | 322 | +0.568 | **0.268** [0.226, 0.313] | 512 | +0.315 | 0.395 [0.348, 0.444] | 0.495 [0.446, 0.544] |
| p13 (p = 1.3) | 400 | 199 | +0.369 | **0.092** [0.068, 0.125] | 303 | +0.202 | 0.177 [0.143, 0.218] | 0.228 [0.189, 0.271] |

Brackets: Wilson 95 % intervals. D = Δlog µ glacier − Δlog µ control; the control region is
unaffected in all scenarios (mean Δlog µ control between −0.012 and +0.008).

## Against the expectations stated before the run

1. **none (size of C2):** the expectation was a rejection rate ≈ 0.01 / 0.04 and a mean D between
   0 and +0.05.
   - Result: **0.005 / 0.020**. C2 is somewhat **conservative** under the frozen model.
   - Mean D −0.006 / +0.017. The look-1 value is just below the expected range but within the
     Monte Carlo error (SE of the mean 0.015).
   - So C2 itself is sound when the model is right.
2. **p11:** the expectation was a clearly positive D and a rejection rate most likely above 0.3.
   - Result: **D +0.78, rejection 0.715. Confirmed.**
   - The expected upper limit, if every injected event were assigned to the background, was
     Δlog µ ≈ 1.3. Observed is 0.77. Roughly 40 % of the extra events end up in µ_neu; the rest
     the frozen triggering explains through the injected events themselves.
3. **Ordering:** **confirmed.**
   - Bias and rejection rate fall from p10 to p13.
   - At look 2 the bias is smaller (D +0.47 against +0.78 for p11), but the rejection rate is
     higher (0.85 against 0.72). The longer window lowers the SE more than the bias falls, and
     α is 0.04 instead of 0.01.

## Decision rule (protocol)

The rejection rate under p11 at look 1 is **0.715 > 0.05**. By the rule stated before the run,
**C2 as frozen is not interpretable at look 1** without handling the 2025 sequence.
- Look 2 is not a way out either: 0.85 under p11.
- Even under p13 both looks are far above nominal (0.09 / 0.18).

**This is a finding about C2, not about A8.** The A8 gate cannot catch it, because glacier-region
failures are only qualifications (A8.1). The control region is unaffected, so the gate stays
silent. Any change to C2 needs a separate dated addendum before 2027-01-01. That is Johann's
decision.

## Options (for Johann; I do not choose)

1. **Model the sequence explicitly in C2.** Freeze, before 2027-01-01, an additional Omori term
   A·(t − t_ms)^(−p) for the 2025 sequence in the C2 intensity of the glacier region, with A and p
   fixed from data. The residual bias when the true p differs from the frozen one can be measured
   with this same code before freezing.
   - With data to 2025 only, p is poorly determined (23 days).
2. **Use the 2026 data for the tail fit (needs your decision).** Ten months of decay would pin
   down p far better than 23 days. C2 uses 2026 only as trigger history, so a fit on it does not
   touch the test window 2027+. It does mean looking at data after the baseline freeze (up to
   2025), and that should be decided and documented in advance.
   - Option 2 strengthens option 1.
3. **Exclusion radius around the epicentre.** This changes the region and therefore needs new
   baselines (µ_ref, σ_y from 2016–2025 without that area). It is a larger intervention in what is
   frozen.
4. **Later start of the C2 window** (e.g. 2030), or C2 for this cycle declared not evaluable by
   rule.
   - Under p11 the tail still adds about 340 events in 2030–2036, so a later start reduces the
     bias but does not remove it. (Hand value from the calibration: A·∫ over 2030–2037 ≈ 860 −
     517 ≈ 343.)

My recommendation: options 2 + 1 together, with a check of the residual bias using this code,
before 2027-01-01. If that is not feasible in time, option 4 with an honest statement. Johann
decides.

## Limitations (as stated in the protocol)

- The tail is an extrapolation from 23 days plus one analog; p is varied, not estimated.
- No spatial structure, no large aftershocks with their own sequences, no completeness changes
  after 2025.
- The injected events have no frozen-model offspring (the empirical rate already contains all
  generations). If part of the real future tail were itself well described by the frozen
  triggering, the bias would be somewhat smaller. The ordering p10–p13 brackets this.
- Resources: 2,000 replicates in 24.6 min, peak job memory 1,184 MB (cap 2,500 MB).
