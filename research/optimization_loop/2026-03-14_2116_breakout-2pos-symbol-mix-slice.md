# breakout sizing follow-up：2 仓弱小时的 symbol-mix 结果切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把上一轮已经确认的“`2` 仓小时偏弱”继续落成可复核结果，直接回答这些弱小时更集中在哪些 `symbol pair`，并把结论同步到网页总入口。

## 为什么选这个

`Current relay baton` 的 breakout 第 3 条明确写了下一步要看 `2` 仓弱小时的 `split / regime / symbol mix`，这属于真实结果导向切片，不是 wording 微步。并且可完全复用现有 artifacts，无需重型下载。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 3 个 helper：
     - `build_hourly_active_position_mix_detail(...)`
     - `summarize_hourly_active_position_symbol_mix(...)`
     - （沿用现有 hourly path artifacts）
   - 在 `active_positions=2` 桶上，生成三条线（`raw / confirm_1 / avoid_fluctuating`）的 `symbol pair` 对照汇总；
   - 新增 durable artifact：
     - `reports/artifacts/support_breakout_v0_h24/hourly_active_position_2_symbol_mix_compare_20bps.csv`
   - 在 `support_breakout_v0_h24/report.html` 新增可见段：
     - `如果继续追 2 仓弱小时，它们更像卡在什么 symbol mix？`
2. 更新 `docs/TODO.md`
   - 将 breakout Top 3 第 3 条标记为完成 `[x]`；
   - 将结果补充为具体 pair 级读法（不是只停留在“2 仓偏弱”）。
3. 更新 `scripts/build_alpha_closure_board_report.py`
   - breakout 卡片 evidence/next 同步 pair 级结果：
     - 弱点更像集中在 `BTC/SOL`、`ETH/SOL`、`BNB/ETH` 等 2 仓 pair 结构；
     - 下一步应继续追这些弱 pair 在 `split / regime` 上的集中位置，而不是盲目 cap 并发。
4. 重建可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 核心结果（20bps hourly mark-to-market）

### 1) raw 的 2 仓弱小时确实高度集中在少数 pair

在 `raw_v0` 的 `active_positions=2` 桶里：
- 占比最大 pair：`BTC-USD + SOL-USD`
  - 约 `34` 小时，占 raw 两仓小时约 `45.95%`
  - mean hourly return 约 `-0.18%`
- 最差 pair：`ETH-USD + SOL-USD`
  - mean hourly return 约 `-0.31%`

这说明“2 仓偏弱”不是均匀噪声，更像少数并发 pair 在拖累。

### 2) avoid_fluctuating 的改善更像“换掉了一部分坏 pair 结构”

- `BTC-USD + SOL-USD` 从 raw 的约 `34` 小时降到 gate 下约 `3` 小时；
- gate 下出现均值为正的 pair（如 `BNB-USD + SOL-USD` 约 `24` 小时、mean hourly return 约 `+0.11%`）；
- 但 `ETH-USD + SOL-USD` 与 `BNB-USD + ETH-USD` 仍偏弱，说明 gate 不是万能开关。

### 3) breakout 第 3 条已从“原则”推进到“pair 级可执行问题”

当前最有价值的 next step 已更明确：
- 不再先做“全局并发上限一刀切”；
- 而是继续追这些弱 `2` 仓 pair 更集中在哪些 `split / regime`，再决定 sizing policy 如何收。

## 验证

验证命中：
- `reports/artifacts/support_breakout_v0_h24/hourly_active_position_2_symbol_mix_compare_20bps.csv` 已生成；
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现新段标题与 pair 表格；
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已将 breakout 第 3 条标记为 `[x]` 并同步结果；
- `reports/site/factors/alpha_closure_board/report.html` 已同步 pair 级 evidence/next。

## Commit

本轮**未提交**。

原因：当前 repo worktree 已长期处于高脏状态，且本轮涉及路径（`docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应 site 输出）在本轮前已存在在途改动；此时做 selective commit 仍无法稳定保证仅打包本轮变更。
