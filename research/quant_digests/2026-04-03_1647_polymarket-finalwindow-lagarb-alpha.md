# 别把这份 2026 v5 bot 读成“AI 下注工具”：它真正可独立复现的 base alpha，是「Binance 领涨/领跌 × Polymarket 最后 120 秒滞后定价」
- 时间：2026-04-03 16:47 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `config.py` + `signal_engine.py` + `risk.py` + `executor.py` + `bot.py` + `analyze.py`）+ Polymarket / Chainlink / Binance 公共接口路径校对
- 主题类型：raw alpha
- 基础 alpha：**crypto-linked binary market 的 cross-venue lag arb**——当 Binance 现货/指数侧的短秒级方向变化已出现，但 Polymarket 的 `BTC/ETH 5m/15m UP/DOWN` 合约赔率还没跟上时，在临近到期窗口买入被低估的一侧，吃的是 **leader venue → hard-expiry binary venue** 的短暂滞后修复。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/relative-value/prediction-market/polymarket/binance/chainlink/5m/15m/hard-expiry/final-window/lag-arb/maker-mode/kelly/late-entry/external-data/repo/public-data/cost/risk
- 证据类型：GitHub README/source 规则级证据 + 公共数据接口可达性/字段路径校对

## 1. 这次看了什么
先把 **base alpha** 说清楚：

> **这不是 AI alpha，也不是 event scanner，也不是“让 LLM 决定要不要买”。真正的 alpha 本体，是 Binance/Chainlink 先动、Polymarket 二元赔率后动。**

翻成人话：
- `BTC/ETH 5m/15m UP/DOWN` 这类 binary 合约，越接近到期，价格越应该像“短时间内收涨概率”的实时映射；
- 如果 Binance 这边已经在 10s/30s/60s 上给出明确方向，而 Polymarket 订单簿里的 YES/NO 价格还没把这个变化吃进去，那里就会出现可交易的 **赔率滞后**；
- 于是策略在 **最后 120 秒到 3 秒** 的窗口里，买入被低估的一边，靠的是 **leader venue 价格发现领先**，不是靠宏大叙事，更不是靠 AI 猜新闻。

这条线为什么值得进当前素材池？因为它满足几件很难同时满足的事：
1. **raw alpha 很清楚**：不是 gate，不是 overlay，本体就是 binary-price underreaction；
2. **频率天然贴 5m/15m**：不是硬把日频材料强行压成快周期；
3. **策略组件完整**：entry / exit / sizing / risk / cost 都给出来了；
4. **和 desk 当前短周期方向直接相邻**：虽然交易 venue 不是 perp，但底层驱动仍是 crypto 秒级价格发现。

一句话结论先放前面：

> **这份 repo 真正有价值的不是“AI 过滤器”，而是“临近到期的 binary 合约，能不能被 leader venue 的超短 momentum/OFI 抢跑”。如果要做最小实验，先把 AI 全关掉，只测 final-window lag arb。**

## 2. 核心结论
### 2.1 这份 repo 的主线到底是什么
主仓库是：
- **Author / Year / Title / Venue**：`andiyusanto` / 2026 / *Polymarket Latency Arbitrage Bot (v5)* / GitHub repo
- **Readable URL**：<https://github.com/andiyusanto/opus-clude-polymarket-arbitrage-bot>
- **Repo URL**：<https://github.com/andiyusanto/opus-clude-polymarket-arbitrage-bot>
- **DOI**：无（repo-based intake）

repo README 标得很明白：
- 监控的是 **BTC/ETH up/down prediction markets on Polymarket**；
- 参考的是 **Binance WebSocket**；
- v4 开始又叠了一层 **Chainlink RTDS** 作为 resolution-oracle 方向确认；
- v5 才新加了 AI filter 和 event scanner。

所以别被 README 的“AI v5”抢走注意力。按对 desk 最有用的读法，repo 里真正该 intake 的东西是：

> **用 leader venue 的短秒级价格变化去估一个临近到期 binary market 的 fair value，然后只在最后时间窗里、只在 edge 足够厚的时候出手。**

### 2.2 规则壳已经给到什么程度
从 `config.py`、`signal_engine.py`、`executor.py`、`risk.py` 可以直接拆出完整骨架：

#### 数据与市场
- **Leader source**：Binance WebSocket（`wss://data-stream.binance.com/stream`）
- **Secondary confirmation**：Chainlink RTDS（repo 中 `chainlink_feed.py`）
- **Execution venue**：Polymarket CLOB（`https://clob.polymarket.com`）
- **发现市场**：Polymarket Gamma API（`https://gamma-api.polymarket.com/events`）
- **标的**：repo 主写 `BTC` / `ETH` 的 `5m/15m` UP/DOWN 合约

