# 别把这篇 Hawkes LOB 论文只读成 event-time ML：更该先测的是「base imbalance × next-event clock」1m execution-trigger raw alpha

- 时间：2026-03-28 11:15 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/microstructure/lob/base-imbalance/hawkes/point-process/event-time/single-asset/execution-trigger/bitfinex/usdtusd/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2023 arXiv 全文 HTML + 本地 PDF 抽取 + Crossref 元数据 + 2023 IFAC precursor 元数据交叉
- 主题类型：raw alpha
- 基础 alpha：订单簿前几档形状不对称（base imbalance）本身就含有下一次有效价格变动方向信息；再叠加“下一次簿上事件很快发生”的 Hawkes event-time 预测，可以把这条信息变成更可执行的短周期方向信号
- 是否可独立复现：是（需要公开可抓的逐笔盘口/成交事件流；用交易所 websocket 即可做最小版）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（论文原版太贴近 1 秒级事件时钟且未计成本；但可很快 desk 化成 1m/3m 的最小完整实验）

## 1. 这次看了什么，为什么它比再补一篇泛 gate 更值得

这次主看的是：

> **Raffaele Giuseppe Cestari, Filippo Barchi, Riccardo Busetto, Daniele Marazzina, Simone Formentin (2023 arXiv / 2025 ECC)**  
> **Hawkes-based cryptocurrency forecasting via Limit Order Book data**

以及它明确承接的 precursor：

> **Riccardo Busetto, Simone Formentin (2023)**  
> **Continuous-time modeling of financial returns based on Limit Order Book data**

先回答这轮最重要的那句：**这篇东西的 base alpha 是什么？**

不是“LOB 很重要”，也不是“用 Hawkes 很高级”。

更直接地说：

> **盘口前几档的形状不对称，本身就带着下一次价格有效变动的方向信息；而当簿上事件到达很密、下一次 event 很快就要来时，这条方向信息更有机会在极短窗口里兑现。**

所以它不是纯 filter，也不是只服务某个 breakout / retest 的附庸。它本身就是一条**微结构 raw alpha**：

- alpha 本体：`base imbalance -> next-event return sign`
- event-time 放大器：`high self-excitation / short expected inter-arrival time`
- 执行定位：`1m 为主，3m 次之，5m 还能测，15m 更像聚合或上层编排窗口`

为什么这轮值得补它？因为最近 intake 里：

- cross-sectional / pairs / carry 已经很多；
- 纯外部慢变量（链上 / 宏观 / ETF）也不少；
- **但“盘口形状 + 事件时钟”这种可独立成型的微结构 raw alpha 家族，素材密度还不够。**

这篇虽然不是最终可直接上实盘的完整答案，但它给了一个很清楚的**可复现原子信号**：

> **book-shape edge 不该只按 bar-close 静态读，而该和“下一次事件多久来”一起读。**

## 2. 论文里真正有交易价值的部分是什么

论文的结构很简单：

1. 先证明 **Base Imbalance（BI）** 和未来 return sign 确实有关；
2. 再用 **Hawkes process** 预测“下一次 LOB event 何时发生”；
3. 把 event-time 预测喂给一个 **continuous output error (COE)** 模型，输出下一次 return sign；
4. 和几个 benchmark 比：
   - `Oracle`：假设你神知道下一次 event 时间
   - `Naive`：假设下一次 event 固定 1 秒后到来
   - `MA`：假设下一次 event 在过去 60 秒平均间隔后到来
   - `Hawkes`：根据自激强度动态预测

真正值钱的不是“又一个分类器”，而是这个拆法：

> **方向信息和事件时钟要分开建模。**

这点对 desk 很重要，因为很多短周期研究会把“有没有 edge”和“edge 何时兑现”揉成一个黑箱概率。这个 paper 则把它拆成：

- **signal layer**：book shape / imbalance
- **clock layer**：event arrival intensity

这比直接做一个 end-to-end 黑箱分类器更容易移植、调试、做失败归因。

## 3. Base alpha 到底长什么样

论文沿用 precursor 里的 **Base Imbalance（BI）** 定义。它不是常见那种“买一量 - 卖一量”的单点深度差，而是用**盘口前若干档价格曲线形状**去衡量 bid / ask 两边的“厚薄不对称”。

文中的公式可写成：

`BI_k = ((P_bid,1 - P_bid,10) - (P_ask,10 - P_ask,1)) / ((P_bid,1 - P_bid,10) + (P_ask,10 - P_ask,1))`

