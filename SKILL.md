---
name: performance-optimization
description: Diagnose code-performance bottlenecks, develop bounded optimization patches, or evaluate existing patches using the project's performance harness and reproducible evidence. Use for agent-managed performance optimization, profiling-guided C/C++ work, performance-patch evaluation, and the final convergence chart of an optimization line; not general refactoring, financial trading advice, or training a new statistical judge.
---

# Performance optimization

Guide the agent; reuse the harness. This skill does not implement a statistical
judge, certify a universal error bound, or grant permission to publish changes.

## Choose the requested scope

| Request | Work permitted within the request |
|---|---|
| Diagnose / explain a bottleneck | Read source and existing evidence; explain hypotheses. Do not edit target code or launch builds/profiling unless that execution is in scope. |
| Optimize | Establish a bounded experiment, then generate and evaluate a scoped patch. Confirm the patch-generating model before generation. |
| Evaluate an existing patch | Preserve patch identity; use existing evidence or the authorized measurement plan. Do not generate a replacement patch. |

For ambiguous "make it faster" requests, start with read-only discovery and a
concrete plan. Ask only for choices that materially affect scope, budget, or
authority. Do not make the user reapprove each ordinary command in an already
authorized bounded run.

## Choose the diagnostic path

The symptom class selects the first evidence; it is a routing aid, not a
mandatory tool run. Source reading and runtime evidence are complementary.
perf/PMU is one option, never a requirement for every project: projects without
a PMU adapter use their own runtime evidence (logs, counters, traces, service
statistics). A missing capability is recorded and reported, not forced.

| Symptom | First look | Next evidence to obtain |
|---|---|---|
| CPU hot: on-CPU samples concentrate in few symbols | Hot function source, callers, invariants | Sampled profile of the real workload; assembly of the actual built binary with compiler/flags/CPU |
| Waiting / I/O: wall time far above on-CPU time, flat samples | Where the task blocks or polls; the metric boundary | Off-CPU/wait attribution from the project's tracing, events or service statistics |
| Lock contention | Contended lock paths, hold/waiter counts available in runtime tooling | Wait chain and the sharing structure in source |
| Scalability: throughput stops improving with more cores/workers | Sharing, queueing and cross-core traffic in the design | Throughput-vs-resource curve; whether the metric counts parallel work honestly |
| Measurement itself unreliable: noise dominates, counters missing or zero, unstable runs | The harness, configuration, host and recordkeeping | Fix the measurement setup before optimizing code; missing events are unknown, not zero cost |

A read-only diagnosis may use any of the above without launching builds or
profiling; those run only when execution is in scope.

With no runtime evidence yet, the code-reading stage can only list hypotheses
by cost type (work, waits, contention, scale limits). After authorization, the
first measurement is a low-cost discrimination pass - per-stage wall vs CPU
time, wait or lock counts, queue depths - before choosing profiling tools.

### Where to read next

How-to detail lives in the user's blog; this skill only routes to it. Read a
target only when its condition holds, never the whole blog. Paths are relative
to `<blog-root>`, the local clone of
https://github.com/Jasper-aa64/Jasper-aa64.github.io. Headings carry explicit
`{#id}` anchors, so grep the id; English pages are `*.md`, Chinese twins
`*.zh.md`, and the same anchors work on https://jasper-aa64.github.io. The perf
special is `content/posts/low-latency-perf-profiling.md`; the bottleneck
reference is `content/ref/bottlenecks.md`.

| In hand | Read next |
|---|---|
| perf chosen, nothing measured yet | perf special `{#commands}`, `{#before}`; probe counters first (`{#demo-probe}`): `<not supported>` or 0 means unavailable, so sample with `cpu-clock` and use annotate (`{#events}`) |
| Report shows bare addresses | `{#symbols}`: stripped binary, or a path under `/tmp/perf-` that perf before 6.11 reads as a JIT map |
| perf stat output | `{#stat-ratios}` |
| perf report output | `{#report-lines}`; annotate any function with >= 20% of samples, then `{#annotate-scan}` (samples often land one instruction after the slow one) |
| Threads contend, or throughput stops scaling with cores | `{#c2c}`, `{#scaling}` |
| A profile or source signal | `grep -rH "^signal:" --include="*.md" --exclude="*.zh.md" <blog-root>/content/bottlenecks` (one line per card; rendered as `{#lookup}`), then read only the matching card `content/bottlenecks/<id>.md`; if none matches, return to the symptom table above |
| Writing new code | bottleneck reference `{#new-code}`, `{#isa-dispatch}` |
| A long fix such as SIMD widening | the card's `source:` file, plus its `-impl.md` sibling if any, in intel/intel-performance-skills at commit 3e33aec |
| Why a bottleneck costs time | the posts the card links to |
| Patch builds and passes correctness | this skill's sections on the experiment contract, screening and confirmation, and interpretation, plus [the evidence checklist](references/evidence.md) |
| Developer and agent agree the line has converged | [the convergence chart rules](references/convergence.md); render with `scripts/render_convergence_chart.py` |

Once a signal matches a card, read the card before editing; do not fix from
memory. A card's verify items are self-checks; promotion still follows the
contract and fresh confirmation here. New bottlenecks arrive as new card files,
so route through the lookup rather than to individual cards.

## Discover before invoking

1. Identify the target repository separately from the harness repository. Read
   their applicable instructions and current status. Do not clean user changes.
