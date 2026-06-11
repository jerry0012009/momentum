# Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade / fresh intake keep_P1

- 时间：2026-04-19 00:40 UTC
- 对象：`research/quant_digests/2026-04-18_2238_liqshock-oiunwind-exhaustionfade-alpha.md`
- 执行动作：fresh intake 最小首判；只补 `30m fade` 的 symbol bucket + 简单成本梯度，回答它是否仍保得住可独立承接的 after-cost raw alpha
- 结论：`keep_P1`
- 正式 Rank：`Rank 423`

## 本轮最小检查
直接复用 digest 已落库事件样本：
- `reports/artifacts/quant_digests/2026-04-18_liq_oi_unwind_events.csv`
- 总事件数：`42`
- 标的：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- 口径：把 `signed_30m_bps` 反向解释为 `30m exhaustion fade gross edge`，再压到简单 round-trip 成本梯度 `4/6/8/10/12bps`

## 结果
### 组合层
全 8 币组合的 `30m fade`：
- gross：`+13.99bps/event`
- net4 / net6 / net8：`+9.99 / +7.99 / +5.99bps`
- `net8` 胜率：`69.1%`

说明这条线不是“成本一压就塌”的纯概念事件研究；即使先用保守的统一 round-trip 成本，组合层仍保留正 net。

### symbol bucket
明显分成两组：
- 稳定正 bucket：
  - `BTC +19.54bps gross`（`net8 +11.54`）
  - `ETH +16.08bps gross`（`net8 +8.08`）
  - `SOL +13.23bps gross`（`net8 +5.23`）
  - `XRP +31.66bps gross`（`net8 +23.66`）
  - `ADA +31.31bps gross`（`net8 +23.31`）
- 明显不适合默认 fade 的 bucket：
  - `BNB -3.06bps gross`
  - `LINK +2.07bps gross`（`net4` 已负）
  - `DOGE +4.19bps gross`（只在 `net4` 勉强持平，`net6/net8` 转负）

把 scope 先收窄到 `BTC/ETH/SOL/XRP/ADA` 这 5 币后：
- gross：`+22.74bps/event`
- net8：`+14.74bps/event`
- `net8` 胜率：`80.0%`

## 系统认知变化
`liquidation shock × OI unwind -> 30m exhaustion fade` 已经通过 fresh intake 最小首判：它不是全币种通用模板，但在 `BTC/ETH/SOL/XRP/ADA` 这组 symbol 上保留了清楚的 after-cost pocket，因此应保留为新的 `P1 / surviving candidate`，而不是直接收口到 `background/P0`。

## 唯一剩余 blocker
唯一值得继续补的 blocker 已收敛为：
- **entry realism / delay 轴**：比较 `event close 反手` vs `1-bar delay` vs 简单 micro-confirm，确认这条 `30m fade` 在更诚实入场下是否仍保住净边

当前不再适合继续补新的 symbol/cost 轴，因为这一轴已经足够回答 first verdict：
- 有清楚 pocket；
- 且 pocket 不是单一币幻觉；
- 但默认 scope 不能再写成全 8 币通杀。

## 本轮 verdict
- `Rank 423`：`5m liquidation shock × OI unwind -> 30m exhaustion fade` 完成 fresh intake 最小首判，保留 `keep_P1`
- 建议 survivor scope：`BTC/ETH/SOL/XRP/ADA`
- 下一步若要继续，只应做 1 次便宜且诚实的 `entry realism / delay` follow-up
