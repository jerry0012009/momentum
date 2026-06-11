# 别把 funding divergence 扫描只当监控：这份开源库更适合先落地 cross-exchange carry 这条 raw alpha（先过成本阈值）
- 时间：2026-03-23 12:16 UTC
- 类型：GitHub 仓库 + perp 定价论文 + Binance/Bybit 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-exchange funding-rate divergence carry（高 funding 一侧收租，低 funding 一侧付租更少/可收租）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/relative-value/stat-arb/cross-exchange/perp-perp/perp-spot/market-neutral/cost/execution/1m/3m/5m/15m
- 证据类型：工程证据 + 论文证据 + 本地快检（可复现）

## 1. 这次看了什么
这次主看 **aoki-h-jp/funding-rate-arbitrage (2023)**。先把 base alpha 说清楚：**不是猜方向，而是抓同一币在不同交易所 funding 的“利差”**，做 market-neutral carry（perp-perp 或 perp-spot 组合），赚 funding divergence 净额。

## 2. 核心结论
- **一句话核心结论：** funding divergence 本身可以是独立 raw alpha（carry / relative value），但只有在“利差显著大于交易成本”时才值得做。  
- **一句话证明方式：** repo 直接把 `divergence - commission = revenue` 写成可计算框架；我又用 Binance+Bybit 公共接口做了同口径快检，看到“可交易窗口很少且集中在极端币”。
- repo 示例里（按其费率假设）出现过：`Divergence 0.7328%`、`Commission 0.202%`、`Revenue +0.5308/100USDT`，说明极端时段确实可能有净 carry。  
- 但本地快检（`487` 个 Binance/Bybit 重叠 USDT 合约）显示：按 taker 往返成本 `0.20%`，**仅 `4` 个符号为正净额**；说明这不是“常时可开”的 alpha。  
- 对较液态子集（双边 24h 成交额均 ≥ `50M`，共 `25` 个符号），仅 `1` 个为正净额；`BTC/ETH/SOL` 当前 funding divergence 分别约 `0.0076%/0.0008%/0.0036%`，在 taker 费率下对应 break-even 持有约 `8.8/83.9/18.4` 天（按 8h funding 粗算），短线 carry 空间偏薄。  
- 最值得复用的不是“榜单 TopN”，而是 repo 的**策略骨架**：统一 funding 抓取、跨所对齐、手续费显式入账、先算净额再谈执行。

## 3. 为什么和当前项目直接相关
- 它直接补 raw alpha 素材池里的 **carry / funding / relative value** 分支，不再只围绕 breakout/retest 内循环。  
- 这条线可独立做完整策略：entry、exit、持仓时限、成本约束、仓位上限、交易所/币种白名单都能清楚定义。  
- 与 `1m/3m/5m/15m` 的关系：funding 结算是低频事件，但**执行与风险监控**可以用 `1m/3m/5m/15m`（冲击成本、basis 漂移、强平距离、盘口容量）完成最小实验。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / carry / market-neutral
- 基础 alpha：`alpha = funding_divergence - roundtrip_cost`（仅当净额显著为正才开）
- regime：跨所资金费分化明显且可持续、两边盘口深度足够、转账/保证金通道稳定
- filter / veto：低流动性小币、单边费率临时上调、盘口冲击超阈值、基差漂移过快、资金费刷新前后异常跳变
- risk / sizing / execution overlay：按可成交深度分层限仓、优先 maker/低费通道、分批建仓、设 `max_hold_funding_intervals` 与净额衰减止盈/止损

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 在跨所 funding divergence 极端区间，market-neutral carry 在成本后仍有正期望；普通区间不值得做。  
- **最小定义：**
  - 数据：Binance `premiumIndex` + Bybit `v5/market/tickers(linear)`，每 5 分钟快照一次。  
  - 交易池：两所重叠 USDT perp，先做“液态白名单”（双边 24h 成交额门槛）。  
  - 入场：`divergence_pct > fee_roundtrip + safety_buffer`（例如 `0.20% + 0.08%`）。  
  - 出场：`divergence_pct < 0.08%` 或达到 `max_hold = 3~6` 次 funding 结算。  
  - 仓位：每标的风险预算固定 + 交易所集中度上限。  
- **最小回测切口：** 先跑最近 `60` 天，5 分钟采样；把手续费、滑点、资金费方向、借贷/资金占用成本一起计入。  
- **先看 4 个指标：** `post_cost_pnl_per_interval`、`hit_ratio_after_cost`、`holding_intervals`、`max_basis_drift_drawdown`。

## 5. 风险与保留意见
- funding alpha 最大问题不是“有没有信号”，而是**成本和容量**：净额常常被手续费/滑点吃掉。  
- 极端利差常伴随极端风险（小币、流动性断层、风控限仓、临时下线），不能把榜单收益当可成交收益。  
- repo 里成本模型是静态费率近似，真实执行还要加借贷、资金占用、转账与延迟风险。  
- 本次快检是“快筛证据”，不是实盘结论；下一步必须进入 post-cost 事件回放。

## 6. 来源
1. **aoki-h-jp. (2023). _funding-rate-arbitrage_. GitHub repository.**  
   - Repo URL: https://github.com/aoki-h-jp/funding-rate-arbitrage  
   - Readable URL: https://github.com/aoki-h-jp/funding-rate-arbitrage
2. **He, S., Manela, A., Ross, O., & von Wachter, V. (2022/2024). _Fundamentals of Perpetual Futures_. SSRN / arXiv.**  
   - DOI: `10.2139/ssrn.4301150`  
   - Readable URL: https://arxiv.org/abs/2212.06888
3. **Binance USDⓈ-M Futures API.**  
   - Mark/Funding Snapshot: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price
4. **Bybit V5 Market API.**  
   - Tickers (linear): https://bybit-exchange.github.io/docs/v5/market/tickers

## 7. 本地复现产物
- `reports/artifacts/quant_digests/funding_divergence_binance_bybit_20260323_1210.csv`
- `reports/artifacts/quant_digests/funding_divergence_binance_bybit_liquid_20260323_1212.csv`
- `reports/artifacts/quant_digests/funding_divergence_binance_bybit_liquid_maker_taker_20260323_1213.csv`