2. Locate the actual runner, evaluator, configuration, correctness checks and
   evidence schema. Inspect code before invoking an unfamiliar entrypoint:
   `--dry-run` can write synthetic results and `--help` need not be side-effect-free.
3. Read the project's own adapter if it has one: the note, usually linked from
   its AGENTS.md, that lists the harness entrypoints and their boundaries, locks,
   verdict labels and known traps, sometimes with a read-only inventory helper.
   A clean inventory or green helper means the local files were read, not that
   execution, remote readiness, provenance or promotion is approved. Without an
   adapter, inventory the entrypoints read-only from their source.

## Project adaptation boundary

This skill is generic. Before executing any harness step, identify at minimum:
the metric and units, workload/fixture identity, correctness gate, execution
environment, agreed budget, where raw evidence lands, per-sample run identity
(which build, which arm), and how each run returns to the same initial state.
The project supplies every value; none of them may default to a historical
number from another project.

A new measurement entry must pass acceptance before its numbers support any
conclusion: run the same build as both arms repeatedly and check the noise
level with no systematic arm difference; make the state reset reproducible;
make the correctness criterion catch a known error; and keep the raw records
complete with correct units. A failed acceptance is handled as "measurement
itself unreliable".

Each project's adapter carries its own commands, thresholds and verdict labels.
Do not carry one project's commands, historical budgets or labels into another
- a different service, language or repository. Use the project's actual schema;
without an adapter, stop before execution and state the gap, while read-only
diagnosis may continue.

## Establish the experiment contract

Before any new build, benchmark or profiling run, record the target revision and
workspace changes, workload/fixture identity, metric and units, allowed changes,
correctness checks, evaluator version/policy source, execution host, result path,
candidate/run/time limits and stop conditions. Include warmup, reference runs,
replication, failures and retries in the budget; distinguish pairs from arm runs.
Use an agreed budget, not a copied historical 30-minute or 0.5% default.

Missing metric targets need not block read-only diagnosis. They do block claims
that an unspecified target was met. Missing executables, occupied locks or broken
recordkeeping block affected execution; never invent a repaired historical ledger.

For a new AI patch, obtain explicit user confirmation of model and reasoning
effort for this batch. Reconfirm on a new batch or model change. Check the actual
backend invocation matches that confirmation; metadata alone is insufficient.
Do not silently fall back to a different model/provider. If unsupported, stop
generation and offer the supported options without choosing for the user.
Ordinary build/timing commands and evaluation of a supplied patch do not require
choosing a generating model. Record any unavailable historical provenance honestly.

## Diagnose, patch and measure

Use [the evidence checklist](references/evidence.md) when forming a hypothesis.
Pair the actual hot source with profile evidence, actual assembly and recorded
CPU/compiler/flags where relevant. Distinguish CPU work from waiting. Missing PMU
events, zero counters or empty reports are not evidence of zero cost. Static
analysis can suggest a patch; it cannot establish a runtime speedup.

Keep one reviewable hypothesis per candidate where practical. Do not change the
workload, correctness oracle, metric boundary or gate to make a patch succeed.
Explicitly account for moving work outside the timed window and rare costly paths.
Build and correctness precede performance conclusions. Record actual arm identity
from the execution plan, never infer it from which run is faster. Preserve raw
samples, artifacts, deviations and invalid attempts. Do not discard inconvenient
samples or add attempts after seeing results unless that rule was authorized ahead
of time. Profiling/instrumented runs are separate from promotion measurements.

## Screen candidates, confirm separately

Screening (exploration) only picks candidates: write the screening rule and the
candidate cap into the contract before screening, and record how many were
screened. Selected candidates are concluded from pre-agreed, FRESH confirmation
measurements. Screening data is never merged into confirmation, and the report
uses the confirmation result - not the best screening number, which is
naturally inflated by selection.

Every patch identity stands alone: a patch changed after seeing results is a
new candidate without inherited evidence, and merging two candidates is a new
candidate needing its own confirmation. List screening and confirmation budgets
separately in the contract; "change until it wins" iteration rounds count into
the budget.

## Interpret and stop

Keep separate: raw verdict; stage and observed sample count; correctness and
infrastructure validity; evidence-only status; current promotion authority; user
authorization to commit, merge, push or open a PR. Never infer a terminal state
from a missing final stage or a completed timing process. Unknown states remain
unknown and require schema review; they are not rejection, success or a zero
denominator row.

Performance claims go through the project's performance-gated path; do not
reroute a performance patch through a correctness-only bypass. A noisy
single-run signal is not promotion. Research artifacts are not production
authorities. Use the project's actual verdict labels; do not invent new ones.

Stop on the agreed budget, invalid evidence, scope violation, correctness failure,
or an unresolved/noisy result that requires a separately authorized retry. Do not
automatically enlarge samples, train a new judge, switch targets or start a paper
study. A valid accepted verdict supports a scoped evidence claim, not automatic
integration or a promise of general performance improvement.

When the developer and the agent agree the line has converged - the stop
condition is reached and correctness plus a final representative re-measure
pass - draw the final chart per [the convergence chart rules](references/convergence.md).
Only landed, confirmed optimizations become points; every other candidate goes
in the table under the chart.

## Hand off in plain language

Report briefly in the user's language: what changed or was diagnosed; what evidence
supports it; what remains unknown; measured cost; next authorized action. Link the
patch and evidence using real absolute paths. Separate local commit, remote push
and PR status. Give a useful intermediate result without calling a plateau
"convergence" or a fixture test "live performance validation".
