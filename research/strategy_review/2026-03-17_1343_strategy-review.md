# 2026-03-17 13:43 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 不换席，也不改 board 结构：`Paper Seat = EMA running paper / waiting_not_due` 继续成立；`Live Seat` 继续暂空；`Rank 35` 已在 `12:46 UTC` 完成最小 clean replication 并压回 `park / evidence pool`；`Rank 17 / Rank 2 / Rank 29` 三条 `P3 narrow paper pilot` 当前则都已被 reconciliation 明确标成 `no_default append/review need`。因此当前最诚实的桌面读法是：**身份层仍有三个 `P3`，但当前没有一条正在运行中的 fresh Scout 候选；若 bot3 恢复正常，默认应先切新的 `paper / repo based 5m / 15m crypto` fresh intake，只有在暂时没有更高边际价值新线时，才允许先落到 `Run 3 / tiny-live plumbing / reconciliation`。**

## 当前 strongest evidence

1. **Paper Seat 继续由 EMA 占据，且当前仍是真实 `waiting_not_due`**
   - 最新 due guardrail 继续显示：
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
     - A 股三条 lane：`2026-03-18 07:00 UTC`
   - 当前全 desk **没有** `due-now / overdue` lane。
   - 结论：
     - **`Paper Seat = EMA running paper / waiting_not_due`**；
     - bot3 当前仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 的顺序导流，不能在 EMA waiting-window 空转。

2. **Live Seat 继续暂空，没有候选值得升格**
   - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，但仍只是 `paper-only`；
   - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**；
   - `Rank 29` 虽然已是 **`P3 / narrow paper pilot approved`**，但仍然只是 `paper-only + middle-bucket red-watch`；
   - `Rank 35` 现已压回 `park`。
   - 因此当前没有任何候选达到 `P4 / tiny-live review candidate`。

3. **Rank 35 已完成 first verdict，并被如实压回 park**
   - `2026-03-17_1233_rank35-vwap-pullback-intake.md` 先把这条线压成新的 fresh intake；
   - `2026-03-17_1248_rank35-clean-replication-park.md` 随后完成了唯一允许的最小 clean replication：
     - `combo_long_only @ utc_day 6bps ≈ +1.72% / positive_asset_ratio≈66.67% / mean_trades≈3.7`
     - `combo_long_only @ funding_8h 6bps ≈ +1.97% / positive_asset_ratio≈66.67% / mean_trades≈4.0`
     - `time-pocket honesty` 呈 `正 / 负 / 正`，且每桶交易数都极薄；
     - `bias_plus_vwap_reclaim` 对 `VWAP anchor` 明显敏感（`utc_day≈+8.69%` vs `funding_8h≈-0.51%`）。
   - 结论：
     - **`Rank 35 -> P0 / park / evidence pool`**；
     - 当前不够诚实进入 `paper candidate pool`，也不该继续占默认 Scout 主资源。

4. **Rank 17 / Rank 2 / Rank 29 三条 P3 当前都被明确写成 `no_default append/review need`**
   - `2026-03-17_1301_p3-lane-reconciliation.md` 已把三条 `P3 narrow paper lane` 的当前 desk 读法写成 reader-facing artifact：
     - `bot3_append_review_need = no_default`
     - `default_owner = manual_narrow_paper_runner`
   - 最新 reconciliation 摘要：
     - `Rank 2 -> no_default / manual_narrow_paper_runner`
     - `Rank 17 -> no_default / manual_narrow_paper_runner / open_positions = 2`
     - `Rank 29 -> no_default / manual_narrow_paper_runner`
   - 最关键的 desk 含义是：
     - **即使 `Rank 17` 当前仍有 open paper positions，它们也只属于专属 narrow-paper refresh continuity，不自动构成 bot3 默认 append/review need。**
   - 因此当前默认主资源不该再围着这三条 P3 补近义 wiring。

5. **当前 Scout 的真正主资源判断，是“先找新 intake；若暂无合格新线，再允许先落到 reconciliation”**
   - `Rank 30 / 31 / 32 / 33 / 34 / 35`：都已完成当前允许动作并压回 `park / evidence pool`；
   - `Rank 5 / Rank 6`：仍偏外部数据依赖，不适合作为当前轮次的 cheapest honest Scout 主线；
   - 因此当前最诚实的默认排兵布阵应是：
     - **先比较是否有新的 `paper / repo based 5m / 15m crypto` fresh intake 候选可接；若没有，就允许先落到 `Run 3 / tiny-live plumbing / reconciliation`，而不是硬开弱 fresh intake。**

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25 / 26 / 27 / 28 / 30 / 31 / 32 / 33 / 34 / 35`
  - `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate**
  - **当前空缺**
