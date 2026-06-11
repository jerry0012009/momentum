# 2026-03-17 11:38 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 不换席，但 Scout 主线已经再次明确收口并切新：`Paper Seat = EMA running paper / waiting_not_due` 继续成立；`Live Seat` 继续暂空；`Rank 29` 仍是 `P3 narrow paper pilot` 且当前最小 monitoring / weekly-review need 已消化；`Rank 30 / Rank 31 / Rank 32` 则都已完成各自允许的最小 clean replication 并压回 `park / evidence pool`。因此当前最诚实的桌面读法是：三条 `P3`（`Rank 17 / Rank 2 / Rank 29`）继续保留身份，但默认主资源不该继续磨旧 P3，也不该重开刚 park 的 `Rank 30 / 31 / 32`；新的默认主点已经切到 **`Rank 33 endpoint NW + confirmed HL reclaim`**，下一轮最该做的是给它那 1 次最小 clean replication。**

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
   - `Rank 29` 虽然已是 **`P3 / narrow paper pilot approved`**，但仍然只是 `paper-only + middle-bucket red-watch`；
   - `Rank 33` 现在还只是 fresh intake。
   - 因此当前没有任何候选达到 `P4 / tiny-live review candidate`。

3. **Rank 29 当前仍是 P3，但当前最小合法 need 已被消化**
   - 证据链已闭合：
     - `09:21` 最小 clean replication 成功；
     - `09:25` no-overlap honesty check 通过；
     - `09:41` time stability 检查后升到 **`P3`**；
     - `10:06` 已把当前最小 monitoring / weekly-review need 压成：
       - `narrow_paper_pilot_monitoring_board.csv`
       - `narrow_paper_pilot_weekly_review_queue.csv`
   - 当前最诚实口径：
     - **`Rank 29 = paper-only narrow pilot + middle-bucket red-watch`**；
     - 若没有新的真实 append/review row，就不该继续围着它补近义 wiring。

4. **Rank 30 / Rank 31 / Rank 32 都已在最小 clean replication 后压回 park**
   - `Rank 30 trendln paired-channel breach`：
     - `breach_plus_reclaim_hold @ 6bps ≈ -7.33%`
     - `positive_asset_ratio = 0/3`
     - `mean_false_break_ratio ≈ 82.39%`
     - 结论：**`park / evidence pool`**
   - `Rank 31 chanlun-pro second-buy`：
     - `structural_higher_low_reclaim @ 6bps ≈ -31.30%`
     - `positive_asset_ratio = 0/3`
     - `mean_false_reclaim_ratio ≈ 35.04%`
     - 结论：**`park / evidence pool`**
   - `Rank 32 EMA structure vs MA slope`：
     - 主 pocket 虽有正值，但 `mean_no_trade_ratio≈99.78%`
     - 交易密度极薄，不够当前 desk admission 门槛
     - 结论：**`park / evidence pool`**
   - 因此这三条线当前都已用完默认 Scout 预算，不应立刻重开。

