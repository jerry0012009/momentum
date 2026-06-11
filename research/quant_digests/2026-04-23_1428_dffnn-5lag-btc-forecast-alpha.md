# 别把这篇 2021 DFFNN 论文只读成“又一个价格预测摘要”：对 short-cycle crypto desk，更该先拆的是「最近 5 根 5m 价格 → 下一根 5m 价格预测」这条 single-asset raw alpha 候选
- 时间：2026-04-23 14:28 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：用最近 5 根 `5m` BTC 价格预测下一根 `5m` BTC 价格；若预测涨跌幅超过交易阈值，则顺预测方向做多/做空，未超过阈值则不交易。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：single-asset / high-frequency / forecasting / deep-learning / BTC / 5m / momentum / execution-threshold
- 证据类型：论文证据

## 1. 这次看了什么
看的是 Lahmiri, Bekiros 在 *Cognitive Computation* 发表的短文 **Deep Learning Forecasting in Cryptocurrency High-Frequency Trading**。它不是完整交易系统，而是一个很短、很干的预测实验：拿 `2016-01-01 ~ 2018-03-16` 的 BTC `5m` 数据，共 `65,535` 个样本，用最近 5 个价格点喂给三层 DFFNN，预测下一时点价格。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：不是“AI 很厉害”，而是 **短窗价格自身的局部路径，对下一根 `5m` 价格还有可预测性**。
- 模型输入非常朴素：只有最近 5 个价格；输出是下一根价格。对我们 desk 来说，这比大而全特征工程更像一个可快速复刻的基线。
- 论文主要证明的是 **forecast RMSE**，不是交易 PnL。最佳训练算法是 Levenberg–Marquardt，RMSE `1.4406`，好于 Powell-Beale `2.3187` 和 resilient `2.9715`。
- 所以它能支持“先做 raw alpha 候选 intake”，但**还不能直接支持‘这条策略成本后能赚钱’**。

## 3. 为什么和当前项目有关
这篇最有用的地方，不是让我们照搬 DFFNN，而是提供一个很清楚的 short-cycle 母式：
**先回答“纯价格路径本身还有没有短窗预测力”，再决定要不要叠 volume / order-book / regime。**
对当前 desk，这正好能补一类和 pairs / carry / cross-sectional 不同的素材：**single-asset、5m-native、可直接往 `1m/3m/5m` 推的预测型 raw alpha 基线**。

一句话核心结论：**只用最近 5 根 `5m` BTC 价格，也可能提取出下一根价格的短窗延续/修正信息。**

一句话证明方式：**作者用 `65,535` 个 BTC `5m` 样本，比较三种 DFFNN 训练算法，靠 out-of-sample RMSE 证明短窗价格预测不是纯噪音。**

最值得复用/复现的点：**不是深度网络本身，而是“5-lag very-short-horizon forecast baseline + trading threshold” 这个最小母式。**

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 预测型单资产
- 基础 alpha：最近 5 根 `5m` 价格对下一根 `5m` 价格存在可提取的短窗预测力
- regime：论文未给；desk 侧应优先测试高波动 / 高成交时段是否更强
- filter / veto：预测涨跌幅必须超过手续费+滑点+安全缓冲；低波动时不交易
- risk / sizing / execution overlay：波动率缩放仓位、单笔 time-stop（1~3 bar）、maker-first 或至少严格成本阈值

## 4. 可复刻的最小实验
**研究假设**：若 `pred_next_return = pred_price / current_price - 1` 足够大，则 BTC 下一根 `5m` 的真实回报更可能同向。

**可计算定义**：
1. 输入：最近 5 根 `5m` close
2. 输出：下一根 `5m` close
3. 信号：
   - `pred_next_return > +th` 做多
   - `pred_next_return < -th` 做空
   - 其余空仓
4. 出场：持有 1 根、2 根、3 根分别做 A/B test

**最小回测切口**：Binance BTCUSDT perp，先跑近 `90d` `5m`；再向 `1m/3m` 压缩测试。阈值 `th` 先扫 `2 / 4 / 6 / 8 bps`。

**最该先看**：
- 成本后 `avg net bps/trade`
- 阈值抬高后 trade count 是否断崖

## 5. 风险与保留意见
- 论文证明的是预测误差，不是交易收益；**RMSE 变好 ≠ 成本后可交易**。
- 输入只有价格，没用成交量、盘口、funding、basis，说明它像“最小基线”，但也容易被更近年的市场微结构噪音吃掉。
- 样本是 `2016~2018` BTC，和当前 24/7 perp 市场的流动性结构差很多；transfer 风险不小。
- 训练算法里 Levenberg–Marquardt 在在线更新上未必最方便；如果要 live，更可能先用更轻的 MLP / 线性 / ridge 做对照。

## 6. 下一步怎么测
先别急着上深网大工程，按下面顺序：
1. 先做 **5-lag 线性回归 / ridge / 小 MLP** 三个 baseline；
2. 把输出统一转成 `pred_next_return`，扫 `2~8bps` 交易阈值；
3. 对比 `hold 1 / 2 / 3 bars` 与 `maker-ish 4bps`、`taker-ish 8bps` 两档成本；
4. 若 BTC `5m` 有正 edge，再决定要不要加 volume / realized vol / OFI，把它升级成更像 desk 可交易的 forecasting sleeve。

## 7. 来源
- Salim Lahmiri, Stelios Bekiros. (2021). *Deep Learning Forecasting in Cryptocurrency High-Frequency Trading*. Cognitive Computation.
- DOI: `10.1007/s12559-021-09841-w`
- Readable URL: `https://doi.org/10.1007/s12559-021-09841-w`
- PDF URL: `https://link.springer.com/content/pdf/10.1007/s12559-021-09841-w.pdf`
