# AP4b – documented deviations from the protocol (2026-10-21)

Recorded **while the run was still in progress**, before the remaining scenarios had finished and
before any AP4b results document was written. Protocol: `gate_power_ap4b_protocol.md` (`d71f0a3`).

## D1 – cluster_plus stopped at 11 of 100 replicates (decision: Johann, 2026-10-21)

- **What happened.** Part 1 (07:45–13:21) aborted when one cluster_plus replicate hit the 3 GB job
  memory cap (`ArrayMemoryError`, 601 MiB request for 78.7 million pair indices).
- **Cause.** The frozen `etas_nonstat.mu_window_mle` builds all event pairs within tmax
  (`etas_nonstat.pairs`), so its memory grows quadratically with the catalogue size. At an
  effective branching ratio of 0.95, single bootstrap catalogues need about 3 GB per call. The frozen
  code is not changed.
- **The memory cap worked as intended:** a clean abort with no system freeze, and all 711 replicates
  finished before the abort were saved.
- **Options put to Johann:**
  - (a) the remaining 89 replicates with 1 worker and an 8 GB cap, an estimated 10–17 h;
  - (b) keep cluster_plus at 11 replicates.

  Johann chose **(b)**.
- **Consequence for reporting.** cluster_plus is reported with n = 11 and its Wilson intervals. It
  is not used for any conclusion beyond "T1 reacts to a strongly rising count", which AP4 already
  showed. The question new to AP4b, stronger clustering **at the same rate**, is answered by
  `cluster_plus_same_rate`, which runs in full.
- **Selection effect.** The 11 finished replicates are the ones that completed before the
  aborting replicate. Replicates with very large catalogues are more likely to be the slow or
  failing ones, so the 11 may under-represent the heaviest catalogues. This is stated with the
  result.

## D2 – order of execution (no effect on results)

Part 2 (from 13:22) runs the remaining scenarios without cluster_plus and, per the pre-stated stage
rule, raises null from 500 to 1,000. After 500 null replicates the upper Wilson bound was 0.023
for L and 0.026 for L + T3, both above 0.02. Every replicate's seed depends only on
(seed, scenario index, replicate), not on the order or the worker, so the order does not change any
number. The logs of part 1 are kept as `run_stdout_part1.log` and `run_stderr_part1.log`.

## D3 – summarize fix (no effect on results)

`summarize` divided by zero for scenarios without replicates; fixed in `7e7a37b`.
