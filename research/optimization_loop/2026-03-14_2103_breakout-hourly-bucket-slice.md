# breakout sizing honesty：hourly active-position bucket 结果切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：在已有 `entry-only / hourly path / 1-slot` 三档约束基础上，再补一刀真实结果：把 `raw / confirm_1 / avoid_fluctuating` 的 `20bps hourly mark-to-market` 路径按 `active_positions` 拆桶，回答 sizing follow-up 的关键问题——当前拖累到底是不是“最拥挤时刻”。

## 为什么选这个

当前 Top 3 第 3 条仍是 open（`raw sizing / portfolio honesty 再往前补半步`），而且它是典型“下一刀该做结果而不是继续写文案”的任务。

这一刀的价值在于：
1. 完全复用现有 hourly path artifacts，不需要新增重型下载；
2. 直接产出可复核数据（不是措辞）；
3. 能把后续 sizing policy 从“拍脑袋限并发”收窄成更可验证的问题。

## 做了什么

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 helper：`summarize_hourly_active_position_buckets(...)`
   - 对以下三条路径统一做 `active_positions` 拆桶：
     - `raw_v0`
     - `confirm_1`
     - `avoid_fluctuating`
   - 新增 durable artifact：
     - `reports/artifacts/support_breakout_v0_h24/hourly_active_position_bucket_compare_20bps.csv`
   - 在 `support_breakout_v0_h24` 报告新增结果段：
     - **把 hourly path 按活跃仓位数拆开后，真正拖累这条线的是“最拥挤时刻”吗？**
2. 更新入口同步
   - `docs/TODO.md`：给 Top 3 第 3 条补最新结果
   - `scripts/build_alpha_closure_board_report.py`：breakout 卡片 evidence/next 同步这刀结果
   - 重建页面：
     - `reports/site/factors/support_breakout_v0_h24/report.html`
     - `reports/site/factors/alpha_closure_board/report.html`
     - `reports/site/plans/momentum_todo.html`

## 关键结果

来自 `hourly_active_position_bucket_compare_20bps.csv`：

### 1) 最弱桶不是 4 仓，而是 2 仓并发

- `raw_v0` 的 `2` 仓小时：
  - hour share 约 `16.67%`
  - mean hourly return 约 `-0.15%`
  - negative hour share 约 `63.51%`
- `raw_v0` 的 `4` 仓小时：
  - hour share 约 `36.04%`
  - mean hourly return 约 `+0.10%`

=> 当前不支持“最高并发最差”的直觉。

### 2) confirm_1 / avoid_fluctuating 也给出同方向提示

- `confirm_1` 的 `2` 仓小时 mean return 约 `-0.02%`
- `avoid_fluctuating` 的 `2` 仓小时 mean return 约 `-0.09%`

=> `2` 仓并发弱小时是跨方案都存在的薄弱点，不是 raw 独有噪声。

### 3) sizing follow-up 应从“where”入手，而不是“cap all high-concurrency”

这轮结果把下一步问题收窄成：
- 先定位这些 `2` 仓弱小时集中在哪些 `split / regime / symbol mix`；
- 再决定 sizing policy 怎么收（例如是否要做状态条件化仓位收缩），
- 而不是先行盲目 cap 掉最高并发。

## 验证

- 报告段落已落页：
  - `reports/site/factors/support_breakout_v0_h24/report.html`
  - 命中标题：`把 hourly path 按活跃仓位数拆开后，真正拖累这条线的是“最拥挤时刻”吗？`
- 新 artifact 已生成：
  - `reports/artifacts/support_breakout_v0_h24/hourly_active_position_bucket_compare_20bps.csv`
- 入口同步已完成：
  - `docs/TODO.md`
  - `reports/site/plans/momentum_todo.html`
  - `reports/site/factors/alpha_closure_board/report.html`

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍较脏，且本轮涉及文件（`docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、相关 site 输出）部分在本轮前已处于 dirty 状态；此时做 selective commit 无法稳定保证只包含本轮变更。