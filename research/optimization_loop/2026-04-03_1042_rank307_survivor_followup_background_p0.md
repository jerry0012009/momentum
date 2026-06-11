# Rank 307 survivor follow-up — Kalshi strike-gap / neighboring-contract binary mispricing

- Time: 2026-04-03 10:42 UTC
- Target: `Rank 307 / Kalshi strike-gap / neighboring-contract binary mispricing`
- Previous state: `Surviving candidate slot`
- Decision: `background/P0`
- Slot impact: `Surviving candidate slot` 清空；不升级 `P2`

## What I checked
这轮按 survivor-only follow-up 的要求，直接去回答一个很具体的问题：

> `fair probability - market mid` 这条 15m binary mispricing，在更长样本、至少两档 `time_to_expiry` bucket、以及 maker/taker 成本梯度下，是否还保留可复现的 post-cost monotonicity？

我没有再补泛泛 repo 解读，而是用 repo 自带 `data/sample_features.csv` 做了最小诚实快检：
- 样本：repo 自带 `2470` 行面板，覆盖 `BTC / ETH / SOL / XRP`
- 合约数：从 ticker 还原得到约 `25` 个 15m contract（BTC 7，ETH 6，SOL 6，XRP 6）
- outcome 口径：对每个 contract 用最后一条 `real_price` 与 `floor_strike` 比较，还原 YES/NO 结算结果
- bucket：按 `time_to_expiry` 取三档代表点
  - `early`：`600~900s`
  - `mid`：`300~600s`
  - `late`：`180~300s`
- side 口径：先用最朴素、最可审计的 survivor check——按 `price_vs_strike_pct` 的符号决定做 YES 还是 NO
- 成本口径：
  - maker-ish：按 repo fee 近似 `1.75% * P * (1-P)` 外加中价成交
  - taker-ish：按 repo fee 近似 `7% * P * (1-P)` 外加跨价成交（YES 用 ask，NO 用 `1 - yes_bid`）

## Quick results
### 1) 分 bucket 后，cross-asset 表现并不稳定
按每个资产、每个 bucket 取一条代表快照后，maker/taker 平均单合约净值如下：

- **BTC**
  - early: maker `+0.4350` / taker `+0.4167`
  - mid: maker `-0.1050` / taker `-0.1183`
  - late: maker `+0.1075` / taker `+0.0983`
- **ETH**
  - early: maker `+0.1570` / taker `+0.1380`
  - mid: maker `+0.1817` / taker `+0.1667`
  - late: maker `+0.0900` / taker `+0.0833`
- **SOL**
  - early: maker `-0.0060` / taker `-0.0300`
  - mid: maker `+0.0392` / taker `+0.0217`
  - late: maker `-0.0892` / taker `-0.0967`
- **XRP**
  - early: maker `-0.1290` / taker `-0.1500`
  - mid: maker `+0.0658` / taker `+0.0500`
  - late: maker `-0.1750` / taker `-0.1850`

这已经足够说明：
- edge **不是**跨资产稳定；
- edge **不是**跨 `time_to_expiry` 稳定；
- 至少在 `SOL / XRP` 与 late bucket 上，maker/taker 两档都明显会塌。

### 2) 按 `|price_vs_strike_pct|` 强度分组，也没有保留应有的 decile/quantile monotonicity
把全部 bucket 代表点混在一起，按 `|price_vs_strike_pct|` 从低到高分五组后：

- Q1: maker `-0.0162` / taker `-0.0400`
- Q2: maker `+0.0889` / taker `+0.0707`
- Q3: maker `+0.1482` / taker `+0.1279`
- Q4: maker `+0.0057` / taker `-0.0007`
- Q5: maker `+0.0157` / taker `+0.0114`

如果这条 survivor 真已经准备好升 `P2`，更合理的期待应该是：
- 信号越极端，post-cost edge 越稳定；
- 至少高分位应明显优于中间分位；
- maker 与 taker 不至于在极端分位基本失去梯度。

但当前看到的是：
- 只有中间分位（Q2/Q3）看起来好；
- 更极端的 Q4/Q5 没有继续变强，甚至接近塌平；
- 这更像 starter sample 上的局部 pocket，而不是已经通过 survivor check 的稳健 mispricing 主语。

## Honest verdict
`Rank 307` 这轮 **不能** 升 `P2`。

原因不是“完全没信号”，而是：
1. survivor follow-up 要求验证的 **更长样本 + time bucket + maker/taker post-cost monotonicity**，当前并没有被证明成立；
2. 公开 starter sample 里更像是 **资产/时段选择性 pocket**，不是可以带着较高置信度进入 `P2 admission` 的稳定主线；
3. 在 policy 约束下，survivor 只有这一次便宜诚实 follow-up；这次没有产出足够强的层级上移证据，就不该继续前排占位。

## Why this changes system belief
第一轮 fresh intake 让我们知道：这不是纯 prediction-market 容器故事，它确实有一个可交易 skeleton。

但这轮 survivor check 进一步说明：**当前公开证据仍不足以证明 `fair probability - market mid` 这条 binary mispricing 在更长样本、不同 `time_to_expiry` bucket 与 maker/taker 成本下保留稳定单调性；现有 edge 更像 sample-specific pocket，因此不升级 `P2`，直接回到 `background/P0`。**

## Result sentence for runtime
`Rank 307` 的 survivor-only follow-up 已完成：repo starter sample 无法证明 `fair probability - market mid` 在更长样本、至少两档 `time_to_expiry` bucket 与 maker/taker 成本下仍保留稳定的 post-cost monotonicity；当前 edge 更像资产/时段选择性 pocket，而非可进入 admission 的稳健主线，因此本轮结论 = `background/P0`。
