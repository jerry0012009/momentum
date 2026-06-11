# 别把这份 2025/2026 OBI 仓只读成“做市工程模板”：对 short-cycle desk，更该先保留的是「order book imbalance → 几秒级 mid-price 漂移」这条 base alpha，再把 maker quote skew 包成完整策略壳

- 时间：2026-04-17 09:20 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `backtest_standx_OBI.py` + `backtest_standx_OBI_optuna.py` + `docs/OBI_half_spread.md`）+ Binance USDⓈ-M 公共深度快照 live probe（BTCUSDT，180s，top20）
- 主题类型：raw alpha
- 基础 alpha：**盘口里近端 bid depth 明显大于 ask depth 时，未来几秒 mid-price 更容易往上漂；反之更容易往下漂。repo 里的 maker quote skew / position skew / dynamic half-spread，不是 alpha 本体，而是把这条 ultra-short microstructure alpha 包成可交易做市壳。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / microstructure / order-book-imbalance / maker / market-making / quote-skew / fair-value / volatility-spread / position-skew / binance / standx / repo / public-data / 1m / 3m / 5m
- 证据类型：GitHub repo 实现 + 本地 live public-data sanity probe

## 1. 这次看了什么
主材料是一个比较新的 GitHub 仓：

- **Author / Maintainer：** djienne
- **Year：** 2025 创建，2026 仍有更新
- **Title：** *StandX Market Making Backtest BTC*
- **Venue：** GitHub repo（内含数据采集、格式转换、hftbacktest 回测、Optuna 搜参）
- **DOI：** N/A
- **Readable URL：** <https://github.com/djienne/StandX_Market_Making_Backtest_BTC>
- **Repo URL：** <https://github.com/djienne/StandX_Market_Making_Backtest_BTC>

先把一句话讲清楚：

> **这份东西最值钱的地方，不是“会做市”这四个字，而是它把一条很清楚的 base alpha 写成了代码：`OBI 极端值 -> fair value 偏移 -> 双边挂单向有利方向倾斜`。**

也就是说，真正该 intake 的第一层不是 maker shell，而是：
- **盘口买盘更厚时，未来几秒更容易向上；**
- **盘口卖盘更厚时，未来几秒更容易向下。**

## 2. 核心结论
### 2.1 一句话结论

> **这是一条可以独立成型的 microstructure raw alpha：OBI 先给 ultra-short 方向偏置，做市外壳只是把“预测几秒漂移”翻译成“该把 bid 往近处挪，还是把 ask 往远处摆”。**

### 2.2 一句话它是怎么证明的

> **repo 用逐笔/逐档簿记回放 + maker/taker 费用 + latency + position cap 去回测；我又用 Binance 公共 `top20 depth` 做了一个 180 秒 live sanity probe，确认 OBI 极端值和随后 3~20 秒的 mid 漂移方向确实有关。**

### 2.3 为什么我认为值得进素材池
- 它的 **base alpha 讲得清楚**，不是“黑箱 market making”；
- repo 已经把 **entry / quote placement / sizing / fee / latency / inventory skew** 都写进壳里；
- 这条信号天然贴近 `1m/3m`，再往上也能服务 `5m` 的 execution veto，而不是又一篇日频换皮故事。

## 3. repo 里最值钱的 3 层结构
### 3.1 第一层：base alpha = near-book imbalance 预测几秒级漂移
`backtest_standx_OBI.py` 里核心信号很直白：
- 在 `looking_depth` 范围内累计 bid / ask 深度；
- 算 `imbalance = bid_qty - ask_qty`；
- 再对 rolling window 做 z-score，得到 `alpha`；
- 用 `fair_price = mid_price + c1 * alpha` 把公允价往强侧推。

翻成人话：

> **盘口里如果买单墙更厚，系统就认为“真实公允价”应该略高于当前 mid；如果卖单墙更厚，就认为公允价应略低。**

### 3.2 第二层：半价差不是固定写死，而是“波动率决定挂多远”
repo 不是机械挂一格，而是把 half-spread 绑定到短窗波动率：
- 默认 `step_ns=100ms`
- `window_steps=6000`，大约 **10 分钟 warm-up**
- `update_interval_steps=50`
- `half_spread_tick = volatility * vol_to_half_spread`

意思很简单：
- 市场动得快，就挂宽一点，少被白白打掉；
- 市场安静，就挂窄一点，提高成交率。

### 3.3 第三层：inventory skew 把 alpha 包成完整做市壳
repo 还把持仓塞回报价：
- `normalized_position = position * mid / max_position_dollar`
- bid / ask depth 会被 `skew` 按持仓方向调整；
- 持仓太长就少买多卖，持仓太短就少卖多买。

所以它不是“只会看方向”，而是：

> **先用 OBI 决定哪边更值得主动贴近，再用 inventory skew 控制别把自己越做越歪。**

