# 别把这篇 2022 SSRN BTC 论文只读成“seasonality 小品文”：对 short-cycle desk，更该先拆的是「10-day local-extrema branch-split long router」这条 raw alpha

- 时间：2026-04-13 11:45 UTC
- 类型：2022 SSRN 论文摘要镜像/策略代码镜像复核（PapersWithBacktest + QuantBuffet）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题标签：raw-alpha/single-asset/major-only/trend-following/mean-reversion/local-extrema/10day-high/10day-low/branch-split/long-only/router/btc/eth/sol/binance-perpetual/15m/5m/paper/public-data/cost/risk
- 证据类型：论文摘要镜像 + 二次代码镜像 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**把“价格来到 rolling 10-day 局部极值”拆成两条独立 long 信号：触发 10-day 新高时做顺势 continuation，触发 10-day 新低时做 drawdown-bounce mean reversion；不要把高点分支和低点分支粗暴并成同一条规则。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 这次看了什么

这轮看的是一篇 2022 BTC 论文及其可读镜像/代码镜像：原论文同时谈了 seasonality、trend-following、mean reversion，但对 short-cycle desk 真正更值钱的不是“NYSE 开收盘时段”那层，而是一句很容易被忽略的话——**BTC 在局部高点更容易顺势，在局部低点更容易反弹。** 我把它直接翻译成一个可复现 raw alpha 壳：`10-day local extrema -> branch-split long router`，再用 Binance USDⓈ-M `BTC/ETH/SOL` 的 `15m/5m` 公共 K 线做最小 portability probe。

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = “rolling 10-day 局部极值的分支化 long 路由”。** 价格创近 10 天新高，不把它当 overbought 反手，而是先测 continuation long；价格刷近 10 天新低，不把它当单纯崩掉，而是先测 bounce long。

翻成人话：
- 这不是“见高就空、见低就多”的对称反转；
- 也不是“突破就追 / 回撤就抄底”这种口号式总结；
- 它真正要表达的是：**同样都是局部极值，顶部和底部对应的后续动力学不一样。**
  - `local max` 更像趋势延续；
  - `local min` 更像回撤后的弹回；
- 所以它天然不是一条单一规则，而是**两个子 alpha**。

这也是为什么它应该被归类为 `raw alpha`，而不是 `filter / regime / overlay`：
- 局部极值本身就是 entry 触发条件；
- 后续 flat / hold-horizon 就能构成最小交易壳；
- 不需要先依附别的主信号才能成立。

## 3. 这次看的来源

### 主来源（paper）
- **Authors：** Matúš Padyšák, Radovan Vojtko
- **Year：** 2022
- **Title：** *Seasonality, Trend-following, and Mean reversion in Bitcoin*
- **Venue：** SSRN Electronic Journal
- **DOI：** <https://doi.org/10.2139/ssrn.4081000>
- **Readable URL：** <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4081000>
- **Repo URL：** N/A

### 可读摘要镜像
- **PapersWithBacktest strategy page：** <https://paperswithbacktest.com/strategies/seasonality-trend-following-and-mean-reversion-in-bitcoin>
- **QuantBuffet strategy page（含 Lean 代码镜像）：** <https://quantbuffet.com/en/2024/04/13/mean-reversion-and-trend-following-based-on-min-and-max-in-btc/>

这两个镜像都保留了同一条核心描述：
- BTC 在局部最大值附近更容易 trend；
- BTC 在局部最小值附近更容易 bounce back；
- QuantBuffet 还给了一个非常原始但可执行的 long-only 代码镜像：**当日价格等于过去 10 天 max 或 min 时开多，持有一天。**

### 本轮本地 artifacts
- Probe script：`reports/artifacts/quant_digests/2026-04-13_localextrema_probe.py`
- Probe metrics：`reports/artifacts/quant_digests/2026-04-13_localextrema_probe_metrics.csv`

## 4. 这条线为什么值得写进当前池子

它值得进池，不是因为“又一个 BTC 形态说法”，而是因为它补了当前研究池里一个挺缺的缝：

