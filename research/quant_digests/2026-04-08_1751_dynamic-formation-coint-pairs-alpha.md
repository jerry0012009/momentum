# 别把这篇 2021 arXiv pairs 论文只读成 cointegration 教材：对 short-cycle desk，更该先测的是「dynamic formation lookback × coint spread fade」这条完整 raw alpha
- 时间：2026-04-08 17:51 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：cointegrated spread mean reversion（协整价差回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / cointegration / formation-period / lookback / Johansen / Engle-Granger / 5m / 15m
- 证据类型：论文证据

## 1. 这次看了什么
我看的是 **Masood Tadi, Irina Kortchmeski (2021), _Evaluation of Dynamic Cointegration-Based Pairs Trading Strategy in the Cryptocurrency Market_**。它不是只证明“crypto 里也有配对交易”，而是把更适合我们 desk 的关键问题拆开了：**pair 怎么选、formation lookback 多长、单对做还是 basket 做、成本进来后还剩多少**。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：不是趋势，不是 breakout，而是 **协整关系稳定时，价差偏离后会回归**，所以做 `spread fade`。
- 论文最值钱的地方不是“cointegration 这个词”，而是：**formation / admission 层本身就是 alpha 成败的一半**。同样做价差回归，pair 选错、lookback 选错，绩效会差很多。
- 作者用 **BitMEX 分钟级数据 + bid/ask + market-order fees** 做回测，不是只拿 mid-price 画图；这对 short-cycle desk 比很多纯统计论文更有参考价值。
- 文中周度重选 pair 的单对版本，约 **90% 的月份为正**；平均月收益大约 **17.3%（ADF）/ 13.9%（KSS）**，说明 formation 层做对后，短周期 spread fade 的命中率可以很高。
- 更激进的 **Johansen basket** 版本给出约 **1.44 XBT realized P&L、196% annualized return、24.7% annualized vol、Sharpe 7.94**；这不等于我们能照抄，但很明确地说明：**pair basket + 动态再估计** 比死拿单一 pair 更值得先测。

## 3. 为什么和当前项目有关
这篇和我们当前 `momentum` 主线直接相关，因为它补的是 **raw alpha 素材池里的 pairs / stat-arb 主干件**，而且不是泛泛而谈：
- 它给的是 **完整策略壳**：formation → admission → entry/exit → sizing → fee-aware evaluation；
- 它提醒我们，不要把 pairs 研究只做成“找到协整就上”的静态教材；
- 对 `1m/3m/5m/15m` 来说，最值得迁移的不是论文里的具体 BitMEX 币种，而是：
  1. **rolling formation window**，
  2. **pair/basket 动态重选**，
  3. **先过成本再谈 Sharpe**。

一句话核心结论：**crypto pairs 真能做，但真正决定能不能活下来的，往往不是 z-score 本身，而是 formation lookback 和 admission。**

一句话证明方式：**作者用分钟级 BitMEX 数据、真实 bid/ask 报价与手续费，把单对 / basket / 多种 formation 方案逐个回测比较。**

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral / mean reversion
- 基础 alpha：协整 pair 的 spread 偏离后回归
- regime：只在协整关系仍稳定、half-life 不过长、近窗残差分布没劣化时启用
- filter / veto：formation 期重新筛 pair；ADF / Johansen 显著性不过关、残差方差过大、交易成本覆盖不足时 veto
- risk / sizing / execution overlay：按 hedge ratio 配对；限制单 pair 权重；用 bid/ask + taker fee 计成本；超时未回归则强平

## 4. 可复刻的最小实验
**研究假设**：在 Binance/OKX 流动性较好的 perp universe 里，`rolling formation` 选出的协整 pair，比“固定 pair + 固定 lookback”更有机会在 `5m/15m` 成本后活下来。

**最小定义**：
- universe：`BTC/ETH/SOL/XRP/ADA/LINK/AVAX` 等 liquid majors；
- formation：滚动 `3d / 5d / 7d / 10d` 四档；
- admission：Engle-Granger p-value 过线 + OU half-life 不超过 `96` 根 `15m` bar；
- signal：spread z-score `>|2|` 入场，回到 `0~0.5` 区间离场，或 `1.5 × half-life` 超时离场；
- cost：先用双腿 taker-taker `8~16 bps` 梯度；如果 taker 后死掉，再看 maker-ish execution 有没有救。

**最该先看的 2 个指标**：
1. `post-cost expectancy / trade`
2. `positive window ratio`（rolling 月/周为正比例）

**下一步怎么测**：
先别上复杂 basket。先做一个最小 A/B：
- A：固定 `ETH/SOL` 或 `ETH/XRP` pair + 固定 `7d` formation；
- B：同一 universe 下，每天/每周滚动重选 top-1 pair；
- 比较两者在 `15m` 与 `5m` 的成本后存活率、trade count、回撤斜率。
如果 B 明显更稳，再升级到 top-3 basket。

## 5. 风险与保留意见
- 论文样本是 **2018-2019 BitMEX**，市场结构、币种生态、手续费环境和今天不一样，不能把年化数字直接搬到现货/永续 desk。
- 文中高 Sharpe 说明“这条线值得复现”，不说明“今天还能原样赚”。pairs 在 crypto 特别容易死在 **手续费、funding、pair 失稳、再平衡频率过高**。
- 这篇最该复用的是 **formation / admission 思路**，不是直接迷信某个历史最佳 pair。
- 如果 `5m` 成本后明显转负，不要硬压；这条线很可能更适合 `15m`，或者必须配 maker execution / 更严 admission。

## 6. 来源
- Tadi, M., & Kortchmeski, I. (2021). *Evaluation of Dynamic Cointegration-Based Pairs Trading Strategy in the Cryptocurrency Market*. arXiv / working paper.
- arXiv: `2109.10662`
- Readable URL: `https://arxiv.org/abs/2109.10662`
- PDF: `https://arxiv.org/pdf/2109.10662.pdf`