5. **新的 fresh-intake 主线已经切到 Rank 33**
   - `2026-03-17_1128_rank33-nw-hl-reclaim-intake.md` 已把：
     - `Rank 33 endpoint NW + confirmed HL reclaim / causal swing persistence gate`
     - 正式压成新的 fresh-intake artifact。
   - 当前 hard verdict 只有一个：
     - **`fresh intake only / admit_to_clean_replication_queue`**
   - 选择它而不是其他方向的原因很清楚：
     - 直接复用当前 repo 的 `endpoint_nadaraya_watson + confirmed_extrema` 因果因子栈；
     - 不需要新的 prediction-market / equity proxy 外部数据；
     - 比继续磨 `Rank 17 / 2 / 29` 的近义接线更贴近当前仍存活的 pullback / structure 家族。
   - 冻结入口规则：
     - `trade on = endpoint NW slope 与 higher-tf bias 同向，最近一个确认低点保持 HL，且当前 close 重新站回 NW smooth 之上并突破最近确认高点（做空反向）`
     - `trade off = NW slope 走平/反向、最近确认低点转成 LL、当前 bar 无法 reclaim NW smooth / 最近确认高点，或突破后很快跌回结构错误一侧`
   - 结论：
     - 当前新的默认 Scout 主点已经切到：
       - **`Rank 33 -> 1 次最小 clean replication`**。

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25 / 26 / 27 / 28 / 30 / 31 / 32`
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
- **Pre-P / Stage A（尚未进入 P 分级）**
  - `Rank 33 endpoint NW + confirmed HL reclaim / causal swing persistence gate`：`fresh intake only / admit_to_clean_replication_queue`

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据，当前仍是 **`running paper / waiting_not_due`**。
- **Live Seat**：继续暂空。
- **Scout Seat**：当前 active 候选结构应写成：
  1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
  2. `Rank 2`（`P3 / narrow paper pilot approved`）
  3. `Rank 29`（`P3 / narrow paper pilot approved`）
  4. `Rank 33`（`Pre-P / fresh intake only / admit_to_clean_replication_queue`）
- 但默认主资源判断应明确写成：
  - `Rank 17 / Rank 2 / Rank 29` 当前都没有新的真实 `append/review need`；
  - `Rank 30 / Rank 31 / Rank 32` 已 park，不再继续占默认主资源；
  - 因此若继续认领 `Scout Seat`，**优先落到 `Rank 33` 的那 1 次最小 clean replication**。

## 接下来优先级 Top 1~3

1. **优先给 `Rank 33` 做 1 次最小 clean replication**
   - 固定复用 `BTC/ETH/SOL 120d 15m` cache；
   - 只比较：`raw_extrema_reclaim / nw_hl_reclaim / nw_hl_plus_highbreak`；
   - 第一刀只回答：
     - `post_cost_return`
     - `trade_count`
     - `false_reclaim_ratio`
     - `time-pocket honesty`
   - 做完后应快速给出：`park / P1` 的 first verdict。

2. **若 `Rank 33` 直接失败，就回到新的 fresh intake 比较**
   - 继续限定在：**paper / repo based 的 `5m / 15m crypto` 候选**；
   - 若 `Rank 5 / Rank 6` 仍因 prediction-market / equity-proxy 外部依赖不够便宜诚实，就继续挑下一条新的 fresh intake。

3. **只有出现新的真实 `P3 append/review need` 时，才回补 `Rank 29 / Rank 17 / Rank 2`**
   - 当前三条 P3 都不该默认继续磨；
   - 只有真实 queue / ledger / monitoring / weekly-review append 行出现时，才重新拿到主资源。

## TODO / web / cron 的改动或建议

### 本轮不改顶板口径
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `11:28 UTC` 已经同步到当前最准口径：
  - `EMA` 继续 `waiting_not_due`
  - `Rank 30 / 31 / 32 -> park`
  - `Rank 33 -> fresh intake only / admit_to_clean_replication_queue`
- 因此这轮属于**无新 desk verdict 的巡检确认**，不再额外改 TODO 文案。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_1138_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 desk 相关 cron 仍可维持：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = ok`
- 这轮顺手看到一个变化：
  - `bot7-quant-digest-4h` 当前状态已恢复为 `ok`
- 因此当前无需再就 bot7 做节奏调整。

## 风险与不确定性

1. `Rank 29` 当前确实已经够到 `P3`，但它是 **paper-only + middle-bucket red-watch**，不是“无条件更高等级”的候选。
2. `Rank 30 / 31 / 32` 虽都 park，但它们都是今天刚跑完 first verdict 的反例；短期内不应因为“都在结构家族附近”就立刻重开。
3. `Paper Seat` 继续 `waiting_not_due`，因此 bot3 不能再借 paper due-follow-up 名义空转。

## 本轮一句话结论（给 Jerry）

**这轮最大的变化不是新升格，而是 Scout 通道又完成了一次诚实收口：`Rank 30 / 31 / 32` 都已经在 first verdict 后压回 park，默认 fresh-intake 主线正式切到 `Rank 33 endpoint NW + confirmed HL reclaim`。现在桌上仍是三个 `P3`（`Rank 17 / Rank 2 / Rank 29`），但默认主资源不该再磨旧 P3；下一轮最该做的还是把 `Rank 33` 快速做成 first verdict。**
