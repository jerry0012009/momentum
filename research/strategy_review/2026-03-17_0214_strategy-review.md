# 2026-03-17 02:14 UTC · Desk Board Review

## 本轮一句话判断

**这轮没有新的换席，也没有新的 promoted scout winner。当前 authoritative desk 读法在 01:34 基础上继续成立：`Paper Seat = EMA`，且 `00:20 UTC` 的 crypto due-now refresh 已真实消化，因此继续维持 `running paper pilot / waiting_not_due`；`Live Seat` 继续保持暂空；`Scout Seat` 方面，`Rank 16 ORB threshold + protective closing session gate` 也已在 `source intake -> clean replication + Light Stability Pack` 后被诚实压回 `park / evidence pool`。因此当前默认顺序仍然是：**新的 `paper / repo based 5m/15m crypto` fresh intake first，`Rank 2` 只在真实 append/review need 或 verdict-changing check 时再继续认领。** 本轮不需要再改顶板口径。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due，不需要再临时切回 due-followup**
   - `2026-03-17 00:20 UTC` 已实际执行：
     - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - `ema_paper_trading_refresh_history.csv` 已新增：
     - `Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-16 00:00 UTC`
   - 当前累计 completed-bar rows 已增至：`8`
   - 最新 due guardrail 已把 crypto 下一次 close 推到：`2026-03-18 00:00 UTC`
   - A 股下一次 close 仍在 `2026-03-17 07:00 UTC`，当前还只是 `waiting_not_due`
   - 因此当前对 `Paper Seat` 的正确读法仍是：
     - **`running paper pilot / waiting_not_due`**

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `Rank 2` 仍是 narrow-paper 范围内的 paper-only 候选；
   - `Rank 7 ~ Rank 16` 均已压回 `park / evidence pool`；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 16 已完成 clean replication + Light Stability Pack，并被诚实地压回 park**
   - `Rank 16 ORB threshold + protective closing session gate` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`park / evidence pool`**；
   - 关键证据（相对最不差变体=`confirm1_outside`，6bps/side）：
     - `mean_total_return ≈ -7.51%`
     - `positive_asset_ratio = 0/3`
     - `mean_trades ≈ 154.7`
   - 其余对照：
     - `retest_hold ≈ -8.36%`
     - `confirm2of3_outside ≈ -9.10%`
     - `protective_close_overlay ≈ -21.50%`
     - `raw_orb ≈ -35.11%`
   - 更重要的是：
     - 参数邻域没有一档转正
     - 跨标的 `0/3` 为正
     - 成本从 `6bps -> 20bps` 继续恶化到约 `-39.98%`
   - 一句话：**它不是“少做交易显得更稳”，而是“做了不少交易仍整体亏损”，因此应及时 park。**

4. **Rank 15 继续维持 park，不存在 re-open 价值**
   - `Rank 15 support/resistance regime-switch confirmation gate`：
     - `mean_total_return ≈ -1.94%`
     - `positive_asset_ratio = 1/3`
     - `mean_no_trade_ratio ≈ 81.73%`
     - 仍然四项快筛硬 fail
   - 它看起来是当前串里“亏得没那么多”的一条，但不等于接近 `paper candidate`
   - 当前更诚实读法仍是：确认层让交易更稀，但没有带来足够强的 post-cost / cross-asset / stability 证据。

5. **Rank 2 仍保留 narrow paper pilot 身份，但默认继续退居二线**
   - `Rank 2 combo_all` 仍是唯一 surviving 的 narrow-paper 候选；
   - 但它近期已连续补完 `ledger template -> refresh seed -> weekly review seed -> writeback seed -> continuity snapshot -> refresh history`；
   - 当前更诚实的 desk 读法仍是：
     - 它继续保留席位；
     - 但只有在出现真实 `append/review need` 或 verdict-changing check 时，才值得再占主资源；
     - 否则默认优先给新的 `paper / repo based 5m / 15m crypto` fresh intake。

## 当前 weakest / should-park lines

- 继续把 `Rank 16` 当 active Scout 候选：应停止。
- 在 `Rank 2` 已连续补完多张 narrow-paper wiring 卡后，继续默认给它追加近义 wiring：应停止。
- 把 `Rank 15/16` 这种“亏损收窄但没过稳定性线”的候选误读成接近 `paper candidate`：当前不诚实。
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
  15. `Rank 15 support/resistance regime-switch confirmation gate`（Henderson, Jacka, Liu, Maeda 2021/2025）→ `park`
  16. `Rank 16 ORB threshold + protective closing session gate`（Wu, Syu, Lin, Ho 2021；Syu et al. 2020）→ `park`

## 接下来优先级 Top 1~3

1. **继续新的 `paper / repo based 5m/15m crypto` fresh intake / clean replication**
   - 当前 `Paper Seat` 已是 `waiting_not_due`；
   - `Rank 7 ~ Rank 16` 都已在当前 fast-lane 口径下给出 `park`；
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
- 新增本轮 review：`research/strategy_review/2026-03-17_0214_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不再额外改 `docs/TODO.md` 的 desk 口径**：当前顶板已经由最新 bot3 产物完成关键同步：
  - `Paper Seat` 继续是 `waiting_not_due`
  - `Rank 16 -> park`
  - 当前回退链继续是：`fresh paper/repo intake first > Rank 2 only on real append/review need > tiny-live plumbing`
- **不改 cron 频率**：当前 `bot2` / `bot3` / `bot7` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. 当前 `Rank 7 ~ Rank 16` 已形成更长串 `park`；若下一轮继续只开低边际候选，容易继续出现“看起来很忙但没有新 candidate”的假推进。
2. `Rank 2` 仍是唯一 surviving 的 narrow-paper 候选；若新的 intake 继续快速 park，桌面会再次回到“要不要给 Rank 2 更多默认资源”的问题。
3. `Paper Seat` 当前虽已回到 `waiting_not_due`，但 A 股下一次 close 已在数小时内；若 close 后未 append，需要再次临时切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮没有新的换席：EMA 继续是 `waiting_not_due`；`Rank 16` 也已 clean replication 后压回 `park`。所以当前默认排班仍应继续是：先开新的 `paper / repo based 5m/15m crypto` fresh intake，`Rank 2` 只在真实 append/review need 时再继续认领。**
