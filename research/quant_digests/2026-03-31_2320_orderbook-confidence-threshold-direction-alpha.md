# 别把这篇 2025 *Applied Sciences* 论文只读成黑箱分类器：对 desk 更该先测的是「order-book / taker-flow imbalance × confidence threshold」短周期 directional raw alpha，但 5m proxy 只有在 top-decile admission + maker-ish cost 下才刚转正

- 时间：2026-03-31 23:20 UTC
- 类型：2025 *Applied Sciences* 开放获取论文摘要/元数据 + OpenAlex/Crossref metadata + Binance USDⓈ-M Perpetual 公开 `5m` 本地 proxy quick check
- 主题类型：raw alpha
- 基础 alpha：**短周期 order-book / taker-flow imbalance 能提供下一段方向预测，但只有在模型置信度足够高时才执行**；alpha 本体是 **microstructure-driven directional continuation / follow-through**，不是单独的 filter
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-book/taker-flow/confidence-threshold/directional/single-asset/cross-asset/binance/perpetual/5m/15m/1m/3m/paper/public-data/cost
- 证据类型：论文摘要级硬结果 + 公共 kline/taker-volume proxy replication

## 1. 这次看了什么
这次主材料是 **Alexandr Kuznetsov, Олексій Костенко, K.O. Klymenko, Zoriana Hbur, Roman Kovalskyi (2025), _Machine Learning Analytics for Blockchain-Based Financial Markets: A Confidence-Threshold Framework for Cryptocurrency Price Direction Prediction_, *Applied Sciences***。

先按这轮任务要求回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：短周期 order-book / taker-flow imbalance 所携带的方向信息，在高置信度时更容易转成下一段价格 follow-through。**

所以它不是单纯的 ML 壳子，也不是“预测器外面再套一个风控阈值”。它的 alpha 本体很清楚：
- 市场微观结构里有 **可交易的方向信息**；
- 但这个方向 edge **不是 every bar 都该打**；
- 真正值钱的是把 **direction prediction** 和 **trade execution admission** 拆开。

这点对我们 desk 很重要，因为它直接对应 `1m / 3m / 5m / 15m` 的现实：
- 方向信号可以很多；
- 真正赚钱的，往往只是最有把握的一小撮；
- admission rule 不是附属品，而是策略骨架的一部分。

## 2. 论文里最值得记住的硬点
这篇 paper 最有价值的，不是“又有个神经网络准确率很高”，而是它把 **方向预测** 和 **是否执行** 明确分开了。论文摘要给出的关键数字很硬：

- 样本：**11** 个 major crypto pairs
- 时间：**12 个月**
- executed trades 的方向准确率：**82.68%**
- executed trades 的平均净收益：**151.11 bps / trade**
- market coverage：**11.99%**
- 入选特征里，**81.3%** 来自 order-book microstructure

翻成人话：
1. 这不是想在全市场每个时点都出手；
2. 它承认 **coverage 低**，但换来更高的每笔质量；
3. 短周期 edge 的核心，不在宏观叙事，而在 **order-book / flow microstructure**；
4. confidence threshold 不是单独的 overlay，而是 **alpha 从 paper edge 走向可执行策略** 的必要组件。

## 3. 为什么它值得进当前素材池
当前 `momentum` 里已经有很多：
- pairs / cointegration / basket stat-arb
- basis / funding / cross-venue carry
- breakout / trend / pseudo-session continuation
- OFI / quote-gap / maker-taker 等微结构线索

但还缺一张更明确的卡：

> **把“方向预测”本体和“什么时候值得下注”这件事分开写清楚的短周期 raw alpha 卡。**

这篇 paper 值得收进池子，因为它满足本轮高优先级要求：
- **是 raw alpha，不是 filter 伪装成 alpha**；
- **可独立复现**：order book、trade flow、kline、taker-buy volume 都能从公开源先做 proxy；
- **可直接落成完整策略**：entry / exit / sizing / cost / admission rule 都能明确写；
- 对 `1m / 3m / 5m / 15m` 映射自然，不需要硬扯低频外部数据。

## 3.5 策略拆解（必填）
- 方向属性：short-horizon directional / microstructure follow-through
- 基础 alpha：**高置信度的 order-book / taker-flow imbalance 预测下一段同向收益**
- regime：更适合流动性较好、book state 稳定、毒流不极端的阶段
- filter / veto：**confidence threshold**；低置信度不交易
- risk / sizing / execution overlay：按置信度分桶决定仓位；高成本环境下必须偏 maker-ish，或只打 top-decile / top-5% 信号

