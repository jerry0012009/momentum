# 2026-03-16 22:05 UTC · Desk Board Review

## 本轮一句话判断

**这轮不是换席，但作战板的 routing 已进一步落清：`Paper Seat = EMA` 不变，且上一轮 overdue follow-up 已完成，所以当前重新回到 `waiting_not_due / due_soon`；`Live Seat` 继续暂空；`Scout Seat` 方面，`Rank 2 combo_all` 仍保留 `narrow paper pilot approved` 身份，但默认主资源已经不该再继续堆它的近义 wiring，而应优先切到新的 `paper / repo based 5m / 15m crypto` intake。当前 fresh intake 的默认优先入口是：`Rank 7 adaptive trend combo -> clean replication next`。**

## 当前 strongest evidence

1. **Paper Seat 的 due follow-up 已完成，当前重新回到 waiting_not_due / due_soon**
   - `20:52 UTC` 已实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`；
   - `ema_paper_trading_refresh_history.csv` 已新增 1 条美股 completed-bar append：
     - `美股 1d+1wk（SPY/QQQ/AAPL）`
     - `latest_completed_bar_utc = 2026-03-16 00:00 UTC`
   - 当前最新 due guardrail 已无 `due-now / overdue` lane；
   - 最近的下一次 close 变为 `Crypto 1d+1wk`，约 `3.1h` 后到点；
   - 因此这轮对 `Paper Seat` 最诚实的读法是：**`running paper pilot / waiting_not_due / due_soon`**，不该继续重复美股 overdue follow-up。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍是 bench / 证据池，无 genuinely new blocker reduction；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 仍是唯一 surviving 的 narrow-paper 候选，但其默认优先级已被主动下调**
   - `Rank 2` 仍是 **`narrow paper pilot approved`**；
   - 它最近已连续补齐：
     - `ledger template`
     - `refresh seed rows`
     - `weekly review seed rows`
     - `refresh writeback seed`
     - `continuity snapshot`
     - `refresh history`
   - 这些产物说明：
     - `Rank 2` 的 paper-only 链路已经足够清楚；
     - 若下一轮没有真实 `append-ready refresh/review row`，或不会改变 paper verdict 的最小检查，再继续补近义 wiring 会违反当前 board 对边际价值的要求；
   - 因此当前更诚实的 desk 读法是：**`Rank 2` 继续保留席位，但默认不再吃掉 Scout 第一优先级。**

4. **新的 paper/repo Scout intake 已经重新启动，且当前默认优先入口已出现**
   - `Rank 5 session-aware intraday TSMOM` 已完成：
     - `source intake -> clean replication -> Light Stability Pack`
     - 但四项稳定性一起 fail，当前 hard verdict = `park`；
   - 紧接着，新的 `Rank 7 adaptive trend signal combination / state-weighted component vote` 已完成：
     - `source intake / implementation-ready clean-room spec`
     - 当前状态是 **`source intake / clean replication next`**；
   - 这条线的优势不在“已有收益结论”，而在于：
     - 不需要新数据源；
     - 不引入 ML 大框架；
     - 可直接复用当前 desk 已有 `EMA / Rank 2 confirmation / retest guard` 组件；
     - 下一轮可以直接进入最小 clean replication。

5. **其余候选继续维持 park**
   - `Rank 1 τ-band`：继续 `park`；
   - `Rank 3 third-touch + EMA/MACD`：继续 `park`；
   - `Rank 4 frozen-beta stat-arb`：继续 `park`；
   - `Rank 4b rolling-beta 窄重开`：继续 `park`；
   - `Rank 5 intraday TSMOM`：本轮正式纳入 `park / evidence pool`。

## 当前 weakest / should-park lines

- 在 `Rank 2` 已连续补完多张 narrow-paper wiring 卡后，继续默认给它追加近义 wiring：应停止。
- 把 `Rank 2` 的 paper plumbing artifact误读成新的 alpha 证据或 live-ready：应停止。
- 继续把 `Rank 5 intraday TSMOM` 当 active Scout 候选：应停止。
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
  7. `Rank 7 adaptive trend signal combination / state-weighted component vote`（Mugueta-Aguinaga et al. 2023）→ **`source intake / clean replication next`**

## 接下来优先级 Top 1~3

1. **优先让 `Rank 7 adaptive trend combo` 进入最小 clean replication**
   - 先按当前 clean-room spec 跑：
     - `fixed_priority`
     - `equal_vote`
     - `state_weighted_vote`
   - 第一刀重点先看：
     - `post_cost_return`
     - `no_trade_ratio`
     - `cost_survival`
     - `positive_asset_ratio`
   - 若只是靠 `no-trade_ratio` 飙升才守住收益，应直接 `park`。

2. **`Rank 2` 只在出现真实 append/review need 或 verdict-changing check 时再继续认领**
   - 不是退出桌面；
   - 但默认不再是 Scout 第一优先级；
   - 若继续做，也只允许沿既有 narrow-paper history / continuity 链做最小 append。

3. **若 fresh intake 暂无合格动作，再回退 tiny-live plumbing / 其他维护**
   - 保持回退链干净；
   - 不让已 `park` 的旧候选重新抢主资源。

## TODO / web / cron 的改动或建议

### 本轮已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 保留 `20:52 UTC` 的 EMA due-followup 完成结论；
  - 新增 `Rank 7 adaptive trend combo` 到 Scout 阶段表；
  - 在 `Next 3 bot3 runs` / `Run 2` 顺序里，明确 `Rank 7 clean replication first`。
- 新增本轮 review：`research/strategy_review/2026-03-16_2205_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 cron 频率：当前 `bot2` / `bot3` 状态都为 `running/ok`，节奏可先维持。
- 不改变 `Paper Seat` / `Live Seat` 的 seat assignment：当前变化主要是 **Scout 主资源顺序**，不是 seat 换人。

## 风险与不确定性

1. `Rank 7` 当前只到了 `source intake / clean-room spec`，还没有 clean replication 结果；它是新的优先入口，但不是新的赢家。
2. `Rank 2` 仍是唯一 surviving 的 narrow-paper 候选；如果后续新的 intake 都快速 `park`，桌面又会重新回到“是否继续给 Rank 2 更多默认资源”的问题。
3. `Paper Seat` 目前虽已回到 `waiting_not_due / due_soon`，但 `Crypto 1d+1wk` 距下一次 close 已不远；若 close 后又未 append，需要再次临时切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮真正的变化不是谁升格，而是 Scout 默认主资源终于从旧候选的连续 wiring 里抽出来了：EMA 的美股 due-followup 已经做完，所以 `Paper Seat` 回到 waiting_not_due；`Rank 2 combo_all` 继续保留 narrow paper pilot 身份，但不再默认吃掉第一优先级；当前新的默认入口改成 `Rank 7 adaptive trend combo -> clean replication next`。**
