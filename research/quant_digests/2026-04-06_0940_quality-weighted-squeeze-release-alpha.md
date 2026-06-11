# 别把这份 2026 Coinbase squeeze repo 只读成“TTM Squeeze 教程”：对 short-cycle desk，更该先测的是「quality-weighted squeeze release × ATR-defined R shell」这条完整 raw alpha

- 时间：2026-04-06 09:40 UTC
- 类型：2026 GitHub repo source audit（GitHub API metadata + `README.md` + `run_backtest.py` + `strategy/technical.py` + `strategy/signal_generator.py` + `core/backtester.py` + `results/params_library.csv`）
- 主题类型：raw alpha
- 基础 alpha：**压缩结束后的方向性扩张会延续一段；更适合我们 desk 的不是“squeeze 存在”本身，而是把 `squeeze duration × volume × momentum` 写成入场与仓位评分，再配 `ATR stop / ATR target / trailing stop` 做成完整 continuation 壳**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/breakout/squeeze-release/bollinger-band/keltner-channel/volume-confirmation/quality-weighted-sizing/atr-stop/trailing-stop/continuation/coinbase/perpetual/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：仓库源码直读（规则、执行、成本、仓位、风控都已落到代码）

## 1. 这次看了什么
这轮主看 **jicheolha (2026) 的 GitHub repo `keltrader`**。它不是那种只给几张 equity curve、却不肯把规则写清楚的仓库；相反，源码里已经把下面几层都写出来了：

1. **setup 定义**：`BB inside KC` 压缩结束；
2. **方向判断**：突破 band，或者至少 momentum 与释放方向一致；
3. **确认层**：`volume_ratio` 和 `RSI` veto；
4. **仓位层**：`squeeze duration × volume × momentum` 组合成 signal quality，再映射到仓位；
5. **执行层**：next-bar open 入场，显式计入手续费与 slippage；
6. **风险层**：`ATR stop / ATR target / 1R 后 trailing stop / 连亏后降仓`。

README 给的 headline 回测也足够具体：
- 样本：`DOGE / ETH / SOL / XRP`
- 区间：`2021-01-01` 到 `2025-12-28`
- 结果：`+177%` return、`158` 笔、`58%` 胜率、`1.75` profit factor、`20%` max drawdown

我不会直接信这个收益，但它至少说明：**这不是“只会画图的 squeeze 指标仓库”，而是一个已经把完整策略骨架写出来的 repo。**

## 2. 先回答：这篇东西的 base alpha 是什么？
- 主题类型：raw alpha
- 基础 alpha：**compression release continuation**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

一句话翻成人话：
> 市场先收窄、再放大时，第一段放大量并不一定立刻结束；如果这次 release 伴随更长压缩、更高成交量、更强方向动量，那么顺着 release 方向跟一小段，往往比把所有 squeeze 都一视同仁更有交易价值。

这里最关键的是：
**repo 真正值钱的不是“TTM Squeeze 有效”这句老话，而是它把“哪种 squeeze 值得做大、哪种只配轻仓”写成了一个可执行评分器。**

## 3. 为什么这轮值得进研究池
这轮仍然值得写，原因不是“我们又发现了一个 breakout 形态”，而是它补了一个当前素材池里还不够扎实的空位：

1. **它是完整策略壳，不只是 shape。**  
   最近我们已经收过不少 raw alpha，但很多还停在“信号像不像有用”。这份 repo 往前多走了一步：把 admission、sizing、risk、execution 都写成代码了。

2. **它和 3 月底那篇“bottom-quartile BB compression breakout”不是同一件事。**  
   那篇更像在问：**压缩突破本体有没有 alpha？**  
   这份 repo 更像在问：**同样是压缩释放，哪些应该重仓，哪些应该轻仓甚至跳过？**

3. **它对 `1m / 3m / 5m / 15m` 非常友好。**  
   因为所需输入只有公开 OHLCV，不依赖 funding、L2、链上或私有特征；最小实验可以非常快地在 Binance / Hyperliquid / Coinbase 公共 bar 数据上重做。

## 4. 源码里真正写了什么

### 4.1 setup：压缩结束，不是压缩期间乱开仓
`strategy/technical.py` 里，压缩的定义非常标准：
- `BB(20, 2.0)`
- `KC(20, 1.5 × ATR)`
- 当 `BB_Lower > KC_Lower` 且 `BB_Upper < KC_Upper` 时记作 `Squeeze = True`

真正触发 setup 的条件不是“正在 squeeze”，而是：
- 前一根还在 squeeze；
- 当前这根刚 release；
- 且前面这段 squeeze 至少持续 `min_squeeze_bars`。

