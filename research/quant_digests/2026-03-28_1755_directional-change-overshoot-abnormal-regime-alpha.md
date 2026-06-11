# 别把 Directional Change 继续只当 breakout follow-up：这篇 2023 paper 更该先测的是「event-trigger overshoot capture + abnormal-regime veto」完整 raw alpha

- 主题类型：raw alpha
- 基础 alpha：**当价格从局部低点完成一次 Directional Change（DC）上行确认后，后续 overshoot 段存在可捕捉的顺势延续；但一旦出现 `α·θ` 级别的反向确认，或 HMM 把状态判成 abnormal regime，就应立即退出 / 停做。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-03-28 17:55 UTC
- 类型：论文
- 主题标签：raw-alpha/event-driven/directional-change/overshoot/trend/momentum/event-clock/hmm/regime-veto/adaptive-threshold/alpha-decay/binance/btc/eth/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2023 arXiv 全文 txt 抽取 + 规则/表格级结果核对

## 1. 这次看了什么

这次主看的是：

- **Authors**：Bing Wu, Xiangzu Han
- **Year**：2023
- **Title**：*Intelligent trading strategy based on improved directional change and regime change detection*
- **Venue**：arXiv preprint
- **DOI**：未见正式 DOI
- **Readable URL**：https://arxiv.org/abs/2309.15383
- **PDF URL**：https://arxiv.org/pdf/2309.15383
- **Repo URL**：未见作者官方公开 repo

一句话先说结论：

> **这篇东西最适合 desk 的，不是再把 DC 当成某个 breakout/follow-up 的确认器，而是把它直接升格成一个独立的 event-driven raw alpha：DC 上行确认后去吃 overshoot，反向 DC 确认或 abnormal regime 出现就撤。**

这和前面已经写过的 `DC first-hit follow-up gate` 不是一回事。那条线本质是 **filter / verdict**；这篇 paper 给的则是一个可以单独站起来的 **完整 raw alpha 骨架**。

## 2. 这篇 paper 的 base alpha 到底是什么

先按你要求回答一句：

> **base alpha = 事件驱动的短趋势延续。**

不是传统 fixed-bar 的 `r[t-1] -> r[t]`，也不是单纯 breakout 名词替换。

它真正做的事情是：

1. 不再按固定时间切 K；
2. 先用 **Directional Change（DC）** 在价格真正走出一段有意义的位移时才“记一次事件”；
3. 当上行 DC 被确认后，假设后面通常还会有一段 **overshoot**；
4. 但如果价格很快走出反向确认，或者 HMM 把市场切进 **abnormal regime**，就立刻退出/停做。

翻成人话：

> **先等市场自己走出“值得记录”的位移，再去吃它后面的续动；一旦路径形态不对，或者状态机说现在是异常期，就别硬扛。**

这就是一个清楚的 raw alpha，不是单纯 filter。

## 3. 为什么它值得进当前短周期素材池

和当前 desk 已经积累的材料对比，这篇 paper 有三个直接价值：

### 3.1 它补的是“事件时钟 raw alpha”，不是又一个固定 bar 动量

现在素材池里已经很多是：

- fixed-bar momentum / reversal
- cross-sectional rank
- funding / basis / pairs / lead-lag
- microstructure / order-flow / options-flow

但**真正用 event-clock 重采样价格路径**、并且能直接落成交易规则的 raw alpha 还不多。

DC 的价值就在这：

> **不是先定 `5m/15m` 再问价格怎么走，而是先看价格是否真的动到值得触发事件，再决定有没有交易。**

这对 crypto 很自然，因为 crypto 的“有事时很快、没事时很吵”。

### 3.2 它天然自带 path-aware exit，比“入场后固定拿 N 根”更诚实

paper 的主交易逻辑不是“买了以后机械 hold N 根”，而是：

- 上行 DC 确认后进场；
- 先尝试吃一段 **overshoot continuation**；
- 若走出反向 DC 确认，则提前撤；
- 若 regime 进入 abnormal，则暂停交易。

这比很多只会写 entry 的材料更完整，离 desk 需要的 `entry / exit / veto / risk` 更近。

### 3.3 它是 raw alpha + regime gate 一体化骨架

当前允许更灵活地读 paper：如果 paper 里有更适合我们 desk 的旁支想法，可以单独拎出来。

这篇最值钱的“旁支”其实就是：

- **raw alpha 本体**：DC-confirmed overshoot continuation
- **shared gate / risk layer**：RCD-HMM abnormal regime veto

所以它既能单独落地成一条策略，也能沉淀出一个可复用组件：

> **基于 DC 派生指标（RDC）的 abnormal regime veto。**

## 4. 论文里最值得拿走的证据

### 4.1 样本和实验体量不小

