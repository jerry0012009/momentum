# 别把这份今天刚创建的 order-book notebook 只读成数据体操：对 short-cycle desk，更该先测的是「top20 depth imbalance × tight-spread continuation」这条 microstructure raw alpha

- 时间：2026-04-05 00:59 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `order_book_extensive_analysis.ipynb` 存档输出）+ Bybit 公共 orderbook 文档
- 主题类型：raw alpha
- 基础 alpha：**盘口前 20 档深度失衡（bid-vs-ask imbalance）会在接下来极短窗口继续推着 mid-price 往同方向走；而且这条 edge 在 tight spread 状态更强。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-book-imbalance/depth-imbalance/top20/tight-spread/continuation/event-time/bybit/btcusdt/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo notebook 内置单日样本统计与信号分层输出；目前不是多日 walk-forward，但已经足够做最小复现

## 1. 先回答一句：base alpha 是什么？

**base alpha = 当买盘深度显著大于卖盘深度时，未来几秒 / 几十个事件的 mid-price 更容易继续上漂；当卖盘深度显著占优时，未来 mid-price 更容易继续下滑。**

这不是：
- breakout 形态复读；
- 5m K 线级别的趋势因子；
- “跌了以后会不会弹”的反转故事。

它更像是：

> **盘口库存不平衡 → 极短窗口价格发现继续沿失衡方向推进。**

所以它属于很纯的 **microstructure raw alpha**。

## 2. 为什么这轮值得选它？

结合最近 digest 进展，当前池子里已经有不少：
- pairs / stat-arb
- funding / basis / carry
- 单资产 trend / breakout / fade
- 一批“order flow / OBI”相关，但很多是 **5m 级别的反转、确认或 maker conviction gate**

这轮更值得补的，反而是一个更底层、也更“快”的原型：

> **book-depth 失衡本身能不能当 raw alpha？**

原因很简单：
- 它天然更适合 `1m / 3m`，而不是被硬塞回 `15m`；
- 如果成立，它不只是一条独立 alpha，还是很多现有策略的 **entry confirmer / execution veto / maker skew driver**；
- 它跟之前的 OBI 题材不重复：
  - 不是 `5m downbar + buy pressure -> 1h bounce` 那类反转；
  - 不是 signed trade imbalance 的 maker-only 过滤器；
  - 而是**同方向 continuation** 的更原生 microstructure 版本。

对 short-cycle desk 来说，这类材料的价值很高：
**哪怕最后独立 taker 策略不赚钱，它也很可能成为别的 alpha 的 shared trigger。**

## 3. 这份 repo 到底提供了什么？

主材料来自今天刚创建的 GitHub repo：

- **Author / Repo Owner**：`Starkl7`
- **Year**：2026
- **Title**：`Crypto-OrderBook-Imbalance`
- **Venue**：GitHub repository（无 DOI / 无期刊）
- **Repo URL**：<https://github.com/Starkl7/Crypto-OrderBook-Imbalance>
- **Notebook Raw URL**：<https://raw.githubusercontent.com/Starkl7/Crypto-OrderBook-Imbalance/main/order_book_extensive_analysis.ipynb>
- **GitHub API Metadata**：<https://api.github.com/repos/Starkl7/Crypto-OrderBook-Imbalance>

repo 很小，核心几乎都在一个 notebook 里，但信息密度够高：
- 数据文件：`2026-01-01_BTCUSDT_ob200.data`
- 主题：`orderbook.200.BTCUSDT`
- 处理方式：按 **snapshot / delta** 重建本地 order book
- 特征：
  - best bid / ask
  - mid
  - spread_bps
  - bid / ask top20 volume
  - `imbalance_top20 = (bid_vol_top20 - ask_vol_top20) / (bid_vol_top20 + ask_vol_top20)`
- 验证方式：
  - 事件时间 forward return（10 / 50 / 200 / 500 events）
  - 秒级 forward return（1s / 2s）
  - spread regime（tight / normal / wide）分层

同时 Bybit 官方文档也说明：
- `orderbook.200.{symbol}` 是公开订阅流；
- 线性合约 level-200 的推送频率是 **100ms**；
- message schema 的 `snapshot / delta / ts / cts / seq / u` 全部公开；
- 本地重建 order book 的规则也是公开的。

所以这条线的最大优点是：
**不是私有数据故事，而是真能拿公开流快速复现。**

## 4. notebook 里最值钱的证据，不是图，而是这几组数

### 4.1 样本本身足够密：24 小时、42.4 万条 level-200 消息

