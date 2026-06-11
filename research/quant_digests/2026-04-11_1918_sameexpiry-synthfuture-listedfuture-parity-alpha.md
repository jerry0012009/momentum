# 别把这份 2026 options repo 只读成做市框架：对 short-cycle desk，更该先盯的是「same-expiry synthetic future × listed future parity gap」这条 raw alpha

- 时间：2026-04-11 19:18 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `strategies/arbitrage/conversion.py` + `strategies/arbitrage/option_box.py`）+ Binance Options / USDⓈ-M Quarterly Futures 公共 live-BBO probe
- 主题类型：raw alpha
- 基础 alpha：**同一标的、同一到期日、同一 strike 的 `call - put` 会合成一条 synthetic future；当它相对同 expiry 的 listed future 出现可交易的 parity gap 时，做多便宜 forward、做空更贵 forward，等 gap 收敛或持有到 expiry 锁定价差。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/options/futures/same-expiry/synthetic-forward/put-call-parity/conversion-reversal/binance/btc/eth/1m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 策略代码 + 交易所公共报价 probe

## 1. 这次看了什么
主材料不是论文，而是一份 **2026 高信号 options research repo**：

- **Repo:** `signorloops/crypto-options-research-platform`
- **Repo URL:** <https://github.com/signorloops/crypto-options-research-platform>
- **Readable README:** <https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/README.md>
- **关键代码 1：conversion / reversal**
  - <https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/strategies/arbitrage/conversion.py>
- **关键代码 2：box spread**
  - <https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/strategies/arbitrage/option_box.py>

这份 repo 很容易被读成：

> 又一个“期权做市 / 波动率 / Greeks / 风控”大而全框架。

但对我们现在的 short-cycle desk，更值得先单独拎出来的，不是做市，也不是 IV 曲面，而是它在 `conversion.py` 里已经写得很清楚的一条 **完整 raw alpha 壳**：

> **same-expiry synthetic future vs listed future parity gap。**

翻成人话：

- 用同一 expiry、同一 strike 的 `call - put`，能拼出一条 synthetic future；
- 再拿它去对同 expiry 的季度 future；
- 谁更贵，就空谁；谁更便宜，就多谁；
- 赌的是 **同到期 forward 不该长期错开**。

这不是 filter，也不是 overlay。

这是标准的 **relative-value / stat-arb raw alpha**。

## 2. 为什么这条线值得写，而且不算和已有 funding / basis 主题重复
我们最近已经写过不少：

- spot ↔ perp basis
- perp ↔ perp funding / carry
- same-expiry cross-venue futures basis
- options RND directional

但这条线和它们都不一样：

1. **它不是 directional options view**  
   不是猜 BTC 会涨跌，而是看 **options-implied forward** 和 **listed future** 有没有偏离。

2. **它不是普通 spot-perp basis**  
   这里两条腿都是同 expiry forward exposure，噪声比 `spot + financing + borrow` 更少。

3. **它不是 box spread carry 到期教材**  
   box 更偏 hold-to-expiry carry；这里更适合 short-cycle desk 的地方在于：
   **可以 1m / 5m 盯 parity gap，做 intraday 收敛，而不是只等到期。**

一句话说清 base alpha：

> **同 expiry 的 forward 曝险不该在同一交易所里长期出现两套价格；当 synthetic future 和 listed future 错开到足够大，就做 parity close。**

## 3. repo 里最该拿走的，不是“框架很全”，而是这 3 个可执行零件
### 3.1 `conversion.py` 已经把策略骨架写出来了
repo 里的 `ConversionArbitrage` 很直接：

- 算 `call - put` 的 synthetic forward；
- 和理论 / 对冲腿比较；
- 偏离过阈值就触发 `conversion` 或 `reversal`；
- 同时给了：
  - `get_hedge_position()`
  - `calculate_margin_requirement()`
  - `calculate_pnl_scenarios()`
  - `verify_arbitrage_bounds()`

也就是说，它不是一句空洞的“平价可能失效”。

它已经接近完整策略：

- **entry**：gap 过阈值
- **hedge**：合成腿 vs 对冲腿
- **exit**：gap 回归 / 到期 / time stop
- **risk**：保证金与边界检查
- **PnL**：逐腿可分解

### 3.2 这条线天然适合 desk 做成“分腿价格监控器”
对 short-cycle desk，最有价值的不是慢悠悠地讲 no-arb，而是把它变成一个持续运行的 intraday panel：

- synthetic bid / ask
- listed future bid / ask
- 可执行 best-side edge
- gap z-score
- 距离 expiry 天数
- strike 距离 ATM 的 moneyness

所以这条线虽然属于 options RV，但落地方式反而很像我们已经熟悉的 futures RV / basis monitor。

### 3.3 它比 spot 版 conversion 更贴近 crypto 实盘
传统教材常写：

- long/short spot
- long/short call
- long/short put

