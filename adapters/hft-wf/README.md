# HFT-wf adapter

Everything specific to the HFT-wf harness lives in this folder: this note, the
read-only inventory helper `inspect_harness.py` and its fixture tests. HFT-wf's
own chart examples and labels stay in its `收敛图规范.md`.

Source snapshot inspected: `9adb660c8f21ba912d4a8b2747389ce22605f078`.
This is a navigation aid, not a frozen execution policy. Resolve every path below
against the actual HFT-wf root. Recheck current files when the checkout changes.
Do not copy credentials, private host identifiers or production configurations into
this skill. Obtain execution-host choices from the current authorized task.

## Existing entrypoints

| Path | Role / invocation boundary |
|---|---|
| `docs/optimization_harness_operator_manual.md` | Read before live operation: scope, host weather, locks, work shifting, provenance and report gate. |
| `scripts/headless_auto_loop.py` | Controller; can generate patches, copy workspaces, launch remote work and write artifacts. Not an inventory command. |
| `scripts/headless_remote.sh` | Default batch. Remote dispatch stages a content-addressed helper bundle; do not substitute an arbitrary old remote checkout. |
| `scripts/patch_agent.py` | Candidate generation; not a generic evaluation command. Read backend dispatch and provenance writes before use. |
| `scripts/attempts_schema.py` | Existing provenance/work-shifting checks. Legacy acceptance in this code is not permission to submit a new unrecorded candidate. |
| `scripts/perf_validation_lock.py` | Shared execution-host lock. `check` is local to where invoked; `acquire` and `release` mutate state. |
| `scripts/perf_capability.py` | Existing capability machinery. Check current per-run capability evidence before interpreting perf. |
| `scripts/performance_report_gate.py` | `--task-json <absolute-task.json>` validates a final performance delivery contract; not a benchmark. |
| `.trellis/scripts/task.py`, `.trellis/workflow.md` | Use the current project lifecycle if present/required. Do not infer availability from an old chat; do not reconstruct missing history. |

Task-specific TWAP work additionally reads `docs/twap_perf_runbook.md`,
`docs/报告规范.md`, `docs/论文线证据采集.md`, and its actual batch adapter
(`scripts/twap_headless_remote.sh` if present). Do not start services or change
fixtures merely because these documents mention them.

Public-paper drivers are separate adapters. At this source snapshot the manual
mentions `05-Paper/experiments/public_second_target_202609/scripts/candidate_runner.py`,
but that path is absent in the inspected checkout. Locate actual artifacts in the
authorized checkout rather than constructing a path or reusing another driver.
Never run a frozen historical public package as a generic new-project runner.

## Controller CLI: inspect, then construct a task-specific command

The inventory helper extracts literal argparse options without executing the file.
At this snapshot the controller exposes:

- `--run-dir`, `--source-root`, `--candidate-workspace`, `--patch-command`;
- `--candidate-seed-file`, `--candidate-ledger`, `--replication-history`;
- `--remote-host`, `--remote-hft-root`, `--remote-batch-script`, `--remote-run-dir`;
- `--max-iterations`, `--max-hours`, `--max-candidates`, `--measure-runs`;
- `--stop-file`, `--first-accepted-stop`, `--dry-run`.

These are options, not a complete safe command. Verify which quantities include
warmup, escalation and replication before translating the user's budget. Default
values are not user consent. The controller is not automatically an existing-patch
adapter; inspect its materialization/seed path so evaluation cannot generate a
replacement. If no safe supported path exists, stop and explain the adapter gap.

`--dry-run` explicitly generates synthetic evidence and writes run state. Do not
use it for read-only diagnosis or count it as real validation.

## Generation backend: do not trust metadata as dispatch

Observed in `scripts/patch_agent.py` at the snapshot:

- Default mode is `api`; `PATCH_AGENT_MODEL` has a hard-coded fallback default.
- API failure can automatically enter CLI fallback; the observed Claude CLI call
  does not explicitly pass a model flag.
- `codex` direct-edit mode returns before the shared provenance-write block.
- The controller's legacy compatibility can accept absent provenance fields.

Consequently, do not launch this default generation path on the strength of a
confirmed-model metadata field. Verify explicit backend model/effort selection,
no unapproved fallback, and provenance written for the actual path. If not possible
with the current adapter, block generation only; continue safe diagnosis or evaluate
an already supplied patch. Adapter repair is a separate scoped change, not a reason
to modify frozen code while running an optimization task.

For new proposed patches, preserve the prompt/hash, model, reasoning effort,
generation time and actual patch SHA. Record the user's confirmation source/batch.
Do not stamp the user's requested model onto an output of an unverified backend.

## Execution and evidence

For HFT-wf tasks the project requires Linux execution evidence; Windows fixture
tests are not promotion measurements. Before shared-host builds, profiling,
service/fixture changes or timing, use the existing atomic host lock with the
long-lived owner PID. A local check does not inspect the remote lock. Never remove
a foreign/live lock or treat its disappearance as proof that work completed.

Use the current host policy. The manual has older clean-host-only wording alongside
later replicated-noisy states; preserve the actual current policy/version and
require explicit valid replication/host evidence for that route. Do not silently
rewrite semantics to match a convenient paragraph. Unresolved policy conflicts
block promotion, not retrospective deletion of evidence.

Read `run_state.json`, `comparison_summary.json`, timing history, per-stage judges
and the candidate's authoritative terminal/replication record as applicable.
Names differ across adapters: verify sources instead of inventing a universal
`final` field. Sample depths record observations, not proof of formal termination.

| Observed state | Handling in this skill |
|---|---|
| `accepted` | Potential current authorization only with valid build, correctness, host and complete evidence under the recorded policy. |
| `accepted_noisy_replicated` | Verify independent replication and applicable policy; a label alone is insufficient. |
| `accepted_noisy_single` | Evidence only; no current promotion. |
| `accepted_class_a` | Preserve system promotion history, outside this class_b evaluation; not a performance proof. |
| `neutral`, `NOISY_PENDING`, pending/escalation states | Preserve stage/context; no current performance authorization. Do not infer sample count from label. |
| rejected / infrastructure failure | Preserve underlying reason; infrastructure failure is not a demonstrated bad patch. |
| Missing/unknown verdict or class | Explicit unknown, not false/success. Review schema and keep record visible. |

Recognized legacy spellings such as `Class B` require an explicit alias mapping,
raw value preservation and visible normalization. Do not accept arbitrary unknown
classes. Correctness failure can be a legal shared terminal for class_a or class_b.

## Research boundary

dd_lin1 and P1/P2 are research artifacts, not operational promotion authorities.
Do not start P3, retune the judge, enlarge historical evidence pools or declare a
universal FAR from a routine optimization request. Existing harness use is separate
from the stopped learned-judge research. New real-project work need not await that
research, but any PR still needs its own scoped evidence and user authorization.
