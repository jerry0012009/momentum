# 别把这份 multi-pair crypto trader 只读成“多币机器人”：对 short-cycle desk，更该先测的是「watchlist top-score rotation × oversold-in-uptrend resumption」这条 raw alpha 壳——但 Binance perp 迁移版明显不过成本线

- 时间：2026-04-13 20:44 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `ARCHITECTURE.md` + `simple_multi_bot.py` + `multi_pair_portfolio_trader_v5.py`）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题标签：raw-alpha/cross-sectional/rotation/single-asset/trend/pullback-resumption/rsi/ema/volume/watchlist/top-score/long-only/kucoin/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：源码规则 + 近六周公共数据 portability probe + desk-level strategy reframing

- 主题类型：raw alpha
- 基础 alpha：**单币层面做的是「超卖回踩后、仍处短期上行结构中的 resumption long」；组合层面做的是「在多币 watchlist 里，只持有 top-score 的机会」；也就是 `per-asset pullback-resumption alpha × cross-asset top-score rotation`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = oversold pullback inside short-term uptrend, then rotate into the strongest watchlist names.**

不是“多开几个币就更稳”。
也不是“机器人并发扫描=alpha”。
更不是把 `portfolio bot` 这层工程壳误读成策略本体。

repo 里真正能被 desk 拆出来的，是一条两层结构：

1. **单币 alpha：** `RSI(14) 超卖 + EMA9 > EMA21 + volume spike`，赌的是**上升结构内的回踩恢复**；
2. **组合壳：** 当很多币同时出现候选时，**按 score 排名，只拿 top-N**，把“单币无聊期”转成“watchlist 轮动”。

翻成人话：
- 单个币上，它本质上不是 breakout，而是 **顺势里的 pullback-resumption**；
- 多币层面，它不是 pair/stat-arb，而是 **opportunity routing / top-score rotation**。

所以这轮我把它归到 **raw alpha 壳**，但不是完整策略：
> **alpha 本体是单币 resumption；rotation 只是放大候选覆盖面。**

## 2. 这次看了什么

### 主来源（repo）
- **Author / Owner：** GitHub owner `Everaldtah`
- **Year：** 2026
- **Title：** *Multi-Pair Crypto Trading Bot*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/Everaldtah/multi-pair-crypto-trader>
- **Repo URL：** <https://github.com/Everaldtah/multi-pair-crypto-trader>
- **Repo 描述：** `Multi-pair cryptocurrency trading bot for KuCoin`
- **本轮 shallow clone 可见最新提交：** `Hermes Bot | Mon Apr 13 11:56:24 2026 +0000 | Initial commit: multi-pair crypto trading bot system`

### 本轮直接审的关键文件
- `README.md`
- `ARCHITECTURE.md`
- `simple_multi_bot.py`
- `multi_pair_portfolio_trader_v5.py`

