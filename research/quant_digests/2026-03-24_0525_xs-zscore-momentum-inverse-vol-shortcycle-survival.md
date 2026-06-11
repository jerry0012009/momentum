# 别把这份仓库只当 residual MR：更该先测的是「XS z-score momentum + inverse-vol gate」raw alpha，但短周期先被成本吃掉
- 时间：2026-03-24 05:25 UTC
- 类型：2024 GitHub 仓库 + 本地独立最小复核 + 论文地基
- 主题类型：raw alpha
- 基础 alpha：cross-sectional z-score momentum（做多短窗相对强势币、做空相对弱势币），并用 inverse-vol gate 控制开机时段
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前 `5m/15m` 映射口径下未过成本线）
- 主题标签：raw-alpha/cross-sectional/momentum/trend/inverse-volatility/regime-gate/cost-survival/binance/perp/crypto/5m/15m/repo/paper
- 证据类型：仓库代码 + 公共行情最小复核 + 文献地基

## 1. 这次看了什么
先回答 base alpha：**不是 filter，本体就是 XS momentum**。这次主看 `briplot/systematic-crypto-strategy` 里之前没被单独消化的分支：`z-score momentum + inverse volatility filter`。它和我们昨天 intake 的 residual MR 属于同一仓库，但不是同一 alpha 家族，正好补当前 desk 的 trend/momentum raw-alpha 侧。

## 2. 核心结论
- **一句话结论：** 这条线在仓库日频口径里“像 alpha”，但压到我们关心的 `15m/5m` 后，**毛边不差、净值先死**；最需要先复现的不是“再找最优窗口”，而是 `换手-成本-调仓频率` 生存线。  
- **一句话怎么证明：** 按仓库同构公式（`z-score -> tanh -> 横截面归一`，并保留 inverse-vol gate）在 Binance USDT perp 公共 K 线上做最小复核，直接对比 `gross` 与 `post-cost`。

关键数据点（本地最小复核）：
1. `15m`（10 币，4500 bars）：最好 gross 约 **+0.826 bps/bar**（`short=24,long=96,th=1.25`），但在 **4 bps 成本**下同参数 net 约 **-0.645 bps/bar**，年化 Sharpe 为负。  
2. `15m` 全参数网格里，**4 bps 下最佳 net 仍为 -0.481 bps/bar**（`short=48,long=288,无 vol gate`），说明不是“参数没调好”，而是当前频率与成本错配。  
3. `5m`（10 币，4500 bars）：gross 最高仅约 **+0.093 bps/bar**，在 4/8/12 bps 成本下全部显著转负；turnover 约 **0.24~0.32/bar**，成本侵蚀强于信号优势。

## 3. 为什么和当前项目直接相关
- 这是明确的 **raw alpha intake**，不是再写一个解释层。  
- 它直接服务我们当前缺口：`trend / momentum` 在短周期下怎么活，而不是继续只补 MR/stat-arb。  
- 更关键的是：它天然可以拆成完整策略组件并进入实盘前评审：
  - entry：横截面 z-score 排序建多空权重  
  - exit：按 bar 频率重平衡（或低频重平衡）  
  - sizing：横截面归一 + 杠杆上限  
  - risk：vol gate / 黑窗 / 单币权重上限  
  - cost：fee+slippage 随换手显式入账

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / market-neutral momentum
- 基础 alpha：相对强弱的短窗延续
- regime：低到中波动、横截面分化不塌缩时更友好
- filter / veto：inverse-vol gate（`rolling_vol < long_vol_mean * threshold`）
- risk / sizing / execution overlay：调仓节流、最小权重阈值、参与率上限、成本阶梯评估

## 4. 与 `1m/3m/5m/15m` 的关系
- `15m`：可作为 first-verdict 主频率；当前显示“毛利存在但净值被换手吞噬”。
- `5m/3m/1m`：不建议直接复制；在当前口径下频率越高，成本死亡越快。
- 对 desk 的正确定位：**这是可独立复现的 raw alpha 候选，但短周期要先做“低换手化改造”才有生存可能。**

## 5. 最小可复现实验口径
- 数据源：Binance USDⓈ-M Futures klines（公开 REST，无需 key）
- 公开性：公开可得
- 更新频率：交易所 bar 级（可映射 `1m/3m/5m/15m`）
- 本轮口径：
  - 币池：`BTC, ETH, BNB, SOL, XRP, DOGE, ADA, LINK, LTC, BCH`
  - 15m：4500 bars（`2026-02-05 -> 2026-03-24`）
  - 5m：4500 bars（`2026-03-08 -> 2026-03-24`）
  - 信号：`z=(short_mean-long_mean)/long_std -> tanh -> CS normalize`，持仓滞后 2 bars
  - 成本：`4/8/12 bps * turnover`

## 6. 下一步怎么测（必须）
1. **先做调仓节流**：从“每 bar 重平衡”改成 `every 3/6/12 bars`，同口径复测 `net bps` 与 turnover。  
2. **做权重截断**：只交易 |z| 前 `K` 名（如 2/3/4），其余权重归零，检验“少交易是否能保住 edge”。  
3. **做分层开机**：仅在 `cross-sectional dispersion` 高分位启用，低分位停机，验证是否能提升成本后存活率。  
4. **做成本反推阈值**：输出每组参数的 break-even bps，作为 paper-trading 前置准入门槛。  
5. **再决定是否进 shadow**：若 `15m` 在 4 bps 仍无法转正，先不升实盘队列。

## 7. 风险与保留意见
- 目前样本偏短（尤其 5m 仅约半个月），只能算 first verdict。  
- 仓库原始结论基于日频，直接压短周期会放大微观成本与冲击。  
- 当前复核未纳入资金费率与盘口冲击模型，实盘净值只会更苛刻。

## 8. 来源
1. **Plotnik, B. (2024). _systematic-crypto-strategy_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/briplot/systematic-crypto-strategy  
   - Repo URL: https://github.com/briplot/systematic-crypto-strategy  
2. **Plotnik, B. (2024). _classproject_brianplotnik.ipynb_（仓库内策略实现）.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/briplot/systematic-crypto-strategy/main/classproject_brianplotnik.ipynb  
   - Repo URL: https://github.com/briplot/systematic-crypto-strategy/blob/main/classproject_brianplotnik.ipynb  
3. **Liu, Y., Lu, X., & Wang, J. (2021). _Asymmetry, tail risk and time series momentum_. International Review of Financial Analysis.**  
   - Venue: International Review of Financial Analysis  
   - DOI: https://doi.org/10.1016/j.irfa.2021.101938  
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S1057521921002458  
   - Repo URL: N/A  
4. **Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). _Time Series Momentum_. Journal of Financial Economics.**  
   - Venue: Journal of Financial Economics  
   - DOI: https://doi.org/10.1016/j.jfineco.2011.11.003  
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X11002613  
   - Repo URL: N/A  
5. **Binance Developers. _USDⓈ-M Futures Market Data: Kline/Candlestick Data_.**  
   - Venue: Official Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 9. 本地复现产物
- `reports/artifacts/quant_digests/zscore_momentum_inverse_vol_20260324/summary_15m.csv`
- `reports/artifacts/quant_digests/zscore_momentum_inverse_vol_20260324/summary_5m.csv`
- `reports/artifacts/quant_digests/zscore_momentum_inverse_vol_20260324/meta.json`