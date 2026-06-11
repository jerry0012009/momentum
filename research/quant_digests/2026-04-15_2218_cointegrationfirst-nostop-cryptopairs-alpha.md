# 别把这篇 2023 crypto pairs 论文只读成“又一篇配对教材”：对 short-cycle desk，更该先保留的是「cointegration-first pair admission × no-stop intraday spread fade」这条 raw alpha

- 时间：2026-04-15 22:18 UTC
- 类型：2023 SSRN 论文摘要/实现镜像复核（QuantBuffet strategy mirror + Harbourfront 摘要转述 + Crossref/OpenAlex/author page）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**先用 `cointegration` / 长关系筛 pair，再在日内交易阶段做 spread deviation fade：当两条腿的相对价格偏离历史均衡太多时，做多低估腿、做空高估腿，赌的是相对错价回归，而不是单腿方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（至少可先落成一个完整 baseline；论文原始最优参数仍需后续 paper-faithful 复核）
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/pair-admission/no-stop/intraday/spread-zscore/top20-universe/hourly/daily/15m/5m/paper/abstract-mirror/public-data/cost/risk
- 证据类型：paper abstract + strategy mirror + metadata + public-data portability

## 1. 这次看了什么
这轮主看的是：

- **Authors：** Chiara Lesa, Ronald Hochreiter
- **Year：** 2023
- **Title：** *Cryptocurrency Pair Trading*
- **Venue：** SSRN Electronic Journal
- **DOI：** `10.2139/ssrn.4433530`
- **Readable URL：** <https://doi.org/10.2139/ssrn.4433530>
- **辅助可读来源：**
  - QuantBuffet 策略镜像页：<https://quantbuffet.com/en/2024/04/15/pairs-trading-in-cryptocurrencies/>
  - Harbourfront 摘要转述页：<https://harbourfrontquant.substack.com/p/pairs-trading-in-the-cryptocurrency>
  - 作者页面条目：<https://www.hochreiter.xyz/>
- **Repo URL：** N/A（未见作者公开 GitHub 仓库）

先把一句话说清楚：

> **这篇东西的 base alpha 很清楚，不是“大盘会涨/跌”，而是 cointegrated pair 的相对错价会回归。**

所以它不是 filter，不是 regime，也不是解释型综述。它本体就是一条可以直接写成交易规则的：

> **pairs / stat-arb / relative-value / mean-reversion raw alpha。**

我这次没有把它读成“又一篇讲配对交易原理的论文”，而是先抓里面对我们 desk 最有交易意义的分叉：

> **如果要把它翻成短周期 desk 的第一版 baseline，更值得先保留的不是 `distance-first`，而是 `cointegration-first pair admission × no-stop intraday spread fade`。**

这也正好和今天稍早 intake 的那篇 2024 pairs 方法横评形成一个很有用的对照：
- 2024 那篇更像在说：**simple distance baseline 非常值得先跑**；
- 这篇 2023 working paper 则在提醒：**真正进到交易层时，cointegration-selected pairs 通常更稳，而 stop-loss 反而可能把 intraday pairs 的 edge 砍掉。**

## 2. 一句话核心结论
> **对 crypto short-cycle desk 来说，这篇 paper 最值得保留的不是“pairs trading 也能做”这种空话，而是：pair admission 优先保留 cointegration，执行层优先保留 no-stop 的 spread fade baseline——因为 intraday 交易虽然更赚钱，但一旦机械加 stop-loss，优势会明显变差。**

## 3. 它是怎么证明这件事的
一句话版：

> **作者把 `Distance` 和 `Cointegration` 两类 pair selector，放在同一批 crypto、同一 formation/trading 切分、同一 daily/hourly 频率框架下对比，并同时检查 trading frequency 与 stop-loss 对结果的影响。**

翻成人话：
- 不是只证明“pairs 在 crypto 有时能赚钱”；
- 而是更具体地问：
  1. **pair 怎么选更好？**
  2. **日内做是不是比日频更强？**
  3. **止损到底是保护你，还是把 edge 自己切掉？**

