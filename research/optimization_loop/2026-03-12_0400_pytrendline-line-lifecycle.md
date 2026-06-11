# PyTrendline 报告：补 line lifecycle 与 state diagram

## Why this was chosen now

这轮继续沿着最近几次自动优化的同一条主线推进：`pytrendline_research` 的 explainability / auditability。

最近几轮已经补了：
- decision chain
- filter waterfall
- accepted vs rejected examples

在这些规则与真实样例之间，当前最相邻、也最值得补齐的一步，就是把“一条线的生命周期”明确讲出来：
- 什么时候它还只是 candidate；
- 什么时候它已经成为有效结构线；
- 什么时候它被标成 breakout；
- 什么时候它只是结果里仍存在、但不再默认展示；
- 当前页面有没有 expired / retired state。

这既延续了同一研究线程，也直接补强了页面的可审计性与时间语义边界说明。

## What changed

### 1) 在报告中新增 `Line lifecycle` 区块

文件：
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`

新增生命周期表，按状态解释一条线会经历什么：
- candidate pivot-pair
- rejected before result pool
- valid non-breakout line
- breakout-tagged line
- grouped but not representative
- best-from-group representative
- expired / invalidated state?（明确当前页面未单独建模）

每个状态都补了：
- 当前窗口下的 evidence 计数；
- 这个状态在当前页面里到底代表什么；
- 它会如何出现在报告里，或为什么默认不直接出现在图上。

### 2) 新增单独的 `state diagram`

新增 artifact：
- `reports/artifacts/pytrendline_research/line_lifecycle_state_diagram.svg`

这张图把当前页面的状态流转画成了单独示意：
- `candidate -> rejected`
- `candidate -> valid result`
- `valid result -> valid non-breakout / breakout tagged`
- 两条分支再进入 duplicate grouping
- 最终分成 `best-from-group` 与 `grouped away`

同时在图底部明确写清：
- 当前页面没有单独的 expired / retired state；
- breakout 后更像是“保留为研究事件线”，而不是 bar-by-bar 退场审计对象。

### 3) 回写 TODO

已将以下条目标记完成：
- `在报告中新增一个 line lifecycle 区块`
- `给 line lifecycle 配一张状态流转图 / state diagram`

## Validation / evidence

### A. 最小重建

执行：
- `/root/clawd/jerry/momentum/.venv/bin/python /root/clawd/jerry/momentum/scripts/build_pytrendline_report.py --ticker BTC-USD --period 10d --interval 5m --window-bars 96`

结果：
- 成功重建 `reports/site/factors/pytrendline_research/report.html`

### B. 页面存在性检查

已确认生成后的 HTML 包含：
- `Line lifecycle：一条线从 candidate 到代表线会经历什么`
- `State diagram：line lifecycle 状态流转图`
- `line_lifecycle_state_diagram.svg`

### C. 新 artifact 检查

已确认：
- `reports/artifacts/pytrendline_research/line_lifecycle_state_diagram.svg` 已生成
- 文件大小非 0，可被报告页面直接引用

## Risks / caveats

- 这轮补的是“窗口末端视角的生命周期解释”，还不是 bar-by-bar replay 审计。
- 当前 lifecycle 里的 evidence 计数，依然基于当前窗口扫描结果，而不是历史每根 bar 的存活轨迹。
- 页面现在已经明确说明“没有 expired / retired state”，但如果后面要走到正式 signal engine，这部分仍需要单独设计。

## Next recommended step

下一轮最自然的相邻动作有两个：

1. **selected line deep-dive**
   - 选 1 条 support、1 条 resistance，把 `m / b / num_points / score / breakout_index` 逐项讲透。

2. **时间语义 / 生命周期边界**
   - 单独说明现在看到的是“窗口末端回头看”的结果，哪些字段带事后视角，哪些可以视为当时已知。

## Commit hash (if committed)

- 实现与报告变更已 selective commit：`2ef9df7` (`report(pytrendline): add line lifecycle state diagram`)

## Commit note

本轮 repo 内仍有与本次无关的脏文件（例如 interval sweep / crypto rebound / reading deep dives / 较早 optimization loop 记录等），因此没有整仓提交；只 selective commit 了本轮直接相关的：
- `docs/TODO.md`
- `scripts/build_pytrendline_report.py`
- `reports/site/factors/pytrendline_research/report.html`
- `reports/artifacts/pytrendline_research/*`（本轮重建产物）

本记录文件将单独提交，避免把无关脏文件一并打包进同一个提交。
