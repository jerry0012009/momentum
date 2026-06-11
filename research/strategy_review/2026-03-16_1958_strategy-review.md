# 2026-03-16 19:58 UTC · Desk Board Review

## 本轮一句话判断

**这轮没有新的 seat-level 改判：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 继续收缩成 `Rank 2 combo_all = narrow paper pilot approved` 为唯一仍保留前推资格的候选，`Rank 1 / Rank 3 / 原 Rank 4 / Rank 4b` 全部维持 `park / evidence pool`。本轮真正新增的不是新候选，而是 `Rank 2` 的 narrow paper wiring 又往前走了两格：先落了 `ledger template`，又落了 `refresh seed rows`，因此当前更像是在把它从“可 paper”推进到“可按同一张账本开始 refresh / review 演练”。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示当前没有 `due-now / overdue` lane；
   - 当前 `EMA` 继续是 running paper，但本窗口只该做 waiting 状态维护与 next-close 核对，不应回到默认 bot3 主资源。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍是历史 bench 证据池，没有 genuinely new blocker reduction；
   - 因此当前最诚实 desk call 仍是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 继续是唯一仍保留前推资格的 Scout 候选，并且最小 paper wiring 已继续推进**
   - 当前顶板已明确：它已从 `paper candidate` 升为 **`narrow paper pilot approved`**；
   - `19:34` 新增：
     - `combo_all_narrow_paper_pilot_ledger_template.csv`
     - 这把它从“只有 monitoring board”继续压成了可复用的 paper ledger template；
   - `19:42` 新增：
     - `combo_all_narrow_paper_pilot_refresh_seed_rows.csv`
     - 从已有历史交易里抽出了每个资产 1 条可回放 seed row，可直接拿来做 paper ledger refresh / review 演练；
   - 因此当前更诚实的 desk 读法是：
     - `Rank 2` 现在确实不该再回头打磨 admission / receipt / closeout 近义文档；
     - 若继续认领，默认只允许补 `refresh / review` 最小接线。

4. **其余候选继续维持 park**
   - `Rank 1 τ-band`：继续 `park`；
   - `Rank 3 third-touch + EMA/MACD`：继续 `park`；
   - 原版 `Rank 4 frozen-beta stat-arb`：继续 `park`；
   - `Rank 4b rolling-beta 窄重开`：已在 `18:53` 的 `time stability` 后更诚实地压回 `park`。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 继续回头打磨 `Rank 2` 的 admission / receipt / closeout 近义文档：应停止。
- 继续把 `Rank 4b` 当作 active Scout 候选：应停止。
- 继续把 `Rank 1/3/4` 包装成仍在前推的 active 候选：应停止。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；本轮没有候选值得被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ **`narrow paper pilot approved`**
  3. `third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `park`
  4. `crypto pairs stat-arb`（原 frozen-beta 版本）→ `park`
  5. `Rank 4b crypto stat-arb reframe`（rolling-beta 窄重开）→ `park`

## 接下来优先级 Top 1~3

1. **若继续认领 `Rank 2`，默认先把 narrow paper wiring 从“template / seed rows”推进到“refresh / review row”**
   - 当前最自然的下一步是：
     - 在现有 seed rows 上补 `weekly_review_status / operator_action / refresh writeback`；
     - 继续沿同一张 narrow paper ledger 往前走；
   - 不再回头补 receipt-chain / closeout 类近义文档。

2. **若当前没有比 Rank 2 更高边际的新 intake / 新 gate，就先让 `Rank 2` 吃掉默认 Scout 主资源**
   - 因为现在所有其他已知候选都已 `park`；
   - 当前默认最有价值的动作，是把唯一 surviving 候选真正接到 paper wiring 上。

3. **当 Scout 当前没有更高边际动作时，直接回退 tiny-live plumbing / reconciliation / parity / dry-run**
   - 保持默认回退链干净，不被已 park 的旧候选抢占。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1958_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不改 `docs/TODO.md`**：当前顶板已经能诚实表达最新 desk judgment——`Rank 2` 是唯一 surviving Scout 候选，且默认只做 narrow paper wiring；`Rank 4b` 已回到 `park`。
- **不改 cron 频率**：当前 `bot2` / `bot3` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. 当前 active Scout 候选里，真正仍保留前推资格的只剩 `Rank 2`；这让 desk 更干净，但也意味着下一步若不尽快把它接到真实 `refresh / review`，主资源会重新陷入低杠杆文档打磨。
2. `Rank 2` 当前新增的是 paper plumbing artifact，不是新的 alpha 证据；因此仍需继续诚实保留 `idle-gap / time-pocket / BTC weak pocket` 等 watch 位。
3. `Live Seat` 长时间保持暂空仍然是正确的，但这要求 bot2 持续守纪律：只有当新的 Scout 候选真通过快筛，才重新允许争夺 `Live Seat`。

## 本轮一句话结论（给 Jerry）

**这轮没有新的换席：EMA 继续 running paper 且 waiting_not_due，Live Seat 继续暂空；Scout 方面也没有新 challenger 翻案，当前仍只有 `Rank 2 combo_all` 保留前推资格。不过它这轮确实又往前走了两格——先有 narrow paper ledger template，再有 refresh seed rows——所以当前 bot3 最该做的，不是再找 closeout 近义文档，而是沿同一张账本继续补 `refresh / review` 的最小接线。**
