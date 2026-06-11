# 别把这篇 2026 Hawkes LOB 论文只读成“高频预测模型”：对 short-cycle crypto desk，更该先拆的是「order-flow excitation state × base-imbalance signed drift」这条 microstructure raw alpha
- 时间：2026-04-20 19:45 UTC
- 类型：论文 + GitHub
- 主题类型：raw alpha
- 基础 alpha：盘口事件的**自激/互激强度**先决定“下一次 mid-price 什么时候动”，再用 **Base Imbalance（BI）** 决定“更可能往哪边动”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：microstructure / order-book / hawkes / base-imbalance / event-time / BTC / 1m / 3m / 5m
- 证据类型：论文证据 + 公开代码

## 1. 这次看了什么
看的是 Davide Raffaelli、Raffaele Giuseppe Cestari、Daniele Marazzina、Simone Formentin 2026 年论文 *Forecasting Bitcoin price movements using multivariate Hawkes processes and limit order book data*，以及配套仓库 `Learning2Control/MultivariateHawkesLOB`。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：不是“静态盘口厚度大就涨”，而是**盘口事件簇的到达节奏**本身带信息；当某类吃单/撤单/中间价变动在短时间内连续冒出来时，下一次价格跳动的时间与方向都更可预测。
- 作者把问题拆成两步：先用 **multivariate Hawkes** 预测下一次 mid-price change 的到达时间，再用 **BI** 预测那次变化更偏向上还是下；这比“只做 sign 分类”更贴近实盘，因为它把 **什么时候该着急下单** 也一起建模了。
- 论文样本是 Bitfinex `BTC/USD` 2024-01 的约 **300 万条 LOB 更新**，其中约 **374,538** 次 mid-price change；事件间隔中位数只有 **0.215 秒**，这说明信号确实是超短微结构层，而不是慢频因子。
- 结果上，`HawkesTime` 的平均方向准确率约 **0.67**，明显高于只用 Hawkes 直接判符号的 `HawkesSign` 约 **0.55**；同时平均推理时间约 **1.8ms**，快于对照的 **2.6ms**。
- 时间预测本身也明显更像样：多元 Hawkes 的 median relative error 约 **0.747**，优于单变量 Hawkes **1.525**、移动平均 **1.981**、Poisson **3.542**、naive **4.098**；说明 **跨事件类型的互激** 不是装饰，而是主信号。

## 3. 为什么和当前项目有关
这和 `momentum` 当前主线的关系很直接：它给的不是又一个慢频“方向观点”，而是一条能服务 `1m/3m/5m` 的 **microstructure raw alpha**。更重要的是，它提醒我们：对短周期 desk，盘口 alpha 不一定非得退化成静态 `OBI/microprice`，也可以先建一个 **event-time admission layer**——只有当盘口进入“高激发、高可预测”状态时，才放大现有 `imbalance / microprice / queue-pressure` 信号。

## 3.5 策略拆解（必填）
- 方向属性：超短周期单资产微观结构 / 顺势漂移
- 基础 alpha：`高 excitation 的盘口事件簇 + 偏置 BI -> 下一次 mid-price 更可能沿该方向跳动`
- regime：高流动、事件密集、盘口连续更新的时段更适合；死盘/稀疏盘时应降权
- filter / veto：点差过宽、深度过薄、事件到达稀疏、异常跳价时 veto
- risk / sizing / execution overlay：只适合小 size、低延迟、maker/taker 混合执行；若 1m 聚合后 edge 仍薄，应退回成 execution admission，而不是裸方向单独交易

## 4. 可复刻的最小实验
- 研究假设：`top-5~10 level` 的 BI 只有在“最近几十秒盘口事件显著自激/互激”时，才更稳定地预测下一段 `1m/3m` 漂移。
- 一个可计算定义：在 Binance `bookTicker` / `depth` 流里先做 `1s` 采样，构造 `(i) top-5 BI`、`(ii) 最近 30~60s 的 mid-price change / best-bid depletion / best-ask depletion 计数`、`(iii) excitation proxy = 这些事件的 EWMA 强度`；只在 `excitation_proxy` 进入上分位时，测试 `BI` 对 next `12/36/60` 秒或 next `1/3` 根 `1m` bar 的方向命中率与 bps。
- 最小回测切口：`BTCUSDT` 先做，周期先看 `1m/3m`，样本先取最近 `7~14d` 高频快照。
- 最该先看哪 1~2 个指标：`gross bps / event`、`hit-rate uplift vs 静态 BI baseline`。

## 5. 风险与保留意见
- 论文数据是 Bitfinex `BTC/USD`，迁移到 Binance/Hyperliquid 时，盘口层级、撮合节奏、fee 结构都会变。
- 这条线天然偏高频；如果 desk 当前拿不到稳定 L2/L3 或低延迟执行，别硬包装成独立主策略，更合理的是先把它做成 **短窗 admission / urgency score**。
- 方向准确率 `0.67` 听起来高，但对应的是“下一次 mid-price change”而不是扣完摩擦后的净收益；成本与队列位置仍是生死线。

## 6. 来源
- Raffaelli, D., Cestari, R. G., Marazzina, D., & Formentin, S. (2026). *Forecasting Bitcoin price movements using multivariate Hawkes processes and limit order book data*. *Decisions in Economics and Finance*.
- DOI: `10.1007/s10203-026-00570-z`
- Readable URL: `https://link.springer.com/article/10.1007/s10203-026-00570-z`
- PDF URL: `https://link.springer.com/content/pdf/10.1007/s10203-026-00570-z.pdf`
- Repo URL: `https://github.com/Learning2Control/MultivariateHawkesLOB`
