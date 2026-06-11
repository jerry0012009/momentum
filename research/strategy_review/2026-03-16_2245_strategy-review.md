# 2026-03-16 22:45 UTC · Desk Board Review

## 本轮一句话判断

**这轮对 bot2 来说是按最新已生效作战板做的无额外换席巡检：`Paper Seat = EMA running paper / waiting_not_due / due_soon` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 当前已从“Rank 7 clean replication next”进一步推进到“`Rank 7 = park`、`Rank 8 = park`、`Rank 9 = source intake / clean replication next`”。因此当前 desk 的默认快线已经不是继续给 `Rank 2` 叠近义 wiring，而是优先让 `Rank 9 regime-switch stack` 进入最小 clean replication。**

## 当前 strongest evidence

1. **Paper Seat 已完成本轮应做的 due follow-up，并回到 waiting_not_due / due_soon**
   - `20:52 UTC` 的 `EMA due-now` follow-up 已真实落账：`美股 1d+1wk（SPY/QQQ/AAPL）` 已追加到 `latest_completed_bar_utc = 2026-03-16 00:00 UTC`；
   - 当前最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
     - `Crypto 1d+1wk（BTC/ETH/SOL）` 为最靠前的 `due_soon`（约 `3.1h` 后到点）
     - 其余 lane 仍是 `waiting_not_due`
   - 因此当前对 `Paper Seat` 的正确读法仍是：**`running paper pilot / waiting_not_due / due_soon`**。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍是 bench / 历史证据池，无 genuinely new blocker reduction；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 仍保留 narrow paper pilot 身份，但不再默认吃掉 Scout 第一优先级**
   - `Rank 2 combo_all` 仍是 **`narrow paper pilot approved`**；
   - 但它最近已连续补齐：
     - `ledger template`
     - `refresh seed`
     - `weekly review seed`
     - `writeback seed`
     - `continuity snapshot`
     - `refresh history`
   - 当前更诚实的 desk 读法是：
     - 它继续保留席位；
     - 但只有在出现真实 `append/review need` 或 verdict-changing check 时，才值得再次占用主资源；
     - 否则继续做它会重新滑回低杠杆 wiring。

4. **最新 fresh intake 链条已经推进到：Rank7 park，Rank8 park，Rank9 clean replication next**
   - `Rank 7 adaptive trend combo`：
     - 已完成 `source intake -> clean replication + Light Stability Pack`
     - 当前 hard verdict = **`park / evidence pool`**
     - 关键原因：`fixed_priority` 虽在 6~20bps 维持小幅正向，但 `no_trade_ratio≈98.6%`；而 `state_weighted_vote / equal_vote` 在 6bps 显著为负，参数邻域稳定性硬 fail
   - `Rank 8 EMA shielding / threshold + retest_hold`：
     - 已完成 `source intake -> clean replication + Light Stability Pack`
     - 当前 hard verdict = **`park / evidence pool`**
     - 关键原因：最佳变体 `retest_hold` 在 6bps 仍约 `-6.50%`、`positive_asset_ratio=0/3`，时间 / 参数 / 跨标的 / 成本四项全硬 fail
   - `Rank 9 regime-switch indicator stack / no-buy-downtrend gate`：
     - 当前已完成 **`source intake / clean-room spec`**
     - 当前最诚实位置是：**`clean replication next`**
     - 这是新的默认 fast-lane 入口

5. **其余候选继续维持 park**
   - `Rank 1 τ-band`：继续 `park`
   - `Rank 3 third-touch + EMA/MACD`：继续 `park`
   - `Rank 4 frozen-beta stat-arb`：继续 `park`
   - `Rank 4b rolling-beta 窄重开`：继续 `park`
   - `Rank 5 intraday TSMOM`：继续 `park`

## 当前 weakest / should-park lines

- 在 `Rank 2` 已连续补完多张 narrow-paper wiring 卡后，继续默认给它追加近义 wiring：应停止。
- 继续把 `Rank 7/8` 当作 active Scout 候选：应停止。
- 把 `Rank 2` 的 paper plumbing artifact误读成新的 alpha 证据或 live-ready：应停止。
- 在没有新 pair universe / 新数据源 / 新 spec 时重开 `Rank 4/4b`：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due / due_soon`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；本轮没有候选值得被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ **`narrow paper pilot approved`**
  3. `third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `park`
  4. `crypto pairs stat-arb`（原 frozen-beta 版本）→ `park`
  5. `Rank 4b crypto stat-arb reframe`（rolling-beta 窄重开）→ `park`
  6. `Rank 5 session-aware intraday TSMOM`（Li, Sakkas, Urquhart 2022）→ `park`
  7. `Rank 7 adaptive trend signal combination / state-weighted component vote`（Mugueta-Aguinaga et al. 2023）→ `park`
  8. `Rank 8 EMA shielding / threshold + retest_hold`（De Angelis et al. 2021）→ `park`
  9. `Rank 9 regime-switch indicator stack / no-buy-downtrend gate`（Naganjaneyulu et al. 2023）→ **`source intake / clean replication next`**

## 接下来优先级 Top 1~3

1. **优先让 `Rank 9 regime-switch stack` 进入最小 clean replication**
   - 第一刀重点先看：
     - `post_cost_return`
     - `positive_asset_ratio`
     - `trades_per_asset`
     - `no_trade_ratio`
     - `cost_survival`
   - 若最优版本只是靠 `no_trade_ratio` 飙升才守住收益，应直接 `park`。

2. **`Rank 2` 只在出现真实 append/review need 或 verdict-changing check 时再继续认领**
   - 它没有退出桌面；
   - 但当前默认不再是 Scout 第一优先级；
   - 若继续做，也只允许沿既有 narrow-paper history / continuity 链做最小 append。

3. **若 fresh intake 暂无合格动作，再回退 tiny-live plumbing / 其他维护**
   - 保持回退链干净；
   - 不让已 `park` 的旧候选重新抢主资源。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_2245_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不再额外改 `docs/TODO.md` 的 desk 口径**：当前顶板已经由最新 bot3 产物完成关键同步：
  - `Rank 7 -> park`
  - `Rank 8 -> park`
  - `Rank 9 -> source intake / clean replication next`
  - 当前回退链已明确为 `Rank 9 clean replication next；Rank 2 only on real append/review need`
- **不改 cron 频率**：当前 `bot2` / `bot3` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. `Rank 9` 当前只到了 `source intake / clean-room spec`，还没有 clean replication 结果；它是新的优先入口，但不是新的赢家。
2. `Rank 2` 仍是唯一 surviving 的 narrow-paper 候选；若后续新的 intake 都快速 `park`，桌面会再次回到“要不要给 Rank 2 更多默认资源”的问题。
3. `Paper Seat` 当前虽已回到 `waiting_not_due / due_soon`，但 `Crypto 1d+1wk` 距下一次 close 已不远；若 close 后未 append，需要再次临时切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮没有新的换席，但最新 Scout 排班已经彻底收紧：EMA 的 overdue follow-up 已做完，Paper Seat 回到 waiting_not_due / due_soon；Rank 7 与 Rank 8 都已 clean replication 后压回 park；当前新的默认入口只剩 `Rank 9 regime-switch stack -> clean replication next`，而 Rank 2 则退回“只在真实 append/review need 时再继续认领”的角色。**
