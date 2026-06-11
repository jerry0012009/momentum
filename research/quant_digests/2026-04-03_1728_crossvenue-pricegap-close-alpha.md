# Crépellière, Pelster, Zeisberger（*Journal of Financial Markets* 2023）+ Binance/Bybit 公共 `1m` 快检：别把跨所价差回归只当“老套利故事”，对 short-cycle desk 更该先测的是「alt perp venue-dislocation × maker-first spread-close shell」
- 时间：2026-04-03 17:28 UTC
- 类型：论文 + ScienceDirect 可读摘要/Highlights + Binance/Bybit 公共 `1m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**同一标的在不同交易所的瞬时错价会向 law-of-one-price 回归**；交易上就是 `long cheap venue / short rich venue` 做 spread close，而不是赌单边方向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但**对执行与费率极其敏感**
- 主题标签：raw-alpha / relative-value / stat-arb / cross-venue / same-underlier / law-of-one-price / spread-close / maker-first / perp-perp / binance / bybit / 1m / 3m / 5m / 15m / paper / public-data / cost / execution / risk
- 证据类型：JFM 2023 摘要与 Highlights + 本地 public-data `1m` 便携性快检

**先回答 base alpha：这篇东西的 base alpha 很清楚，不是“市场更有效”这种空话，而是 `跨交易所同标的价差回归`。如果价差不回归，就没有 alpha；如果会回归，剩下比拼的是你能不能用足够便宜、足够快、足够稳的执行把它吃到。**

## 1) 这次为什么写它
当前 digest 池里已经有：
- same-underlier 多报价 bucket；
- Coinbase premium lead-lag；
- 多种 pairs / coint / residual stat-arb；
- funding / basis / carry。

但**“最朴素的跨所同标的价差回归”本身**，反而还没被单独写成一篇 short-cycle digest。

这条线值得补，原因很直接：
1. 它是 **raw alpha**，不是纯 filter；
2. 它天然属于 `1m / 3m / 5m / 15m` desk 可测试的 relative-value / stat-arb；
3. 它能直接给我们一个很重要的现实判断：
   - 这条 alpha 在 majors 上是不是已经死得差不多了？
   - 如果没完全死，残余 alpha 更集中在 **哪类币 / 哪类 venue / 哪种执行模式**？

换句话说，这篇不是为了证明“套利很厉害”，恰恰是为了更诚实地判断：**跨所 spread-close 现在到底还剩多少可交易边角料。**

## 2) 论文里最值得 desk 记住的，不是“存在套利”，而是“2018 之后这条线迅速变成执行生意”
主材料：
- **Tommy Crépellière, Matthias Pelster, Stefan Zeisberger (2023)**, *Arbitrage in the market for cryptocurrencies*, **Journal of Financial Markets**, Vol. 64, Article 100817.
- DOI: `10.1016/j.finmar.2023.100817`
- Readable URL: `https://www.sciencedirect.com/science/article/pii/S1386418123000150?via%3Dihub`
- DOI URL: `https://doi.org/10.1016/j.finmar.2023.100817`

ScienceDirect 页面里的 Highlights/Abstract 已经把最关键的结论说透了：
- **Arbitrage opportunities in cryptocurrency markets existed.**
- **Their magnitude decreased greatly from April 2018 onward.**
- **It is hardly possible to exploit existing price differences since then.**
- 作者给出的解释里，最重要的是：
  - **informed trading** 增加；
  - **trading fees** 仍然重要；
  - **legal restrictions** 也是约束。

翻成人话就是：

> 跨所价差不是没有，但它越来越不像“看见就捡”的地上钱，更像一门 execution / fee tier / inventory / venue risk 的苦活。

这对我们 desk 的意义非常大，因为它把这条线的定位讲清楚了：
- **alpha 本体** 仍然存在：`spread close`
- 但能不能变成净收益，不取决于你会不会写 z-score，而取决于：
  - 你做的是不是还保留 dislocation 的那一小撮币；
  - 你是不是被 taker fee 全吃掉；
  - 你是不是有足够快的 maker-first / inventory-aware 执行壳。