## 4. 这篇 paper 对 desk 最有价值的读法
这篇东西最值钱的地方，不是“神经网络比传统分类器强”，而是下面这句：

> **trade / no-trade admission 本身，就是 alpha 的一部分。**

很多短周期研究容易犯一个错：
- 先做一个略有方向性的分类器；
- 再默认每次都打；
- 最后发现费用一吃，alpha 没了。

这篇 paper 的 desk 化读法正好相反：
- 先承认市场大多数 bar 不值得打；
- 再让模型只在 **高 confidence** 区域出手；
- 最后把成本、覆盖率、每笔质量一起看。

这其实比“再造一个更复杂的因子”更适合我们当前阶段。

## 5. 我先做了一个最便宜的 public-data proxy
为了避免只抄摘要，我做了一个很便宜的 desk 版 proxy，用的是 **Binance USDⓈ-M Perpetual 公开 `5m` kline**，因为它自带：
- OHLCV
- quote volume
- taker buy volume

### 5.1 proxy 设置
- 标的：`BTC / ETH / SOL / ADA / XRP / DOGE / BNB / LINK`
- 样本：`2026-01-01 ~ 2026-03-31`
- 频率：`5m`
- 预测目标：**下一段 `15m` 方向**（即未来 3 根 `5m`）
- 特征：
  - `ret1 / ret3 / ret12`
  - `high-low range`
  - `bar body`
  - `taker buy imbalance`
  - `volume z-score`
  - 短窗 realized vol
  - `imbalance × volume` / `body × imbalance`
- 模型：最简单的 pooled logistic regression
- 成本：先用 **round-trip 10 bps** 做 taker-ish stress，再看 `4 / 6 bps` maker-ish 情形

这当然不是论文原版。论文用的是 **daily macro + high-frequency order book microstructure** 的神经网络框架；我这里只是先看一个便宜 proxy 能不能把它的核心命题——**高 confidence admission 更值钱**——保留下来。

### 5.2 proxy 的核心结果
测试集整体（不设 admission）只有：
- 方向准确率约 **53.10%**
- 平均 gross edge 约 **0.82 bps / trade**

但当我只打更高置信度区间时，质量确实单调上升：

| confidence bucket | coverage | accuracy | avg gross bps/trade |
|---|---:|---:|---:|
| 全部样本 | 100% | 53.10% | 0.82 |
| top 30% confidence | 30% | 56.31% | 1.93 |
| top 20% confidence | 20% | 57.34% | 2.78 |
| top 15% confidence | 15% | 58.28% | 3.72 |
| top 10% confidence | 10% | 59.94% | 5.04 |
| top 5% confidence | 5% | 60.65% | 7.00 |

### 5.3 这组 proxy 怎么解释
这组数值其实非常有信息量：

1. **confidence threshold 的方向是对的。**
   coverage 下降时，accuracy 和 gross edge 都在升。

2. **但便宜 proxy 还远不够。**
   在 `10 bps` taker-ish 成本下，连 top 5% confidence 也还是约 **-3.00 bps / trade**。

3. **只有当执行成本降到 maker-ish 水平时，alpha 才开始勉强露头。**
   - top 10% confidence：`coverage ≈ 10%`、`accuracy ≈ 59.94%`，若成本按 **4 bps**，平均约 **+1.04 bps / trade**；按 **6 bps** 则仍是 **-0.96 bps**。
   - top 5% confidence：`coverage ≈ 5%`、`accuracy ≈ 60.65%`，若成本按 **4 bps**，平均约 **+3.00 bps / trade**；按 **6 bps** 仍只剩 **+1.00 bps**，到 **10 bps** 就又转负。

换句话说：

> **这条 alpha 不是“有点预测力就能拿去打”的类型。它更像一条必须同时满足“高 confidence + 低成本 + 更细 flow 特征”的精细化短周期 directional alpha。**

这反而和论文精神是对齐的：paper 里真正的 edge，不只是分类器，而是 **microstructure richness + selective execution** 的组合。

## 6. 对 `1m / 3m / 5m / 15m` 的映射
### 6.1 `5m`
这是当前最自然的 admission 频率：
- 公开数据便于最小实验；
- taker-buy volume 已经能先当 cheap flow proxy；
- 可以先验证 confidence bucket 是否真有 monotonic edge。

### 6.2 `1m / 3m`
更适合下一步补：
- 用更细的 imbalance / microprice / trade sign / queue proxy；
- 看 signal 是不是在更细颗粒度上更像论文所说的 microstructure alpha；
- 同时更适合 maker/taker split 与 fill-quality 估计。