notebook 存档输出给出的基础统计：
- 样本区间：**2026-01-01 00:00:01.998 UTC ~ 2026-01-02 00:00:01.998 UTC**
- 解析消息数：**424,195**
- 其中 snapshot：**2** 条；delta：**424,193** 条
- 样本标的：**BTCUSDT**
- 原始数据文件大小：**183,668,659 bytes**

这意味着平均节奏大约是：
- 一天 42.4 万条 order book 事件；
- 粗略折算每秒约 **4.9** 条消息；
- 对 `1s / 2s / 10~200 events` 的最小 alpha 检验已经够密。

### 4.2 盘口失衡不是噪声：`imbalance_top20` 分布很宽

notebook 描述统计：
- `imbalance_top20` 平均值：**0.0481**
- 标准差：**0.3447**
- 最小值：**-0.9001**
- 最大值：**0.9780**

翻成人话：
- 这不是一个只在 `[-0.05, +0.05]` 里抖动的小指标；
- 在很多时刻，前 20 档深度会明显偏向某一边；
- 因而它具备做 decile 分层的基础，不是硬凑特征。

### 4.3 最关键：imbalance decile 与未来收益基本单调

`50-event` forward return（单位：bps）里，decile 结果非常干净：

- decile 1（最 ask-heavy）：**-0.2673 bps**
- decile 2：**-0.1884 bps**
- decile 3：**-0.1256 bps**
- decile 4：**-0.0642 bps**
- decile 5：**+0.0004 bps**
- decile 6：**+0.0681 bps**
- decile 7：**+0.1229 bps**
- decile 8：**+0.1553 bps**
- decile 9：**+0.1989 bps**
- decile 10（最 bid-heavy）：**+0.2612 bps**

也就是说：

> **从最偏卖压到最偏买压，50-event 的 extreme-decile spread 大约是 0.5285 bps。**

`200-event` 更明显：
- decile 1：**-0.3136 bps**
- decile 10：**+0.5271 bps**
- extreme-decile spread：**0.8407 bps**

这条单调性是这轮最值钱的东西。
它说明这不是“只在极端点偶然有点 edge”，而是：
**失衡越偏向 bid，未来 drift 越偏正；越偏向 ask，未来 drift 越偏负。**

### 4.4 它不是只存在于 event-time 幻觉里：秒级读数也保留同方向关系

`1s` forward return：
- decile 1：**-0.0631 bps**
- decile 10：**+0.0542 bps**
- extreme-decile spread：**0.1172 bps**

`2s` forward return：
- decile 1：**-0.1033 bps**
- decile 10：**+0.0904 bps**
- extreme-decile spread：**0.1938 bps**

这很重要，因为很多 event-time alpha 会被吐槽成：
“只是消息更密的时候更容易看到更多更新，不是真正的 wall-clock 可交易信号。”

但这里至少从 notebook 存档结果看，**转成 1 秒 / 2 秒后，方向关系还在。**

当然，边际也立刻暴露了：
- edge 很小；
- 绝不适合高 taker fee 的粗暴扫单；
- 更像是 **maker leaning / skew / fast confirmation** 的信号。

### 4.5 tight spread 才是更好的土壤

repo 的 spread-regime 分层也很有用。
在 `50-event` horizon 下，decile10-minus-decile1 的极值差：

- **tight**：**0.6573 bps**
- **normal**：**0.4343 bps**
- **wide**：**0.4411 bps**

这句话非常 desk-friendly：

> **不是 spread 越宽 edge 越大；恰恰相反，盘口健康、价差紧的时候，这条 depth-imbalance continuation 更干净。**

这给了一个明确的执行含义：
- 不要把 OBI 失衡简单理解成“宽价差 / 混乱状态下的方向暴露”；
- 这条 alpha 更像是 **正常市场中的供需轻微倾斜**，而不是 panic 阶段的瞎冲。

## 5. 对 short-cycle desk，应该怎么读它？

### 5.1 它首先服务 `1m / 3m`，不是天然服务 `15m`

最诚实的读法是：
- 这条 alpha 的原生频率在 **秒级 / event-time**；
- 它更适合做 `1m / 3m` 的快信号或入场确认；
- 对 `5m / 15m`，更适合作为：
  - breakout confirm
  - fade veto
  - maker skew
  - execution timing layer

所以不要误读成：
“又发现了一条可以直接在 15m bar close 上做多做空的主信号。”

不是。
它更像是一个 **micro alpha primitive**。

### 5.2 这条线最可能先在哪些标的活下来？

优先级我会放在：
1. **BTCUSDT perp**
2. **ETHUSDT perp**
3. **SOLUSDT perp**（但更容易受冲击成本和假深度影响）

