# 别把这份 2026 GitHub 新仓库继续写成 3m HFT：它更该先测的是「1s 微结构压力 → 3m~15m 方向漂移」raw alpha，但当前 taker 只到 30m 才勉强留边
- 时间：2026-03-27 19:27 UTC
- 类型：2026 GitHub 新仓库 + README/source/输出文件审阅
- 主题类型：raw alpha
- 基础 alpha：`1s` 盘口失衡、microprice 偏移、主动/被动流与短时波动状态里，存在可学习的未来方向 edge；repo 把它实现成 `BTC` 的 long-only timing，但对 desk 更值钱的其实是「同一组微结构特征在 `3m/5m/15m` 到底能不能扛过成本」这条 raw alpha 母线
- 是否可独立复现：是（需要自抓公开订单簿/成交事件流；repo 未附原始输入文件）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/microstructure/directional/order-book/lightgbm/purged-walkforward/horizon-sweep/btc/gemini/1s/3m/5m/15m/30m/repo/cost
- 证据类型：repo 代码证据 + repo 输出文件证据

## 1. 这次看了什么
这次看的是 **kailiu0712 在 2026-03-15 发布的 GitHub 仓库 _-5-min-level-Directional-Prediction-for-Crypto-HFT_**。

先直接回答这篇东西的 **base alpha**：

> **不是“LightGBM 预测方向”这种空话，而是：1 秒级盘口失衡、depth pressure、microprice-vs-mid、主动/被动成交流，能不能对未来几分钟的 BTC mid-price 漂移给出可交易的方向 edge。**

repo 的实现方式很完整：
- 从原始 BTC 事件流重建本地订单簿
- 聚合成 `1s` snapshot
- 做多类标签：`negative / mild / positive`
- 用 **purged 5-fold walk-forward** 训练 LightGBM
- 再把 `prob_positive - prob_negative` 转成信号
- 用滚动分位阈值做 **dynamic entry / exit**
- 最后跑一个 **cost-aware long-only backtest**

所以这不是单纯的“模型 demo”，而是一条可以明确拆解成 **feature → label → model → signal → execution** 的 raw alpha 骨架。

不过，对当前 desk 真正更值钱的地方，不是照搬 repo 的 long-only 回测，而是回答一个更实际的问题：

> **同一套 `1s` 微结构特征，放到 `3m / 5m / 15m` 的短周期方向 alpha 上，哪里开始有 gross edge，哪里成本后还能活？**

这件事和当前素材池直接相关，因为最近 intake 里有不少 `pairs / XS reversal / carry / lead-lag`，但**把超短微结构特征明确映射到更慢一点、可落到 short-cycle desk 的持有期**，还值得继续补样本。

## 2. 核心结论
### 2.1 repo 里真正的信号本体是什么
`feature_engineering.py` 里，repo 先从事件流重建订单簿，再抽取 1 秒级微结构特征。最值得记的不是某个模型参数，而是下面这几类特征：

- **top-of-book 状态**：`best_bid / best_ask / mid / spread / microprice`
- **盘口深度与形状**：`bid_depth_1 / ask_depth_1 / bid_depth_5 / ask_depth_5`、depth entropy、HHI、slope
- **盘口失衡**：`imbalance_1 / imbalance_5 / depth_pressure_5`
- **事件流**：trade / place / cancel / fill 的计数与成交量
- **主动 + 被动净流**：`signed_trade_flow_1s`、`net_passive_flow_1s`、`net_order_flow_1s`
- **秒内路径**：open/high/low/close mid、秒内 realized variation、spread variation
- **滚动窗口聚合**：不同秒窗上的 volatility、flow、imbalance 均值与 z-score

也就是说，repo 的 base alpha 不是“黑箱分类器”，而是一个很标准、很 desk 化的命题：

> **当盘口深度倾斜、microprice 偏移、主动买卖失衡和被动流撤单/补单一起朝一个方向共振时，未来几分钟 mid-price 更容易延续漂移。**