#### Entry logic（核心）
repo 的信号不是“看涨就买”，而是一个 **fair-value vs current-binary-price** 的差值交易：
1. 从 Binance tick history 里算 `10s / 30s / 60s` 三档 momentum；
2. 再加一个 `momentum acceleration`（最近 10s 比 30s 更强还是更弱）；
3. 加一个 `consecutive tick direction`，要求最近 15s 至少有连续同向 tick；
4. 再把这些拼成一个 `fair value ∈ [0.05, 0.95]`；
5. 如果 `fair > Polymarket YES`，买 YES；否则买 NO；
6. 只有在 `edge_pct >= min_edge_pct` 且 `lag_pct >= lag_threshold_pct` 时才下单。

repo 里默认参数：
- `min_edge_pct = 1.2%`
- `lag_threshold_pct = 1.5%`
- `confidence_threshold = 40`
- `min_momentum_pct = 0.05`
- 至少 `2` 个同向连续 ticks

这其实已经是一个完整 raw alpha：

> **binary 合约价格没有及时反映 leader 价格变动时，买低估概率。**

#### 时间窗（非常关键）
repo 最值钱的不是“买不买”，而是 **什么时候才值得买**：
- `min_time_remaining_sec = 120.0`
- `max_time_remaining_sec = 3.0`

也就是：
- **太早不做**，因为 binary 价格还会被噪声、流动性和中间波动拖着走；
- **太晚也不做**，避免最后 3 秒流动性/成交确认问题；
- 真正打的是 **临近到期、赔率开始向终局概率收敛** 的最后窗口。

这点对 short-cycle desk 很重要，因为它说明：

> **alpha 不是“全时段都存在”，而是高度 time-conditioned。**

#### 执行逻辑
repo 明确区分 maker 与 taker：
- 默认 `use_maker_orders = True`
- `maker_tick_offset = 1`
- `maker_fill_timeout_sec = 8.0`
- 只有当 `edge_pct >= 6.0%` 时才允许 taker fallback

成本假设：
- `taker_fee_pct = 1.80%`
- `maker_rebate_pct = 0.20%`
- `simulated_slippage_pct = 0.3%`
- `fee_buffer_pct = 0.3%`

所以这条 alpha 的经济学并不是“随便方向对了就行”，而是：

> **如果你能以 maker 低成本挂进去，1.2% 的 edge 也许够；如果你要用 taker 冲进去，成本会把大部分薄 edge 直接吃掉。**

#### 仓位与风控
repo 不是 fixed size，而是 Kelly 缩放：
- `kelly_fraction = 0.34`
- `max_position_pct = 3.0`
- `kill_switch_drawdown = 15.0`
- 单资产总暴露上限：`20%`
- 最大并发持仓：`5`
- 到期前 `10` 秒自动平仓

也就是说，它不是单纯的信号脚本，而是已经把：
- sizing
- exposure cap
- kill switch
- expiry close
- order cooldown
都拆清楚了。

### 2.3 这份 repo 最值得 intake 的，不是 AI
v5 README 一眼看过去最显眼的是 AI filter，但从 source 看，AI 更像一个 **可选 overlay**，不是 alpha 本体。

更关键的是，`signal_engine.py` 里 AI filter 那段调用顺序本身就值得警惕：
- `validate_signal(...)` 调用里引用了 `side` 和 `edge_pct`；
- 但这两个变量在代码里是 **后面才定义** 的。

这意味着：
1. repo 作者想表达的是“AI 只做 pre-trade validation”；
2. 但当前实现顺序看起来并不适合把 AI 当主研究主题；
3. **第一轮复现应默认关闭 AI**，先把纯 quant lag-arb 壳跑通。

这正好也符合本轮 intake 原则：

> **不要把 overlay 伪装成 raw alpha。**

## 3. 为什么和当前 desk 直接相关
先回答一句：

> **为什么这东西比再补一篇普通 trend/pairs 更值得？**

因为它补的是当前库里相对少的一类：
- 不是传统 perp/spot 的单边趋势；
- 不是又一条 z-score pair；
- 而是 **hard-expiry 二元概率市场** 上，由 crypto leader venue 驱动的 **relative-value / lag-repair** alpha。

它和当前 desk 的关系有三层：

### 3.1 它本身就是一条完整 raw alpha
而且是少数能把以下都写清楚的：
- **entry**：fair value vs YES/NO edge
- **exit**：到期前 10 秒 / 合约收敛
- **sizing**：Kelly × position cap
- **risk**：daily drawdown kill switch / concurrent cap / asset exposure cap
- **cost**：maker/taker 分流 + slippage + fee buffer

