# 别把 24h 涨跌幅只当 UI：`Pure Momentum` 更该先测的是「rolling 24h stale-return roll-off」same-clock raw alpha，但 2025Q4~2026Q1 Coinbase/Binance 迁移几乎不剩净 edge
- 时间：2026-03-26 12:40 UTC
- 类型：2022 SSRN working paper（作者页 2025 仍在更新）+ Coinbase 公共 API 原论文数据口径 + Coinbase/Binance 公共 `15m/1h` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**24 小时滚动展示窗里即将被“挤出”的 stale return，会机械改变屏幕上的过去 24h 涨跌幅；若交易者会对这个“显示变化”而不是新信息本身作反应，那么 `t` 时刻的 same-clock 后续回报，会对 `t-24h` 的同栏 return 产生系统响应。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/event-clock/attention/rolling-window/stale-return/24h-rolloff/time-series/cross-sectional/coinbase/binance/15m/1h/5m/3m/crypto/paper/external-data/cost
- 证据类型：论文全文证据 + 当前公开市场最小迁移快检

## 1. 这次看了什么
先回答 base alpha：**这不是一般的“过去涨了所以继续涨/跌了所以继续跌”，而是“rolling 24h 涨跌幅展示窗在滚动时，会把 24 小时前那一小段 return 挤出参考窗；如果用户盯着 24h 排行榜/涨跌幅面板交易，就可能对这个展示层变化本身做反应”。**

主材料是 **Fracassi & Kogan, _Pure Momentum in Cryptocurrency Markets_**。这篇东西对当前 desk 真正有价值的，不是“又一个抽象行为金融故事”，而是它给了一个**极便宜、极明确、天然贴着 `15m/1h` 事件时钟**的 raw alpha 原型：

- `1h` 版：看 **24 小时前同一小时** 的 return；
- `15m` 版：看 **24 小时前同一 15m 栏** 的 return；
- 可以做 **单资产 same-clock time-series**，也可以做 **多资产横截面 rich-vs-cheap stale-return**。

这和我们前面做过的 `intraday clock polarity` shared gate 不同：**那条更像“先判当前时段偏 momentum 还是 reversal” 的 filter；这条是直接把“滚动展示窗的 stale-return roll-off”当成 alpha 本体。**

## 2. 核心结论
### 2.1 论文真正说了什么
- 原文样本来自 **Coinbase 公共 API**，覆盖 **138** 个币、**2015-01-01 到 2021-12-31**，同时看 **1h** 与 **15m** K 线。
- 论文核心发现很干净：
  - **当前 `1h` 回报** 与 **恰好 `24h` 前的 `1h` 回报** 存在显著负关系；
  - 这种效应在 **24h 标记之前并不出现**，并且**在之后 4 小时内逐步衰减**；
  - **`15m` 回报** 也会对 **恰好 `24h` 前的 `15m` 回报** 强响应，而不是对“差一点到 24h”的 return 响应；
  - 效应在 **更高流动性币种里更明显**；
  - 论文给出的横截面做法是：**long 24-lagged return 最低的两只、short 最高的两只**，得到 **年化收益 538% / Sharpe 3.52（交易成本前）**；
  - 但作者也明确写了：**考虑典型费用与冲击成本后，不再盈利。**

翻成人话：**这条线的 edge 不是来自“基本面有新消息”，而是来自“屏幕上过去 24h 的显示值，在没有新消息时也会因为滚动窗切换而变化，而部分交易者会追着这个变化下单”。**

### 2.2 这条 alpha 对短周期 desk 的真正价值
它值钱的地方有 3 个：
1. **raw alpha 非常清楚。** 不是 filter、不是 regime、不是解释层；
2. **天然是 `15m/1h` 事件时钟信号。** 不需要等日频收盘，也不是低频宏观变量硬塞进短周期；
3. **很容易快速证伪。** 只要当前市场/当前 venue 不再对 rolling 24h 面板过敏，这条 edge 会很快在公开数据里显形为“几乎没了”。

也正因为如此，它很适合放进素材池：**即使当前 transfer 不好，它也是一条值得低成本持续巡检的 short-cycle raw alpha 家族。**

## 3. 为什么和当前项目直接相关
结合 `LEARNING_TRACK`、`FACTOR_BACKLOG` 和最近两天 intake 节奏，当前 desk 已经连续补了不少：
- pairs / stat-arb / relative value
- basis / funding / carry
- microstructure lead-lag
- short-term reversal

这轮再补一条 **event-clock / display-driven raw alpha**，边际价值是成立的：
- 它不是又回到 breakout / retest 内循环；
- 它也不是把外部低频变量硬装成 `5m` 主信号；
- 它直接扩充的是 **raw alpha 素材池**，而且是一条**可以 very-fast falsification 的 raw alpha**。