这首先是 **raw alpha**，不是 filter。

### 2.2 这套 repo 怎么把信号变成交易
README 和源码给出的主链路比较清楚：

1. **标签是 cost-aware 的**  
   `mild` 中性带不是固定死的，而是：
   `max(MILD_RETURN_THRESHOLD, TRANSACTION_FEE_RATE * multiplier)`

2. **模型是 purged walk-forward**  
   `modeling.py` 用 `TimeSeriesSplit(n_splits=5)`，并且对 train/test、fit/validation 都加了与 `prediction_horizon` 等长的 purge gap。

3. **信号不是固定阈值，而是动态分位数**  
   `signal = EWM((prob_positive - prob_negative) * (1 - prob_mild))`
   
   再用上一段滚动窗口的：
   - `SIGNAL_SCORE_BUY_QUANTILE = 0.9`
   - `SIGNAL_SCORE_CLOSE_QUANTILE = 0.1`
   做买入/平仓阈值。

4. **执行回测是保守的 taker 风格**  
   `hft_backtesting.py` 明确写的是：
   - long-only
   - next row 的 `best_ask` 买入
   - next row 的 `best_bid` 卖出
   - entry / exit 都扣手续费
   - `MIN_HOLD_SECONDS = max(60, PREDICTION_HORIZON // 3)`

这几个点拼起来以后，repo 真正给 desk 的不是“高命中率”，而是：

> **一套相对诚实的、避免时间泄漏、并且把成本提前写进标签和执行层的微结构 raw alpha 骨架。**

### 2.3 最重要的几个数字
repo 当前 `config.py` 里最关键的参数是：

- `PREDICTION_HORIZON = 180`（约 `3m`）
- `TRANSACTION_FEE_RATE = 0.001`（单边 `10 bps`，round-trip 约 `20 bps`）
- `SIGNAL_SCORE_WINDOW_MINUTES = 60`
- `BUY_QUANTILE = 0.9`
- `CLOSE_QUANTILE = 0.1`
- `MIN_HOLD_SECONDS = 60`

但更值得看的，是 repo 已经提交的 `output_minute/overall_metrics_*.csv`：

**3m 版本：**
- trade count：**`34`**
- avg holding time：**`1898.9s`**（约 `31.6m`）
- cumulative gross return：**`+0.253%`**
- cumulative net return：**`-3.098%`**
- max drawdown：**`-4.12%`**

**15m 版本：**
- trade count：**`20`**
- avg holding time：**`3691.4s`**（约 `61.5m`）
- cumulative gross return：**`+1.793%`**
- cumulative net return：**`-0.223%`**
- max drawdown：**`-2.17%`**

**30m 版本：**
- trade count：**`18`**
- avg holding time：**`4193.1s`**（约 `69.9m`）
- cumulative gross return：**`+2.003%`**
- cumulative net return：**`+0.183%`**
- max drawdown：**`-2.13%`**

这组数字最值钱的地方在于它回答了一个很硬的问题：

1. **gross edge 不是完全没有**，而且 horizon 拉长后更明显；
2. **单边 10 bps / round-trip 20 bps 的 taker 假设，足够把 3m~15m 基本压平**；
3. **同样的微结构特征，不一定该交易成“更快更短”的 HFT，反而可能要往更慢的持有期迁移。**

这比“accuracy 高不高”对 desk 更重要。

### 2.4 这份 repo 最值得注意的两个限制
#### 限制一：它训练的是方向分类，但执行只做了 long-only
模型本身是三分类：`negative / mild / positive`。

也就是说，repo 明明已经在学：
- 哪些状态更可能向上
- 哪些状态更可能向下
- 哪些状态不值得做

但回测只把它变成了 **long-only timing**，没有对 `negative` 一侧做对称 short。

对 desk 来说，这意味着：