paper 用的是 **2019-01-01 到 2020-10-31** 的外汇 tick data，覆盖：

- **8 个货币对**
- **176 个 dataset 切片**
- **超过 3.9 亿条 price entries**

它不是小样本巧合，而是在多标的、多切片上看这个框架是否站得住。

### 4.2 关键 headline 不是“某个参数最好”，而是 IDC + HMM 组合整体明显更强

作者比较了四类方法：

- **FT**：固定阈值、上下行对称处理的基础 DC 策略
- **OPTT**：只优化阈值 θ
- **IDC**：在阈值之外再加入下行 decay coefficient `α`
- **ITA**：`IDC + RCD-HMM`

最重要的结果在 Table 3 / Table 4：

#### 收益（Cumulative Return Rate）

- **FT 平均**：`-24.36%`
- **OPTT 平均**：`-10.47%`
- **IDC 平均**：`16.89%`
- **ITA 平均**：`58.76%`

也就是说，**只做固定 DC 不够，单做参数优化也不够；真正把收益和稳健性同时拉起来的是“非对称 DC + abnormal regime veto”。**

#### 回撤（Maximum Drawdown）

- **FT 平均 MDD**：`19.08%`
- **OPTT 平均 MDD**：`13.30%`
- **IDC 平均 MDD**：`7.93%`
- **ITA 平均 MDD**：`3.53%`

这很关键：它不是“靠加大风险才多赚”，而是**收益上去、回撤还明显更低**。

### 4.3 几个单市场数字也很醒目

虽然我们不会直接把 FX 数字搬到 crypto，但几个点很说明问题：

- `EUR/USD`：ITA **137.47%**，明显高于 IDC **31.75%**
- `USD/JPY`：ITA **121.69%**，明显高于 IDC **17.29%**
- `USD/CAD`：ITA **75.86%**，高于 IDC **48.50%**

同时回撤端：

- `EUR/USD` 的 ITA MDD 只有 **1.03%**
- `USD/JPY` 的 ITA MDD 为 **1.96%**
- `USD/CAD` 的 ITA MDD 为 **2.77%**

这说明 abnormal-regime veto 并不是装饰件，而是真在压尾部风险。

### 4.4 统计检验也支持 ITA 排名第一

作者对 return 和 MDD 做了 Friedman / Conover 检验：

- 在 **收益** 上，ITA 平均排名 **1.0000**，显著优于 IDC / OPTT / FT
- 在 **回撤** 上，ITA 平均排名 **1.2381**，同样显著优于其余方法

这意味着 paper 给出的不是“个别 pair 运气好”，而是一个更系统的结构改进。

## 5. 真正该搬进 desk 的，不是整套 FX 假设，而是这 3 个组件

### 5.1 组件 A：自适应事件触发阈值 `θ`

paper 把 `θ` 设在 **[0.0003, 0.003]**，也就是大约 **3~30 bps** 的触发范围；并用 Bayesian Optimization 动态找最优值。

对 crypto，最可搬的不是精确数值本身，而是这个思想：

> **触发阈值必须自适应，不能全年拿一个固定值。**

尤其在 `1m/3m/5m/15m` 上，不同币、不同波动状态、不同 session 的合适 `θ` 会差很多。

### 5.2 组件 B：非对称回撤确认 `α·θ`

paper 不是把上下行完全对称处理，而是给 down move 一个 **decay coefficient `α`**，搜索范围 **[0.1, 1]**。

翻成人话就是：

> **不是每次上行事件都值得等到完整反转；有些时候只要出现较小级别的反向确认，就该认错离场。**

这个设计很 desk 化，因为它本质上是：

- 让 entry 去吃 overshoot continuation
- 让 exit 更快响应路径衰减

### 5.3 组件 C：RDC -> HMM abnormal regime veto

作者把 RDC（基于相邻 DC extremum 的 return / duration 指标）喂给 **2-state HMM**，输出：

- `S1 = normal`
- `S2 = abnormal`

交易规则里最值钱的一条其实很简单：

> **state = S2 时，直接暂停交易。**

对我们 desk，这个东西不一定只服务这条 DC 策略。它以后完全可以被拿去当：

- intraday momentum gate
- breakout veto
- shock-fade size-down overlay

## 6. desk 化后的最小可复现实验

### 6.1 先怎么把它翻译到 crypto

最小版不要从 tick 开始卷太深，先做 **bar-proxy DC**：

- **数据源**：Binance public `aggTrades` / trade websocket（若要更细），以及公开 `1m` klines（最小近似实验）
- **标的**：先 `BTCUSDT`、`ETHUSDT`，再加 `SOLUSDT`
- **执行频率**：事件在 `1m` 上判定；执行落在 `1m/3m/5m`，`15m` 仅做更慢版验证

### 6.2 最小 raw alpha 规则