更直白地说：**如果这条线在今天的 Coinbase/Binance 上已经死了，我们应该尽快知道；如果它只在某些 retail-exposed venue / symbol bucket / maker 成本口袋里还活着，也应该尽快把“活在哪”定位出来。**

## 3.5 策略拆解（必填）
- 方向属性：既可做 **single-asset time-series**，也可做 **cross-sectional long-short**；本质是 **same-clock event alpha**
- 基础 alpha：
  - `15m`：`signal_i,t = - r_i,t-96`
  - `1h`：`signal_i,t = - r_i,t-24`
  - 含义：`24h` 前同栏若是大正收益，则它即将滚出 rolling 24h 参考窗，显示层会面临“被动下修”；反之亦然
- 横截面读法：
  - 每个 bar 对 universe 按 `signal_i,t` 排序
  - long 最低 stale-return 组，short 最高 stale-return 组
- time-series 读法：
  - 单币若 `signal_i,t` 足够大，则顺着 `signal` 方向开仓 1 bar
- entry：
  - 默认 `next-bar open`
  - 先只做 `|r_{t-96}|` / `|r_{t-24}|` 处于滚动分位上尾的极端样本，避免全天 bar-bar 硬打
- exit：
  - 基线先看 **持有 1 bar**；
  - 论文提示效应在 `1h` 口径下 **4 小时内衰减**，所以扩展版可测 `2~4` bar decay exit
- sizing：
  - time-series：单币固定风险 + 近 24h realized vol 逆波缩放
  - cross-section：equal-risk 或 inverse-vol，净敞口归一到 1.0 gross
- risk：
  - 若做横截面，优先市场中性；
  - 若做 time-series，需对 BTC beta 暴露设上限
- cost：
  - 这条线的第一性约束不是方向，而是 **费用/冲击**；
  - 没有 **maker / rebate / 低冲击** 优势时，不应默认它能穿过常规 perp taker 成本

## 4. 这轮最小快检：当前市场 transfer 到底还剩多少
为了不只复述论文，我做了 3 个当前口径的最小检查：

### 4.1 Binance Futures `15m`（近 120d，`BTC/ETH/SOL/XRP/DOGE/BNB`）
产物目录：`reports/artifacts/quant_digests/pure_momentum_clock_20260326_1211/`

- pooled `15m` own-signal 相关：**`corr ≈ +0.0052` / `beta ≈ +0.0052`**
- 横截面 `long lowest lag24 / short highest lag24`：
  - **gross ≈ +0.167 bps/bar**
  - **annualized gross Sharpe ≈ 1.88**
  - 但 **6 bps round-trip 后 ≈ -5.83 bps/bar**
- `1h` 稀疏版（只看 signal spread 最高 20% 时段）也只到：
  - **gross ≈ +1.41 bps/bar**
  - **6 bps round-trip 后仍为负**

### 4.2 Binance Spot `15m`（同样近 120d、同类大币）
产物目录：`reports/artifacts/quant_digests/pure_momentum_clock_20260326_1211_spot/`

- pooled `15m` own-signal 相关：**`corr ≈ +0.0053` / `beta ≈ +0.0053`**
- 横截面版本：
  - **gross ≈ +0.163 bps/bar**
  - **6 bps round-trip 后 ≈ -5.84 bps/bar**

### 4.3 Coinbase Spot `15m`（更贴近原论文 venue，近 120d，`BTC/ETH/SOL/XRP/DOGE/ADA`）
产物目录：`reports/artifacts/quant_digests/pure_momentum_clock_20260326_1211_coinbase/`

- pooled `15m` own-signal 相关：**`corr ≈ +0.0046` / `beta ≈ +0.0046`**
- 横截面版本：
  - **gross ≈ +0.070 bps/bar**
  - **annualized gross Sharpe ≈ 0.74**
  - **6 bps round-trip 后 ≈ -5.93 bps/bar**

### 4.4 这轮快检的诚实读法
- **原论文是强 raw alpha 证据。**
- 但在我用当前 **2025Q4~2026Q1** 的 Coinbase/Binance 公开数据做的最小 transfer 里：
  1. own-signal 并没有重现论文叙事里的清晰负相关；
  2. 横截面版本即使 gross 为正，也只剩 **`0.07~0.17 bps/bar`** 这种量级；
  3. 一旦扣到常规短周期成本，**几乎立刻死掉**。

所以这轮更诚实的结论不是“论文错了”，而是：**这条 alpha 至少在当前主流可得样本上，已经不再是可以直接搬进短周期现货/永续的即插即用骨架。**

