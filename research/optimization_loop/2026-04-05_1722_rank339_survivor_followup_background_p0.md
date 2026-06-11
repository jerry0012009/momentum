# Rank 339 / rotating-universe anti-survivor XS momentum — survivor follow-up = background / P0

- 时间：2026-04-05 17:22 UTC
- 对象：`Rank 339 / rotating-universe anti-survivor XS momentum`
- 执行动作：survivor 唯一一次 decisive follow-up
- 结论：`drop_to_background / P0`
- 产物：`reports/artifacts/rank339_survivor_followup/summary.csv`

## 这次具体怎么测
按 state 指定的最小 clean-room，只回答一个问题：

> 把 `survivor sleeve / rotating sleeve / combined sleeve` 放进同一套 `8h/24h blended XS momentum + 15m bars + 1h rebalance + 10bps roundtrip cost` 壳里后，净收益是否真的主要只留在 rotating sleeve？

本轮直接使用现成 `30d 15m perp cache`：
- **survivor sleeve（9）**：`BTC ETH BNB XRP ADA DOGE LTC BCH SOL`
- **rotating sleeve（9）**：`AAVE AVAX DOT LINK NEAR SUI UNI WLD ZEC`
- **combined sleeve（18）**：两者并集

统一规则：
- score = `0.5 * zscore(8h return) + 0.5 * zscore(24h return)`
- 每 `1h` 做一次横截面 rebalance
- long top `20%` / short bottom `20%`
- 每次 rebalance 扣 `10bps` 往返成本

## 结果
`reports/artifacts/rank339_survivor_followup/summary.csv` 的关键数：

- **survivor**：`mean_net_bps = -8.16`，`win_rate = 40.5%`，`t_stat = -1.29`
- **rotating**：`mean_net_bps = +3.76`，`win_rate = 44.1%`，`t_stat = +0.32`
- **combined**：`mean_net_bps = -0.70`，`win_rate = 52.4%`，`t_stat = -0.14`

翻成人话：
- survivor sleeve 明确不行；
- combined sleeve 也没有留下 after-cost 净收益；
- rotating sleeve 虽然均值转正，但强度只剩一个很弱的正偏移，`t_stat` 远不到“清楚可迁移净收益壳”的程度。

## 为什么这次不升 P2
这轮 follow-up 的门槛不是“只要 rotating 比 survivor 好一点点就算”，而是：

> rotating sleeve 必须在 after-cost 口径下留下足够清楚、可迁移、不是被 turnover/样本波动轻易吃掉的独立净收益壳。

这次没有达到。

更具体地说：
1. **universe-engineering 差异是真的**：survivor 明显弱于 rotating；
2. **但 alpha 壳还不够硬**：rotating 的 after-cost 正均值太薄，统计强度不足；
3. **一旦并回 combined，优势就被冲淡到接近归零**，说明它目前更像 universe 叙事提示，而不是已可 admission 的策略壳。

## runtime impact
- `Rank 339` 用尽 survivor 唯一一次 follow-up
- 层级迁移：`Surviving candidate -> Background pool / P0`
- `Surviving candidate slot` 释放
- `Fresh intake slot` 保持在 `research/quant_digests/2026-04-05_0059_top20-depth-imbalance-tightspread-continuation-alpha.md`
- 当前不存在新的 `Active P2`

## 一句话结果
`Rank 339` 的 clean-room follow-up 证明了“rotating sleeve 比 survivor sleeve 更像动量生存土壤”这件事方向上没错，但在统一 `8h/24h blended XS momentum + 1h rebalance + 10bps cost` 壳下，rotating sleeve 只留下强度不足的薄正均值，尚不足以构成可迁移 admission 壳，因此 survivor follow-up 收口为 `drop_to_background / P0`。
