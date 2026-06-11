# 2026-03-17 10:17 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 的关键不是换席，而是确认 `Rank 29` 已经从 `P2` 真正推进到 `P3 narrow paper pilot`，且它当前最小合法 `monitoring / weekly-review` 接线已在 `10:06 UTC` 被如实消化；与此同时，新的 fresh-intake 主线已经切到 `Rank 30 trendln paired-channel breach`。因此当前最诚实的桌面读法是：`Paper Seat = EMA running paper / waiting_not_due`；`Live Seat` 继续暂空；`Scout Seat` 身份层是 `Rank 17（P3） + Rank 2（P3） + Rank 29（P3）`，但默认主资源不该继续磨旧 P3，而应在确认三条 P3 都没有新的真实 append/review 行后，优先给 `Rank 30` 那 1 次最小 clean replication。**

## 当前 strongest evidence

1. **Paper Seat 继续由 EMA 占据，且当前仍是真实 `waiting_not_due`**
   - 最新 due guardrail 显示：
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
   - `Rank 29` 虽然已推进到 **`P3 / narrow paper pilot approved`**，但仍然只是 `paper-only`，并没有进入 `P4 / tiny-live review candidate`；
   - `Rank 30` 现在还只是 fresh intake。
   - 因此当前没有任何候选达到 `Live Seat` 的升格门槛。

3. **Rank 29 已从 `P2` 真正推进到 `P3 narrow paper pilot approved`**
   - `2026-03-17_0921_rank29-clean-replication.md` 已给出强 first verdict：
     - `6bps/side ≈ +75.23%`
     - `positive_asset_ratio = 3/3`
     - `mean_trades ≈ 160`
     - `mean_false_break_ratio ≈ 7.56%`
   - `2026-03-17_0925_rank29-no-overlap-honesty-check.md` 证明这不是 overlap 放大：
     - `6/10/15bps` aggregate 仍保持为正，`positive_asset_ratio=3/3`
   - `2026-03-17_0941_rank29-time-stability-p3.md` 又完成当前 `P2` 唯一允许的 genuinely verdict-changing 最小检查：
     - `6bps` 下 `bucket_1 / bucket_2 / bucket_3` 全部保持 `3/3` 资产为正；
     - 但 `10/15bps` 的 `bucket_2` 明显变弱，因此当前更诚实的结论是：
       - **`promote to narrow paper pilot approved（P3）`**，同时带着 `middle-bucket red-watch` 前进。
   - 结论：
     - `Rank 29` 当前已不再是 `P2`，而是：
       - **`P3 / narrow paper pilot approved（paper-only + middle-bucket red-watch）`**。

4. **Rank 29 当前最小 P3 need 也已被如实消化**
   - `2026-03-17_1006_rank29-p3-monitoring-redwatch.md` 已把当前最小接线落成：
     - `narrow_paper_pilot_monitoring_board.csv`
     - `narrow_paper_pilot_weekly_review_queue.csv`
   - 当前冻结口径：
     - `breakout_align_ge2 + no_overlap_guard + next-bar open 持有 8 根`
   - 当前 watch 明确写成：
     - `bucket_2` = red-watch
     - `BTC 20bps tail` = watch
     - weekly-review queue 中 `BTC / ETH = red_watch_now`，`SOL = yellow_watch_now`
   - 因此当前更诚实的 desk 读法不是“继续围着 Rank 29 做近义 wiring”，而是：
     - **它当前最小合法 monitoring / review need 已被消化；若没有新的真实 append/review row，就不该继续占默认主资源。**

5. **新的 fresh-intake 主线已切到 Rank 30**
   - `2026-03-17_1007_rank30-trendln-channel-intake.md` 已把：
     - `Rank 30 trendln paired-channel breach / corridor breakout gate`
     - 正式压成一张 fresh intake 卡。
   - 当前 hard verdict 只有一个：
     - **`admit_to_clean_replication_queue`**
   - 冻结入口规则：
     - `trade on = 因果配对的 support/resistance lines 已形成，corridor width 没有异常漂移，随后 close-confirm breach outer line，且 composite trend 同向`
     - `trade off = 没有 paired active lines / 只有 wick 穿越 / breach 后很快收回 corridor 内`
   - 它当前的边际价值高于：
     - 继续磨 `Rank 29 / 17 / 2` 的近义接线
     - 也高于带额外外部数据依赖的 `Rank 5 / Rank 6`
   - 结论：
     - 当前新的默认 Scout 主点已切到：
       - **`Rank 30 = fresh intake only / admit_to_clean_replication_queue`**。

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25 / 26 / 27 / 28`
  - `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate**
  - **当前空缺**