翻成人话：

- 不是看一档挂了多少量；
- 而是看**前 10 档 bid 曲线和 ask 曲线谁更“陡 / 厚 / 近”**；
- 这更接近“短期价格往哪边更容易被推过去”的几何结构。

论文在去掉零收益事件后，把数据按 decile 分箱，得到：

- **`corr(avg BI, avg future return) = -0.96`**

这个数字非常夸张。它不等于“直接可交易收益率 = 很高”，但说明：

> **BI 和未来 return sign 的关系不是弱相关噪音，而是强结构。**

所以真正的 raw alpha，不是“Hawkes 预测下一次 event 很厉害”，而是：

> **盘口形状本身就带方向，只是这个方向需要配合“事件马上要来”才更容易兑现。**

## 4. 数据、样本和论文原始实验口径

论文用的是 **Bitfinex 上 USDT/USD 的 LOB 数据**，由 **CryptoTick** 提供：

- 时间范围：**2019-04-13 到 2019-05-07**
- 总记录数：**1,615,982 条 LOB records**
- 深度：**最多 50 档**
- 时间戳分辨率：**至少到 1 秒**

作者还给了几个很重要的口径提醒：

- **零收益事件占约 80%**，这些都被剔除了；
- 剩余非零收益事件里，**约 34% 有 1 分钟缺口**；
- 也就是说，这不是那种“完整丝滑、无缺失”的理想高频样本。

验证与仿真设置：

- **50 个验证场景**
- 每个场景 **2 分钟**
- Hawkes 训练窗：**20 分钟**
- COE 训练窗：**50 分钟**
- Hawkes warm-up：**2.5 分钟**
- 预测窗：**5 秒**

交易仿真规则非常朴素：

- 预测 sign 为正：买入 **10,000 美元** USDT
- 预测 sign 为负：做空 **10,000 美元** USDT
- sign 预测对则盈利，错则亏损
- **不计交易成本**

这也直接决定了我们该怎么读这篇文章：

- **它是 raw alpha 研究，不是可直接搬去实盘的 PnL 宣传册；**
- 真正可迁移的是结构，而不是原文里那条“USDT/USD + 无成本”的 toy trading rule。

## 5. 论文结果该怎么读，别读歪

论文的 headline 是：

- `Hawkes` 在 **return sign accuracy** 上优于 `Naive` 和 `MA`
- 在 **累计 profit** 上也优于两者
- 效果接近 `Oracle`，但当然仍不如 `Oracle`

虽然文中可读文本没有直接给出每个 boxplot 的精确数值，但有三个结果是明确的：

1. **BI 本身确实带强方向结构**（decile 相关系数 `-0.96`）
2. **单纯知道 BI 还不够，event-time 预测质量会影响收益兑现大小**
3. **Hawkes 的价值主要不是换 alpha 本体，而是改善“什么时候该相信它”**

这点很关键，因为如果你把这篇 paper 简化成：

> “Hawkes 比 Naive 更准”

那就读窄了。

更实用的 desk 读法应该是：

> **book-shape alpha 的兑现速度，本身就是状态变量；当 event clustering 很强、下一次簿上事件很快发生时，盘口信息更值得下手。**

## 6. 为什么我把它归成 raw alpha，而不是 filter / overlay

因为它首先回答得清：**基础 alpha 是什么。**

不是 trend gate，不是 regime veto，不是 position sizing。它有自己独立的方向逻辑：

- 输入：盘口前几档的 shape asymmetry
- 标签：下一次有效 return sign
- 兑现窗口：超短 event-driven horizon

它当然也能往下拆成：

- filter：只在高-intensity 时段启用其他 alpha
- execution veto：event sparse 时别追
- maker skew：event clustering 强时调整挂单方向

但这些都是**二次利用**。

它的第一性身份仍然是：

> **可独立建模、可独立回测、可独立关停的微结构 raw alpha。**

## 7. desk 化以后，最值得先做的不是“全量 Hawkes”，而是一个诚实的 1m execution-trigger 版本

原论文太贴近 1 秒级 event clock；如果你直接照抄，多半会遇到两个问题：

1. 自己没有那样干净的逐 event 数据；
2. 就算有，taker 成本也可能把极短 edge 吃没。

所以更适合 desk 的最小版本，不是“完整复制论文”，而是把它拆成三层：

### 7.1 Signal：盘口形状不对称

先复刻一个更朴素的 `BI_t`：

