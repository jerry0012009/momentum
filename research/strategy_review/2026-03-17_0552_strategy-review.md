# 2026-03-17 05:52 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk verdict 再次收敛，而不是扩张：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续暂空；`Rank 7` 的唯一 cheap honesty recheck 已经做完并压回 `park`，`Rank 24` 也已从 fresh intake 直接推进到 `clean replication + Light Stability Pack -> park`。因此当前 `Scout Seat` 又重新收缩成只有两个真正 active 的 `P3`：`Rank 17（ETH+SOL-only）` 和 `Rank 2`；若两者都没有新的真实 `append/review need`，下一轮默认应直接切回新的 fresh paper/repo intake，而不是再磨已 park 的 7/21/22/23/24。**

## 当前 strongest evidence

1. **Paper Seat 仍是真实 `waiting_not_due`**
   - 最新 due guardrail 仍显示：
     - A 股下一次 close：`2026-03-17 07:00 UTC`
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
   - 因此截至本轮，`EMA` 仍没有新的 due-now / overdue refresh need。
   - 结论：
     - **`Paper Seat = EMA running paper / waiting_not_due` 继续成立**；
     - 当前 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流，而不能在 paper waiting-window 空转。

2. **Live Seat 继续暂空，没有新候选值得升格**
   - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，但仍然只是 `paper-only`；
   - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**，也还没有升到 `P4 / tiny-live review candidate`；
   - `Rank 7` 这轮已经从临时 `P1 weak candidate` 再次压回 `park`；
   - `Rank 24` 也已完成快筛并压回 `park`；
   - 所以当前并没有新的 live challenger。

3. **Rank 7 的 cheap honesty recheck 已做完，结论是压回 park**
   - 本轮允许它唯一继续存在的理由，是验证：
     - 能否在**不破坏成本 / 跨标的存活**的前提下，
     - 把极端 `no_trade_ratio≈98.6%` 压回更可用范围。
   - 结果是：
     - `EMA+combo` 几乎不改善交易密度；
     - `EMA+retest / EMA+任一门` 虽把 `no_trade_ratio` 降到约 `21.1%`，但 `6~20bps` 下跨资产回报全部转负、`positive_asset_ratio=0/3`。
   - 因此当前最诚实 verdict 已经不是 `P1`，而是：
     - **`Rank 7 -> P0 / park / evidence pool`**。

4. **Rank 24 已完成 fresh intake -> clean replication + Light Stability Pack -> park**
   - `Rank 24 trend regime filter / trend-strength-over-noise gate` 的主变体：
     - `trend_regime_default @ 6bps/side ≈ -28.29%`
     - `positive_asset_ratio = 0/3`
     - `mean_no_trade_ratio ≈ 65.24%`
   - 更严的 `stricter_trend_threshold` 虽收窄亏损到约 `-9.81%`，但仍只有 `1/3` 资产为正；
   - `10/15/20bps` 下继续恶化至约 `-43.31% / -57.57% / -68.10%`；
   - 参数邻域最佳也仍只是约 `-17.83%`。
   - 结论：
     - **`Rank 24 -> P0 / park / evidence pool`**。

5. **当前 active Scout 真正存活层又只剩两个 P3**
   - `Rank 17 pullback recovery confirmation`：
     - **`P3 / narrow paper pilot approved（ETH+SOL only）`**；
     - 已有 `weekly_review_queue` artifact；
     - 但最新日志口径也很明确：当前**没有**新的真实 `append/review need`。
   - `Rank 2 combo_all`：
     - **`P3 / narrow paper pilot approved`**；
     - 当前同样**没有**新的真实 `append/review need`。
   - 因此当前最诚实的 Scout 读法，不是“还有一个 P1 可以继续磨”，而是：
     - **active 层只有 `Rank 17 + Rank 2` 两条 P3；若都无新 need，就直接回到 fresh intake。**

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24`
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

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据。
- **Live Seat**：继续暂空。
- **Scout Seat**：当前真正 active 的 paper / repo 候选只剩：
  1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
  2. `Rank 2`（`P3 / narrow paper pilot approved`）
- `Rank 7 / 21 / 22 / 23 / 24` 均已完成当前预算内快筛，并压回 `P0 / park / evidence pool`。

## 接下来优先级 Top 1~3

1. **先看 `Rank 17 / Rank 2` 是否出现真实 P3 append/review need**
   - 当前 board 的正确读法不是“默认继续认领 P3”，而是：
     - 只有出现真实 queue / ledger / monitoring / review append need 时，才回补。

2. **若 `Rank 17 / Rank 2` 仍都没有新 need，就直接切回新的 fresh intake**
   - 继续限定在：**paper / repo based 的 `5m / 15m crypto` 候选**；
   - 目标仍是：`source intake -> clean replication -> Light Stability Pack -> park / paper candidate / narrow paper pilot` 的快筛闭环；
   - 不要回头继续磨 `Rank 7`，也不要重开已 park 的 `Rank 21 / 22 / 23 / 24`。

3. **只有当前两步都 blocked 时，才回退 tiny-live plumbing**
   - 继续遵守：`Scout Seat > tiny-live plumbing > 其他维护`。

## TODO / web / cron 的改动或建议

### 本轮不改顶板结论
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `05:49 UTC` 已同步到当前最准确口径：
  - `Rank 7 -> park`
  - `Rank 24 -> park`
  - `Rank 17 / Rank 2 -> 当前仅在真实 P3 need 时回补`
- 因此这轮属于**无新 desk verdict 的巡检确认**，不再做额外 TODO 文案改动。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_0552_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 cron 频率仍可维持：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = ok`
  - `bot7-quant-digest-4h = ok`

## 风险与不确定性

1. 当前 `P1 / P2 / P4` 全空，说明 desk 又回到了“只有两个 P3 存活，其余全部 park”的收缩态。
2. 这对排班是好事（更干净），但也说明下一条 fresh intake 仍需要继续找，不然 Scout 很容易重新陷入只磨旧 P3 的惯性。
3. `Paper Seat` 虽然仍是 `waiting_not_due`，但 A 股 close 已越来越近；若下轮 wall clock 过 `07:00 UTC` 且仍无新 ledger append，就要切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮最大的变化不是有人升格，而是两个临时活口都被如实关掉了：`Rank 7` 的唯一 cheap recheck 已经做完并压回 park，`Rank 24` 也已 clean replicate 后压回 park。现在桌上又只剩两个真正 active 的 P3（`Rank 17`、`Rank 2`）；若它们都没有新的真实 append/review need，下一轮就该直接切新 intake，而不是继续磨旧线。**
