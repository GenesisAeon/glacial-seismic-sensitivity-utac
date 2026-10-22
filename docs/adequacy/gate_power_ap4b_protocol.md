# AP4b protocol: gate size and power with the frozen b, binned n and a 20-year warm-up

Status: **fixed before the run** (committed before any counted AP4b replicate). Exploratory and
synthetic only; no 2026 data; no threshold is derived from real data. Requested by Johann via Aeon
(`agent-inbox/an-claude/2026-10-20_Aeon_P133-AP4-Entscheidungen.md`), items 2–4.

## What changes compared with AP4 (`gate_power_protocol.md`, results `gate_power.md`)

| | AP4 | AP4b |
|---|---|---|
| b-value | assumed 1.0 | **frozen 2016–2025**: SE_Alaska_AK 0.913, Interior_AK_ctrl 0.945 (`load_b_values`, commit `a930c5a`) |
| analytic branching ratio for the scenarios | continuous GR (overstated n, see the correction in `gate_power.md`) | **binned** (`n_dm = 0.1`, matches the simulator) |
| warm-up before the 2025 history | 2 years | **20 years** |
| gate rules evaluated | S, L | S, L, **L + T3** (T3 of the control region at 0.005) |
| seed | 20261019 | **20261020** (fresh replicates) |

Effective branching ratios of the frozen model with the frozen b, binned: SE-Alaska 0.865,
Interior 0.650. Scenarios that change the shape (p12, alpha_half) keep these; cluster_plus and
cluster_plus_same_rate set the effective n to 0.95; same_rate lowers µ so the expected annual
count stays as in the model.

**Rate check before the protocol** (count-only, pilot seed 999, 200 replicates, not counted).
Simulated mean window count divided by the stationary µ e^{σ²/2}/(1 − n), with a 20-year warm-up:

| Scenario | SE_Alaska_AK | Interior_AK_ctrl |
|---|---:|---:|
| null | 0.953 | 1.029 |
| cluster_plus | 0.978 | 1.078 |
| cluster_plus_same_rate | 1.114 | 1.017 |

Each ratio lies within about 2 SE of 1; the model rate is reached (Aeon item 2). With a 2-year
warm-up the n = 0.95 scenarios reached only 0.71–0.90.

L + T3 was suggested after AP4's results had been seen. Its size and power are therefore estimated
here on **fresh** replicates (new seed), not on the AP4 replicates.

## Unchanged from AP4

- Scenarios: null, p12, alpha_half, cluster_plus, cluster_plus_same_rate, swarm_ctrl, swarm_glac,
  mc_jump, signal_glac.
- Definitions of T1/T2/T3, the S and L rules, and the resolution: T1 with 1,000 simulations; T2
  with B = 399 (smallest p 0.0025, so the T2 level in L is 0.0025; reported as in AP4). T3 uses a
  10-year reference sample drawn with the region's frozen b.
- Sizes: null 500, every other scenario 100.
- Resources: 2 worker processes; Windows job object with 4 of 8 logical CPUs, below-normal
  priority. The memory cap is **3 GB** (pilot peak 1.68 GB at a 2 GB cap). Each replicate is
  appended to `<scenario>.jsonl` (resumable).
- Stage rule: null is raised to 1,000 (same command, same seeds) only if the upper 95 % Wilson
  bound of the L **or** the L + T3 false-gate rate exceeds 0.02.

Timing pilot (seed 999, not counted), seconds per replicate: null ≈ 43, mc_jump ≈ 23,
same_rate ≈ 46, cluster_plus ≈ 626 (292–1107). Projection ≈ 16 h in total. Coordination: N4 (neural
lab) finished its main run on 2026-10-20 at 15:05; AP4b does not overlap it.

## Expectations (stated before the run)

- S: false-gate rate below the independence value 0.23, as in AP4 (T3 conservative).
- L: ≈ 0.005–0.01. L + T3: at most ≈ L + 0.005.
- signal_glac: not above the null rates (separation principle).
- mc_jump: L + T3 catches it far more often than L, through T3 of the control region.
- cluster_plus_same_rate: open. AP3 suggests that T1, via overdispersion, and T2 are the
  candidates. It is reported as measured, including "no test fires".

## Reported

`docs/adequacy/gate_power_ap4b.md`, with the same structure as `gate_power.md` and an added L + T3
column; raw data in `results/adequacy/gate_power_ap4b/`.