- **P2 = paper candidate**
  - **当前空缺**（`Rank 29` 已升到 `P3`）
- **P3 = narrow paper pilot**
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
  - `Rank 2 combo_all`
  - `Rank 29 trendline breakout navigator / multi-swing causal breakout state machine`
- **P4 = tiny-live review candidate**
  - **当前空缺**
- **Pre-P / Stage A（尚未进入 P 分级）**
  - `Rank 30 trendln paired-channel breach / corridor breakout gate`：`fresh intake only / admit_to_clean_replication_queue`

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据，当前仍是 **`running paper / waiting_not_due`**。
- **Live Seat**：继续暂空。
- **Scout Seat**：当前真正的 active 候选结构应写成：
  1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
  2. `Rank 2`（`P3 / narrow paper pilot approved`）
  3. `Rank 29`（`P3 / narrow paper pilot approved`，但当前最小 monitoring need 已消化）
  4. `Rank 30`（`Pre-P / fresh intake only / admit_to_clean_replication_queue`）
- 但默认主资源判断应明确写成：
  - `Rank 17 / Rank 2 / Rank 29` 当前都没有新的真实 `append/review need`；
  - 因此若继续认领 `Scout Seat`，**优先落到 `Rank 30` 的那 1 次最小 clean replication**；
  - `Rank 26 / 27 / 28` 已 park，不再继续占默认主资源。

## 接下来优先级 Top 1~3

1. **优先给 `Rank 30` 做 1 次最小 clean replication**
   - 固定复用 `BTC/ETH/SOL 120d 15m` cache；
   - 第一刀只回答：
     - `trade_count`
     - `false_break_ratio`
     - `post_cost_return`
     - `width-stability`
   - 然后快速给出：`park / P1` 的 first verdict。

2. **若 `Rank 30` 直接失败，就回到新的 fresh intake 比较**
   - 继续限定在：**paper / repo based 的 `5m / 15m crypto` 候选**；
   - 若 `Rank 5 / Rank 6` 仍因 prediction-market / equity-proxy 外部依赖不够便宜诚实，就继续挑下一条新的 fresh intake。

3. **只有出现新的真实 `P3 append/review need` 时，才回补 `Rank 29 / Rank 17 / Rank 2`**
   - 当前三条 P3 都不该默认继续磨；
   - 只有真实 queue / ledger / monitoring / weekly-review append 行出现时，才重新拿到主资源。

## TODO / web / cron 的改动或建议

### 本轮不改顶板口径
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `10:07 UTC` 已经同步到当前最准口径：
  - `EMA` 继续 `waiting_not_due`
  - `Rank 29 -> narrow paper pilot approved（P3）`
  - `Rank 29` 当前最小 monitoring / weekly-review 接线已消化
  - `Rank 30 -> fresh intake only / admit_to_clean_replication_queue`
- 因此这轮属于**无新 desk verdict 的巡检确认**，不再额外改 TODO 文案。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_1017_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 desk 相关 cron 仍可维持：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = ok`
- 外围仍有一条需单独排查：
  - `bot7-quant-digest-4h = error`
- 这不影响本轮 desk judgment，但建议继续与交易台主线分开处理。

## 风险与不确定性

1. `Rank 29` 当前确实已经够到 `P3`，但它是 **paper-only + middle-bucket red-watch**，不是“无条件更高等级”的候选。
2. `Rank 17 / Rank 2 / Rank 29` 虽都在桌上，但如果接下来几轮主要都只剩 writeback / closeout 近义卡，就应继续压低它们的默认主资源优先级。
3. `Paper Seat` 继续 `waiting_not_due`，因此 bot3 不能再借 paper due-followup 名义空转。

## 本轮一句话结论（给 Jerry）

**这轮最大的变化不是换席，而是 `Rank 29` 已经从 `P2` 真正推进到了 `P3 narrow paper pilot`，而且它当前最小 monitoring / weekly-review need 也已经被消化掉了。现在桌上是三个 `P3`（`Rank 17 / Rank 2 / Rank 29`）加一条新的 fresh intake（`Rank 30`）；默认主资源不该继续磨旧 P3，下一轮最该做的是把 `Rank 30` 快速做成 first verdict。**
