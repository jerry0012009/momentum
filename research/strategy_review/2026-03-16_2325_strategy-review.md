# 2026-03-16 23:25 UTC · Desk Board Review

## 本轮一句话判断

**这轮不是新的换席，而是对 22:45 之后连续 3 张 bot3 新卡做的 seat-level 收口确认：`Paper Seat = EMA running paper / waiting_not_due / due_soon` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 则已从“`Rank 9 clean replication next`”进一步推进到“`Rank 9 = park`、`Rank 10 = park`、`Rank 11 = source intake / clean replication next`”。因此当前 desk 的默认 fast lane 已经再次前推：不是继续给 `Rank 2` 叠 narrow-paper wiring，也不是重跑 `Rank 7/8/9/10`，而是优先让 `Rank 11 Lo-style causal extrema pattern gate` 进入最小 clean replication。**

## 当前 strongest evidence

1. **Paper Seat 仍是 EMA，且当前仍处于 waiting_not_due / due_soon**
   - `20:52 UTC` 的美股 due-followup 已真实落账，`美股 1d+1wk（SPY/QQQ/AAPL）` 已追加到 `latest_completed_bar_utc = 2026-03-16 00:00 UTC`；
   - 当前最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
     - `Crypto 1d+1wk（BTC/ETH/SOL）` 为最近的 `due_soon` lane；
     - A 股 / 美股其余 lane 仍是 `waiting_not_due`；
   - 因此当前对 `Paper Seat` 的正确读法仍然是：**`running paper pilot / waiting_not_due / due_soon`**，而不是重新切回 `due-now / overdue`。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `Rank 2` 仍是 narrow-paper 范围内的 paper-only 候选；
   - `Rank 11` 目前还只到 `source intake / clean replication next`；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 9 已完成 clean replication + Light Stability Pack，并被诚实地压回 park**
   - `Rank 9 regime-switch indicator stack / no-buy-downtrend gate` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`park / evidence pool`**；
   - 关键证据：
     - `winner_variant = regime_gate_only`
     - `mean_total_return ≈ -10.28% @ 6bps/side`
     - `positive_asset_ratio = 1/3`
     - 时间 / 参数 / 跨标的 / 成本-交易数四项快筛全部硬 fail；
     - `regime_plus_psar_rsi` 甚至没有形成可交易样本，且已修掉“零交易版本误当 winner”的排序 bug。
   - 因此当前不该再把 `Rank 9` 写成 `clean replication next` 或 `paper candidate hopeful`。

4. **Rank 10 也已完成 clean replication + Light Stability Pack，并被压回 park**
   - `Rank 10 volatility-managed EMA / ATR sizing overlay` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`park / evidence pool`**；
   - 关键证据：
     - `atr_clip_050_150 @ 6bps/side mean_total_return ≈ -26.21%`
     - `positive_asset_ratio = 0/3`
     - `mean_max_drawdown ≈ -35.03%`
     - 对照 `baseline_100` 也没有被改善，反而更差；
     - 时间 / 参数 / 跨标的 / 成本-交易数四项快筛全部未过。
   - 因此这条线当前最多只算 `EMA risk-layer counterexample`，不进入 `paper candidate pool`。

5. **当前新的 fresh intake 已推进到 Rank 11，且它是最新默认 fast-lane 入口**
   - `Rank 11 Lo-style causal extrema pattern gate` 已完成：
     - `source intake / clean-room spec`
   - 当前最诚实位置是：**`source intake / clean replication next`**；
   - 它当前边际价值高于继续磨 `Rank 2` 或重看 `Rank 7/8/9/10`，因为它同时满足：
     - repo-based / paper-based
     - 15m crypto 直接可落
     - 不需要新数据源
     - 规则可清楚写成 `trade on / trade off`
     - 已预先写进 lookahead / repaint guardrail
   - 所以当前新的 Scout 默认入口应明确切到：**`Rank 11 clean replication next`**。

6. **Rank 2 仍保留 narrow paper pilot approved 身份，但当前继续退居二线**
   - `Rank 2 combo_all` 仍是唯一 surviving 的 narrow-paper 候选；
   - 但它近期已连续补完 `ledger template -> refresh seed -> weekly review seed -> writeback seed -> continuity snapshot -> refresh history`；
   - 当前更诚实的 desk 读法仍是：
     - 它继续保留席位；
     - 但只有在出现真实 `append/review need` 或 verdict-changing check 时，才值得再占主资源；
     - 否则默认优先给新的 paper/repo fast-lane intake。

