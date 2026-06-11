# 2026-03-16 20:28 UTC｜Scout Seat：Rank 2 refresh writeback seed（最小接线继续推进）

## 为什么这轮选这个
按 `TRADING DESK BOARD` 先判执行顺序：

- `Run 1 / Paper Seat`：`EMA` 仍是 `waiting_not_due`，本轮不应在 waiting-window 空转；
- `Run 2 / Scout Seat`：默认主资源位；
- `Live Seat` 仍暂空，且没有 bot2 新 promoted candidate 点名。

先比较 active Scout 候选边际价值：

1. `Rank 2 combo_all`
   - 当前唯一仍在前推链路中的候选（`narrow paper pilot approved`）；
   - 前两轮已落 `ledger template -> refresh seed -> weekly review seed`；
   - 若继续认领它，按 board 7.6 只允许补最小 `paper ledger / monitoring / refresh / review` 接线。
2. `Rank 4b / Rank 4 / Rank 3 / Rank 1`
   - 当前都在 `park / evidence pool`，没有新 gate 或新数据源，边际价值低于继续打通 Rank 2 的执行链。

因此本轮主点固定为：
- **把 Rank 2 的 `weekly review seed` 继续压成可直接执行的 `refresh writeback seed`。**

紧邻子点：
- 给 reader-facing 页面补可见链接，避免只在 artifact 层新增。

## 本轮改动
### 1) 新增脚本
- `scripts/build_rank2_narrow_paper_writeback_seed.py`

功能：
- 读取：
  - `combo_all_narrow_paper_pilot_refresh_seed_rows.csv`
  - `combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv`
- 生成：
  - `combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv`
  - `reports/site/factors/scout_volume_supportflip_higherlow_15m/writeback_seed_report.html`

核心输出字段：
- `weekly_review_status`
- `primary_watch`
- `writeback_status`
- `gate_action`
- `refresh_cycle_id`
- `next_review_due_utc`
- `promotion_boundary`

### 2) reader-facing 同步
- 在 `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html` 增加了“narrow paper writeback seed（本轮新增）”卡片，并链接到：
  - `writeback_seed_report.html`
- 在 `reports/site/reading/trendline_alpha_scout/report.html` 的 Rank 2 卡片新增一条：
  - `narrow paper refresh writeback seed`（含 artifact + 页面链接）

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_rank2_narrow_paper_writeback_seed.py`
2. `python3 scripts/build_rank2_narrow_paper_writeback_seed.py`
3. `grep -n "writeback seed\|writeback_seed_report" reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html reports/site/reading/trendline_alpha_scout/report.html`

## 新产物 / deployable artifact
- `reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv`

当前 writeback 状态（按资产）：
- `BTC-USD`：`red_watch_hold`，`gate_action=hold_narrow_paper_and_escalate_weekly_ticket`
- `ETH-USD`：`green_watch_continue`，`gate_action=continue_paper_and_log_review`
- `SOL-USD`：`green_watch_continue`，`gate_action=continue_paper_and_log_review`

## 硬结论（hard verdict）
- 本轮把 Rank 2 从“有 weekly review seed”继续推进到“有可直接写回的 refresh writeback seed”。
- 这一步没有改写 seat verdict：
  - 仍是 `narrow paper pilot approved / paper-only`；
  - 仍不允许越级写成 live-ready。
- 同时把风险表达得更具体：
  - BTC 继续维持 red watch，必须带 ticket 升级；
  - ETH/SOL 才是 green continue。

## 对 desk 主线的意义
- 这是典型的 `Run 2` 最小接线推进：
  - 不新开候选，不扩研究框架；
  - 直接减少 `Rank 2` 的执行 gate（从“能 review”推进到“能 writeback”）。
- 也符合当前优先级：
  - `Scout Seat > tiny-live plumbing > 其他维护`。

## 网页可见落点
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/writeback_seed_report.html`
- `reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`（新增入口卡片）
- `reports/site/reading/trendline_alpha_scout/report.html`（新增 writeback seed 条目）

## Git / 提交
- 未提交。
- 原因：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