但在 crypto 实盘里，**用同 expiry future 当对冲腿** 往往更自然：

- 不用单独处理现货借贷
- 不必把 stablecoin 利率 / borrow rate 全部硬塞进第一版
- 账面更接近我们现有 futures 执行栈

所以这次更适合 desk 的改写不是：

> `call - put` vs `spot - PV(K)`

而是：

> `call - put + K` vs `same-expiry listed future`

## 4. 这轮 public-data probe：Binance 同 expiry options / futures 上，当前 live BBO 有没有可打的 parity gap？
我做了一个很克制的 live probe：

### 数据源 / 公开性 / 更新频率
- Binance Options `eapi/v1/ticker`：公开 REST
- Binance USDⓈ-M delivery futures `fapi/v1/ticker/bookTicker`：公开 REST
- 频率：理论上可 `1m` 甚至更快轮询；这轮先做 one-shot live BBO snapshot

### 对齐口径
只保留：

- **BTC / ETH**
- **存在同 expiry listed future 的 expiry**：`260626`、`260925`
- 同一 `(asset, expiry, strike)` 的 call / put 成对报价
- moneyness 约束：`|ln(K / F_mid)| < 0.15`
- 期权价差不过分离谱：`call_spread_frac < 0.5` 且 `put_spread_frac < 0.5`

### 可执行定义
定义：

- `synthetic_bid = K + call_bid - put_ask`
- `synthetic_ask = K + call_ask - put_bid`

两种 best-side 机会：

1. **long synthetic / short future**  
   `edge = future_bid - synthetic_ask`

2. **short synthetic / long future**  
   `edge = synthetic_bid - future_ask`

只要 `edge > 0`，才算**未扣手续费前**就已经存在 gross parity gap。