1. **它是明确的 raw alpha，不是又一个 shared gate。**
   - 最近池子里已经有不少把结构、资金费率、波动或盘口当 gate / veto 的材料；
   - 这条线更朴素：**极值本身就是方向触发。**

2. **它把 trend 和 mean reversion 放进同一个母题里，但不是混着做。**
   - 很多研究会把两者写成“市场有时趋势、有时反转”；
   - 这篇东西真正有用的地方，是给了一个很具体的路由点：**local max vs local min。**

3. **它对 short-cycle desk 很友好。**
   - 不需要外部数据；
   - 不需要订单簿或链上；
   - 用公开 K 线就能做最小实验；
   - 而且能自然映射到 `15m / 5m`。

4. **它不是近期 digest 的重复。**
   - 不是 pairs；
   - 不是 funding / basis；
   - 不是 LVN / profile；
   - 也不是前几天那篇 cross-sectional `MAX effect` 的“彩票型极端值高估值 fade”。

## 5. 最重要的读法修正：不要照抄“max 或 min 都做多”的合并规则

QuantBuffet 镜像里的最小代码壳是：
- 计算过去 10 天 max / min；
- 若当前价格等于 max 或 min，则开多；
- 持有 1 天；
- 其余时间空仓。

这个壳有个优点：**非常容易复现。**

但如果直接把它读成：
> “哦，反正碰到 10-day max 或 10-day min 都做多就行。”

那就会把论文里最有价值的信息抹平掉。对 desk 来说，正确的拆法应该是：

- **分支 A：`local max -> continuation long`**
- **分支 B：`local min -> rebound long`**

然后分别回答：
- 它们是不是该用同样的 holding horizon？
- 它们是不是该跑在同一批币上？
- 它们是不是能共享同样的 veto / cost budget？

如果这些问题不分开测，最后常见结果就是：
- 强分支把弱分支抹掉；
- 合并回测看起来一般；
- 然后你误以为“这条线没用”。

## 6. public-data portability probe：我怎么把它翻到 `15m / 5m`

