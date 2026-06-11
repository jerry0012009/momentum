# 别把这份 2025/2026 Crypto Strategy Lab 仓库只读成“12 个数学信号拼盘”：对 short-cycle desk，更该先拆的是「True Range 扩张 × 价格动量背离 → 反身性衰竭 fade」这条 raw alpha

- 时间：2026-04-16 00:55 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `docs/STRATEGY_GUIDE.md` + `config/strategies/true_range_divergence.yaml` + `src/strategies/true_range_divergence/signal.py` + GitHub API metadata）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**当单资产短周期里 True Range/波动扩张方向 与 价格动量方向出现背离时，往往代表当前推进已进入“高噪声、低效率、接近衰竭”的阶段；交易上不追随原动量，而是反向做 `fade the momentum`，赌后续几根 bar 的局部均值回归。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（**repo 已给出 entry delay / hold / decay / regime filter，但 sizing / cost / venue friction 还不完整，而且当前源码有配置接线问题，不能直接当 production shell**）
- 主题标签：raw-alpha/single-asset/mean-reversion/volatility-price-divergence/true-range/momentum-divergence/exhaustion-fade/entry-delay/fixed-hold/15m/5m/binance-perpetual/repo/public-data/cost/risk
- 证据类型：repo source + public-data probe

## 1. 这次看了什么

这轮主看的是 GitHub 新仓：

- **Author：** Joel Saucedo
- **Year：** 2025（repo 创建）/ 2026（当前 intake 时间）
- **Title：** *Crypto-Strategy-Lab*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/joel-saucedo/Crypto-Strategy-Lab>
- **Repo URL：** <https://github.com/joel-saucedo/Crypto-Strategy-Lab>
- **Strategy guide：** <https://raw.githubusercontent.com/joel-saucedo/Crypto-Strategy-Lab/main/docs/STRATEGY_GUIDE.md>
- **Signal source：** <https://raw.githubusercontent.com/joel-saucedo/Crypto-Strategy-Lab/main/src/strategies/true_range_divergence/signal.py>
- **Config：** <https://raw.githubusercontent.com/joel-saucedo/Crypto-Strategy-Lab/main/config/strategies/true_range_divergence.yaml>

GitHub API 元数据（抓取时间 2026-04-16 UTC）显示：
- repo 创建于 **2025-05-27**
- 最近更新于 **2026-03-12**
- 当前 star 很少（**7**），所以它不是“社区验证过的大热门模板”，更像一个值得 source audit 的新研究仓

先把一句话说清楚：

> **这篇东西的 base alpha 不是“波动大就反转”，也不是“ATR filter”。它的 alpha 本体是：当 TR 扩张和价格动量不同步时，原方向推进质量在变差，接下来更容易出现短持有窗的反向回摆。**

所以它不是纯 filter，也不是 overlay；它本体就是一条：

> **single-asset / short-horizon / mean-reversion raw alpha。**

## 2. 为什么这题值得进池

我们这几轮已经累积了不少：
- funding / carry / basis
- pairs / cointegration / spread fade
- cross-sectional loser/winner
- lead-lag / catch-up

但**单资产、纯价量内生、又不是老套 RSI/BB 的短周期 mean reversion 母板**其实还可以继续补。

这条 TR-价格背离线有几个优点：

1. **完全不依赖外部数据。**
   - 只要 OHLCV 就能做。
2. **base alpha 很清楚。**
   - 不是“解释市场”，而是直接定义一个可交易失配：`volatility expansion != price momentum direction`。
3. **天然适配 `5m / 15m`。**
   - 它本来就是短持有的 exhaustion / fade 逻辑，不需要硬把日频论文拧成分钟级。
4. **可以服务 desk 的很多变体。**
   - 单资产 fade
   - BTC shock 后 alt 同类信号 veto
   - 做 execution veto：当 TR 爆、但动量质量差时，不追 breakout

所以即便当前 repo 版本还不算完整 production shell，这条母 alpha 本身仍值得进入素材池。

## 3. repo 里到底写了什么

`docs/STRATEGY_GUIDE.md` 对这条策略的摘要非常直接：

- **名称：** True Range Divergence Strategy
- **数学底层：** `TR = max(H-L, |H-C_prev|, |L-C_prev|)`
- **edge 定义：** price-volatility divergence
- **交易意图：** 当波动与价格趋势脱节时，做均值回归

