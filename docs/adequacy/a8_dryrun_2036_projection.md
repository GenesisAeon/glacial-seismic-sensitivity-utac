# A8 dry run, projected 2036 look (10-year window, streaming code path)

**FUNCTIONAL TEST ONLY, synthetic window. Not a C2 result; says nothing about C2 or the glacier
hypothesis.** Purpose: **measure** (not estimate) memory and runtime of the A8 gate L + T3 for the
look ending 2036-12-31, with the streaming code path on main (`forecast.iter_window` /
`simulate_counts`, streamed `stats.ogata_ks_bootstrap`, commit `4a1e8c9`). Run on 2026-10-23 on the
box (Linux, 8 cores, 15 GB RAM, 1 process), script `scripts/a8_dryrun_2036_projection.py`, raw
output `results/adequacy/a8_dryrun/dryrun_2036_projection.json`.

## Set-up

| | Choice |
|---|---|
| Window | 10 years, the length of [2027-01-01, 2037-01-01) |
| History (triggers only) | real 2025 events from the frozen snapshot (stand-in for 2026; contains the 2025-12-06 M6.8 sequence, so the glacier case is a stress case) |
| "Observed" window | one synthetic catalogue per region from the frozen model (µ mixture, frozen b, dm 0.1). No 2026+ data read. |
| T3 reference | the A8 sample: all real events ≥ 2.1, 2016–2025 (5,442 / 2,098) |
| T1 | 10,000 simulations (control) |
| T2 | control B = 10,000; **glacier B = 500** (see runtime) |
| Seed | 20261023, dry-run seed only (not the A8 seed) |
| Memory method | `tracemalloc` peak (Python + NumPy heap) over the whole run, and `resource.getrusage(...).ru_maxrss` (process peak RSS, includes tracemalloc's own overhead). `/usr/bin/time` is not installed on the box. |

## Measured memory and runtime

| | Value |
|---|---|
| Window events (synthetic) | glacier 7,581 (+ 2,608 history), control 2,726 (+ 287) |
| **Peak memory, tracemalloc** | **2,079 MB** (reached in the glacier region) |
| **Peak RSS** | **2,241 MB** |
| T1 control (10,000 sims) | 33 s |
| T2 control (B = 10,000) | 1,955 s (33 min) |
| T2 glacier (B = 500) | 893 s, i.e. ~1.8 s per bootstrap catalogue with tracemalloc, 1.66 s without (measured on 20 catalogues) |
| Total | 2,880 s (48 min) |
| **Extrapolated** glacier T2 with B = 10,000 | ≈ 4.6 h (1.66 s × 10,000); not measured |

**What drives memory.** Streaming works: catalogues are no longer kept, and memory does not grow
with the number of simulations (only the D_b array, 80 kB at B = 10,000). The peak now comes from
**one** catalogue: the Ogata KS builds all event pairs within tmax = 1 yr (`etas_nonstat.pairs`).
For the synthetic glacier window plus history these are 20.7 million pairs; a single KS on it
needs 966 MB (tracemalloc). The 2.08 GB peak is the largest bootstrap catalogue among the 500.

**Caveat.** The peak depends on the largest catalogue drawn, and pair count grows roughly with the
square of the event count. With B = 10,000 in the glacier region, larger catalogues are likely
(T1 control: median 2,582, maximum 6,740 of 10,000), so the true peak at the 2036 look can be
higher than 2.1 GB. It was not measured with B = 10,000 because of the 4.6 h runtime. A machine
with ≥ 8 GB free RAM is recommended for the real evaluation.

## Outcome (functional only)

| Region | T1 p | T2 p | T3 p (raw) | T3 p (post-check) |
|---|---:|---:|---:|---:|
| SE_Alaska_AK | – | 0.956 (B = 500) | 2.9e-32 | 0.0041 |
| Interior_AK_ctrl | 0.785 | 0.791 | 5.8e-25 | 0.325 |

Raw run: L + T3 **triggered** (by T3_ctrl). After the post-check: L + T3 **not triggered**, L not
triggered, S triggered (glacier T3 at 0.0041; under A8 a qualification only).

## Finding: float representation of binned magnitudes

The raw T3 p-values are an artefact. `catalog.prepare` bins as `(m / 0.1).round() * 0.1`, which
gives e.g. 2.3000000000000003 (about 35 % of real magnitudes differ from their 6-decimal form),
while the simulator reports `np.round(..., 6)` = 2.3. The two-sample KS then sees two different
values per bin and breaks every tie in the same direction. With the reference rounded to 6
decimals (same seeds, same windows) T3 gives 0.0041 / 0.325; T1 and T2 are unaffected. The script
now rounds the reference; the JSON keeps the raw run and adds the post-check.

**Relevance for A8:** none for the real gate, because window and reference both pass through
`catalog.prepare` and have the same representation (the 2023–2025 dry run gave T3_ctrl = 0.989).
It matters for any check that compares real with simulated magnitudes. A guard (e.g. rounding to
1 decimal inside `m_test_ks2`) would make T3 robust; that is a code change before the code tag and
is left to Claude / Johann.
