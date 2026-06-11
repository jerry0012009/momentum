# 别把这篇 2025 Financial Innovation 论文继续只拆成 filter：它的 headline 更该进入素材池的是「CUSUM 事件条 + Triple Barrier」完整 raw alpha
- 时间：2026-03-27 04:48 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：当 1m 价格路径先累积出足够大的方向性事件（CUSUM 触发）后，预测“下一段有意义的同向/反向价格摆动”，并用 Triple Barrier 做真实出场，而不是盯固定时间 bar 的 next-bar 涨跌。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-driven/directional/cusum/triple-barrier/resnet-lstm/binance/btc/eth/1m/3m/5m/15m/paper
- 证据类型：论文证据（Financial Innovation，全文 HTML 可读）

## 1) 这次看了什么
看的是 **Przemysław Grądzki、Piotr Wójcik、Stefan Lessmann (2025)** 的论文 **《Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning》**。前两次 intake 已把它拆成过 gate/filter，但这次不再拿旁支当主角，而是回到它自己的 **headline raw alpha**：**用事件条而不是时钟条定义交易机会，再用真实止盈/止损/超时标签训练方向策略。**

## 2) 核心结论（先说人话）
- **一句话核心结论：** 真正可交易的东西，不是“预测下一根 5m/15m bar 涨跌”，而是“等市场先走出一段像样事件，再去赌下一段有意义摆动的方向”。
- **一句话证明方式：** 作者用 Binance `2018-01 ~ 2023-06` 的 BTC/ETH tick 数据，做 **5 类采样 × 3 档参数 × 2 种标签 × 6 个模型 × 3 个随机种子 × 5 个 OOS 季度**，总计 **2700 个模型**，并把 **0.1% 开仓 + 0.1% 平仓** 成本直接扣进回测。
- 论文最关键的实证结论是：**next-bar 几乎不够付成本**。在全部 **210 个 next-bar 实验**里，只有 **29 个** 年化净收益为正。
- 真正稳定活下来的组合是 **CUSUM 事件条 + Triple Barrier + ResNet-LSTM**。其中 **ETH 的 CUSUM 2%** 在完整测试集上做到 **年化净收益 91.6% / Sharpe 1.42 / 最大回撤 25.1%**；**CUSUM 3%** 也有 **54.1% / 1.03**。相比之下，同一张表里 **1h time bar** 是 **-30.0% / -0.53**。
- **BTC 也不是全面爆炸，但方向一致**：在 Triple Barrier 下，**BTC 的 CUSUM 2%** 仍有 **20.4% 年化净收益 / 0.51 Sharpe**，而 **1h time bar** 是 **-44.3% / -1.30**。
- 一个很值钱的细节是：作者后来试了 **动态波动率 Triple Barrier**，结果并没有更好；反而说明第一优先级不是“再做更花的 barrier”，而是先把 **sampling / labeling honesty** 搞对。

## 3) 为什么和当前项目有关
这次值得收进池子，是因为它补的是我们还缺的一类 **完整、可独立复现的事件驱动方向 raw alpha**，而不是再补一个 shared gate。它和现有大量 clock-based 题材不同：不是按整点、整根 K 线、固定 formation window 去做判断，而是让市场自己决定“什么时候真的发生了一次值得交易的事件”。这对 `1m/3m/5m/15m` desk 很重要，因为很多短周期 alpha 不是方向错，而是 **取样单位错了**：时间 bar 把噪音和有意义摆动揉在一起，最后只剩高换手、低净 edge。

## 3.5) 策略拆解（必填）
- 方向属性：**事件驱动顺势 / 方向延续型**
- 基础 alpha：**CUSUM 触发后的“下一段有意义价格摆动方向”可预测**
- regime：高流动性主流币、存在明显 event clustering 的时段更优
- filter / veto：只做高置信度信号（论文用 `p>0.6` 做多、`p<0.4` 做空）
- risk / sizing / execution overlay：对称 TP/SL + vertical barrier；一次只开一笔；先按 `1x notional` 或固定风险预算做最小版，成本至少按 round-trip `20bps` 起算

## 4) 可复刻的最小实验
**研究假设：** 把输入单位从固定 `5m/15m` 改成 `1m` 上的 directional CUSUM 事件条后，哪怕先不用深度学习，只用轻量分类器，也能比 fixed time-bar 的 next-bar 标签更接近“成本后可交易”。

**一个可计算定义：**
1. 用 Binance BTC/ETH perpetual `1m` close 构造 directional CUSUM；先试阈值让事件频率落在 **8~25 次/天**；
2. 每个事件条上做最小特征：近 8/16 个 event-bar 的 return、realized vol、EMA 偏离、RSI、volume z-score；
3. 标签别再用 next-bar，改成 **对称 Triple Barrier**：止盈/止损先试 `0.6% / 0.6%`、`0.9% / 0.9%`，超时先试 `24` 个 event bars 或 `90` 分钟；
4. 第一轮模型直接用 **XGBoost / Logistic**，先验证“采样 + 标签”本身，不急着复制深度网络。

**最小回测切口：** `BTC/ETH`，`2025Q4~2026Q1`，public perp `1m` 数据；对照组是同一套特征下的 `5m` 或 `15m` fixed-bar + next-bar 标签。

**先看 2 个指标：**
- 成本后 `expectancy / trade`
- `Sharpe + trades/day` 是否同时优于 fixed-bar baseline

## 5) 风险与保留意见
- 论文主证据只覆盖 **Binance、BTC、ETH**，外推到小币要重新定阈值。
- 论文没有把真实滑点做进 order-book 级仿真，所以 live 端要比 paper 更保守。
- `CUSUM` 阈值太低，会退化成噪音 next-bar；太高，又会把样本数压没。
- 论文里 **feature engineering 对 BTC 很关键**：去掉特征工程后，`BTC CUSUM 2% + Triple Barrier 5%` 从 **+20.4%** 直接掉到 **-24.2%**；说明它不是“随便喂个模型都行”。

## 6) 来源
1. **Grądzki, P., Wójcik, P., & Lessmann, S. (2025). _Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning_. Financial Innovation.**
   - DOI: <https://doi.org/10.1186/s40854-025-00866-w>
   - Readable URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w>
   - PDF URL: <https://link.springer.com/content/pdf/10.1186/s40854-025-00866-w.pdf>
   - Table 4 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/4>
   - Table 5 URL: <https://link.springer.com/article/10.1186/s40854-025-00866-w/tables/5>
2. **Binance public market data**
   - Publicity: 公开可得
   - Update frequency: tick / `1m`
   - Readable URL: <https://data.binance.vision/>

## 7) 下一步怎么测（一句话）
别先卷模型，先拿 `1m` BTC/ETH perpetual 把 **fixed-bar + next-bar** 和 **CUSUM event-bar + Triple Barrier** 做一版 A/B，若成本后 expectancy 还活着，再决定要不要上 ResNet-LSTM。