> **repo 现在展示出来的，不是这条 raw alpha 的上限；真正应该测的是 long/short 对称版。**

#### 限制二：artifact 版本和 config 存在不一致
`config.py` 里：
- `PREDICTION_HORIZON = 180`（约 `3m`）
- 但 `VERSION = "_30m_from_1s_ticks_smoothed"`

同时 repo 又提交了 `3m / 10m / 15m / 30m` 多套输出文件。

这说明：
- repo 里**研究思路是真的**；
- 但**版本管理并不干净**，不能把它直接当严格可审计 benchmark。

再加上原始输入文件 `gemini_24h_analysis.csv` 并未随 repo 一起发布，所以它是一个 **高信号 research scaffold**，但还不是 clean replication artifact。

## 3. 为什么和当前项目有关
如果问：**为什么这篇比再补一个泛 filter 更值得？**

答案是：因为它补的还是 raw alpha，而且补的是当前素材池里很需要的一条细分支——**单资产、微结构、可往 `1m/3m/5m/15m` 迁移的方向型 alpha 骨架**。

具体说有三点：

1. **它不是只给解释层。**  
   base alpha 很清楚，就是盘口压力和订单流能不能预测几分钟后 drift。

2. **它回答了“horizon 选哪里”这个 desk 真问题。**  
   不是所有 1 秒级特征都该拿去做 1~3 分钟；这份 repo 给出的更像是一个 **horizon sweep 实验框架**。

3. **它比纯论文更快进入最小实验。**  
   特征表、purged CV、动态阈值、回测骨架都已经有了；对当前项目来说，直接把数据源替成 Binance/Bybit 公共 feed 就能开始 first verdict。

## 3.5 策略拆解（必填）
- 方向属性：单资产、方向型、事件驱动，repo 当前实现为 long-only；desk 更应改成 long/short 对称版
- 基础 alpha：盘口失衡、microprice 偏移与净订单流的共振，会在未来 `3m~30m` 里留下可学习的 mid-price drift
- entry：`signal_score > rolling 0.9 quantile` 时，在下一条 quote 的 `best_ask` 进场；desk 版建议改成 `p(pos)-p(neg)` 的双侧 threshold
- exit：`signal_score < rolling 0.1 quantile` 时，在下一条 quote 的 `best_bid` 平仓；另有最小持有时间约束
- sizing：repo 是接近满仓的全有全无 long-only；desk 版应改成 `|p(pos)-p(neg)|` 分层，或 inverse-vol / edge-proportional sizing
- risk：单品种 BTC、单 venue、quote latency、spread 突刺、事件流缺口、版本管理不干净、原始数据缺失
- cost：repo 假设 **单边 `10 bps`**，这几乎决定了 3m/10m/15m 版的生死；必须重新跑 maker/taker 梯度
- 更适合的 regime：高流动性主币、深盘口、低显性成本窗口；重大新闻/盘口失真时需要单独隔离
- 主要 veto：spread 抬升、盘口不连续、数据采样中断、极端事件时 next-quote 假设失真

## 4. 这份 repo 里哪些组件最值得偷
### 4.1 最值得先偷的不是模型，而是“诚实的研究框架”
对 desk 来说，最值得复用的有四件：

1. **cost-aware label**：先把小于成本的 move 归到 `mild`
2. **purged walk-forward**：避免 horizon overlap 泄漏
3. **动态滚动分位阈值**：不用死阈值硬切
4. **把分类概率转成 signal score**：而不是直接 argmax 硬开平仓

### 4.2 第二值得偷的是 feature family，而不是具体 feature importance 排名
即便不照搬 repo 全部列名，也至少应该保留这三族：

- **盘口失衡族**：`imbalance_1 / imbalance_5 / depth pressure / microprice-mid`
- **流族**：`signed trade flow / passive flow / net order flow`
- **波动-状态族**：秒内 realized variation、spread variation、quote update intensity