不建议一开始就全市场扩散，原因是：
- 这条 edge 本来就只有不到 1 bps 级别；
- alt perp 的真实排队、撤单、毒性、假深度，会比 BTC 更快吃掉毛 edge；
- 先在最厚的 1~3 个品种确认“方向关系 + 成本曲线 + 稳定性”，再谈 cross-sectional 扩张。

## 6. desk 版完整策略壳：可以直接写最小回测

## 6.1 Universe

第一版只做：
- Bybit / Binance 最液体 perp
- `BTCUSDT`, `ETHUSDT`，必要时加 `SOLUSDT`
- 数据必须同时拿：
  - order book depth（最好 level 50/200）
  - trades / agg trades
  - mid / spread / top-of-book

如果只拿到 Binance 的浅层书，也可以先做粗版；
但若要贴近 source，最好优先用 **Bybit level-200**。

## 6.2 Signal

最小实现直接照 source：

```text
imbalance_top20 = (sum_bid_qty_top20 - sum_ask_qty_top20)
                  / (sum_bid_qty_top20 + sum_ask_qty_top20)
```

然后做两种版本：

### 版本 A：原生秒级 continuation
- 每次 book 更新都刷新 `imbalance_top20`
- 计算 rolling percentile / decile
- long trigger：`imbalance_decile >= 9`
- short trigger：`imbalance_decile <= 2`
- spread gate：只在 `tight` 或 `normal` spread regime 启动

### 版本 B：映射到 1m / 3m
把秒级信号聚合成 bar 内得分：

```text
obi_score_1m = mean(last 30~60s imbalance_top20)
obi_persist = pct(last 30~60s snapshots with decile in top/bottom 20%)
```

- long：`obi_score_1m > q80` 且 `obi_persist > 0.6`
- short：`obi_score_1m < q20` 且 `obi_persist > 0.6`
- 如果用于 `3m`，则把观察窗扩到 90~180 秒

这一步的核心不是换 fancy 模型，而是把**瞬时盘口倾斜**变成**可执行的 bar 内累计压力**。

## 6.3 Entry / Exit

### 纯秒级版
- **Entry**：信号触发即下单
- **Exit**：
  1. 固定持有 `1s / 2s / 5s` 三档做对照；
  2. 或持有 `10 / 50 / 200 events`；
  3. 若出现反向 decile（如从 9/10 掉到 1/2）则提前离场；
  4. 若 spread 从 tight 突然切到 wide，则直接 flatten。

### 1m / 3m 映射版
- **Entry**：每 10s 或每 bar 内滚动判断一次，不必等 bar close
- **Exit**：
  - `30s / 60s / 180s` time stop
  - opposite signal close
  - spread widening veto
  - 微型止损：如反向 mid move 超过 `2~3 bps`

## 6.4 Sizing

因为毛 edge 很薄， sizing 必须保守：
- 单品种先做固定小 notional
- 然后再切到 inverse micro-vol sizing
- 每个 symbol 设置最大 quote / taker notional cap
- 若是 maker-first 版本，按 queue capacity 和 inventory 上限控仓

更直白一点：
**先验证信号，不要一上来把容量幻想写太满。**

## 6.5 Risk / Cost

这里必须泼冷水：

- `1s / 2s` horizon 的 gross edge 只有 **0.12 ~ 0.19 bps**（extreme spread）
- `50 / 200 events` 也只有 **0.53 ~ 0.84 bps**

这意味着：
- 对大多数普通 taker fee 档位，**独立 aggressive taker 策略很可能直接被费用吃光**；
- 真正更现实的落地路径是：
  1. **maker skew / quote leaning**：根据 OBI 调整挂单偏向；
  2. **已有主策略的入场确认**：只有当 OBI 与主方向一致才放行；
  3. **taker but only on fee-favorable / internalized / VIP execution path**。

建议在回测里至少分 3 档成本：
- maker optimistic：`0 ~ 0.5 bps/side`
- blended：`0.5 ~ 1.0 bps/side`
- taker realistic：`2 ~ 5 bps/side`（按实际 venue 档位填）

如果只有第一档活，那就别把它包装成独立 taker alpha，
而应老老实实归类成：
**microstructure directional primitive + execution layer**。

## 7. 这条线最容易犯的错

### 错法 1：把“方向单调”误读成“可直接市价扫单”

source 给出的统计最漂亮的地方，是 decile 单调。
但这不等于：
- 可以无脑 aggressive；
- 每次触发都值回票价；
- 不需要看 queue / fee / latency。

这类 alpha 最常见的死法，就是**信号正确，但执行方式错误**。

### 错法 2：把它硬拉长到 15m 主信号

