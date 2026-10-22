# Continuous line

Read this when opening a line and whenever a session resumes one. Every
candidate still follows `SKILL.md`; this file adds what holds across candidates.

## Opening authorization

Written into the ledger verbatim before the first run, never rewritten:

- model and reasoning effort for patch generation;
- total budget in the project's unit, the candidate cap, and the part reserved
  for the final re-measure;
- allowed changes, and what stays frozen: data layout, threads and cores,
  workload parameters, compiler flags, the timing boundary;
- the screening rule and the confirmation rule (sample size, statistic, decision
  threshold), the same for every candidate of the line;
- the stop rule: budget spent, N consecutive candidates without a landing, or
  the landed version within an agreed distance of the larger floor
  ([two floors](floors.md)), whichever comes first.

A later change from the user is appended with its date and source and applies
only to candidates opened after it; it never relabels earlier results.

## Ledger

One directory per optimization line, under the result path named in the
contract:

- `ledger.md`, rewritten after every step: the authorization and the contract;
  the measurement-entry acceptance (A/A noise, the known error the correctness
  gate caught); the floors of each landed version (how built, build hash, value,
  interval); the landed chain (k, version hash, candidate, confirmed change
  against k-1 with its interval); budget spent and left by stage (acceptance,
  floors, screening, confirmation, final reserve); and one line naming the next
  step and the version it applies to.
- `candidates.tsv`, one row per candidate, appended: id, base version,
  hypothesis, card, patch SHA, correctness, screening result, confirmation
  result, verdict, cost, evidence path.

Raw records stay in the per-run directories the ledger points to; the ledger
summarizes them and never replaces them.

## Resuming

After a context reset, a crash or in a new session, read `ledger.md` first.
Check that the checkout's landed version matches the ledger's last hash and that
any run in flight left complete records. An incomplete run is invalid: rerun it
as a new attempt counted in the budget, never fill it in. Then continue from the
next step. Never rebuild state from memory or from the conversation.

## Measuring against the landed version

- The baseline arm of every screen and confirmation is the current landed
  version. The original appears again only in the final re-measure.
- After a landing, profile again before choosing the next hypothesis: the
  hotspot moves.
- Results of candidates screened against the previous version are stale once
  something lands: rebase and screen them again as new candidates, or drop them.

## Ending

When the stop rule fires, re-measure the original and every landed version in
one session, interleaved on the same host with the sample size reserved at the
opening, and draw the chart from those numbers; confirmation numbers from
different sessions are never joined into one line. A landed version that does
not beat its predecessor in this re-measure stays on the chart and is reported,
since a regression between landed points is never hidden. The report names the
stop condition that fired, the landed chain, the distance from the floors, the
candidate table and the budget used.
