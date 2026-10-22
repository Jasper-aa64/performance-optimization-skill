# Two floors

Two variants of the program, measured with the same accepted measurement entry
as the real one, show how much of the time is computation and how much is
waiting for data. They need no hardware counters, so on a machine without a PMU
they stand in for the IPC and miss-rate readings, and in a continuous line they
give the stop rule a distance to measure.

## Build them

- Compute floor: the same code path and the same work per item, with the data
  shrunk to fit in cache, for example by mapping every index onto a few KB
  (index modulo a small count). The output is wrong by construction; check only
  that the work per item is unchanged: trip counts, calls, the path taken.
- Data floor: the computation removed and the loads kept: same addresses, same
  order, each loaded value folded into a checksum that is written out so the
  compiler cannot drop the loads. Check in the assembly that the loads remain.

Build both from the version being measured, outside the candidate line, with the
same flags, host, pinning and metric boundary. They are instruments: never
candidates, never landed, never on the chart. Record how each was built, its
build hash and its result; their runs count in the budget.

Measure the real version and its two floors in the same session, interleaved;
numbers from different sessions are not compared. In a continuous line do this
for the baseline and again after every landing, because a landed patch can
change the work, the loads or both.

## Read them

With T the real time, C the compute floor and D the data floor, judged against
the noise from the A/A check:

| Reading | Meaning |
|---|---|
| C well below T, D close to T | The time is waiting for data. Treat it as the memory-bound reading of the perf special (`{#stat-ratios}`) and follow its link. |
| C close to T, D well below T | The time is computation; memory work will not move it. |
| T close to C + D | Computation and waiting take turns; overlapping them is the headroom. |
| C + D well below T | The time goes elsewhere: synchronization, the timing boundary, a rare path. Return to the symptom table in `SKILL.md`. |

max(C, D) is a reference for the current design, not a bound on every design: a
patch that changes the layout, the bytes touched or which core does the work can
go below it. Removing the computation also lets the core keep more loads in
flight, so D can understate the waiting inside the real program.

The floors say how far the current design is from its reference, not that
nothing is left to gain.
