# 别把 US 时段流量只当 ETF 延续：这份 2026 新仓库更适合我们先复现的，是 spot crypto 的横截面日内反转 raw alpha
- 时间：2026-03-23 10:23 UTC
- 类型：GitHub 新仓库（完整研究笔记）+ 经典论文链路 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-sectional intraday reversal（按 US 时段窗口做“当窗赢家-输家”反向组合）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/intraday/reversal/momentum/session-effect/spot-crypto/etf/transaction-cost/impact/5m/15m
- 证据类型：工程证据 + 文献证据 + 本地快检（可复现）

## 1. 这次看了什么
这次主看 **BNeillDickey (2026)** 新仓库 *intraday-crypto-reversal-project*。它的 **base alpha** 很清楚：
**在固定 US 时段窗口内，按 30 分钟收益做横截面排序，做“多输家、空赢家”的日内反转组合（美元中性）**，并明确给出 entry/exit/cost/impact。

## 2. 核心结论
- **一句话核心结论：** 这份材料最值钱的不是“某个指标”，而是一条可独立落地的 `cross-sectional intraday reversal` 完整策略骨架。  
- **一句话证明方式：** 仓库用 5 年样本、固定时段窗口、三段成本模型（commission+spread+impact）和 ADV 过滤，把“有信号”和“可交易”分开检验。  
- 仓库给出的 spot close-window 结果：**gross Sharpe 5.85、gross alpha 24.0 bps/day**；morning-window：**gross Sharpe 7.29、gross alpha 22.8 bps/day**。  
- 但同一仓库也明确：加完整成本后，策略会被冲击成本严重侵蚀（作者报告里 impact 远大于剩余 alpha budget），所以它是 **raw alpha 有信息、执行层很难** 的典型。  
- 这和我们 desk 当前目标高度匹配：它属于独立 raw alpha 家族（不是 breakout 配件），且天然可拆成 `alpha 本体 + 可交易性/容量 overlay` 两层。

本地最小快检（Binance Spot 公共数据，20 个主流 USDT 对，15m，2025-12-01~2026-03-23；每日日内 decile 多空，美元中性）结果：
- **morning 窗口**（信号 13:30–14:00，持有 14:15–14:45 UTC）：`+0.33 bps/day`，Sharpe `0.17`（112 天）
- **close 窗口**（信号 19:30–20:00，持有 20:15–21:00 UTC）：`-0.92 bps/day`，Sharpe `-0.54`（112 天）
- 当前读法：主流大币口径下，横截面反转并不强；要想让这条 raw alpha 活下来，重点应转向 **中盘可交易宇宙、成本与容量约束、执行方式**，而不是继续把它当“无摩擦 alpha”。

## 3. 为什么和当前项目直接相关
- 它直接扩充了我们稀缺的 **raw alpha 素材池**：`cross-sectional / relative-value / intraday`，不依附现有 breakout 主线。
- 它自带完整策略结构：信号窗口、持有窗口、组合构建、成本模型、容量约束，能直接进入复现流水线。
- 它还能反向服务我们当前研发节奏：当 raw alpha 在大币上偏弱时，下一步该补的是 **universe 与 execution**，不是先堆更复杂过滤器。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值（同窗赢家-输家反转）
- 基础 alpha：按窗口收益 `r_signal` 排序，long bottom decile、short top decile，做下一窗口回归
- regime：优先在“流动性仍可承接、时段流量集中”的窗口开机
- filter / veto：ADV 过低、点差异常、重大事件窗、单日横截面可交易资产数不足
- risk / sizing / execution overlay：美元中性、单币权重上限、分层费率+点差+冲击成本、容量上限与 participation cap

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** US 时段横截面反转在 crypto 并非普适，但在“中盘且流量聚集窗口”可能形成可交易 pocket。  
- **最小定义：**
  - 频率：先 `15m`，再下钻 `5m/3m`
  - 信号：`r_signal = close(t2)/open(t1)-1`（固定 30 分钟窗口）
  - 组合：long bottom 10%、short top 10%，美元中性
  - 出场：固定下一窗口平仓 + `max_hold` 超时保护
  - 成本：至少先加 `commission+spread`，第二步再加 `sqrt(参与率)` 冲击
- **最小回测切口：**
  - Universe A：前 20 主流币（建立“是否有 alpha”下限）
  - Universe B：中盘且可交易币池（建立“是否有容量”上限）
- **优先看 4 个指标：** `post-cost bps/day`、`turnover/day`、`capacity@participation cap`、`rolling Sharpe`。

## 5. 风险与保留意见
- 该策略最容易死在 **成本与冲击**，不是死在“有没有统计信号”。
- ETF 与 spot microstructure 不同，不能把 ETF 的窗口结论直接迁移到 24/7 spot/perp。
- 我们本地快检目前是主流大币口径，结论更偏“保守下限”；是否存在可交易 pocket 仍需中盘宇宙验证。

## 6. 来源
1. **BNeillDickey. (2026). _intraday-crypto-reversal-project_. GitHub repository.**  
   - Repo URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project  
   - Readable URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project
2. **Heston, S., Korajczyk, R., & Sadka, R. (2010). _Intraday Patterns in the Cross-Section of Stock Returns_. Journal of Finance.**  
   - DOI: `10.1111/j.1540-6261.2010.01564.x`  
   - Readable URL: https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2010.01564.x
3. **Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). _Market Intraday Momentum_. Journal of Financial Economics.**  
   - DOI: `10.1016/j.jfineco.2018.02.001`  
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X18300743

## 7. 本地复现产物
- `reports/artifacts/quant_digests/intraday_cs_reversal_20260323/summary.csv`
- `reports/artifacts/quant_digests/intraday_cs_reversal_20260323/daily_window_returns.csv`
- `reports/artifacts/quant_digests/intraday_cs_reversal_20260323/run_meta.txt`