### 本地 artifact
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_options_futures_parity_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_options_futures_parity_probe_detail_2026-04-11.csv`

## 5. first verdict：结构是对的，但当前 Binance live BBO 下还没过线
先说结论：

> **这条 alpha 的结构非常清楚，但我这轮在 Binance 同所 options / quarterly futures 的 live BBO 上，没有看到 gross-positive 的可执行 parity gap。**

这不是坏事，反而说明：

- 同所同 expiry 的 listed future 已经把 parity 吸得很紧；
- 真正有价值的，不是把它吹成“白捡套利”，而是把它做成 **严谨的 options RV 监控器**；
- 若要出正 edge，更可能要等 **事件期、expiry 周、剧烈波动、薄 strike、跨 venue**，而不是平时静态扫一眼就有肉。

### 5.1 BTC：16 个筛后 triplet，best-side 仍为负
summary 里 BTC 的结果：

- 筛后 triplet：**16**
- 覆盖 expiry：`260626`、`260925`
- **median best-side edge ≈ -23.07 bps**
- 最好的一档也只是：
  - expiry：`260626`
  - strike：`78000`
  - best side：`long synthetic / short future`
  - **edge ≈ -55 USDT / -7.46 bps**

翻成人话：

> **连最好的一档，synthetic ask 仍比 future bid 更贵约 7.5 bps；还没到可做的程度。**

### 5.2 ETH：12 个筛后 triplet，最好一档也没翻正
ETH 的结果：

- 筛后 triplet：**12**
- 覆盖 expiry：`260626`、`260925`
- **median best-side edge ≈ -31.95 bps**
- 最好的一档：
  - expiry：`260626`
  - strike：`2400`
  - best side：`short synthetic / long future`
  - **edge ≈ -2.98 USDT / -12.91 bps**

也就是说：

> **ETH 当前 live BBO 下甚至比 BTC 更紧，至少在这轮筛选里没有看到可执行 gross edge。**

### 5.3 当前更像“没有被市场喂饭”，不是“alpha 不存在”
这里要区分两件事：

1. **alpha 的定义是否成立？**  
   成立。base alpha 很清楚。

2. **当前这个 venue / 这组 strike / 这一个时点，有没有净可交易 edge？**  
   这轮答案是：**没有。**

这两件事不矛盾。

就像很多 cross-venue futures RV 一样：

- 结构上是对的；
- 但大多数时刻没信号；
- 真正值钱的是把它盯住，并知道**什么时候**它会突然张开。

## 6. 这条线为什么仍然值得进研究池
尽管 live one-shot 没看到正 edge，我仍然认为它值得留在 raw alpha 素材池，原因有 4 个。

### 6.1 它补上了“options RV”这一层，而不是重复老题
我们现在的 raw alpha 池里：

- futures / perp RV 很多
- pairs / stat-arb 很多
- microstructure 也很多

但 **options-implied forward vs listed future** 这一层几乎还没单独拆过。

这次至少把它写清楚了：

- 什么是 alpha 本体
- 什么不是 alpha 本体
- 怎么定义 entry / exit
- 怎么做第一轮 public probe

### 6.2 它和 `1m / 5m / 15m` 并不冲突
这条线不是“每根 K 都强制交易”的 directional signal，
但非常适合做成：

- **1m**：实时监控 / 事件触发
- **5m**：主执行分辨率
- **15m**：慢一点的 time-stop / carry-to-close 监控

也就是说，它更像 **dislocation book**，不是全天候 sign book。

### 6.3 它是完整策略，不是研究散件
这条线天然自带：

- entry：best-side edge > 0 且过费用阈值
- exit：edge 回到 0 附近 / time stop / expiry 前平仓
- sizing：按两腿最薄深度和净 edge 分层
- risk：单 strike、单 expiry、单 event gross limit
- cost：期权 spread + future spread + taker/maker fee + 撤单失败 / 追单滑点

所以它不是 filter，不是 overlay。

它是完整 raw alpha 壳。

### 6.4 当前 Binance 没肉，不代表 cross-venue 没肉
同所 parity 往往最紧，这是正常的。

真正更值得 desk 下一步测的，反而可能是：

- Binance options synthetic future vs Deribit / OKX 同 expiry future proxy
- event window（CPI / FOMC / 大波动）前后 parity gap 是否瞬时拉开
- expiry 周 ATM / near-ATM 的 gap 是否系统性放大

换句话说：

> **Binance 同所没给肉，反而提示下一步该去找“谁的腿慢了”。**

## 7. 策略拆解（必填）
- 方向属性：relative value / stat-arb / market-neutral-ish
- 基础 alpha：same-expiry synthetic future vs listed future parity gap close
- regime：优先高活跃、near-ATM、报价连续、距离 expiry 不太远但仍有交易深度的时段
- filter / veto：best-side edge 未过 fees+slippage 不做；单腿 quote stale 不做；深度太薄不做；极端事件里单腿跳价过快不做
- risk / sizing / execution overlay：按净 edge / quote depth / strike liquidity 分层；限制单 expiry gross；优先 maker on slower leg；设置 `time stop + edge stop + quote-staleness kill-switch`

## 8. 可复刻的最小实验
### 最小研究假设
> 当同 expiry synthetic future 与 listed future 的 best-side executable gap 超过成本阈值时，未来 `1m / 5m / 15m` 更可能出现 parity close，而不是继续扩张。

### 最小实验口径
- 资产：BTC / ETH
- expiry：`260626`、`260925`（后续可滚动更多季月）
- strike：near-ATM 到轻度 OTM
- 数据：
  - options bid/ask
  - listed future bid/ask
  - 时间戳对齐后的 executable edge panel
- 先看 3 个核心指标：
  1. `best_side_edge_bps`
  2. edge 触发后未来 `1m / 5m / 15m` 的 close 幅度
  3. 扣 friction ladder 后剩余净 edge 的占比

## 9. 下一步怎么测
下一步我不会再停留在 one-shot snapshot，而是直接做 4 件事：

1. **做 1m panel，不再只看单时点**  
   连续抓 `options bid/ask + quarterly future bid/ask`，至少做 `7d~30d` 面板，先回答：
   - 正 edge 到底多久出现一次？
   - 主要集中在哪些 strike / 时段 / 波动状态？

2. **做 event-study，不再混在平静样本里平均**  
   重点看：
   - 高 realized vol 窗口
   - 宏观数据前后
   - expiry week
   - funding / basis 快速变化时段

3. **把同所 parity 升级成跨 venue parity**  
   如果 Binance 同所本来就很紧，那更可能出信号的地方是：
   - one leg 在 Binance options
   - 另一 leg 在 Deribit / OKX future / perp proxy

4. **显式加 friction ladder**  
   第一版至少同时跑：
   - gross edge
   - `gross - 5 bps`
   - `gross - 10 bps`
   - `gross - 20 bps`

如果 `gross` 都常年不过零，这条线在该 venue 就只是监控器；
如果 `gross` 偶发翻正、但 `gross-10bps` 全灭，它更像 ultra-selective event alpha；
只有 `gross-10bps` 仍有事件簇，才值得进可执行复现队列。

## 10. 来源
### Repo / code
- `signorloops/crypto-options-research-platform`
  - Repo URL：<https://github.com/signorloops/crypto-options-research-platform>
  - README：<https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/README.md>
  - Conversion / reversal：<https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/strategies/arbitrage/conversion.py>
  - Option box：<https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/strategies/arbitrage/option_box.py>

### Public data endpoints used in this note
- Binance Options ticker：<https://eapi.binance.com/eapi/v1/ticker>
- Binance USDⓈ-M futures book ticker：<https://fapi.binance.com/fapi/v1/ticker/bookTicker>
- Binance Options exchange info：<https://eapi.binance.com/eapi/v1/exchangeInfo>
- Binance USDⓈ-M futures exchange info：<https://fapi.binance.com/fapi/v1/exchangeInfo>

### Local artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_options_futures_parity_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_options_futures_parity_probe_detail_2026-04-11.csv`