### 本轮自建 probe 产物
- 脚本：`reports/artifacts/quant_digests/2026-04-13_multi_pair_watchlist_rotation_probe.py`
- 汇总：`reports/artifacts/quant_digests/multi_pair_watchlist_rotation_probe_summary_2026-04-13.json`
- 明细：`reports/artifacts/quant_digests/multi_pair_watchlist_rotation_probe_detail_2026-04-13.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 真正有用的不是“多币同时跑”这层工程感，而是 `oversold-in-uptrend resumption` 这条单币 raw alpha + `watchlist top-score rotation` 这层组合壳；但我把它迁到 Binance majors perp 后，`15m` 和 `5m` 都明显不过成本线。**

### 一句话证明方式
> **证明不靠 README 自述，而靠源码阈值本身：`simple_multi_bot.py` 里 entry score 是 `0.5 + RSI<30 ? +0.2 : 0 + EMA9>EMA21 ? ±0.15 + volume_ratio>1.5 ? +0.1 : 0`，`score>=0.7` 才买；我按 repo 默认 `TP=+3% / SL=-1.5% / max_positions sweep / next-bar-open entry` 把它迁到 Binance USDⓈ-M 八个 majors 的 `15m/5m` 数据上，结果 `15m` 主口径 `207` 笔、单笔平均净收益 `-22.9 bps`，`5m` 主口径 `252` 笔、单笔平均净收益 `-28.1 bps`，而且几乎全靠止盈/止损出场，说明 alpha 本体还不够硬。**

## 4. 为什么这轮值得写

因为它补的是池子里相对少的一种原型：

1. **不是传统 pairs / basis / funding。**
   - 它提供的是一种 **跨 watchlist 的机会路由壳**；
   - 能回答“当单一币种没机会时，是否该去别的币上找同一类信号”。

2. **不是纯 filter / overlay。**
   - 单币那条 `RSI + EMA + volume` 是可以独立下单的；
   - 组合层只是排序和容量控制，不是本体。

3. **和今天那篇单币 RSI 壳不完全一回事。**
   - 那篇更像“单资产趋势跟随壳”；
   - 这份 repo 更像“单币 resumption + watchlist rotation 选机会”。

所以它虽然没过线，但仍值得进研究池：
> **不是为了立刻实盘，而是为了把“单币信号 × 跨币路由”这类架构拆开看清楚。**

## 5. repo 真正提供了什么

## 5.1 `simple_multi_bot.py`：核心不是并发，而是一个很朴素的 3 因子打分器
源码里最关键的不是 asyncio，而是下面这组规则：

- 初始分：`0.5`
- `RSI < 30`：`+0.2`
- `RSI > 70`：`-0.2`
- `EMA9 > EMA21`：`+0.15`，反之 `-0.15`
- `volume_ratio > 1.5`：`+0.1`
- `score >= 0.7`：`BUY`
- `score <= 0.3`：`SELL`

注意这里的设计语言：
- **RSI** 负责找回踩；
- **EMA** 负责保证不是纯左侧抄底；
- **volume** 负责确认恢复不是死猫弹。

这已经是一条清楚的 raw alpha 壳，不只是机器人工程。

## 5.2 `README.md` / `ARCHITECTURE.md`：repo 想表达的是“单币会无聊，所以要 watchlist 轮动”
repo 的叙事很明确：

- 单币（尤其 ETH）会进入 chop zone；
- bot 不想在一个无聊币上反复被噪音打；
- 所以把同一套规则铺到 12 个币上，按 score 选更强机会。

翻成人话：
> **它不是先发明了更好的 alpha，而是先发明了更大的候选池。**

这点对 desk 很重要，因为很多 bot 的问题根本不是 entry rule 不会写，而是：
- 候选太少；
- 只盯一个币；
- 一旦那个币没 trend，系统就闲死。

## 5.3 `multi_pair_portfolio_trader_v5.py`：v5 增加了很多壳，但 alpha 核心没变强多少
v5 加了：
- MFI / MACD / Bollinger / SuperTrend / ADX
- correlation filter
- ATR sizing
- rebalance
- market regime

但从 desk 视角，最需要先拆开的不是这些“大而全”组件，而是：

1. **entry alpha 到底是什么？**
2. **rotation 是否真的比单币更有效？**
3. **成本后还能不能活？**

如果这三件事先答不清，后面的相关性过滤、Kelly、再平衡都只是精装修。

## 6. 我做的 Binance public-data portability probe

## 6.1 数据与口径
- **数据源：** Binance USDⓈ-M public `/fapi/v1/klines`
- **公开性：** 完全公开，无需 key
- **频率：** `15m` 与 `5m`
- **样本区间：** `2026-03-01 00:00 UTC` 到 `2026-04-13 20:00 UTC`
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT / LINKUSDT / AVAXUSDT / DOTUSDT / ADAUSDT / DOGEUSDT`
- **最小实验：**
  - 用 repo 的核心 3 因子打分；
  - `score >= 0.7` 在下一根开盘做多；
  - 出场：`+3% take profit`、`-1.5% stop loss` 或 `score <= 0.3`；
  - 成本假设：单边 `4 bps fee + 2 bps slippage`；
  - 主口径先看 `max_positions = 3`，再做容量 sweep：`1 / 2 / 3 / 5`。

### 一个重要提醒
这不是在复刻 KuCoin live bot 的全部实现；
而是在问一个更 desk 的问题：
> **把这条 alpha 壳搬到 Binance 短周期 perp 上，它到底有没有 first verdict 的生存性？**

## 6.2 先记最重要的 6 个数

### 数 1：`15m` 主口径不过线
`15m`, `max_positions=3`：
- 交易数：`207`
- 胜率：`30.9%`
- 单笔平均净收益：`-22.9 bps`
- 总净收益：`-4734 bps`
- 平均持有：`41.0 bars`（约 `10.3h`）

这不是“略差一点”，而是：
> **repo 这套信号直接迁过来，在 `15m` 上明显不够覆盖成本。**

### 数 2：`5m` 更差，不是更快就更好
`5m`, `max_positions=3`：
- 交易数：`252`
- 胜率：`29.8%`
- 单笔平均净收益：`-28.1 bps`
- 总净收益：`-7074 bps`
- 平均持有：`125.3 bars`（约 `10.4h`）

注意这个持有时间很关键：
- 虽然信号在 `5m` 上触发；
- 但真正的持仓并没有变成短打；
- 反而只是把噪音采样频率变高了。

### 数 3：容量放大不能把负 alpha 变正
容量 sweep：

#### `15m`
- `max_pos=1`：`83` 笔，单笔 `-37.3 bps`
- `max_pos=2`：`145` 笔，单笔 `-31.7 bps`
- `max_pos=3`：`207` 笔，单笔 `-22.9 bps`
- `max_pos=5`：`319` 笔，单笔 `-18.1 bps`

#### `5m`
- `max_pos=1`：`91` 笔，单笔 `-28.5 bps`
- `max_pos=2`：`171` 笔，单笔 `-30.4 bps`
- `max_pos=3`：`252` 笔，单笔 `-28.1 bps`
- `max_pos=5`：`394` 笔，单笔 `-22.7 bps`

结论不是“开更多仓就更好”，而是：
> **rotation 能分散一点单币噪音，但救不了本体信号太弱。**

