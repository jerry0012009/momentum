# 别把跨所价差只做成静态 spread fade：这篇 2024 *Digital Finance* 更该先测的是「arb gap 先放大、后收敛」的短周期 raw alpha
- 时间：2026-03-30 17:58 UTC
- 类型：2024 *Digital Finance* 开放获取全文 HTML + Springer table-level 抽取
- 主题类型：raw alpha
- 基础 alpha：**同一标的的跨所/跨报价 arbitrage gap 在刚出现时不会立刻回归，反而常被同向订单流再推一段；随后市场才进入 closure 阶段，而且 USDT 市场比 USD 市场收敛更快。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/same-underlier/cross-exchange/arbitrage-gap/state-machine/continuation-then-closure/order-flow/market-impact/usdt-vs-usd/btc/eth/1m/3m/5m/15m/paper/public-data/prospective-collection/cost
- 证据类型：开放获取论文全文证据 + 表格级结果抽取 + desk 化策略迁移

## 1. 这次看了什么
主看这篇：

1. **Barucci, Emilio; Giuffra Moncayo, Giancarlo; Marazzina, Daniele (2024). _Market impact and efficiency in cryptoassets markets_. Digital Finance.**
   - DOI：`10.1007/s42521-023-00095-9`
   - Readable URL：`https://link.springer.com/article/10.1007/s42521-023-00095-9`
   - DOI URL：`https://doi.org/10.1007/s42521-023-00095-9`

先把 **base alpha** 说清楚：

> **这次不是在讲 execution overlay，也不是再讲“static arb 很难做”。真正的 raw alpha 是：跨所/跨报价价差在 shock 当下会先沿着 gap 方向继续放大，随后才进入 closure；而这个 phase transition 的时钟，在 USDT 市场和 USD 市场并不一样。**

这点和我们最近几篇 `same-underlier multiquote mean reversion` digest 不一样。之前那批更像：
- 价差偏了 → 回归；
- 重点在 spread 定义、pair 选择、multivariate 路由。

这篇真正新增的是：
- **别假设 gap 一出现就该 fade；**
- 短周期里更像一个 **两阶段状态机**：
  1. `gap birth / amplification`
  2. `delayed closure`
- 而且 **USDT 与 USD 的关闭速度不同**，这直接决定你该把持有窗放在哪个时间桶上。

所以这轮更值得 intake 的，不是“再多一个 arbitrage paper”，而是：
**same-underlier relative-value 家族里，一条可直接服务 `1m/3m/5m/15m` 的 event-path raw alpha。**

## 2. 核心结论
先给结论，不绕：
- **主题类型：raw alpha**
- **基础 alpha：arb gap 的短时继续放大 + 随后按 quote 市场异步收敛**
- **是否可独立复现：是**（前瞻采集更容易；历史全量同步回放用商业数据更省事）
- **是否可直接落地完整策略：是**

论文最值钱的不是“crypto 市场存在 inefficiency”这种大而化之结论，而是它给了三条非常 desk 化的证据：

1. **gap 不是立刻被交易 activity 消掉。**
   论文 Table 8 显示：`|OF|` 和成交量上升时，arb spread 反而更大，不是更小。

2. **signed OF 在超短周期先推着 gap 继续走。**
   Table 9 显示，`OrderFlow_t` 对 arbitrage spread 的系数在 `1m` 为正：
   - `BTC-USD`: **+0.0662**
   - `ETH-USD`: **+0.0662**
   - `BTC-USDT`: **+0.0273**
   - `ETH-USDT`: **+0.0046**

3. **然后 gap 才开始收敛，而且 USDT 收敛更快。**
   到 `5m`：
   - `BTC-USDT`: **-0.0069**
   - `ETH-USDT`: **-0.0116**
   - `BTC-USD`: **+0.0028**（还没完全翻负）
   - `ETH-USD`: **-0.0141**

翻成人话就是：
**同样是价差 shock，USDT 侧更像“1m 先顺着冲一下，5m 就该开始想 closure”；USD 侧则更拖，至少 BTC-USD 在 5m 还没完全进入稳定 closure。**

## 3. 为什么和当前项目直接相关
这轮不是在补综述，也不是在补纯解释型 microstructure 常识。它和当前 desk 直接相关，原因有三：

1. **它本身就是 raw alpha。**
   做的是 same-underlier / cross-exchange / cross-quote 的相对价值，而不是给已有 alpha 再加一层修饰。

2. **它补的是“路径形状”，不是又一个静态 spread 水平。**
   我们现在 pairs / relative-value 素材池里，很多逻辑默认 `偏离 -> 回归`。这篇提醒的是：
   **短周期最值钱的可能不是 spread level，而是 spread 的相位切换。**

