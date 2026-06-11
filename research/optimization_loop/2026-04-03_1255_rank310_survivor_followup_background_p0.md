# Rank 310 survivor follow-up：7d funding carry gate × delta-neutral 对冲壳不升 P2，回到 background/P0

- 时间：2026-04-03 12:55 UTC
- 对象：`Rank 310 / 7d funding carry gate × delta-neutral 对冲壳`
- 轮次角色：bot3 survivor-only follow-up（本轮 `cycle_plan` 第 1 条）
- 结论：`background/P0`

## 这轮实际回答的问题
不是再问“funding carry 有没有经济直觉”，而是问：

> 这条 `7d annualized funding hurdle -> spot long + perp short` 的 carry 壳，是否已经有足够诚实的跨币种/更真实 friction 证据，值得从 survivor 直接升到 `P2`？

本轮答案：**还不够。**

## 为什么不升 P2
基于当前 authoritative source（`research/quant_digests/2026-04-03_1108_deltaneutral-eth-funding-carry-gate-alpha.md`）能确认的内容，这个对象目前仍主要成立于下面这组证据：

1. **主样本仍是单 repo、单主要标的 ETH carry 叙事**
   - digest 明确把最小实验顺序写成“先单币 `ETHUSDT`，再扩 `BTC/SOL`”。
   - 这说明当前公开证据里，`BTC / SOL` 还只是下一步计划，不是已完成并能改层级的结果。

2. **公开结果依赖单一成本壳，未完成更真实 friction 收口**
   - 当前 repo 只把交易成本压成统一的 `0.20%` 进出假设。
   - 但对这类 delta-neutral carry，真正会改变 desk 认知的 friction 不是一句总成本，而是：
     - taker / spread / slippage 分拆后是否仍有净边；
     - 现货借币或资金占用 proxy（capital usage / borrow drag）计入后是否仍成立；
     - funding reversal 与 basis 压缩时，净 carry 是否会快速消失。
   - 这些在当前公开证据里都还没有被做成会改变层级的诚实验证。

3. **时间稳定性与 regime 依赖被承认，但没有被补成 admission 级证据**
   - digest 已直接承认结果对 `2021` 高 funding 环境依赖较高，且 `2022–2026` Sharpe 明显变弱（约 `0.4`）。
   - 这意味着它更像“高 funding 年景下的 carry 壳”，而不是已经证明跨 regime 仍稳定的 survivor。

4. **当前仍缺少会改变系统认知的跨资产稳定性证据**
   - survivor follow-up 的成功条件写得很清楚：至少要回答 `BTC / ETH / SOL` 跨币种、并纳入更真实 friction 后，是否仍有稳定 post-cost expectancy。
   - 现有材料没有给出这条回答；只有“可以以后这样做”的实验提纲。

## 为什么也不继续拖在 survivor
按 policy，survivor 只允许 **1 次** 最小 decisive follow-up。

这次 follow-up 已经把唯一关键问题问清楚了：
- 不是这条 carry 完全没价值；
- 而是 **当前公开证据还不足以把它从 `keep_P1` 推进到 `P2`**。

继续留在 survivor 只会变成“再等等、再补一点”的拖延，不符合当前 policy。

## 对这条对象的诚实口径
更准确的说法是：

> `Rank 310` 目前证明了“funding carry + delta-neutral hedge + threshold gate”是一条可独立描述的 raw alpha 主语；但公开证据仍主要停在单 repo、单主要标的、固定总成本壳与高-funding regime 依赖，尚不足以证明它在 `BTC/ETH/SOL` 跨币种和更真实 friction 下仍有稳定 post-cost expectancy。

所以这轮应当：
- **不升 `P2`**；
- **不再占用 survivor 前排**；
- **回到 `background/P0` 保留证据**。

## 本轮会改变系统认知的一句话
`Rank 310` 的 survivor-only follow-up 已完成：当前公开证据只够确认它是“可独立描述的 funding carry raw alpha 壳”，但还不够证明其在 `BTC/ETH/SOL` 跨币种与更真实 friction 下仍保留稳定 post-cost expectancy，因此不升 `P2`，直接回到 `background/P0`。