- **P2 = paper candidate**
  - **当前空缺**
- **P3 = narrow paper pilot**
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
  - `Rank 2 combo_all`
  - `Rank 29 trendline breakout navigator / multi-swing causal breakout state machine`
- **P4 = tiny-live review candidate**
  - **当前空缺**

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据，当前仍是 **`running paper / waiting_not_due`**。
- **Live Seat**：继续暂空。
- **Scout Seat**：当前 active 身份层仍是：
  1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
  2. `Rank 2`（`P3 / narrow paper pilot approved`）
  3. `Rank 29`（`P3 / narrow paper pilot approved`）
- 但当前 operational read 应明确写成：
  - 三条 P3 当前都没有新的真实 `append/review need`；
  - `Rank 30 / 31 / 32 / 33 / 34 / 35` 已 park，不再继续占默认主资源；
  - 因此若继续认领 `Scout Seat`，**默认应先切新的 `paper / repo based 5m / 15m crypto` fresh intake；若一时没有合格新线，再允许先落到 `Run 3 / reconciliation`。**

## 接下来优先级 Top 1~3

1. **优先比较并认领下一条新的 fresh intake**
   - 继续限定在：**paper / repo based 的 `5m / 15m crypto` 候选**；
   - 当前不应重开 `Rank 30~35`，也不应继续围着 `Rank 17 / 2 / 29` 做近义接线。

2. **若当前还没拿到更高边际价值新线，就先落到 `Run 3 / tiny-live plumbing / reconciliation`**
   - 这不是放弃 Scout，而是避免“为了不闲着而硬开弱候选”；
   - 当前最合适的 reconciliation 主题，已经通过 `manual narrow paper lanes` 把 `no_default append/review need` 边界写清了。

3. **只有出现新的真实 `P3 append/review need` 时，才回补 `Rank 29 / Rank 17 / Rank 2`**
   - 当前三条 P3 都不该默认继续磨；
   - 只有真实 queue / ledger / monitoring / weekly-review append 行出现时，才重新拿到主资源。

## TODO / web / cron 的改动或建议

### 本轮不改顶板结构
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `12:53 UTC` 已经同步到当前最准口径：
  - `Rank 35 -> park`
  - 三条 `P3 lane = no_default append/review need`
  - `若暂无更高边际价值 fresh intake，则允许先落到 Run 3 / reconciliation`
- 因此这轮属于**无新 desk verdict 的巡检确认**，不再额外改 TODO 结构；只保留本轮 markdown 记录 + 邮件 + 首页刷新。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_1343_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 desk 相关 cron 状态：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = error`
  - `momentum-narrow-paper-lanes = idle`
  - `bot7-quant-digest-4h = ok`
- 结论：
  - 当前**不建议马上改 cron 频率**；
  - 但 `bot3-momentum-auto-opt-13m` 当前为 `error`，应在 desk 之外单开一个小排查；
  - `momentum-narrow-paper-lanes` 当前为 `idle`，与本轮 reconciliation 口径并不冲突，但值得后续顺手确认 owner 是否按预期执行。

## 风险与不确定性

1. `Rank 29` 当前确实已经够到 `P3`，但它是 **paper-only + middle-bucket red-watch**，不是“无条件更高等级”的候选。
2. `Rank 35` 的 edge 并非完全没有，但它对 `VWAP anchor` 的敏感度和极薄交易密度意味着：当前更适合作为证据池，而不是 desk 主资源。
3. `bot3-momentum-auto-opt-13m` 当前为 `error`，所以“接下来 3 个 runs”现在更像**恢复后应如何排**，不是已经稳定在跑的状态。

## 本轮一句话结论（给 Jerry）

**这轮最大的变化不是新升格，而是确认执行层边界已经收紧：`Rank 35` 也已经完成 first verdict 并被诚实压回 park，同时三条 `P3` lane 已被明确写成 `no_default append/review need`。所以现在桌上虽仍有三个 `P3`（`Rank 17 / Rank 2 / Rank 29`），但默认主资源不该再磨旧 P3，也不该重开 `Rank 30~35`；如果 bot3 恢复正常，下一轮最该做的是直接切下一条新的 fresh intake，暂时没有好线时才先落到 reconciliation。**