### 6.1 probe 口径
- **市场：** Binance USDⓈ-M Perpetual
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT`
- **频率：** `15m`、`5m`
- **历史：** 最近约 `120` 天公开 K 线
- **lookback：** `10` 天 rolling extreme
- **触发：**
  - `max_branch`：当前 close 创 rolling 10-day 新高
  - `min_branch`：当前 close 创 rolling 10-day 新低
- **执行近似：** 下一根 bar `open` 入场
- **退出：** 固定 horizon time-stop，`no-overlap`
  - `15m`: 测 `24 / 36` bars
  - `5m`: 测 `36` bars
- **方向：** long-only
- **成本：** 当前结果只看 gross，不含 fee / slippage / funding

### 6.2 为什么这样翻
原论文/镜像是日频表达，short-cycle desk 不能机械照搬“一天持有”。
所以我保留它的核心母体：
- **10-day extreme 是信号源；**
- **max / min 是两条不同分支；**
- **其余全部简化成最容易落地的 next-open + fixed-horizon。**

这个 probe 的目的不是宣布“策略已毕业”，而是先回答三个问题：
1. 这条线有没有 gross pocket？
2. `max_branch` 和 `min_branch` 是不是本来就该分开看？
3. 它更像 BTC-only，还是 majors 才能迁移？

## 7. 关键结果：真正有价值的不是“极值都做多”，而是**branch split + major filter**

## 7.1 BTC：`15m` 顶部 continuation 有料，底部 branch 反而拖后腿

### `BTCUSDT 15m | 24 bars`
- `max_branch`：**20 笔**，平均 **`+35.05 bps/trade`**，胜率 **`50.0%`**
- `min_branch`：**22 笔**，平均 **`-75.65 bps/trade`**，胜率 **`36.4%`**
- `combined`：**42 笔**，平均 **`-22.93 bps/trade`**

这组数非常关键：
- 如果你把论文简化成“碰到极值都做多”，那在最近这段 `BTC 15m` 上是**负的**；
- 但如果只保留 `local max -> continuation` 这个分支，gross 是正的，而且不薄。

### `BTCUSDT 5m | 36 bars`
- `max_branch`：**26 笔**，平均 **`+2.70 bps/trade`**
- `min_branch`：**33 笔**，平均 **`+11.56 bps/trade`**，胜率 **`57.6%`**
- `combined`：**59 笔**，平均 **`+7.66 bps/trade`**

这说明：
- BTC 到了更快的 `5m`，强分支反而切到 `local min -> rebound`；
- 同一个母题，在不同时间尺度上**主导分支会换**。

## 7.2 ETH：portability surprisingly strong，但依然是 branch-sensitive

### `ETHUSDT 15m | 24 bars`
- `max_branch`：**18 笔**，平均 **`+63.27 bps/trade`**，胜率 **`72.2%`**
- `min_branch`：**24 笔**，平均 **`-43.36 bps/trade`**
- `combined`：**42 笔**，平均 **`+2.34 bps/trade`**

### `ETHUSDT 5m | 36 bars`
- `max_branch`：**22 笔**，平均 **`+19.99 bps/trade`**
- `min_branch`：**34 笔**，平均 **`+55.83 bps/trade`**，胜率 **`64.7%`**
- `combined`：**56 笔**，平均 **`+41.75 bps/trade`**

ETH 给的启发是：
- 这不是只能写进 BTC 角落的一次性 observations；
- 至少在 recent sample 里，**major coin 的局部极值路由是能迁移的**；
- 但它依然不能被粗暴地统一成“极值 long-only 万能规则”，因为 `15m` 的强分支是顶部 continuation，`5m` 的强分支更偏底部 bounce。

## 7.3 SOL：说明这条线不是“全市场普适”

### `SOLUSDT 5m | 36 bars`
- `max_branch`：**26 笔**，平均 **`-33.38 bps/trade`**
- `min_branch`：**38 笔**，平均 **`-29.29 bps/trade`**
- `combined`：**64 笔**，平均 **`-30.95 bps/trade`**

### `SOLUSDT 15m | 24 bars`
- `combined`：**50 笔**，平均 **`-16.75 bps/trade`**

SOL 的作用不是“再找个失败样本”，而是明确告诉我们：
> 这条线更像 `BTC / ETH` 这种 major behavior alpha，而不是适合随手扩展到高 beta alt 的通用模板。

## 8. 对当前 desk 的真正落点：把它当成两个子书，不要当成一个统一壳

我现在对这条线的最实用结论是：

1. **不要直接部署 `max_or_min -> long` 合并书。**
   - 合并后经常被弱分支拖掉；
   - recent sample 里 `BTC 15m combined` 就是直接转负。

2. **先拆成两条子书。**
   - `Book A`: `local max -> continuation long`
   - `Book B`: `local min -> rebound long`

3. **优先从 majors 做，不要一开始就铺到 SOL / alt。**
   - 当前 portability 更像 major behavior；
   - alt 上噪声、反身性和单边挤压更容易把这个结构打碎。

4. **时间尺度要分别校准。**
   - `15m` 先优先看 `max_branch`
   - `5m` 先优先看 `min_branch`

这就让它不再是“BTC 论文里的一个趣味观察”，而是能转成 desk 语言的一组明确模块：
- 顺势 continuation 子书
- drawdown-bounce 子书
- major-only universe filter
- fixed-horizon / time-stop execution 壳

## 9. 策略拆解（必填）

- 方向属性：single-asset / long-only / branch-split
- 基础 alpha：`10-day local extrema`
- 分支 1：`local max -> continuation`
- 分支 2：`local min -> rebound`
- regime：先限 `BTC / ETH` 这类 liquid majors
- 执行：next-bar open 或更保守的 break/reclaim 确认
- 退出：固定 horizon time-stop，优先不要把两分支共享同一个 horizon
- risk / sizing：固定风险预算；单笔 notional cap；`no-overlap`
- cost：先压 `6 / 10 / 15 bps per side` 看剩余 edge

## 10. 下一步怎么测（必须项）

1. **先把两分支彻底拆开做独立 grid，而不是继续看 combined。**
   - `max_branch` 单独扫 `8 / 12 / 24 / 36` bars
   - `min_branch` 单独扫 `8 / 12 / 24 / 36` bars
   - 看每个 symbol / timeframe 各自最优 horizon

2. **给 `local max` 和 `local min` 加不同的 regime veto。**
   - `max_branch`：加 trend-strength / ADX / slope filter
   - `min_branch`：加 oversold stretch / ATR shock / volume capitulation filter
   - 不要假设两分支共享同一套 veto

3. **从 close-trigger 升级到更可成交的 intrabar 结构。**
   - 例如 `突破 10-day max 后的下一次 pullback reclaim` 再进
   - 或 `跌破 10-day min 后的第一根反包` 再进
   - 这能直接回答：当前 edge 是 close-based 偶然，还是更底层的行为结构

4. **用 majors-only 做 first pass post-cost。**
   - 先只保留 `BTC / ETH`
   - 成本压 `6 / 10 / 15 bps per side`
   - 若 gross 很快被吃光，再考虑 maker-first / passive entry

5. **别急着扩 universe，先测“分支共享是否错误”。**
   - 这轮最重要的发现不是哪个币最强；
   - 而是**统一合并规则本身可能就是错的。**

## 11. 风险与保留意见

- 原论文主战场是 BTC，ETH/SOL 这里只是 portability probe，不应被误当成论文原结论；
- 当前样本只覆盖最近约 120 天，可能包含较强的趋势/反弹 regime 偏差；
- 结果只看 gross，不含手续费、滑点、资金费率；
- `max_branch` 的正收益有时来自少数较大赢家，不能只看平均 bps；
- `min_branch` 在 BTC/ETH/SOL 之间分化很大，说明它比 continuation 分支更 regime-sensitive。

## 12. 一句话结论

> 这篇 2022 BTC 论文对 short-cycle desk 最值得接的，不是“某个时段 seasonality”，而是 **10-day 局部极值的分支化 long 路由**：`local max` 更像 continuation，`local min` 更像 rebound，但两者绝不能粗暴并成一条统一规则。最近的 Binance majors probe 里，`BTCUSDT 15m` 的 `max_branch` 有 **20 笔 / +35.05 bps`gross`**，而同口径 `combined` 反而是 **-22.93 bps/trade**；`ETHUSDT 5m` 的 `min_branch` 则有 **34 笔 / +55.83 bps`gross`**。所以这条线值得进 raw alpha 素材池，但进入复现排期前，必须先做 **branch split + majors filter + post-cost**。

## 13. 本轮产物

- 研究笔记：`research/quant_digests/2026-04-13_1145_localextrema-branchsplit-long-router-alpha.md`
- Probe script：`reports/artifacts/quant_digests/2026-04-13_localextrema_probe.py`
- Probe metrics：`reports/artifacts/quant_digests/2026-04-13_localextrema_probe_metrics.csv`

## 14. 来源

1. **Padyšák, M., & Vojtko, R. (2022). _Seasonality, Trend-following, and Mean reversion in Bitcoin_. SSRN Electronic Journal.**
   - DOI：<https://doi.org/10.2139/ssrn.4081000>
   - Readable URL：<https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4081000>

2. **PapersWithBacktest mirror page**
   - URL：<https://paperswithbacktest.com/strategies/seasonality-trend-following-and-mean-reversion-in-bitcoin>

3. **QuantBuffet strategy page / Lean code mirror**
   - URL：<https://quantbuffet.com/en/2024/04/13/mean-reversion-and-trend-following-based-on-min-and-max-in-btc/>

4. **Binance USDⓈ-M Futures Public API**（本轮 portability probe 实际使用）
   - Kline / Candlestick Data：<https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
