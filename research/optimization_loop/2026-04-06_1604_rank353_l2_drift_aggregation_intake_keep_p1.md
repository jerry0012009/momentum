# Rank 353 / L2 drift aggregation fresh intake keep P1

- Time: 2026-04-06 16:04 UTC
- Target: `research/quant_digests/2026-04-06_1350_l2-10s-drift-aggregation-alpha.md`
- Verdict: `keep_P1`
- Rank: `353`

## Why this changes system belief
`persistent high-confidence L2 drift aggregation` 不是单纯 README 叙事，也不只是“100ms HFT demo”：对象已经把独立主语压到 `continuous L2 pressure -> future 10s directional drift`，并给出可独立复现的最小交易壳（公开 Binance `depth20@100ms` live 流、明确 10s label、calibrated probability、阈值触发、ask/bid 入场、10s 后 mid 退出）。虽然训练样本依赖 Tardis 归档、README 还没给足 fee/slippage 后完整样本外 PnL，但 first-pass intake 所需的 `独立 raw alpha 主语 + 最小可验证壳 + 最基础 after-cost honesty 边界` 已经成立，因此不该直接打回 `background / P0`，而应保留为一次 `P1 survivor` 跟进对象。

## What I checked
1. digest 已明确把对象定位成 `continuous L2 pressure -> aggregated short-cycle directional edge`，不是 sizing overlay / regime gate。
2. repo README 明确写出：
   - Binance `btcusdt@depth20@100ms` live stream
   - 131 features
   - 10-second 3-class direction target
   - calibrated LightGBM probabilities
   - threshold-triggered paper trades
3. `model_runner.py` 证实输出是可阈值化的 `P(Decrease), P(Stable), P(Increase)` calibrated probability，而不是不可比的裸 score。
4. `trade_manager.py` 证实交易壳至少诚实地把 spread crossing 写进 entry：
   - LONG 用 `asks[0]`
   - SHORT 用 `bids[0]`
   - 10 秒后按 mid 结算
5. 关键缺口也明确存在：
   - 训练数据依赖 Tardis，不是完全免费归档；
   - 当前 repo 主要是 live dashboard / paper-trade 壳，未给出完整 fee+slippage+impact 后的稳健样本外归因；
   - 若直接照搬 100ms 连发，极易被交易频次和执行摩擦吃掉。

## Why keep_P1 instead of P2
这轮只是 first verdict。它已经足够证明“值得做唯一一次便宜诚实 follow-up”，但还没到能直接升 P2：
- 还没证明把 100ms/10s 原生信号聚合到 `1m/3m` 后，after-fee 仍留有最小可迁移 edge；
- 也还没证明 BTC 外横移稳定性。

所以最诚实的位置是：
- **不是 P0**：因为它确实有独立主语和可验证壳；
- **也不是 P2**：因为还没完成 decisive follow-up；
- **应进 P1 survivor**：下一步只值得做一次“聚合后是否仍有 edge”的便宜诚实检查。

## Reader-facing conclusion
**Rank 353：`persistent high-confidence L2 drift aggregation` fresh intake first verdict 完成，保留为 `P1 survivor`。**

这条线的可取之处不在“131 个 feature”本身，而在它已经把 `L2 pressure -> calibrated probability -> thresholded directional trade shell` 串完整；下一次 follow-up 只需要回答一个决定性问题：**把 100ms/10s 微结构方向信号聚合成 `1m/3m` short-cycle admission 后，扣掉更诚实的交易摩擦，是否还剩可迁移 edge。**