默认 `min_squeeze_bars = 3`。这点很重要，因为它明确避免了把“仍在压缩里的噪声震荡”误当成可交易 breakout。

### 4.2 方向：先看 band 突破，不够清楚再看 momentum
`detect_breakout()` 的顺序是：
- 若当前 `close > BB_Upper` → long
- 若当前 `close < BB_Lower` → short
- 否则退回到 `Momentum_Norm` 的符号

其中：
- `Momentum = close - BB_Mid.shift(momentum_period)`
- `Momentum_Norm = Momentum / ATR`
- 默认 `momentum_period = 12`

也就是说，它不是纯粹“上轨外就是做多”，而是给了一个 **band break > normalized momentum** 的双层方向判定。

### 4.3 admission：volume 和 RSI 不是主信号，而是确认/否决
默认 admission 参数：
- `min_volume_ratio = 1.2`
- `RSI overbought = 75`
- `RSI oversold = 25`

翻译一下：
- 没量的 release，不给过；
- long 侧如果已经非常 overbought，不追；
- short 侧如果已经非常 oversold，不追。

这对 short-cycle 很实用，因为它把最常见的两个假突破来源——**无量 release** 和 **极端末端追价**——先挡掉一层。

### 4.4 sizing：repo 最值得偷的地方是 quality-weighted position size
`strategy/signal_generator.py` 里最有意思的是这个 signal quality：
- `40%` 权重给 squeeze 持续时间
- `35%` 权重给 volume ratio
- `25%` 权重给 normalized momentum

而且不是线性打分，而是 **exponential diminishing returns**：
- 刚刚超过阈值时，只给低分；
- 超得越多，分数继续上升，但边际收益递减；
- 再把这个 quality 从 `base_position=10%` 映射到 `max_position=30%`。

另外它还有一条很 desk-friendly 的规则：
- 若最近连续亏损，则仓位乘上 `0.85 ^ losses`

这就把“压缩释放后容易连错几次”的现实，直接写进了仓位退火逻辑。

### 4.5 exit / cost：next-bar open + ATR R-multiple，比很多 repo 诚实
`run_backtest.py` 与 `core/backtester.py` 给了几条关键细节：
- 默认 `trade timeframe = 1min`
- 默认 `signal timeframe = 2h`
- **next-bar open** 才入场，不偷看 signal bar close
- `commission = 5 bps`
- `slippage = 2 bps`
- `ATR stop = 2.0`
- `ATR target = 3.0`
- `trail_trigger_r = 1.0`，即走出 `1R` 后才启动 trailing

而 trailing 也不是胡乱追：
- 先到 `1R` 才激活；
- long 侧 stop 不许再回到 break-even 以下；
- short 侧对称处理。

所以这不是“看到突破，凭感觉拿一拿”的系统，而是已经把 **收益目标、止损、持仓续拿、成本** 一起写清了。

## 5. desk 版最该怎么改，不要机械照搬
repo 默认是：
- `2h` 信号
- `1m` 执行
- Coinbase spot price 生成信号，再去 perpetual 执行

这对我们不是问题，因为真正可迁移的不是交易所，而是策略结构。

### 5.1 15m 主版本
建议先做一个最像 desk 的版本：
- universe：`BTC / ETH / SOL / XRP` 或 top liquid majors
- signal TF：`15m`
- execution TF：`1m`
- squeeze bars：`3 / 6 / 9`
- volume ratio：`1.1 / 1.3 / 1.5`
- stop / target：`1.5 / 2.0 / 2.5 ATR` vs `2.0 / 3.0 / 3.5 ATR`

最关键的 ablation 不是“band 该不该用 2.0”，而是：
1. **equal-size vs quality-weighted-size**
2. **无量不过 vs 直接做**
3. **只固定 TP/SL vs 加 `1R trailing`**

### 5.2 5m 快版本
`5m` 版本可以更激进，但建议只保留一套轻量 admission：
- 继续用 `squeeze release`
- 继续用 `volume_ratio`
- 先不要在第一版里叠太多 trend EMA / regime filter

否则很容易把它做成“信号本体弱，只能靠很多 filter 才勉强存活”的伪 raw alpha。

### 5.3 1m / 3m 的角色
`1m / 3m` 更适合做：
- child execution
- next-bar open / pullback entry 优化
- trailing / stop precision

不建议一开始就把 alpha body 下沉到 `1m`，因为 squeeze release 在这个尺度上更容易被纯 microstructure 噪声打碎。

