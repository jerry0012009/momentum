# 别把 tight spread 直接当成低风险成交：对 short-cycle desk，更该先补「order-book variation × bid-depth」这层 liquidity-timing overlay
- 时间：2026-04-05 20:03 UTC
- 类型：2025 *Journal of Risk and Financial Management* 开放获取全文（MDPI PDF）+ Crossref / OpenAlex 元数据 + 公开 L2 API 可得性确认
- 主题类型：overlay
- 基础 alpha：pairs / carry / cross-venue gap / OFI directional 等所有依赖低冲击成交的短周期 alpha
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：overlay/execution/liquidity/order-book/variation/spread/imbalance/bid-depth/liquidity-timing/shared-overlay/pairs/carry/cross-venue/microstructure/binance/okx/1m/3m/5m/15m/paper/open-access/public-data/cost/risk
- 证据类型：论文全文 + 元数据 + 公开 API 可得性确认

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha 不是单独一条新 raw alpha；它服务的是所有需要穿过 order book 的短周期 alpha。**
> 所以这轮应把它归类成 **execution / risk overlay**，而不是硬伪装成一条新的主信号。

## 1. 这次看了什么
这轮主看的是：

1. **Angerer, M., Gramlich, M., & Hanke, M. (2025). _Order Book Liquidity on Crypto Exchanges_. Journal of Risk and Financial Management, 18(3), 124.**
   - DOI：`10.3390/jrfm18030124`
   - Readable URL：`https://doi.org/10.3390/jrfm18030124`
   - PDF：`https://www.mdpi.com/1911-8074/18/3/124/pdf?version=1740661051`
   - Repo URL：无
2. Crossref / OpenAlex 元数据
3. 公开 L2 数据可得性确认：
   - Binance Spot：`https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=20`
   - OKX Books：`https://www.okx.com/api/v5/market/books?instId=BTC-USDT&sz=20`
   - Binance Futures REST 这边当前 IP 已触发限频提示，更适合用 websocket 连续采样，而不是高频 REST 轮询

这轮虽然不是继续补 raw alpha，但我仍然觉得值得写，原因很直接：

- 过去几天 raw alpha intake 已经很密，尤其是 pairs / carry / order-book / microstructure 族；
- 这些东西最后能不能从 gross edge 变成 net edge，往往不是死在 signal，而是死在 **什么时候进、什么时候别进、当时 book 薄不薄**；
- 这篇 paper 给的最值钱部分，不是“哪个交易所更好”，而是它定义了一个很适合移植到 `1m / 3m / 5m / 15m` 的 **order-book variation** 概念：
  **同样是 tight spread，book 的“会不会突然被打穿”是另一件事。**

## 2. 一句话核心结论 + 它怎么证明
### 一句话核心结论
**对 short-cycle desk，quoted spread 不能单独当执行条件；更该把 `variation（book 跳层风险） + bid-side depth / imbalance` 一起纳入 entry veto / sizing / maker quote policy。**

### 一句话它怎么证明
作者用 2019 年四家 CEX 的全簿或 top-20 order book 数据，构造了一个新的 **order book variation** 指标：
- 每隔 `5min` 取一次快照；
- 看当前 mid-price 相对上一个快照，在 bid / ask 两侧分别最接近落到第几档；
- 取两侧里更坏的那个 level rank，作为本次 jump 的“跳层数”；
- 再在日内聚合成 **平均 variation** 和 **最大 variation**。

翻成人话就是：

> **不是只看当下 spread 窄不窄，而是看“这本书下一下会不会突然跳很多档”。**

## 3. 论文里最值钱的 5 个点
### 3.1 数据口径足够硬，不是几只币的小样本故事
论文数据来自 **Binance / Kraken / Huobi / OKEx** 四家交易所，样本期是 **2019-01-01 到 2019-09-30（273 天）**。

作者最终保留：
- **1086 个 trading pairs**
- **254,728 个 pair-day observations**
- 每天最多 **288 个 `5min` snapshots**
- 每次看 **双边最多 20 档 order book**

这比“抓一个月 BTCUSDT top-of-book 然后开始讲 microstructure”要扎实得多。

### 3.2 最值得 desk 拿走的不是 spread，而是 `variation risk`
论文最有用的结果之一，是把 liquidity 重新拆成两层：

1. **quoted / VWAP spread**：你现在看得到的静态成本
2. **order-book variation**：你下单那一刻，book 会不会突然跳层、把你打到更差价位

这对 short-cycle 特别关键，因为很多策略在回测里默认：
- “当下 spread 很窄 = 可放心成交”

但 paper 的意思其实更接近：
- **spread 只是其中一维**；
- 真正影响成交后 PnL 的，还包括 **book 稳不稳定、bid side 有没有托住、你是不是正好踩在 liquidity 被 timing 的那一刻。**

