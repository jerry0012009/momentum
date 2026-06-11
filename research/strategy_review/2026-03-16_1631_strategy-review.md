# 2026-03-16 16:31 UTC · Desk Board Review

## 本轮一句话判断

**这轮仍是无变更巡检：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 当前阶段表也不变——`Rank 2 combo_all` 仍是唯一留在窄范围 `paper candidate pool` 的候选，`Rank 1 / Rank 3 / Rank 4` 均继续停在 `park / evidence pool`。本轮新增产物主要是在把 `Rank 2` 的 `paper candidate` 接线、跨标的稳定性与 `Run 3` handoff 写得更实，而不是触发新的 seat-level 升格。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
     - 美股下一次 close：`2026-03-16 20:00 UTC`
     - Crypto 1d 下一次 close：`2026-03-17 00:00 UTC`
     - A 股下一次 close：`2026-03-17 07:00 UTC`
   - 因此当前 `EMA` 继续是 running paper，但本窗口只该做 waiting 状态维护与 next-close 核对，不该重回默认 bot3 主任务。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍只有旧的 hard verdict，且 blocker 仍无 genuinely new reduction：
     - `pure_down = 0/100`
     - `predown_bridge_12h = 0/11`
     - `downrisk_48h = 0/109`
     - `future_pure_down_48h = 0/44`
   - 因此当前最诚实的 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 继续是唯一仍保留前推价值的 scout 候选**
   - 最新几轮新增的不是 seat-level 升格，而是把它的 `paper candidate` 接线压实：
     - `paper candidate admission memo`
     - `paper candidate monitoring board`
     - `Run 3 handoff map -> tiny-live plumbing`
     - `cross-asset stability dry-check`
   - 当前综合读法：
     - clean replication 已完成；
     - friction / trade-count / parameter stability / cross-asset baseline 已有 reader-facing 卡片；
     - `cross-asset stability` 继续确认它是 `2/3` 资产为正，但 `BTC` 这条腿仍偏弱（约 `-1.15%`, `false_break_ratio≈20%`）；
     - 因此它仍是 **窄范围 `paper candidate / one more light check`**，而不是 `Live Seat / tiny-live ready`。

4. **Rank 3 与 Rank 4 继续留在 evidence pool**
   - `Rank 3 third_touch_plus_ema_macd`：
     - `trade-count honesty = fail`
     - `time stability = fail`
     - `parameter stability` 中 `cross_asset_neighbor_floor / trade_count_neighbor_floor` 也 fail
     - 因而继续维持 `park`
   - `Rank 4 crypto pairs stat-arb`：
     - 最小 clean replication 已跑通；
     - 但三组 pairs first pass 整体偏负（约 `-12.42% / -22.91% / -27.77%`）
     - 因而 clean replication 本身已经足以给出 `park`

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 继续把 Rank 3 包装成接近 live 的候选：继续 park。
- 在 Rank 4 clean replication 已整体偏负后，继续默认给它更多主资源：继续 park。
- 在 `EMA waiting_not_due` 窗口里重开 EMA 发散研究：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；没有候选值得在这轮被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ `paper candidate`（窄范围 / one more light check）
  3. `third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `park`
  4. `crypto pairs trading / stat-arb`（paper + repo seed）→ `park`

## 接下来优先级 Top 1~3

1. **继续把 Rank 2 `combo_all` 当成当前唯一仍保留前推价值的 scout 候选**
   - 下一步应补的是 `paper candidate` 的 admission write-back / narrow scope / monitoring 约束；
   - 不再重做 headline，也不默认扩新实验矩阵。

2. **当 Scout 暂时没有合格主点时，直接回退到 tiny-live plumbing**
   - 沿 `handoff / review-ticket / writeback / registry` 这条 closeout / reconciliation 链继续补相邻卡；
   - 不回头重写抽象 live 规则页。

3. **其余 Scout 候选默认停在 evidence pool，等待 bot2 新点名**
   - `Rank 1/3/4` 当前都不应继续占用默认主资源；
   - 后续若要重开，必须由 bot2 明确点名，并说明是换 scope、换 calibration，还是重新进 Light Stability Pack。

## 本轮改动

### 已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1631_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 `docs/TODO.md`：当前顶板已经能诚实表达最新 desk judgment——`Live Seat` 暂空、`Rank 2` 留在 `paper candidate pool`、`Rank 1/3/4` 已收口到 `park`。
- 不改 cron 频率：当前节奏仍合理，`bot3` 当前为 `ok`。
- 不改单独网页 verdict：这轮新增证据是在**加深既有阶段判断**，不是新增 seat-level 升格。

## 风险与不确定性

1. `Rank 2 combo_all` 现在虽然是唯一留在 `paper candidate pool` 的候选，但仍只覆盖 `120d / 15m / 3 assets`，且 time/cadence 仍有弱 pocket；因此只能是窄范围 paper candidate。
2. 当前所有其他候选都已被收口到 `park / evidence pool`；这让 desk 更干净，但也意味着 bot2 接下来需要更主动决定：是继续把 Rank 2 往 paper candidate 接线，还是开一个新的外部来源候选。
3. `Live Seat` 长时间保持暂空是诚实的，但也要求 bot2 持续守纪律：不为“桌上必须有 live challenger”而降低标准。

## 本轮一句话结论（给 Jerry）

**这轮没有新的 seat-level 改判：EMA 继续 running paper 且 waiting_not_due，Live Seat 继续暂空；Rank 2 仍是唯一留在窄范围 `paper candidate pool` 的候选，而 Rank 1 / Rank 3 / Rank 4 都继续留在 `park / evidence pool`。**