这比一般“pairs 教程型”材料更值钱，因为它直接碰到 production 最常见的三个问题：
- admission
- frequency
- risk rule

## 4. 论文里最值得记住的硬信息
### 4.1 研究对象与设计
从 QuantBuffet 镜像页、Harbourfront 转述和公开元数据可交叉确认：

- **Universe：** top 20 cryptocurrencies（按市值）
- **方法主轴：** `Distance Method` vs `Cointegration Method`
- **formation / trading 切分：** `2 : 1`
- **比较维度：**
  - pair selection method
  - trading frequency（daily vs hourly / intraday）
  - 是否加 stop-loss

这已经足够说明：

> **它不是只给一个“找两条腿做回归”的模糊想法，而是明确把 selection、execution frequency、stop policy 都摆上了台面。**

### 4.2 摘要里最重要的结论
公开摘要和二级转述里，最值得记的不是收益曲线，而是这 4 句：

1. **formation period 的频率，不太影响最终选出的 pairs。**
2. **Cointegration-selected pairs 一般优于 Distance-selected pairs。**
3. **intraday trading 更赚钱。**
4. **但一旦加 stop-loss，这个 intraday 优势会明显变差。**

还有一句很关键：

5. **Distance 方法因为成交次数更多，交易成本更伤。**

把它翻成 desk 语言就是：

> **distance-first 更像“便宜好跑的 baseline/候选池生成器”；真正到了要交易的那一层，cointegration pair admission 往往更适合做主 baseline，而 hard stop 则要非常谨慎。**

### 4.3 二级实现镜像给出的 baseline 数字
QuantBuffet 的策略镜像页给了一组可参考的实现型指标：

- **Annualized Return：** `70.4%`
- **Volatility：** `39.76%`
- **Sharpe Ratio：** `1.77`
- **Maximum Drawdown：** `-21%`
- **Win Rate：** `58%`

这些数我不会直接当作“论文原表精确复刻”，但它们至少说明两件事：

1. **这条 base alpha 能很自然地写成完整回测规则；**
2. **它不是那种只能停留在概念层的 pairs 论文。**

### 4.4 镜像代码里最有用的参数骨架
QuantBuffet 页面上的代码镜像虽然不是作者原仓，但足够给我们第一版 baseline 壳：

- **pair_count：** `6`
- **entry threshold：** 约 `2σ`
- **close / take-profit 逻辑：** z-score 回到均值附近就平
- **position shape：** long one leg / short the other leg
- **capital slicing：** 组合资金按 pair 数均分

这意味着：

> **至少在工程上，entry / exit / sizing 的第一版骨架已经是完整的，不需要我们再从零脑补。**

## 5. 为什么这篇现在值得 intake
### 5.1 它补的是“pairs 交易层”，不是再补 admission 综述
最近几天 intake 里，pairs / stat-arb 已经不少：
- distance-first selector
- dynamic factor basket
- copula mispricing
- cluster-first / network-first pair admission
- validation-ranked spread fade

但这些材料里，很多更偏：
- selector ranking
- pair admission
- 复杂模型增强

而这篇的价值在于：

> **它直接把 selection + trading frequency + stop-loss 放进同一张桌子上。**

也就是说，它不是只在回答“怎么找 pair”，而是在回答：

> **pair 找完以后，交易层最容易把 edge 搞坏的地方是什么？**

### 5.2 它给了一个很重要的反直觉提醒：别本能加 stop-loss
很多人看到 stat-arb / pairs，第一反应都是：
- 既然是 mean reversion，
- 那我就顺手加个 hard stop，
- 看起来更安全。

但这篇最值钱的分叉恰恰是：

> **在 intraday crypto pairs 里，stop-loss 不一定在帮你控风险，反而可能在最需要“等回归”的地方把你洗出去。**

这对 short-cycle desk 很关键，因为这类策略和 breakout/trend 完全不同：
- breakout 里，止损往往是在切错误方向；
- pairs MR 里，止损有时是在切“尚未回归完成的临时偏离”。

所以这篇不是在说“永远不要止损”，而是在提醒：

