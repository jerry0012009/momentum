# 2026-03-17 08:57 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 不是换席，而是把 fresh-intake 通道重新点亮：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续暂空；`Rank 28` 已在最小 clean replication + Light Stability Pack 后压回 `park`，而 `Rank 29 trendline breakout navigator / multi-swing causal breakout state machine` 已被正式收敛为新的 `fresh intake only / eligible for one minimal clean replication`。因此当前最诚实的 Scout 读法是：桌面保留两个 `P3` 身份（`Rank 17 / Rank 2`），但默认主资源不该继续磨旧 P3；当前真正的新 active 主线是 **`Rank 29 = Pre-P / fresh intake`**，下一轮若继续认领，默认只允许做它的 1 次最小 clean replication。**

## 当前 strongest evidence

1. **Paper Seat 继续由 EMA 占据，且当前仍是真实 `waiting_not_due`**
   - 最新 due guardrail 仍显示：
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
     - A 股三条 lane：`2026-03-18 07:00 UTC`
   - 因此当前全 desk **没有** `due-now / overdue` lane。
   - 结论：
     - **`Paper Seat = EMA running paper / waiting_not_due`**；
     - bot3 当前必须继续按 `Scout Seat > tiny-live plumbing > 其他维护` 的顺序导流，不能在 EMA waiting-window 空转。

2. **Live Seat 继续暂空，没有新候选值得升格**
   - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，但仍只是 `paper-only`；
   - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**；
   - `Rank 28` 已压回 `park`；
   - `Rank 29` 目前还只是 `fresh intake only`，连 clean replication 都还没做；
   - 因此当前没有任何候选达到 `P4 / tiny-live review candidate`。

3. **Rank 28 已完成当前预算，并在 first clean replication 后压回 park**
   - 最新 optimization log：`2026-03-17_0841_rank28-crossmarket-clean-replication.md`
   - 这条线先前以 `Rank 28 cross-market intraday leader-laggard TSMOM` 进入 source-intake；
   - 随后已完成 **1 个最小 clean replication + Light Stability Pack**：
     - `funding_8h_q60 @ 6bps/side ≈ -16.58%`
     - `positive_asset_ratio = 0/3`
     - `mean_false_follow_ratio ≈ 66.42%`
     - 邻近版本 `utc_day_q70` 也仍约 `-5.28% / 0/3 positive`
   - 四项轻稳定性检查结论也很干净：
     - 时间稳定性：`0/3 positive buckets`
     - 参数稳定性：邻域 `0/3 positive`
     - 跨标的稳定性：`0/3 assets positive`
     - 成本 / 交易数稳定性：`6/10/15/20bps` 全线不转正
   - 结论：
     - **`Rank 28 -> P0 / park / evidence pool`**；
     - 这条线已用完当前默认 Scout 预算，不应继续重开。

4. **Rank 29 已成为当前新的 fresh-intake 主线，但仍停留在 Pre-P**
   - 最新 optimization log：`2026-03-17_0847_rank29-trendline-breakout-navigator-intake.md`
   - 来源不是空想，而是 repo 里已存在的 clean-room 模块：
     - `src/momentum/signals/trendline_breakout_navigator.py`
     - `docs/SIGNALS_TRENDLINE_BREAKOUT_NAVIGATOR.md`
   - 当前冻结规则已能清楚写成：
     - `trade on = 至少一档 swing timeframe 形成可审计 active line，随后 close 真突破 active support/resistance，且 composite trend 同向`
     - `trade off = 没有 active line、只有 provisional line 但没有后续有效 pivot，或只是 wick interaction / 假突破而没有 close-confirm breakout`
   - 且当前 intake 读法没有明显 `lookahead / repaint` 红旗：confirmed pivot / line state / segment 都是逐 bar 因果更新。
   - 但它现在仍**没有**完成 clean replication，因此当前最诚实的档位不是 `P1/P2`，而是：
     - **`Pre-P / fresh intake only / eligible for one minimal clean replication`**。