3. **它对 `1m / 3m / 5m / 15m` 的映射非常自然。**
   - `1m`：shock detection / continuation leg
   - `3m`：继续持有 or 部分止盈
   - `5m`：USDT 侧 closure/fade 主窗口
   - `15m`：USD 侧更慢的 closure 检查窗

如果要回答一句“它为什么比继续补一个普通 raw alpha 更值得”：
**因为它不是替代现有 same-underlier alpha，而是在告诉我们这些 alpha 的正确时间结构：不是立即 fade，而是先 continuation 再 closure。**

## 3.5 策略拆解（必填）
- 方向属性：**same-underlier / relative-value / stat-arb / event-driven / state-machine**
- 基础 alpha：**当同一标的在多市场出现 arb gap 时，signed order flow 会先把 gap 沿原方向推大；随后 gap 才回落，且 USDT 侧比 USD 侧快**
- regime：
  - 更适合 **活跃成交、gap 真实由流量推动** 的时段；
  - 在低流动、价格冻结、或大额单边撤单主导的时段要降权。
- filter / veto：
  - 只有当 gap 超过费用门槛后才入池；
  - 需要同步看到 **gap shock + OF sign**，否则不当 continuation；
  - 若 gap 只来自单边坏点或 stale quote，直接 veto；
  - 极端 news / venue outage / API lag 时禁做。
- risk / sizing / execution overlay：
  - 按 `gap / expected_cost` 或 `gap z-score / realized vol` 缩放仓位；
  - continuation leg 与 closure leg 分开记账；
  - 需要显式核算 taker/maker、借贷/short 约束、跨 venue transfer 与库存占用。

## 4. 论文里真正可直接复现的机制
### 4.1 数据与样本
论文用的是 **Kaiko tick-by-tick** 交易数据，样本期：
- **2019-04-01 ~ 2020-10-31**
- **21 家交易所**
- 六个市场：`BTC-USDT / ETH-USDT / ETH-BTC / BTC-USD / ETH-USD / USDT-USD`
- 价格先采到 **1s**，再构造 **1m return** 和 **1m order flow**

这个口径的一个重要启发是：
**研究单位不是日线“有没有价差”，而是秒级同步交易后，分钟尺度的 gap path。**

### 4.2 论文怎么定义 arbitrage opportunity
作者沿用 Makarov & Schoar 路线，把 arbitrage 定义成：
- 同一市场/同一标的在不同交易所之间，
- 能够在同一秒买一边、卖另一边，
- 并拿到正的无库存风险利润。

利润定义不是只看 spread，而是：
- `arbitrage spread × bid/ask 可成交最小量`

也就是：
**这篇不是抽象价差论文，而是明确把“能不能成交”写进了机会定义。**

### 4.3 最值钱的地方：不是静态 spread，而是 spread 的路径
论文在第 6 节不是只问“有没有 arb opportunity”，而是继续问：

> 当 arbitrage spread 已经出现后，订单流和成交量到底是在帮你把它关掉，还是先把它推得更大？

作者做了两组关键回归：
1. `arb_spread_t ~ arb_spread_{t-1} + |OF_t|`
2. `arb_spread_t ~ arb_spread_{t-1} + OF_t`

结果很关键：
- **绝对不平衡 `|OF|` 越大，spread 往往越大，不是越小**；
- **signed OF 在 1m 上往往先放大 spread，随后才转为 closure。**

这就给了 desk 一个直接可交易的解释：
**gap birth 时别急着做教科书 fade，先判断自己是不是正处在“市场还没开始修 gap”的那几分钟里。**

## 5. 关键实证结果
### 5.1 频率与大小：USDT 机会更频繁，但 spread 更小
Table 6 的几组数字很适合直接拿来当 desk 判断基准：

- **BTC-USDT**
  - `opp_perc`: **20.84%**
  - 平均 spread: **4.73**
  - net profits（扣 0.10% taker fee 后）: **0**

- **ETH-USDT**
  - `opp_perc`: **13.14%**
  - 平均 spread: **4.64**
  - net profits: **0**

- **BTC-USD**
  - `opp_perc`: **2.04%**
  - 平均 spread: **26.05**
  - net profits: **665,464.04**

- **ETH-USD**
  - `opp_perc`: **0.47%**
  - 平均 spread: **41.75**
  - net profits: **293,533.80**

翻成人话：
- **USDT 市场更常有机会，但 spread 更薄，静态 taker-arb 很容易被费用吃掉；**
- **USD 市场机会更少，但单次 spread 更大。**

