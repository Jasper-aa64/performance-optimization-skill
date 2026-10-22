# performance-optimization

An agent skill for performance work on real code. It takes an agent from "this is
slow" to a decision backed by evidence: find where the time goes, recognize the
bottleneck, write one bounded patch per hypothesis, check correctness, and keep
the patch only if a pre-agreed measurement on fresh data confirms it. Under one
opening authorization it can keep going as a continuous line, landing each
confirmed patch and measuring the next against it until a stop rule written in
advance fires. At the end of a line it draws one final convergence chart.

It runs in Codex (`$performance-optimization`) and in Claude Code or any agent
that can read files. [中文说明在下面](#中文说明).

## The five steps

The skill tells the agent which step it is in and what to read next.

1. **Scope.** Diagnose, optimize, or evaluate an existing patch. Read-only
   discovery comes first. Before any build, benchmark or profiling run, write an
   experiment contract: metric and units, workload, correctness checks, host,
   budget and stop conditions.
2. **Find the time.** Route by what is in hand (nothing measured yet,
   `perf stat`, `perf report`, contention, scaling) to the matching section of
   the perf special on the author's blog. Probe hardware counters first; on a VM
   without a PMU, sample with `cpu-clock` and read annotate.
3. **Recognize the bottleneck.** Look the signal up in the bottleneck lookup,
   one line per card, then read only the matching card: signal, cause, fix,
   verification, and links to the mechanism. Never fix from memory.
4. **Patch and accept.** One reviewable hypothesis per candidate; correctness
   before performance. Screening only picks candidates; a pre-agreed, fresh
   confirmation decides. A card's verification items are self-checks, not
   acceptance.
5. **Stop and converge.** A correctness failure, a failed screen or an
   unconfirmed result ends that candidate. A run stops on the agreed budget,
   invalid evidence, a scope violation or a stop rule written in advance. A
   continuous line lands each confirmed candidate, measures the next against it
   and keeps its ledger on disk until its stop rule fires. At the end, draw the
   final chart with landed, confirmed optimizations only.

## How it loads

The skill uses progressive disclosure, so an agent reads a few small files per
task instead of everything:

- Always in context: the one-sentence `description` in `SKILL.md`.
- When triggered: `SKILL.md`, which routes and holds the rules.
- On demand: `references/`, an adapter, one blog section, one bottleneck card.
- Rarely: the posts a card links to, Intel's original pattern file, raw evidence.

How-to content lives in one place, the blog; the skill only points at stable
anchors. A new bottleneck arrives as a new card file and appears in the lookup
without any change to the skill.

## Layout

```text
SKILL.md                              router and rules
agents/openai.yaml                    Codex display metadata
references/evidence.md                what evidence to gather, how to record a candidate, how to read uncertainty
references/convergence.md             rules for the final convergence chart
references/continuous-line.md         authorization, ledger and resuming for a continuous line
references/floors.md                  two floors: computation vs waiting for data, without counters
scripts/render_convergence_chart.py   dependency-free SVG renderer for that chart, with tests
```

## Install

- Codex: clone this repository to `~/.codex/skills/performance-optimization`,
  or link that path to a clone.
- Claude Code: the same under `~/.claude/skills/performance-optimization`, or
  point the session at `SKILL.md`.

## Adapters

The skill is project-agnostic. A project with its own harness keeps an adapter
note in its own repository, usually linked from its AGENTS.md, describing its
entrypoints, metric, correctness gate, locks and verdict labels. Without one the
agent may still diagnose read-only. To execute, it needs the adapter or an
authorization that hands over a frozen baseline package (target build, workload,
metric, correctness gate), from which it builds its own measurement entry and
accepts it before trusting a number. With neither, it stops before execution and
states the gap.

## Related

- Perf special: https://jasper-aa64.github.io/posts/low-latency-perf-profiling/
- Bottleneck cards: https://jasper-aa64.github.io/ref/bottlenecks/
- The measurement method behind step 4: https://github.com/Jasper-aa64/promotion-gate-audit
- Source of the bottleneck patterns: https://github.com/intel/intel-performance-skills (commit 3e33aec)

## Limits

- Without hardware counters, IPC, cache-miss, branch-miss and c2c readings are
  unavailable. The skill records the gap instead of guessing; the two floors
  (`references/floors.md`) still tell computation from waiting for data.
- The cards so far are CPU-level patterns. Waits, I/O and syscall-heavy
  hotspots fall back to the symptom table in `SKILL.md`.
- "Unconfirmed within this budget" does not mean "no effect", and the skill
  cannot certify that nothing is left to gain. The floors are a reference for
  the current design, not a proof.

## Tests

```text
python -B -m unittest discover -s scripts -v
```

---

## 中文说明

一个给 agent 用的性能优化 skill，管的是从"这段代码慢"到"有证据的结论"：找出时间花在哪，认出是哪种瓶颈，一个假设写一个有边界的补丁，先过正确性，再用事先约定、用全新数据的测量确认，确认了才收。开场一次授权，还能连续跑一条优化线：确认一个落地一个，下一个跟落地版比，直到事先写好的停线规则触发。一条线结束时，画一张最终的收敛图。

Codex 里用 `$performance-optimization` 调用；Claude Code 或其他能读文件的 agent 直接读 `SKILL.md`。

### 五步

skill 告诉 agent 现在在哪一步、下一步读什么。

1. **定范围。** 是诊断、优化，还是评测已有的补丁。先只读摸底；编译、跑基准、采 profile 之前，先写实验契约：指标和单位、负载、正确性检查、机器、预算、停止条件。
2. **找时间花在哪。** 按手上有什么（还没测、有 `perf stat`、有 `perf report`、线程抢、多核扩展不上去）路由到博客 perf 专题对应的小节。先探测硬件计数器；没有 PMU 的虚拟机上，用 `cpu-clock` 采样加 annotate。
3. **认瓶颈。** 拿信号去瓶颈查找表里对（一张卡片一行），只读对上的那张卡片：信号、原因、修法、验证、讲原理的链接。不凭记忆改。
4. **改和收。** 一个候选一个可审的假设；先正确性，后性能。筛选只负责挑候选，结论只看事先约定、用全新数据的确认。卡片里的"验证"只算自查，不算验收。
5. **停和收敛。** 正确性失败、没过筛、没确认，只结束这一个候选；预算用完、证据无效、越界，或者事先写下的停线规则到了，才停下这次运行。连续优化线确认一个就落地一个，下一个跟落地版比，台账写在盘上，直到停线规则触发。最后画收敛图：只画已落地、已确认的优化。

### 怎么分层加载

用渐进式披露，一次任务只读几个小文件：

- 常驻：`SKILL.md` 头部一句话的 `description`。
- 触发后：`SKILL.md`，负责路由和规矩。
- 按需：`references/`、某个项目的适配器、博客的某一节、某一张瓶颈卡片。
- 很少用到：卡片链到的原理文章、Intel 原文、原始证据。

怎么做的内容只放博客一处，skill 只指向稳定的锚点。以后加一种瓶颈，只多一个卡片文件，查找表自动带上，skill 不用改。

### 目录

```text
SKILL.md                              路由和规矩
agents/openai.yaml                    Codex 里显示的名字和默认提示
references/evidence.md                要收集哪些证据、候选怎么登记、不确定性怎么读
references/convergence.md             最终收敛图的规矩
references/continuous-line.md         连续优化线的开场授权、台账、续跑
references/floors.md                  两个地板：不靠计数器，分清在算还是在等数据
scripts/render_convergence_chart.py   不依赖第三方库的收敛图出图脚本，带测试
```

### 安装

- Codex：把仓库克隆到 `~/.codex/skills/performance-optimization`，或者把这个路径链接到一份克隆。
- Claude Code：同样放到 `~/.claude/skills/performance-optimization`，或者让会话直接读 `SKILL.md`。

### 适配器

skill 本身不绑项目。有自己 harness 的项目，在自己的仓库里放一份适配说明（一般从它的 AGENTS.md 链过去），写清入口、指标、正确性门、锁和结论标签；没有的话，agent 可以只读诊断；要执行，授权里得交给它一份冻结的基线包（目标版本、负载、指标、正确性门），它据此自己搭测量入口，验收过了才信数字。基线包也没有，执行前停下来说明缺什么。

### 相关链接

- perf 专题：https://jasper-aa64.github.io/zh/posts/low-latency-perf-profiling/
- 瓶颈卡片：https://jasper-aa64.github.io/zh/ref/bottlenecks/
- 第 4 步背后的测量方法：https://github.com/Jasper-aa64/promotion-gate-audit
- 瓶颈卡片的出处：https://github.com/intel/intel-performance-skills（提交 3e33aec）

### 边界

- 拿不到硬件计数器时，IPC、缓存缺失、分支失败和 c2c 都没有，skill 记下缺口，不猜；两个地板（`references/floors.md`）照样能分清在算还是在等数据。
- 目前的卡片都是 CPU 层面的瓶颈；等待、I/O、系统调用为主的热点，回到 `SKILL.md` 里按症状分的表。
- "本次预算内未确认"不等于"没效果"，skill 也证明不了"已经榨干、没有可改的了"。地板只是当前设计的参照，不是证明。

### 测试

```text
python -B -m unittest discover -s scripts -v
```
