# 2026-04-13 16:17 UTC — Rank 399 survivor 唯一 follow-up 收口（t-1 lagged liquidity + 2/3/4-bar stagger）

## 执行小点
- target: `Rank 399 / top-half liquidity XS loser-bounce shell`
- action: survivor 唯一 follow-up（一次性出口决策）

## 本轮最小 honesty / execution 检查（同轴合并）
- honesty：liquidity admission 明确改为 `t-1 lagged quote-volume ranking`，避免同窗 volume 排名泄漏。
- execution realism：在同一信号定义下加入 `2/3/4-bar staggered rebalance`，直接测试“降换手是否能把净后翻正”。

## 复核口径
- 数据：Binance USDⓈ-M 12 majors（`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC/DOT/TRX`）
- 频率：`15m`，近 60 天（5760 bars）
- 组合：top-half liquidity tradable（6/12），横截面 loser-bounce/winner-cooldown，`long bottom 20% / short top 20%`
- 成本：统一 taker round-trip `8 bps`
- 变体：`H in {3,6,8}` × `stagger in {1,2,3,4}`

## 关键结果（改变系统认知）
- 在 `t-1 lagged liquidity ranking` 下，`2/3/4-bar stagger` 虽降低 turnover（约 `2.31 -> 0.67`），但 **12 组组合净后全部为负**。
- 最优净后也仅为：`H=8, stagger=4` 的 `-5.40 bps/bar`（仍显著为负）。
- 结论：`Rank 399` 的 survivor 唯一 blocker 已被一次性收口且未通过，执行出口 verdict 为 **`background/P0`**（不再追加第二次 follow-up）。

## 产物
- `reports/artifacts/quant_digests/rank399_survivor_followup_t1lag_stagger_15m_8bps_2026-04-13.csv`
- `reports/artifacts/quant_digests/rank399_survivor_followup_t1lag_stagger_15m_8bps_2026-04-13.json`

## 回写
- `Surviving candidate slot`：`Rank 399 -> none`，follow-up 预算消耗完毕。
- `Background pool`：登记 `Rank 399` 本轮收口后转入 `P0`。
- `cycle_plan[1]`：写入 result 并标记 `done`。