- 用公开 websocket 盘口快照取 top-10 depth
- 每 `1s` 或 `5s` 重采样一次
- 计算：
  - top-1 vs top-10 的 bid/ask span
  - 或等价的 depth-weighted slope / convexity proxy
- 对 `BI_t` 做 rolling z-score

### 7.2 Clock：事件密度 / 自激强度

第一版甚至不必硬上完整 Hawkes MLE，可以先做 proxy：

- 最近 `5s / 10s / 30s` 的 order-book update count
- cancel/add burst ratio
- trade count burst
- book-change intensity EMA

等确认“clock 确实改善兑现”后，再升级成真正的 Hawkes。

### 7.3 Trigger：只在“alpha 可能很快兑现”时开仓

初版规则可以非常诚实：

- **long**：
  - `BI_z` 进入极端分位（如 `97.5%`）
  - 且 `event-intensity_z` 高于某阈值（如 `80%` 分位）
- **short**：
  - `BI_z` 进入反向极端分位（如 `2.5%`）
  - 且 `event-intensity_z` 同样很高

这就把论文的精神保住了：

> **不是 book shape 一极端就交易，而是 book shape 极端 + next-event 真的快要来。**

## 8. 1m / 3m / 5m / 15m 上怎么摆

这里要很诚实。

### 8.1 最适合：`1m`

因为这条线本质就是微结构 + event-time。

- `1m` 最接近原论文的短兑现逻辑；
- 也最容易看出 edge 是不是只存在于极短 markout；
- 如果 `1m` 都没东西，往上大概率只会更稀释。

### 8.2 次适合：`3m`

这是最值得测的“可交易化 compromise”。

- 比 1m 更接近 desk 实际下单/成交/持仓节奏；
- 还能保留相当一部分微结构信息；
- 对成本也稍微更宽容。

### 8.3 仍可测：`5m`

`5m` 更像在问：

> **盘口形状与 event burst 是否会引出一个更长的 follow-through，而不是只是一跳 micro-move？**

如果 `5m` 还有残留 edge，这条线的价值会大很多，因为它能更容易接入当前短周期策略栈。

### 8.4 `15m` 不该硬装成主信号

到了 `15m`，这条线更像：

- execution trigger 的聚合统计量；
- 或者给更慢 alpha 的 admission / veto；
- 或者做 maker skew / size adjustment。

也就是说：

- `1m / 3m`：更像 alpha 本体
- `5m`：看能否外溢成更稳 pocket
- `15m`：更像上层编排变量

## 9. 最小可复现实验：公开数据、更新频率、实验口径

### 9.1 数据源

可直接用公开可抓的交易所 websocket：

- **Binance Spot / Futures**
- **OKX**
- **Bybit**

最小版只需要：

- top-of-book 或 top-10 depth updates
- trades / aggTrades
- mid / spread

### 9.2 公开性

- **公开可得**
- 不需要 vendor 才能做第一版
- 不需要链上解析或专有终端

### 9.3 更新频率

- 原始 feed：毫秒到秒级
- 研究重采样：建议先做 `1s`、再聚合到 `1m / 3m / 5m / 15m`

### 9.4 最小复现实验口径

标的先别铺太广，建议先做：

- BTCUSDT perp
- ETHUSDT perp
- SOLUSDT perp

回测框架：

1. **特征**
   - `BI_t`
   - `event_intensity_t`
   - spread
   - trade-count burst
   - taker imbalance（作为对照，不是必须）
2. **标签**
   - `1m / 3m / 5m / 15m` forward mid return sign
   - 以及 bps markout
3. **比较组**
   - A: `BI only`
   - B: `intensity only`
   - C: `BI × high-intensity gate`
   - D: `full Hawkes/COE`（第二阶段再做）
4. **成交假设**
   - maker-first
   - taker-at-close
   - 半档/一档滑点压力测试
5. **评估**
   - conditional hit rate
   - average markout
   - extreme quantile precision
   - turnover / fill feasibility
   - cost-after edge

## 10. 一个更像策略的初版骨架

如果要把它写成真正能跑的最小策略，而不是论文摘要，我会先这么做：

### 10.1 Entry

- `BI_z` 极端 + `event_intensity_z` 高
- 只做流动性较好的币
- 只在 spread 没明显恶化时进场

### 10.2 Exit

三层足够：

1. **时间退出**：`1m / 3m / 5m / 15m` 多档
2. **信号回落退出**：`BI_z` 回到中性带
3. **price-based stop**：固定 bps 或 micro-ATR

### 10.3 Sizing

不建议满仓，建议：

