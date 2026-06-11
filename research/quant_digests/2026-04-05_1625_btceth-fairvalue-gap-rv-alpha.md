# 别把这份 2026 relative-value engine 只读成本地 dashboard：对 short-cycle desk，更该先测的是「BTC+ETH fair-value gap × residual z-score mean reversion」这条完整 raw alpha

- 时间：2026-04-05 16:25 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `feature_engine.py` / `signal_engine.py` / `interval_profiles.py` / `engine.py` / `risk_engine.py` / `backtest.py` / `monitor.py`）+ Binance 公共 `15m/1h` live portability probe
- 主题类型：raw alpha
- 基础 alpha：**用 BTC 与 ETH 作为双 benchmark，对各 alt 的 log price 做滚动回归得到 fair value；当 alt 相对 fair value 的 residual z-score 极端偏离时，做向 fair value 回归的一边。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/mean-reversion/beta-adjusted/fair-value-gap/residual-zscore/btc-eth-benchmark/binance/15m/5m/3m/1m/repo/public-data/cost/risk
- 证据类型：GitHub 源码审计 + 公共 API 最小 live probe

## 1. 这次看了什么
这轮主看的是一个非常新的 GitHub repo：

- **Jose Duran (`joanduso`) (2026), _Crypto Relative Value Engine_**
  - Venue：**GitHub repository**
  - Created：**2026-03-13**
  - Last pushed：**2026-04-01**
  - DOI：**无**
  - Readable URL：<https://github.com/joanduso/crypto-relative-value-engine->
  - Repo URL：<https://github.com/joanduso/crypto-relative-value-engine->

这次重点审了这些文件：

- `README.md`：项目目标、模式、monitor / dashboard 结构
- `feature_engine.py`：**核心 fair-value / residual / z-score** 计算
- `signal_engine.py`：**entry gate / ranking / fee 假设**
- `interval_profiles.py`：**15m / 1h / 4h 窗口映射**
- `engine.py`：主流程与默认 risk limits
- `risk_engine.py`：**position sizing / stop / take-profit / time-stop**
- `backtest.py`：历史 outcome 模拟框架
- `monitor.py`：把 raw alpha 与 funding / basis / news / regime 叠加成监控器

我最后选它，不是因为它有 dashboard，而是因为这里面真正值钱的不是 UI，而是一条**非常明确、可独立复现、而且天然适合 `15m / 5m` 迁移**的 raw alpha：

> **beta-adjusted relative-value mean reversion**。

这条线比再写一篇 filter / overlay 更值得的原因很简单：

- 它直接扩充的是 **raw alpha 素材池**；
- entry / exit / sizing / fee / risk 在源码里都已经拆出来了；
- 并且它不是老式“找一对 cointegration pair 再做 z-score fade”，而是一个更 desk-friendly 的写法：
  - 每个 alt 都相对 **BTC + ETH** 的联合 fair value 定位；
  - 这更像一个**多 benchmark 的 beta-adjusted mispricing** 框架；
  - 很容易迁移到 `5m / 15m` 的 liquid perp universe。

---

## 2. 先回答：这篇东西的 base alpha 是什么？
先把最关键的问题说透。

### 2.1 它的 base alpha 很明确，而且是 raw alpha
这条策略的核心不是 news，不是 ETF flow，也不是 BTC regime overlay。
真正的 base alpha 是：

> **某个 alt 相对 BTC + ETH 联合解释出来的 fair value 出现了统计上足够大的偏离，而这种偏离倾向于均值回归。**

翻成人话：

1. 先看 alt、BTC、ETH 的价格；
2. 用一个滚动回归估计：在最近一段时间里，这个 alt 正常应该跟着 BTC 和 ETH 怎么走；
3. 得到一个“理论 fair value”；
4. 如果 alt 明显低于这个 fair value，就偏向做多；
5. 如果 alt 明显高于这个 fair value，就偏向做空；
6. 再用 volatility / liquidity / spread stability / funding 把最差的样本过滤掉。

这不是 filter 伪装成 alpha。
它本身就是一条：

- **raw alpha 类型**：relative value / stat-arb / mean reversion  
- **收益来源**：beta-adjusted mispricing 的回归  
- **交易对象**：liquid alts 相对 BTC、ETH 的联合风险因子

### 2.2 为什么我把它当主 digest，而不是把 repo 里的 regime / news / bias 模块当主角
repo 里当然还有：

