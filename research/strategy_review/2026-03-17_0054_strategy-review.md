# 2026-03-17 00:54 UTC · Desk Board Review

## 本轮一句话判断

**这轮没有新的换席，也没有新的 promoted scout winner。当前 authoritative desk 读法已由最新 bot3 产物自行推进并保持稳定：`Paper Seat = EMA`，且 `00:20 UTC` 的 crypto due-now refresh 已真实消化，因此重新回到 `running paper pilot / waiting_not_due`；`Live Seat` 继续保持暂空；`Scout Seat` 方面，`Rank 13` 与 `Rank 14` 也都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`。因此这轮更像是一轮按最新已生效作战板执行的无额外换席巡检：默认顺序继续是 `Scout Seat（fresh paper/repo intake first） > Rank 2 narrow-paper append/review（仅限真实 append/review need） > tiny-live plumbing`。**

## 当前 strongest evidence

1. **Paper Seat 的 crypto due-now 窗口已被真实消化，当前重新回到 waiting_not_due**
   - `2026-03-17 00:20 UTC` 已实际执行：
     - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - `ema_paper_trading_refresh_history.csv` 已新增：
     - `Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-16 00:00 UTC`
   - 当前累计 completed-bar rows 已增至：`8`
   - 最新 due guardrail 已把 crypto 下一次 close 推到：`2026-03-18 00:00 UTC`
   - 因此当前对 `Paper Seat` 的正确读法已经不再是 `due-now / overdue follow-up window`，而是重新回到：
     - **`running paper pilot / waiting_not_due`**

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `Rank 2` 仍是 narrow-paper 范围内的 paper-only 候选；
   - `Rank 7 ~ Rank 14` 均已压回 `park / evidence pool`；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 13 已完成 clean replication + Light Stability Pack，并被诚实地压回 park**
   - `Rank 13 partial-moment asymmetry TSMOM gate` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`park / evidence pool`**；
   - 关键证据（winner=`pm_guard_100`，6bps/side）：
     - `mean_total_return ≈ -71.90%`
     - `positive_asset_ratio = 0/3`
     - `mean_trade_events ≈ 2027`
     - 时间 / 参数 / 跨标的 / 成本-交易数四项快筛全部硬 fail / watch
   - 因此这条线当前只保留作 `TSMOM risk-gate evidence`，不进入 `paper candidate pool`。

4. **Rank 14 也已完成 clean replication + Light Stability Pack，并被压回 park**
   - `Rank 14 cross-asset TSMOM confirmation gate` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`park / evidence pool`**；
   - 关键证据（winner=`peer_dual_gate`，6bps/side）：
     - `mean_total_return ≈ -87.28%`
     - `positive_asset_ratio = 0/3`
     - `mean_trade_events ≈ 3600`
     - 甚至比 `baseline_sign_mom ≈ -78.35%` 更差
     - 时间 / 参数 / 跨标的 / 成本-交易数四项快筛全部硬 fail / watch
   - 因此这条线当前只保留作 `cross-asset confirmation` 反例证据，不进入 `paper candidate pool`。

5. **Rank 2 仍保留 narrow paper pilot 身份，但默认继续退居二线**
   - `Rank 2 combo_all` 仍是唯一 surviving 的 narrow-paper 候选；
   - 但它近期已连续补完 `ledger template -> refresh seed -> weekly review seed -> writeback seed -> continuity snapshot -> refresh history`；
   - 当前更诚实的 desk 读法仍是：
     - 它继续保留席位；
     - 但只有在出现真实 `append/review need` 或 verdict-changing check 时，才值得再占主资源；
     - 否则默认优先给新的 `paper / repo based 5m / 15m crypto` fresh intake。

## 当前 weakest / should-park lines

- 继续把 `Rank 13 / 14` 当 active Scout 候选：应停止。
- 在 `Rank 2` 已连续补完多张 narrow-paper wiring 卡后，继续默认给它追加近义 wiring：应停止。
- 把 `TSMOM` 这一组 15m crypto 反例继续包装成“也许还差一点就能进 candidate”：当前不诚实。
- 在没有新 pair universe / 新数据源 / 新 spec 时重开 `Rank 4/4b`：继续 park。

## Desk verdict

- **Paper Seat：`EMA baseline family`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
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
  11. `Rank 11 Lo-style causal extrema pattern gate`（Lo et al. 2000 + SITONGRUC repo）→ `park`
  12. `Rank 12 averaged support/resistance zone + context gate`（Zhang & Zhou 2024）→ `park`
  13. `Rank 13 partial-moment asymmetry TSMOM gate`（Liu, Lu, Wang 2021）→ `park`
  14. `Rank 14 cross-asset TSMOM confirmation gate`（Pitkäjärvi, Suominen, Vaittinen 2020）→ `park`

## 接下来优先级 Top 1~3

1. **恢复新的 `paper / repo based 5m/15m crypto` fresh intake / clean replication**
   - 当前 `Paper Seat` 已回到 `waiting_not_due`；
   - `Rank 7 ~ Rank 14` 都已在当前口径下给出 `park`；
   - 因此当前最有边际价值的动作，仍是新的 fresh intake，而不是重跑已 park 候选。

2. **`Rank 2` 只在出现真实 append/review need 或 verdict-changing check 时再继续认领**
   - 它没有退出桌面；
   - 但当前默认不再是 Scout 第一优先级；
   - 若继续做，也只允许沿既有 narrow-paper history / continuity 链做最小 append。

3. **若 fresh intake 暂无合格动作，再回退 tiny-live plumbing / 其他维护**
   - 保持回退链干净；
   - 不让已 `park` 的旧候选重新抢主资源。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-17_0054_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不再额外改 `docs/TODO.md` 的 desk 口径**：当前顶板已经由最新 bot3 产物完成关键同步：
  - `Paper Seat` 的 crypto due-followup 已 resolved，重新回到 `waiting_not_due`
  - `Rank 13 -> park`
  - `Rank 14 -> park`
  - 当前回退链已明确为：`Scout Seat（fresh paper/repo intake first） > Rank 2 only on real append/review need > tiny-live plumbing`
- **不改 cron 频率**：当前 `bot2` / `bot3` / `bot7` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. 当前 `Rank 7 ~ Rank 14` 已在现有 fast-lane 口径下形成较长串 `park`；若下一轮继续只开低边际候选，容易出现“看着很忙但没有新 candidate”的假推进。
2. `Rank 2` 仍是唯一 surviving 的 narrow-paper 候选；若新的 intake 继续快速 park，桌面会再次回到“要不要给 Rank 2 更多默认资源”的问题。
3. `Paper Seat` 当前虽已回到 `waiting_not_due`，但 A 股下一次 close 已在数小时内；若 close 后未 append，需要再次临时切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮没有新的换席：EMA 的 crypto due-followup 已在 `00:20` 真实消化，Paper Seat 已回到 `waiting_not_due`；Rank 13 和 Rank 14 也都一轮内完成快筛并压回 `park`。因此当前默认排班应继续是：先开新的 `paper / repo based 5m/15m crypto` fresh intake，`Rank 2` 只在真实 append/review need 时再继续认领。**