## 当前 weakest / should-park lines

- 继续把 `Rank 7 / 8 / 9 / 10` 当 active Scout 候选：应停止。
- 在 `Rank 2` 已连续补完多张 narrow-paper wiring 卡后，继续默认给它追加近义 wiring：应停止。
- 把 `Rank 10` 误读成“EMA risk overlay 还差一点就能接 paper”：应停止。
- 在没有新 spec / 新数据源 / 新 market pocket 时重开 `Rank 4/4b`：继续 park。

## Desk verdict

- **Paper Seat：`EMA baseline family`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due / due_soon`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；本轮没有候选值得被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `Rank 1 τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `Rank 2 volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ **`narrow paper pilot approved`**
  3. `Rank 3 third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `park`
  4. `Rank 4 crypto pairs trading / stat-arb`（原 frozen-beta 版本）→ `park`
  5. `Rank 4b crypto stat-arb reframe`（rolling-beta 窄重开）→ `park`
  6. `Rank 5 session-aware intraday TSMOM`（Li, Sakkas, Urquhart 2022）→ `park`
  7. `Rank 7 adaptive trend signal combination / state-weighted component vote`（Mugueta-Aguinaga et al. 2023）→ `park`
  8. `Rank 8 EMA shielding / threshold + retest_hold`（De Angelis et al. 2021）→ `park`
  9. `Rank 9 regime-switch indicator stack / no-buy-downtrend gate`（Naganjaneyulu et al. 2023）→ `park`
  10. `Rank 10 volatility-managed EMA / ATR sizing overlay`（Moreira & Muir 2017 + ATR proxy）→ `park`
  11. `Rank 11 Lo-style causal extrema pattern gate`（Lo et al. 2000 + SITONGRUC repo）→ **`source intake / clean replication next`**

## 接下来优先级 Top 1~3

1. **优先让 `Rank 11 Lo-style causal extrema pattern gate` 进入最小 clean replication**
   - 第一刀重点先看：
     - `post_cost_return`
     - `positive_asset_ratio`
     - `trades_per_asset`
     - `no_trade_ratio`
     - `false_break_proxy`
     - `cost_survival`
   - 若最优版本只是靠极端少交易或需要大量主观 patch 才能成立，应直接 `park`。

2. **`Rank 2` 只在出现真实 append/review need 或 verdict-changing check 时再继续认领**
   - 它没有退出桌面；
   - 但当前默认不再是 Scout 第一优先级；
   - 若继续做，也只允许沿既有 narrow-paper history / continuity 链做最小 append。

3. **若 fresh intake 暂无合格动作，再回退 tiny-live plumbing / 其他维护**
   - 保持回退链干净；
   - 不让已 `park` 的旧候选重新抢主资源。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_2325_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不再额外改 `docs/TODO.md` 的 desk 口径**：当前顶板已经由最新 bot3 产物完成关键同步：
  - `Rank 9 -> park`
  - `Rank 10 -> park`
  - `Rank 11 -> source intake / clean replication next`
  - 当前回退链已明确为 `Rank 11 clean replication next；Rank 2 only on real append/review need`
- **不改 cron 频率**：当前 `bot2` / `bot3` / `bot7` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. `Rank 11` 当前只到了 `source intake / clean-room spec`，还没有 clean replication 结果；它是新的优先入口，但不是新的赢家。
2. `Rank 2` 仍是唯一 surviving 的 narrow-paper 候选；若后续新的 intake 继续快速 park，桌面会再次回到“要不要给 Rank 2 更多默认资源”的问题。
3. `Paper Seat` 当前虽已回到 `waiting_not_due / due_soon`，但 `Crypto 1d+1wk` 距下一次 close 已不远；若 close 后未 append，需要再次临时切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮没有新的换席，但 Scout 默认入口又往前推了一格：`Rank 9` 和 `Rank 10` 都已经 clean replication 后压回 park，当前新的默认入口只剩 `Rank 11 Lo-style causal extrema pattern gate -> clean replication next`；而 `Rank 2` 则继续退回“只在真实 append/review need 时再继续认领”的角色。**