> **pairs 的风险控制，不该先默认用单腿 directional 那套 hard stop；更该先测的是 time-stop、spread-stop、gross exposure cap、cointegration break veto。**

### 5.3 它也给 raw alpha 池补了一条更完整的母板
这篇对当前 desk 更实用的原因是：

- base alpha 很清楚；
- 可写成完整 long-short 规则；
- 不依赖私有数据；
- 能较快映射到 `15m / 5m`；
- 同时还能自然拆出 risk layer。

所以它不是“再讲一遍 pairs 基础课”，而是：

> **给 short-cycle crypto desk 补一条可直接落成 baseline 的 relative-value raw alpha 母板。**

## 6. 策略拆解（先把完整策略骨架说清楚）
- **方向属性：** market-neutral / long-short / pairs / stat-arb / relative-value / mean-reversion
- **基础 alpha：** cointegrated pair 的 spread 偏离历史均衡后，后续有回归倾向
- **entry：**
  - 先做 pair admission：优先选 cointegration 更稳定、交易成本更可控的 pair
  - 再做 spread 标准化：当 `z-score` 超过阈值（比如 `±2`）时开仓
  - `z > +entry`：short rich leg / long cheap leg
  - `z < -entry`：long rich? 不对，应该是 **long cheap leg / short rich leg**
- **exit：** z-score 回到均值或接近均值时平仓；若到达 time-stop 仍未回归，也应退出
- **sizing：** 先按 pair 数均分 gross notional；第二版再加 volatility scaling / liquidity cap / gross exposure cap
- **risk：**
  - 不先默认上 hard stop
  - 优先测 `spread-stop`、`time-stop`、`pair-level gross cap`、`cointegration break veto`
  - 若 hedge ratio 漂移过快，视为 admission 失效而强平
- **cost：** 论文摘要明确提醒 `Distance` 因为成交更多更容易被 cost 吃掉；迁移到 perp 时至少做 `5 / 10 / 20 / 30 bps` ladder
- **filter / veto：** funding conflict、盘口深度不足、两腿成交不同步、carry 方向冲突、事件期异常波动

## 7. 对 short-cycle desk 的正确翻译
### 7.1 这不是“日内追方向”，而是“日内做相对错价回归”
这条 alpha 的关键不是猜 BTC 会涨还是跌，而是：

> **两条腿之间偏太远时，做收敛。**

所以它特别适合补当前 raw alpha 池里相对价值这条线，而不是继续只围着单腿趋势或单腿反转打转。

### 7.2 `15m / 5m` 的最自然迁移方式
论文/镜像里写的是 daily 与 hourly，对我们 desk 最自然的迁移姿势是：

- **状态层：** `1h` 或 `4h`
  - 做 pair admission
  - 更新 hedge ratio / cointegration 检查
  - 生成可交易 pair 列表
- **执行层：** `15m` 或 `5m`
  - 算 rolling spread z-score
  - 在 spread 偏离明显时入场
  - 用 time-stop / spread-normalization 出场

也就是说：

> **这条策略不是慢频素材不能用，而是非常适合“慢 admission + 快 execution”的 desk 化拆法。**

### 7.3 这篇服务的是哪类 raw alpha
它直接服务于：
- `pairs`
- `stat-arb`
- `relative value`
- `mean reversion`

如果后面还要叠加别的层，最自然的是：
- funding veto
- liquidity veto
- event veto
- spread-cost veto

而不是先把它改造成另一个复杂模型。

## 8. 最小可复现实验
### 8.1 数据源、公开性、更新频率
- **数据源：** Binance USDⓈ-M perpetual public klines
- **公开性：** 完全公开 REST
- **更新频率：** `1m`
- **本轮 portability quick check：** `BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT / BNBUSDT` 的 Binance USDⓈ-M `15m` K 线可正常拉取，最新样本时间对齐到 `2026-04-15 22:00 UTC`
- **最小可复现实验口径：**
  1. 先拿 8~20 个 liquid majors 建 universe；
  2. 用 `1h` 滚动窗口做 pair admission；
  3. 先比较 `cointegration-first` vs `distance-first`；
  4. 对入选 pair 在 `15m` 上做 spread z-score fade；
  5. 执行层再下钻 `5m`；
  6. 显式比较 `no-stop` vs `hard-stop`。