- `btc_market_bias_engine.py`
- `regime_engine.py`
- `news_engine.py`
- `signals/funding_arbitrage.py`
- `signals/basis_trade.py`

但这些更像：

- filter
- regime gate
- overlay
- 监控/路由层

如果 bot7 这一轮要遵守“**优先 raw alpha / 可独立复现完整策略**”的原则，那最该拿走的显然不是这些附属层，而是：

> **BTC+ETH fair-value gap 的 residual z-score 回归壳。**

---

## 3. 为什么这条线比继续补纯 filter 主题更值得？
因为它直接补的是当前 desk 很需要的一类素材：

- 不是单币 breakout；
- 不是又一层 sentiment veto；
- 不是只能依附于别的 alpha 才有意义的 overlay；
- 而是一条**可以单独成策略**的 relative-value / stat-arb raw alpha。

而且它有三个对 short-cycle desk 很实用的优点：

### 3.1 比“单 benchmark beta-neutral”更稳一点
它不是只拿 BTC 当 benchmark，而是把 **BTC + ETH** 一起放进回归里。

这很重要，因为很多 alt 的短周期表现并不是“只跟 BTC 一条线”，而是：

- 大盘方向看 BTC；
- beta / 风格 / L1-L2 情绪更容易被 ETH 共振带动。

所以用双 benchmark 做 fair value，比单纯 `alt vs BTC spread` 更接近我们实际看到的盘面结构。

### 3.2 比传统 pair trading 更容易扩到一篮子 alt
传统 pairs 的问题是：

- pair admission 重；
- 对稳定性敏感；
- 一旦某对失配就要重建。

这条写法更像：

- 给每个 alt 一个相对大盘的 fair-value anchor；
- 再做统一的 z-score / vol / liquidity / funding gate；
- 然后横向比较机会分数。

这对 desk 来说，比手工维护很多 pair 更容易工程化。

### 3.3 它已经自带完整策略壳，而不是只给一个 signal
源码里不只是给了 residual z-score，还把下面这些都写出来了：

- entry threshold
- fee 假设
- liquidity gate
- volatility gate
- spread stability gate
- funding veto
- top-N selection
- stop / take-profit
- time-stop
- risk budget

也就是说，这不是“有个想法，但离实盘还很远”的材料；而是一个**能直接压成最小实验**的壳。

---

## 4. 源码里的策略到底怎么做

## 4.1 数据口径：公开可得，可直接最小复现
repo 默认用的是 Binance 公共接口：

- `api/v3/klines`：spot K 线
- `fapi/v1/fundingRate`：futures funding

默认 alt universe：

- `XRPUSDT`
- `SOLUSDT`
- `ADAUSDT`
- `DOGEUSDT`
- `BNBUSDT`
- `LTCUSDT`
- `LINKUSDT`
- `AVAXUSDT`

benchmark：

- `BTCUSDT`
- `ETHUSDT`

这意味着最小复现实验不依赖私有数据：

- **公开性**：公开 API 可拉  
- **更新频率**：跟 K 线频率同步（`15m / 1h / 4h`）  
- **最小实验口径**：直接按 repo 的 Binance 端点就能复现

### 4.2 fair value 是怎么来的
`feature_engine.py` 的核心是一个滚动 OLS：

```python
log_alt ~ intercept + beta_btc * log_btc + beta_eth * log_eth
```

在每个时点得到：

- `predicted_log_price`
- `fair_value = exp(predicted_log_price)`
- `residual_log = log_alt - predicted_log_price`
- `z_score = (residual_log - rolling_mean) / rolling_std`
- `deviation_pct = alt_price / fair_value - 1`

然后交易方向非常直接：

- `deviation_pct < 0` → **LONG**（alt 低于 fair value）
- `deviation_pct > 0` → **SHORT**（alt 高于 fair value）

这是非常干净的 raw alpha 结构。

### 4.3 15m 框架不是乱拍脑袋，而是给了明确窗口
`interval_profiles.py` 里，`15m` profile 直接写死为：

- 回归窗口：`96 * 7 = 672 bars`（约 **7 天**）
- z-score 窗口：`96 * 3 = 288 bars`（约 **3 天**）
- stability 窗口：`96 bars`（约 **1 天**）
- volatility 窗口：`96 bars`（约 **1 天**）

这点很关键，因为它说明：

> **这不是日频想法硬搬到盘中；作者本来就在按 `15m` 口径设计。**

