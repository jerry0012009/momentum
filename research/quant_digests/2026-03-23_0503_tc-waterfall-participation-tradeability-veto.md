# 别把 15m 成本只写成固定手续费：这份新 repo 里更值钱的是 `commission→spread→impact` 瀑布与 participation veto
- 时间：2026-03-23 05:03 UTC
- 类型：GitHub 仓库（Jupyter 回测）
- 主题类型：overlay
- 基础 alpha：breakout / fib retest / ema-psar（既有 setup，交易性约束）
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/transaction-cost/market-impact/adv/participation/risk-overlay/veto/repo/crypto/5m/15m
- 证据类型：工程证据（公开 notebook + 公共数据回测输出）

## 1. 这次看了什么
这次不再盯“新入场形态”，而是从 **BNeillDickey (2026)** 的公开 notebook 里抽一个更适合 desk 的旁支：**同一套日内信号，为什么在 spot crypto 被冲击成本打穿，而在 ETF 还能活**。

## 2. 核心结论
- **一句话核心结论：** 对我们 15m 三条收口线来说，下一步更该先测的不是再炼 admission 细节，而是把 `impact / ADV participation` 做成 shared tradeability veto（至少先做 size gate）。
- **一句话说明它怎么证明：** 该 repo 把交易成本拆成 `commission + spread + square-root impact`，并用 time-varying ADV 过滤后做容量与压力测试，直接给出成本瀑布而不是只报“净值曲线好看”。
- repo 的 spot close-window 里，测试期 gross alpha 约 **24.0 bps/day**、gross SR **5.85**；但扣完成本后关键矛盾是 impact：
  - 佣金后还算能活（文中给到 SR 约 +4.02）；
  - 佣金+点差后只剩约 **2.6 bps/day** 预算；
  - 实际 impact 约 **97.0 bps/day**，约是剩余预算的 **37x**，把策略直接打穿。
- 这不是“仓位太大才出问题”：repo 还报告即便很小 notional，mid-cap 参与率带来的冲击仍主导；而 ETF 侧因为 ADV 充足，impact 基本可忽略。
- 对 desk 的含义很直接：**先判断能不能交易（tradeability），再谈 follow-up / retest / EMA-PSAR admission 的细节。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：很多“看起来该追”的信号，真实问题可能不是方向错，而是冲击后 R 不够；应先过 participation veto 再放行 follow-up。
- 对 `Fibonacci confirmation / retest_hold`：回踩确认常发生在流动性更薄的次级时段，若不加 ADV/impact 约束，容易把“确认层”误写成“高成本层”。
- 对 `EMA / PSAR raw alpha focus`：这条线现在最缺的是成本后生存口径。把 `impact budget` 放到主流程里，比继续加一个形态过滤更接近 OOS 真问题。

## 3.5 策略拆解（必填）
- 方向属性：不改方向信号；属于 execution / risk overlay
- 基础 alpha：沿用 breakout-short / Fib retest_hold / EMA-PSAR 原始触发
- regime：按 liquidity/ADV bucket 切分（high / mid / low liquidity）
- filter / veto：`expected_edge_bps - (commission+spread+impact_est)` 必须为正
- risk / sizing / execution overlay：按 participation 桶做 `1.0 / 0.5 / 0` 仓位缩放

## 4. 可复刻的最小实验
### 研究假设
给三条 15m 主线加一个统一 `tradeability gate`（不是改方向），能显著改善 post-cost expectancy 与回撤质量，且不会靠过度砍单伪改善。

### 一个可计算定义
- 数据：
  - 交易信号：现有 breakout/Fib/EMA-PSAR 15m 事件；
  - 市场数据：Binance 1m/5m 成交额（聚合到 15m）估算 rolling ADV。
- 每笔候选单估算：
  - `tc_comm_bps = fixed`
  - `tc_spread_bps = bucket_spread`
  - `tc_impact_bps = k * sqrt(order_notional / ADV_30d)`
  - `net_edge_proxy = expected_edge_bps - tc_comm_bps - tc_spread_bps - tc_impact_bps`
- 规则：
  - `net_edge_proxy <= 0` → veto
  - `0 < net_edge_proxy <= x` → half-size
  - `> x` → full-size

### 最小回测切口
- 标的：BTC / ETH / SOL perpetual
- 周期：15m（可用 5m 执行价近似滑点）
- 样本：近 180d
- 成本梯度：6 / 10 / 15 bps + impact proxy
- 对照：baseline vs +tradeability gate

### 第一轮先看
- post-cost expectancy
- `false_follow_through_after_cost`（特别是 breakout-short）
- trade retention（确认不是靠砍掉大多数单）
- cost-to-gross-alpha ratio

## 5. 风险与保留意见
- 该证据来自工程 notebook，不是同行评审主文；可用于“先做可复现 gate”，不宜直接当最终参数。
- impact 估算依赖 `k` 与 ADV 口径，跨交易所会漂移；第一轮应把它当风险闸门，不要当精确预测器。
- ETF 与 crypto perpetual 的微观结构不同，不能直接搬绝对 bps，只能迁移“成本瀑布框架”。

## 6. 来源
1. **BNeillDickey (2026). _Intraday Return Reversals and Momentum Around the US Equity Session in Cryptocurrency Markets_. GitHub repository / Jupyter Notebook.**
   - Authors / Year / Title / Venue: BNeillDickey / 2026 / 同上 / GitHub Repository
   - DOI: N/A
   - Readable URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project
   - Repo URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project
   - Notebook URL: https://github.com/BNeillDickey/intraday-crypto-reversal-project/blob/main/Intraday_Crypto_Reversal_Project.ipynb
2. **Binance USDⓈ-M Futures Market Data API（用于最小实验的数据口径）**
   - 数据源：Binance Developers
   - 公开性：公开可得
   - 更新频率：分钟级
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
3. **Yahoo Finance / yfinance（repo 中 ETF 分钟/小时数据来源）**
   - 数据源：Yahoo Finance Chart API / yfinance
   - 公开性：公开可得
   - 更新频率：分钟/小时（受历史窗口限制）
   - Readable URL: https://finance.yahoo.com/