## 4. 我补的 public-data 快检
我额外跑了一个很轻的 live probe：
- **数据源：** Binance USDⓈ-M 公共 `depth` API
- **标的：** `BTCUSDT`
- **口径：** 连续 `180s`、每秒抓一次 `top20` 深度
- **指标：** 用 top20 depth 算 OBI；看当前 OBI 分位极端值，对未来 `3/5/10/20s` mid return 的影响
- **artifact：**
  - `reports/artifacts/quant_digests/2026-04-17_depth_imbalance_maker_skew_probe.py`
  - `reports/artifacts/quant_digests/2026-04-17_depth_imbalance_maker_skew_probe_summary.json`
  - `reports/artifacts/quant_digests/2026-04-17_depth_imbalance_maker_skew_probe_samples.csv`

### 4.1 关键数字
- **5s horizon：** 高 OBI 桶平均 `+0.589 bps`，低 OBI 桶平均 `-0.797 bps`
- **10s horizon：** 高 OBI 桶平均 `+0.972 bps`，低 OBI 桶平均 `-0.628 bps`
- **20s horizon：** 高 OBI 桶仍约 `+0.638 bps`，但方向命中已明显变脆

我的读法不是“已经能上线”，而是：

> **OBI 的方向性在几秒级是活的，但窗口一拉长就开始衰减，所以它更像 ultra-short base alpha / maker skew anchor，而不是裸 taker 追单信号。**

## 5. 对我们 desk 的正确读法
### 5.1 这轮为什么归到 `raw alpha`
因为它的 base alpha 可以直接说清楚：

> **盘口不平衡会先于价格微漂移。**

这不是纯 filter，也不是纯 execution。execution 壳只是把它包装成完整策略。

### 5.2 和当前 `1m / 3m / 5m / 15m` 的关系
- **1m / 3m：** 最自然，适合直接做 maker skew / quote placement / child-order veto
- **5m：** 不适合拿 OBI 直接当 bar-close 主信号，但很适合做 entry refinement
- **15m：** 更像 execution veto 或“只在 microstructure 顺风时才放行”的确认层

### 5.3 它服务于哪些 raw alpha
除了单独做 ultra-short maker shell，它还可以服务：
1. **短窗 momentum continuation**：只在盘口同向时追
2. **shock fade / mean reversion**：盘口没反向配合就别急着抄底摸顶
3. **pairs / spread fade execution**：只在被交易腿的盘口失衡不对着你时进场

## 6. 策略拆解（必填）
- **方向属性：** 单资产 / microstructure / ultra-short directional edge，执行形态偏 maker
- **基础 alpha：** order book imbalance 极端值先于几秒级 mid-price 漂移
- **regime：** 高噪声、深度虚胖、盘口频繁撤单时，alpha 易衰减
- **filter / veto：** 最小半价差、最小有效深度、盘口刷新稳定性、事件前后禁做
- **risk / sizing / execution overlay：** volatility-scaled half-spread、inventory skew、position cap、maker/taker fee、latency

## 7. 可复刻的最小实验
### 7.1 数据源、公开性、更新频率
- **数据源：** Binance / Bybit 公共 depth WebSocket 或 REST 快照
- **公开性：** 公开可得，无需私有成交回报
- **更新频率：** 秒级甚至亚秒级
- **最小口径：** 先做 `BTC/ETH/SOL`，top `10/20/50` depth 三档对照

### 7.2 下一步怎么测
先别急着上完整做市回放，先做 3 个最小实验：
1. **signal-only**：`OBI decile -> next 1/3/5/10/20s mid return`，看方向性和衰减速度；
2. **friction ladder**：把信号翻成最简单双边/单边 quote skew，测 `maker only / maker+taker fallback / taker impossible` 三档；
3. **cross-asset portability**：同样口径跑 `BTC/ETH/SOL`，确认这是不是只在 BTC 活着。

最该先看的两个指标：
- **高/低 OBI 分桶后的 future mid return 差值**
- **扣掉最小成交摩擦后的每笔期望值是否仍为正**

## 8. 风险与保留意见
- 我这次的 live probe 只有 **180 秒**，只能算 sanity check，不算稳健回测；
- REST depth 会有采样误差，真实交易更该用 WebSocket L2 增量流；
- OBI 特别容易受 spoofing / cancel-replace / 交易所撮合细节影响；
- 这类 edge 半衰期很短，**更适合 maker 壳，不适合裸 taker chase**。

## 9. 来源
- djienne. (2025/2026). *StandX Market Making Backtest BTC*. GitHub.
  - Readable URL: <https://github.com/djienne/StandX_Market_Making_Backtest_BTC>
  - Key files: <https://raw.githubusercontent.com/djienne/StandX_Market_Making_Backtest_BTC/main/backtest_standx_OBI.py>, <https://raw.githubusercontent.com/djienne/StandX_Market_Making_Backtest_BTC/main/backtest_standx_OBI_optuna.py>, <https://raw.githubusercontent.com/djienne/StandX_Market_Making_Backtest_BTC/main/docs/OBI_half_spread.md>
- Binance USDⓈ-M Futures Public API.
  - Depth endpoint doc: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book>