## 3) 对 short-cycle desk 的正确翻译
### 3.1 这不是“方向预测”，而是最标准的 relative-value raw alpha
策略骨架非常朴素：
- 标的：同一 underlier 的两家交易所 perp（例如 Binance vs Bybit）
- 信号：`spread_t = ln(price_A / price_B)` 或标准化后的 z-score
- 入场：当 spread 偏离 rolling mean 足够多时，**short rich venue / long cheap venue**
- 出场：spread 回到均值附近、穿零、或时间到期

### 3.2 它和我们已经写过的其他题材有什么不同
- 和 **Coinbase premium impulse** 不同：那条主要是 **lead-lag / price discovery**；这条是 **同标的跨 venue 同步回归**。
- 和 **same-underlier 多报价 bucket** 不同：那条更像 **cross-quote / multi-quote 结构差**；这条是 **venue-to-venue law-of-one-price**。
- 和普通 **pairs trading** 不同：这里两条腿不是“相似资产”，而是**同一资产**，所以 base alpha 更干净，但可交易利润更薄。

所以这条线的研究重点，不该是“再发明一个 fancy pair selector”，而是：
**先判断哪些币、哪些 venue 组合，今天还值得给它 execution 资源。**

## 4) 本地 public-data `1m` 最小快检：2026 年的跨所 spread 还剩多少？
我用公开 REST 接口做了一个最小 portability probe：
- 数据源：
  - Binance USDⓈ-M Futures `fapi/v1/klines`
  - Bybit `v5/market/kline`
