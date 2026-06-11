# 别把 volume shock 统一当 continuation：这篇 2022 RIBAF 更该先测的是「同币 5m return×volume shock 的 coin-specific polarity」raw alpha

- 时间：2026-03-29 06:48 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：同一币种在 `5m` 出现“大收益 + 异常放量”后，后续 `1~3` 根并不存在统一方向；`BTC/XRP` 更像 exhaustion fade，`ETH/SOL` 更像 shock continuation，因此更适合做 **coin-specific polarity map**，而不是全市场统一的 volume-confirmation 规则
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/time-series/post-shock/volume-return/polarity-map/continuation/mean-reversion/single-asset/btc/eth/sol/xrp/doge/ada/binance-perpetual/5m/15m/1m/3m/paper/public-data/cost
- 证据类型：2022 RIBAF ScienceDirect 摘要/section snippets + Crossref 元数据 + Binance USDⓈ-M Perpetual 公共 `5m` 本地 sanity check

## 1. 这次看了什么

主看 **Larisa Yarovaya, Damian Zięba (2022), _Intraday volume-return nexus in cryptocurrency markets: Novel evidence from cryptocurrency classification_, Research in International Business and Finance, Vol. 59, DOI: `10.1016/j.ribaf.2021.101592`**。

- Authors：Larisa Yarovaya, Damian Zięba
- Year：2022（online 2021, journal issue 2022）
- Title：_Intraday volume-return nexus in cryptocurrency markets: Novel evidence from cryptocurrency classification_
- Venue：Research in International Business and Finance
- DOI：`10.1016/j.ribaf.2021.101592`
- Readable URL：<https://www.sciencedirect.com/science/article/abs/pii/S0275531921002130>
- DOI URL：<https://doi.org/10.1016/j.ribaf.2021.101592>
- Repo URL：未见作者公开 repo

这篇 paper 表面写的是 **volume-return relationship**，但对当前 desk 更有价值的读法，不是再说一遍“放量很重要”，而是：

> **高频里，volume 更像一个“事件放大镜”，但它放大的不是统一 continuation，而是不同币种、不同频率下完全不同的 post-shock polarity。**

翻成人话：

- 别把所有 `volume spike` 都当成趋势确认；
- 也别把所有 `volume spike` 都当成 exhaustion；
- 更诚实的做法，是给每个 major coin 建一个 **continuation / fade polarity map**，只在自己的优选方向上交易。

这条线对我们是 **raw alpha**，不是纯 filter。因为 entry/exit、方向、持有期都能直接冻结出来。

## 2. 论文真正给 desk 的核心东西

### 2.1 论文不是只看 BTC，而是 30 个币、多个频率、并专门比较频率衰减

作者用的是 **30 个高成交加密货币**，样本期：

- `2018-02-15 ~ 2019-07-30`
- 频率：`5m / 20m / 30m / 1h`，并用 daily 做稳健性补充
- 方法：**non-parametric Granger non-causality test** + copula robustness

这点对 desk 很关键，因为它不是只给一个“BTC 特例”，而是在问：

> **return 和 volume 的因果关系，到了 intraday 多频率以后，究竟还剩什么？**

### 2.2 最该拿走的一句不是“volume predicts return”，而是“关系会随频率变、且币种不统一”

论文摘要式结论其实很克制：

- **对大多数币，returns Granger-cause volumes**；
- 也有若干 **bidirectional causality**；
- **volume-return 关系会随着频率下降而衰减 / 消失**；
- 作者还专门研究了 **Bitcoin volume 对其他 29 个币的 returns / volumes 的影响**。

这意味着短周期 desk 不该把 volume 读成一个静态因子，而该读成：

1. **越短频，volume 越有可能只是“刚发生过冲击”的痕迹**；
2. 既然 volume 往往是被 return 先推出来的，那后面更该看的是：
   - 这波冲击是继续扩散？
   - 还是已经接近 exhaustion？
3. 而这个答案，很可能 **不是全市场同一个方向**。

这正好对冲了我们常见的一种坏习惯：

> 看见放量阳线，就自动脑补 continuation；看见放量阴线，就自动脑补加速。

这篇 paper 更像是在提醒：**先分币，再分频，再决定 polarity。**

### 2.3 作者还用了“cryptocurrency classification”去解释差异，这给了我们一个更轻的 desk 版本

论文里会用一些静态属性解释差异，比如：

- founder’s country of origin
- headquarters
- protocol / token
- consensus algorithm

