# 别把 crypto 24/7 继续当成“没有 session”：这篇 2023 arXiv 更该先落地的是「UTC 时钟 × 宏观时间戳」共享 gate
- 时间：2026-03-29 10:22 UTC
- 类型：2023 arXiv 全文 PDF + 本地全文抽取 + Binance USDⓈ-M Perpetual 公共 `1m` 近 31 天 quick check
- 主题类型：filter
- 基础 alpha：无独立 raw alpha；它服务于 `trend / breakout / shock continuation` 的 admission，也服务于 `short-term reversal / fade` 的 veto
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：filter/shared-gate/regime/time-of-day/utc-clock/macro-event/quarter-hour/full-hour/session-overlap/weekend/volatility/liquidity/admission/veto/btc/eth/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：全文论文证据 + 公共市场数据 quick check

## 1. 这次看了什么
主材料是 **Wątorek, Skupień, Kwapień, Drożdż (2023), _Decomposing cryptocurrency high frequency price dynamics into recurring and noisy components_**。我重点看了全文 PDF 里的：
- 数据与方法：Binance `10s` 级 BTC / ETH / DOGE / WIN，样本期 `2020-01` 到 `2022-12`
- intraday / intraweek 平均路径
- correlation-matrix / eigensignal 分解
- 论文里的 Table 1（高相关日与美国宏观发布时间对照）

另外我补了一层 desk 化 quick check：
- Binance USDⓈ-M Perpetual `BTCUSDT` 公共 `1m` klines
- 样本约 `44,999` 根 bar，区间 `2026-02-26 04:22 UTC` 到 `2026-03-29 10:20 UTC`
- 只做最小 sanity check：`minute-of-hour`、`hour-of-day`、`weekday-vs-weekend` 的绝对收益强度

这次最值得 intake 的，不是“crypto 也有日历效应”这种泛泛结论，而是：
**即便市场 24/7 连续交易，短周期 desk 仍然可以把“什么时候允许 alpha 发动、什么时候禁止抄底/追价”写成一张可复用的 UTC schedule gate。**

## 2. 核心结论
- **一句话核心结论：** 这篇论文最值钱的不是再证明一遍 crypto 有 intraday seasonality，而是把短周期市场拆成了两部分：
  1. **可重复的外生时钟**：亚洲开盘、欧美重叠、整点/15 分钟、12:30/18:00 美国宏观发布时间；
  2. **更接近噪声的内生波动**：大部分非时钟性微观扰动。
- **一句话它怎么证明：** 论文用相关矩阵 + eigensignal 分解，把 BTC/ETH 的最强重复结构直接对齐到 `12:30 UTC` 的美国宏观发布时间和 `full hour` 的周期性 activity burst；而且周内强度明显高于周末。

几个最值得记住的数据点：
- 论文样本里，BTC / ETH 的**最强同步 intraday eigensignal（`λ1`）集中在 `12:30 UTC`**；作者把相关性最强的日期直接对齐到 **NFP / CPI / PPI / PCE / PI / FOMC statement** 等美国宏观发布时点。
- 论文里 **`λ2` 对应的是整点 activity burst**：BTC / ETH 在 **整点、半点、15 分钟** 都有放大的波动 / 成交 / 交易笔数，其中**整点最强**；WIN 这种低流动币基本没有这个结构。
- 论文的均值路径显示，BTC / ETH 的日内 activity 高峰主要在 **`00:00 UTC`（亚洲时段启动）** 和 **`12:00-16:00 UTC`（欧美重叠）**；周内里 **Friday 最强、weekend 明显更冷**。
- 我补的 Binance perp `1m` quick check 也没打脸这个结论：最近约 31 天的 `BTCUSDT` 上，**整点 minute 平均绝对收益 `5.758 bps`，非整点 `4.952 bps`，高出约 `+16.3%`**。
- 同一 quick check 里，**15 分钟整点族（`00/15/30/45`）平均绝对收益 `5.294 bps`，其他分钟 `4.942 bps`，高出约 `+7.1%`**。
- 同一 quick check 里，**`12:00-15:59 UTC` 平均绝对收益 `6.649 bps`，其余时段 `4.632 bps`，高出约 `+43.5%`**；而 **weekend `3.822 bps`，weekday `5.460 bps`，只有后者的大约 `70%`**。

