# 2026-03-16 21:25 UTC · Desk Board Review

## 本轮一句话判断

**这轮是无换席巡检，且维持上一轮刚收紧后的 routing：`Paper Seat = EMA` 不变，但当前仍应按 `due-now / overdue follow-up` 读；`Live Seat` 继续保持暂空；`Scout Seat` 仍只有 `Rank 2 combo_all` 保留前推资格，但在 `EMA` 的 due-now follow-up 没处理完之前，它不该继续占默认第一优先级。**

## 当前 strongest evidence

1. **Paper Seat 仍应按 due-now / overdue follow-up 读**
   - 当前 wall-clock 已明显超过 `美股 1d+1wk` 下一次 close（`2026-03-16 20:00 UTC`）；
   - 但最新可见 `ema_paper_trading_refresh_history.csv` 仍停在 `2026-03-16 00:01 UTC` 的 `Crypto 1d+1wk`；
   - `美股 1d+1wk（SPY/QQQ/AAPL）` 最新 completed bar 仍是 `2026-03-13 00:00 UTC`；
   - 因此当前最诚实读法仍不是 `waiting_not_due`，而是：**Paper Seat 仍在等待一次显式的 due-now / overdue 检查或新的 append 产物。**

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍是历史 bench 证据池，无 genuinely new blocker reduction；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 仍是唯一保留前推资格的 Scout 候选，但本轮新增的是 wiring 深化，不是 seat-level 升格**
   - `19:34 → 20:38` 它的 narrow paper wiring 已继续推进：
     - `ledger template`
     - `refresh seed rows`
     - `weekly review seed rows`
     - `refresh writeback seed`
     - `continuity snapshot`
   - 最新 `20:24 / 20:28 / 20:38` 三轮进一步说明：
     - BTC 必须保留 `red watch / false_break_watch / blocked_by_red_watch`
     - ETH / SOL 当前是 `green / append_ready`
   - 这使 Rank 2 的 paper 链路更可执行，但**没有**改变它的 seat verdict：
     - 仍是 `narrow paper pilot approved / paper-only`
     - 仍不是 `Live Seat / tiny-live ready`。

4. **其余候选继续维持 park**
   - `Rank 1 τ-band`：继续 `park`；
   - `Rank 3 third-touch + EMA/MACD`：继续 `park`；
   - `Rank 4 frozen-beta stat-arb`：继续 `park`；
   - `Rank 4b rolling-beta 窄重开`：继续 `park`。

## 当前 weakest / should-park lines

- 在 `EMA due-now / overdue` follow-up 尚未落产物前，继续把默认第一优先级放在 `Rank 2` wiring：应暂停。
- 继续把 `Rank 2` 的 wiring 误读成新的 alpha 证据或 live-ready：应停止。
- 继续把 `Rank 4b` 当作 active Scout 候选：应停止。
- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。

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

1. **继续优先 `Run 1 / EMA paper ledger`**
   - 当前默认动作仍应是：
     - 做 `EMA due-now / overdue` 检查；
     - 若有新 completed bar，append ledger / refresh / review；
     - 若仍无可 append completed bar，也要把这个结果写成显式检查产物。

2. **只有 Paper Seat follow-up 处理完，才回到 `Rank 2` 的 narrow paper continuity append**
   - 当前最自然的下一步是：
     - 在现有 continuity snapshot 基础上继续补 `refresh / review append`；
     - 而不是再补 admission / receipt / closeout 近义文档。

3. **若 Paper Seat 也暂时无可执行 append，再回退 tiny-live plumbing / 其他维护**
   - 保持回退链干净，不让已 park 的旧候选重新抢资源。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_2125_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不改 `docs/TODO.md`**：上一轮已把关键 routing 变化写入顶板；本轮没有新的 desk-level 改判。
- **不改 cron 频率**：当前 `bot2` / `bot3` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. 当前 `EMA due-now / overdue` 的判断仍基于：wall-clock 已过 `20:00 UTC`，但最新可见美股 ledger 仍未 append；若新的 refresh 产物很快出现，这轮 routing 会自然恢复为常规 `Paper -> Scout` 节奏。
2. `Rank 2` 当前连续新增的都是 paper plumbing artifact，而不是新的 alpha 证据；因此它虽然仍是唯一 surviving Scout 候选，但仍需继续保留 `BTC red watch / false_break_watch / idle-gap / time-pocket` 等诚实 watch 位。
3. 当前活跃可前推的 Scout 候选过于集中在 `Rank 2`，这让 desk 更干净，但也要求 bot2 持续防止主资源重新滑回低杠杆文档打磨。

## 本轮一句话结论（给 Jerry）

**这轮没有新的换席：EMA 继续坐 Paper Seat，但当前仍应按 due-now / overdue follow-up 读；Live Seat 继续暂空；Scout 方面仍只有 Rank 2 保留前推资格，不过它这轮新增的依旧只是 paper wiring 深化，不足以盖过 Paper Seat 在 `20:00 UTC` 之后的默认优先级。**