## 6. 最小实验怎么做
这轮最值得马上跑的，不是全资产大优化，而是一个 **三步最小实验**：

### 实验 A：alpha 本体有没有东西
在 `15m` 上测试：
- 条件：`prev squeeze = 1`, `curr squeeze = 0`, `squeeze_bars >= k`, `volume_ratio >= v`
- long/short 都做
- entry：next bar open
- exit：`2 ATR stop / 3 ATR target`
- cost：双边 `4~6 bps` + 1 tick slippage

先看：
- net profit factor
- expectancy / trade
- avg hold bars
- breakout 后前 `3/6/12` 根的 path drift

### 实验 B：quality-weighted size 到底有没有增量
在实验 A 通过后，只比较两件事：
1. `equal-risk fixed size`
2. repo 这套 `quality-weighted size`

如果 quality sizing 只是把回撤放大，却没提高 net PF / Sharpe / skew，那它就该降级成 overlay，而不是策略核心。

### 实验 C：1R trailing 是不是核心组件
再做三路对照：
- 固定 `SL/TP`
- `SL/TP + 1R trailing`
- 只 trailing、不设固定 TP

这个实验会直接告诉我们：
**这条 alpha 是赚在第一段脉冲，还是赚在后续延续。**

## 7. 我对这条线的判断
我的判断是：

1. **它值得进池，但先别迷信 README 的 +177%。**  
   那个结果很可能包含样本期 / 参数搜索 / 资产选择偏差。

2. **真正可能可迁移到 desk 的，不是具体参数，而是结构。**  
   尤其是：
   - release 才触发
   - volume-confirm
   - quality-weighted sizing
   - next-bar-open honesty
   - `1R` 后再 trailing

3. **如果第一轮最小实验失败，最值得保留的残部依然是 quality scoring。**  
   换句话说，就算这条 raw alpha 本体最后不够强，`squeeze duration × volume × momentum` 这套 admission / sizing 评分器，仍可能服务别的 breakout / trend 线。

## 8. 下一步怎么测
按优先级我会建议：

1. **先跑 `15m signal + 1m execution` 的单币 majors 版本**  
   这是最接近当前 desk 的主战场，也最容易诚实计成本。

2. **先做 ablation，不要先做大优化**  
   重点比较：
   - 有无 `volume_ratio` gate
   - fixed size vs quality size
   - 有无 `1R trailing`

3. **若 `15m` 成立，再下沉到 `5m`**  
   不要反过来；否则很容易在更高噪声里误判 alpha 死活。

4. **若 `5m` 也成立，再把 `1m / 3m` 留给 execution layer**  
   不要把 `1m` 直接神化成 alpha 主体。

## 9. 公开数据、公开性与最小复现实验口径
这条线的数据要求很简单：
- **数据源**：公开 OHLCV（repo 原生使用 Coinbase Advanced Trade API）
- **公开性**：公开可得
- **更新频率**：按 bar close 更新，可直接拿 `1m / 5m / 15m`
- **最小可复现实验**：只需要 `open/high/low/close/volume`

这点非常适合当前 intake：
- 不需要 funding
- 不需要 order book
- 不需要链上
- 不需要私有成交数据

也因此，它是一个很好的 **快复现、快打分、快淘汰** 原型。

## 10. 来源
1. **jicheolha (2026), `keltrader`**  
   - Type: GitHub repository  
   - Venue: GitHub  
   - DOI: None  
   - Readable URL: <https://github.com/jicheolha/keltrader>  
   - Repo URL: <https://github.com/jicheolha/keltrader>  
   - GitHub metadata: created `2026-03-05`, updated `2026-04-01`

2. **Repo README**  
   - Raw URL: <https://raw.githubusercontent.com/jicheolha/keltrader/main/README.md>

3. **Backtest runner**  
   - Raw URL: <https://raw.githubusercontent.com/jicheolha/keltrader/main/run_backtest.py>

4. **Signal logic**  
   - Raw URL: <https://raw.githubusercontent.com/jicheolha/keltrader/main/strategy/signal_generator.py>

5. **Technical indicators / squeeze detection**  
   - Raw URL: <https://raw.githubusercontent.com/jicheolha/keltrader/main/strategy/technical.py>

6. **Backtester / execution / trailing stop**  
   - Raw URL: <https://raw.githubusercontent.com/jicheolha/keltrader/main/core/backtester.py>

7. **Optimization result library**  
   - Raw URL: <https://raw.githubusercontent.com/jicheolha/keltrader/main/results/params_library.csv>