对学术解释是有帮助的，但对 desk 来说，最小可行版不需要先把这些静态标签做满。

更便宜、也更贴近交易的 desk 读法是：

> **直接做 rolling polarity map：同样是 `|ret|` 大、`volume_z` 大的事件，哪些币后面更适合 follow，哪些币更适合 fade。**

也就是说，先把论文的“分类解释差异”翻译成交易层的“分类决定方向”。

## 3. 本地 5m sanity check：确实不是一个统一方向的世界

为了避免只停在摘要，我用 **Binance USDⓈ-M Perpetual 公共 `5m` kline** 做了一个最小快检：

- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT / DOGEUSDT / ADAUSDT`
- 样本：最近约 `5000` 根 `5m` bar / 每币（约 17 天）
- 事件定义：
  - `|ret_5m| >= 0.5%`
  - `log(quote_volume)` 对过去 `72` 根做 z-score，要求 `z >= 2.0`
- 执行：**next-bar open** 入场
- 持有：`1 / 2 / 3` bars
- 成本：这一步只是 polarity sanity check，**尚未扣费**
- artifact：`reports/artifacts/quant_digests/20260329_volume_return_polarity/summary_z2_ret50bp.csv`

### 3.1 几个最有用的数字

在完全相同的事件定义下，结果不是“一刀切”：

**更像 fade / contrarian 的：**

- `BTCUSDT`：
  - 反向持有 `3 bars` 平均 **+7.17 bps**，`n=30`，胜率 **56.7%**
- `XRPUSDT`：
  - 反向持有 `1 bar` 平均 **+7.56 bps**，`n=37`，胜率 **59.5%**
  - 反向持有 `3 bars` 平均 **+4.56 bps**，胜率 **56.8%**

**更像 continuation 的：**

- `ETHUSDT`：
  - 顺向持有 `2 bars` 平均 **+10.34 bps**，`n=65`，胜率 **52.3%**
  - 顺向持有 `3 bars` 平均 **+8.47 bps**
- `SOLUSDT`：
  - 顺向持有 `2 bars` 平均 **+7.30 bps**，`n=54`
  - 顺向持有 `3 bars` 平均 **+8.26 bps**

**边际较弱 / 暂不急着上桌的：**

- `DOGEUSDT`：顺向 `2 bars` 约 **+4.85 bps**，但 hit rate 只有 **49.3%** 左右
- `ADAUSDT`：顺向 `3 bars` 约 **+4.38 bps**，强度偏弱

一句话总结：

> **同样是“大波动 + 放量”，BTC/XRP 更像短时过冲后回吐，ETH/SOL 更像惯性继续扩散。**

这和论文的主结论是相容的：**volume-return 关系有，但不是单一方向，也不会跨币自动统一。**

### 3.2 这条线为什么比“继续做 volume confirmation gate”更值得先测

因为它更接近一个完整 raw alpha：

- 有清楚的 **event trigger**：`abs(ret)` + `volume_z`
- 有清楚的 **方向判定**：按币种 polarity map 走 continuation 或 fade
- 有清楚的 **持有期**：`1~3 bars`
- 能做 **单资产**，不需要先建复杂 basket
- `1m/3m/5m/15m` 都能映射

相比之下，如果继续把它只写成“放量确认趋势”的 shared gate，反而会过早把信息压扁。

## 3.5 策略拆解（必填）

- 方向属性：post-shock / event-driven / single-asset 短窗 raw alpha
- 基础 alpha：同币 `5m` 大收益 + 异常放量后，未来 `1~3` 根的最佳方向取决于币种自身的 polarity，而不是统一 continuation 或统一 fade
- regime：只在 major perp、盘口正常、spread 正常、成交没塌的时候启用
- filter / veto：
  - `volume_z < 2` 不做
  - `abs(ret_5m) < 0.5%` 不做
  - 数据异常、宏观大事件分钟、资金费结算前后 `±5m` 可先 veto
- sizing / risk / execution：
  - 单笔风险固定
  - next-bar open 入场
  - 默认 no-overlap
  - round-trip 成本先按 `4 / 6 / 8 bps` 三档压测
  - 若做反向 fade，优先看 maker 能否减少成本 cliff

## 4. 为什么和当前项目直接相关

这轮它值得进 digest，不是因为“volume 是经典因子”，而是因为它正好补我们当前素材池里一块还不够系统的东西：

- 我们已经有：
  - cross-crypto lead-lag
  - order-flow shock
  - short-horizon reversal
  - basket stat-arb
- 但还缺一条更朴素、可快速批量化的：
  - **single-asset post-shock polarity map**

这条线的优点是：

1. **raw alpha 很清楚**：不是解释型，不是纯综述
2. **公开数据可拿**：Binance/OKX/Bybit 都能先跑
3. **适配短周期**：天然服务 `1m / 3m / 5m / 15m`
4. **还能反哺别的 alpha**：
   - breakout 的 follow-through veto
   - reversal 的 event admission
   - execution 的 size-up / size-down

但主身份仍应是 **raw alpha 候选**，不是先天 filter。

## 5. 可复刻的最小实验

### 5.1 数据源与公开性

**公开可得，且很快能拿到。**

- 数据源：Binance USDⓈ-M Perpetual 公共 kline / aggTrade / taker volume proxy
- 最小字段：
  - `open, high, low, close`
  - `quote_volume`
  - 若升级版可加 `taker_buy_quote_volume`
- 更新频率：分钟级 / 秒级都可
- 最小实验周期：
  - `1m / 3m / 5m` 主实验
  - `15m` 做 transfer / hold-extension

### 5.2 第一版规则先冻结，不要一开始就过拟合

**Rule v0：**

1. 对每个币单独算：
   - `ret_tf`
   - `log(volume)` 的 rolling z-score（先用 `72` bars）
2. 定义事件：
   - `abs(ret_tf) >= threshold`
   - `volume_z >= z_threshold`
3. 方向先按**月度滚动 polarity map** 冻结：
   - continuation coin：按冲击方向做
   - fade coin：反向做
4. 执行：`next-bar open`
5. 持有：`1 / 2 / 3 / 4` bars
6. no-overlap
7. 成本：至少压 `4 / 6 / 8 bps`

### 5.3 最小实验矩阵

先别上全市场，先做最短路径：

- 资产：`BTC / ETH / SOL / XRP`
- 周期：`1m / 3m / 5m / 15m`
- 事件阈值：
  - `abs(ret)`：`40 / 50 / 60 bps`
  - `volume_z`：`1.5 / 2.0 / 2.5`
- 方向：
  - `always continuation`
  - `always fade`
  - `monthly polarity map`
- 持有：`1 / 2 / 3` bars
- 成本：`4 / 6 / 8 / 10 bps`

要看的不是只有总收益，而是：

- event count
- mean / median return per trade
- hit rate
- MFE / MAE
- 不同 market regimes 下是否翻面

## 6. 这条线当前最诚实的 desk verdict

我的判断：**值得进入 raw alpha 素材池，而且优先级不低。**

原因不是它已经被证明“必赚”，而是它满足当前主线最看重的几件事：

- base alpha 清楚
- 数据公开可得
- 最小实验便宜
- 可直接冻结成 entry / exit / sizing / risk / cost
- 还能自然分叉成 continuation 与 mean-reversion 两条子线

更重要的是，它提醒我们：

> **volume 本身不是方向，volume shock 只是事件放大镜；真正的方向，要按币种 polarity 去读。**

## 7. 下一步怎么测（必须落到执行）

### Next step 1
先做 **`BTC / ETH / SOL / XRP` 的 180d `5m` 冻结版 clean replication**：

- 统一 `next-bar open + no-overlap`
- `abs(ret_5m)` 与 `volume_z` 走固定阈值网格
- continuation / fade / monthly polarity-map 三臂并排
- 成本直接压到 `6 bps/side`

目标：先回答 **polarity map 在成本后是否仍比两端常数方向更诚实**。

### Next step 2
把胜出的币种-方向组合，迁移到：

- `1m / 3m`：看是否更像 execution alpha
- `15m`：看是否只剩 filter 价值

目标：回答它到底是 **主策略** 还是 **更快 trigger / 更慢 gate**。

### Next step 3
若 `BTC/XRP fade` 与 `ETH/SOL continuation` 都能过第一轮，再升级成：

- **coin-specific event book**
- 每天按 rolling 30d 更新 polarity score
- 与现有 breakout / reversal archetype 做 admission overlay 对照

但这一步必须放在第一轮成本后仍存活之后，不能先脑补成大系统。

## 8. 一句话结论

> **这篇 2022 RIBAF 对短周期 desk 最值钱的，不是“volume 有用”，而是“放量冲击后的方向要按币种分开读”——BTC/XRP 更像 fade，ETH/SOL 更像 continuation，足够先做一轮便宜而诚实的 raw-alpha clean replication。**