而 `src/strategies/true_range_divergence/signal.py` 里，实际实现可以翻成人话：

1. 先算 **True Range**；
2. 再算 `TR / MA(TR, n)` 得到 **TR 相对强度**；
3. 再算 `Close / MA(Close, n)` 得到 **价格动量**；
4. 用最近一段窗口把两者各分成前半/后半，比较均值变化方向；
5. 如果
   - TR 方向向上、动量方向向下，或
   - TR 方向向下、动量方向向上，
   就视为 **divergence**；
6. 最终信号方向不是跟随动量，而是：
   - **`signal_direction = - momentum_direction`**
   - 也就是**直接 fade 当前动量方向**。

这点非常关键：

> **base alpha 不是“TR 领先价格”，而是“TR 与价格一旦背离，优先假设当前价格推进在衰竭，因此做反向”。**

这就是一个很清楚的 raw alpha，不需要额外借助外部因子才能成立。

## 4. 为什么它比继续看 generic breakout 更有意思

如果只看仓库目录，`wavelet_energy`、`vpin`、`spectral_*` 这些也都挺吸引人。

但对当前 desk 来说，TR divergence 反而更像一个**低门槛、快验证、快否决**的 alpha intake：

- **输入简单：** OHLCV 即可
- **迁移简单：** 直接上 Binance / Hyperliquid / OKX 15m bar 就能 smoke test
- **解释简单：** “波动在吼，但价格走不动/走反了”
- **执行简单：** 1-bar delay + fixed-hold + hard time-stop 就能搭第一版

这比很多“需要 order book / signed flow / wavelet 依赖”的东西更适合作为当下 intake。

## 5. 但 repo 现在还不能直接照抄上线

这里要明确写一句：

> **它是 raw alpha 候选，不是现成 complete shell。**

原因有三个：

### 5.1 配置接线有 bug

`true_range_divergence.yaml` 把参数放在 `strategy.parameters` 下面；
但 `signal.py` 的 `load_config()` 却是直接 `config.get('tr_lookback', 20)` 这种平铺读取。

结果就是：
- YAML 里写的很多参数，源码实际上**读不到**；
- 运行时更接近默认参数，而不是 config 声称的那套值。

### 5.2 有几个关键参数目前根本没被用上

源码里：
- `divergence_threshold`
- `min_tr_strength`
- `max_tr_strength`

虽然在 config/初始化里出现了，但在实际 `generate()` 路径里几乎没起作用。

这意味着当前 repo 版本更像：
- 有 alpha 想法，
- 有 baseline 实现，
- 但还没完成真正严谨的参数化。

### 5.3 sizing / fee / slippage 不是策略模块里自带的

虽然 `STRATEGY_GUIDE.md` 提到 Kelly / VaR / correlation management 等组合级风险框架，
但**这条具体策略的源码本身**只提供了：
- entry delay
- max hold
- signal decay
- volatility regime filter

还没有把：
- cost budget
- maker/taker choice
- position sizing
- liquidation distance
- symbol routing

完整收进这个单策略模块里。

所以我把它判成：
- **可独立复现：是**
- **可直接落地完整策略：否**

## 6. public-data 最小迁移快检：15m first verdict

我按 repo 的核心逻辑，写了一个最小 public-data probe：

- **市场：** Binance USDⓈ-M perpetual
- **周期：** `15m`
- **时间窗：** `2025-10-01 ~ 2026-04-16`
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- **成本：** 单边 `2 bps`
- **实现：** 近似照搬 `signal.py` 的核心 divergence + entry delay + 8-bar hold + decay

artifact 已落在：
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-16_true_range_divergence_probe.py`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-16_true_range_divergence_probe_summary.json`
- 以及各 symbol CSV

### 6.1 结果先说结论

> **这条 alpha 在 15m taker 直译版上，gross 只有个别币还勉强为正；一扣 `2bps` 单边成本后，四个 major 全部转负。**

关键数字：

- **BTCUSDT**：gross `-0.25%`，net `-3.68%`，entries `349`
- **ETHUSDT**：gross `-3.47%`，net `-8.71%`，entries `533`
- **SOLUSDT**：gross `+2.04%`，net `-3.13%`，gross Sharpe `0.91`
- **BNBUSDT**：gross `+0.35%`，net `-3.58%`

另外一个很关键的点：
- **active bar ratio 只有约 `3% ~ 5%`**