### 8.2 第一轮 baseline 我建议这样写
**版本 A：paper-to-desk baseline**
1. Universe：`BTC / ETH / SOL / XRP / BNB / ADA / DOGE / LINK ...` liquid majors
2. Admission：rolling `1h` close 上做 Engle-Granger / 简化 cointegration 筛选
3. Hedge ratio：rolling OLS
4. Signal：spread z-score（`lookback = 96` 个 `15m` bar 起步）
5. Entry：`|z| >= 2.0`
6. Exit：`z` 回到 `0 ~ 0.5` 区间
7. Risk：只先用 `time-stop`（例如 `16~32` 个 `15m` bar），**不先上硬止损**
8. Cost：双边 `5 / 10 / 20 / 30 bps`

### 8.3 下一步怎么测
下一步不要再泛泛谈“pairs 是否有效”，直接做下面 5 个 A/B：

1. **Admission A/B：cointegration-first vs distance-first**  
   看当前 liquid-major perp 环境里，哪一层更稳、哪一层 turnover 更低。

2. **Execution A/B：`15m` signal × `15m` entry vs `15m` signal × `5m` execution**  
   看快执行能不能降低入场噪声与双腿错位。

3. **Risk A/B：no-stop vs hard-stop vs time-stop**  
   这是这篇 paper 最值得我们亲自复核的分叉，不要跳过。

4. **Threshold A/B：`1.5σ / 2.0σ / 2.5σ`**  
   看 edge 到底更怕噪声，还是更怕机会太少。

5. **Cost A/B：spot proxy vs perp proxy / taker vs maker-first**  
   复核论文里“Distance 被 cost 吃得更厉害”这句，看看在 today perp 上是否仍成立。

### 8.4 第一批必须盯的指标
- pair-level 与 portfolio-level `gross / net Sharpe`
- `trade count`
- `median holding time`
- `half-life` 与实际持仓时长的错配程度
- `stop-out rate`
- `mean reversion completion rate`
- `spread excursion before reversion`
- `entry-to-fill slippage`
- `cointegration break frequency`

## 9. 风险与保留意见
- **当前主证据并非论文全文。** 我们能清楚确认 base alpha、结论方向和一版完整实现骨架，但若要做 paper-faithful replication，后续仍应补全文。
- **QuantBuffet 页面是实现镜像，不是作者原始代码仓。** 里面的具体参数可作为 baseline，但不应直接当作者最终最优参数。
- **pairs MR 很怕“看起来 market-neutral，实际是两条腿一起崩”。** 所以 production 风险控制不能只看 spread，还要看腿间流动性与同步成交。
- **no-stop 不等于不控风险。** 这篇最有价值的提醒是“别默认用 hard stop”，不是“什么 stop 都不要”。
- **如果迁移到 perp，两腿 funding 方向可能会把纯 spread edge 改写。** 所以 funding conflict 应该是第二层必测 veto。

## 10. 来源
1. **Lesa, C., & Hochreiter, R. (2023). _Cryptocurrency Pair Trading_. SSRN Electronic Journal.**
   - DOI: `10.2139/ssrn.4433530`
   - Readable URL: <https://doi.org/10.2139/ssrn.4433530>
2. **Crossref metadata**
   - <https://api.crossref.org/works/10.2139/ssrn.4433530>
3. **OpenAlex metadata**
   - <https://api.openalex.org/works?filter=doi:10.2139/ssrn.4433530>
4. **QuantBuffet strategy mirror / code mirror**
   - <https://quantbuffet.com/en/2024/04/15/pairs-trading-in-cryptocurrencies/>
5. **Harbourfront 摘要转述**
   - <https://harbourfrontquant.substack.com/p/pairs-trading-in-the-cryptocurrency>
6. **Author page reference**
   - <https://www.hochreiter.xyz/>
