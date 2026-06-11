# 2026-03-16 20:45 UTC · Desk Board Review

## 本轮一句话判断

**这轮不是换席，但默认排班确实变了：`Paper Seat = EMA` 不变，`Live Seat` 继续暂空，`Scout Seat` 仍只有 `Rank 2 combo_all` 保留前推资格；真正变化是——当前 wall-clock 已经过 `美股 1d+1wk` 的下一次 close（`2026-03-16 20:00 UTC`），而最新可见 EMA ledger 还没有 append 到新的美股 completed bar，所以本轮起默认顺序应临时切回 `Run 1 / Paper Seat continuation first`。在新的 `due-now / overdue` 检查或 append 产物出现前，不该继续把默认主资源放在 Rank 2 wiring 上。**

## 当前 strongest evidence

1. **Paper Seat 重新进入 due-now / overdue follow-up 窗口**
   - 当前时间已过 `2026-03-16 20:00 UTC`；
   - 但最新可见 `ema_paper_trading_refresh_history.csv` 仍停在 `2026-03-16 00:01 UTC` 的 `Crypto 1d+1wk`；
   - `美股 1d+1wk（SPY/QQQ/AAPL）` 最新 completed bar 仍是 `2026-03-13 00:00 UTC`；
   - 这说明当前最诚实的读法不再是 `waiting_not_due`，而是：**在新的 due-now / overdue 检查或 append 产物出现前，Paper Seat 应重新拿回默认优先级。**

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍是历史 bench 证据池，无 genuinely new blocker reduction；
   - 因此当前 desk call 仍是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 仍是唯一保留前推资格的 Scout 候选，但它本轮应退到 Paper Seat follow-up 之后**
   - 当前顶板已明确：`Rank 2` 仍是 **`narrow paper pilot approved`**；
   - `19:34 → 20:38` 它的 paper wiring 又连补了几格：
     - `ledger template`
     - `refresh seed rows`
     - `weekly review seed rows`
     - `refresh writeback seed`
     - `continuity snapshot`
   - 这些产物都说明：
     - 若继续认领 `Rank 2`，它确实已经不该回头打磨 admission / receipt / closeout 近义文档；
     - 但在当前 `EMA` 已进入 due-now / overdue follow-up 窗口时，`Rank 2` 应先让位给 `Run 1 / Paper Seat continuation`。

4. **其余候选继续维持 park**
   - `Rank 1 τ-band`：继续 `park`；
   - `Rank 3 third-touch + EMA/MACD`：继续 `park`；
   - 原版 `Rank 4 frozen-beta stat-arb`：继续 `park`；
   - `Rank 4b rolling-beta 窄重开`：已在 `18:53` 的 `time stability` 后更诚实地压回 `park`。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 在当前 `EMA` 已进入 due-now / overdue follow-up 窗口后，仍默认把主资源放在 `Rank 2` 的 narrow paper wiring：应暂停。
- 继续把 `Rank 4b` 当作 active Scout 候选：应停止。
- 继续回头打磨 `Rank 2` 的 admission / receipt / closeout 近义文档：应停止。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / due-now-overdue follow-up window`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；本轮没有候选值得被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ **`narrow paper pilot approved`**
  3. `third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `park`
  4. `crypto pairs stat-arb`（原 frozen-beta 版本）→ `park`
  5. `Rank 4b crypto stat-arb reframe`（rolling-beta 窄重开）→ `park`

## 接下来优先级 Top 1~3

1. **先回到 `Run 1 / EMA paper ledger`**
   - 当前最自然的动作是：
     - 先做 `EMA due-now / overdue` 检查；
     - 若有新 completed bar，可直接 append ledger / refresh / review；
     - 若仍无可 append completed bar，也应把这个“为什么没有”的结果写成显式检查产物，而不是继续默认跳过。

2. **只有当 Paper Seat follow-up 完成后，才回到 `Rank 2 narrow paper wiring`**
   - 到那时 `Rank 2` 最自然的下一步仍是：
     - `weekly_review_status / operator_action / refresh writeback`
     - 或继续沿同一张 continuity snapshot append；
   - 但它现在不是默认第一优先级。

3. **若 Paper Seat 也暂时无可执行 append，再回退 tiny-live plumbing / 其他维护**
   - 让回退链继续保持干净，避免已 park 的旧候选重新占默认主资源。

## TODO / web / cron 的改动或建议

### 本轮已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 在 `Paper Seat` 下补了 `20:45 UTC` 的 due-now / overdue 注记；
  - 在 `Next 3 bot3 runs` 的当前窗口说明里，把默认顺序显式切回 `Run 1 / Paper Seat continuation first`。
- 新增本轮 review：`research/strategy_review/2026-03-16_2045_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 cron 频率：当前 `bot2` / `bot3` 状态都为 `running/ok`，节奏可先维持。
- 不改变 `Live Seat` 与 `Scout Seat` 候选阶段表：当前变化主要是**排班先后顺序**，不是新的 seat promotion。

## 风险与不确定性

1. 当前 `EMA due-now / overdue` 的判断，是基于：wall-clock 已过 `20:00 UTC`，但最新可见美股 ledger 仍未 append；后续若很快出现新的 refresh 产物，这轮 routing 会自然回到之前的 `Paper -> Scout` 正常节奏。
2. `Rank 2` 当前新增的是 paper plumbing artifact，不是新的 alpha 证据；因此它虽然仍是唯一 surviving Scout 候选，但不应在 Paper Seat due-now 时抢默认第一优先级。
3. 若 bot3 在 due-now 窗口里继续按旧的 `waiting_not_due` 口径工作，说明 desk state 识别还有滞后；这需要 bot2 在 review 中持续纠偏。

## 本轮一句话结论（给 Jerry）

**这轮真正的变化不是谁升格，而是默认顺序切回来了：现在已经过了 `20:00 UTC`，而 EMA 的美股 ledger 还没看到新的 append，所以当前默认主资源应先回 `Paper Seat` 做 due-now / overdue follow-up；只有这一步处理完，才轮到 `Rank 2 combo_all` 继续 narrow paper wiring。**