5. **Rank 17 / Rank 2 的 P3 身份仍保留，但当前都没有新的真实 append/review need**
   - `Rank 17` 的当前最小 weekly-review writeback seed 已在 `07:32 UTC` 做完；
   - `Rank 2` 的当前最小 weekly-review writeback seed 已在 `07:46 UTC` 做完；
   - 因此当前默认主资源不该再继续围着这两条 P3 做近义 wiring。
   - 更诚实的当前 Scout 读法应是：
     - **旧 P3 只在有新 need 时回补；当前新增主点是 `Rank 29` 的 1 次最小 clean replication。**

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25 / 26 / 27 / 28`
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
  - `Rank 29 trendline breakout navigator / multi-swing causal breakout state machine`：`fresh intake only / eligible for one minimal clean replication`

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据，当前仍是 **`running paper / waiting_not_due`**。
- **Live Seat**：继续暂空。
- **Scout Seat**：
  - 当前保留的成熟身份层仍是：
    1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
    2. `Rank 2`（`P3 / narrow paper pilot approved`）
  - 但当前真正的新 active 主线已切到：
    3. `Rank 29`（`Pre-P / fresh intake only / one minimal clean replication allowed`）
  - `Rank 28` 已在 first verdict 后压回 `P0 / park`，不应继续占默认主资源。

## 接下来优先级 Top 1~3

1. **先做 `Rank 29` 的 1 次最小 clean replication**
   - 固定复用 `BTC/ETH/SOL 120d 15m` cache；
   - 第一刀只回答最便宜的三个问题：
     - `trade count`
     - 轻 friction 后 aggregate 是否仍可存活
     - `false-break / wick-rejection` 是否比既有 breakout 系列更诚实
   - 做完应尽量直接给出：`park / paper candidate / narrow paper pilot` 方向判断，不允许长期停在 intake 态。

2. **若 `Rank 29` clean replication 直接失败，就重新比较下一条 fresh intake**
   - 先看 `Rank 5 / Rank 6` 是否仍因 prediction-market / equity-proxy 外部数据依赖不够便宜诚实；
   - 若仍不够便宜诚实，就继续切到下一条新的 `paper / repo based 5m / 15m crypto` intake。

3. **只有出现新的真实 `P3 append/review need` 时，才回补 `Rank 17 / Rank 2`**
   - 当前两条 P3 不该默认继续磨；
   - 只有真实 queue / ledger / monitoring / review append need 出现时，才重新拿到主资源。

## TODO / web / cron 的改动或建议

### 本轮不改顶板口径
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `08:47 UTC` 已经同步到当前最准口径：
  - `EMA` 继续 `waiting_not_due`
  - `Rank 28 -> park`
  - `Rank 29 -> fresh intake only / eligible for one minimal clean replication`
- 因此这轮属于**无新 desk verdict 的巡检确认**，不再额外改 TODO 文案。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_0857_strategy-review.md`
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

1. 当前 `P2` 继续为空，说明最近 fresh-intake 通道虽然还活着，但 `Rank 26 / 27 / 28` 都在最小诚实检查后被快速打回 `park`；吞吐诚实，但 alpha 味道仍不够浓。
2. `Rank 29` 当前只是 source intake，不要因为它来自 repo 内已有模块，就提前把它当“半个 winner”；它必须先过 clean replication。
3. `Rank 17 / Rank 2` 虽仍在桌上，但如果接下来几轮主要都只剩 writeback / closeout 近义卡，就应继续压低其默认主资源优先级。

## 本轮一句话结论（给 Jerry）

**这轮最大变化是 fresh-intake 通道已经切到新的 `Rank 29`：`Rank 28` 已 clean replicate 后压回 park，而 `Rank 29 trendline breakout navigator` 已被正式收敛成下一条值得花 1 刀预算验证的候选。桌上两个 `P3`（`Rank 17 / Rank 2`）仍保留身份，但当前默认主资源不该继续磨它们；下一轮最该做的就是把 `Rank 29` 快速做成 first verdict。**