这条线最强的证据是秒级 / event-time。
你当然可以聚合成 `1m / 3m`，
但如果一路硬压成 `15m` 主因子，很可能会被：
- 更慢的 trend / mean reversion 因子稀释；
- funding / session / inventory shock 混淆；
- bar aggregation 直接洗掉。

### 错法 3：只看 BTC 一天样本就宣称“稳了”

目前 source 的短板也要写清楚：
- 只有 **一天**；
- 只有 **BTCUSDT**；
- 还没有 out-of-sample；
- 还没有真正成交模型。

所以它现在的地位应该是：
**高质量 intake 候选，不是已验证生产因子。**

## 8. 当前最诚实的 verdict

**Verdict：值得进 raw alpha 池，而且优先级不低。**

原因不是“它已经证明可以独立赚钱”，而是：
1. **base alpha 很清楚**：depth imbalance → same-direction drift；
2. **source 直接可复现**：公开 book feed + 明确特征公式；
3. **和当前 desk 目标高度匹配**：更适合 `1m / 3m` 的高强度 alpha；
4. **即便独立 taker 不活，也很可能作为 shared gate / maker skew 非常有价值。**

如果让我给一个更务实的定位：

> **它首先是一个值得进池的 microstructure raw alpha；其次才是一个待验证的独立策略。**

## 9. 下一步怎么测（直接排最小实验）

### 实验 A：复刻 source 的最小事实，不要先做 fancy execution

目标：先确认关系是否存在。

数据：
- Bybit public `orderbook.200` + trade stream
- 标的：`BTCUSDT`
- 样本：至少最近 **30 天**，覆盖不同波动 regime

输出：
- `imbalance_top20` decile vs `1s / 2s / 5s / 10s` forward return
- `10 / 50 / 200 events` forward return
- `tight / normal / wide` 分层
- UTC hour 分层

判定标准：
- 看单调性是否稳定；
- 看极值 spread 是否在多数天都为正；
- 看是不是只在少数波动时段才成立。

### 实验 B：从“单点失衡”变成“可执行持久失衡”

把信号改成 persistence 版本：

```text
persist_long = pct(last 20~50 snapshots with imbalance_decile >= 9)
persist_short = pct(last 20~50 snapshots with imbalance_decile <= 2)
```

比较：
- 单次瞬时 decile 触发
- 连续持久 decile 触发
- EWMA imbalance 触发

目标：
**找出最不容易被噪声翻面的版本。**

### 实验 C：跨资产移植，但先只测最厚的两三个品种

标的：
- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`

不要急着上全市场。
先看：
- 哪些品种还能保留 decile 单调；
- 哪些品种虽然方向对，但成本后归零；
- 哪些品种其实更适合 maker skew 而不是 taker alpha。

### 实验 D：成本敏感性必须单列，不要混在总回测里

至少跑 3 套：
1. post-only maker first
2. blended execution
3. pure taker

然后输出：
- 毛 edge
- 净 edge
- hit rate
- average holding time
- cancel / miss rate

目标不是把曲线做漂亮，
而是先回答一句：

> **这条线到底是独立 alpha，还是 execution primitive？**

## 10. 与当前 `1m / 3m / 5m / 15m` 框架的关系

- **1m / 3m**：最相关，适合直接做 alpha 或 entry confirmer
- **5m**：可以做 bar 内 pressure summary，用来过滤 breakout / fade
- **15m**：不建议当主信号；更适合做 execution veto 或只在 bar 内优化开仓时点

换句话说：

> **这条线不是要取代 5m/15m 主策略，而是给更快层提供一个可复现的 microstructure 原件。**

## 11. 来源与链接

1. **Starkl7 (2026). _Crypto-OrderBook-Imbalance_. GitHub repository.**  
   Repo URL: <https://github.com/Starkl7/Crypto-OrderBook-Imbalance>  
   GitHub API metadata: <https://api.github.com/repos/Starkl7/Crypto-OrderBook-Imbalance>

2. **Starkl7 (2026). _order_book_extensive_analysis.ipynb_.**  
   Raw notebook: <https://raw.githubusercontent.com/Starkl7/Crypto-OrderBook-Imbalance/main/order_book_extensive_analysis.ipynb>

3. **Bybit API Documentation — Orderbook WebSocket (public).**  
   Readable URL: <https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook>

---

**一句话结论：**
这轮最该 intake 的，不是“又一个 OBI 概念”，而是**前 20 档深度失衡在 tight spread 下能否稳定转成 1m/3m 可执行 continuation alpha**；如果独立 taker 不活，它也大概率值得留下来做 shared microstructure gate。