这也正好解释了为什么这篇更值得转成 **timing alpha**，而不是照抄成“看见 gap 就无脑跨所搬砖”。

### 5.2 1m 先 continuation，5m/10m 再 closure
Table 9 是整篇最值钱的表之一。

#### BTC-USD
- `1m OF_t`: **+0.0662**
- `5m OF_t`: **+0.0028**
- `10m OF_t`: **-0.0037**

#### BTC-USDT
- `1m OF_t`: **+0.0273**
- `5m OF_t`: **-0.0069**
- `10m OF_t`: **-0.0083**

#### ETH-USDT
- `1m OF_t`: **+0.0046**
- `5m OF_t`: **-0.0116**
- `10m OF_t`: **-0.0118**

#### ETH-USD
- `1m OF_t`: **+0.0662**
- `5m OF_t`: **-0.0141**
- `10m OF_t`: **-0.0158**

最重要的不是系数绝对值多大，而是**符号翻转的时间位置**：
- `USDT`：更早从 continuation 切到 closure；
- `BTC-USD`：到 `5m` 还没完全翻负，closure 更慢。

这基本就等于在告诉我们：
**同一个 gap alpha，`hold time` 不能所有市场写死一样。**

### 5.3 market activity 不是在帮你立刻修价差
论文 Table 8 还给了一个很反直觉但很有用的结果：
- 不管是 `|OF|` 还是成交量，变大时都不是让 arb spread 缩小；
- 在 crypto 里，它们更像是在 **先把 spread 撑开**。

这对短周期 desk 很重要，因为它直接否掉了一个常见直觉：
> “看见成交活跃 + gap 出现，就应该马上赌回归。”

论文的答案更接近：
> **先别急，活跃很可能是在帮 gap 完成最后一段放大。**

## 6. desk 化后的完整策略骨架
### 6.1 先定义信号，不要急着定义价差
第一版不要从“z-score 多大”开始，而要从 **event** 开始：

1. 对同一标的的多 venue / 多 quote 维护实时 mid 或可成交价格；
2. 定义 `arb_gap_t = rich_venue_px - cheap_venue_px - fees - transfer_buffer`；
3. 只有当 `arb_gap_t > hurdle` 时，才认为进入 `gap-open` 状态；
4. 同时记录当分钟 `OF_t` 或买卖成交笔方向代理。

### 6.2 状态机而不是单一 fade 规则
更像下面这个 skeleton：

- **State A: gap-open / continuation probe**
  - 条件：`arb_gap_t > hurdle` 且 `OF_t` 与当前 gap 方向一致
  - 动作：顺着 gap 方向做小仓 continuation
  - 目标窗口：`1m~3m`

- **State B: closure handoff**
  - 条件：gap 未继续放大，或 OF sign 开始衰减 / 反转
  - 动作：平 continuation；必要时切到 fade/closure
  - 目标窗口：
    - `USDT`：优先看 `3m~5m`
    - `USD`：优先看 `5m~15m`

- **State C: stale / broken quote veto**
  - 条件：gap 只出现在单 venue、盘口深度极浅、或报价长时间不动
  - 动作：不交易

### 6.3 为什么这比“静态搬砖”更像当前 desk 该测的东西
因为 paper 自己已经告诉你：
- USDT 静态 taker-arb 净利润会被 10bps 费用吃掉；
- 真正值得转移的不是 static carry，而是 **gap path timing**。

换句话说：
**raw alpha 不在“最终一定会收敛”这件事本身，而在“它什么时候还在放大、什么时候才进入 closure”这个时间错配。**

## 7. 对当前短周期（1m / 3m / 5m / 15m）的映射
### 7.1 1m
最适合做：
- gap shock detection
- OF sign 确认
- continuation leg

### 7.2 3m / 5m
最适合做：
- continuation → closure handoff
- USDT 侧的主要退出/反手窗口

### 7.3 15m
最适合做：
- USD 侧更慢的 closure 检查
- 把“还没修完的 gap”与“已经死掉的机会”区分开

### 7.4 最自然的 desk 映射
如果用当前更容易拿到的市场去测，最先该上的不是现货跨所提款搬砖，而是：
- **同标的多 venue perpetual / spot-perp proxy**
- 或 **同 venue 多 quote 的准跨市场 proxy**

因为这两类都更容易：
- 做空
- 控费
- 回测与实盘连接

## 8. 最小可复现实验（现在就能做）
### 8.1 数据源、公开性、更新频率
第一版不需要商业数据，也不必等 Kaiko：
- `Binance / OKX / Bybit` 公开 websocket 或 REST 行情
- 维护同一标的（如 `BTCUSDT`, `BTC-USDT-SWAP`, `BTCUSDT perp`）的可成交 mid / spread
- 频率：`1s` 或 `250ms~1s` 汇总到 `1m`

