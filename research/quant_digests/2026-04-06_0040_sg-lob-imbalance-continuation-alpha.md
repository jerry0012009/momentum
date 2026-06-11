# 别把 LOB 论文继续读成“要上 DeepLOB”：这篇 2025 arXiv 更该先测的是「Savitzky-smoothed depth imbalance × simple-model continuation」这条 microstructure raw alpha

- 时间：2026-04-06 00:40 UTC
- 类型：2025 arXiv 全文 HTML + Bybit public historical LOB portal + Bybit orderbook API docs source audit
- 主题类型：raw alpha
- 基础 alpha：**先把多档盘口不平衡、spread、weighted-mid 变化做 Savitzky–Golay 去噪，再用简单模型（Logistic / XGBoost）预测极短期 mid-price continuation；最后把 sub-second directional vote 聚合成 `1m / 3m` 可交易 conviction。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-book/depth-imbalance/mid-price/continuation/denoising/savitzky-golay/kalman/logistic/xgboost/deeplob/bybit/btcusdt/1m/3m/5m/15m/paper/public-data/cost/risk
- 证据类型：arXiv 全文给出样本、特征、去噪流程、分类任务、深浅模型对比、准确率与 runtime 表；Bybit 历史盘口与 API 文档公开可拿

## 1. 这次看了什么

主看的是：

**Wang, Haochuan (2025). _Exploring Microstructural Dynamics in Cryptocurrency Limit Order Books: Better Inputs Matter More Than Stacking Another Hidden Layer_. arXiv.**

这篇最值钱的点，不是又来一遍“LOB 可以预测短期价格”，而是它把一个对当前 desk 很实用的结论讲得很明确：

> 真正值得先拿走的，不是继续堆更深网络，而是先把盘口噪声压掉，再用更简单、更快、更可解释的模型做方向票数。

论文用 **Bybit BTC/USDT 100ms 盘口快照**，比较了 Logistic、XGBoost、CatBoost、CNN+LSTM、CNN+XGBoost、DeepLOB，在 `100ms / 500ms / 1000ms` 预测窗口下，测试 raw / Kalman / Savitzky–Golay 三种输入。对我们 desk 来说，最该 intake 的不是“哪路网络名字更大”，而是这条可以直接改写成交易壳的 **denoised depth-imbalance continuation raw alpha**。

## 2. 先回答一句：这篇东西的 base alpha 是什么？

**base alpha = `去噪后的多档盘口不平衡 + 微价格变化` 所隐含的短时 continuation。**

翻成人话：
- 不是把 order book 只当 execution 辅助；
- 也不是把这篇只读成“深度学习 benchmark”；
- 而是把盘口里原本被 flicker / cancel / micro-noise 淹没的供需偏移，先做平滑，再直接拿来预测下一小段价格方向。

所以它不是单纯 filter，也不是纯解释型材料；它本身就是一条 **microstructure raw alpha**，只不过天然更适合 `1m / 3m`，再往 `5m` 外推，而不是硬写成 `15m` 主信号。

## 3. 为什么这轮值得进研究池

先问一句：**它为什么比继续补一个 shared gate 更值得？**

因为这轮拿走的是一条可以独立复现、独立回测、独立定价成本的 **完整快频 raw alpha 骨架**：

1. **数据公开可拿。**
   论文主数据来自 Bybit 历史盘口下载页；live 版也能接 Bybit orderbook API / websocket。
2. **信号本体清楚。**
   不是黑盒 embedding，而是 `imbalance / spread / weighted mid / depth` 这类能解释的微结构量。
3. **和现有 OBI/OFI intake 不重复。**
   我们之前已经 intake 过不少 “盘口不平衡本身”；这篇真正新增的是 **SG/Kalman 去噪 + 深浅模型对照 + 深度层数 trade-off**。
4. **能直接落地 entry / exit / sizing / risk / cost。**
   只要把 sub-second score 聚合成 minute conviction，就能形成独立交易策略，而不只是 execution veto。

