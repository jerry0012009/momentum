# Intraday Time-Series Momentum：不是所有“动量”都要看几天，日内前段走势本身也可能是 alpha
- 时间：2026-03-11 05:35 UTC
- 类型：论文
- 主题标签：trend / momentum / intraday / regime / alpha
- 证据类型：论文证据 + 工程迁移假设

## 1. 这次看了什么
这次看的是 **Li, Sakkas, Urquhart (2021/2022), _Intraday time series momentum: Global evidence and links to market characteristics_**。它研究的不是月频或日频趋势，而是一个更贴近短周期的问题：**同一天里，前半段的方向，能不能预测后半段的方向。** 论文用 16 个发达市场的高频指数数据验证：`前 30 分钟收益` 对 `最后 30 分钟收益` 有显著预测力，而且这种效应会随市场状态变化而变强或变弱。

## 2. 核心结论
- 论文证据：作者在 16 个发达市场上发现，**开盘后前 30 分钟收益（含 overnight 信息）可以正向预测当日最后 30 分钟收益**；合并样本与多数单市场上都成立。
- 论文证据：样本外上，**16 个市场里有 11 个市场 OOS R² 为正**；基于该信号的简单交易策略在 **13 个市场** 获得显著正收益，并在 **12 个市场** 的 Sharpe 上跑赢被动持有。
- 论文证据：这个日内动量并不是“越平静越好”，而是**在流动性更差、波动更高、信息更离散时更强**。作者据此把来源解释为 **市场微观结构摩擦 + 投资者行为迟滞**，而不只是一个纯统计巧合。
- 对当前项目最有启发的一点是：短周期 alpha 不一定非得来自“连续 N 根 K 的滚动收益率”，也可能来自**某个会话前段的信息冲击，在会话后段继续被消化**。

## 3. 为什么和当前项目有关
这篇比经典 TSMOM 更贴近你现在的 `5m/15m` 主线，因为它回答的是“**短周期里还剩什么趋势延续**”。它对 `momentum` 的意义主要有三点：
- 它支持把“动量”从滚动窗口扩展成 **session-aware 动量**：不是随时都算，而是在特定会话切片里算。
- 它提示 **regime 不是附属品**：如果一个短周期延续效应本来就只在低流动性 / 高波动 / 离散信息时更强，那么过滤器不是锦上添花，而是效应定义的一部分。
- 它也提醒你别直接照搬股票“开盘—收盘”结构到 crypto：**Crypto 是 24/7，没有天然 overnight**，所以必须主动定义“信息批次”与“会话边界”。

## 4. 可复刻的最小实验
- 研究假设：Crypto 15m 上若存在日内 TSMOM，它更可能出现在**人为定义的会话边界**附近，而不是全天任意时刻都稳定存在。
- 一个可计算定义：
  - 先把 24h 切成固定会话，优先试两种：
    1. **8h funding 会话**（00:00 / 08:00 / 16:00 UTC）
    2. **24h UTC 会话**（00:00 UTC 起）
  - `lead_ret = first_2bars_return`（前 30 分钟，对 15m 即前 2 根）
  - `tail_ret = last_2bars_return`（会话最后 30 分钟）
  - 方向规则：`signal = sign(lead_ret)`，仅在 `abs(lead_ret)` 超过阈值时入场。
  - 条件分层：按会话内 `realized_vol` 分位、成交额分位、funding 前后切片分别统计。
- 最小回测切口：
  - 资产：BTC perpetual、ETH perpetual、SOL perpetual
  - 周期：15m
  - 样本：近 180d~365d
  - 对照：
    1. 无条件 session-ITSM
    2. 只做高波动分位
    3. 只做低流动性 / 低成交额分位
- 最该先看：
  1. `post_cost_return`
  2. `positive_window_ratio`

## 5. 风险与保留意见
- 这篇论文的原始对象是**发达市场股票指数**，不是 crypto，也不是 24/7 市场。
- 论文里的一个关键条件是“overnight + 开盘后 30 分钟”的信息堆积；Crypto 没有统一开盘，这个机制必须通过 **funding、UTC 日切、欧美开盘时段** 等代理去重建。
- 如果搬到 crypto 后效果消失，不一定说明“短周期动量无效”，也可能说明：**真正有效的不是 rolling momentum，而是离散信息批次后的延续。**
- 所以下一步不该直接做大而全组合，而是先验证：**哪些会话边界最像股票里的开盘。**

## 6. 来源
- Li, Z., Sakkas, A., & Urquhart, A. (2022). *Intraday time series momentum: Global evidence and links to market characteristics*. Journal of Financial Markets, 57, 100619.
- DOI: https://doi.org/10.1016/j.finmar.2021.100619
- Readable URL: https://www.sciencedirect.com/science/article/pii/S138641812100001X
- Accepted version PDF: https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf
