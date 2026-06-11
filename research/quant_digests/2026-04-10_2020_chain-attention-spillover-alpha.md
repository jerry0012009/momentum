# 别把这篇 2026 arXiv 只读成“跨链风险传染”：对 short-cycle desk，更该先测的是「chain leader attention shock × rival-basket underperformance」这条 raw alpha

- 时间：2026-04-10 20:20 UTC
- 类型：2026 arXiv working paper（全文可读）+ Binance USDⓈ-M `5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**当某条链的原生代币在短时间内出现 attention shock（强势领涨）时，竞争链代币篮子在后续 `1h~2h` 更容易相对走弱；可先写成 `long leader / short rival basket`，也可拆成 `rival short-only`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前更像 **alt-chain sleeve**，样本主要由 `ARB/AVAX` 事件驱动，不应直接包装成全市场万能框架）
- 主题标签：raw-alpha/cross-sectional/relative-value/negative-spillover/cross-chain/attention/substitution/leader-rival/market-neutral/5m/15m/1h/2h/paper/public-data/cost/risk
- 证据类型：论文全文 + public-data portability probe

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = chain-level attention-induced substitution。**
>
> 更交易化地说，不是“链 A 涨，链 B 也跟涨”，而是：
>
> **`某条链原生代币短时强势吸走注意力/风险资金 -> rival chains 后续更容易相对跑输`**。
>
> 所以这轮把它定位成 **cross-sectional / relative-value raw alpha**，不是单纯 risk note。

## 1. 这次看了什么
这次看的是：

- **Mengzhong Ma, Te Bao, Yonggang Wen (2026)**
- **_One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets_**
- **Venue**：arXiv working paper
- **DOI**：`10.48550/arXiv.2602.23762`
- **Readable URL**：<https://arxiv.org/abs/2602.23762>
- **PDF URL**：<https://arxiv.org/pdf/2602.23762>
- **Repo URL**：未见官方复现仓库

这篇 paper 的核心不是“crypto 也有 contagion”，而是更反直觉的一句：

> **blockchain 之间经常不是同涨同跌，而是“一条链吸金，别的链让位”。**

作者用的是 **Ethereum / Solana / BSC / Arbitrum / Avalanche** 的链上资产组合与链级活动变量，样本覆盖 **2022-04-28 ~ 2025-03-31**，主频是 **half-day**。这本来偏中频，但它里面真正对我们 short-cycle desk 最有价值的旁支，不是宏观叙事，而是：

> **attention shock 可不可以改写成一个短周期的 leader-vs-rivals 相对价值 book？**

我认为答案是：**值得，而且和 4/8 那篇 generic LASSO seesaw 不是一回事。**

- `2026-04-08_1503_crosscrypto-seesaw-lasso-alpha.md` 更像 **无结构的全横截面 spillover ranker**；
- 这篇则提供了一个**更可解释的链竞争框架**：
  - 先识别哪条链在吸走注意力；
  - 再做 rival-basket 的 underperformance。

这更像一个能直接接到 desk 上的 **event-style relative-value shell**。

## 2. 论文里最值得带走的不是“负相关存在”，而是“attention shock 会放大负 spillover”
### 2.1 基础结论：跨链经常是负 spillover，不是同向扩散
作者先在链组合收益上估计 baseline 模型，发现 **negative spillover 比正向 co-movement 更常见**。

文中 Table 3 / Table 7 给出的例子包括：

- **Ethereum** 对 **Arbitrum** 的 unconditional spillover 为负：`β = -0.140`
- 控制全球市场变量后，**BSC** 仍显著受到 **Solana / Arbitrum** 负 spillover：
  - `β20 = -0.032`
  - `β30 = -0.239`
- **Avalanche** 在投资者偏向 **Arbitrum** 时，负 spillover 明显放大：`β42 = -1.368`

翻成人话：

> **不是“crypto beta 一起冒泡”，而是资金/注意力会在链之间做替代配置。**

### 2.2 真正对交易更重要的是：极端 attention shock 会把效应放大
作者在 Table 8 里把 **extreme return dummies** 当作 attention shock proxy，结论更像 desk 语言：

- **Ethereum** 投资者会在 **Solana / Arbitrum** 出现极端上涨时卖出自己链上的资产：
  - Solana upward extreme：`β13 = -0.464`
  - Arbitrum upward extreme：`β33 = -0.901`
- **BSC** 投资者在 **Solana** 极端上涨时也会卖出：`β23 = -0.152`
- **Arbitrum** 对 **Ethereum / Solana** 的极端收益也会出现同向的 attention reallocation 反应：
  - 对 Ethereum：`β13 = -0.062`，`β14 = -0.071`
  - 对 Solana：`β23 = -0.076`，`β24 = -0.077`

所以这篇 paper 真正可交易的句子不是“相关性变负了”，而是：

> **当 rival chain 出现 attention shock（尤其极端上涨）时，你手里这条链更容易被抽走资金。**

这已经很接近一个短周期 raw alpha 的 event 定义了。

## 3. 为什么它和当前项目直接相关
这轮值得做，不是因为它“很新”，而是因为它正好补我们现在最该补的素材池：

- **raw alpha**，不是纯解释/综述；
- **cross-sectional / relative value**，不是再写单币 breakout；
- **可以写成完整策略壳**，不是只有一个 regime 标签；
- **能和现有 pairs / spillover / cross-market 框架拼起来**，但本身又不等于它们。

如果一句话说它为什么比继续补一个普通 overlay 更值得：

> **因为它给的是“链竞争导致的相对回报再分配”，这本身就是一条独立的 relative-value raw alpha，不只是风险背景。**

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional / relative-value / market-neutral
- 基础 alpha：`chain leader attention shock -> rival basket underperformance`
- 首选交易壳：`long leader / short equal-weight rivals`
- 次选交易壳：`short rivals only`（当 leader continuation 不稳定或资金约束更严时）
- regime：alt-chain attention rotation、链叙事切换、事件驱动热度迁移时更可能强
- filter / veto：
  - 只有当 leader 的短窗回报达到极端分位且明显拉开 runner-up 时才做
  - 只做高流动链代币
  - funding / spread / taker-fee 不过线时 veto
- risk / sizing / execution：
  - leader 端与 rival 端做波动归一或 notional 中性
  - 固定 `1h~2h` time-stop
  - 事件过密时限制同方向重叠仓位

## 4. 我做的 desk 化 public-data probe：先问“能不能在 Binance 代币代理上站住”
### 4.1 数据与最小实验口径
我没有硬搬论文的 half-day 链上组合，而是做了一个更接近 desk 的 **public-data portability probe**：

- 数据源：Binance USDⓈ-M 公共 `fapi/v1/klines`
- 标的：`ETHUSDT / SOLUSDT / BNBUSDT / ARBUSDT / AVAXUSDT`
- 频率：`5m`
- 样本：近约 **120 天**
- 代理思路：用**原生代币 perp** 价格，代替论文里的链组合 + attention proxy
- 事件定义：
  1. 每根看过去 `12` 根（`1h`）回报
  2. 找当下 leader chain token
  3. 只有当 leader 的过去 `1h` 回报处在全样本 **top 5%**，且比 runner-up 至少高 **2 个百分点** 时，才算一次有效 shock
- 执行：信号 bar 收盘确认，下一根起持有固定 `24` 根（`2h`）
- 两个版本：
  - `short rivals only`
  - `long leader / short rivals`

结果文件：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_chain_negative_spillover_probe_summary_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_chain_negative_spillover_probe_detail_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_chain_negative_spillover_probe_by_leader_2026-04-10.csv`

### 4.2 第一眼结论：不是所有链都一样，但这条 alpha 确实能形成 tradeable spread
我在最强的一档参数上得到：

- lookback：`1h`
- hold：`2h`
- leader shock：全样本 **95% 分位以上**
- leader-runner-up gap：`>= 2%`
- 事件数：`93`

对应结果：

- **leader 本身后续 `2h` 平均继续上涨：`+51.19 bps/event`**
- **rival basket 做空端平均贡献：`+45.84 bps/event`**
- **`long leader / short rivals` 总 spread：`+97.03 bps/event`**
- **胜率：`67.7%`**

这组结果最重要的地方在于：

> **不是只有 leader continuation，rival side 自己也在掉。**

也就是说，这条东西并不只是“追涨强者”，而更像论文说的那种 **attention-induced substitution**：

> **强链吸金，弱链让位。**

### 4.3 更细一点看：当前公共代理下，样本主要由 `ARB/AVAX` 类 alt-chain shock 驱动
这轮 probe 的一个很重要的限制是：

- `93` 个有效事件里，**ARBUSDT = 51**，**AVAXUSDT = 40**，`SOLUSDT` 只有 `2` 个；
- 对应 leader-by-leader 平均 `2h` spread：
  - `ARBUSDT` shock：**`+149.85 bps/event`**
  - `AVAXUSDT` shock：**`+41.30 bps/event`**
  - `SOLUSDT` shock：样本太少，不应解读

这说明现在最诚实的 desk 读法不是“所有链都存在同样强的短周期替代效应”，而是：

> **至少在 Binance 公共代币代理里，最值得先测的是 alt-chain rivalry sleeve，尤其是 `ARB/AVAX` 这类容易发生 narrative rotation 的链。**

### 4.4 为什么这条线比 generic spillover ranker 更适合当前落地
和 4/8 那篇 generic LASSO seesaw 相比，这篇有两个更适合实盘拆解的地方：

1. **事件定义更经济解释化**
   - 不是黑箱 rank 出来谁压谁
   - 而是“哪条链在吸 attention”

2. **交易对象更像可管理的 sleeve**
   - 可以单独做 `ARB/AVAX vs ETH/BNB` 这类链竞争 book
   - 也可以挂到已有 relative-value / pairs / market-neutral 架构里

所以这轮不是重复写负 spillover，而是把它从“generic cross-coin seesaw”推进成一个**链主题、事件触发、可解释的 relative-value book**。

## 5. 这条策略怎么写成一个完整壳
### 5.1 最小可执行版本
- **universe**：先用 `ETH / SOL / BNB / ARB / AVAX`，后续再补 `OP / MATIC / SUI / APT` 等链叙事代币
- **signal**：
  - `ret_1h(leader)` 进入全样本或滚动窗口高分位
  - 且 `leader - runner_up >= delta`
- **entry**：信号 bar 收盘确认后，下一根开 `long leader / short equal-weight rivals`
- **holding**：`12` 或 `24` bars（`1h / 2h`）
- **exit**：
  - 固定 time-stop
  - 或 leader-runner gap 回落到阈值下方时提前平仓
- **sizing**：
  - leader leg 与 rival basket 做 notional-neutral 或 vol-neutral
  - 每次事件 cap gross exposure，避免 narrative cluster 连续触发时叠仓过重
- **cost**：
  - maker/taker 分开记
  - funding 若持仓跨资金费边界需单独记账

### 5.2 和 `1m / 3m / 5m / 15m` 的关系
- `1m / 3m`：更适合做事件确认后的 execution slicing、滑点约束、是否被快反噪音打掉
- `5m`：最适合做 signal 定义与主研究频率
- `15m`：更适合降换手，测试是不是能把 `2h` 壳压缩成更低摩擦版本

所以这条线最自然的第一版是：

> **`5m` 识别 leader attention shock，持有 `1h~2h` 的 relative-value spread。**

## 6. 风险与保留意见
### 6.1 论文频率和我们的频率不是一回事
论文主频是 **half-day chain portfolio**，我这里是 **`5m` token proxy**。所以这轮结论回答的是：

> **这个经济机制能不能被压缩成短周期最小实验？**

答案是能；但它还不能替代论文原口径。

### 6.2 当前公共代理的事件分布不均衡
这轮强结果明显由 `ARB/AVAX` 事件主导，说明：

- 它更像 **alt-chain competition book**，不是“ETH/BTC 万能主脉冲”；
- production 之前一定要做 leader-cluster 分桶，不然会把少数链的高 signal 当成全局规律。

### 6.3 需要认真扣成本，不要被高 event expectancy 迷惑
`+97 bps/event` 很亮眼，但这是一条**低频事件书**，不是每根都做。真正上线前要检查：

- 事件当天盘口够不够深
- 开平仓时是不是正好遇到 narrative 爆量的最差成交时点
- rival basket 的执行是否会被一两条弱流动腿拖累

### 6.4 它和已有“spillover”主题有关系，但不能混成一个锅
最容易犯的错是把它写成“又一个 spillover alpha”。

更准确的说法应该是：

- 4/8 那篇更像 **generic cross-coin spillover ranking**；
- 这篇更像 **chain competition / attention substitution event book**；
- 两者都属于 relative-value，但落地方式和解释完全不同。

## 7. 下一步怎么测
这轮最该继续做的不是再摘论文句子，而是直接上 5 组 A/B：

### A. 事件定义 A/B
- 现在用的是 `1h return top 5% + gap >= 2%`
- 下一步直接扫：
  - `30m / 1h / 2h` lookback
  - `90% / 95% / 97%` shock quantile
  - `1% / 1.5% / 2% / 3%` leader-runner gap

### B. 交易壳 A/B
- `long leader / short rivals`
- `short rivals only`
- `top leader / short closest competitors only`
- `alt-chain sleeve only` vs `all-chain basket`

### C. 执行频率 A/B
- `5m` 事件、`1h` 持有
- `5m` 事件、`2h` 持有
- `15m` 降采样版，看 post-cost 是否更稳

### D. 代理变量 A/B
- 现在只用原生代币价格
- 下一步应补：
  - on-chain activity（活跃地址、TPS、TVL 变化）
  - perp OI / funding 作为 attention crowding proxy
  - social/news launch timestamps 作为 narrative shock proxy

### E. 生产可行性 A/B
- 先只跑 `ARB/AVAX` 主导的 alt-chain sleeve
- 再测试是否值得扩到 `OP / MATIC / SUI / APT`
- 同时做 cost bucket：大事件 / 普通事件 / 爆量事件 的成交质量对比

## 8. 一句话结论
这篇 2026 arXiv 最值得 desk 先拿来做的，不是“crypto 跨链也会传染”这句大话，而是：

> **当某条链的原生代币在短窗内强势吸走注意力时，竞争链代币篮子在后续 `1h~2h` 确实会更容易相对走弱；这条 `leader-vs-rivals` relative-value raw alpha，已经能用 Binance 公共 `5m` 数据做出最小可复现事件书。**

## 9. 来源
- Mengzhong Ma, Te Bao, Yonggang Wen. (2026). *One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets*. arXiv working paper.
- DOI: `10.48550/arXiv.2602.23762`
- Readable URL: <https://arxiv.org/abs/2602.23762>
- PDF URL: <https://arxiv.org/pdf/2602.23762>
- Repo URL: 未见官方复现仓库
- 本地文本快照：`/root/clawd/jerry/momentum/tmp_cross_chain_negative_spillovers_2026.txt`
- 本地 public probe 结果：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_chain_negative_spillover_probe_summary_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_chain_negative_spillover_probe_detail_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_chain_negative_spillover_probe_by_leader_2026-04-10.csv`