## 4. 论文里最值得拿走的证据

## 4.1 真正有增量的不是更深网络，而是 Savitzky–Golay 去噪

论文最有用的一组结果，是 **binary classification** 下的 `500ms / 1000ms` horizon：

- **500ms, 40-level LOB, SG**：
  - XGBoost：**0.7281**
  - Logistic：**0.7284**
- 对照 **raw**：
  - XGBoost：**0.6542**
  - Logistic：**0.6517**
- 对照 **Kalman**：
  - XGBoost：**0.6301**
  - Logistic：**0.4882**

也就是说，单看这组，**先去噪** 比 **换更复杂模型** 重要得多；而且 SG 对 simple models 的帮助，明显强于 Kalman 在这篇里的默认调参结果。

再看 **1000ms, 40-level LOB, SG**：
- XGBoost：**0.7150**
- Logistic：**0.7089**
- raw 对照分别只有 **0.6509 / 0.6515**

这说明：
- alpha 不是只存在于最极端的 100ms 噪声里；
- 在更可交易的 `500ms~1s` 级别，去噪后的盘口 continuation 仍有信息。

## 4.2 ternary 结果同样支持“先把噪声处理好”

在 **ternary classification** 里，`500ms, 40-level LOB`：
- raw Logistic：**0.4356**
- SG Logistic：**0.5434**

`1000ms, 40-level LOB`：
- raw Logistic：**0.4901**
- SG Logistic：**0.5382**

这类结果对 desk 的实际意义是：

> 当你把任务写成 up / flat / down，而不是强迫模型每次都二选一时，去噪后的盘口特征更适合做“有把握才开仓”的 conviction score，而不是每根都出手。

这正好适合我们把它改成：
- `1m` 上的开仓 admission / veto；
- `3m` 上的短 holding raw alpha；
- `5m` 上的 child execution direction bias。

## 4.3 深度层数很关键：40-level 信息明显强于浅层简化版

论文还给了一个很值钱的 portability 提醒：

在 **SG + XGBoost + T=1** 的对照里：
- **40 levels**：Accuracy **0.7150**，support **5,442**
- **10 levels**：Accuracy **0.5837**，support **17,471**
- **5 levels**：Accuracy **0.5797**，support **18,336**

翻成人话：
- 更深的盘口层数，确实有增量 alpha；
- 但一旦要求 40-level 完整快照，可用样本会明显下降；
- 所以实盘设计里必须同时跑：
  - `full-depth high-conviction 版本`
  - `shallow-depth portable 版本`

这对 `1m / 3m` 很重要，因为真实数据流里，深度缺失、快照抽样不齐、不同 venue 的 L2 完整度都会影响信号稳定性。

## 4.4 简单模型也能做到“够快 + 够强”

论文的 sequence-length 对照说明：
- **XGBoost, T=1**：Accuracy **0.5732**，训练约 **1m36s**
- **XGBoost, T=10**：Accuracy **0.5949**，训练约 **7m04s**
- **Logistic, T=1**：Accuracy **0.5551**，训练约 **1m11s**
- **Logistic, T=10**：Accuracy **0.5716**，训练约 **9m13s**

不是说这些 runtime 数字能直接外推到我们环境，而是说明了一件事：

> 对这类盘口 alpha，`轻模型 + 好输入` 很可能比 `重模型 + 原始噪声输入` 更适合做快速迭代和 walk-forward。

这很符合当前 desk 的目标：**先补可快速复现的 alpha 素材池**，而不是先陷进大模型工程。

## 5. 对当前 short-cycle desk，最诚实的读法是什么？

最诚实的读法不是：
- “现在就把 100ms 预测直接搬成高频交易系统”；
- 也不是“把 15m 主信号改成纯 LOB 驱动”。

更合理的读法是：

- **主 raw alpha 周期放在 `1m / 3m`**；
- 用 `100ms -> 1s` 的盘口方向票数，聚合成 minute-level conviction；
- `5m` 作为持有或切换频率；
- `15m` 不作为这条线的主 alpha 周期，只保留为上层 regime / risk clamp。