### 数 4：sell signal 基本没发挥作用
主口径里：
- `15m sell_frac = 0.0`
- `5m sell_frac = 0.0`

也就是说，绝大多数仓位不是靠“信号翻空”退出，
而是靠：
- `TP`
- `SL`

这很说明问题：
> **当前 score 更像 entry gate，不像闭环状态机。**

## 6.3 分币看，不是全军覆没，但也不是稳稳可迁移

### `15m` 主口径里还有正 pocket
- `DOGEUSDT`：`29` 笔，均值 `+39.7 bps`
- `ETHUSDT`：`31` 笔，均值 `+12.2 bps`
- `BTCUSDT`：`20` 笔，均值 `+18.0 bps`

### 但负 pocket 更大
- `SOLUSDT`：`39` 笔，均值 `-69.7 bps`
- `AVAXUSDT`：`18` 笔，均值 `-87.0 bps`
- `DOTUSDT`：`31` 笔，均值 `-45.9 bps`

### `5m` 也只有局部正 pocket
- `AVAXUSDT`：`25` 笔，均值 `+18.0 bps`
- `ETHUSDT`：`37` 笔，均值 `+8.3 bps`

但：
- `ADA / SOL / LINK / DOT` 全都比较差。

这说明最合理的读法不是“这策略废了”，而是：
> **它更像少数标的 pocket 才成立，不能拿广谱 watchlist 直接平推。**

## 7. 这条线对 short-cycle desk 的正确读法

## 7.1 它是 raw alpha 壳，但不是可直接上线的完整策略
因为它已经回答了：
- 什么时候进：`oversold + trend intact + volume confirms`
- 进什么：`watchlist 里 score 更高的币`
- 怎么退：`TP / SL / sell signal`

但它还没回答清楚：
- 成本后哪些币值得保留
- short side 要不要做
- regime 下该不该开机
- capacity / correlation 真正怎么压

所以最稳妥的分类是：
> **可独立复现的 raw alpha 壳；但还不是能直接实盘的完整策略。**

## 7.2 rotation 不是 alpha，本体还是单币 signal
这个 repo 最容易被误读的地方就是：
- 看到 multi-pair，就以为优势来自“组合神奇”；
- 但 probe 已经说明，**组合只能缓冲，不能造 alpha**。

真正决定成败的还是：
- `RSI<30` 在 crypto perp 上是不是太死；
- `EMA9>EMA21` 对短周期来说是不是太松；
- `volume>1.5x` 是否真的能识别恢复而非脉冲尾声。

## 7.3 更适合 desk 的迁移方向
如果真要继续，最合理的迁移不是照抄，而是：

1. **保留 watchlist routing 这个想法；**
2. **重写单币 alpha 本体；**
3. **只把成本后为正的币种收入候选池。**

也就是：
> **把它当“机会路由器模板”，不要当“信号已验证模板”。**

## 8. 对当前 `1m/3m/5m/15m` 研发的直接价值

### 有价值的部分
1. **watchlist routing 这层值得保留**
   - 可以服务于别的 raw alpha：
     - breakout
     - OFI
     - pairs residual fade
     - funding/basis pocket

2. **简单 3 因子打分的表达方式很清楚**
   - 容易做 admission card
   - 容易替换内部组件

3. **源码里的 portfolio shell 能启发后续架构**
   - top-score ranking
   - max-position gating
   - correlation veto
   - ATR sizing

### 没过线的部分
1. **广谱 majors 直接平推不行**
2. **`5m` 不是天然更强，只是更吵**
3. **sell 阈值没有形成真正闭环**

## 9. 下一步怎么测

按优先级，我会建议这样推进：

### 方案 A：先把“币种录取线”做好
只保留近样本成本后为正的 pocket：
- `15m` 先看 `BTC / ETH / DOGE`
- `5m` 先看 `ETH / AVAX`

再重跑：
- OOS split
- rolling window
- friction ladder（`4/6/8/10 bps` 单边）

### 方案 B：把死阈值 RSI 改成更 desk-friendly 的 pullback 定义
可替换为：
- `zscore pullback in intact trend`
- `EMA band overshoot + recovery`
- `short-term drawdown percentile + trend filter`

因为当前 `RSI<30` 在 perpetual 上太像“接 falling knife 的弱版”。

### 方案 C：把 entry 和 exit 拆开重做
当前 exit 几乎只靠 TP/SL，说明 `score<=0.3` 不够工作。

优先测试：
- time stop（`8h / 12h`）
- trailing stop
- trend-break exit（如 `EMA9<EMA21`）
- volume-failure exit

### 方案 D：让 rotation 服务于更强的 alpha，而不是反过来
也就是：
- 不把这个 repo 当最终策略；
- 而是把它的 watchlist ranking / top-N allocation，拿去服务更强的单币 alpha。

## 10. 最后一句话

> **这份 repo 值得收下的不是“多币 bot”这个外壳，而是“单币 resumption alpha 可以通过 watchlist top-score routing 提高候选覆盖”这个研究框架；但当前这套 `RSI<30 + EMA9>EMA21 + volume spike` 直译到 Binance short-cycle perp，结论很明确：还不够硬。**
