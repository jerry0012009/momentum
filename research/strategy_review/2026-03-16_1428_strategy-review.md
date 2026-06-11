# 2026-03-16 14:28 UTC · Desk Board Review

## 本轮一句话判断

**这轮是无变更巡检：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 当前仍按四档阶段表推进——`Rank 1 τ-band = park`，`Rank 2 combo_all = paper candidate（窄范围 / one more light check）`，`Rank 3 third_touch_plus_ema_macd = Light Stability Pack`，`Rank 4 crypto pairs trading = source intake / clean replication`。本轮新增证据只是把 Rank 2 的升格坐实、以及把 Rank 3 继续压回 Light Stability Pack，并没有触发新的 seat-level 改判。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
     - 美股下一次 close：`2026-03-16 20:00 UTC`
     - Crypto 1d 下一次 close：`2026-03-17 00:00 UTC`
     - A 股下一次 close：`2026-03-17 07:00 UTC`
   - 这说明当前 `EMA` 依旧是 running paper，但本窗口只该做 waiting 状态维护与 next-close 核对，不该重回默认 bot3 主任务。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍只有旧的 hard verdict，且 blocker 仍无 genuinely new reduction：
     - `pure_down = 0/100`
     - `predown_bridge_12h = 0/11`
     - `downrisk_48h = 0/109`
     - `future_pure_down_48h = 0/44`
   - 因此当前最诚实的 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 的 paper-candidate 身份被进一步坐实**
   - 最新 `paper candidate admission memo` 明确写清：
     - clean replication 已完成；
     - `Light Stability Pack` 四项里，参数稳定性通过、跨标的/成本基线通过、交易数基线通过；
     - 仍有弱 pocket：`idle_gap_guard=fail`、`time_false_break_guard=fail`、`early bucket` 负 pocket。
   - 这并没有改变上一轮判断，而是把它**更正式地收口成窄范围 `paper candidate`**：
     - 可以进入 `paper candidate pool`
     - 但仍带 `one more light check`
     - 仍不能偷升格成 `Live Seat / tiny-live ready`

4. **Rank 3 `third_touch_plus_ema_macd` 仍被压在 Light Stability Pack**
   - 本轮新补的 `trade-count honesty` 与 `time stability dry-check` 反而把边界讲得更清楚：
     - `trade-count honesty`：**fail**
       - `total trades = 1`
       - `active assets = 1/3`
       - `min asset trades = 1`
       - `min active months per asset = 1`
     - `time stability dry-check`：**fail**
       - `three_bucket_sample_floor` fail
       - `bucket_asset_coverage` fail
   - 所以这轮最重要的不是“Rank 3 又多了一条 positive evidence”，而是：**它当前样本过薄，只能继续维持 `Light Stability Pack / one more light check`，不能升 `paper candidate`。**

5. **Rank 4 `crypto pairs trading / stat-arb` 继续停在 source intake / clean replication**
   - 当前只是被纳入外部来源 scout 队列；
   - 还没进入完整 replication 结果页，也还没开始 `Light Stability Pack`；
   - 因而当前仍不应抢占更靠前的席位或主资源顺位。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 在 `Rank 3` 样本仍薄到 `trade-count / time stability` 明确 fail 时，把它包装成更接近 live 的 challenger：继续 park。
- 在 `EMA waiting_not_due` 窗口里重开 EMA 发散研究：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；没有候选值得在这轮被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ `paper candidate`（窄范围 / one more light check）
  3. `third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `Light Stability Pack`
  4. `crypto pairs trading / stat-arb`（paper + repo seed）→ `source intake / clean replication`

## 接下来优先级 Top 1~3

1. **继续把 Rank 2 `combo_all` 当成当前最靠前的 scout 候选**
   - 下一步不该再重做 headline，而应补它窄范围 `paper candidate` 所需的最小 ledger / monitoring / scope 约束表达。

2. **Rank 3 继续停在 Light Stability Pack**
   - 若要继续，只能补还缺的轻量诚实守门；
   - 不允许把它包装成 `paper candidate`，更不允许抢 `Live Seat`。

3. **Rank 4 pairs trading 保持 source intake / clean replication**
   - 只做最小 clean replication；
   - 不在当前轮次里越级进 `Light Stability Pack` 或 `paper candidate`。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1428_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 `docs/TODO.md`：当前顶板已经能诚实表达最新 desk judgment——`Live Seat` 暂空、`Rank 2` 进 `paper candidate pool`、`Rank 3` 仍在 `Light Stability Pack`、`Rank 4` 仍停在 `source intake / clean replication`。
- 不改 cron 频率：当前节奏仍合理，`bot3` 当前为 `ok`。
- 不改单独网页 verdict：这轮新增证据是在**加深既有阶段判断**，不是改席位、改 rank、或改排班逻辑。

## 风险与不确定性

1. `Rank 2 combo_all` 现在虽然最像 `paper candidate`，但仍只覆盖 `120d / 15m / 3 assets`，且 time/cadence 还有弱 pocket；因此只能是窄范围 paper candidate。
2. `Rank 3` 当前最容易被误包装：它 friction / continuity 看起来不差，但 trade-count / time stability 已经明确告诉我们样本太薄，不能偷升格。
3. `Live Seat` 长时间保持暂空是诚实的，但也要求 bot2 持续守纪律：不为“桌上必须有 live challenger”而降低标准。

## 本轮一句话结论（给 Jerry）

**这轮没有新 seat-level 改判：EMA 继续 running paper 且 waiting_not_due，Live Seat 继续暂空；Scout 阶段表也不变——Rank 2 更正式地坐实为窄范围 `paper candidate`，Rank 3 则因 trade-count / time stability fail 被继续压在 `Light Stability Pack`。**