也就是说，这篇更适合服务：
- `microstructure continuation`
- `fast mean-reversion / continuation router` 的方向层
- `price-based alpha` 的 child execution bias

但这轮 digest 里，我们把它优先保留为 **可独立回测的 raw alpha**，不是只写成 shared gate。

## 6. desk 版策略骨架

## 6.1 数据与特征

- 交易对象：先从 **BTCUSDT perp** 起步，第二轮再扩到 `ETH / SOL` 等高流动性标的
- 数据源：
  - 历史：Bybit historical LOB download
  - live：Bybit orderbook API / websocket
- 原始采样：`100ms` snapshots
- 初版深度：并排做 `top5 / top10 / top20 / top40`

特征先不要贪多，先做这几类：
- `I1 / I5 / I20 / I40`：不同层级的 bid-ask imbalance
- `spread_bps`
- `weighted_mid_change`
- `depth_slope`
- `best-level queue change`
- `microprice deviation`

每个特征并排保留三版：
- raw
- Savitzky–Golay
- Kalman

## 6.2 信号定义

最小可交易版，不直接用论文里的 accuracy 做文章，而是把模型输出改成 **minute conviction**：

1. 每 `1s` 训练 / 推理一次下一段 `1s` 或 `3s` 的方向分数：`score_t = p(up) - p(down)`
2. 聚合到 `1m`：
   - `conviction_1m = mean(score_t)`
   - `persistence_1m = share(score_t > θ)`
   - `shock_1m = max(|score_t|)`
3. 开仓规则：
   - **LONG**：`conviction_1m > q80` 且 `persistence_1m > 0.60` 且 spread 不在日内最差分位
   - **SHORT**：对称条件

这条线本质上还是 raw alpha，因为它直接决定方向，而不是只给 veto。

## 6.3 entry / exit / sizing / risk / cost

### Entry
- 首版按 `1m close` 决策；
- 如果盘口仍顺风、spread 较窄，则优先挂被动单；
- 如果 alpha 半衰期太短，再退回 taker 版做保守验证。

### Exit
- 固定 holding：先测 `1 / 2 / 3` 根 `1m bar`
- 或者 `conviction` 反号提前平仓
- 或者 hit `microprice stop / adverse bps stop` 平仓

### Sizing
- 按过去 `N` 分钟 realized micro-vol 反比缩放
- 单次 notional 不超过组合资金 `10%`
- spread / depth 差时自动降杠杆或不下单

### Risk
- 单笔止损：`8~15 bps` 起步，按币种再调
- 若盘口深度突然塌陷或 spread 扩到日内高分位，强制减仓
- 连续 `k` 笔信号失效触发 session kill-switch

### Cost
- 第一轮必须先按 **taker fee + spread cost** 算净值
- 第二轮再测 maker fill assumption
- 单独记录：
  - quote-to-fill ratio
  - gross-to-net decay
  - average holding time
  - queue miss rate

## 7. `1m / 3m / 5m / 15m` 怎么映射

## 1m
这条线最自然的主战场。

- 论文原始信息量本来就在亚秒级；
- 折算到 `1m`，还能保留够多 microstructure edge；
- 同时成本与成交假设还能被普通 desk 回测框架承受。

## 3m
适合做更稳一点的持有版本。

- 保留 fast alpha
- 降低过度换手
- 更容易比较 after-cost 是否优于 1m

## 5m
更适合作为：
- `1m/3m` 信号的 holding bucket
- 或 price-based strategy 的 execution direction bias

## 15m
不建议把这条线直接硬写成 15m 主信号。

更合理的用途是：
- 作为上层 trend / volatility regime
- 决定 fast alpha 是否放大或收缩仓位

## 8. 最小可复现实验

## 实验 A：去噪是否真的带来可交易增量？

