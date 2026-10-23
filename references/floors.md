# Two floors

Two variants of the program, measured with the same accepted measurement entry
as the real one, show how much of the time is computation and how much is
waiting for data. They need no hardware counters, so on a machine without a PMU
they stand in for the IPC and miss-rate readings, and in a continuous line they
give the stop rule a distance to measure.

## Build them

- Compute floor: the same code path and the same work per item, with the data
  shrunk to fit in cache. Keep the items of one unit of work distinct - for
  example map the k-th item of a unit onto slot k of a small table - and keep
  the table small enough to stay cached. A plain modulo by a small count can put
  two items of one unit on the same record; the later one then waits for the
  earlier one's store, a dependency the real program does not have, and the
  floor comes out high. The output is wrong by construction; check only that
  the work per item is unchanged: trip counts, calls, the path taken.
- Data floor: the computation removed and the memory accesses kept: same
  addresses, same order, each loaded value folded into a checksum that is
  written out so the compiler cannot drop the loads, and the program's stores
  kept as well (store something cheap, such as the running checksum), because a
  dirty line costs a write-back when it leaves the cache. Check in the assembly
  that the loads and stores remain.

Build both from the version being measured, outside the candidate line, with the
same flags, host, pinning and metric boundary. They are instruments: never
candidates, never landed, never on the chart. Record how each was built, its
build hash and its result; their runs count in the budget.

Measure the real version and its two floors in the same session, interleaved;
numbers from different sessions are not compared. Give each floor as many runs
as the real version gets in that session and report its interval: a floor
measured twice cannot say how close the real version is.
In a continuous line do this for the baseline and again after every landing, with a short A/A of the real
version in the same session, because a landed patch can change the work, the
loads or both, and the noise at its speed.

## Read them

With T the real time, C the compute floor and D the data floor, judged against
the noise from the A/A check:

| Reading | Meaning |
|---|---|
| C well below T, D close to T | The time is waiting for data. Read the memory special `content/posts/low-latency-memory-latency-bandwidth.md` (`{#in-practice}`, and its sections on memory-level parallelism and prefetching; the perf special's `{#stat-ratios}` links to it too): how many independent loads one unit of work keeps in flight, and whether the next address waits for this load. |
| C close to T, D well below T | The time is computation; memory work will not move it. |
| T close to C + D | Computation and waiting take turns; overlapping them is the headroom. |
| C + D well below T | Two readings. The time goes elsewhere (synchronization, the timing boundary, a rare path), or the computation in the real loop keeps fewer loads in flight than D had, so D understates the waiting (below). Rule out the first with the symptom table in `SKILL.md`; if none of it applies, treat the time as waiting for data. |

max(C, D) is a reference for the current design, not a bound on every design: a
patch that changes the layout, the bytes touched or which core does the work can
go below it, which is why the stop rule's floor condition is used only when the
allowed changes keep the layout, bytes touched and cores. Removing the
computation also lets the core keep more loads in flight, so D can understate
the waiting inside the real program.

A report that the time is close to a floor therefore names the design the
floor was measured on - layout, bytes touched, which cores - and the allowed
changes that could move it. The floors say how far the current design is from
its reference, not that nothing is left to gain.

## Stage probes

Timestamps around the stages of one unit of work - a handoff between threads, a
wait, one pass - in an instrumented build show where the time goes inside T.
They follow the floors' rules: built from the version being measured, run as
instruments, never candidates, their runs counted in the budget. Use them to
say why a candidate lost before its direction is marked closed.
