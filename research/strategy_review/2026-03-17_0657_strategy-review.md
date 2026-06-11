# 2026-03-17 06:57 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 有两个关键点：第一，`Paper Seat` 仍由 `EMA` 占据，但现在距离 A 股 `07:00 UTC` close 只剩几分钟，因此下一次 bot3 run 的默认顺序应临时切回 `Run 1 / due-now-or-just-passed follow-up`；第二，`Scout Seat` 不再只是两条 `P3`，因为 `Rank 26 regime_triplet state gate` 已在本轮被推进到 **`P2 / paper candidate`**。因此当前最诚实的桌面读法是：`Paper Seat = EMA（due window imminent）`，`Live Seat = 暂空`，`Scout Seat = Rank 17 P3 + Rank 2 P3 + Rank 26 P2`；当这次 A 股 due-window 被处理完后，默认比较顺序应是：先看 `Rank 17 / Rank 2` 是否有真实 P3 need；若无，就优先给 `Rank 26` 那 1 次 genuinely verdict-changing 的最小检查，回答“升 P3 / 压回 park”。**

## 当前 strongest evidence

1. **Paper Seat 仍是 EMA，但下一轮应先回 due-follow-up**
   - 最新 due guardrail 仍显示：
     - A 股下一次 close：`2026-03-17 07:00 UTC`
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
   - 因此截至本轮，`EMA` 仍技术上属于 `waiting_not_due`；
   - 但当前 wall-clock 已到 `06:57 UTC`，距离 A 股下一次 close 只剩数分钟，且下一次 `bot3-momentum-auto-opt` 很可能已落在 close 之后。
   - 结论：
     - **`Paper Seat = EMA running paper / due-window imminent`**；
     - 当前 desk 不应再把“下一次默认动作”写成纯 `Scout first`，而应临时改成：
       - **先做 `Run 1 / EMA due-now-or-just-passed follow-up`**。

2. **Live Seat 继续暂空**
   - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，但仍然只是 `paper-only`；
   - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**；
   - `Rank 26` 虽然已经升到 **`P2 / paper candidate`**，但还没有到 `P3`，更没有到 `P4 / tiny-live review candidate`；
   - 因此当前没有值得升格到 `Live Seat` 的候选。

3. **Rank 26 已经成为当前 Scout 真正的新 active 候选**
   - `Rank 26 regime_triplet state gate` 已完成：
     - `source intake`
     - `clean replication`
     - `Light Stability Pack`
   - 当前 hard verdict：**`paper candidate（P2）`**
   - 关键证据：
     - 主变体 `strict_up_down`
     - `6bps/side≈+14.65%`
     - `positive_asset_ratio=2/3`
     - 时间正收益 bucket `2/3`
     - 参数邻域不是单点热像素
     - `10bps/side` 仍约 `+2.44%`
   - 但约束也很清楚：
     - `15/20bps` 已转负（约 `-11.01% / -22.68%`）
     - `mean_no_trade_ratio≈86.58%` 偏高
   - 因此它当前最诚实的分级只能是：
     - **`P2 / paper candidate`**，而不是直接升 `P3`。

4. **Rank 25 的那次 P2 red-watch 检查已经做完，并压回 park**
   - `Rank 25 EMA + Donchian breakout` 上一轮曾临时进入 `P2 / time-stability red-watch`；
   - 但紧接着那 1 次 genuinely verdict-changing 的最小检查已经完成；
   - 结果说明：
     - 时间稳定性问题不是单点像素；
     - 在正邻域和 `ETH+SOL-only` scope 下也没修复；
   - 因此当前最诚实的 verdict 已是：
     - **`Rank 25 -> P0 / park / evidence pool`**。

