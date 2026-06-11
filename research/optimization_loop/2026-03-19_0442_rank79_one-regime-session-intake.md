# Rank 79 / one-regime-per-session source intake
- 时间：2026-03-19 04:42 UTC
- 席位：Scout Seat
- 主点：把 `one-regime-per-session shared allocation overlay` 冻结成 queue-facing source intake（只认领 1 个主点，无额外子点）

## 0. 开场检查
- `git status --short` 显示 repo 内外已有大量与本轮无关的脏文件；本轮只做选择性新增，不混提既有脏改。
- 最新 optimization logs：`0431 rank78-time-stability-scope-promotion` -> `0410 rank78-band-clean-replication` -> `0350 rank78-band-intake`。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：全 desk 仍无 `due-now / overdue`，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T04:33:36Z`：`new_closed_trades_appended=0`，因此当前没有新的 `P3 status-changing event` 抢走 Scout 主资源。

## 1. 本轮为什么不是继续碰 P3 continuity
当前 `Paper Seat = EMA / running paper / waiting_not_due` 没变；`Live Seat` 仍空；`P3 continuity` 既没有 due-now，也没有新的 append/open-position 异常。本轮合法动作仍应落在 `Scout Seat`，而不是回头围着 `Rank 17 / 2 / 29 / 32b` 做低频 continuity。

## 2. 先比较 active Scout 候选的边际价值
本轮只对当前最相关的 3 条重新排序：
1. **Rank 79 / one-regime-per-session overlay**
2. **fresh source：first-30m impulse quality gate（2026-03-19 04:26）**
3. **fresh source：realized-semivariance asymmetry gate（2026-03-19 03:43）**

更诚实的排序是：
`one-regime-per-session overlay > first-30m impulse quality gate > RS+/RS- asymmetry gate > 其他 fresh pool > Rank 35b > Rank 16b > tiny-live plumbing`

原因：
- `one-regime-per-session` 直接回答 desk 当前最核心的问题：**breakout/EMA continuation 与 Fib retest 是否不该在同一段 15m session 里一起抢同一笔钱**。这比继续给单条 lane 加 filter 更贴当前主线。
- `first-30m impulse quality` 很有价值，但它更像 continuation 放行阀，优先级仍低于先做 session 级预算分配。
- `RS+/RS- asymmetry` 更像 shared directional veto / sizing 扩展，价值在，但仍低于先处理 lane 冲突。

## 3. 两条轻量诚实守门
### 3.1 trade on / trade off
可清楚冻结：
- `continuation regime`：只放行 `breakout-short follow-up + EMA/PSAR continuation`
- `retest regime`：只放行 `Fib retest_hold`
- `unclear regime`：`no-trade / half-size`

### 3.2 lookahead / repaint / leakage
首轮规则可以避免明显数据泄漏：
- 只用当前 session 前 `4` 根 `15m`、opening range、session VWAP、ATR14 等当下可得数据；
- 执行统一 `signal 当根及之前数据 + next-bar open + no-overlap`；
- 禁止用整段 session 的后验结果、后续回踩是否成功、或 lane PnL 结果回填 regime 标签。

## 4. 本轮 hard verdict
**`Rank 79 / one-regime-per-session shared allocation overlay = guard-passed / admit_to_clean_replication_queue`**

这轮先不把它吹成 paper candidate，也不偷跑 heavy backtest。更诚实的状态只是：
- 它已经满足最小 source-intake 条件；
- 下一轮若 EMA 仍 `waiting_not_due`，值得拿 **1 次真正会改变 verdict 的最小 clean replication**；
- 若 clean replication 证明它只是靠大幅砍交易数变好看，就应快速压回 `park / evidence pool`。

## 5. 产物
- artifact：`reports/artifacts/literature/scout_rank79_one_regime_per_session_source_intake_card.csv`
- reader-facing page：`reports/site/reading/repo_scout/rank79_one_regime_per_session_source_intake.html`

## 6. 对 board 的最小更新口径
- `Rank 78` 已完成 `promote to narrow paper pilot approved (EMA-only suppression overlay)`，不再占用本轮 Scout 主资源。
- 当前新的 fresh Scout 顺序应写成：
  - `Rank 79 / one-regime-per-session overlay`
  - `fresh source：first-30m impulse quality gate`
  - `fresh source：RS+/RS- asymmetry gate`
  - `其他 fresh source`
- 下一轮若 `EMA` 仍 `waiting_not_due`，默认动作应是：给 `Rank 79` 1 次最小 clean replication，而不是回头磨旧 `P3 continuity`。
