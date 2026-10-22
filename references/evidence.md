# Evidence checklist

Use only the sections needed for the current task. Missing evidence changes the
claim or next action; it is not an invitation to launch unrelated collection.

## Give the agent useful visibility

- Source: actual hot function plus its callers and relevant invariants.
- Workload: fixture, input size, concurrency, cache state and metric boundary.
- Profile: real path, time, sampled event, symbols, non-empty artifact and
  capability status. Separate on-CPU evidence from off-CPU wait attribution;
  ordinary on-CPU samples do not explain where blocked time was spent.
- Assembly: from the actual built binary/hot symbol, with compiler version,
  flags, LTO/PGO status and binary identity. Generic compiler-explorer examples
  or unrelated builds are hypotheses, not evidence of the deployed instruction.
- CPU: model/core type, ISA support, VM/container status and pinning where known.
  CPU-specific false dependencies must be checked for that microarchitecture;
  seeing POPCNT or a dependency chain alone does not establish a bottleneck.
- Benchmark: paired raw observations and correctness checks, separately from
  instrumented profiling. Missing hardware counters are unknown, not zero misses.

## Form hypotheses from evidence

Enter from either end. Source entry reads the hot function, its invariants and
callers first. Profile entry starts from samples or wait attribution and walks
back to source. Either way, each candidate hypothesis states three things:

1. Applicability premise - which call pattern, data shape, allocation path or
   CPU this change actually hits.
2. Semantics at risk - what behavior, order, boundary or resource ownership
   could change.
3. Verification - the correctness check and the measurement that would confirm
   or refute it.

Prefer removable work, algorithmic/data-layout costs and waits supported by
evidence. Drill into spills, port pressure or instruction-specific quirks only
when the hotspot and the target CPU justify it. Read CPU/architecture-specific
anti-pattern references on demand when the evidence actually points there -
never as a full manual sweep before looking at data. This is a preference, not
a fixed sequence that forces every task to run every profiler.

## Candidate record

Record project/commit, actual patch hash, target/workload/build identity, hypothesis,
allowed changes, generation provenance if applicable, metric contract, policy
source/version, ordered arm plan, correctness result, raw samples, actual costs,
deviations and output paths. Preserve unknown historical compiler/model values.

Moving initialization, caching or cleanup outside the window needs a total-work
accounting. Batch elapsed is not request p99. A change in CPU usage with flat wall
time is a resource result, not automatically a latency win.

Keep all known rows and their provenance. Same patch across sessions is a repeat
measurement, not a new optimization discovery. Missing files do not silently
shrink denominators. Check original sample order and units, including numeric
strings and any recorded normalization; do not overwrite raw evidence.

## Interpreting uncertainty

- REAL means a code modification, not certified beneficial performance.
- Constructed-null provenance and an indeterminate measurement label can coexist;
  describe what the construction certificate actually covers.
- A wide interval is evidence of limited resolution in that observation, not a
  universal detection floor. Cross-session estimate differences are observations,
  not automatically a causal environmental effect.
- Record independent reference/replication cost separately from decision cost.
- Do not import a fixed 0.5% threshold, significance level or CI recipe from a
  paper package into another project's policy without a documented choice.
- Hash equality establishes the specified content relation, not prior freezing,
  trustworthy execution, independence, or statistical validity by itself.

## Compact handoff example

"Changed [scoped work]. Correctness [result]; performance [raw decision + current
authority] on [workload/host/observations]. Used [budget]. Unknown: [specific gap].
Patch/evidence: [paths]. Commit/push/PR: [separate states]. Next: [bounded action]."

Use plain Chinese when the user is conversing in Chinese. Do not bury a blocked
generation backend, invalid measurement or missing evidence behind a green test
count. No-new-experiment fixture tests validate tooling, not performance claims.
