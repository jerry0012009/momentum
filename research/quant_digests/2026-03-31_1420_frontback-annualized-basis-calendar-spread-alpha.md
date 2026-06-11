# 别把这份 2026 新 repo 只看成 BTC curve 回测：更该先测的是「front-vs-back annualized basis 收敛 × regime-aware calendar spread」完整 raw alpha
- 时间：2026-03-31 14:20 UTC
- 类型：GitHub 仓库源码审阅
- 主题类型：raw alpha
- 基础 alpha：BTC 近月/远月期货年化 basis 的期限结构均值回复（calendar spread mean reversion）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw alpha / relative value / stat-arb / calendar spread / term structure / basis / btc / futures / 15m / 5m / repo / public-data / cost
- 证据类型：工程经验

## 1. 这次看了什么
看了 `abailey81/Crypto-Statistical-Arbitrage` 这个 2026 GitHub 仓库的 `strategies/futures_curve` 模块，重点审了 `__init__.py`、`calendar_spreads.py`、`futures_walk_forward.py`。README 里写了 BTC futures curve 策略 Sharpe `5.81`、总收益 `203.70%`、最大回撤 `0.89%`、总交易 `44,652`，这些绩效先不要信；真正有价值的是：它把 entry / exit / sizing / risk / walk-forward 骨架都公开了，足够我们做一轮诚实的 first verdict。

## 2. 核心结论
- 这篇东西的 **base alpha** 很清楚：不是 generic funding carry，而是 **BTC 期限结构过陡后的近远月年化 basis 收敛**。换句话说，赌的是 curve mean reversion，不是赌 BTC 单边方向。
- 代码里给出的主规则很完整：`avg_basis > 15%` 且处于 contango 时，做 **long near / short far**；`avg_basis < -10%` 且处于 backwardation 时，反向做 **short near / long far**。这已经是完整 raw alpha，不只是 filter。
- 出场也写得很清楚：long calendar 在 basis 回落到 `5%` 附近止盈，short calendar 在 basis 回升到 `-3%` 附近止盈；若 basis 继续朝不利方向多走 `5%`，或者 near DTE `< 7`、持有 `> 90` 天，就强制离场。
- 风控/仓位不是空白：默认最大仓位上限来自 `max_position_pct=25%`，再乘 `signal_strength × liquidity × regime_multiplier`；危机期再乘 `0.3`，并加 venue capacity 上限。这说明它不是“有信号没执行壳”的半成品。
- 对当前 desk 更重要的价值，是它补的是 **期限结构 / 日历价差** 这条 raw alpha 支线。我们最近已经积累了很多 funding、pair spread、lead-lag、XS reversal/momentum，但 **front-back curve MR** 明显还不够密。
- **一句话核心结论**：当 BTC dated futures 的整条曲线过于陡峭时，先别只盯 funding，直接测 near-far 年化 basis 的收敛，可能更像一个能独立下单的相对价值 alpha。
- **一句话证明方式**：这个判断不是靠摘要吹出来的，而是靠 repo 源码里明确的阈值、止盈止损、DTE 约束、仓位规则和 walk-forward 外壳撑起来的。

## 3. 为什么和当前项目有关
当前 `momentum` 项目已经不缺“再来一个 breakout / retest / funding ranking”的 intake；更缺的是 **能直接扩充 raw alpha 素材池、且与现有素材不完全同质** 的方向。这个主题的好处有三点：
- 它是 **relative-value / stat-arb**，不是再做一篇单边趋势；
- 它天然能映射到 `15m` 监控、`5m` 精细入场，不要求 tick 级 order book；
- 它把 `entry / exit / sizing / risk / cost` 一次性写齐，适合作为 desk 的完整策略候选，而不是只当辅助过滤器。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 期限结构均值回复
- 基础 alpha：BTC 近月 vs 远月期货的年化 basis 收敛
- regime：只在 steep contango / steep backwardation 这类“曲线过陡”状态下开仓
- filter / veto：curve quality、near DTE `>= 7`、front/back DTE 差 `>= 30`、流动性分数、可选 funding 一致性校验
- risk / sizing / execution overlay：`25%` 资本上限、signal-strength/liquidity/regime 乘数、危机期 size-down、4-leg 成本模型、到期前强平、basis adverse move `5%` 止损

## 4. 可复刻的最小实验
- **研究假设**：BTC 曲线在极端 contango / backwardation 时，后续 `1~5` 天存在足够稳定的收敛，能覆盖四腿手续费与滑点。
- **可计算定义**：
  1. `basis_i = (F_i / S - 1) * 365 / DTE_i * 100`
  2. 选 near/front 与 far/back 两腿，定义 `avg_basis = (basis_near + basis_far) / 2`
  3. long calendar：`avg_basis > 15`、regime=contango、nearDTE `>= 7`、far-near DTE `>= 30`
  4. short calendar：`avg_basis < -10`、regime=backwardation
  5. exit：long 在 `avg_basis < 5`；short 在 `avg_basis > -3`；若自开仓后 adverse basis move 超过 `5`，立刻止损
- **最小回测切口**：先只做 **同 venue** 的 BTC 当季/次季合约，`15m` 作为交易时钟，`5m` 只用于更细的入场定位；样本先拉 `2024-01 ~ now`。若 spot 难拿，可先用同 venue perp mid 作为 spot proxy，但必须单独记录 proxy 误差。
- **最该先看**：先看 `post-cost net bps / trade` 与 `holding-days distribution`；第二层再看 `basis half-life` 与 `capacity after four-leg costs`。如果 trade count 很低但单笔边际厚，就把它当 event alpha，不强求 always-on。

## 5. 风险与保留意见
- 这是 **brand-new repo + 0 star** 的工程线索，不是已验证论文；README 的绩效数字必须当成“待证伪陈述”，不能直接继承。
- dated futures 的真实可成交性比 perp 差很多，`5m/15m` K 线回测很容易高估 fill quality；正式复现时最好切到 mid + bid/ask 或 top-of-book 近似。
- basis 年化公式非常吃合约日历、到期口径和 spot proxy 口径；如果 perp funding 时点处理不一致，会把 curve alpha 和 funding 噪音搅在一起。
- cross-venue calendar spread 的保证金切分、转仓与腿错配问题很重；第一轮应该先做 **same-venue honest baseline**，别一上来就跨 venue。

## 6. 来源
- abailey81. (2026). *Crypto-Statistical-Arbitrage*. GitHub repository.
  - Readable URL: `https://github.com/abailey81/Crypto-Statistical-Arbitrage`
  - Repo URL: `https://github.com/abailey81/Crypto-Statistical-Arbitrage.git`
- `strategies/futures_curve/__init__.py`（默认参数：`15%/-10%` entry、`5%/-3%` exit、`5%` stop、`7` 天 near DTE 下限）
  - Readable URL: `https://github.com/abailey81/Crypto-Statistical-Arbitrage/blob/main/strategies/futures_curve/__init__.py`
- `strategies/futures_curve/calendar_spreads.py`（entry / exit / sizing / cost / crisis adjustment 核心逻辑）
  - Readable URL: `https://github.com/abailey81/Crypto-Statistical-Arbitrage/blob/main/strategies/futures_curve/calendar_spreads.py`
- `strategies/futures_curve/futures_walk_forward.py`（walk-forward、危机期参数调整、regime adaptive 外壳）
  - Readable URL: `https://github.com/abailey81/Crypto-Statistical-Arbitrage/blob/main/strategies/futures_curve/futures_walk_forward.py`
