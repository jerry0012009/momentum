# Volatility Managed Portfolios：先管仓位，再谈 alpha
- 时间：2026-03-10 06:08 UTC
- 类型：论文
- 主题标签：volatility / risk / position-sizing / trend
- 证据类型：论文证据 + 工程经验

## 1. 这次看了什么
这次看的核心是 Moreira & Muir 的论文 **Volatility Managed Portfolios**，再配一篇 Man Institute / Quantpedia 的实践型总结。它们讨论的不是“怎么发明新因子”，而是：**同一个因子或策略，在高波动时少做、低波动时多做，风险收益比会不会更好。**

## 2. 核心结论
- 论文证据：对 market、value、momentum 等多类因子，按波动率动态缩放仓位后，Sharpe ratio 往往提升；原因是波动上升并没有被同等幅度的预期收益上升所补偿。
- 实践结论：volatility targeting 往往会在高波动时自动降杠杆、低波动时放大敞口，因此常见效果不是“绝对收益一定更高”，而是**左尾更薄、回撤更稳、波动更平滑**。
- 对趋势系统尤其重要：很多趋势/突破策略最难受的阶段，不是“信号完全错”，而是**信号本来就脆弱时还用固定大仓位硬扛高波动**。
- 重要保留：现有强证据主要来自股票、信用、部分因子组合，并不是对 **Crypto 15m** 的直接证明；把这个思想迁移到短周期加密，仍然需要你自己回测验证。

## 3. 为什么和当前项目有关
它和 `momentum` 当前主线非常相关，因为你现在已经有多个“方向层 + 触发层 + 确认层”的模板，但**风险层**还没有被单独系统化。这个主题更像：
- 风控/执行层改进
- 候选模块：`ATR position sizing`
- 方法论提醒：不要只盯着“信号对不对”，还要看“仓位是不是在最差的时候开得太大”

换句话说，它不是给你一个新 alpha，而是帮你判断：**现有 alpha 能不能活得更久。**

## 4. 可复刻的最小实验
- 研究假设：对同一个 15m 趋势模板，加入波动率缩放后，成本后收益未必显著提高，但 max drawdown 和收益曲线平滑度可能改善。
- 一个可计算定义：
  - 基线：固定名义仓位 `position = 1.0`
  - 波动率缩放版：`position_t = clip(target_vol / rv_t, min_pos, max_pos)`
  - 如果你想先和现有工程兼容，可先用 ATR 近似：`position_t = clip(atr_ref / ATR_t, 0.5, 1.5)`
- 最小回测切口：
  - 模板：`ema_donchian_breakout`
  - 资产：BTC, ETH, SOL
  - 周期：15m
  - 样本：近 180d，至少做一次 OOS split + rolling
- 最该先看：
  1. `max_drawdown`
  2. `post_cost_return`
  - 辅助再看：`positive_window_ratio`

## 5. 风险与保留意见
- 波动率缩放容易“卖飞”强趋势：如果波动突然变大但趋势继续延续，它会因为主动降仓而少赚。
- 短周期里交易成本更敏感；若仓位缩放过于频繁，可能会被手续费和滑点吃掉改善。
- ATR 缩放与论文里的 realized volatility scaling 不是一回事；ATR 更适合做工程上的第一近似，不应说成“论文已证明 ATR sizing 有效”。
- 如果策略本身没有 edge，vol targeting 只能改善曲线形态，**不能把坏策略变成好策略**。

## 6. 来源
- Moreira, A., & Muir, T. (2016/2017). *Volatility Managed Portfolios* (NBER Working Paper 22208): https://www.nber.org/papers/w22208
- Man Institute. *The Impact of Volatility Targeting*: https://www.man.com/insights/the-impact-of-volatility-targeting
- Quantpedia. *An Introduction to Volatility Targeting*: https://quantpedia.com/an-introduction-to-volatility-targeting/
