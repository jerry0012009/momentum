# Rank 290 survivor follow-up：最小 live bar-close markout 未证明可迁移 after-cost pocket，回 background/P0

- 时间：2026-04-02 07:08 UTC
- 对象：`Rank 290 / L2 imbalance × aggressive trade delta × EMA vote`
- 目标：执行 survivor 唯一一次诚实 follow-up，直接判断它在 `BTC/ETH/SOL/BNB/DOGE` 上是否至少留下一块成本后仍存活的 `1m/3m` pocket，并区分 `volume bonus` 是 alpha 本体还是噪音装饰。

## 本轮执行
我没有再去补同维度的叙事性材料，而是直接做了一个最小 live recorder：

- 数据源：Binance USDⓈ-M public API
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT / DOGEUSDT`
- 采样时长：约 `4` 分钟
- 频率：每 `5s`
- 每分钟保留最后一个 bar-close proxy snapshot
- 特征口径：
  - `imbalance(top20)`
  - 最近 `500` 笔 `aggTrades` 的 aggressor `delta`
  - `EMA(50)` 方向
  - `volume_ratio >= 1.2` 的 bonus 票
- 信号口径：沿用 repo 的 `>=3 votes 且多空不平` 规则
- 输出 artifact：
  - `reports/artifacts/rank290_survivor_followup_live/samples.json`
  - `reports/artifacts/rank290_survivor_followup_live/minute_signals.csv`
  - `reports/artifacts/rank290_survivor_followup_live/summary.csv`
  - `reports/artifacts/rank290_survivor_followup_live/summary.json`

## 结果摘要
### 1) 信号并不稀缺，但稳定 pocket 没站出来
按 bar-close 分钟级快检：

- `BTCUSDT`：4 个可观测分钟里出现 2 次信号；`avg +1m ~= +1.48 bps`，`avg +3m ~= +6.02 bps`，样本极小，且离可交易 after-cost pocket 仍太远。
- `ETHUSDT`：4 分钟里 `0` 次信号。
- `SOLUSDT`：4 分钟里 `0` 次信号。
- `BNBUSDT`：4 分钟里出现 2 次信号，但 `avg +1m ~= -3.05 bps`。
- `DOGEUSDT`：4 分钟里出现 1 次信号，`avg +1m ~= -4.45 bps`。

当前唯一看起来“没那么差”的只有 `BTC` 的单个 `+3m` 观测，但这既没有跨币扩展，也没到足以覆盖 taker 成本的诚实门槛；`BNB/DOGE` 则直接给出负 markout，`ETH/SOL` 在这段 live 窗口里甚至没有形成可持续 admission。

### 2) `volume bonus` 更像噪音装饰，不是 alpha 本体
本轮有信号的分钟里：

- `BTC` 的 2 次信号都 **不需要** `volume bonus`
- `BNB` / `DOGE` 的触发更依赖高 `volume_ratio`，但短 markout 反而是负的

这和 intake 时的直觉一致：

> 真正有信息量的是 `imbalance + delta + EMA` 三腿共振；`volume` 更像会抬高触发密度、但不保证 pocket 质量的噪音加分项。

## Survivor verdict
### 结论：不升 `P2`，直接回 `background/P0`
这次唯一 follow-up 的目标不是证明“它永远无效”，而是看它是否已经足够留下 **至少一块清晰、可复核、可迁移** 的成本后 pocket，值得占用前排资源。

本轮答案是否定的：

1. 没有出现跨 `BTC/ETH/SOL/BNB/DOGE` 的一致 pocket；
2. 唯一略正的 `BTC +3m` 只是极小样本毛边，离 after-cost verdict 太远；
3. `volume bonus` 没证明是 alpha 本体，反而更像噪音放大器；
4. 在 survivor 预算只有 1 次的规则下，这组证据不足以诚实地把它推进到 `P2`。

因此按照 policy，应把 `Rank 290` 收口到 `background/P0`，而不是继续让它占用 survivor/front slot。

## 写回 runtime 的系统认知
`Rank 290` 的 survivor 唯一 follow-up 已收口：最小 live `1m/3m` bar-close markout 没有在 `BTC/ETH/SOL/BNB/DOGE` 上留下可迁移的 after-cost pocket；其中 `BTC` 只剩样本过小的 `+3m` 毛边，`BNB/DOGE` 短 markout 直接为负，且 `volume bonus` 更像噪音装饰而非 alpha 本体，因此不升 `P2`，直接回 `background/P0`。
