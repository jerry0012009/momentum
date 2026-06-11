# 别把 crypto momentum 只做横截面排名：这篇 2024 论文更该先复现的是「市场分位状态 TSMOM（top-third long / bottom-third short）」完整骨架
- 时间：2026-03-24 10:30 UTC
- 类型：近 5 年论文（全文 PDF）+ Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：市场组合自身过去收益分位状态驱动的时间序列动量/反转（TSMOM state strategy）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/time-series/percentile-state/market-portfolio/long-short/regime/cost/crypto/1m/3m/5m/15m/paper
- 证据类型：论文实证 + 本地最小快检（可复现）

## 1) 先回答：这篇东西的 base alpha 是什么？
**base alpha = 市场组合 own-past return 的“分位状态持续性”**：
- 当 lookback 收益落在历史分布 top-third，做多市场组合；
- 当 lookback 收益落在历史分布 bottom-third，做空市场组合；
- 中间状态空仓。

它是可独立运行的 raw alpha，不依赖额外外部因子先验。

## 2) 这次看了什么
主材料：
- **Han, Kang, Ryu (2024)**《Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions》

这篇对 desk 的价值点不是“又一篇 momentum 综述”，而是它把完整策略链路写清楚了：
- entry：按历史分位（top-third / bottom-third）入场
- exit：按持有期滚动退出（并测试不同 holding）
- sizing：分布式进场（降低 weekday 偏置）
- risk：显式看 MDD / liquidation risk
- cost：交易费与可交易性前提都写进框架

## 3) 核心结论（给 desk 的短答案）
- **一句话结论：** 这条线值得进入 raw alpha 素材池，尤其适合做 `15m` 的“可切换多空”骨架；但直接压到 `5m` 容易被噪音+换手+成本吃掉。  
- **一句话原因：** 论文在日频给出可复现的完整结构，我做的最小快检也看到“15m 可工作、5m 易失效”的分层。

关键数据点：
1. **论文（2014-01~2023-08，日频）**：`(j=28, k=5)` long-only 的 **Sharpe=1.51**（成本后），高于市场 buy&hold 的 **0.85**。  
2. **论文同口径**：cross-sectional momentum 明显更弱（21 组里 5 组被清算，且很多“均值收益显著”组合在 log-return 口径下并不赚钱）。  
3. **本地快检（Binance perp 等权 5 币市场代理）**：
   - `15m`（6000 bars，4bps/次换手）：long-short **净 +11.77%**，Sharpe **1.43**；
   - `5m`（15000 bars，同费率）：long-short **净 -42.77%**，Sharpe **-6.83**。  
   说明这条 alpha 对频率与交易成本非常敏感。

## 4) 与当前短周期（1m/3m/5m/15m）的关系
- 对 `15m`：可作为**独立运行**的趋势/状态 raw alpha（不是只做 filter）。
- 对 `5m`：更像需要强执行约束后才能生存（否则高换手吞噬边际）。
- 对 `1m/3m`：建议先当“实验频段”，优先做成本与成交约束压力测试，不建议直接当主生产频段。

## 5) 最小可复现实验（已给出可跑口径）
### 数据源（公开可得）
1. Binance USDⓈ-M Klines API：`/fapi/v1/klines`
   - 公开性：公开接口（无需 key）
   - 更新频率：1m/5m/15m 可直接取
2. Binance 官方 API 文档
   - 公开性：公开文档
   - 用途：字段定义、限频与口径对齐

### 最小实验口径
- 市场代理：`BTC/ETH/SOL/BNB/XRP` 等权组合收益
- 规则：
  - lookback `j=28 bars`
  - holding `k=5 bars`（分布式进场）
  - top-third long，bottom-third short
  - 交易成本：4 bps × 换手
- 输出：
  - long-only / short-only / long-short 三条净值
  - mean bps/bar、Sharpe、MDD、active ratio、turnover

## 6) 这次本地产物
- `reports/artifacts/quant_digests/tsmom_toptercile_percentile_probe_20260324/summary.json`
- `reports/artifacts/quant_digests/tsmom_toptercile_percentile_probe_20260324/signal_frame_15m.csv`
- `reports/artifacts/quant_digests/tsmom_toptercile_percentile_probe_20260324/signal_frame_5m.csv`
- `reports/artifacts/quant_digests/tsmom_toptercile_percentile_probe_20260324/market_percentile_tsmom_probe.py`

## 7) 风险与保留意见
- 本地快检窗口偏短（近 2 个月量级），只用于 **admission 级别**，不用于宣布稳定 alpha。  
- 15m 与 5m 的结果分裂，提示“频率映射不是线性缩放”，必须做 walk-forward 与多窗口复核。  
- 当前还是市场代理（basket）口径，下一步要加入真实执行假设（taker 比例、滑点、成交失败）。

## 8) 下一步怎么测（具体动作）
1. **先做频率迁移网格**：固定 state 规则，跑 `1m/3m/5m/15m` + 费用梯度（4/8/12bps），找净边际拐点。  
2. **做 regime-aware 开关**：只在“波动/趋势达标”状态启用 short leg，验证能否降低 15m 的回撤。  
3. **做执行诚实化**：加入 taker 占比、最小名义成交额、participation 上限，重算净 bps。  
4. **做 OOS/WFA**：按月滚动训练-验证-测试，避免把单段行情当结构性结论。

## 9) 来源（paper / docs）
1. **Chulwoo Han, Byeongguk Kang, Jehyeon Ryu (2024). _Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions_. SSRN Electronic Journal.**  
   - Venue: SSRN Electronic Journal  
   - DOI: `10.2139/ssrn.4675565`  
   - Readable URL: https://doi.org/10.2139/ssrn.4675565  
   - PDF URL: https://quanticfund.net/wp-content/uploads/2024/05/SSRN-id4675565.pdf  
   - Repo URL: N/A（paper-only）
2. **Binance Developers (official docs). _USDⓈ-M Futures API Docs_.**  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
