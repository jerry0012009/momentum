# 别把这份 2026 大而全交易引擎只读成“volume profile 教学模块”：对 short-cycle desk，更该先拆的是「value-area 回归 × LVN 穿越」这条完整 raw alpha 壳
- 时间：2026-04-18 00:49 UTC
- 类型：2026 GitHub repo source audit（GitHub API metadata + `README.md` + `src/strategies/volume_profile.py`）
- 主题类型：raw alpha
- 基础 alpha：拍卖式均衡回归——价格脱离当期成交最密集区（Value Area / POC）后，倾向回到“成交最拥挤的公平价”；而穿越低成交空洞（LVN）时，倾向快速滑向下一块成交密集区
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/auction-market/volume-profile/poc/value-area/lvn/mean-reversion/breakout-shell/vwap/atr/5m/15m/repo/public-data/cost/risk
- 证据类型：源码规则

## 1. 这次看了什么
看了 **mefai-dev (2026)** 的 GitHub repo **Mefai Autotrade**，重点不是它 README 里那堆“20+ strategies”，而是源码里的 `src/strategies/volume_profile.py`。这个模块已经把一条可直接落地的短周期策略壳写得很完整：
- 用最近一段 session K 线重建 volume profile；
- 算 `POC`（成交最密集价）、`VAH/VAL`（70% 成交价值区上下沿）、`HVN/LVN`（高/低成交节点）；
- 给出 3 类 entry：`POC bounce`、`value-area edge re-entry`、`LVN breakout`；
- exit / sizing / risk 也不是空着：`POC/VA` 目标位、`ATR stop`、`risk_pct` 仓位归一都在源码里。

repo 元数据也说明它是很新的仓：创建于 **2026-03-25**，最近一次 push 在 **2026-04-08**。

## 2. 先回答：base alpha 是什么？
**base alpha 很清楚：不是泛“技术分析确认层”，而是 auction-market 里的两段式 raw alpha。**

更直白地说：
1. **回归腿**：价格跑出价值区后，如果又回到 `VAH/VAL` 内，往往会继续朝 `POC` 这个“最拥挤成交价”回归；
2. **穿越腿**：如果价格穿过 `LVN` 这种低成交真空带，往往会更快滑向下一块有成交承接的区域。

所以它不是单纯 mean reversion，也不是单纯 breakout，而是一个很适合 desk 的**“拍卖结构路由器”**：
- 在 value edge 上更像 **fade / reversion**；
- 在 LVN 上更像 **acceptance breakout / fast traverse**。

这比继续写一篇泛 BB/RSI/EMA 壳更值钱，因为当前索引里几乎还没有把 **volume profile / auction structure** 当成主主题展开。

## 3. 源码里真正有价值的策略骨架
### 3.1 Profile 怎么建
源码用最近 `session_bars` 根 K 线建 profile，默认：
- `num_bins = 50`
- `value_area_pct = 70%`
- `session_bars = 288`（正好对应 `288 x 5m = 1` 天）

实现上不是 tick 级真 profile，而是把每根 bar 的成交量均匀分摊到其覆盖的价格 bins。这个做法不完美，但**对 5m/15m 最小实验已经够诚实**，因为它只需要公开 OHLCV 就能复刻。

### 3.2 三类 entry 已经写死在源码里
**(a) POC bounce**
- 若现价离 `POC` 足够近（默认 `0.1%` 内），
- 现价在 `POC` 下方就做多，在 `POC` 上方就做空。

这条最像“围绕公平价的短距回归”。

**(b) Value-area edge re-entry**
- 上一根还在 `VAH` 外、这一根重新回到 `VAH` 内：做空；
- 上一根还在 `VAL` 外、这一根重新回到 `VAL` 内：做多。

翻成人话：**价格试图逃离高成交区，但又没逃出去，回到价值区时，先按失败逃逸处理。**

**(c) LVN breakout / traverse**
- 从下往上穿过 `LVN` 中部：做多；
- 从上往下穿过 `LVN` 中部：做空。

这条不是“突破就追”那么粗糙，本质更像：**低成交区像空气层，价格一旦进去，容易更快滑向下一块有成交承接的区域。**

### 3.3 exit / sizing / risk 不是空白
源码里的完整壳：
- **止盈**：优先回到 `POC`；若方向关系不合，就退到 `VAH/VAL`
- **止损**：`ATR stop`，默认 `atr_stop_mult = 1.5`
- **仓位**：`calculate_position_size(account_balance, entry, stop, risk_pct)`
- **风险预算**：默认 `risk_pct = 1.0`
- **附加上下文**：signal metadata 里还塞了 `poc / va_high / va_low / vwap / hvn_count / lvn_count`

也就是说，这不是“只有信号没有交易壳”的半成品；它已经满足我们这轮优先级里最重要那条：**可直接落地为完整策略。**

## 4. 为什么这题现在值得进研究池
### 4.1 它补的是当前 digest 池里的一个空白
最近几天已经很密的方向包括：
- order-flow / OBI / CVD
- pairs / cointegration / spread z-score
- funding / basis / carry
- maker / market-making

但 **volume profile / auction structure** 几乎没被作为主 alpha 母板认真展开。这个主题刚好补空位，而且不依赖私有 L2、也不需要 prediction market 外部数据。

### 4.2 对短周期 desk 很友好
它天然适合 `5m/15m`，也能往 `1m/3m` 下钻：
- `5m`：先做 session profile + POC/VA/LVN 母版；
- `15m`：适合做更粗的 acceptance / rejection；
- `1m/3m`：可把 `LVN traverse` 做得更接近 execution-aware routing。

