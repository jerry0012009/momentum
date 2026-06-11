# Rank 183 / cbeth-eth-rolling-fair-basis-mr — P2 admission (effectiveness / expected return)
- 时间：2026-03-26 10:54 UTC
- 对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- 本轮角色：bot3 只执行当前 `cycle_plan` 的第 1 个 pending 小点；不改排班，只回答更保守执行口径下这条 `CBETH spot + ETH perp 15m rolling fair-basis MR` 是否仍有 admission-level effectiveness

## 结论
**单一收口 verdict：`keep_P2`。**

更具体地说：

> `Rank 183` 在更保守的 pair round-trip 与小中仓位执行假设下，`15m` 主对象仍保有足够支撑 pre-paper 的成本后净边；但它还没有强到本轮就该直接升入 `P3`。

这轮改变系统认知的点，不是“它还能不能活”，而是：

> **它不是只在 `20 bps` 理想化口径下才勉强成立；即使把总 pair RT 抬到约 `26~30 bps`，`15m` 的主 pocket 仍为正，尤其 `z>=2.0` 的 pocket 还有明显余量。**

## 本轮怎么重算
复用 intake / honesty gate 产物：
- `reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/trade_log.csv`
- `reports/artifacts/quant_digests/cbeth_eth_honesty_gate_20260326_1044.json`

已有回放里的 `net_ret` 默认对应 **pair RT = 20 bps**。本轮直接从 `gross_ret` 重算更保守的成本梯度，检验当总成本提高到 `24 / 26 / 28 / 30 / 32 / 35 / 40 bps` 时，每笔净收益是否仍能穿透成本。

## 结果
### 1) `z >= 1.5`：到 `30 bps` 仍有正的平均单笔净边，但余量已不算宽
- `20 bps`：mean `+20.36 bps`，median `+16.09 bps`，win rate `91.4%`
- `26 bps`：mean `+14.36 bps`，median `+10.09 bps`，win rate `77.9%`
- `30 bps`：mean `+10.36 bps`，median `+6.09 bps`，win rate `67.6%`
- `35 bps`：mean `+5.36 bps`，median `+1.09 bps`，win rate `52.5%`
- `40 bps`：mean `+0.36 bps`，median `-3.91 bps`，win rate `39.2%`

翻成人话：`z>=1.5` 这层在 `26~30 bps` 还活，但一旦把总成本抬到 `35~40 bps`，它就开始从“可 admission”滑向“几乎只剩薄 edge”。

### 2) `z >= 2.0`：更像当前最稳的 pre-paper pocket
- `20 bps`：mean `+29.86 bps`，median `+24.67 bps`，win rate `99.5%`
- `26 bps`：mean `+23.86 bps`，median `+18.67 bps`，win rate `93.2%`
- `30 bps`：mean `+19.86 bps`，median `+14.67 bps`，win rate `86.4%`
- `35 bps`：mean `+14.86 bps`，median `+9.67 bps`，win rate `76.8%`
- `40 bps`：mean `+9.86 bps`，median `+4.67 bps`，win rate `62.7%`

这说明如果后续要写成更像 paper-spec 的窄版 admission，对 `Rank 183` 最诚实的理解不是“所有 `z>=1.5` 都一样好”，而是：

> **`z>=2.0` 的 15m pocket 在保守成本口径下仍明显更厚，更接近可写成 pre-paper spec 的主区间。**

### 3) `z >= 1.25`：更像流量层，不像当前应该优先保留的 production pocket
- `30 bps`：mean `+6.00 bps`，median `+2.27 bps`
- `35 bps`：mean `+1.00 bps`，median `-2.73 bps`
- `40 bps`：mean `-4.00 bps`，median `-7.73 bps`

这层很容易被额外执行摩擦吃掉，不适合作为当前 admission 的主支柱。

## 和小中仓位执行假设怎么对上
上一轮 honesty gate 已经给出一版 Coinbase `CBETH-USD` 盘口深度：
- `2k USD`：约 `2.6~2.9 bps` 冲击
- `5k USD`：约 `3.0~3.6 bps`
- `10k USD`：约 `3.0~4.8 bps`
- `25k USD`：约 `5.0~7.7 bps`

把这些数字翻成人话：
- 若策略从 **`2k~10k USD` 小中仓位** 起步，再叠加 ETH perp 这一侧的 taker/滑点，**总 pair RT 被抬到 `26~30 bps` 是合理的保守 admission 口径**；
- 在这个区间里，`Rank 183` 的 `15m` 仍然是正的，尤其 `z>=2.0` pocket 还有明显余量；
- 但若预设成更大号仓位、或把真实总成本视作长期更接近 `35~40 bps`，那 `z>=1.5` 的大部分流量就不再那么舒服，容量故事会明显收缩。

## 为什么这轮是 keep_P2，不是 promote_P3 / P1 re-scope / P0
- **不是 `promote_P3`**：effectiveness 这条轴已经通过，但当前还没回答 `cross-asset/time stability` 与 `parameter stability + exit framing`；就这轮证据看，它更像“足够继续走 admission”，还不到“本轮必须直接进 paper launch queue”。
- **不是 `P2->P1 re-scope`**：这里没有出现新的 scope 翻案；相反，是当前 `15m` 对象本体在更保守成本下依然站得住。
- **不是 `drop_to_background`**：因为它并没有在保守成本下塌到连最小可执行规模都穿不透成本。
- **是 `keep_P2`**：因为系统现在知道，`Rank 183` 的 effectiveness 并非幻觉，但真正该继续保留的是更窄、更厚的 `15m / higher-z pocket`，而不是泛化成“所有偏离都值得打”。

## 本轮改变系统认知的一句话
`Rank 183` 的 `15m` fair-basis MR 在更保守的 `26~30 bps` pair RT 下仍保有 admission-level 净边，其中 `z>=2.0` pocket 最厚；因此它应继续留在 `Active P2`，但更像一个待收窄 spec 的 pre-paper 候选，而不是已可直接进 `P3` 的完整 launch 对象。

## 产物
- 复用：`reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/trade_log.csv`
- 复用：`reports/artifacts/quant_digests/cbeth_eth_honesty_gate_20260326_1044.json`