### 3.3 variation 的横截面差异很大，说明“什么时候下”确实重要
按 base type 分组，作者报告的 variation 很不一样：

- **OKEx cryptocurrency**：
  - mean variation = **1.48**
  - max variation = **8.04**
- **Huobi stablecoin**：
  - mean variation = **6.86**
  - max variation = **39.4**

这不是一点点噪声差异，而是非常大的 execution regime 差异。

翻成人话：

> **有些 book 平时只跳 1~2 档，有些 book 日内最差时能跳接近 40 档。**
>
> 如果你的策略要 taker 进出、要 stop、要 hedge，这种差异足够把“同一信号”做成两条完全不同的净值曲线。

### 3.4 最反直觉但最有用的点：tight spread 不一定等于低冲击风险
论文发现，variation 和 spread / imbalance 的关系并不简单到“越紧越安全”：

- variation 与 spread 显著负相关；
- variation 与绝对 imbalance（ANOBI）也显著负相关；
- fixed-effects 回归里，**L5 VWAP spread 每增加 1%，variation 大约下降 `0.53% ~ 0.41%`**；
- **L10 ANOBI 每增加 1%，variation 的变化大约在 `-0.08% ~ +0.02%` 区间**，方向更弱，但 interaction term 显著。

这背后的 desk 化解释不是“spread 越宽越好”，而是：

> **真实交易会 timing。**
>
> 当 liquidity 看起来足够好、足够值得打的时候，反而更容易出现 market order 去吃 book，导致你看到的是 tight spread，但同时也更可能遇到 book 快速变化。

所以对 taker 策略来说，**“spread 变窄就冲”是危险的**。更稳的做法是：
- 既看 spread；
- 也看 predicted variation / recent max variation；
- 再看 bid-side depth / imbalance 是否在支撑你想做的方向。

### 3.5 bid side 比 ask side 更重要，尤其对下跌和止损很关键
论文里一个很适合 desk 落地的结论是：

- **更高的 bid-side depth 更能降低 variation risk**；
- 当 order book 更偏向 negative imbalance / bid-side 不够厚时，variation 风险更容易上升；
- 作者甚至明确写到：投资者更愿意支付更高 spread 去卖出，而不是去买入新仓。

这件事对我们有两个直接含义：

1. **做多 alpha 的 stop / exit 风险，不能只盯 ask。更该盯 bid 有没有突然塌。**
2. **所有依赖被动止盈、主动止损、动态对冲的策略，都该把 bid-side thinning 当成更高优先级警报。**

## 4. 这轮最值得移植的，不是交易所比较，而是一个共享 overlay
如果只从“哪家交易所更有流动性”来读，这篇东西其实会很快失效，因为论文样本是 2019。

但如果把它读成一个 **shared liquidity-timing overlay**，价值就大很多。

它最适合服务至少 4 类已有 raw alpha：

1. **pairs / stat-arb / cross-venue gap mean reversion**
2. **funding / basis / carry**（需要 roll、换腿、临近 funding 边界再平衡）
3. **order-book / OFI directional**（spread 紧但未必 safe）
4. **maker / market-making**（何时缩 size、何时 widen quote、何时干脆撤）

所以这轮不是继续堆一条新 raw alpha，而是给已经很多的 raw alpha 池补一层更可复用的执行框架。

## 4.5 策略拆解（必填）
- 方向属性：shared execution / liquidity-timing overlay
- 服务对象：pairs、carry、cross-venue、maker、microstructure directional
- overlay 本体：`spread + variation + bid-side depth/imbalance -> entry veto / size scalar / execution mode`
- trade-on：
  - 最近一段 `variation` 不高；
  - bid-side depth 没有明显塌陷；
  - 当前策略预期 edge 能覆盖显性成本 + 预估冲击成本；
- veto：
  - recent / predicted max variation 进入高分位；
  - bid-side depth 快速变薄；
  - ANOBI / NOBI 提示 book 结构对当前方向不友好；
  - 需要 taker 进出，但 execution mode 仍假设“tight spread = safe”；
- sizing / risk：
  - variation 分位越高，size 越小；
  - bid-side depth 越差，long alpha exit 相关仓位越应主动降；
  - maker 策略在 variation 高位时 widening / reduce quote count / pull quote

## 5. 跟 `1m / 3m / 5m / 15m` 怎么接
这篇 paper 本身是 `5min` order-book snapshots，但对我们不是问题，反而正适合往下或往上聚合。

### 对 `1m / 3m / 5m / 15m` 的 desk 化映射
- **`1m`**：把 websocket L2 snapshots（如 `250ms/500ms/1s`）聚合成 bar 内 `avg variation / max variation`
- **`3m`**：更适合 pairs / basis / OFI alpha 的 execution veto
- **`5m`**：与论文最接近，优先做第一版 replication
- **`15m`**：更像上层 admission / sizing gate，而不是逐笔 execution gate

