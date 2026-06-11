# 别把这份 Bybit technical bot 只读成“指标投票机器人”：对 short-cycle desk，更该先拆的是「daily-trend veto × 15m technical-vote continuation」这条完整 raw alpha 壳——而 Binance 迁移版 edge 几乎全靠 daily filter

- 时间：2026-04-14 01:40 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `backtest_full.py` + `bot.py`）+ Binance USDⓈ-M `15m/1d` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**`15m` 上由 `MACD cross + RSI 极值 + Bollinger 极值 + volume spike + EMA/4h 同向` 组成的 technical-vote continuation；`1d EMA20/50` 只负责 veto / regime，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/continuation/technical-vote/macd/rsi/bollinger/ema/daily-filter/score/sl-tp/trailing-stop/bybit/binance-perpetual/15m/1d/repo/public-data/cost/risk
- 证据类型：源码规则 + 180d public-data portability probe

## 1. 这次看了什么
主来源是 GitHub 仓库：
- **Author / Owner：** MarkusSela
- **Year：** 2026
- **Title：** *bybit-technical-bot*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/MarkusSela/bybit-technical-bot>
- **Repo URL：** <https://github.com/MarkusSela/bybit-technical-bot>

repo 很像“纯技术指标打分机器人”，但真正值得 desk 拆开的不是“指标很多”，而是它已经把一条**可直接下单的完整壳**写清楚了：`15m` 进场、score 分层、固定 `SL/TP`、daily veto、fee 假设、circuit breaker、live trailing。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的不是 Fear & Greed，也不是 trailing，而是 **`daily-trend veto` 保护下的 `15m technical-vote continuation` 完整壳**；迁到 Binance 后，这条壳子有 first-pass 正形状，但**edge 几乎全靠 daily filter 保住**。
- **一句话证明方式：** 我把 repo 的静态 backtest 逻辑迁到 Binance USDⓈ-M 上，对 `DOGE/SUI/XRP/WLD/ETH` 这 5 个与 repo top-6 的交集资产跑了最近 `180d`、`15m` + `1d` 公共数据；结果 `daily filter ON + repo_prev_close` 为 **2140 笔 / 50.0% 胜率 / +4.88 bps 每笔**，而 **去掉 daily filter 直接翻成 2950 笔 / -6.28 bps 每笔**。
- `next_open` 保守入口下也没塌：**2143 笔 / 49.93% 胜率 / +4.60 bps 每笔**，说明正形状不完全靠 entry price 偏乐观。
- 但更高 score 在 Binance 交集子集上**并没有更强**：`score 3-4` 是主贡献（**+6.11 bps/笔**），`score 5` 反而 **-15.62 bps/笔**，`score 6-7` 也只有 **-5.05 bps/笔**。
- repo README 里的 `+259.9%` 不宜直接当“可交易账户收益”理解：`backtest_full.py` 实际是**逐笔累加价格净变动百分比**，没有把 `risk_pct × leverage` 真正映射到账户权益曲线；而且 README 强调的 **v1.3 progressive trailing** 并没有在 `backtest_full.py` 里一起回放。

## 3. 为什么和当前项目有关
这轮有价值，因为它不是只给一个“也许有效的 filter”，而是给了一个**完整可拆的 production skeleton**：
- alpha 本体：`15m` 趋势同向 technical vote continuation；
- regime / veto：`1d EMA20/50` 日线方向过滤；
- risk：score 分层 `SL/TP`；
- execution/risk overlay：trailing、circuit breaker、最小名义金额限制。

对当前 `momentum` 主线，这比单纯再看一篇“指标综述”更有用，因为它能直接服务两个动作：
1. 把 `base alpha` 和 `daily veto` 明确拆开；
2. 快速做“壳子可迁移吗”的 first verdict，而不是只盯 README 自述收益。

## 3.5 策略拆解（必填）
- 方向属性：**single-asset / trend-following continuation**
- 基础 alpha：**`15m` 局部趋势同向时，技术极值 + MACD cross + volume spike 触发的 continuation / resumption**
- regime：**日线 `price vs EMA20/EMA50` 决定 long-only / short-only / neutral**
- filter / veto：**daily trend veto；弱分数不做；本轮迁移结果还提示：高分数未必更优，score bucket 本身也该重验**
- risk / sizing / execution overlay：**score 分层 `SL/TP/risk_pct`、progressive trailing、min notional、daily loss circuit breaker**

## 4. 可复刻的最小实验 + 下一步怎么测
### 本轮最小实验
- 市场：Binance USDⓈ-M perpetual
- 资产：`DOGEUSDT / SUIUSDT / XRPUSDT / WLDUSDT / ETHUSDT`
- 样本：最近 `180d`
- 数据：公开 `15m` 与 `1d` klines
- 口径：单资产、同一时刻每币最多一笔、双边 taker 成本按 repo `0.11%` round trip
- 产物：
  - 脚本：`reports/artifacts/quant_digests/2026-04-14_bybit_technical_bot_binance_probe.py`
  - 汇总：`reports/artifacts/quant_digests/bybit_technical_bot_binance_probe_summary_2026-04-14.csv`
  - 明细：`reports/artifacts/quant_digests/bybit_technical_bot_binance_probe_detail_2026-04-14.csv`

### 下一步怎么测
1. **先补正确账户级回测**：把 `risk_pct × leverage × concurrent positions × circuit breaker` 真正映射到 equity curve，不要再用“逐笔价格净变动求和”冒充账户收益。
2. **把 daily filter 单独做 admission test**：当前它把交集子集从 **-6.28 bps/笔** 拉到 **+4.88 bps/笔**，说明它不是可有可无的装饰层，而是这条壳目前最关键的 gate。
3. **把 score bucket 重排**：Binance 交集里明显不是“分越高越好”，应先测试 `score 3-4 only`、`exclude score>=5`、以及 `WLD/XRP/DOGE only` 的口袋组合，再决定是否保留原始 score ladder。
4. **最后才补 trailing 真回放**：repo live bot 的 trailing 可能改变收益分布，但它不该先于 base shell admission；先确认静态壳在账户级口径下站不站得住，再看 trailing 是增益还是幻觉。

## 5. first verdict
这份 repo 值得留在素材池，**因为它确实给了完整策略壳**，不是只有解释层；但当前更诚实的读法不是“又一个 +259% 机器人”，而是：

> **`15m technical-vote continuation` 在 `daily-trend veto` 保护下有 first-pass 生存性；但 headline backtest 记账口径偏松，而且高分数并没有跨 venue 稳定迁移。**

所以它的优先落点不是直接实盘，而是进入：**`daily-gated continuation shell` 的 clean replication / admission check 队列。**
