# 别把这篇 2026 深度学习 pairs 论文只读成“LSTM 更准”：对 short-cycle crypto desk，更该先拆的是「dynamic cointegration basket residual fade」这条 raw alpha 壳
- 时间：2026-04-25 18:06 UTC
- 类型：论文 + GitHub repo
- 主题类型：raw alpha
- 基础 alpha：一篮子本该一起走的币，若短时偏离其动态均衡关系太远，后续更容易向均值回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / cointegration / basket / dynamic-spread / 15m / 5m
- 证据类型：论文证据 + 工程实现 + public-data portability probe

## 1. 这次看了什么
看的是 Tsoku、Makatjane 2026 年 Frontiers 论文 *Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs*，以及对应的 2026 GitHub 复现仓 `M-man2591/deep-learning-crypto-pairs-trading`。

## 2. 核心结论
- 这篇东西真正的 base alpha 不是“DNN/LSTM 会预测”，而是 **dynamic cointegration spread / residual 的均值回归**；深度学习更像在做 spread forecast 和阈值排序。
- 论文主样本给出的 headline 很好看：repo 复现口径里 `Sharpe 2.94`、active position-days `71.0%`、ADF `p=0.041`、rolling Johansen trace stat `292.6`；但这些结果主要建立在 **日频**、`2018-01-02 ~ 2026-02-01`、以及作者定义的 dynamic-score 空间上。
- 对我们 desk 更值钱的旁支，不是照搬 DNN/LSTM，而是先把它还原成一个可交易壳：`rolling cointegration -> residual z-score -> threshold entry -> zero-cross / time stop exit`。
- 我用 Binance USDⓈ-M public `15m` 对 `ETH/BNB/LTC/XRP` 做了一个最小 portability probe（rolling OLS basket proxy，lookback `192` bars，`|z|>=2`，max hold `12` bars，四腿 taker 成本粗扣 `16bps`）：共 `34` 笔，平均 **gross `-7.8 bps/笔`**、gross 胜率 `44.1%`；扣成本后平均 **net `-23.8 bps/笔`**、net 胜率仅 `17.6%`。
- 所以当前更诚实的结论是：**“动态协整篮子偏离后回归”这条 raw alpha 壳有研究价值，但还不能把论文 headline 直接降采样成 `15m` 主策略。**

## 3. 为什么和当前项目有关
这篇材料和 `momentum` 有关，不是因为又多了一个“AI 预测价格”的故事，而是因为它提供了一条很标准的 **relative-value / stat-arb raw alpha 骨架**：
- 先找“本来应该一起动”的资产组；
- 再测“谁暂时走飞了”；
- 最后赌它回到队伍里。

这正好补的是 desk 的 **raw alpha 素材池**，而且和单资产 breakout / momentum 完全不是一类东西。更重要的是，repo 已经把几个研究上最容易作弊的点写出来了：rolling estimation、expanding percentile、防 look-ahead、co-integrating vector 平滑降换手。这些都很适合复用到我们自己的 honest stat-arb shell 里。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / 均值回复
- 基础 alpha：dynamic cointegration residual 偏离过大后回归
- regime：协整关系稳定、相关组没有明显结构性断裂时更适合交易
- filter / veto：只在 residual 绝对 z-score 足够大、rolling ADF / trace 仍过线、且预估换手成本不过高时入场
- risk / sizing / execution overlay：beta / hedge ratio 平滑、gross exposure cap、time stop、zero-cross exit、成本 veto、必要时只做 maker-ish child execution

## 4. 可复刻的最小实验
- 研究假设：`1h parent -> 15m/5m child` 下，动态协整残差的极端偏离仍能给出可交易回归。
- 一个可计算定义：在 `ETH/BNB/LTC/XRP` 或同 sector basket 上，rolling `96~192` bars 估计 hedge ratio；当 `|residual_z| > 2.5~3.0` 时入场，`z` 回到 `0~0.5` 或持有 `4~12` bars 离场。
- 最小回测切口：Binance USDⓈ-M，先做 `15m`，再把入场拆到 `5m` child execution；重点看 `ETH/LTC/XRP/BNB` 或换成更同质的 L1 / exchange-token / payment-token 小篮子。
- 最该先看两个指标：**cost 后 avg bps/trade**、**极端阈值提高后 trade count 是否还够**。
- 下一步怎么测：先别加 DNN，先做 `plain dynamic residual fade` baseline；若 baseline 仍负，再测试两件事——(1) 只保留 `|z|>=3` 极端尾部；(2) 加 `cointegration-health gate`（rolling ADF / trace / half-life 上限）看是否能把坏 regime 剪掉。

## 5. 风险与保留意见
- 论文是日频，直接压到 `15m` 很容易把“长期均衡”压成“短期噪音”。
- repo 里风险指标很多仍在 score / z-space，不是完整 dollar PnL；而且没有严肃 slippage。
- 现在这组 `ETH/BNB/LTC/XRP` 在 Binance perp 上四腿成本太疼，说明 **signal 可能没死，但默认 execution 壳不对**。
- 真正值得继续追的，不是“DNN 比 LSTM 强多少”，而是：有没有更同质的小篮子、或者更低换手的 `1h parent` 版本，能把 raw alpha 留住。

## 6. 来源
- Tsoku, J. T., & Makatjane, K. (2026). *Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs*. Frontiers in Applied Mathematics and Statistics.
- DOI: `10.3389/fams.2026.1749337`
- Readable URL: `https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full`
- Repo URL: `https://github.com/M-man2591/deep-learning-crypto-pairs-trading`
