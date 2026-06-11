# 2026-03-17 08:17 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 继续收口而不是扩张：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续暂空；`Rank 2` 当前最后一个明确可见的 `P3 weekly review` need 已在 `07:46 UTC` 被压成 `writeback seed`，而新的 fresh intake `Rank 27 Mt.Gox neckline confirmation` 也已在 `08:15 UTC` 跑完最小 clean replication 并压回 `park`。因此当前最诚实的 Scout 读法是：桌面虽然仍保留两个 `P3` 身份（`Rank 17 / Rank 2`），但默认主资源已不该继续磨旧 P3 或重开 `Rank 27`；若 `Rank 5 / Rank 6` 仍因额外数据依赖不够便宜诚实，就应直接切到下一条新的 `paper / repo based 5m / 15m crypto` fresh intake。**

## 当前 strongest evidence

1. **Paper Seat 继续由 EMA 占据，且当前确实回到 `waiting_not_due`**
   - 最新 due guardrail 仍显示：
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
     - A 股三条 lane：`2026-03-18 07:00 UTC`
   - `07:04 UTC` 的 A 股 due-follow-up 已真实消化，并在 refresh history 追加了 `贵州茅台 1d+1wk` 的新 completed-bar row。
   - 因此当前全 desk **没有** `due-now / overdue` lane，`Paper Seat` 继续按 **`waiting_not_due`** 处理。

2. **Live Seat 继续暂空，没有新候选值得升格**
   - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，但仍只是 `paper-only`；
   - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**；
   - `Rank 27` 已在 first clean replication 后压回 `park`；
   - 因此当前没有任何候选达到 `P4 / tiny-live review candidate`。

3. **Rank 2 的当前最小 P3 need 也已被如实消化**
   - 最新 optimization log：`2026-03-17_0746_rank2-weekly-review-writeback-seed.md`
   - 这轮不是再磨 `Rank 2` 的 admission / closeout 近义说明，而是把它当前真实存在的 `weekly review` need 压成：
     - `combo_all_narrow_paper_pilot_weekly_review_writeback_seed.csv`
   - 结果：
     - `ETH/SOL` 继续按 `green weekly review` 追加；
     - `BTC` 继续保留 `red_watch_hold / blocked_by_red_watch`。
   - 结论：
     - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**；
     - 但当前它的可见最小 `append/review` need 已经被进一步消化掉。

4. **Rank 27 的 fresh intake 已完成最小 clean replication，并压回 park**
   - `2026-03-17_0759_rank27-mtgox-neckline-intake.md` 先把这条线收敛为：
     - 当前 fresh intake 里最值得吃掉下一轮 clean replication 预算的候选；
     - 下一轮唯一允许动作 = 1 个最小 clean replication。
   - `2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md` 随后已完成这 1 刀 clean replication：
     - `raw_breakout`：`6bps≈-13.79%`，`positive_asset_ratio=0/3`，`false_break_ratio≈71.56%`
     - `neckline_confirm`：`6bps≈-17.42%`，`positive_asset_ratio=0/3`，`false_break_ratio≈62.50%`
     - `neckline_confirm_plus_retest_hold`：`6bps≈-3.03%`，`positive_asset_ratio=0/3`，`false_break_ratio≈68.67%`
   - 结论很干净：
     - 它没有同时做到“收益更好 + 假突破率更低”；
     - 最好的 challenger 也仍是 `positive_asset_ratio=0/3`；
     - 因此当前 hard verdict = **`Rank 27 -> P0 / park / evidence pool`**。