### 3.2 它天然落在 `5m / 15m`
很多低频材料要硬压成快周期会变味；这条不是。
它的市场本体就是：
- `5m`
- `15m`

所以最小实验可以直接做，不需要先发明“如何把日频论文缩成 5m”。

### 3.3 它还能反向服务我们对 perp alpha 的理解
如果未来不直接做 Polymarket，这条材料仍有 desk 价值：
- binary 合约的滞后，本质上是 **另一个 venue 对 crypto 短秒级冲击的慢反应**；
- 这和跨交易所 premium、跨 venue price discovery、event-contract mispricing，本质是一类问题。

换句话说：

> **先把它当 standalone 策略看；若不做 binary 执行，再把它降级成“外部确认/对照市场”。**

## 3.5 策略拆解（必填）
- 方向属性：**cross-market / relative-value / hard-expiry binary lag arb**
- 基础 alpha：**leader venue（Binance/Chainlink）价格发现领先于 Polymarket binary odds 的短暂滞后修复**
- 原 repo 的完整策略组件：
  - `signal layer`：10s/30s/60s multi-TF momentum + acceleration + consecutive-tick consistency
  - `pricing layer`：fair value vs `YES/NO` market price
  - `admission layer`：final-window only（120s → 3s）、min edge、min lag、min confidence、min momentum
  - `execution layer`：maker-first，extreme edge 才 taker fallback
  - `exit layer`：接近到期自动平仓
  - `sizing layer`：Kelly fraction × max position cap
  - `risk layer`：daily DD kill switch / open-count cap / per-asset exposure cap
  - `cost layer`：1.8% taker fee、0.2% maker rebate、0.3% simulated slippage、fee buffer

## 4. 这条 alpha 在我们这边该怎么读
### 4.1 不要把它读成“预测市场很神奇”
它不是在预测谁会赢，而是在交易：

> **一个临近到期、结算规则清晰、概率解释明确的合约，是否还没有把 leader 价格发现 fully price in。**

也就是说：
- 本质不是新闻判断；
- 不是观点投资；
- 不是 AI 讲故事；
- 是 **价格映射收敛**。

### 4.2 它更像哪类传统 desk 思路
如果翻成更熟悉的 desk 语言，它更接近：
- cross-venue lead-lag
- near-expiry event contract mispricing
- hard-close window arbitrage
- binaryized short-horizon relative value

所以它不是游离主题，反而能和我们现有这些材料形成互证：
- Coinbase/Binance premium impulse
- Kalshi/Polymarket binary mispricing
- lead-lag / OFI / time-of-day execution window

### 4.3 这条线真正的脆弱点是什么
repo 给了完整 skeleton，但脆弱点也很清楚：
1. **maker fill risk**：挂单如果 8 秒内不成交，edge 可能已经没了；
2. **binary 订单簿薄**：1.2% edge 看着不小，但盘口深度可能不够；
3. **late-window 竞争极强**：越靠近 expiry，越容易被更低延迟对手吃掉；
4. **paper/live 差异可能大**：README 自己也要求先积累 200+ paper trades 再谈 live；
5. **AI 过滤器不应当先信**：当前实现先天更像 overlay，而且 source 顺序还有明显疑点。

## 5. 对 `1m / 3m / 5m / 15m` 的可迁移性
### 5.1 直接可迁移
- **5m**：最直接，对应 repo 原生目标市场；
- **15m**：也直接，对应 README 写的 recurring market；
- **1m / 3m**：概念上可迁移，但前提是平台上存在足够深度、足够稳定的同类短合约，否则 alpha 还在、容量不在。

### 5.2 不能硬搬的部分
- `10s/30s/60s` momentum 这套 fair-value mapping，不一定能原封不动搬到 perp 上；
- 因为 Polymarket 这里多了一个 **hard expiry + binary payoff** 的结构；
- 在 perp/spot 上，价格不是概率，收敛机制也不同。

所以要老实写：

> **这是一条可以独立交易的 raw alpha，但它不是“直接复制到 perp 里就还是同一条 alpha”。**

对 perp 更合理的读法是：
- 先把它当 standalone binary strategy；
- 再测试 Polymarket price / odds 是否能反向做成 crypto perp 的外部 gate。

## 6. 最小可复现实验（先做什么）
### 实验 A：纯复制 repo 的最小 paper 版（优先级最高）
目标：先验证 **不靠 AI** 的 final-window lag arb 有没有正向 expectancy。

