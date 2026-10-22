# Final convergence chart

Draw this once, at the end of an optimization line, when the developer and the
agent agree the line has converged: the stop condition is reached (agreed budget
spent, resolution exhausted, or no remaining hotspot worth a candidate), and
correctness plus a final representative re-measure of the last safe baseline
pass. During exploration keep ledgers and internal diagnostic charts only, and
label any dated intermediate chart as a draft. The final chart and report keep a
stable file name and are overwritten, not versioned by date.

## What becomes a point

- Point 0 is the baseline before the line started.
- Point k is the safe baseline after the k-th landed optimization: a candidate
  that passed correctness and was confirmed on fresh data under the contract.
- Everything else stays off the line and goes in a table under the chart
  (candidate, result, handling): rejected, unconfirmed or noisy, pending,
  build-only, synthetic or dry-run, correctness not closed, failed on
  replication. That table is the evidence for why the line stopped.
- A bundle of small changes becomes one point only after the bundle itself is
  confirmed as a new candidate; its members never enter the curve one by one.
- Re-measuring the same code at another sample size or workload tier is
  evidence for an existing point, not a new point.
- If nothing landed, draw no convergence line; report the candidates in the
  table instead.

## Hard rules

- One metric per chart. Different interfaces, paths or statistics get separate
  charts; do not join them into one cumulative curve or replace the single line
  with panels.
- No smoothing: never add a point to make the curve look steadier, never drop
  the baseline, never hide a regression between landed points.
- Cumulative change, in the metric's own unit: `gain = start - end` and
  `ratio = (start - end) / start` for lower-is-better metrics. For
  higher-is-better metrics flip the sign and say so in the subtitle.
- Correctness-first tasks may add a separate diagnostic chart (for example a
  count of lost messages). Its title and axis say what it measures; it is never
  a gain chart.

## Style

- Line chart, about 1040 x 579 (16:9), light horizontal grid only.
- Title top-left in bold: `Landed safe optimizations: N` (Chinese:
  `已合入安全优化：N个`).
- Subtitle right under it: `start -> end, cumulative gain X <unit> / Y%`.
- X axis: iteration. Y axis: the metric with its unit.
- Blue line (`#3f7be0`), white points with blue edges, each point's value in
  bold under it, each optimization's name slanted along its segment.
- Footer bottom-right in small grey text: environment and gate only, for example
  `Linux gate · compare passed`. No company or internal system names.

## Rendering

`scripts/render_convergence_chart.py` renders this style as dependency-free SVG
from a TSV with one row per point:

```text
python <skill-root>/scripts/render_convergence_chart.py \
  --input <points.tsv> --output <chart.svg> \
  --x-column iter --y-column <metric> --label-column label \
  --title "Landed safe optimizations: N" \
  --subtitle "start -> end, cumulative gain X <unit> / Y%" \
  --x-title "Iteration" --y-title "<metric> (<unit>)" --unit "<unit>" \
  --footer "<environment> · <gate>"
```

Feed it landed points only. `--safe-only` applies HFT-wf's TWAP columns
(`status=PASS`, `lost=0`, `unknown_pushes=0`); other projects filter their TSV
before rendering. `--filter key=value` keeps matching rows; `--remap-x` numbers
the kept rows 0..N-1; `--zero-min` starts the Y axis at zero.
