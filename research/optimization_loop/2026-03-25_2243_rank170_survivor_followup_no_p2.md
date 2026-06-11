# Rank 170 survivor follow-up：不升 P2，回到 background pool

- 时间：2026-03-25 22:43 UTC
- 对象：`Rank 170 / portable microstructure reversion basket`
- 阶段：`Surviving candidate` 唯一一次 decisive follow-up
- 结论：**不升 `P2`，回到 `Background pool`**

## 本轮只回答的问题
这条跨资产可移植的 `taker-imbalance × VWAP-pressure` `1m/3m` pressure-reversion basket，在**最小成本**与**最小执行诚实约束**下，是否还保留值得进入 `P2` 的可复制净边？

## 直接证据
来自 intake 产物 `reports/artifacts/quant_digests/portable-microstructure-reversion_20260325_2227/`：

1. `bar_horizon_summary.csv` 显示，横截面 market-neutral 毛边虽然存在，但核心都停留在 **约 1 bps gross / rebalance** 的量级：
   - `1m hold 1 bar = +1.171 bps`
   - `1m hold 3 bars = +1.209 bps`
   - `3m hold 1 bar = +0.667 bps`
   - `5m hold 1 bar = +0.645 bps`
2. 同一份 summary 也已经说明，`15m` 基本失效：`15m hold 1 bar = -0.043 bps`，`hold 3 bars = -1.618 bps`。这说明它不是一个可自然拉长持有、靠降换手就能轻松保住净边的 family。
3. `asset_summary_1m_proxy.csv` 显示资产贡献高度不均匀：
   - `ROSEUSDT next1m/3m/5m = +4.889 / +5.658 / +5.678 bps`
   - `BTCUSDT next1m/3m/5m = +0.581 / +0.614 / +0.951 bps`
   - `ETCUSDT next1m/3m/5m = +0.016 / +0.278 / +0.426 bps`
   也就是说，当前“universality”更像**共享 feature family 被少数尾部币放大**，而不是已经在更可扩展的流动性层级上都形成了厚实净边。
4. 这条线的诚实执行版本不是单腿 paper alpha，而是 **每次 rebalance 同时做 long top-2 / short bottom-2 的 market-neutral 篮子**。即便不预设激进 taker-taker，当前展示出来的毛边也还没有厚到足以自然覆盖真实双边 friction、排队不确定性与 bar-close 执行偏差。

## 为什么这一步不能升 P2
`P2` 需要的是“值得继续做 admission 的 deployable skeleton”，不是“统计上显著但仍主要停留在 gross 的玩具篮子”。当前证据不满足：

- **effectiveness 不够厚**：最好的横截面结果也只是 `~1.2 bps gross / 1m rebalance`，对一个分钟级、双边、持续换手的 basket 来说，这还没有形成诚实可复制的净边缓冲。
- **cross-asset stability 不够干净**：主信号并非均匀来自可扩展资产层，而是被 `ROSE` 这类尾部币明显抬高；`BTC/LTC/ETC` 的分钟级边际薄得多。
- **time stability 只支持超短窗 pocket**：`1m/3m` 还有毛边，`15m` 直接失效，说明它目前更像 short-window microstructure pocket，不是已能稳健升格的 broad family。
- **honesty / execution realism 仍未过线**：当前证据来自公共 `1m` K 线 proxy，而不是可成交价格审计；在这种口径下，`~1 bps` gross 本来就应默认按“还不够诚实”处理，而不是先乐观推进到 `P2`。

## 本轮 verdict
`Rank 170` 的 survivor follow-up 已完成：**当前证据只支持把它保留为“可继续留档的 microstructure pressure-reversion background hypothesis”，不支持它在最小成本与最小执行诚实约束下已经形成值得进入 `P2` 的可复制净边。**

因此本轮把它从 `Surviving candidate slot` 诚实结束并移回 `Background pool`。