### 4.4 entry / filter / fee 假设
`signal_engine.py` 里 `COPILOT` 默认阈值是：

- `abs(z_score) >= 1.75`
- `realized_volatility <= 1.40`
- `quote_volume >= 2,500,000`
- `spread_stability_score >= 0.45`
- `abs(funding_rate) <= 0.0015`
- `fee_bps = 8`
- `top_n = 5`

翻成人话就是：

- 偏离不够大，不做；
- 波动太爆，不做；
- 流动性不够，不做；
- residual 本身太乱，不做；
- funding 太极端，不做；
- 即使做，也只挑 top 机会。

### 4.5 risk / sizing / exit 已经给了完整壳
`engine.py` + `risk_engine.py` 的 `COPILOT` 默认 risk 框架：

- 最大并发仓位：`1`
- 最大日亏损：`3%`
- 最大周回撤：`7%`
- 单笔风险预算：`1% equity`
- 最大持有：`48h`
- 基础 stop：`3%`
- 基础 take-profit：`6%`

而且不是死板固定止损：

- stop 会随 realized vol 调整；
- take-profit 会根据 `edge_after_fees_pct` 和 stop 距离联动；
- position size 用风险预算 / stop distance 算出。

所以这条题材满足“**可直接落地完整策略（entry/exit/sizing/risk/cost）**”这一条。

---

## 5. 最关键的 6 个数据点

### 5.1 这不是老 repo 翻新，而是 2026-03-13 新建、4 月还在更新
GitHub API 元数据：

- `created_at = 2026-03-13T04:47:55Z`
- `pushed_at = 2026-04-01T19:57:14Z`

也就是说，这轮确实算得上**近 5 年内、而且是最近几周还在活跃的新 repo**。

### 5.2 15m 的 base alpha 定义很完整：7d fair value + 3d z-score + 1d stability/vol
这比很多只说“做 z-score reversion”但不告诉你窗口怎么压缩的材料强很多。

作者已经明确把 `15m` 结构写成：

- `7 天`回归看 fair value
- `3 天`看 residual 是否极端
- `1 天`看残差是否稳定、波动是否可接受

这非常适合我们直接压成 `15m -> 5m` 的最小移植实验。

### 5.3 entry threshold 不保守到完全不触发，也没宽到只剩噪音
核心 admission 条件：

- `|z| >= 1.75`
- `stability >= 0.45`
- `fee = 8 bps`

这组阈值不是纯学术写法，而是明显在试图兼顾：

- 偏离幅度
- 可成交性
- 成本后净边际

### 5.4 我按 repo 逻辑做了一个 `15m` live probe：信号是活的，但默认流动性门槛对 spot 15m 偏高
用 repo 默认 universe + Binance 公共数据，在 `2026-04-05 16:15 UTC` 的 `15m` 快检结果里：

- **SOLUSDT**
  - fair-value gap：**-3.12%**
  - `z = -2.19`
  - `spread_stability_score = 0.86`
  - 方向：**LONG**
- **XRPUSDT**
  - fair-value gap：**-2.26%**
  - `z = -1.88`
  - `spread_stability_score = 0.91`
  - 方向：**LONG**

但：

- 这轮 **没有标的通过全部默认 filter**；
- 主因不是 z-score 不够，而是 `quote_volume >= 2.5m` 这一条在 **spot 15m** 上偏严。

这很有价值，因为它说明：

> **alpha 本体是活的，但 15m 直接照搬 repo 的 spot volume gate，可能会把大部分机会先挡掉。**

### 5.5 同样逻辑切到 `1h`，SOL 当下就能过默认 admission
我又按 `1h` profile 快检了一次，`2026-04-05 16:00 UTC`：

- **SOLUSDT**
  - fair-value gap：**-3.32%**
  - `z = -1.82`
  - `realized_vol = 0.31`
  - `quote_volume ≈ 2.50m`
  - `stability = 0.80`
  - **通过默认 filter**

这进一步说明：

- 这条 raw alpha 不是无效；
- 更像是 **15m 上的流动性门槛需要按 bar 周期重标定**；
- 核心 fair-value gap / residual z-score 结构仍然是可工作的。

### 5.6 这个 repo 最大的工程价值，是把 raw alpha 和 overlay 拆开了
`monitor.py` 里还能叠：

- funding signal
- basis signal
- BTC directional bias
- macro / ETF / Fear & Greed / news