## 5. desk 化后的判断
### 5.1 该怎么给它定性
- **主题类型：raw alpha** —— 不是 filter，也不是 overlay
- **基础 alpha：rolling 24h stale-return roll-off 导致的 same-clock 显示冲击**
- **是否可独立复现：是** —— 数据公开、公式很短、事件时钟清楚
- **是否可直接落地完整策略：否** —— 当前 transfer 下成本后基本不活

### 5.2 它还值不值得留在研究池
我认为 **值得，但要降级成“持续巡检的 raw alpha 家族”，而不是当前的优先 live-candidate**。

最合理的 desk 读法是：
- **不要把它当 always-on bar-by-bar 信号**；
- 应改成 **event-triggered / extreme-bucket / retail-exposed-venue-only** 的研究对象；
- 更像是在问：**“哪些 venue / 哪类币 / 哪种 UI 曝光环境下，交易者还会对 rolling 24h 显示值过敏？”**

## 6. 可复刻的下一步怎么测
这里必须继续往下拆，而不是停在“paper 不错但现在不行”。

### 6.1 第一优先：把 signal 从“裸 `r_{t-24h}`”改成“展示层真实冲击”
当前最小快检只是用了简化版：`signal = -lag24_return`。更贴论文机制的做法应是直接构造：
- **若当前价格不变，仅因参考窗滚动而导致的 `reported_24h_return` 变化量**；
- 或直接用：
  - `display_delta_hat_t = reported_24h_return_if_price_flat_next_bar - reported_24h_return_now`

这比裸 lag return 更接近交易者实际看到的屏幕变化。

### 6.2 第二优先：只在 retail-exposed venue / symbol bucket 做
论文样本来自 Coinbase。下一轮应优先：
- **Coinbase spot top movers / gainers/losers UI 曝光较强币种**
- 再和 Binance spot / perp 做 A/B

如果这条线真是 **attention-driven**，它更可能先活在“用户会盯 24h 榜单”的地方，而不是专业 perp taker 最拥挤的 venue。

### 6.3 第三优先：改成极端样本 + maker 成本口袋
先别全天打满。优先测：
- 仅做 `|display_delta_hat|` 的 top `5% / 10%` 事件；
- 只在高流动性、低冲击币上做；
- maker / rebate / 低滑点口径下重新看 break-even

### 6.4 第四优先：从纯 time-series 改成“same-clock 相对值”
可测一个更 desk 化的横截面版本：
- `score_i,t = -(r_i,t-24h - median_j r_j,t-24h)`
- 也就是：**做“24h 前同栏最容易被 UI 下修/上修的那批币”的相对值篮子**

这可能比单币 time-series 更接近短周期市场中性的实际可用形态。

## 7. 风险与保留意见
- 论文的经济机制是 **attention / salience**，因此**venue 依赖性很可能很强**；
- 这类 alpha 的半衰期可能非常短，被更专业的做市/统计套利玩家吃掉后，会迅速退化；
- 当前我做的是 **最小 transfer check**，不是对原论文的 clean replication；
- 因此本轮结论应理解成：
  - **原始 paper alpha：成立，值得收录；**
  - **当前 desk 直接搬运：默认不成立；**
  - **后续只值得在“展示冲击更真实 + venue 更贴机制 + 成本更低”的 pocket 里继续追。**

## 8. 来源
1. **Fracassi, C., & Kogan, S. (2022). _Pure Momentum in Cryptocurrency Markets_. SSRN Electronic Journal.**
   - DOI: `10.2139/ssrn.4138685`
   - Readable URL: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4138685`
   - Mirror PDF: `https://assets.ctfassets.net/c5bd0wqjc7v0/4RzmvaUG64ixNPXWuZGXbo/7115cc7bef963d2ff5abbacf879f5b1e/SSRN-id4138685.pdf`
   - Author page: `https://cesare-fracassi.github.io/publication/decentralized-crypto`
   - Repo URL: `N/A`
2. **Coinbase Exchange API docs / public candles endpoint**
   - Readable URL: `https://api.exchange.coinbase.com/products/BTC-USD/candles`
3. **Binance public kline endpoints**
   - Spot: `https://api.binance.com/api/v3/klines`
   - Perpetual: `https://fapi.binance.com/fapi/v1/continuousKlines`

## 9. 本地相关产物
- Digest：`research/quant_digests/2026-03-26_1240_pure-momentum-24h-rolloff-alpha.md`
- Artifact（Binance perp）：`reports/artifacts/quant_digests/pure_momentum_clock_20260326_1211/summary.json`
- Artifact（Binance spot）：`reports/artifacts/quant_digests/pure_momentum_clock_20260326_1211_spot/summary.json`
- Artifact（Coinbase spot）：`reports/artifacts/quant_digests/pure_momentum_clock_20260326_1211_coinbase/summary.json`
