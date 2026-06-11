# 别把“tea time”只读成流动性高峰：这篇 2025 RQFA 论文对 desk 更该先测的是「固定 UTC 时钟 alpha」，但当前可交易 pocket 已经漂移
- 时间：2026-03-27 18:22 UTC
- 类型：2025 Review of Quantitative Finance and Accounting 开放获取全文 HTML + Binance USDⓈ-M Perpetual 公共 `1h` transfer check（执行映射到 `15m`）
- 主题类型：raw alpha
- 基础 alpha：**固定 UTC 小时的可预测收益漂移（clock-based seasonality）；对 short-cycle desk 来说，本体不是“茶点时段成交更高”，而是“某些 UTC 时段天然更偏 continuation / fade，可直接写成定时开平仓 schedule”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/time-of-day/utc-clock/seasonality/intraday/schedule/continuation/fade/cross-exchange/binance/perpetual/1h/15m/5m/paper/external-data/cost
- 证据类型：论文全文 + 本地公共数据最小迁移快检

> 先回答 base alpha：**这是 raw alpha，不是 filter。** 赚钱本体就是 **固定 UTC 小时的方向性 drift / fade**；成交、波动、流动性高峰只是解释层，不是 alpha 本体。

## 1. 这次看了什么
这次主看：

1. **Alexander Brauneis, Roland Mestel, Erik Theissen (2025)**, *The crypto world trades at tea time: intraday evidence from centralized exchanges across the globe*, **Review of Quantitative Finance and Accounting**.
   - DOI: `10.1007/s11156-024-01304-1`
   - DOI URL: `https://doi.org/10.1007/s11156-024-01304-1`
   - Readable URL: `https://link.springer.com/article/10.1007/s11156-024-01304-1`
   - 证据形态：Springer 开放获取 HTML 全文可读
2. 本地 transfer check：
   - 数据源：Binance USDⓈ-M Perpetual 公共 K 线 API（公开可得）
   - 标的：`BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK`
   - 频率：`1h`（用于复刻 paper 的 clock 粒度），执行映射到 `15m`
   - 样本：`2025-01-01` ~ `2026-03-27 18:00 UTC`
   - 产物目录：`reports/artifacts/quant_digests/tea_time_clock_alpha_20260327/`

这篇 paper 的 headline 是：**在没有开闭市和隔夜结算约束的 24/7 crypto 市场里，时间-of-day 结构仍然很强，而且全球很多交易所会在同一个 UTC 时段同时变活跃——也就是所谓的 “tea time”。**

但对我们 desk 来说，更值钱的读法不是“16:00~17:00 UTC 很热闹”本身，而是：
- **时钟型 raw alpha 是真实存在的一类素材池；**
- 它可以脱离具体 K 线形态，直接写成 `trade on / trade off`；
- 它很适合作为 `1m / 3m / 5m / 15m` 的底层 schedule skeleton，再叠加更快的确认或 veto。

## 2. 一句话核心结论
**这篇东西最该带进 desk 的，不是“茶点时段成交量最高”，而是“24/7 crypto 也有固定 UTC 时钟偏置；可以把某些小时当成独立 raw alpha 家族来做，而不是只把它当背景知识”。**

## 3. 它怎么证明这个结论
**作者用 `1940` 个 trading pairs、`38` 家交易所、`30,744` 个小时的数据，对每个小时做 dummy regression，比较 returns / volatility / illiquidity / volume / transactions 的时间分布，并验证这些 pattern 在不同大洲、不同币对上仍高度相似。**

## 4. 3 个关键数据点
1. **样本很大，而且不是单交易所单币种。**
   - 样本区间：`2018-07-01` 到 `2022-01-01`
   - 频率：`1h`
   - 最终样本：`1940` 个交易对、`38` 家交易所、覆盖 `386` 个 coins / tokens
   - 作者还说明：在若干历史截面上，样本覆盖了前 200 大币里约 `83%~97%` 的总市值、`86%~99%` 的总交易量。
2. **论文里的 headline pattern 很清楚。**
   - returns 在 **UTC 早晨最弱**，在 **early afternoon 和 evening 最强**；
   - trading activity / volatility / illiquidity 在 **`16:00~17:00 UTC`** 一起见顶；
   - 这些 pattern 在 **Americas / Europe / Asia** 上都很像，说明它不只是本地开盘时差故事。
