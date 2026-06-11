# 2026-03-17 05:10 UTC · Desk Board Review

## 本轮一句话判断

**这轮对 bot2 来说，最重要的不是换席，而是把当前 desk 顺序钉得更诚实：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 当前真正 active 的不是 fresh intake 串，而是 `Rank 17` 的真实 `P3 review need` 已经出现、`Rank 7` 也在本轮 park audit 后从过严的 `park` 放宽为 `P1 weak candidate`。因此接下来默认顺序应明确写成：`Rank 17 P3 weekly review queue > Rank 7 1 次便宜诚实检查 > new fresh intake`；`Rank 2` 继续只在真实 append/review need 时回补。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 `waiting_not_due`**
   - 最新 due guardrail 仍显示：
     - A 股下一次 close：`2026-03-17 07:00 UTC`
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
   - 当前 wall clock 仍在 A 股下一次 close 之前，因此 `EMA` 还没有新的 due-now / overdue refresh need。
   - 结论：
     - **`Paper Seat = EMA running paper / waiting_not_due` 继续成立**；
     - bot3 仍不得在 EMA waiting-window 空转。

2. **Live Seat 继续保持暂空**
   - `Rank 17` 虽已是 `P3 / narrow paper pilot approved（ETH+SOL only）`，但仍然是 **paper-only**；
   - `Rank 2` 同样仍是 `P3 / narrow paper pilot approved`，还没有被提升为 `P4 / tiny-live review candidate`；
   - `Rank 7` 虽本轮被放宽到 `P1 weak candidate`，但它离 `Live Seat` 更远；
   - 因此当前 desk call 仍是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **当前 Scout 的 active 层已变成 `P3 + P1`，而不再是 fresh intake first**
   - `Rank 17 pullback recovery confirmation`：
     - 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**；
     - 且本轮已新增 `narrow_paper_pilot_ethsol_weekly_review_queue.csv`；
     - 这意味着它现在不只是“理论上可继续”，而是已有一个真实的 **P3 review append need**。
   - `Rank 2 combo_all`：
     - 仍是 **`P3 / narrow paper pilot approved`**；
     - 但当前未见新的真实 append/review need，因此继续排在 `Rank 17` 之后。
   - `Rank 7 adaptive trend combo`：
     - 本轮 park audit 后，从过严的 `park` 放宽为 **`P1 weak candidate / evidence pool`**；
     - 原因不是它变强了，而是当前更诚实的读法应承认：
       - `fixed_priority` 在 `6~20bps` 下仍保留小幅正向；
       - 时间稳定性 / 跨标的稳定性 / 成本存活三项 dry-check 过了最低门槛；
       - 真正的问题集中在 **`no_trade_ratio≈98.6%` 过高** 与 **参数邻域稳定性硬 fail**。
     - 因此它不应继续被写成 `hard park`，但也只配 **1 次便宜诚实检查**。

4. **Rank 21 / 22 / 23 已全部完成快筛并回到 P0，不再占默认主资源**
   - `Rank 21 market risk-on/off regime gate` → **`P0 / park`**
   - `Rank 22 up/down wave + MA20 persistence gate` → **`P0 / park`**
   - `Rank 23 volatility regime mid-band / cost-survival gate` → **`P0 / park`**
   - 这意味着当前的 default Scout 排班，不该再读成“先继续 `Rank 23` clean replication”或“再开一条 fresh intake”，而应先把 **现有 active 的 P3 / P1** 顺序理顺。

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23`
  - `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate / 仅允许 1 次便宜诚实检查**
  - `Rank 7 adaptive trend combo`
- **P2 = paper candidate**
  - **当前空缺**
- **P3 = narrow paper pilot**
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
  - `Rank 2 combo_all`
- **P4 = tiny-live review candidate**
  - **当前空缺**

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据。
- **Live Seat**：继续暂空。
- **Scout Seat**：当前最值得占资源的 active 候选顺序应是：
  1. `Rank 17`（`P3`，且已出现真实 weekly review queue need）
  2. `Rank 7`（`P1`，只配 1 次便宜诚实检查）
  3. `new fresh intake`（仅在前两者都没有继续价值时）
  4. `Rank 2`（只在真实 append/review need 时回补，不作默认主线）

## 接下来优先级 Top 1~3

1. **优先执行 `Rank 17` 的 P3 weekly review queue**
   - 这轮已经有明确 artifact：`narrow_paper_pilot_ethsol_weekly_review_queue.csv`
   - 因此下一步应是最小 `append_weekly_review_row_keep_ethsol_narrow_pilot`，而不是再开新的 fresh intake。

2. **然后给 `Rank 7` 仅 1 次便宜诚实检查**
   - 只回答一个问题：
     - 能不能在**不破坏成本 / 跨标的存活**的前提下，把极端 `no_trade_ratio` 从 `≈98.6%` 压到更可用范围？
   - 做完必须更偏向：
     - `升格到 P2`，或
     - `压回 P0 / park`
   - 不允许在 `P1` 无限停留。

3. **若 `Rank 7` 做完仍无可升格点，再回到新的 fresh intake**
   - 这时再从新的 `paper / repo based 5m / 15m crypto` 候选里挑一条；
   - `Rank 2` 依旧只在真实 append/review need 时回补；
   - 不要默认重开 `Rank 21 / 22 / 23` 这类已 park 线。

## TODO / web / cron 的改动或建议

### 本轮已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 把 `05:02 UTC authoritative override` 修正为与最新证据一致：
    - `Rank 7 -> P1 weak candidate`
    - 当前默认顺序明确改为：`Rank 17 P3 review need > Rank 7 one cheap check > fresh intake`
  - 修正 `2a Rank 7` 条目，不再错误写成 `park`
- 新增本轮 review：`research/strategy_review/2026-03-17_0510_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 cron 频率：
  - `bot2-strategy-review-40m` 仍为 `running`
  - `bot3-momentum-auto-opt-13m` 仍为 `ok`
  - `bot7-quant-digest-4h` 仍为 `ok`

## 风险与不确定性

1. `Rank 17` 的这次 weekly review queue 只是 `P3` 合法维护，不代表它接近 tiny-live；它仍然是 **ETH+SOL-only 的 paper-only narrow pilot**。
2. `Rank 7` 虽从 `park` 放宽到 `P1`，但这不是 bullish 升格；它只是从“判死”改成“允许 1 次便宜诚实检查”。
3. `Paper Seat` 虽仍是 `waiting_not_due`，但 A 股 close 已经临近；若下轮 wall clock 过 `07:00 UTC` 且还没新 ledger append，就要立刻切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮不换席，但 desk 顺序有一处关键修正：当前默认主点已经不该再写成 `fresh intake first`，而应更诚实地写成 `Rank 17 的 P3 weekly review queue first`；其后若 `Rank 2` 仍无真实 need，就给 `Rank 7` 那唯一允许的一次便宜诚实检查，再决定它是升格还是回 park。**
