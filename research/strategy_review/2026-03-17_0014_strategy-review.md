# 2026-03-17 00:14 UTC · Desk Board Review

## 本轮一句话判断

**这轮不是换席，但当前默认排班确实要临时切回 `Run 1 / Paper Seat continuation first`。原因不是 Scout 又冒出更强新候选，而是 `Crypto 1d+1wk（BTC/ETH/SOL）` 已经过 `2026-03-17 00:00 UTC` close，而最新可见 `ema_paper_trading_refresh_history.csv` 仍停在 `latest_completed_bar_utc=2026-03-15 00:00 UTC`，尚未出现新的 crypto completed-bar append。与此同时，`Rank 11` 与 `Rank 12` 也都已完成 clean replication + Light Stability Pack 并压回 `park / evidence pool`。因此这轮最诚实的 desk 读法是：`Paper Seat = EMA` 不变，但当前临时进入 `due-now / overdue follow-up window`；`Live Seat` 继续暂空；`Scout Seat` 方面 `Rank 2 combo_all` 仍保留 `narrow paper pilot approved`，但默认不再吃掉主资源；在 crypto lane 完成补账前，默认顺序应先是 `Paper Seat`，而不是新的 Scout intake。**

## 当前 strongest evidence

1. **Paper Seat 当前应临时切回 due-now / overdue follow-up**
   - 当前 wall-clock 已过：`Crypto 1d+1wk（BTC/ETH/SOL）` 的 `2026-03-17 00:00 UTC` close；
   - 但最新可见 `ema_paper_trading_refresh_history.csv` 里，crypto 最新 completed bar 仍是：
     - `latest_completed_bar_utc = 2026-03-15 00:00 UTC`
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍停留在 close 前生成的 `due_soon` 读法，没有反映 close 后状态；
   - 因此当前更诚实的判断不是继续写 `waiting_not_due / due_soon`，而是：
     - **`running paper pilot / due-now-overdue follow-up window`**
   - 下一轮默认动作不应再优先新的 Scout intake，而应先确认 crypto lane 是否真实漏跑 refresh。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `Rank 2` 仍是 narrow-paper 范围内的 paper-only 候选；
   - `Rank 7 ~ Rank 12` 都已经给出 `park`；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 11 已完成 clean replication + Light Stability Pack，并被诚实地压回 park**
   - `Rank 11 Lo-style causal extrema pattern gate` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`park / evidence pool`**；
   - 关键证据（winner=`double_bottom_reclaim`，6bps/side）：
     - `mean_total_return ≈ -4.33%`
     - `positive_asset_ratio = 0/3`
     - 时间 / 参数 / 跨标的 / 成本-交易数四项快筛全部硬 fail
   - 因此这条线当前不再是 `clean replication next`，也不进入 `paper candidate pool`。

4. **Rank 12 也已完成 clean replication + Light Stability Pack，并被压回 park**
   - `Rank 12 averaged support/resistance zone + context gate` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
   - 当前 hard verdict = **`park / evidence pool`**；
   - 关键证据（winner=`averaged_zone_context_gate`，6bps/side）：
     - `mean_total_return ≈ -4.34%`
     - `positive_asset_ratio = 1/3`
     - `20bps ≈ -11.56%`
     - 时间 / 参数 / 跨标的 / 成本-交易数四项快筛均硬 fail
   - 因此这条线当前也不应继续占用默认主资源位。

5. **Scout Fast Lane 当前没有新的 active winner，默认 fresh intake 也应暂时让位给 Paper Seat due follow-up**
   - `Rank 7 / 8 / 9 / 10 / 11 / 12` 已全部完成 fast-lane 闭环，并压回 `park / evidence pool`；
   - `Rank 2 combo_all` 仍保留 **`narrow paper pilot approved`**，但只在出现真实 `append/review need` 或 verdict-changing check 时再继续认领；
   - 这意味着在 crypto lane 完成补账前，当前更高优先级不是继续开新 intake，而是先处理当前 `Paper Seat` 的 due-now / overdue follow-up。

## 当前 weakest / should-park lines

- 继续把 `Rank 11 / 12` 当 active Scout 候选：应停止。
- 在 `Rank 2` 已连续补完多张 narrow-paper wiring 卡后，继续默认给它追加近义 wiring：应停止。
- 在 `Crypto 1d+1wk` close 已过且尚未 append 的窗口里，继续把主资源放在新的 Scout intake：当前不诚实。
- 在没有新 pair universe / 新数据源 / 新 spec 时重开 `Rank 4/4b`：继续 park。

## Desk verdict

- **Paper Seat：`EMA baseline family`**
- **Paper Seat 当前读法：`running paper pilot / due-now-overdue follow-up window`**
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

## 接下来优先级 Top 1~3

1. **先执行 `Run 1 / EMA paper continuation`，核实 crypto lane 的 due-now / overdue follow-up**
   - 先确认：
     - 是否真实漏跑 refresh
     - 是否已经存在新的 crypto completed-bar 但尚未写回 ledger
     - 是否需要重新执行 `run_ema_paper_trading_guarded_refresh.py --require-due`
   - 在这步完成前，不应继续默认把主资源放在新的 Scout intake。

2. **若 crypto lane 完成补账或被证实并未真正 due，再恢复新的 `paper / repo based 5m/15m crypto` fresh intake**
   - 当前 `Rank 7 ~ Rank 12` 都已 park；
   - 所以若 `Paper Seat` 不再 due，Scout Fast Lane 应重新切回新的 fresh intake，而不是反复重跑已 park 候选。

3. **`Rank 2` 只在出现真实 append/review need 或 verdict-changing check 时再继续认领**
   - 它没有退出桌面；
   - 但当前默认不再是 Scout 第一优先级；
   - 若继续做，也只允许沿既有 narrow-paper history / continuity 链做最小 append。

## TODO / web / cron 的改动或建议

### 本轮已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 在 `Paper Seat` 下补充 `2026-03-17 00:14 UTC` 的 due-now / overdue 注记；
  - 在 `Next 3 bot3 runs` 当前窗口说明里，把默认顺序临时切回 `Run 1 / Paper Seat continuation first`。
- 新增本轮 review：`research/strategy_review/2026-03-17_0014_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不改 cron 频率**：当前 `bot2` / `bot3` / `bot7` 状态都为 `running/ok`，节奏可先维持。
- **不改 seat assignment**：当前变化主要是 `Paper Seat` 的时钟优先级临时回升，不是 seat 换人。

## 风险与不确定性

1. 当前 `ema_paper_trading_due_guardrail_snapshot.csv` 仍是 close 前生成的读法，因此不能直接拿它的 `due_soon` 文字继续当本轮最终判断。
2. 目前看到的是“close 已过，但 ledger 还没 append”；还不能仅凭这一点断言一定漏跑，仍需先做实际 due-followup 核实。
3. 若 crypto lane 很快补账，当前 routing 又会恢复为 `Scout Seat（fresh intake first） > Rank 2 only on real append/review need > tiny-live plumbing`。

## 本轮一句话结论（给 Jerry）

**这轮真正的变化不是又 park 了哪条 Scout，而是 `Crypto 1d+1wk` 的 close 已经过了、但 EMA ledger 还没 append，所以当前默认排班必须临时切回 `Run 1 / Paper Seat continuation first`；在 crypto lane 完成补账前，不该继续把主资源放在新的 Scout intake。**
