# 2026-03-17 04:23 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 继续维持最新顶板，不额外换席：`Paper Seat = EMA running paper / waiting_not_due`；`Live Seat` 继续保持暂空；`Scout Seat` 当前真正活着的候选仍只有两条 `P3`（`Rank 17 ETH+SOL-only`、`Rank 2 combo_all`），而 fresh intake 已经切到 `Rank 22 up/down wave + MA20 persistence gate`。因此本轮最诚实的排兵布阵仍是：先把 `Rank 22` 推到 `clean replication`，只有当 `Rank 17 / Rank 2` 出现真实 append/review need 或 genuinely verdict-changing check 时，才回补现有 P3。**

## 当前 strongest evidence

1. **Paper Seat 仍是真实 `waiting_not_due`，不该空转也不该伪 refresh**
   - `ema_paper_trading_refresh_history.csv` 最新已写到：
     - `Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-16 00:00 UTC`
   - 最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
     - A 股下一次 close：`2026-03-17 07:00 UTC`（约 `6.7h` 后到点）
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
   - 因此当前对 `Paper Seat` 的正确读法仍是：
     - **`running paper pilot / waiting_not_due`**
   - 这也意味着：当前 bot3 主资源默认应继续落到 `Scout Seat > tiny-live plumbing > 其他维护`，而不是在 EMA waiting-window 里空转。

2. **Live Seat 继续保持暂空，当前没有候选值得被升格**
   - `Rank 17` 已是 `P3 / narrow paper pilot approved（ETH+SOL only）`，但仍是 **paper-only**，还不是 `P4 / tiny-live review candidate`；
   - `Rank 2` 也是 `P3 / narrow paper pilot approved`，且近期更多是在补最小 paper wiring，而不是减少 live gate；
   - `Rank 22` 目前还只到 `fresh intake accepted / pending Stage A + clean replication`，更不具备抢占 `Live Seat` 的资格；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **当前 Scout 真实存活层只有两个 P3，且都没有新的 append/review need**
   - `Rank 17 pullback recovery confirmation`：
     - 已完成 `clean replication + Light Stability Pack`；
     - 又完成 1 次 genuinely verdict-changing 的 scope-honesty check；
     - 当前更诚实的 verdict = **`P3 / narrow paper pilot approved（ETH+SOL only）`**；
     - `BTC` 继续 **`P0 / park / excluded red-watch leg`**。
   - `Rank 2 combo_all`：
     - 仍是 **`P3 / narrow paper pilot approved`**；
     - 但当前没有真实 `append/review need`，若继续默认回补，大概率又会落回低边际值 wiring。

4. **Rank 21 已完成快筛并压回 park，新的 fresh intake 已切到 Rank 22**
   - `Rank 21 market risk-on/off regime gate`：
     - 已完成 `source intake -> clean-room spec -> clean replication + Light Stability Pack`；
     - 主变体 `market_risk_2of3` 在 `6bps/side` 下跨资产约 `-25.01%`、`positive_asset_ratio=0/3`；
     - 当前硬结论 = **`P0 / park / evidence pool`**。
   - `Rank 22 up/down wave + MA20 persistence gate`：
     - 已完成 **`source intake / clean-room framing`**；
     - `trade on / trade off` 已能清楚写出；
     - 当前没有明显 `lookahead / repaint / data leakage`；
     - 但还**没有**完成 `clean replication`，因此当前最诚实状态仍是：
       - **`pre-P / Stage A（fresh intake accepted / pending clean replication）`**。

## 当前 weakest / should-park lines

- 继续把 `Rank 21` 当 active 主线：应停止，它已经完成快筛并压回 `park`。
- 把 `Rank 22` 提前写成 `P1/P2` 或更高：当前不诚实；它还没过 `clean replication`。
- 在 `Rank 17 / Rank 2` 没有真实 append/review need 时继续默认补它们：也应停止。
- 因为桌上暂时没有 `P4`，就强行把某个 P3 或 fresh intake 提成 `Live Seat`：应停止。

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21`
  - `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate**
  - **当前空缺**
- **P2 = paper candidate**
  - **当前空缺**
- **P3 = narrow paper pilot**
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
  - `Rank 2 combo_all`
- **P4 = tiny-live review candidate**
  - **当前空缺**
- **Pre-P / Stage A（尚未进入 P 分级）**
  - `Rank 22 up/down wave + MA20 persistence gate`：`source intake accepted / pending clean replication`

## Desk verdict

- **Paper Seat**：`EMA baseline family`，继续 **keep**。
- **Live Seat**：继续 **暂空**，当前没有值得升格的候选。
- **Scout Seat**：
  - 当前 active 候选不是一串旧 rank，而是：
    1. `Rank 22`（`Pre-P / Stage A -> clean replication next`）
    2. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
    3. `Rank 2`（`P3 / narrow paper pilot approved`，仅在真实 need 时回补）
  - 其余旧候选维持 `P0 / park / evidence pool`。

## 接下来优先级 Top 1~3

1. **先做 `Rank 22 up/down wave + MA20 persistence gate` 的最小 clean replication**
   - 固定 `BTC/ETH/SOL 120d 15m cache`；
   - 第一刀只回答：
     - `post-cost return`
     - `positive_asset_ratio`
     - `trade count / no-trade ratio`
     - 是否一加轻 friction 就归零。
   - 做完立刻更偏向给出：`park / paper candidate / narrow paper pilot`，而不是在 spec 阶段久留。

2. **若 `Rank 17` 出现真实 append/review need，优先补它的 P3 最小 paper 接线**
   - 只允许：
     - `paper ledger / monitoring / refresh / review` 最小续写；或
     - 一个真正会改变 paper verdict 的最小检查。
   - 不允许回到近义 admission / wording / wiring。

3. **`Rank 2` 继续退居第三优先级**
   - 只有在出现真实 `append/review need` 或 genuinely verdict-changing check 时，才值得回补；
   - 否则当前优先级仍低于 `Rank 22 clean replication`，也低于 `Rank 17` 的新 P3 真实 need。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-17_0423_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不额外改 `docs/TODO.md` 顶板**：最新 `04:16 UTC` 口径已经同步到位，包含：
  - `Rank 21 -> park`
  - `Rank 22 -> fresh intake accepted / pending clean replication`
  - `Rank 17 / Rank 2 -> P3`
- **不改 cron 频率**：当前 `bot2-strategy-review-40m = running`，`bot3-momentum-auto-opt-13m = ok`，`bot7-quant-digest-4h = ok`，节奏暂可维持。

## 风险与不确定性

1. `Rank 22` 现在只是 source intake 通过，真正值不值得活下去，要看下一轮 clean replication；当前不能因为规则短就提前乐观。
2. 当前 `P1 / P2 / P4` 都空缺，说明桌面仍是“两头化”：大多数 fresh intake 很快被打回 `P0`，少数才直接活到 `P3`。
3. `Paper Seat` 虽是 `waiting_not_due`，但 A 股 close 已在数小时内；若 close 后没有新 ledger append，下一轮就要临时切回 `Run 1` 做 due-now / overdue follow-up。

## 本轮一句话结论（给 Jerry）

**这轮 desk verdict 基本不变：EMA 继续坐 `Paper Seat` 且当前确实 `waiting_not_due`；`Live Seat` 继续空着；Scout 里真正活着的仍是两个 `P3`（`Rank 17 ETH+SOL-only`、`Rank 2`），而新的主资源已经切到 `Rank 22` 的 clean replication。简化成一句话：先别再磨旧 P3，先把 `Rank 22` 快速做成 `park / paper candidate / narrow paper pilot` 三选一。**