但这些没有盖掉 raw alpha 主体，反而让我们更容易做拆件实验：

- 先测 base alpha；
- 再测 regime gate；
- 再测 external overlay。

这正符合现在 desk 需要的“**把素材拆成可复现实盘组件**”的节奏。

---

## 6. 对 short-cycle desk，最值得拿走的不是 dashboard，而是这条 desk 版策略壳
我会把这条 repo 里的核心思想，压成下面这个更适合我们 desk 的版本。

### 6.1 desk 版主结论
> **先用 BTC+ETH 双 benchmark 定义 alt 的 fair value，再做 residual z-score 回归；把 liquidity / vol / stability / funding 当 admission gate，而不是把 news / macro 当主信号。**

这意味着它服务的是一条非常标准、但很实用的 raw alpha：

- **raw alpha 本体**：beta-adjusted relative-value mean reversion
- **gate**：liquidity / volatility / residual stability / funding
- **可选 overlay**：BTC regime / macro / sentiment / news

### 6.2 为什么这条线特别适合 `5m / 15m`
因为这类 fair-value gap 信号最怕两件事：

- 太慢，回归已经走完才看到；
- 太快，纯噪音把 z-score 搞脏。

`15m` 正好是个还不错的折中层：

- 足够快，能抓 intraday dislocation；
- 又没有 `1m` 那么吃微观结构噪音；
- 很容易把 7d / 3d / 1d 这些窗口映射成稳定统计量。

如果要往 `5m` 推，我反而建议：

- 保留 fair-value 框架；
- 但把 admission 设计得更严格；
- 尤其要对 `volume gate` 和 `fill model` 重标定。

### 6.3 一个更适合我们 desk 的可执行版本
#### 交易对象
- Binance USDⓈ-M 前 `10~20` 个最活跃 perp
- benchmark：`BTCUSDT + ETHUSDT`

#### fair-value 模型
每个 alt 在每个 bar 做：

```text
log(alt) = a + b1*log(BTC) + b2*log(ETH)
```

得到：

- `fair_value`
- `residual_log`
- `z_score`

#### 入场
- `|z| >= z_entry`
- `residual stability >= threshold`
- `rolling realized vol <= max_vol`
- `quote volume >= liquidity_floor`
- `|funding| <= funding_cap`

其中：
- `z_entry` 初始先测 `{1.5, 1.75, 2.0, 2.25}`
- `liquidity_floor` 不要直接抄死 `2.5m`，而是改成：
  - 绝对值版：`{0.5m, 1.0m, 2.0m}`
  - 或分位版：`过去 30 天本币同周期 volume 的 50% / 70% / 85% 分位`

#### 方向
- residual / deviation 为负 → LONG
- residual / deviation 为正 → SHORT

#### 离场
优先测三种：
1. `z` 回到 `0 ~ ±0.25`
2. 固定持有 `H ∈ {8, 16, 24, 32}` bars
3. 先到 time-stop 或 opposite signal 就平

#### sizing / risk
- 单笔风险预算：`0.5% ~ 1.0%`
- 并发：`1~3` 个最高分候选
- stop：`2.0% ~ 4.0%` 或 `k * residual-vol`
- take-profit：`1.25x ~ 2.0x stop`
- 日内 kill-switch：`2R` 或 `3R`

#### 成本
- taker-only：`8 ~ 12 bps`
- maker/taker mix：`4 ~ 8 bps`
- 另加保守滑点：`1 ~ 3 bps`

---

## 7. 最小实验应该怎么测
这是这篇最重要的部分：别只停在“能看懂源码”。

## 7.1 第一轮最小实验
### 目标
先验证：

> **BTC+ETH fair-value gap 的 residual z-score，在 crypto short-cycle 上是否有稳定回归边。**

### 实验口径
- 交易所：Binance USDⓈ-M（优先 perp，不要 spot/perp 混搭）
- 周期：`15m` 主测，`5m` 次测
- universe：前 `10~20` 个高流动 USDT perp
- benchmark：`BTCUSDT + ETHUSDT`
- 训练/滚动窗口：
  - 回归窗：`{5d, 7d, 10d}`
  - z-score 窗：`{2d, 3d, 5d}`
- entry：`|z| ∈ {1.5, 1.75, 2.0, 2.25}`
- exit：`z→0` / `time-stop` / `opposite signal`
- cost：`6 / 8 / 10 / 12 bps`