如果历史回放不足，可以先做：
- **前瞻采集**（最诚实）
- 或抓近期公共成交/盘口增量做短样本 quick probe

### 8.2 最小实验口径
我会建议第一轮先别做 full transfer，而是做一个极简 state-machine MVP：

1. **Universe**：`BTC` 与 `ETH` 的 2~3 个高流动 venue / quote 通道。
2. **Gap 定义**：
   - `gap_t = rich_bid - cheap_ask - round_trip_cost`
   - `gap_t > 0` 才算 event。
3. **OF 代理**：
   - 用 taker buy/sell volume 或 tick rule signed trades 估计 `OF_t`。
4. **Entry**：
   - `gap_t` 刚突破 `hurdle`
   - 且 `OF_t` 与 gap widening 方向一致。
5. **Exit A（continuation）**：
   - `1~3` 根 `1m` bar 后止盈/时间退出。
6. **Exit B（closure）**：
   - USDT 侧先测 `3m~5m fade`
   - USD 侧再测 `5m~10m` 或 `15m fade`
7. **Cost**：
   - 至少测 `4 / 8 / 12 bps` 三档；
   - 若是跨 venue spot，额外加入库存占用与转移缓冲；
   - 若是 perp-perp / spot-perp，加入 funding 与 basis 偏移。

## 9. 下一步怎么测（必须）
1. **先做 continuation-only 与 immediate-fade 的正面对照。**
   - 同一批 event、同一成本口径；
   - 比较“gap 出现就反向 fade” vs “先持 1m continuation 再退出”。

2. **按市场类型拆 hold-time。**
   - `USDT`：主测 `1m -> 5m`；
   - `USD` 或更慢市场：主测 `1m -> 10m/15m`；
   - 不要一把尺子量所有 venue。

3. **把 OF sign 纳入 event 标签。**
   - 没有 signed OF 的 gap，只能算 spread 偏离；
   - 有 signed OF 的 gap，才是这篇 paper 真正提示的 alpha 事件。

4. **先在可做空、低费用场景复刻。**
   - 现货跨所 taker-arb 在 paper 样本里 USDT 侧被费率吃掉；
   - 所以 desk 第一版更该放在 perp/perp 或 maker-dominant 场景，不要照搬 spot taker 搬砖。

5. **记录 phase transition 的稳定性。**
   - 如果 `1m continuation -> 5m closure` 的符号翻转很稳定，说明这是结构；
   - 如果翻转时点乱跳，说明你拿到的更多是 venue-specific 噪音。

## 10. 风险与保留意见
- 论文样本在 **2019-2020**，今天的 fees、venue structure、stablecoin 生态已经变了；
- paper 用 Kaiko 同步 tick 数据，历史回放质量高于普通公共 REST；
- **USDT 静态 arb 在 paper 里扣 10bps taker fee 后不赚钱**，所以别误读成“这是无脑搬砖策略”；
- 这条线最该迁移的是 **timing alpha**，不是最终 static arb PnL；
- 若拿不到稳定 signed trades / OF 代理，信号会明显降级。

## 11. 来源
1. **Barucci, E., Giuffra Moncayo, G., & Marazzina, D. (2024). _Market impact and efficiency in cryptoassets markets_. Digital Finance.**
   - Authors: Emilio Barucci; Giancarlo Giuffra Moncayo; Daniele Marazzina
   - Year: 2024
   - Venue: *Digital Finance*
   - DOI: `10.1007/s42521-023-00095-9`
   - Readable URL: `https://link.springer.com/article/10.1007/s42521-023-00095-9`
   - DOI URL: `https://doi.org/10.1007/s42521-023-00095-9`
   - Repo URL: `N/A`

2. **Makarov, I., & Schoar, A. (2020). _Trading and arbitrage in cryptocurrency markets_. Journal of Financial Economics.**
   - 作为论文 arbitrage 定义与比较基准
   - DOI: `10.1016/j.jfineco.2019.07.001`
   - Readable URL: `https://doi.org/10.1016/j.jfineco.2019.07.001`

3. **Binance / OKX / Bybit 官方公开行情 API 文档**
   - 用于前瞻采集 same-underlier 多 venue / 多 quote 的最小实验

## 12. 本地相关产物
- Digest：`research/quant_digests/2026-03-30_1758_arb-gap-amplify-then-close-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-30_1758_arb-gap-amplify-then-close-alpha.html`