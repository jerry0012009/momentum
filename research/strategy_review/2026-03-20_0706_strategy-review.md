# 2026-03-20 07:06 UTC bot2 strategy review

## 本轮先检查了什么
- repo status：`master`；`git status --short | wc -l = 1695`
- 最近 optimization logs：最新到 `2026-03-20_0652_rank111_event_clock_clean_replication.md`
- 最近 strategy review：最新到 `2026-03-20_0617_strategy-review.md`
- 当前 cron：
  - `bot3-momentum-auto-opt-13m` 下一拍在 `07:09 UTC`
  - `momentum-narrow-paper-lanes-20m` 最近一次 `06:52 UTC`
  - 本轮 bot2 review cron 正常触发
- EMA guardrail：再次执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果已回到 **`waiting_not_due`**
- EMA refresh history：最新一条为 **`2026-03-20 07:01 UTC / 创业板ETF 1d / active_primary / latest_completed_bar_utc=2026-03-20 00:00 UTC`**，说明刚才 A 股 primary due window 已被真实消化
- narrow-paper 托管：`manual_narrow_paper_last_run_summary.json @ 2026-03-20T06:52:36Z` 仍是 `new_closed_trades_appended=0`

## Desk verdict（直接回答本轮 5 个问题）

### 1. 当前 Paper Seat 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 体系内仍在跑的 secondary / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d` 仍只算 `shadow_watch`
- 独立 hosted paper continuity lanes（专属托管，不是新 seat）：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 结论：A 股 `07:00 UTC` due 已被 `07:01 UTC` 的 primary refresh 消化，当前整桌重新回到 **`Paper Seat = waiting_not_due`**。

### 2. Live Seat 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  - `basis dislocation short veto` 还没走到 `clean replication`
  - `alpha-beta abstain / profit-window` 连 `source intake` 都还没开始，还要先过 `ex-ante translation honesty gate`
  - `Rank 111 / abnormal-return event clock` 虽完成最小 clean replication，但当前只够 **`P1 weak candidate / evidence_pool`**，并未升到 `P2`
- 因此现在没有任何候选够资格抢 `Live Seat`。

### 3. Scout Seat 目前在复刻哪些 paper / repo 候选？
- 当前主点：**`basis dislocation short veto`**（下一手应做 `source intake + 两条轻量诚实守门`）
- 紧邻子点：**`alpha-beta abstain / profit-window`**（若 basis 失败，则做 `ex-ante translation honesty gate` 的 source intake）
- 已完成本轮前置快筛、但不再占主资源位：**`Rank 111 / abnormal-return event clock follow-up gate`**

### 4. 这些候选分别处在 P0 / P1 / P2 / P3 / P4 的哪一档？
- `basis dislocation short veto` = **`P0`**（`source intake next / fresh paper+public-data reserve`）
- `alpha-beta abstain / profit-window` = **`P0`**（`source intake next, but ex-ante translation honesty gate first / fresh paper+repo reserve`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`clean replication done / keep_P1 / budget used / evidence_pool`）
- `Rank 93 / 90 / 91 / 82 / 80 / 81` = **`P1`**（`older evidence_pool / budget used`）
- `Rank 110 / 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width` = **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 仍空，`P4` 仍空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 预期会快速返回 `waiting_not_due`，因为 `07:01 UTC` 的 A 股 primary refresh 已落账
2. **Run 2 = 若 EMA 仍 waiting_not_due，则只给 `basis dislocation short veto` 1 次 `source intake + 两条轻量诚实守门`**
3. **Run 3 = 若 basis guard-pass，则只给它 1 次最小 clean replication；若 basis hard-fail / exhausted，则切 `alpha-beta abstain / profit-window` 的 ex-ante honesty gate source intake**
   - 只有 fresh intake 这一层也 exhausted 后，才允许回退到 `tiny-live plumbing`
   - 除非出现新的 `due-now / overdue` paper refresh 或真实 `P3 status-changing event`，否则本轮之后不再继续分配 `P3 continuity` 预算

## 本轮最小必要更新
- 已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 明确写回 `07:01 UTC` 的 A 股 primary refresh 已落账
  - 明确写回 `Paper Seat` primary anchor 与 hosted paper lanes
  - 明确把 `Scout Seat` 从 `Rank 111` 切到 `basis dislocation short veto > alpha-beta abstain`
  - 明确维持 `Live Seat = 暂空`
  - 刷新 `Next 3 bot3 runs`

## 结论（一句话）
本轮不是“EMA 还在等，所以整桌继续等”，而是：**EMA 的 A 股 due 已在 07:01 UTC 被真实消化；Paper Seat 重新回到 waiting_not_due，Scout 主资源位现在应正式切到 `basis dislocation short veto`，Live Seat 继续留空。**
