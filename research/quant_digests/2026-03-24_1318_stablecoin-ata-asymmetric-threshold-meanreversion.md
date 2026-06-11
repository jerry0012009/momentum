# 别把 stablecoin 配对只做对称阈值：这篇 2024 论文+配套代码更该先复现的是「ATA 非对称回归」生存线
- 时间：2026-03-24 13:18 UTC
- 类型：近 5 年论文（摘要可得）+ 作者公开仓库 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：锚定价（1.0）附近的配对均值回归（stablecoin relative-value / pairs）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/relative-value/stat-arb/pairs/stablecoin/threshold/ata/sta/cost/1m/3m/5m/15m
- 证据类型：论文摘要+开源代码+本地最小快检

## 1) 先回答：这篇东西的 base alpha 是什么？
**base alpha = 稳定币价比偏离锚定价后的回归交易**：当价比跌到 `1-α`（或涨到 `1+α`）时入场，回到目标价位时离场，赚“偏离→回归”的相对价值。

## 2) 这次看了什么
主材料是 **Bağcı, Kaya Soylu, Kıran (2024)** 的 stablecoin 算法交易论文（STA/ATA），以及作者给出的公开代码仓库 `bagcim/TradingAlgorithm`。代码里直接给了 `USDT/DAI` 的参数扫描逻辑、交易费假设和示例数据，属于可以马上复刻的工程骨架。

## 3) 核心结论（给 desk 的短答案）
- **一句话核心结论：** 这条线可做短周期 raw alpha，但先别照抄论文参数；当前主流稳定币偏离幅度远小于论文示例，阈值和费率必须重标定。
- **一句话证明方式：** 论文摘要给出 STA/ATA 的机制差异与适用场景；我再用 Binance 公共 5m 数据做 30 天最小快检，直接看“触发率+成本后存活”。

关键数据点：
1. 仓库代码（`TradingAlgorithm.m`）对 `USDT/DAI` 样本扫描 `α=0.2%~2.0%`，并注明示例最优约 `α=0.35%`，默认单边交易费 `0.1%`。  
2. 我的 30 天 Binance `5m` 快检：`USDCUSDT` 与 `USDTDAI` 的最大偏离仅约 `5~7 bps`，在 `α=0.35%` 下**零触发**。  
3. 对波动更大的 `FDUSDUSDT / FDUSDUSDC`：`α=0.10%` 时有触发（分别约 4.05% / 8.25% bar 命中），但若按 `0.1%` 手续费，ATA 在该窗口分别约 `-0.25% / -0.24%`，说明成本是第一生死线。

## 4) 为什么和当前 1m/3m/5m/15m 有关
- 这是**可独立运行**的 pairs / stat-arb 原型，不依赖趋势判断。  
- 对 `5m/15m`：更适合做“低频触发+高胜率回归”模块；对 `1m/3m`：只在显著偏离或事件窗（脱锚/再锚）才有意义。  
- 它还能作为其它 raw alpha 的共享 veto：当稳定币价比异常扩大时，降低高杠杆方向性策略仓位。

## 4.5 策略拆解（必填）
- 方向属性：相对价值 / 配对均值回归  
- 基础 alpha：`ratio = P(base/quote)` 偏离 1.0 后回归  
- regime：仅在“偏离可覆盖 round-trip 成本 + 最小滑点预算”时开启  
- filter / veto：订单簿深度不足、盘口点差过宽、重大脱锚新闻时禁用  
- risk / sizing / execution overlay：小仓位分层进场；优先 maker；设置最大持仓时长与未回归止损

## 5) 可复刻的最小实验（下一步怎么测）
- **研究假设**：stablecoin 配对在短周期存在可交易回归，但可交易区间随费率和市场状态变化。  
- **可计算定义**：
  - STA：`Pb=1-α, Ps=1+α`
  - ATA：`Pb=1-α, Ps=1.0`（先测低估回归，过估侧做镜像）
- **最小回测切口**：Binance 现货 `USDCUSDT/FDUSDUSDT/FDUSDUSDC/USDTDAI`，`1m/3m/5m/15m`，滚动 30~90 天。  
- **先看 2 个指标**：
  1) `trigger_rate`（每千根触发次数）；
  2) `net_bps_after_cost`（含手续费与最小滑点）。

## 6) 风险与保留意见
- 论文正文当前不可直接全文抓取，本文对论文部分按“摘要证据”处理，不做强外推。  
- 稳定币价比长期贴近 1，导致“要么不触发、要么触发后被费用吃掉”是高概率情形。  
- 真实执行里，成交排队、吃单冲击、资金费和交易规则变化都会削弱回归边际。

## 7) 本地产物
- `reports/artifacts/quant_digests/stablecoin_sta_ata_probe_20260324/stablecoin_sta_ata_probe.py`
- `reports/artifacts/quant_digests/stablecoin_sta_ata_probe_20260324/summary.json`

## 8) 来源
1. **Mahmut Bağcı, Pınar Kaya Soylu, Selçuk Kıran (2024). _The Symmetric and Asymmetric Algorithmic Trading Strategies for the Stablecoins_. Computational Economics, 64, 2663–2684.**  
   - DOI: `10.1007/s10614-023-10532-x`  
   - Readable URL: https://link.springer.com/article/10.1007/s10614-023-10532-x
2. **bagcim (GitHub). _TradingAlgorithm_.**  
   - Repo URL: https://github.com/bagcim/TradingAlgorithm
3. **Binance Spot API Docs（公开）**  
   - URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data