### 公开数据是否拿得到
能拿到，而且足够快做最小实验：
- Binance Spot `depth` REST / websocket：公开可得
- OKX Books REST / websocket：公开可得
- Binance Futures 这边 REST 容易碰限频，更建议直接上 websocket

也就是说，这条 overlay **不是必须买私有 L2 数据** 才能先做第一轮实验。

## 6. 给 desk 的最小实验版本
第一版别做复杂模型，先做一个 rule-based liquidity-timing governor：

1. 连续收 `top20` book snapshots
2. 对每个 `1m / 3m / 5m / 15m` bar 计算：
   - `L1 relative spread`
   - `L5 VWAP relative spread`
   - `L10 ANOBI`
   - `avg variation`
   - `max variation`
3. 在现有 raw alpha 外再套一层规则：
   - **taker alpha**：`max variation` 过高则不进；bid-side 深度不足则 size-down
   - **maker alpha**：variation 高位时 widen quotes / reduce inventory skew / 降撤单频率
   - **pairs/carry**：需要双腿同时成交时，只在两腿都通过 liquidity veto 时才允许入场
4. 对比 baseline 与 overlay：
   - fill quality
   - slippage
   - adverse selection
   - stop-out 后的二次滑点
   - net pnl / turnover-adjusted sharpe

## 7. 下一步怎么测（最重要）
### 7.1 先测哪几条现有策略
优先把这层 overlay 接到 3 类现有策略上做 A/B：

1. `2026-04-05_1606_twotier-funding-rate-crossvenue-arb-alpha.md`
2. `2026-04-05_1919_winneronly-losershort-veto-xs-alpha.md`（执行层，只测入场质量，不改主信号）
3. `2026-04-04_1016_bybit-laddered-inventory-skew-maker-alpha.md`

### 7.2 最小实验口径
- **数据源**：Binance Spot / OKX Books 公共 L2；如果做合约则优先 websocket
- **标的**：先做 `BTCUSDT / ETHUSDT / SOLUSDT`，再扩到 pairs / dual-leg
- **采样**：`1s` snapshots，聚合到 `1m / 3m / 5m / 15m`
- **特征**：
  - `L1 spread`
  - `L5 VWAP spread`
  - `L10 ANOBI`
  - `avg variation`
  - `max variation`
  - bid-side depth slope
- **标签 / 目标**：
  - 下一个 bar 的 realized slippage
  - stop 执行后的 extra impact
  - maker fill 后 `30s / 60s / 180s` adverse selection
- **比较项**：
  - gross pnl
  - net pnl
  - slippage per trade
  - turnover
  - stop-out loss amplification
  - quote-to-fill ratio（maker）

### 7.3 先看什么结果
第一轮先别追求“收益大增”，只看 3 件事：

1. **有没有明显降低最差 5% 交易的滑点尾部；**
2. **在不显著减少交易数的前提下，net pnl 有没有改善；**
3. **bid-side thinning 能不能比 spread 自己更早预警坏成交。**

## 8. 先别自嗨的地方
1. **论文样本是 2019。** 不能把“哪家交易所更好”直接照搬到 2026。
2. **作者的 book variation 是跨日聚合后研究，不是现成可部署信号。** 我们要做的是把它 desk 化成实时 overlay。
3. **spread 和 variation 的负相关，不能被误读成“spread 越宽越该下单”。** 它说明的是 liquidity timing / endogenous trading，不是鼓励去吃宽价差。
4. **如果只拿 REST 低频抓书，可能抓不到真正的 micro-burst。** 想认真做 `1m`，最好还是 websocket。

## 9. 这轮最值得记住的 desk 化结论
如果只记一句：

> **tight spread 不是低风险成交的同义词。对 short-cycle alpha，更该把“book 会不会突然跳层”与“bid side 有没有托住”一起纳入执行决策。**

## 10. 来源
1. **Angerer, Martin; Gramlich, Marius; Hanke, Michael (2025). _Order Book Liquidity on Crypto Exchanges_. Journal of Risk and Financial Management, 18(3), 124.**
   - DOI：`10.3390/jrfm18030124`
   - Readable URL：`https://doi.org/10.3390/jrfm18030124`
   - PDF：`https://www.mdpi.com/1911-8074/18/3/124/pdf?version=1740661051`
   - Repo URL：无
2. **Crossref metadata**
   - `https://api.crossref.org/works/10.3390/jrfm18030124`
3. **OpenAlex metadata**
   - `https://api.openalex.org/works?search=Order%20Book%20Liquidity%20on%20Crypto%20Exchanges`
4. **公开 order-book API 可得性确认（2026-04-05 UTC）**
   - Binance Spot depth：`https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=20`
   - OKX Books：`https://www.okx.com/api/v5/market/books?instId=BTC-USDT&sz=20`
   - 备注：Binance Futures 高频 REST 在当前 IP 上出现限频封禁提示，live 采集应优先 websocket