5. **因此当前 Scout 的真正主资源判断，已经不是“继续比较 Rank 17 / Rank 2 / Rank 27”，而是“旧 active need 已大体消化，应切下一条 fresh intake”**
   - `Rank 17` 的当前最小 `weekly review writeback seed` 已在 `07:32 UTC` 做完；
   - `Rank 2` 的当前最小 `weekly review writeback seed` 已在 `07:46 UTC` 做完；
   - `Rank 26` 已在 genuinely verdict-changing recheck 后压回 `park`；
   - `Rank 27` 也已在最小 clean replication 后压回 `park`；
   - 所以当前最诚实的默认排兵布阵应是：
     - **旧 P3 只在出现新的真实 append/review need 时回补；否则直接切新的 fresh intake。**

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25 / 26 / 27`
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

- **Paper Seat**：继续由 `EMA baseline family` 占据，当前是 **`running paper / waiting_not_due`**。
- **Live Seat**：继续暂空。
- **Scout Seat**：
  - 身份上仍保留两个 `P3`：
    1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
    2. `Rank 2`（`P3 / narrow paper pilot approved`）
  - 但当前默认主资源判断已变成：
    - `Rank 17 / Rank 2` 只有在出现新的真实 `append/review need` 时才值得回补；
    - `Rank 27` 已完成当前允许预算并压回 `park`；
    - 因此**当前默认应切新的 fresh intake，而不是继续磨旧 P3 / 已 park 线。**

## 接下来优先级 Top 1~3

1. **先快速比较 `Rank 5 / Rank 6` 是否已经足够“便宜且诚实”可接下一刀**
   - 不是为了重开旧线，而是为了先判断当前剩余 backlog 里有没有比全新 intake 更便宜的一刀。
   - 若它们仍需要额外 prediction-market / equity proxy 数据，当前就不该拿默认主资源。

2. **若 `Rank 5 / Rank 6` 仍不够便宜诚实，就直接切新的 fresh intake**
   - 继续限定在：**paper / repo based 的 `5m / 15m crypto` 候选**；
   - 目标仍是：`source intake -> clean replication -> Light Stability Pack -> park / paper candidate / narrow paper pilot` 的快筛闭环；
   - 不要再围着 `Rank 17 / Rank 2 / Rank 27` 打磨近义接线。

3. **只有前两步都 blocked，才回退 tiny-live plumbing**
   - 继续遵守：`Scout Seat > tiny-live plumbing > 其他维护`。

## TODO / web / cron 的改动或建议

### 本轮不改顶板口径
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `08:12 UTC` 已经同步到当前最准口径：
  - `EMA` 继续 `waiting_not_due`
  - `Rank 17 / Rank 2` 当前最小 P3 need 已分别消化
  - `Rank 27 -> park`
  - 默认应切新的 fresh intake
- 因此这轮属于**无新 desk verdict 的巡检确认**，不再额外改 TODO 文案。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_0817_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 desk 相关 cron 仍可维持：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = ok`
- 仍有一条外围问题需单独排查：
  - `bot7-quant-digest-4h = error`
- 这不影响本轮 desk judgment，但值得另外开一个小修复回合。

## 风险与不确定性

1. 当前 `P2` 再次为空，说明最近两条 fresh intake（`Rank 26 / 27`）都在最小诚实检查后被快速打回 `park`；这对吞吐是诚实的，但也意味着新的 alpha 候选还得继续找。
2. `Rank 17 / Rank 2` 仍在桌上，但如果未来几轮主要都只剩 writeback / operator packet / closeout 近义卡，就应继续压低它们的默认主资源优先级。
3. `Paper Seat` 现在重新回到 `waiting_not_due`，所以 bot3 不能再借 paper due-follow-up 名义空转。

## 本轮一句话结论（给 Jerry）

**这轮最重要的变化不是新升格，而是确认又一轮收口已经完成：`Rank 2` 的当前 P3 weekly-review need 已被压成 writeback seed，`Rank 27` 的 fresh intake 也已 clean replicate 后压回 park。现在桌上虽然还保留两个 `P3`（`Rank 17 / Rank 2`），但默认主资源已经不该继续磨旧 P3；如果 `Rank 5 / Rank 6` 仍不够便宜诚实，下一轮就该直接切新的 fresh intake。**
