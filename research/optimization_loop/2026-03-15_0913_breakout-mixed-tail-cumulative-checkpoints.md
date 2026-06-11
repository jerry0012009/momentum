# Breakout mixed-tail cumulative shadow checkpoints

- 时间：2026-03-15 09:13 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 本轮只推进 1 个主点：继续沿 breakout 的 `down+flat mixed-tail overlay` 补一层**更长、但仍克制**的 shadow honesty；不重开 EMA / Fib，也不新增近义 board。

## 为什么认领这刀

按当前 steering，breakout 仍是最高执行优先级，而 mixed-tail overlay 已经有：
- overall first-pass 为正；
- rolling walk-forward `3/3` active windows 为正；
- 但 non-overlap `5d/10d` forward blocks 与 target-pocket honesty 仍是 split verdict。

因此这轮继续问一个更 deployment-facing 的小问题：

> 如果把 mixed-tail overlay 也翻成从首个触发时点开始的 **cumulative shadow review checkpoints**，它到底是“前瞻一看就塌”的假 gate，还是“累计路径还站得住、但依然不够 promotion”的 shadow-only gate？

## 本轮完成

### 1) 新增 mixed-tail overlay 的 cumulative checkpoint artifact

在 `scripts/build_support_breakout_v0_reports.py` 中，把现有 `summarize_hourly_pair_shadow_checkpoints(...)` 复用到：
- 基线：`avoid_fluctuating_eth_sol_pair_halfsize`
- 对照：`avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay`
- review days：`[5, 10, 15, 20]`

新增 artifact：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_shadow_checkpoints_20bps.csv`

### 2) 刷新 breakout 主报告

`reports/site/factors/support_breakout_v0_h24/report.html` 新增 mixed-tail overlay 的一节：
- cumulative shadow review checkpoints 是否仍为正；
- 最弱 checkpoint 有多薄；
- 为什么这还不足以改写 `one_more_gate`。

### 3) 同步 TODO / plans 入口口径

- `docs/TODO.md` 新增一条 `[x]` 结果记录；
- 重新生成 `reports/site/plans/*`，确保 TODO 页面同步更新。

## 结果

相对默认 `ETH+SOL pair halfsize` 基线，mixed-tail overlay 从首个触发日开始的 cumulative checkpoints 为：

- `5-day`：`+0.55pp`，回撤改善 `+0.51pp`
- `10-day`：`+0.57pp`，回撤改善 `+0.51pp`
- `15-day`：`+0.59pp`，回撤改善 `+0.51pp`
- `20-day`：`+0.19pp`，回撤改善 `+0.49pp`

对应读法：
- 当前 `4/4` checkpoints 仍为正，所以它**不是**“一进累计 shadow review 就塌”的假 gate；
- 但 edge 到 `20-day` 已明显收窄成 very thin；
- 再结合前面已知的 `5d/10d non-overlap blocks = 1/2 正, 1/2 负`，以及 target-pocket conditional honesty 也会翻弱，mixed-tail overlay 仍不能诚实写成 admission clearance。

## 本轮 verdict

本轮结果让 breakout 的结构更清楚，但**没有**改写正式 verdict：

- `default pair halfsize`：继续保留为 breakout 默认主候选
- `down+flat mixed-tail overlay`：仍是 `shadow-only mixed gate`
- `blunt pure-down overlay`：维持 reject / sanity check
- breakout 总 verdict：继续维持 `shadow-admission queue / one_more_gate`

一句话：

> mixed-tail overlay 的 cumulative shadow review 比 non-overlap blocks 看起来更稳，但稳得还不够；它更像“可继续观察的 shadow gate”，还不是能替代默认 pair candidate 的 promotion patch。

## 变更文件

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_shadow_checkpoints_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

## 最小验证

已执行：

```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py
python3 scripts/build_support_breakout_v0_reports.py
python3 -m py_compile scripts/build_plans_site.py
python3 scripts/build_plans_site.py
```

结果：通过。

## Git / hygiene 备注

本轮开始前工作区已存在大量无关脏改动与未跟踪文件；`git status --short` 观察到：
- `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py` 等本轮涉及文件本身就已经在脏状态；
- repo 中还存在大量与本轮无关的报告、artifact、memory 与 workspace 级未跟踪文件。

因此这轮**没有提交**：当前不适合做安全的 selective commit，避免把无关改动混入本轮结果。