5. **当前 Scout active 层应读成 `P3 + P3 + P2`**
   - `Rank 17 pullback recovery confirmation`：
     - **`P3 / narrow paper pilot approved（ETH+SOL only）`**
     - 仅在真实 `append/review need` 时回补
   - `Rank 2 combo_all`：
     - **`P3 / narrow paper pilot approved`**
     - 仅在真实 `append/review need` 时回补
   - `Rank 26 regime_triplet state gate`：
     - **`P2 / paper candidate`**
     - 当前默认允许的下一步，是 1 次会改变 verdict 的最小检查，目标：`升 P3 / 压回 park`

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25`
  - `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate**
  - **当前空缺**
- **P2 = paper candidate**
  - `Rank 26 regime_triplet state gate`
- **P3 = narrow paper pilot**
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
  - `Rank 2 combo_all`
- **P4 = tiny-live review candidate**
  - **当前空缺**

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据，但当前是 **due-window imminent**。
- **Live Seat**：继续暂空。
- **Scout Seat**：当前真正 active 的 paper / repo 候选为：
  1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
  2. `Rank 2`（`P3 / narrow paper pilot approved`）
  3. `Rank 26`（`P2 / paper candidate`）
- `Rank 25` 已在最小 red-watch recheck 后压回 `park`；`Rank 7 / 21 / 22 / 23 / 24` 同样都维持 `P0 / park / evidence pool`。

## 接下来优先级 Top 1~3

1. **下一次 bot3 run 先做 `EMA due-now-or-just-passed follow-up`**
   - 因为 A 股下一次 close 就在 `07:00 UTC`；
   - 下一次 bot3 run 大概率已处于 close 已过窗口；
   - 因此默认应先确认是否出现新的 `ledger / refresh` append need。

2. **若这次 due-window 已被如实消化，再比较 `Rank 17 / Rank 2` 是否有真实 P3 need**
   - 当前对这两条 P3 的诚实口径仍是：
     - **有真实 queue / ledger / monitoring / review append need 才回补**；
     - 没有就别继续磨近义接线。

3. **若 `Rank 17 / Rank 2` 仍无真实 need，就优先给 `Rank 26` 那 1 次 genuinely verdict-changing 最小检查**
   - 目标固定为二选一：
     - **升到 `P3 / narrow paper pilot`**，或
     - **压回 `P0 / park`**
   - 不允许把它长时间卡在 `P2` 研究态。
   - 只有当 `Rank 26` 也被快速否掉时，才回到新的 fresh intake。

## TODO / web / cron 的改动或建议

### 本轮已改
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `authoritative override`：
  - 保留 `Rank 26 -> P2 paper candidate`
  - 同时写清楚：由于当前已接近 `07:00 UTC`，**下一次 bot3 run 应先回 `Run 1 / EMA due-follow-up`**，而不是继续默认纯 Scout-first
- 新增本轮 review：`research/strategy_review/2026-03-17_0657_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 cron 频率仍可维持：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = ok`
  - `bot7-quant-digest-4h = ok`

## 风险与不确定性

1. `Rank 26` 是今天第一条重新活到 `P2` 的 fresh intake，这说明 Scout 通道还没死；但它的成本厚度不足，所以离 `P3` 还差一刀真正会改变 verdict 的最小检查。
2. `Rank 25` 从 `P2` 很快被压回 `park`，也说明当前 desk 对 fresh intake 的容忍预算仍应保持短、快、诚实。
3. `Paper Seat` 当前虽还没正式进入 due-now，但离 A 股 close 已只差几分钟；下一轮如果不先看 `Run 1`，就会与当前 wall-clock 脱节。

## 本轮一句话结论（给 Jerry）

**这轮最大的变化不是换席，而是桌上重新出现了一个真正的 `P2`：`Rank 26 regime triplet state gate` 已通过快筛进入 `paper candidate`。但因为 A 股 `07:00 UTC` close 已迫在眉睫，下一次 bot3 run 仍应先回 `EMA due-follow-up`；等这次 due-window 消化完，再优先决定 `Rank 26` 是升 `P3` 还是压回 `park`。**