先做 long-only 版本，别一开始就加反手：

1. 用 `1m` close 或 `1m` high/low 更新 DC 极值点；
2. 当价格从最近 trough 上行超过 `θ`，确认上行 DC；
3. **下一根 bar 开盘做多**；
4. 出场有三种：
   - 达到预设 overshoot 目标（例如从 trough 算的第二段延续）
   - 出现反向确认，幅度达到 `α·θ`
   - HMM/RDC 状态切到 abnormal
5. abnormal 状态下暂停新开仓；
6. sizing 先用固定风险或小额 vol-target，不用 paper 里的满仓设定。

### 6.3 第一轮参数怎么切

paper 给的 FX 搜索范围可以直接当起点，但 crypto 需要更现实：

- `θ`：先测 **5 / 10 / 15 / 20 / 30 / 40 / 60 bps**
- `α`：先测 **0.2 / 0.4 / 0.6 / 0.8 / 1.0**
- HMM：先固定 **2-state**
- RDC 输入：先用事件 return / duration 的简化版，不要一开始堆太多特征

### 6.4 成本与风控

paper 明确说了：**实验忽略 transaction costs**，而且假设 **short selling is not allowed**。

所以 desk 化时必须补这几件事：

- taker round-trip 先扣 **4 / 6 / 8 bps**
- 再测 maker+taker 混合版本
- 限制 abnormal regime 下不加仓
- 单笔风险先压在组合 NAV 的 **25~50 bps** 级别
- 先不做反手；long-only 过线再考虑 short 对称化

## 7. 为什么我认为它现在比再补一个普通 fixed-bar 动量更值得

因为它补的是 **raw alpha 素材池里还偏薄的一层：event-clock trend / overshoot capture**。

如果继续补普通 fixed-bar momentum，我们得到的多半还是：

- 又一个 lookback
- 又一个 threshold
- 又一个 volatility filter

而这篇给的是另一种价格组织方式：

> **先换时钟，再谈 alpha。**

这件事很重要，因为不少短周期 edge 不是“信号错了”，而是**采样时钟错了**。DC 正好提供了一个足够简单、又足够可复现的 alternative clock。

## 8. 风险与保留意见

- **不是 crypto 原生论文**：paper 在 FX tick data 上成立，迁移到 crypto 必须重新做成本与滑点检查。
- **原文是 long-only + 无成本**：所以 headline 收益不能直接照搬。
- **HMM 有过拟合风险**：尤其样本短、状态切换太勤时，容易把噪声学成 regime。
- **DC 参数很敏感**：paper 自己也证明 `θ` 和 `α` 会随时间漂移，所以不能把某组参数神化。
- **bar-proxy 会损失 tick 信息**：因此第一轮若 `1m` proxy 都没边，就别急着上 tick；但若 `1m` proxy 有边，再往 tick 提纯是合理的。

## 9. 下一步怎么测

### 第一轮：先验证它是不是“独立 raw alpha”，不是滤镜

1. `BTCUSDT / ETHUSDT` 上做 `1m` DC 事件流；
2. 不加任何外部 filter；
3. 只比较三种 exit：
   - 固定 `2θ` overshoot
   - `α·θ` 反向确认
   - `α·θ` + HMM abnormal veto
4. 看成本后是否仍有：
   - 正的 mean trade expectancy
   - 比 fixed-bar breakout 更低的 tail loss

### 第二轮：如果 raw alpha 过线，再扩成 shared component

- 把 `HMM abnormal veto` 拿去给现有 `5m/15m` breakout / continuation / shock-fade 做共享 gate；
- 对比“有无 DC-state veto”时的 trade survival、tail loss、break-even cost。

### 第三轮：再考虑 short side 和 cross-asset

- 如果 BTC/ETH long-only 过线，再测试：
  - short 对称化
  - leader coin DC event -> alt basket follow-through
  - same-state basket sizing

## 10. 来源

- **Wu, B., & Han, X. (2023).** *Intelligent trading strategy based on improved directional change and regime change detection*. arXiv preprint.
  - DOI: 未见正式 DOI
  - Readable URL: `https://arxiv.org/abs/2309.15383`
  - PDF URL: `https://arxiv.org/pdf/2309.15383`
  - Repo URL: 未找到官方公开 repo

- **Tsang, E. P. K., Chen, S.-H., Li, J., et al.**（文中方法脉络引用）Directional Change / regime detection 系列工作。
  - 这类文献主要提供 **DC event clock + RDC regime detection** 方法地基；当前 digest 的主证据仍以上述 2023 paper 为主。

- **Binance Public Market Data**（用于 desk 化最小实验）
  - Klines: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`
  - AggTrades: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#compressedaggregate-trades-list`
  - WebSocket trades / aggTrades 也可公开订阅，用于后续 tick 级提纯
