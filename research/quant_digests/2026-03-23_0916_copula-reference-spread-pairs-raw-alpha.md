# BTC 参考价差 + Copula 配对交易：这是可独立复现、可直接落地的 `5m/15m` raw alpha 候选
- 时间：2026-03-23 09:16 UTC
- 类型：论文 + 开源补充数据（Binance USDT-M Futures）

- 主题类型：raw alpha
- 基础 alpha：**跨币种相对价值偏离（stat-arb / pairs mean reversion）**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs/stat-arb/relative-value/mean-reversion/copula/cointegration/binance/perpetual/5m/15m
- 证据类型：论文证据 + 本地快检（proxy）

## 1) 这次看了什么（先回答 base alpha）
这篇 2025 论文（Tadi & Witzany）给出的 **base alpha** 很清楚：
> 不是追趋势，而是做“**两条 BTC-reference stationary spread 的相对错价回归**”。

做法是先把每个 alt 对 BTC 构造成价差过程 `S^i_t = BTC_t - β_i * Alt_i_t`，再从这些价差里选配对，用 copula 条件概率当 mispricing 指标，按阈值开平仓。

## 2) 核心结论（可直接拿来做 desk intake）
- 论文主结果在 `5m`（EG 路径）非常强：**总净收益最高 205.9%（α1=0.20）**。
- 同一组 `5m`（EG）下，**年化净收益 56.7% → 75.2%（α1: 0.10→0.20）**，显著好于 `hourly`（51.6% → 35.1%）。
- 风险收益比也给到可执行信号：`5m`（EG）**Sharpe 最高 3.77**；且 RoMaD 为 **3.90 / 4.33 / 6.76**。
- 对照组很关键：传统 return-based/level-based/cointegration baseline 在高频下要么成本侵蚀严重、要么收益风险比显著弱；论文明确显示该 reference-asset copula 方法在其样本里更优。

**一句话核心结论：** 这不是“又一个 filter”，而是一条能独立开仓、独立出场的短周期相对价值 raw alpha。  
**一句话证明方式：** 作者用 Binance 多币种 `5m + hourly` 真正回测（含交易成本对比）并与多种传统配对法做 head-to-head 比较。

## 3) 为什么和当前项目直接相关
我们最近连续多篇是 confirmation/filter/overlay，这篇正好补回 **独立 alpha 主体**，且与当前 desk 的 `5m/15m` 节奏一致：
- 可作为与 breakout/EMA 不同风险来源的“第二引擎”；
- 在趋势失灵（chop）阶段，pairs/stat-arb 往往有机会提供补充收益分布；
- 论文给了明确的 `entry/exit/threshold/cost` 框架，落地门槛比纯理论论文低。

## 3.5) 策略拆解（必填）
- 方向属性：相对价值 / 配对统计套利（均值回归）
- 基础 alpha：跨币种相对错价回归（BTC 参考价差 + copula mispricing）
- regime：可加 `trend/chop` 门控，但不是必需前提
- filter / veto：候选对必须先过“参考价差可交易性”筛选（论文是 EG/KSS cointegration + Kendall tau 排序）
- risk / sizing / execution overlay：
  - 每腿名义资金上限（论文示例约 20,000 USDT/腿）
  - 周内固定 `Q1/Q2`，周初重算
  - taker 成本计入（Binance USDT-M taker 0.04%）

## 4) 可复刻的最小实验（下一步怎么测）
**研究假设：** 在 `15m` 上保留“BTC 参考价差 + 条件错价阈值”框架，仍能形成可交易的 pair universe，且成本后优于简单 z-score 配对。  

**最小可计算定义（MVP）：**
1. 数据：Binance USDT-M，`BTC + 19 alt`；
2. 形成期/交易期：`3周形成 + 1周交易` 滚动；
3. 候选筛选：先做参考价差稳定性筛选（正式版用 EG；MVP 可先 proxy）；
4. 信号：
   - 开仓：`mispricing_prob > 0.5 + α1` 或 `< 0.5 - α1`（先试 α1=0.10/0.15/0.20）
   - 平仓：回到 `0.5 ± α2`（先固定 α2=0.10）
5. 交易：next-bar 执行，双边 taker 成本，no-overlap。

**先看 4 个指标：** `post_cost_ann_return`、`Sharpe`、`max_drawdown`、`turnover/cost_ratio`。

**本地快检（15m proxy，仅验证可交易候选供给，不等同正式 EG+copula 回测）：**
- 样本：2022-07-23 ~ 2023-01-19（`15m`，17,281 bars）
- 周扫描：22 周里，`>=2` 候选周占比 **100%**
- 每周候选中位数：**18**
- 入选对 top1/top2 的 |Kendall tau| 中位数：**0.755 / 0.714**

## 5) 风险与保留意见
- 我们本地快检目前只是 **proxy 可交易性筛选**，不是论文原版 EG/KSS + copula 全量复刻，不能拿来替代正式绩效结论。
- 论文样本是 2021–2023；落地前必须做 2024–2026 延长样本 + 手续费/滑点敏感性。
- KSS 路径在论文里高频回撤很差（5m 下甚至出现 >160% 级别极端回撤），上线前需强制风控阈值与 kill-switch。

## 6) 来源
1. **Tadi, M., & Witzany, J. (2025). _Copula-based trading of cointegrated cryptocurrency Pairs_. Financial Innovation.**
   - DOI: https://doi.org/10.1186/s40854-024-00702-7
   - Readable URL: https://link.springer.com/article/10.1186/s40854-024-00702-7
   - Repo URL: N/A（论文未提供官方代码仓库）
2. **Paper Supplementary Data (CSV, public): 5m / hourly close prices for 20 Binance USDT-M contracts**
   - Readable URL: https://static-content.springer.com/esm/art%3A10.1186%2Fs40854-024-00702-7/MediaObjects/40854_2024_702_MOESM1_ESM.csv
   - Repo URL: N/A（期刊补充材料）
3. **Binance USDⓈ-M Futures API（可替代补充数据源）**
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - Repo URL: https://github.com/binance/binance-futures-connector-python

## 7) 本地复现产物
- `reports/artifacts/quant_digests/copula_reference_pairs_20260323/weekly_proxy_candidate_scan_15m.csv`
- `reports/artifacts/quant_digests/copula_reference_pairs_20260323/summary.json`
