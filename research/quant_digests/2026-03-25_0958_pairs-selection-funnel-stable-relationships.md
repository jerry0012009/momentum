# 别把 pairs 继续只卷 entry 阈值：这篇 2026 新论文更该先偷的是「500+ 币 universe 的稳定选对 funnel」
- 时间：2026-03-25 09:58 UTC
- 类型：2026 SSRN 新论文（摘要级证据）+ Hummingbot 执行框架 + Binance Futures 公共 `1h/15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：对稳定币对/相关币对做 market-neutral spread 均值回归；论文真正新增的是 **pair selection funnel**，不是又一个 entry 小修小补
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/pair-selection/correlation-clustering/stability-diagnostics/hummingbot/cost/binance/crypto/1h/15m/5m/paper
- 证据类型：论文摘要证据 + 工程框架证据 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 就是 pairs / relative-value 的 spread mean reversion，本体很清楚。**

这次值得 intake 的不是“pair trade 也能赚钱”这种老话，而是作者把重点放在：**面对 500+ 币、海量候选对，先怎么筛出“关系稳定、回归更像真的”的那一小撮 pair**。摘要给的主线是：用 **correlation clustering + structural metadata + stability diagnostics** 做多阶段 funnel，再把信号丢进 Hummingbot 实盘化。

对 desk 来说，这正好补上最近 pairs digest 里的一个缺口：我们最近已经反复看了 `cointegration / threshold / timeout / OBI veto / Hurst`，但**还缺一个更系统的“先选谁来交易”前端 funnel**。

## 2. 核心结论
- **一句话核心结论：** 这篇 2026 新论文最值钱的不是又发明一个新 z-score，而是告诉你——**pairs 的 edge 很大一部分来自“先少犯错地选对”，而不是进场线再调 0.2σ。**
- 摘要里最硬的三个信息点：
  - 样本是 **2 年 hourly data**；
  - 覆盖 **500+ coins**；
  - 不是只做回测，而是把策略放进 **Hummingbot** 做回测 + live deployment。
- 作者的 funnel 不是单指标排序，而是三层：
  1. **correlation clustering**：先把天然更相关的一簇资产收拢；
  2. **structural metadata**：再用资产属性/关系做二次约束，避免乱配；
  3. **stability diagnostics**：最后再看谁的相对价值关系更持久、更像能收敛。
- 这和当前 desk 很相关，因为它天然服务于两个痛点：
  - **减少假 pair**：把看起来相关、实际上漂移很快的对先筛掉；
  - **减少无效换手**：让后面的 spread MR 不必在全宇宙乱扫。

## 3. 为什么和当前项目直接相关
- 这是标准的 **raw alpha**，不是 filter / overlay 伪装成本体。
- 它直接服务于我们已经在积累的 pairs / stat-arb 线，但补的是**上游 pair sourcing**，不是继续在下游入场阈值内循环。
- 对短周期 desk 的现实映射也顺：
  - **1h**：做 pair selection / stability 更新；
  - **15m**：做 spread 偏离触发；
  - **5m**：做执行切片、止损、fail-fast。
- 如果这条线成立，它能同时提升：
  - trade count 的质量；
  - 单笔回归可靠性；
  - 组合层并发仓位利用率；
  - cost 之后的生存率。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / pairs / market-neutral mean reversion
- 基础 alpha：`spread_t = log(P_A) - β log(P_B)` 偏离后回归
- regime：只在 pair relationship 稳定、相关结构未崩的窗口里交易
- filter / veto：correlation clustering、metadata 同类约束、rolling corr stability / half-life / spread drift 诊断
- risk / sizing / execution overlay：pair 内 beta-neutral / vol-balanced 配仓；组合层限制同时开仓数与 bucket 暴露；执行层显式计入 4-leg fee、funding、滑点

## 4. 本地最小快检（Binance 公共数据，轻量 proxy，不是论文精确复现）
我补了一个 desk 口径的 probe，只检验一句话：**“稳定选对 funnel”是否比 naive top-corr 更像可交易 skeleton。**

- 数据：Binance USDⓈ-M Futures 公共 `1h` K 线
- 宇宙：**14 个高流动 USDT perp**
- 样本：最近 **1200 根 1h bar**（约 50 天），`900` 根训练、`300` 根测试
- 轻量 funnel：
  - `corr > 0.70`
  - rolling corr stability std `< 0.18`
  - half-life 在 `2~72h`
  - 再加一个粗糙 structural bucket（majors / L1 / payments 等）

### 4.1 结果
- funnel 选出的 8 对主要是：`BTC-ETH`、`ETH-BNB`、`BTC-BNB`、`SOL-AVAX`、`SOL-ADA`、`ADA-APT`、`ADA-DOT`、`AVAX-APT`。
- 对照 naive top-corr 8 对：
  - **稳定 funnel：44 笔** 测试期交易；
  - **naive top-corr：60 笔**。
- 但质量更好：
  - stable funnel 的 **mean pair avg pnl proxy ≈ +78.0 bps**；
  - naive top-corr 只有 **≈ +33.4 bps**。
- 如果粗糙按 **12 bps round-trip** 成本代理：
  - stable funnel 篮子仍是 **正的 gross-to-net proxy**；
  - naive top-corr 篮子则被翻成 **负值**。

翻成人话：**pairs 真不一定输在不会开仓，很多时候是前面先选错了对象。**

## 5. 最小可复现实验（面向 15m / 5m）
- **pair selection 频率**：每 `24h` 或每 `3d` 在 `1h` 数据上重选一次
- **交易频率**：用 `15m` spread z-score 触发，`5m` 执行
- formation：最近 `30~60d` 的 `1h` 数据
- selection baseline：
  1. naive top-corr
  2. top-corr + stability
  3. top-corr + stability + metadata bucket
- entry：`1 < |z_spread| < 2`
- exit：回到均值 / `|z| > 2` / timeout `24h, 48h, 72h`
- cost：先跑 `8 / 12 / 16 / 20 bps RT` 四档
- 核心指标：post-cost expectancy、median hold、expiry ratio、同时开仓数、bucket 集中度

## 6. 下一步怎么测（必须）
1. **先把 pair selection 单独做成 admission module**：不要再把 pairs 研究全堆在 threshold 调参上。  
2. **做 3 组 funnel 对照**：`naive corr` vs `corr+stability` vs `corr+stability+metadata`，看谁的 post-cost 才真的活。  
3. **补 ADF / cointegration / rolling-beta drift**：本地 probe 目前是轻量版，下一轮要把 stationarity diagnostics 补全。  
4. **把 1h 选对 + 15m 触发 + 5m 执行串起来**：这更符合 short-cycle desk，而不是把所有判断都压在同一频率。  
5. **做组合容量实验**：记录“同一 bucket 同时开仓几对”时，收益是否只是重复暴露，不是真的多样化。  
6. **若 funnel 确实改善净值，再谈更花的信号**：先把“选谁交易”做对，再继续卷 Hurst / OBI / dynamic threshold。

## 7. 风险与保留意见
- **主论文目前我拿到的是摘要级证据，不是全文**，所以这篇更适合作为高信号 intake，而不是已经完成 deep dive 的定论。  
- 本地快检里的成本与收益是 **beta-hedged leg-return proxy**，只能用于比较 funnel 相对好坏，不能直接当实盘年化。  
- structural metadata 在真实 500+ 币 universe 里可能非常关键；我这里只做了粗 bucket，属于弱替代。  
- pairs 最后仍会死在 fee / funding / 滑点 / 同类暴露堆叠，不会因为“选对更稳定”就自动变成免费 alpha。

## 8. 来源
1. **Stoikov, S., Xu, D., Shao, S., Wang, Y., Zhang, T., & Hu, J. (2026). _Pairs Trading in Crypto_. SSRN.**  
   - Venue: SSRN / posted-content  
   - DOI: `10.2139/ssrn.6188418`  
   - Readable URL: `https://doi.org/10.2139/ssrn.6188418`  
   - Evidence note: 当前直接可得的是 Crossref 摘要字段，核心摘要包含 `2 years hourly data / 500+ coins / correlation clustering + structural metadata + stability diagnostics / Hummingbot live deployment`  
   - Repo URL: **未见 paper-specific public repo**

2. **Hummingbot Foundation. _Hummingbot_.**  
   - Repo URL: `https://github.com/hummingbot/hummingbot`  
   - Readable URL: `https://hummingbot.org/strategies/`  
   - 作用：论文摘要明确提到作者把策略通过 Hummingbot 平台实现与部署，可作为后续工程化容器参考。

3. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9. 本地复现产物
- `reports/artifacts/quant_digests/pairs_trading_in_crypto_probe_20260325_0948/summary.json`
- `reports/artifacts/quant_digests/pairs_trading_in_crypto_probe_20260325_0948/pair_metrics.csv`
- `reports/artifacts/quant_digests/pairs_trading_in_crypto_probe_20260325_0948/selected_pairs_backtest.csv`
- `reports/artifacts/quant_digests/pairs_trading_in_crypto_probe_20260325_0948/naive_topcorr_backtest.csv`