### 2.1 这份材料真正新增了什么
当前素材池里已经有不少 raw alpha：
- breakout / trend / TSMOM
- short-term reversal / shock fade
- lead-lag / relative value
- funding / basis / carry

但这些 raw alpha 反复会撞到一个共同问题：
**什么时候信号更“像真的”，什么时候只是噪声？**

这篇材料补的正是这块共享层：
- 对 `trend / breakout / continuation`，它提供 **admission windows**：
  - `00:00 UTC` 附近
  - `12:00-16:00 UTC`
  - `00/15/30/45` 分钟
  - 美国宏观发布时间附近（尤其 `12:30 UTC`，以及 FOMC statement 的 `18:00 UTC`）
- 对 `mean reversion / fade`，它提供 **veto windows**：
  - 别在整点/宏观释放时段逆着最强 activity 硬抄
  - 周末 / 低 activity 时段更适合测“没有 follow-through 的冲击后回摆”

换句话说，这篇 paper 更像一个 **shared timing map**，而不是另一个 headline alpha。

### 2.2 需要诚实保留的 caveat
这不是一篇直接给你 entry / exit / sizing 的交易论文，所以它**不能被伪装成完整策略**。

更准确的定位应该是：
- **主题类型：filter**
- **基础 alpha：无独立 alpha，本质上服务于已有 raw alpha**

另外，我这次 quick check 也提醒了一个现实点：
- 论文里 `12:30 UTC` 是在**事件日条件下**很强；
- 但在我做的**无条件近 31 天 `1m` 均值**里，`12:30` 的强度没有大到压过 `15:00` 和 `00:00`。

这说明 desk 真要落地，不能只做“固定 12:30 规则”，而应该分成：
1. **无条件 schedule gate**（整点 / 欧美重叠 / 周末冷时段）
2. **有条件 macro gate**（NFP / CPI / FOMC 等事件日才启用）

## 3. 为什么和当前项目有关
如果只问一句：**它为什么比继续补一个普通 raw alpha 更值得？**

我的答案是：**因为 raw alpha 素材池已经不算薄，但它们现在更缺一个共享的“时间地图”，去减少假突破、假 continuation、以及在最差时段硬做 fade。**

它和当前 short-cycle desk 的关系非常直接：
- `1m / 3m / 5m / 15m` 都天然带有 **minute-of-hour / hour-of-day / weekday** 结构；
- 这篇 paper 给的不是慢频叙事，而是能直接写进 bar-level backtest 的 **时钟型 gate**；
- 同一个 gate 至少可以同时服务两类 alpha：
  - `trend / breakout / continuation`
  - `short-term reversal / mean reversion`

也就是说，它符合这轮优先级里那类：
**可同时服务至少 2 类 alpha 的 shared gate / filter。**

## 3.5 策略拆解（必填）
- 方向属性：shared gate / admission-veto / execution-timing
- 基础 alpha：无独立 raw alpha；默认服务于
  - `breakout / TSMOM / post-shock continuation`
  - `short-term reversal / fade / liquidity provision`
- regime：
  - **hot regime**：`00:00 UTC`、`12:00-16:00 UTC`、整点/15 分钟族、美国宏观发布时间窗口
  - **cold regime**：weekend、非重叠时段、非整点且无宏观窗口的平静时段
- filter / veto：
  - continuation 类只在 hot regime 放行，cold regime 缩仓或拒单
  - reversal 类在 hot regime 尤其是 macro / full-hour 窗口优先 veto
  - macro gate 必须是**事件日条件触发**，不能日常常驻
- risk / sizing / execution overlay：
  - 用 `schedule_score` 做 `0 / 0.5 / 1 / 1.25x` 的仓位倍率
  - hot regime 上调滑点/冲击成本假设，不能沿用静态 fee
  - macro 发布前后 `N` 根 bar 设专门的 no-fade / no-new-risk 规则

## 4. 可复刻的最小实验
### 4.1 研究假设
**同一条 raw alpha，在“对的 UTC 时段”与“错的 UTC 时段”上的 post-cost 表现，应该存在显著分层；而且 continuation 与 reversal 对 schedule 的偏好方向相反。**

### 4.2 数据源、公开性、更新频率
1. **交易所 bar 数据（公开可得）**
   - Binance spot / perp `1m` klines
   - 公开性：公开 API
   - 更新频率：分钟级

