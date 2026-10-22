# AP6 protocol: C2 with a frozen Omori term for the 2025-12-06 sequence

Status: protocol, committed **before** any 2026 data are downloaded or looked at.

Decision: Johann Römer, 2026-10-22, in chat: options 2 + 1 of `sequence_tail.md` together. The
sequence is modelled as an extra Omori term in C2, and that term is fitted on 2026 data.

Code:
- module `etas_adequacy/sequence_term.py`;
- script `scripts/sequence_term_c2.py`;
- tests `tests/test_sequence_term.py`.

Previous work: AP5 (`sequence_tail.md`, PR #6). Without handling, C2 rejects in 72 % of
replicates at look 1 under p = 1.1.

## 1. What gets frozen (the C2 addendum, if accepted)

The glacier-region intensity in C2 becomes

    λ(t) = µ_new + Σ_j g_j(t) + S(t),     S(t) = A · (t − t_ms)^(−q),   t in decimal years,

with these parts:
- g is the frozen ETAS triggering, unchanged;
- t_ms = 2025.93113 (2025-12-06 20:41:51 UTC, M6.8);
- (A, q) are fitted once (sections 2–3) and then frozen;
- the control region is unchanged.

µ_new is the MLE of `mu_mle_with_term` (it equals `mu_window_mle` for S = 0). D, SE, looks and α
stay as preregistered. There are two SE variants:
- **A:** the preregistered SE, with the uncertainty of the S fit ignored;
- **B:** the preregistered variance plus the delta-method variance of log µ_new from the
  covariance of (log A, q).

Section 5 decides which variant is used.

## 2. Data (to be downloaded only after this commit)

- ComCat, catalog = ak, with exactly the query of `fetch.catalogs.fetch_comcat`, for the
  **SE_Alaska_AK region only**, from **2026-01-01 up to and excluding 2026-10-22 00:00 UTC**
  (CUTOFF), in monthly chunks.
- The script aborts if any event lies outside that range. No control-region data and nothing
  from 2027 on are requested.
- The snapshot is stored gzip-compressed with mtime 0, together with its SHA-256 values and the
  query list (`results/adequacy/sequence_term/snapshot_2026.json`).
- Triggers from 2025 (including the December sequence) come from the frozen 2016–2025 snapshot.
  Preparation is `catalog.prepare` with the region definition, then the cut M ≥ Mc_ref 2.1
  (tolerance 1e-9).

Note on looking at the data: 2026 data come after the baseline freeze (data up to 2025). C2
uses 2026 only as trigger history; the test window starts 2027-01-01. The fit uses the counts and
times of 2026 events. It does not use any C2 statistic.

## 3. Fit (once, on the real data)

- Maximum likelihood on [2026.0, CUTOFF) for (log µ_2026, log A, q). µ_2026 is a nuisance
  parameter.
- The frozen triggering comes from events within tmax = 1 yr before each event.
- The likelihood is Σ log λ(t_i) − µ·T − A·∫S. The triggered compensator does not depend on the
  parameters.
- Bounds q ∈ [0.2, 3]; starting values q ∈ {0.8, 1.1, 1.5}, keeping the best.
- Covariance from the numerical Hessian.
- Output: `term_fit.json` (A, q, covariance, n, expected term events 2027–2029 and 2027–2036).

## 4. Simulation of the residual bias

Per replicate:
1. Frozen-model catalogues of both regions, 2025–2036, one mixture draw of µ per year, after a
   20-year warm-up.
2. A true sequence tail in the glacier region from 2026, as an inhomogeneous Poisson process
   A_true·(t − t_ms)^(−q_true) without frozen offspring (as in AP5). Magnitudes come from the
   observed sequence magnitudes of days 2–25.
   - q_true = q̂ + dq;
   - A_true matched so the expected tail count in the fit window equals that of the real fit
     (same 2026 count, different decay).
3. The real December 2025 sequence events are added as triggers, without offspring.
4. The term is fitted on the synthetic catalogue in [2026.0, CUTOFF) exactly as in section 3.
5. C2 at both looks: without a term ("none", as preregistered), with variant A, and with
   variant B.

Scenarios, 400 replicates each, main seed 20261024 (pilot seed 997, 10 replicates each, time and
memory only):

| Scenario | Truth |
|---|---|
| dq−0.2, dq−0.1, dq0, dq+0.1, dq+0.2 | tail with q_true = q̂ + dq, no change of µ |
| signal_dq0 | tail with q_true = q̂ **and** glacier background × 1.5 from 2027 (the sought signal) |
| signal_notail | no tail, glacier background × 1.5 from 2027: the power of C2 without the sequence, for comparison |

Resource limits as in AP4/AP5: a job object with 2,500 MB, half of the CPUs, 2 workers, JSONL
checkpoints.

## 5. Acceptance rule (stated before the run)

Nominal rejection rates are 0.01 (look 1) and 0.04 (look 2). A variant is **acceptable** if, for
**each** of dq ∈ {−0.1, 0, +0.1}, its rejection rate (point estimate, 400 replicates) is
**≤ 0.02 at look 1 and ≤ 0.08 at look 2** (at most twice nominal).

1. If variant A is acceptable, **A** is proposed: it has the fewest parts beyond the
   preregistration.
2. Otherwise, if B is acceptable, **B** is proposed.
3. Otherwise neither is proposed. I report the result and the remaining options (e.g. only
   look 2, a later window, a stricter α for look 1); Johann decides.

dq ± 0.2 is a stress test and is reported but is not part of the rule. Power (signal_dq0 against
signal_notail) is reported; there is no threshold for it.

## 6. Expectations (stated before the run)

1. **Fit:** q̂ between 1.0 and 1.3 (AP5: 0.98 on days 2–25, 1.10 for the 2017 analog), with an
   SE of q of about 0.03–0.1 from ten months of data.
2. **"none"** (preregistered C2) under dq0: strongly too many rejections, as in AP5. The size
   depends on q̂, roughly 0.3–0.7 at look 1.
3. **Variant A, dq0:** near nominal (≤ 0.02 / ≤ 0.08).
4. **dq−0.1** (true decay slower than fitted): positive residual bias, so variant A rejects too
   often. This is the most likely reason for failing the rule. B partly compensates.
   **dq+0.1:** negative bias, so conservative.
5. **Power:** signal_dq0 with the term below signal_notail (extra uncertainty, short window), but
   clearly above the nominal size.

## 7. Option (Johann's decision after the result)

A refit with data up to 2026-12-15, with the same method and only the cutoff changed, before the
freeze. The extrapolation becomes shorter and p better determined. The simulation result of this
protocol then applies approximately, conservatively.

## 8. Limitations (stated in advance)

- The tail shape is a pure power law. Other shapes (e.g. a decay that steepens) are only covered
  through dq.
- Completeness in 2026 is assumed constant at Mc 2.1. The magnitude pool comes from
  December 2025.
- No spatial structure. The frozen triggering is used unchanged, although AP5 showed that it
  underpredicts large sequences.
- The December 2025 events in the simulation are fixed (real), not redrawn.