- `size ∝ clip(|BI_z| * intensity_z, 0, cap)`
- 再按短窗 realized vol 做归一
- 对同一资产连发信号设 cooldown

### 10.4 Risk / Cost

最关键的不是方向逻辑，而是三件事：

- spread 会不会在你最想下手时突然变宽；
- 高频盘口更新是否能稳定抓到；
- edge 是否只够覆盖 paper world、覆盖不了真实手续费。

所以这条线很适合：

- **maker / passive bias**
- **event-triggered taker only on strongest quantiles**

而不适合无脑每次 sign 都打。

## 11. 这篇 paper 最大的坑，必须先写在前面

这篇东西有价值，但坑也很明显：

### 11.1 标的是 `USDT/USD`，不是 BTC/ETH perp

它证明的是**结构存在**，不是直接证明这条线在 Binance perp 一样赚钱。

### 11.2 horizon 非常短

原文更接近 next-event / next-few-second 逻辑。迁移到 `1m/3m/5m` 必须先验证是否仍有外溢。

### 11.3 不计成本

这是最直接的红旗。任何 taker-heavy 读法都可能失真。

### 11.4 剔除了大量 zero-return events

原文剔除了约 **80%** 零收益事件；这对“可预测性”一定是有帮助的。实盘时必须把“没动的时候怎么办”也纳入规则，不然会高估 edge。

### 11.5 样本不算长

- 时间范围不长；
- 验证只用 **50 个 2 分钟场景**；
- 更像 proof-of-concept，不像大样本生产级验证。

## 12. 给当前 desk 的最终判断

如果只问一句：**这是不是值得进素材池？**

我会给 **是**。

原因不是论文回测多漂亮，而是它补的是一个很明确、而且当前还不算拥挤的 raw alpha 原子：

> **盘口形状 edge 要和 event clock 一起读。**

如果只问一句：**是不是现在就该当完整实盘策略？**

我会给 **否**。

更合理的定位是：

- **一级身份**：`1m / 3m` execution-trigger raw alpha 候选
- **二级身份**：更慢 alpha 的 microstructure admission / veto
- **最优动作**：先做一个公开 websocket 的最小复制实验，验证 edge 是否能从 next-event 外溢到 1m/3m markout

## 13. 下一步怎么测

先别上全量 Hawkes，先做一个 **两阶段最小实验**：

### Phase A：验证 alpha 本体

- 用 Binance / OKX 公开 websocket 抓 30 天 BTC/ETH/SOL perp
- 每秒重采样 top-10 盘口
- 计算 `BI_z`
- 直接测 `BI_z` 对 `1m / 3m / 5m / 15m` 的 conditional markout

如果这一步不成立，后面 Hawkes 都不用上。

### Phase B：验证 clock layer 是否真有增益

- 在 Phase A 的基础上加入：
  - update-count burst
  - trade burst
  - 简化 Hawkes / intensity proxy
- 看 `BI only` vs `BI × high-intensity gate` 的差异

**只有当 gated 版本明显优于 ungated 版本时，才值得继续做完整 Hawkes/COE。**

这是这篇论文最应该给我们的行动项，不是“再抄一个模型名”，而是：

> **先确认 event clock 能不能把盘口 alpha 变得更可交易。**

## 14. 参考资料与来源

1. **Cestari, R. G., Barchi, F., Busetto, R., Marazzina, D., & Formentin, S. (2023 / 2025). _Hawkes-based cryptocurrency forecasting via Limit Order Book data_.**  
   - Venue: arXiv preprint; later **2025 European Control Conference (ECC)** version titled _Univariate Hawkes-based cryptocurrency forecasting via Limit Order Book data_  
   - ECC DOI: `10.23919/ECC65951.2025.11187051`  
   - arXiv DOI: `10.48550/arXiv.2312.16190`  
   - Readable URL: `https://arxiv.org/abs/2312.16190`  
   - HTML URL: `https://arxiv.org/html/2312.16190v1`  
   - PDF URL: `https://arxiv.org/pdf/2312.16190v1`  
   - Repo URL: 未见作者公开策略仓库

2. **Busetto, R., & Formentin, S. (2023). _Continuous-time modeling of financial returns based on Limit Order Book data_.**  
   - Venue: **IFAC-PapersOnLine**  
   - DOI: `10.1016/j.ifacol.2023.10.218`  
   - Readable URL: `https://doi.org/10.1016/j.ifacol.2023.10.218`  
   - Repo URL: 未见公开仓库