并排回测三条线：
1. raw LOB features
2. SG-smoothed LOB features
3. Kalman-smoothed LOB features

统一：
- 标的：BTCUSDT perp
- 数据：Bybit `100ms` 历史盘口
- 模型：Logistic / XGBoost
- 输出：`1s -> 1m conviction`
- 持有：`1m / 3m`

看：
- after-cost pnl
- hit rate
- mean log return
- turnover
- gross-to-net decay

如果 SG 明显优于 raw，而 Kalman 不稳定，那就说明论文里的核心增量可以迁移。

## 实验 B：深度层数 portability

并排：
- top5
- top10
- top20
- top40

目的不是单纯找最高 accuracy，而是找：
- 哪个深度在 **可得性 / 稳定性 / 成本 / edge** 上最平衡。

如果 top40 只有 paper-level 好看、实盘缺失率太高，就退到 top10/top20 做 portable 版本。

## 实验 C：独立 raw alpha 还是 price alpha 的 child execution？

并排：
1. 纯盘口 conviction standalone
2. 价格 breakout/continuation alpha 单独跑
3. 价格 alpha + 盘口 conviction 同向才开仓

这一步是为了回答：
- 它能不能自己独立赚钱；
- 如果独立性一般，它更适合做 execution booster 还是 admission filter。

## 9. 数据源、公开性与最小复现实验口径

这条主题的外部数据不是低频宏观，而是 **公开可拿的高频盘口数据**：

1. **Bybit historical data portal**
   - 公开性：公开页面可下载
   - 频率：论文使用 `100ms` snapshots
   - 用途：主回测数据源
2. **Bybit orderbook API / websocket**
   - 公开性：公开开发者文档
   - 频率：毫秒级/实时更新
   - 用途：live / replay portability

最小复现实验口径：
- 先只做 `BTCUSDT`
- 先只做 `1` 个交易日到 `5~10` 个交易日 rolling walk-forward
- 先只做 `1s prediction -> 1m holding`
- 先只算 taker cost

这样可以最快回答：这条 edge 是真 alpha，还是只是一组 paper-level classification number。

## 10. 风险与保留意见

- 论文主样本核心展示很短，**以单日 Bybit 盘口为主**，不能把结果直接当成跨月份稳定规律。
- classification accuracy 不等于 after-cost pnl；方向判断对，不代表成交后还能赚钱。
- crypto 盘口里 spoof / cancel / exchange-specific microstructure 很重，跨 venue 可移植性必须实测。
- `40-level` 深度信息虽强，但 live 数据完整度、带宽和存储成本也更高。

## 11. 来源

1. **Wang, H. (2025). _Exploring Microstructural Dynamics in Cryptocurrency Limit Order Books: Better Inputs Matter More Than Stacking Another Hidden Layer_. arXiv.**
   - Authors：Haochuan Wang
   - Year：2025
   - Title：Exploring Microstructural Dynamics in Cryptocurrency Limit Order Books: Better Inputs Matter More Than Stacking Another Hidden Layer
   - Venue：arXiv preprint
   - DOI：<https://doi.org/10.48550/arXiv.2506.05764>
   - Readable URL：<https://arxiv.org/abs/2506.05764>
   - HTML URL：<https://arxiv.org/html/2506.05764>
   - Repo URL：N/A
2. **Bybit Historical Data Download（论文主数据源）**
   - Readable URL：<https://www.bybit.com/derivatives/en/history-data>
3. **Bybit API Documentation — Get Orderbook**
   - Readable URL：<https://bybit-exchange.github.io/docs/v5/market/orderbook>

## 12. 下一步怎么测（一句话）

先在 `BTCUSDT Bybit 100ms LOB -> 1s score -> 1m conviction` 这条链路上并排回测 `raw / SG / Kalman` 与 `top5 / top10 / top20 / top40`，若 SG 版在 after-cost、mean-log-return、gross-to-net decay 三项里都更优，再把它升级成 `1m/3m` 独立 microstructure raw alpha 壳。