### 4.3 数据门槛低
**最小可复现实验只需要公开 OHLCV。**
- 数据源：Binance spot / USDⓈ-M perpetual klines
- 公开性：公开可得
- 更新频率：1m / 3m / 5m / 15m 都有
- 最小实验口径：session rolling profile + bar-volume binning

这点比很多看起来更“高级”的 microstructure 题更现实。

## 5. 我对这份源码的真实判断
### 5.1 值得抄的是“壳”，不是参数
这份代码最值钱的是**把 auction 结构拆成了 entry/exit/risk 的完整语言**，不是默认参数本身：
- `POC proximity 0.1%`
- `VA proximity 0.15%`
- `50 bins`
- `70% value area`

这些数值大概率都要重标。不同币、不同周期、spot/perp 都不会一样。

### 5.2 最大缺点：profile 还是 bar-based proxy
源码不是逐笔 volume-at-price，而是把整根 bar 的量均匀撒进价格区间。这会带来两个问题：
- 越长周期，profile 越糊；
- 大实体 K 会把并不存在的成交密度“抹平”。

所以这更像**低成本第一版研究母板**，不是最终 production 口径。若最小实验有感觉，下一步就该升级到：
- 用 Binance aggTrades 重建更细的 volume-at-price；或
- 至少在 `1m` 先建 profile，再聚合到 `5m/15m` 做交易。

### 5.3 POC bounce 这条最可疑，VA re-entry / LVN traverse 更值得先测
源码里 `POC bounce` 逻辑非常激进：只要足够接近 `POC`，下方就多、上方就空。这个写法容易在单边趋势里被反复打脸。

相比之下，我觉得更值得优先测的是两条：
1. **VAH/VAL re-entry → POC 回归**
2. **LVN 穿越 → 下一高成交区方向延续**

因为这两条更贴近 auction-market 的“接受/拒绝”叙事，也更容易做出干净的事件定义。

## 6. 面向 desk 的最小实验
### 实验 A：value-area re-entry fade
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT` perpetual
- 周期：先 `5m`，再看 `15m`
- profile：滚动过去 `1d`（288 根 5m）或 `2d`
- 入场：
  - `prev_close > VAH` 且 `close <= VAH` → next bar open short
  - `prev_close < VAL` 且 `close >= VAL` → next bar open long
- 出场：
  - `POC` 止盈
  - `1.5 x ATR` 止损
  - `max holding = 12~24 bars`
- 先看指标：`post-cost expectancy`、`hit rate to POC before stop`

### 实验 B：LVN traverse continuation
- 标的：同上
- 周期：`1m/3m/5m`
- 入场：价格首次穿越最近 session 某个 `LVN midpoint`
- 出场：
  - 下一 `HVN` / `VA edge`
  - 或固定 `1R~1.5R`
- 先看指标：`穿越后 1/3/5 bar MFE`、`反向回抽概率`

### 实验 C：把它当 shared router，而不是单独 alpha
如果 A/B 单独不过线，也值得测：
- 趋势 alpha 只在 **LVN 同向穿越** 时放大仓位；
- 均值回归 alpha 只在 **VA re-entry** 时开仓；
- 一旦价格处于高成交拥挤区中央，统一降权或禁入。

## 7. 风险与保留意见
- **最容易被忽悠的点**：volume profile 看起来很“懂市场结构”，但如果只用 bar-volume proxy，很多漂亮的节点其实是分箱幻觉。
- **趋势市风险**：POC/VA 回归在强趋势里会持续逆势。
- **交易成本风险**：这类策略若频繁在 value edge 来回试单，会被 fee + spread 慢慢磨死。
- **session 定义风险**：crypto 是 24/7，daily session 怎么切，会显著影响 profile 形状。UTC 日切、亚洲/欧洲/美洲 session，都该分别测试。

## 8. 一句话结论
这份 repo 真正值得拿走的，不是“volume profile 很酷”，而是：**它把 auction-market 结构翻译成了一个可直接回测的完整策略壳。** 对当前 short-cycle desk，最该先测的不是 POC 附近瞎抄底摸顶，而是 **`VA re-entry -> POC` 的失败逃逸回归腿**，以及 **`LVN traverse` 的低成交空洞穿越腿**。

## 9. 下一步怎么测
1. **先做 5m Binance perpetual 三币母版**：BTC/ETH/SOL，滚动 1d profile。
2. **把三类 entry 分开回测**：`POC bounce`、`VA re-entry`、`LVN traverse` 不要混在一起。
3. **先看事件级而不是整套净值**：每类事件的 `hit POC / hit next HVN / stop-first` 概率，先判断哪条腿真的有 edge。
4. **再做 session 切法敏感性**：UTC 0 点切日、8 小时 session、24 小时 rolling profile 三种并排。
5. **若 bar-profile 有感觉，再升级到 aggTrades 重建 volume-at-price**，确认 edge 不是分箱假象。

## 10. 来源
- mefai-dev. (2026). *Mefai Autotrade*. GitHub.
- Repo URL: `https://github.com/mefai-dev/mefai-autotrade`
- Readable URL: `https://github.com/mefai-dev/mefai-autotrade/blob/master/src/strategies/volume_profile.py`
- Raw URL: `https://raw.githubusercontent.com/mefai-dev/mefai-autotrade/master/src/strategies/volume_profile.py`
- GitHub API metadata used: repository `created_at=2026-03-25`, `pushed_at=2026-04-08`