#### 数据
- Binance WebSocket：BTC / ETH 秒级 mid / trade direction
- Polymarket Gamma API：活跃 `5m/15m` BTC/ETH recurring markets
- Polymarket CLOB：YES/NO best bid/ask + depth
- 可选：Chainlink RTDS 作第二价格源确认

#### 规则（先别发明新东西）
- 只做 `5m` 和 `15m`
- 只在到期前 `120s → 3s` 窗口看信号
- 先不用 AI filter
- 先用 repo 默认阈值：
  - `min_edge_pct = 1.2`
  - `lag_threshold_pct = 1.5`
  - `confidence_threshold = 40`
- 先分开统计 maker 与 taker
- 先把 `BTC_UP / ETH_UP / BTC_DOWN / ETH_DOWN` 全量记录，不要太早只留子集

#### 指标
- 交易数 / 日
- maker fill rate
- gross edge vs realized PnL
- 按剩余时间 bucket（120-90 / 90-60 / 60-30 / 30-3）分层
- 按 edge bucket（1.2-2 / 2-3 / 3-6 / 6+）分层
- 5m vs 15m 分层

### 实验 B：把它转成我们 desk 的 transfer test
目标：判断 Polymarket lag 是否能反过来当 crypto 短周期外部确认。

做法：
- 当 Binance 出现 10s/30s 短冲击后，记录 Polymarket odds 在未来 `30s / 60s / 120s` 是否补涨/补跌；
- 再看 **Polymarket 没跟上** 的时刻，Binance perp 自己后续 `1m/3m/5m` 是否还有余波；
- 如果 leader move 已完全 price in，则这条材料只适合做 binary；
- 如果 binary lag 同时对应 perp 上的二次延续，则可以升级成 external confirmation feed。

## 7. 这轮研究后，我会怎么排优先级
### 值得马上做
1. **final-window lag arb paper logger**
2. **maker fill-rate / depth / edge decay 统计**
3. **5m vs 15m 分组**
4. **禁用 AI 的纯规则版复现**

### 先别急着做
1. AI ensemble filter
2. event scanner
3. politics / sports 非 crypto 事件市场
4. 大量 live 参数优化

原因很简单：

> **当前最需要回答的，不是“AI 能不能再多加 3% 胜率”，而是“base alpha 在扣完真实执行以后，到底还有没有边”。**

## 8. 一页结论
如果只留一句：

> **这份 2026 新 repo 真正该 intake 的不是 AI，而是一条完整、可直接 paper trade 的 `5m/15m` raw alpha：Binance 先动、Polymarket final-window 赔率后动，用 maker-first 的方式去吃 hard-expiry binary 的 lag-repair。**

对当前 desk 的意义：
- 它是 **独立可交易** 的完整策略，不只是 filter；
- 频率天然就是 `5m/15m`；
- 还能给我们补一类当前素材池里较少的 cross-market / hard-expiry relative-value 视角；
- 但第一轮一定要 **关掉 AI、先测 base alpha**，否则很容易把 overlay 当成本体。

## 9. 来源与链接
### 主来源（repo）
1. **andiyusanto (2026)**, *Polymarket Latency Arbitrage Bot (v5)*, GitHub repository  
   - Readable URL: <https://github.com/andiyusanto/opus-clude-polymarket-arbitrage-bot>  
   - Repo URL: <https://github.com/andiyusanto/opus-clude-polymarket-arbitrage-bot>  
   - 关键文件：
     - <https://raw.githubusercontent.com/andiyusanto/opus-clude-polymarket-arbitrage-bot/main/README.md>
     - <https://raw.githubusercontent.com/andiyusanto/opus-clude-polymarket-arbitrage-bot/main/config.py>
     - <https://raw.githubusercontent.com/andiyusanto/opus-clude-polymarket-arbitrage-bot/main/signal_engine.py>
     - <https://raw.githubusercontent.com/andiyusanto/opus-clude-polymarket-arbitrage-bot/main/risk.py>
     - <https://raw.githubusercontent.com/andiyusanto/opus-clude-polymarket-arbitrage-bot/main/executor.py>
     - <https://raw.githubusercontent.com/andiyusanto/opus-clude-polymarket-arbitrage-bot/main/analyze.py>

### 公共数据 / 接口路径
2. **Polymarket CLOB API**  
   - <https://clob.polymarket.com>
3. **Polymarket Gamma API**  
   - <https://gamma-api.polymarket.com/events>
4. **Binance market data streams**  
   - <https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams>
5. **Chainlink Data Streams / RTDS（repo 对齐用）**  
   - <https://docs.chain.link/data-streams>