### 关键输出
至少看这 8 个：

- gross Sharpe
- net Sharpe
- turnover
- avg holding bars
- hit rate
- payoff ratio
- MDD
- capacity proxy（按 volume / top-book notional）

## 7.2 第二轮：只改一件最关键的事——volume gate
这轮 live probe 已经给了一个很明确的信号：

- 15m 上 base alpha 是活的；
- 但 spot `2.5m` quote-volume gate 会过严。

所以第二轮最该做的不是先叠 news，而是先做：

> **absolute liquidity floor vs rolling percentile liquidity floor**

也就是比较：

- 固定 `2.5m`
- 固定 `1.0m`
- rolling 70% 分位
- rolling 85% 分位

看看哪种更适合 `15m`。

## 7.3 第三轮：测双 benchmark 是否真优于单 benchmark
把下面几种并排：

1. `alt ~ BTC`
2. `alt ~ ETH`
3. `alt ~ BTC + ETH`
4. `alt ~ market basket`

这一步很关键，因为如果 `BTC+ETH` 没明显优于 `BTC only`，那实盘就该选更简单、更稳的版本。

---

## 8. 这条题材的主要风险与注意点

### 8.1 repo 现在是 spot klines + futures funding 混搭
这在研究阶段不是致命问题，但在实盘迁移上要小心：

- 信号最好和交易 venue 尽量一致；
- 否则 volume、funding、basis、执行成本口径会有偏差。

所以 desk 版最好直接改成：

- **perp close / perp volume / perp funding 全套一致口径**。

### 8.2 rolling OLS 在 regime 切换时会漂
fair-value 模型本身不是圣杯：

- beta 会变；
- ETH 主导和 BTC 主导会切换；
- 单靠固定窗口 OLS，遇到风格突变会失真。

所以后续可加：

- beta half-life
- EWLS
- regime-conditioned coefficient reset

但这些是第二阶段，不应该妨碍先做最小实验。

### 8.3 这条策略不是“任何偏离都能回”
当偏离来自：

- listing / delisting
- chain exploit
- token unlock
- governance event
- 巨额 liquidation cascade

那 fair-value gap 可能不是 mispricing，而是真实 re-pricing。

所以后续要加一个很实用的 veto：

- **event / news shock veto**

但注意：这仍然是给 raw alpha 加保护，不是把主题改成 filter digest。

---

## 9. 这轮结论
如果只用一句话总结：

> **这份 2026 新 repo 最值得 desk intake 的，不是它的 dashboard，也不是它附带的宏观/新闻模块，而是那条很清楚的 raw alpha：用 BTC+ETH 双 benchmark 定义 alt fair value，再做 residual z-score mean reversion。**

它为什么值得进研究池：

1. **base alpha 清楚**：不是 filter 伪装成 alpha；
2. **可独立复现**：全用 Binance 公共数据就能做；
3. **可直接落地完整策略**：entry / exit / sizing / risk / cost 源码都有；
4. **和 short-cycle desk 直接相关**：15m profile 已经内建；
5. **live probe 说明信号活着**：当前 `15m` 上 SOL / XRP 都出现了明显 fair-value gap，只是 default volume gate 对 spot 15m 偏严。

如果本轮只留一个“下一步就该测”的任务，我的答案是：

> **先把这条 BTC+ETH fair-value gap alpha 用统一的 Binance perp 口径，在 `15m` 上做一轮 volume-gate 重标定 + z-score / exit 网格测试。**

这一步做完，才能判断它到底是：

- 可直接实盘的主 alpha，还是
- 一个很适合挂在更大 relative-value book 里的 admission shell。

---

## 10. 来源链接

### Repo / readable
- Repo homepage: <https://github.com/joanduso/crypto-relative-value-engine->
- README: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/README.md>

### 关键源码
- `feature_engine.py`: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/feature_engine.py>
- `signal_engine.py`: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/signal_engine.py>
- `interval_profiles.py`: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/interval_profiles.py>
- `engine.py`: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/engine.py>
- `risk_engine.py`: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/risk_engine.py>
- `backtest.py`: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/backtest.py>
- `monitor.py`: <https://github.com/joanduso/crypto-relative-value-engine-/blob/main/monitor.py>

### 公共数据端点
- Binance spot klines: <https://api.binance.com/api/v3/klines>
- Binance futures funding history: <https://fapi.binance.com/fapi/v1/fundingRate>