3. **我在当前 Binance perp 的 literal transfer 上，发现“时钟 alpha 还在，但 tea-time headline 已经不该照抄”。**
   - 如果按论文直觉粗写成：`long 13~16 & 20~22 UTC, short 03~06 UTC`，在 `2025-01-01` ~ `2026-03-27` 的 8 币等权 `1h` 组合里：
     - gross cumret **`+25.3%`**
     - gross Sharpe **`0.61`**
     - 但按单边 `4 bps` 成本后，net cumret **`-57.5%`**
   - 也就是说：**paper headline 作为“方向性 schedule”直接照搬，不够。**
   - 但若把 paper 启发转成“重新拟合固定 UTC pocket”，并限制为**简单、低切换 schedule**，2026 Q1 test 里出现了可交易 pocket：
     - `long 20~21 UTC / short 22~23 UTC`（2025 train 选出，2026 test 验证）
     - test gross cumret **`+22.8%`**
     - test net cumret **`+7.15%`**
     - test gross Sharpe **`4.14`**, net Sharpe **`1.46`**
     - 平均日内 position changes 约 **`3.95`** 次

## 5. 为什么这和当前 short-cycle desk 直接相关
### 5.1 它服务的是哪类 raw alpha
- 分类：**time-of-day / schedule-based directional raw alpha**
- 不是：
  - 纯 regime
  - 纯 filter
  - 纯解释性市场结构文章

### 5.2 它补的是素材池哪块缺口
我们最近已经积了很多：
- breakout / continuation
- cross-sectional momentum / reversal
- pairs / stat-arb / lead-lag
- funding / basis / carry

但还相对少系统写一类东西：
> **不靠形态、不靠复杂特征，只靠“时钟本身”定义的 schedule raw alpha。**

这类 alpha 对 desk 有三个现实好处：
1. **最容易先做 first verdict** —— 规则清楚，几乎零特征工程；
2. **最容易和别的 alpha 叠加** —— 可以做 base book，也可以做 session sleeve；
3. **最容易做执行治理** —— 因为开平仓时间是预先知道的，成本和容量更容易估。

## 6. desk 化后的最小策略草图
## 6.1 基础版本：固定 UTC schedule
先做最小可复现版本：