2. **宏观事件时间表（公开可得）**
   - NFP / CPI / PPI / PCE / FOMC statement 发布时间
   - 公开性：美国政府 / 美联储官网日历公开
   - 更新频率：事件驱动、低频
   - 这里的正确定位是：**macro gate / veto**，不是逐根主信号

3. **可选补充：交易笔数 / volume / OI（公开可得）**
   - 用来验证 hot regime 里是否真的伴随 activity / liquidity 变化

### 4.3 最小实验口径
别先做复杂 PCA 复刻，先做 desk 够用的三层 schedule score：

1. **构建一个最小 `schedule_score_t`**
   - `+1`：minute in `{00, 15, 30, 45}`
   - `+1`：hour in `{0, 12, 13, 14, 15, 16}`
   - `+1`：weekday in `{Tue, Wed, Thu, Fri}`
   - `+1`：若当天有 NFP/CPI/PPI/PCE/FOMC，且 bar 落在事件前后 `±2` 根 `5m` bar

2. **拿两类现成 raw alpha 做 AB test**
   - A：`5m breakout / TSMOM / post-shock continuation`
   - B：`5m short-term reversal / shock fade`

3. **比较三种版本**
   - Baseline：不加任何 schedule gate
   - Gated：
     - continuation 只在 `schedule_score >= 2` 放行
     - reversal 只在 `schedule_score <= 1` 放行
   - Inverse：反着做，验证这个 gate 不是纯 data-mining

4. **输出核心指标**
   - post-cost Sharpe / PnL / turnover
   - `return per trade`
   - `slippage sensitivity`
   - `trade count`
   - `hot vs cold` 分层下的 hit-rate / follow-through / MAE / MFE

## 5. 先记住的交易结论
如果这条线要进 desk，正确写法不是“crypto 没开收盘，所以时钟没用”。

正确写法应该是：
**crypto 虽然 24/7，但 activity 并不均匀；整点、15 分钟、亚洲启动、欧美重叠、以及美国宏观发布时间，都是应该显式写进 short-cycle gate 的可交易时钟。**

对 continuation 类：这些窗口更像 admission。

对 reversal 类：这些窗口更像 veto。

## 6. 下一步怎么测
1. **先别复刻论文的 PCA**：第一轮只做简单 `schedule_score`，确认有没有最基础的分层价值。
2. **用两类 alpha 同时测**：至少拿一个 continuation、一个 reversal；如果只测一边，很难证明它是 shared gate。
3. **把 macro gate 单独拆出来**：先测“无条件时钟”，再测“加入事件日条件”；别把两者混在一起。
4. **把成本做成时段相关**：hot regime 不仅更容易出方向，也更容易更贵；如果成本还是静态，结论会偏乐观。
5. **优先从 BTC / ETH 开始**：论文里最稳定的结构也主要在 BTC / ETH；别一上来扩到冷门 alt。

## 7. 来源
1. **Wątorek, M., Skupień, M., Kwapień, J., & Drożdż, S. (2023). _Decomposing cryptocurrency high frequency price dynamics into recurring and noisy components_. arXiv.**
   - Authors: Marcin Wątorek, Maria Skupień, Jarosław Kwapień, Stanisław Drożdż
   - Year: 2023
   - Title: *Decomposing cryptocurrency high frequency price dynamics into recurring and noisy components*
   - Venue: arXiv
   - DOI: https://doi.org/10.48550/arXiv.2306.17095
   - Readable URL: https://arxiv.org/abs/2306.17095
   - Repo URL: N/A

2. **Binance USDⓈ-M Futures API — Kline/Candlestick Data.**
   - Authors: Binance
   - Year: 2026（访问时间）
   - Title: *USDⓈ-M Futures Market Data REST API / Kline Candlestick Data*
   - Venue: Binance Developer Docs
   - DOI: N/A
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - Repo URL: N/A

3. **U.S. Bureau of Labor Statistics / Federal Reserve event calendars（用于 macro timestamp gate）**
   - Authors: U.S. Bureau of Labor Statistics; Federal Reserve
   - Year: 2026（访问时间）
   - Title: *BLS Release Calendar* / *FOMC Meeting Calendars and Information*
   - Venue: Official public calendars
   - DOI: N/A
   - Readable URL: https://www.bls.gov/schedule/news_release/ ; https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
   - Repo URL: N/A