这是最容易快速转译到 Binance/Bybit 公共 feed 的部分。

## 5. 可复刻的最小实验
### 最小实验 A：先做 Binance `BTCUSDT perp` 的对称 long/short 版本
1. **数据源：** Binance Futures 公共 `bookTicker + aggTrades`，聚合成 `1s`
2. **目标：** 先做 `180s / 300s / 900s` 三档（约 `3m / 5m / 15m`）
3. **特征：** 只保留最核心的三族：盘口失衡、净订单流、秒内波动状态
4. **标签：** `negative / mild / positive`，中性带至少覆盖预计 round-trip cost
5. **模型：** 继续用 purged 5-fold walk-forward
6. **交易：** 不做 long-only，改成：
   - `edge > q90` 做多
   - `edge < q10` 做空
   - 中间空仓
7. **成本：** 至少跑 `2 / 4 / 8 / 12 / 20 bps round-trip` 五档

### 最小实验 B：把“更快”与“更慢”做成同一张生存表
不要一上来执着 `3m`。直接做一张 grid：

- horizon：`60s / 180s / 300s / 900s`
- hold：`30s / 60s / signal-exit / 1x horizon / 2x horizon`
- execution：`taker / maker-lite / maker-first`

输出只看三件事：
- gross 是否单调改善
- net 在哪一档第一次转正
- avg holding time 是否明显长于预测 horizon

如果像 repo 一样出现 **“预测 horizon 很短，但实际持有很长”**，就说明这更像一条 **slower drift timing**，不是 ultra-fast alpha。

### 最小实验 C：验证 short 侧到底是不是被 repo 白白浪费了
repo 现在最大的未测空白，就是它明明学了 `negative`，却没交易 short。

下一步必须单独回答：
1. `negative` 侧 precision / recall 是否比 `positive` 更稳定？
2. short 侧在 perp 上是否比 long 侧更容易覆盖成本？
3. long+short 合并后，trade count / exposure / drawdown 会不会比 long-only 更诚实？

## 6. 风险与边界
- **原始数据未附 repo**：可复现，但不是开箱即跑。
- **版本管理不干净**：`PREDICTION_HORIZON` 与 `VERSION` 不一致，说明 artifact 需要二次审计。
- **回测执行很简化**：next-quote bid/ask 不是 queue-aware simulator。
- **当前展示是 long-only**：不能把它当这条 alpha 的最终 verdict。
- **单边 10 bps 假设很重**：更像在测“这条 alpha 能不能扛 taker 税”，不是最优 execution 上限。

## 7. 下一步怎么测
1. **先把 repo 框架平移到 Binance/Bybit 公共数据**，不要先纠结 Gemini。
2. **优先补 long/short 对称版**，这是当前 repo 最大漏项。
3. **先做 horizon/cost/hold 三维表**，别把 1 秒特征天然理解成 1~3 分钟就该最强。
4. **若 `15m` 仍 gross 正、net 近平，先试 maker-first 和 edge buffer；若 `3m` gross 都弱，就不要继续在 execution 上硬救。**

## 8. 来源
- Repo author: `kailiu0712`
- Repo title: *-5-min-level-Directional-Prediction-for-Crypto-HFT*
- Repo created: `2026-03-15`
- Repo URL: https://github.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT
- README raw URL: https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/README.md
- Config raw URL: https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/config.py
- Core code URLs:
  - https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/feature_engineering.py
  - https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/modeling.py
  - https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/hft_backtesting.py
- Output metrics URLs:
  - https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/output_minute/overall_metrics_3m_from_1s_ticks_smoothed.csv
  - https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/output_minute/overall_metrics_15m_from_1s_ticks_smoothed.csv
  - https://raw.githubusercontent.com/kailiu0712/-5-min-level-Directional-Prediction-for-Crypto-HFT/main/output_minute/overall_metrics_30m_from_1s_ticks_smoothed.csv
