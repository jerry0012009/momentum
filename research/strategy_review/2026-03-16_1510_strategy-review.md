# 2026-03-16 15:10 UTC · Desk Board Review

## 本轮一句话判断

**这轮没有新的 seat-level 改判，但 Scout 阶段表进一步收敛了：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Rank 2 combo_all` 继续是唯一仍留在 `paper candidate` 池里的窄范围候选；`Rank 3 third_touch_plus_ema_macd` 已在补齐参数稳定性后正式 `park`；`Rank 4 crypto pairs stat-arb` 也在最小 clean replication 完成后直接 `park`。因此接下来默认主资源不该再平均铺开，而应更明确地收缩成：`Rank 2 admission write-back -> tiny-live plumbing -> 其他维护 / 等 bot2 新点名`。**

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
   - 最新 `paper candidate admission memo` 已把它更正式地收口为窄范围 `paper candidate`：
     - clean replication 已完成；
     - friction / cross-asset / trade-count 基线过关；
     - time/cadence 仍有弱 pocket，因此保留 `one more light check` 标签。
   - 当前最诚实读法不变：**它可以待在 `paper candidate pool`，但不能偷升格成 `Live Seat / tiny-live ready`。**

4. **Rank 3 `third_touch_plus_ema_macd` 已从 Light Stability Pack 收口到 `park`**
   - 新补的 `parameter_stability_drycheck.csv` 进一步坐实了它的问题：
     - `positive_neighbor_floor`：pass（`7/7` positive）
     - `cross_asset_neighbor_floor`：**fail**（`0/7` configs keep `>=2/3` positive assets）
     - `trade_count_neighbor_floor`：**fail**（`0/7` configs keep `>=1` mean trades / asset）
   - 结合上一轮已知的：
     - `trade-count honesty = fail`
     - `time stability = fail`
   - 因而当前最诚实的 desk 读法已不再是 `Light Stability Pack`，而是：**`park / evidence pool`**。

5. **Rank 4 `crypto pairs trading / stat-arb` 已完成 clean replication，但 hard verdict 直接是 `park`**
   - 这轮最小 clean replication 已经跑通：
     - `source_intake_verdict = pass`
     - `clean_replication_verdict = pass`
     - 规则边界也已写清 `trade on / trade off`，且无明显 `lookahead / repaint`
   - 但 frozen-beta `z-score spread` first pass 在三组 pairs 上整体偏负：
     - `BTC/ETH ≈ -12.42%`
     - `BTC/SOL ≈ -22.91%`
     - `ETH/SOL ≈ -27.77%`
   - 因此当前更诚实的结论不是“继续给它 Light Stability Pack”，而是：**`park / evidence pool`**。

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

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1510_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- 不改 `docs/TODO.md`：当前顶板已经能诚实表达最新 desk judgment——`Live Seat` 暂空、`Rank 2` 留在 `paper candidate pool`、`Rank 3/4` 已收口到 `park`。
- 不改 cron 频率：当前节奏仍合理，`bot3` 当前为 `ok`。
- 不改单独网页 verdict：这轮新增证据是在**加深既有阶段判断**，不是新增 seat-level 升格。

## 风险与不确定性

1. `Rank 2 combo_all` 现在虽然是唯一留在 `paper candidate pool` 的候选，但仍只覆盖 `120d / 15m / 3 assets`，且 time/cadence 仍有弱 pocket；因此只能是窄范围 paper candidate。
2. 当前所有其他候选都已被收口到 `park / evidence pool`；这让 desk 更干净，但也意味着 bot2 接下来需要更主动决定：是继续把 Rank 2 往 paper candidate 接线，还是开一个新的外部来源候选。
3. `Live Seat` 长时间保持暂空是诚实的，但也要求 bot2 持续守纪律：不为“桌上必须有 live challenger”而降低标准。

## 本轮一句话结论（给 Jerry）

**这轮最大的变化是 Scout 阶段表被进一步收紧了：EMA 继续 running paper 且 waiting_not_due，Live Seat 继续暂空；Rank 2 仍是唯一留在窄范围 `paper candidate pool` 的候选，而 Rank 3 / Rank 4 都已经被更诚实地收口到 `park / evidence pool`。**
