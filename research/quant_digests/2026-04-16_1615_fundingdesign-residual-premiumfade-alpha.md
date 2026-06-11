# 别把《Designing funding rates for perpetual futures》只读成定价理论：对 short-cycle desk，更该先拆的是「funding-design residual × premium fade admission」这条 raw alpha

- 时间：2026-04-16 16:15 UTC
- 类型：论文（arXiv 全文）+ Binance public-data portability probe（`15m`）
- 主题类型：raw alpha
- 基础 alpha：`perp-spot premium`（基差）回归；`funding-design residual` 只负责做 admission / veto
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/mean-reversion/funding/basis/perpetual/premium/funding-residual/admission/1m/3m/5m/15m/paper/public-data/cost/risk
- 证据类型：论文证据 + public-data probe

## 1) 这次看了什么
- **Authors**：Jaehyun Kim, Hyungbin Park  
- **Year**：2025（arXiv v1）  
- **Title**：*Designing funding rates for perpetual futures in cryptocurrency markets*  
- **Venue**：arXiv（q-fin.MF）  
- **DOI**：`10.48550/arXiv.2506.08573`  
- **Readable URL**：<https://arxiv.org/abs/2506.08573>  
- **HTML Full Text**：<https://arxiv.org/html/2506.08573v1>  
- **Repo URL**：N/A（论文）

这篇论文最值钱的不是“BSDE 数学细节本身”，而是给了一个可工程化的框架：
**funding 应该是围绕目标价偏差（target - perp）去设计的反馈项**，并且交易所实务上常见的是“过去 8 小时平均”的 path-dependent funding。

## 2) base alpha 先说清（必须先回答）
这篇东西在我们 desk 的 **base alpha** 是：

> **`perp-spot premium` 的短周期回归（short rich perp / long cheap spot，或反向）**。

论文里的 funding 设计思想（尤其是 `funding vs premium` 的偏差）更像 **admission / veto 层**，不是替代 base alpha 的新本体。

## 3) 关键结论（这轮最值钱）
1. 论文给出的核心结构可以翻成交易语言：当 funding 与 premium 的“应有反馈关系”偏离时，说明 anchoring 机制在短期内可能失真，**这恰好可作为基差回归策略的开关条件**。  
2. 我们用 Binance `15m` 公共数据（BTC/ETH/SOL，90 天）做的最小 probe 里，`residual` 极值区间确实能分层：
   - `|res_z|>=2 且 residual 与 premium 反号` 桶：2 小时 gross 均值约 **+1.18 bps**，胜率 **60.0%**（`n=375`）
   - `|res_z|>=2 且 residual 与 premium 同号` 桶：2 小时 gross 均值约 **+0.22 bps**，胜率 **53.5%**（`n=1017`）
3. 但这条 edge 目前仍是“薄 edge”：按 round-trip `14 bps` taker 粗口径，仍明显不过线，说明它更像**可复用 admission 组件**，不是可直接 taker 上线的成品策略。

一句话核心结论：
> **funding 设计残差能帮助“挑交易”，但单独拿来做短周期 taker alpha 仍太薄。**

一句话证明方式：
> 先用论文给的 funding-feedback 思路定义 `residual = funding - κ·premium`，再在 Binance `15m` 公共数据上做分桶事件检验，看不同残差桶对后续 2 小时基差回归收益的分层效果。

## 3.5) 策略拆解（必填）
- 方向属性：相对价值 / 统计套利（perp vs spot）
- 基础 alpha：`premium` 回归
- regime：高波动或公告窗降权（可后续并入）
- filter / veto：`funding-design residual` 分桶（优先交易 `residual` 与 `premium` 反号、且 `|res_z|` 较高）
- risk / sizing / execution overlay：ATR 或波动目标缩放 + 单笔时长上限 + taker/maker 成本门槛

## 4) 可复刻的最小实验（可直接抄）
- **数据源（公开可得）**：
  - Binance `premiumIndexKlines`（`15m`）
  - Binance `fundingRate`（8h）
- **更新频率映射**：
  - premium：`1m/3m/5m/15m` 都可
  - funding：8h 离散更新（前向填充）
- **样本**：BTCUSDT / ETHUSDT / SOLUSDT，近 90 天
- **定义**：
  1. `premium_bps` = premium index × 10,000
  2. `κ` = rolling OLS(funding ~ premium)
  3. `residual` = funding_bps_8h - κ·premium_bps
  4. 事件窗收益：未来 8 bars（2h）
- **优先看 2 个指标**：
  - bucket-level gross mean（bps）
  - bucket-level win rate

## 5) 下一步怎么测（1m/3m/5m/15m）
1. **5m（主战）**：把固定 `|res_z|` 改成分位阈值（如 top/bottom decile），并叠加 `premium_z` 双阈值，只做“高失真 + 高偏离”交集。  
2. **1m/3m（快检）**：围绕 funding 结算前后窗口（如 `[-30,+30]` 分钟）测试 residual 的时变效应，验证是否有更高单笔 edge。  
3. **15m（稳健）**：在 current gate 上加入 maker-first 假设，专门评估 `implementation shortfall`，看能否把薄 edge 从 `gross` 搬到 `net`。  
4. **统一 admission 口径**：输出 `trade_count / gross_bps / net_bps / win_rate / holding_time`，先过成本生存线再谈复杂建模。

## 6) 风险与保留意见
- 当前 probe 是 first verdict，不含完整盘口冲击模型；不能当 production 结论。  
- funding 是离散结算变量，硬当逐 bar 主信号易过拟合；更适合和 premium 本体一起做 gate。  
- `κ` 的稳定性依赖样本与币种，跨资产迁移前必须先做 rolling 稳健性检查。

## 7) 本轮产物
- `reports/artifacts/quant_digests/funding_design_residual_probe_2026-04-16_summary.json`
- `reports/artifacts/quant_digests/funding_design_residual_probe_2026-04-16_trades.csv`
- `reports/artifacts/quant_digests/funding_design_residual_probe_2026-04-16_gatecheck.json`

## 8) 来源
1. Kim, J., & Park, H. (2025). *Designing funding rates for perpetual futures in cryptocurrency markets*. arXiv (q-fin.MF).  
   DOI: <https://doi.org/10.48550/arXiv.2506.08573>  
   Readable URL: <https://arxiv.org/abs/2506.08573>
2. Binance USDⓈ-M Premium Index Klines API（public）: <https://fapi.binance.com/fapi/v1/premiumIndexKlines>
3. Binance USDⓈ-M Funding Rate API（public）: <https://fapi.binance.com/fapi/v1/fundingRate>