这说明它不是那种“全天高频乱打”的东西，而更像一个：
- 触发不算太少，
- 但 edge 很薄，
- 一旦 taker 成本进来就被吃掉的 **event-style fade pocket**。

### 6.2 这不代表主题无效，反而说明该怎么改

这个 first verdict 更像在告诉我们：

1. **alpha 想法成立，但当前 signal plumbing 太粗。**
2. **直译到 15m taker execution 不够。**
3. **它更像需要“更极端事件筛选 + 更低摩擦执行 + 更短确认窗”的候选。**

也就是说，它不是“没价值”，而是：

> **更像 raw alpha 母板，而不是可直接上线的 baseline。**

## 7. 对 short-cycle desk 的正确读法

这条线最容易被误读成：
- “波动上来就反手”

但更准确的 desk 版本应该是：

> **只在 `TR 爆出来了、但价格推进质量已经掉了` 的时刻，做短持有的 exhaustion fade。**

换成更工程化的拆法：

- **alpha 本体：** `vol expansion × momentum divergence fade`
- **execution：** 1-bar delay / maker-first / hard time-stop
- **veto：** 极端趋势日、事件窗、资金费率结算前后、低流动币种
- **risk：** 单资产限额、连续亏损冷却、只做高流动 major

它既可以独立做，也可以给别的书做 veto：
- breakout 书在 TR/price divergence 出现时别追
- momentum 书在“噪声扩张但推进走弱”时 size-down

但如果把它写成 overlay，就会错过它本来就是 alpha 本体这件事。这里还是要明确：

> **它首先是 raw alpha；其次才可以兼做 veto/filter。**

## 8. 下一步怎么测

这轮最重要的是把“能不能活”测得更 desk 一点。我建议按下面顺序推进：

### 8.1 先修 repo 的最小接线，再做参数面

第一步不是疯狂优化，而是先修正：
- YAML 嵌套参数读取
- `divergence_threshold` 真正接入
- `min_tr_strength / max_tr_strength` 真正接入

然后直接在 `5m / 15m` 跑三类阈值面：
- divergence threshold
- TR percentile / TR strength threshold
- max hold `2 / 4 / 8 / 12` bars

### 8.2 把“中间波动过滤”改成“极端波动衰竭过滤”

repo 现在的 volatility filter 是：
- 只在 `25% ~ 75%` 分位波动区间交易

这和“volatility spike exhaustion”这个叙事其实有点拧巴。

更值得测的是：
- **只做 top decile / top quartile TR shock 后的背离**
- 或者
- **TR 先极端抬升，再出现动量跟不上的二次确认**

也就是把它从“普通状态下的背离”改成：
- **极端状态下的 exhaustion fade**

### 8.3 缩短持有、压低换手成本

从 first verdict 看，edge 很薄，所以第二轮实验要重点看：
- `maker-first` 是否能救活
- `1~4 bar hold` 是否比 `8 bar hold` 更合适
- `只做 BTC / SOL` 是否优于 ETH / BNB
- `亚洲/欧美活跃时段` 是否有明显差异

### 8.4 最小实验建议口径

**版本 A：BTC/SOL only，Binance perp，5m/15m 双周期**

- Universe：`BTCUSDT`, `SOLUSDT`
- Trigger：`TR_strength >= pct90` 且 `momentum_direction != TR_direction`
- Entry：下一根 bar 开盘/被动挂单
- Exit：
  - `2 / 4 / 8` bar time-stop
  - 或动量符号翻回
- Cost ladder：`0 / 1 / 2 / 4 bps` 单边
- 输出：
  - gross / net Sharpe
  - 每笔 bps
  - adverse excursion
  - signal density

如果这版仍不过线，就说明：
- 这条 alpha 更适合当 **breakout veto**；
- 不该继续当主书 candidate 深挖。

## 9. 一句话结论

> **`true_range_divergence` 值得保留，不是因为 repo 现在已经像 production，而是因为它给了一个很清楚、完全可独立复现、又不依赖外部数据的 single-asset mean-reversion 母 alpha：`TR 扩张 × 价格动量背离 → 短持有衰竭 fade`。但 public 15m first verdict 也已经很诚实：直译 taker 版不过线，下一步要么把它收紧成 extreme-event pocket，要么把它转成 breakout/momentum 书的 execution veto。**