- 频率：`15m`
- 宇宙：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK` perp 等权
- clock signal：固定 UTC 小时触发
- 初始 schedule 不要抄 paper headline，先用更保守的 desk pocket：
  - **long：`20:00~21:59 UTC`**
  - **short：`22:00~23:59 UTC`**
- 执行映射到 `15m`：
  - 在 `20:00` 的第一根 `15m` bar 开多
  - 在 `22:00` 的第一根 `15m` bar 平多并开空
  - 在 `00:00` 的第一根 `15m` bar 平空

这其实就是把 `1h` clock alpha 拆成一个 **`15m` 可执行的 time-sleeve strategy**。

## 6.2 entry / exit
最小版不需要复杂触发：
- **entry**：到点就进
- **exit**：到下一个时段边界就出
- **持有期**：每个 sleeve `2h`

然后再往上加一层最轻的确认：
- long sleeve 内要求 `15m` close 在本小时开盘价之上才保留；
- short sleeve 内要求 `15m` close 在本小时开盘价之下才保留；
- 若条件不满足，就 flat，而不是硬做反向。

## 6.3 sizing
- 先做等权；
- 第二版再上 `inverse-vol`；
- 若把币种扩到 `12~20` 个，建议做 sector / beta cap，避免 meme 组把 clock alpha 变成单风格暴露。

## 6.4 risk / veto
必须加：
1. **重大事件 veto**：CPI / FOMC / ETF / 大所事故时，schedule 不能裸跑。
2. **高 funding / 极端 basis veto**：避免把 clock drift 和 crowding squeeze 混在一起。
3. **日内 stop**：比如单 sleeve `-1.0 ~ -1.5 ATR(15m)`。
4. **连续亏损 throttle**：若最近 `N=5` 个同类 sleeve 连亏，则 size-down 或停一天。

## 6.5 cost
clock alpha 的核心不是预测多准，而是：
> **切换次数够不够少，单位时段 edge 能不能盖过固定成本。**

本轮快检说明：
- 高频“多窗口拼接”的时钟策略很容易 gross 有、net 死；
- 真正值得往下推的，是 **低切换、窗口少、边界清楚** 的 schedule。

正式 friction ladder 至少要跑：
- maker-ish：`2 / 3 / 4 bps` one-way
- mixed：`4 / 5 / 6 bps`
- taker-heavy：`6 / 8 / 10 bps`

## 7. 本地 transfer check：要怎么读才诚实
我这次不是想证明 paper 的 `16~17 UTC` 能直接赚钱，而是想回答：
> **“固定 UTC 小时本身”是不是还值得作为一条 raw alpha 家族继续留在 intake 池里？**

当前答案是：**值得，但不能照抄 headline，需要重新 pocket 化。**

### 7.1 直接照抄 headline，不够
按 paper 的直觉粗翻成 `tea-time strength + early-morning weakness`：
- gross 还有东西；
- net 很差；
- 说明 **clock alpha 不是没了，而是当前 Binance perp 的可交易 pocket 已经从论文样本期漂移。**

### 7.2 重新拟合后，有 pocket，但别过度乐观
我进一步把 schedule 限定为：
- long window 长度 `1~3h`
- short window 长度 `0~2h`
- 平均日内切换次数 `<= 6`

然后：
- 用 **2025 年** 做 train，
- 用 **2026-01-01 ~ 2026-03-27** 做 test。

在这个受限 family 里，**`long 20~21 / short 22~23`** 是更诚实的 desk pocket：
- 它不是 paper headline 原句；
- 但它属于 paper 证明过的那条母线：**crypto 有全球共享的 UTC 时钟结构**；
- 而且它在 out-of-sample test 上，至少先活成了一个 **cost 后仍为正** 的低切换原型。

## 8. 下一步怎么测
按优先级建议这样推进：

1. **把当前 `1h` 发现映射到 `15m` 真执行版。**
   - 同样的 UTC 窗口；
   - 但 entry / exit 放在小时首根和末根 `15m` bar；
   - 看真实 `15m` markout、滑点和最大回撤。
2. **先测单 pocket，不要一上来拼全天 schedule。**
   - 第一优先：`20~21 long / 22~23 short`
   - 第二优先：`21 only long / 05 only short`
   - 看哪种在 `15m` 更稳、成本后更诚实。
3. **把 clock alpha 和 microstructure confirm 拆开测。**
   - clock 决定“允许交易的时段”；
   - `15m` return / VWAP / OI / funding 小特征决定“要不要真的下单”。
4. **做 cross-sectional 版本。**
   - 不是所有币同时做；
   - 同一时段里，优先做历史上对该时段漂移更敏感的币；
   - 可按 `hour-of-day information ratio` 做币种筛选。
5. **做 split-by-regime。**
   - bull / bear / chop；
   - 高 funding / 低 funding；
   - 高 realized vol / 低 realized vol；
   - 看 clock alpha 是独立存在，还是只在某类 regime 下有 pocket。
6. **验证稳定性，而不是只看总收益。**
   - 按月拆 PnL；
   - 看 pocket 是否只集中在 1~2 个月；
   - 若太集中，就只能当 tactical sleeve，不能当 always-on alpha。

> **最该先做的正式版本：** `Binance perp 15m`，只跑 `20~21 UTC long / 22~23 UTC short` 这一个 pocket，先做 `8~12` 个高流动性币等权，加入 `15m` 小时内方向确认与基础成本梯度，看它能不能从“1h clock drift”升级成“15m 可执行 sleeve”。

## 9. 文件与产物
- 研究笔记：`research/quant_digests/2026-03-27_1822_utc-clock-seasonality-alpha.md`
- 产物目录：`reports/artifacts/quant_digests/tea_time_clock_alpha_20260327/`
- 小时均值：`reports/artifacts/quant_digests/tea_time_clock_alpha_20260327/cross_symbol_hourly_means_1h.csv`
- 粗 schedule 回测：`reports/artifacts/quant_digests/tea_time_clock_alpha_20260327/schedule_strategy_portfolio_curve_1h.csv`
- train/test 选时结果：`reports/artifacts/quant_digests/tea_time_clock_alpha_20260327/train_test_clock_selection.json`
- 受限 schedule 搜索：`reports/artifacts/quant_digests/tea_time_clock_alpha_20260327/clock_schedule_search.json`

## Sources
1. **Brauneis, A., Mestel, R., & Theissen, E. (2025). _The crypto world trades at tea time: intraday evidence from centralized exchanges across the globe_. Review of Quantitative Finance and Accounting.**
   - DOI: `10.1007/s11156-024-01304-1`
   - DOI URL: `https://doi.org/10.1007/s11156-024-01304-1`
   - Readable URL: `https://link.springer.com/article/10.1007/s11156-024-01304-1`
2. **Binance USDⓈ-M Perpetual Public Klines API**（本地 transfer check 数据源）
   - API docs: `https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data`
   - 示例：`https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=1500`
