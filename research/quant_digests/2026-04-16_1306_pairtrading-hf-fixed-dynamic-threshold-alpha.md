# 别把这篇 2025 高频 pairs 论文只读成“方法比较”：对 short-cycle desk，更该先拆的是「cointegration spread 回归 × entry-threshold 设计（fixed vs dynamic）」这条 raw alpha

- 时间：2026-04-16 13:06 UTC
- 类型：论文（Crossref 元数据+摘要）+ Binance Spot `5m` 最小可复现实验
- 主题类型：raw alpha
- 基础 alpha：co-integrated pair 的 spread 偏离后回归；交易本体是 spread mean reversion，threshold 只是触发层
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/distance/hybrid/fixed-threshold/dynamic-threshold/5m/15m/1m/3m
- 证据类型：论文摘要级证据 + public-data probe

## 1) 这次看了什么
- **Authors**：Alireza Aghamohammadi, Hossein Dastkhan  
- **Year**：2025  
- **Title**：*Pair trading with high-frequency data in the cryptocurrency market*  
- **Venue**：*China Finance Review International*  
- **DOI**：<https://doi.org/10.1108/cfri-11-2024-0727>  
- **Readable URL**：<https://www.emerald.com/insight/content/doi/10.1108/CFRI-11-2024-0727/full/html>  
- **Repo URL**：N/A

论文摘要给了两个对 desk 很关键的信息：
1) `5m/15m` 高频上 pairs 是可盈利候选；
2) 文中结论偏向 **fixed threshold 优于 dynamic threshold**（收益与 Sharpe）。

## 2) base alpha 先说清
这篇东西的 base alpha 不是“distance/cointegration/hybrid 谁更高级”，而是：

> **当两资产价差（spread）偏离均衡时，做回归交易（long cheap / short rich）。**

distance / cointegration / hybrid 以及 fixed/dynamic threshold 都是这条 alpha 的“配方层”，不是 alpha 本体。

## 3) 最小实验（可复现，先跑通）
我做了一个轻量 transfer probe（public data，可马上复跑）：
- **数据源**：Binance Spot 公共 K 线（无需私有权限）
- **频率**：`5m`
- **样本**：最近 `30d`
- **标的**：`BTC/ETH/BNB/SOL/XRP/DOGE`，共 `15` 对
- **策略骨架**：
  - rolling beta（24h）构造 spread；
  - z-score 标准化；
  - 比较 `fixed entry (|z|>2)` vs `dynamic entry (rolling q90(|z|))`；
  - exit：z 回到 0；
  - 成本：按每边 `1/2 bps` 两档估算 roundtrip。

## 4) 关键数据点（这轮最有用的 3 个）
1. **跨 15 对的中位差值**：`fixed - dynamic = -53.28 bps`（30d 总收益口径），说明这份 transfer 样本里 **dynamic 在更多 pair 上更优**（fixed 更优占比约 `40%`）。
2. **也有 fixed 胜出的口袋**：`ETH-SOL` 上 fixed 总收益约 `+10.77%`，dynamic 约 `+7.03%`，说明“fixed 全面更好”并不稳健。
3. **最强样本对**：`SOL-XRP` dynamic 总收益约 `+16.63%`（fixed 约 `+14.13%`）；即便扣每边 `2 bps` 粗成本，仍有正剩余（但这只是快检，不是容量评估）。

## 5) 这对当前 desk 的意义
- 这是**可独立复现的 raw alpha**，不是纯 filter。
- 真正有价值的不是“相信 fixed 或 dynamic 某一派”，而是把它做成 **pair-aware 的可切换 trigger layer**：
  - 某些 pair（如 ETH-SOL）固定阈值更稳；
  - 某些 pair（如 SOL-XRP）动态阈值更好。
- 因此更适合做成一个 **threshold policy selector**（按 pair / regime 选择 fixed 或 dynamic），而不是单一全局阈值。

## 6) 下一步怎么测（直接可执行）
1. **扩到永续合约（主战场）**：在 Binance USDⓈ-M 对同一框架复跑 `1m/3m/5m/15m`。  
2. **先做 pair admission，再做触发**：先筛稳定关系（half-life、残差方差、协整稳定度），再比较 fixed vs dynamic。  
3. **统一成本模型**：显式区分 maker/taker、滑点、冲击，输出 `gross/net/capacity` 三栏。  
4. **policy 化**：训练一个小 gating（可规则先行）决定“该 pair 当前用 fixed 还是 dynamic”。

## 7) 本轮产物
- `reports/artifacts/quant_digests/pair_hf_fixed_vs_dynamic_probe_2026-04-16.csv`
- `reports/artifacts/quant_digests/pair_hf_fixed_vs_dynamic_compare_2026-04-16.csv`
- `reports/artifacts/quant_digests/pair_hf_fixed_vs_dynamic_summary_2026-04-16.json`

## 8) 来源
1. Aghamohammadi, A., & Dastkhan, H. (2025). *Pair trading with high-frequency data in the cryptocurrency market*. China Finance Review International.  
   DOI: <https://doi.org/10.1108/cfri-11-2024-0727>  
   Readable URL: <https://www.emerald.com/insight/content/doi/10.1108/CFRI-11-2024-0727/full/html>
2. Crossref metadata（含摘要）: <https://api.crossref.org/works/10.1108/cfri-11-2024-0727>