### 6.3 `15m`
更适合作为 **持有期**，而不是信号生成频率：
- 我这次 proxy 也是拿 `5m` 特征去预测未来 `15m`；
- 如果直接把信号粗化到 `15m`，大概率会把很多 microstructure edge 抹平。

## 7. 对 desk 最值得拿走的完整策略壳
这条线不是只有“预测涨跌”四个字。第一版其实已经能写成完整策略：

### Entry
- 每根 `5m` 更新一次 short-horizon direction score
- 只有当 `p(up) > 0.5 + τ` 或 `p(down) < 0.5 - τ` 才入场
- `τ` 不是拍脑袋，要按 coverage bucket 固定成 top `10% / 5%`

### Exit
- 固定持有 `3` 根 `5m`（即 `15m`）
- 或更保守：提前 hit opposite signal / flow reversal 即退出

### Sizing
- 第一版按 confidence 分层：
  - `top 10%`：1x
  - `top 5%`：1.5x
- 更进阶再做 vol-target / liquidity-target

### Risk
- 避开 funding 结算前后极端噪声带
- 避开深度断层 / 异常点差扩张时段
- 连续错信号超过阈值时，短暂 cooldown

### Cost
- **必须显式分 maker-ish 与 taker-ish 两套口径**
- 若只能 taker 进出，优先假设这条线会被吃死；不要先入为主地乐观

## 8. 下一步怎么测（直接给实验单）
### 实验 A：把 cheap proxy 升级成真正的 microstructure 版
- 数据：Binance / Bybit 公开 depth snapshots + aggTrades / bookTicker
- 频率：`1s ~ 5s` 聚合到 `1m`
- 特征：
  - top-of-book spread
  - microprice
  - queue imbalance
  - trade sign imbalance
  - short-term cancel/refresh proxy
- 目标：验证 paper 里“**81.3% 特征来自 order book**”这句在我们 own pipeline 下是否也成立

### 实验 B：先拆 maker / taker，而不是先调模型
- 对照：
  - 全 taker
  - maker entry + taker exit
  - maker/maker（保守 fill ratio）
- 目标：确认这条线到底是 **预测力不够**，还是 **成本壳太厚**

### 实验 C：confidence threshold 不要只看单阈值
- 至少比较：top `20% / 15% / 10% / 5%`
- 指标：coverage、accuracy、gross edge、net edge、tail loss
- 目标：找到“coverage 跌太快之前，net edge 刚转正”的 admission zone

### 实验 D：单币 vs 多币池
- 先对比 `BTC/ETH` 和 `8~12` 个 liquid majors
- 目标：看这条线更像单币微结构 alpha，还是 cross-asset pooled classifier alpha

## 9. 风险与保留意见
- 这篇 paper 的摘要数字很强，但我这边还没拿到其完整订单簿级复现代码；当前只能算 **高信号候选**，不能当已验证 admission。
- public `5m` kline proxy 太粗，只能当“方向对不对”的 first verdict，不能代表真正 order-book alpha。
- 这条线对成本非常敏感；**如果执行做不到 maker-ish 或半 maker-ish，它很可能不值得上实盘。**
- 低 coverage 是这类策略的天然属性，不要强行追求 always-on。

## 10. 一句话结论
这篇 2025 *Applied Sciences* 论文最值得 desk 收进池子的，不是“又一个神经网络涨跌分类器”，而是这条更诚实的完整 raw alpha 读法：

**`order-book / taker-flow imbalance` 的短周期方向 edge 只有在高 confidence 区域才值得下注；cheap `5m` proxy 已经证明 admission rule 方向是对的，但要过成本，下一步必须上更细 order-book 特征和 maker/taker 拆分。**

## 11. 来源
1. **Kuznetsov, A., Костенко, О., Klymenko, K.O., Hbur, Z., & Kovalskyi, R. (2025). _Machine Learning Analytics for Blockchain-Based Financial Markets: A Confidence-Threshold Framework for Cryptocurrency Price Direction Prediction_. Applied Sciences.**
   - Venue：*Applied Sciences*
   - DOI：`10.3390/app152011145`
   - Readable URL：https://doi.org/10.3390/app152011145
   - Article URL：https://www.mdpi.com/2076-3417/15/20/11145
2. **OpenAlex metadata / abstract record**
   - Readable URL：https://api.openalex.org/works?filter=doi:10.3390/app152011145
3. **Crossref DOI metadata**
   - Readable URL：https://api.crossref.org/works/10.3390/app152011145
4. **Binance USDⓈ-M Perpetual Klines API**
   - Readable URL：https://fapi.binance.com/fapi/v1/klines
5. **本地 proxy artifact**
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/threshold_summary.csv`
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/per_symbol_top20_conf.csv`
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/meta.json`