- 公开性：公开可抓，无需私钥
- 更新频率：`1m`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT` 线性永续
- 样本：最近约 `3d`，共 `4321` 个对齐分钟/bar
- 价差定义：`spread = ln(close_binance / close_bybit)`
- 触发壳：
  - `240m` rolling z-score
  - `|z| >= 2`
  - 且绝对价差 `>= 3bps`
  - 下一 bar 入场
  - 回到 `|z| < 0.2` 或最多持有 `15m` 出场
- 说明：这是**收盘价 proxy**，不是盘口 mid/bid/ask；因此只能当最小快检，不是 production 回测

结果文件：
- `reports/artifacts/quant_digests/2026-04-03_cross-exchange-binance-bybit-arb-sanity.csv`

### 4.1 核心数字
| Symbol | 对齐分钟数 | median \|spread\| (bps) | p95 \|spread\| (bps) | share >= 3bps | trades | mean gross pnl / trade (bps) | win rate | median hold (min) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BTCUSDT | 4321 | 0.59 | 1.55 | 0.02% | 1 | 0.60 | 100.0% | 1 |
| ETHUSDT | 4321 | 0.56 | 1.63 | 0.32% | 3 | 1.58 | 100.0% | 15 |
| SOLUSDT | 4321 | 1.21 | 2.53 | 2.01% | 49 | 1.53 | 75.5% | 15 |

### 4.2 这些数字真正说明了什么
先说最重要的结论：

> **BTC / ETH 这条线在 2026 年的分钟级公开 close 数据上，已经非常薄；SOL 还留着一点毛边，但也更像 execution alpha，而不是“裸 spread 就能躺赚”的 alpha。**

更具体地说：
1. **BTC 几乎没肉**
   - 3 天里满足条件的信号几乎没有；
   - `p95` 绝对价差只有 `1.55bps`；
   - 这意味着你如果不是特殊费率、特殊 routing、或不是盘口级别的微结构优势，基本不值得碰。

2. **ETH 也已经很薄**
   - 中位和 `p95` 价差都跟 BTC 类似；
   - 偶尔有 `>=3bps` 偏离，但频率很低；
   - 更像偶发 inventory/latency pocket，不像稳定日内主线。

3. **SOL 才是当前最像“还值得继续做”的那类标的**
   - 中位绝对价差 `1.21bps`，明显高于 BTC/ETH；
   - `>=3bps` 的分钟占比 `2.01%`；
   - 在这个很保守的 spread-close toy shell 下，3 天能打出 `49` 笔信号，单笔 gross `~1.53bps`，胜率 `75.5%`。

但要马上泼一盆冷水：
- **1.53bps gross/trade 远远不等于可净赚**；
- 若两腿都 taker，很多 venue 直接就把利润吃完了；
- 这说明**今天跨所价差回归的关键，不是会不会回，而是你能不能用 maker/rebate/internal inventory 把交易成本压到足够低。**

这和论文主结论是高度一致的：
- alpha 本体没消失；
- **可被普通执行吃到的部分，已经被压得很薄。**

## 5) 这条线现在更适合怎么落地成完整策略
### 5.1 策略拆解（必填）
- 方向属性：market-neutral / relative-value / stat-arb / same-underlier cross-venue
- 基础 alpha：**venue 间同标的错价回归**
- raw alpha 主体：`spread dislocation -> spread close`
- regime：
  - 仅在高流动、低 incident 概率时启用
  - 仅做存在稳定分钟级价差毛边的币种/venue 组合
- filter / veto：
  - funding 差异突然放大时 veto
  - venue API 延迟、标记价格异常、事故公告时 veto
  - 单边 liquidation cascade / ADL 风险升高时 veto
- sizing / risk：
  - 两腿等美元或 beta-hedged 配平
  - 每个 venue 单独限制 gross / leverage / inventory
  - 按 `expected spread half-life` 和 `fee budget` 缩放仓位
- entry：
  - `|spread z| >= 2~2.5`
  - 且绝对 spread 高于**净成本预算 + 安全边际**
- exit：
  - `z -> 0`
  - 或 `|z| <= 0.25~0.5`
  - 或时间止盈/止损 `5~15m`
- stop：
  - `|z|` 继续扩张到 `3.5~4`
  - 或单边 venue 发生 order-book 真空 / quote freeze
- cost：
  - **必须显式测 maker/taker 组合**
  - taker+taker 基本可判死刑
  - maker+taker、maker+maker、inventory netting 才可能活

### 5.2 更像 production 的策略壳应该长什么样
对我们 desk，更现实的落地方式不是“扫所有币，一有价差就双腿打单”，而是：

1. **先做 admission layer**
   - 过去 `7~14d` 每个 symbol × venue-pair 统计：
     - median / p95 spread
     - `>= cost_budget` 的出现频率
     - spread half-life
     - adverse excursion
   - 只保留**有肉、且可控**的组合

2. **再做 execution layer**
   - 尽量一腿 maker、一腿 taker；
   - 如果已有 inventory，优先做 inventory flattening；
   - 重大事件或 venue incident 时自动降杠杆或停机。

3. **最后才去卷 z-score 细节**
   - 这个顺序很重要；
   - 因为在今天的 majors 上，真正决定成败的已经不是 signal 花活，而是成本和执行结构。

## 6) 对 `1m / 3m / 5m / 15m` 的 desk 映射
### 6.1 `1m / 3m`
这是这条 alpha 最自然的频段：
- spread 出现与回归都更清晰；
- 但你更依赖盘口、队列位置、低延迟路由；
- 更适合做成 **microstructure + routing** 组件，而不是普通 bar-strategy。

### 6.2 `5m`
这是目前最像“desk 能快速起最小实验”的档位：
- 还能保留短周期 dislocation；
- 对基础设施要求比 `1m` 低；
- 可以先用 close 或 mid proxy 做筛选，再决定是否下钻盘口级。

### 6.3 `15m`
`15m` 更适合做：
- **admission / regime / cost 评估**；
- 而不是直接拿来做主要 entry 触发。

因为如果 spread 的生命周期经常只有几分钟，那 `15m` 主信号大概率已经太慢。

## 7) 为什么这篇现在比继续补一个普通 breakout 更值得
因为它回答的是一个更底层的问题：

> **哪些 relative-value alpha 还剩“真毛边”，哪些已经只剩 paper alpha？**

这对素材池非常重要。我们不需要再把所有跨所/同标的题材都默认当成“可做”。
这篇给了一个更实用的框架：
- BTC/ETH 这类大币，默认先当**低优先级 execution alpha**；
- 更该把研究火力放在：
  - alt perp；
  - venue-specific inventory pocket；
  - funding/liq/OI 共振造成的临时错价；
  - maker-first / inventory-aware 交易壳。

也就是说，**这篇不是为了抬高跨所套利，而是为了更快把“已经没肉的线”排掉，把资源留给还活着的那部分。**

## 8) 下一步怎么测（本篇最重要的部分）
### 实验 A：把 close proxy 升级成可交易盘口
**目的**：确认 public `1m` close 上看到的毛边，是否真能穿过 bid/ask + fee。

- 数据：Binance / Bybit / OKX / Hyperliquid `best bid/ask` 或 L2 snapshot
- 频率：`1s ~ 5s`
- 输出：
  - mid spread
  - executable spread（买得到/卖得掉的真实双边价差）
  - maker/taker / maker/maker 两种 net PnL

### 实验 B：做 symbol × venue-pair admission ranking
**目的**：别再默认 BTC/ETH 是最值得做的跨所对。

- 对每个 symbol × venue-pair 统计：
  - `median_abs_spread_bps`
  - `p95_abs_spread_bps`
  - `share(spread > cost_budget)`
  - `half_life`
  - `max adverse excursion`
- 输出一个 **tradability score**
- 每天只交易 top `5~10` 个组合

### 实验 C：把 funding / OI / liquidation 当成 spread-close 的 gate，而不是硬说它们本身就是 alpha
**目的**：看看跨所错价是否更容易出现在结构性压力时段。

加三个公开可得特征：
- venue funding spread
- venue-level open interest change
- liquidation cluster / public trigger map

测试问题：
- 价差出现概率是否在这些 stress 条件下明显上升？
- 回归胜率是否上升，还是只是波动更大、风险更脏？

### 实验 D：比较 `1m / 3m / 5m / 15m` 作为触发频段 vs 管理频段
**目的**：分清“signal bar”与“risk bar”。

- `1m/3m`：负责触发
- `5m`：负责 time stop / spread normalization
- `15m`：负责停机、降杠杆、venue veto

如果结果显示：
- 触发必须 `1m` 才有肉，
- 但风险控制用 `5m/15m` 更稳，

那这条线就应该被归类为：
**fast raw alpha + slower risk shell**。

## 9) 一句话结论
这篇 JFM 2023 对我们最有价值的，不是“跨所套利存在过”，而是它很诚实地告诉你：

> **这条 raw alpha 现在还活着，但在 majors 上大多已经被压缩成 execution 生意；真正值得继续深挖的，是 alt venue-dislocation + maker-first / inventory-aware 的那部分残余毛边。**

## 10) 来源
1. Crépellière, Tommy; Pelster, Matthias; Zeisberger, Stefan (2023), *Arbitrage in the market for cryptocurrencies*, **Journal of Financial Markets**, 64, 100817.
   - DOI: `10.1016/j.finmar.2023.100817`
   - DOI URL: `https://doi.org/10.1016/j.finmar.2023.100817`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1386418123000150?via%3Dihub`
2. OpenAlex metadata / abstract reconstruction:
   - `https://api.openalex.org/works/https://doi.org/10.1016/j.finmar.2023.100817?select=display_name,doi,publication_year,authorships,abstract_inverted_index,primary_location,biblio,cited_by_count`
3. Crossref metadata:
   - `https://api.crossref.org/works/10.1016/j.finmar.2023.100817`
4. Public data endpoints used in the quick check:
   - Binance USDⓈ-M Futures Klines: `https://fapi.binance.com/fapi/v1/klines`
   - Bybit Market Kline: `https://api.bybit.com/v5/market/kline`
5. Local artifact:
   - `reports/artifacts/quant_digests/2026-04-03_cross-exchange-binance-bybit-arb-sanity.csv`
