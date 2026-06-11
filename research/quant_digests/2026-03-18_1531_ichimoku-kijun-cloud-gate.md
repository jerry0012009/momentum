# 别把 Ichimoku 整套搬进 15m：真正值得先偷的是 Kijun / cloud-side gate，给 breakout-short / Fib / EMA 做 shared continuation 过滤层
- 时间：2026-03-18 15:31 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/ichimoku/kijun/cloud/continuation/filter/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
这次看的是 `Steinwealth/EasyIchimoku`（创建于 2025-11-02，最近更新于 2026-03-08）。它不是“讲 Ichimoku 原理”的教程，而是一份已经能直接跑 TradingView 的完整 Pine 策略：把 `TK cross + 云层位置 + Chikou + ADX + RSI + 时间过滤 + ATR/BE/trailing` 全部写进了 entry/exit。对我们 desk 真正值得偷的，不是把整套优化参数搬过来，而是它把 continuation 写得很清楚：**只有当 price 站在正确的云层一侧、Tenkan/Kijun 关系已经翻到顺势方向、再叠一层 trend-strength 过滤时，才允许趋势单继续往前走。** 翻成人话：别再把“方向对了”理解成只要 EMA 翻上去就能做；更像先问一句——**这根 15m bar 到底还站不站在一条更慢、更结构化的防守线外面。**

## 2. 核心结论
- **一句话核心结论**：如果当前三条收口线都在纠结“这次突破/回踩到底是不是还算顺势延续”，那比继续往 EMA、PSAR、Fib 上堆局部小修小补更值得先测的，是 **Kijun + cloud-side** 这类结构 continuation gate。
- **一句话证明方式**：这个 repo 的入场条件在代码里写得非常直白：`tk_cross_up/down`、`close > cloud_top / < cloud_bottom`、`chikou >/< close[displacement]`、`adx >= threshold`、`RSI 不在极端区`、再加时间 veto；不是概念图，而是已经冻结成布尔条件。
- 对我们最有价值的不是 Chikou 或云参数本身，而是它表达的交易语义：**顺势单不只要求“快线翻身”，还要求价格离开拥挤区，站到一侧去。**
- 这正好补当前三条线的共同缺口：`breakout-short follow-up` 缺的是“跌破后有没有真正离开旧平衡区”；`Fib retest_hold` 缺的是“回踩后到底是在趋势防守线上方，还是已经回到云里搅”；`EMA / PSAR raw alpha` 缺的是“别让均线自己给自己投票”。
- 如果要回答“为什么这题比继续帮三条线收口更值得”，答案是：**因为它不是换一个新 alpha，而是在三条收口线都能共用的位置上，补一层更结构化的 continuation / avoid-chop gate。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：short 侧最怕的是刚跌破就被反抽收回。最直接的镜像写法是：只有当 `close < cloud_bottom` 且 `tenkan < kijun` 还成立时，breakout-short 才继续有效；若价格重新收回云内，先当 continuation 失真，而不是默认再等等。
- 对 `Fibonacci confirmation / retest_hold`：Fib 负责给“回到哪里”，Kijun / cloud-side 负责给“回到这里以后还有没有结构性防守”。也就是：**Fib 给位置，Kijun/cloud 给状态。** 如果回踩到 0.382/0.5/0.618 后仍在 `cloud_top` 上方，或回踩 Kijun 后快速收回，更像真 hold；反之更像只是回到拥挤区。
- 对 `EMA / PSAR raw alpha focus`：EMA / PSAR 继续做方向/触发层，但 Kijun / cloud-side 可以当外部结构闸门，避免裸 EMA 只在自己定义的趋势里自洽。尤其适合回答“PSAR 应该是主触发，还是只当锚”的问题：如果 PSAR 翻多但价格仍在云内，优先当结构未过关。
- 也和 backlog 里“EMA 结构是清楚方向层、pullback recovery confirmation 值得重点回看”这一进展相匹配：Ichimoku 这里最值得偷的，正是把“方向”与“回踩后是否还处于趋势外侧”揉成一个更有解释力的状态过滤。

## 4. 可复刻的最小实验
- **研究假设**：把 `Kijun + cloud-side gate` 接到现有 `breakout_short`、`fib_retest_hold`、`ema_slope_or_psar_trigger` 上，能比裸信号更稳定地压掉 `4~8 bars` 内的假延续与云内磨损。
- **公开数据源**：Binance perpetual `15m` OHLCV（BTC / ETH / SOL），公开可得；第一轮不需要额外外部低频数据。
- **最小定义**：
  1. 先不用整套 Ichimoku，也不搬 repo 的 tuned preset；第一轮只保留 `Tenkan / Kijun / cloud_top / cloud_bottom` 四个对象；
  2. 参数先冻结两档，不做网格：`classic 9/26/52` 作为朴素基线，`repo-15m 11/10/35` 作为敏感性对照；
  3. long gate：`close > cloud_top` 且 `tenkan > kijun`；short 镜像；
  4. retest_hold 版本可放宽成：最近 `3` 根里至少 `2` 根收在 Kijun 正确一侧，且最新收盘不回云内；
  5. 可选只加一层极轻的 `ADX14 > 12/15`，不要把 RSI、时间过滤、BE/trailing 一起端上来，避免第一轮就变成整套大杂烩。
- **最小回测切口**：最近 `180d`，`15m`，`BTC/ETH/SOL`，统一 `next-bar open`、`no-overlap`、成本先看 `6 / 10 / 15 bps per side`；对照 `base`、`base + kijun_only`、`base + cloud_side`、`base + kijun + cloud_side`、`base + kijun + cloud_side + adx_floor`。
- **最先看的 4 个指标**：`post-cost expectancy`、`trade_count retention`、`4~8 bar failure rate`、`winner truncation rate`。
- **下一步怎么测**：第一轮不要碰参数优化，先只回答一个问题——**Kijun / cloud-side 到底是在减少云内乱追，还是只是在漂亮地砍样本？** 如果它能在 trade retention 还过得去的前提下，稳定压低 failure rate，就值得升成三条收口线共享的结构 gate 候选。

## 5. 风险与保留意见
- 这个 repo 明显是强工程风格、强参数优化风格，不是严格学术 OOS；README 里的收益、胜率、PF 都更像作者自己的 deployment log，而不是可直接继承的 desk 证据。
- 参数很激进，例如 5m ETH 预设写到 `T17 / K12 / SenkouB9 / Disp8`，15m preset 也不是教科书默认值；这恰好说明我们更该偷“条件结构”，而不是偷“数值答案”。
- 时间 veto（周末、晚间、8-9AM PT）在该 repo 里占比很高，带有强 venue / execution 语境；对 24/7 crypto desk，第一轮应把它们全部移除，避免把 session 偏好误当 alpha。
- Ichimoku 与 EMA、VWAP、Donchian 之间有明显信息重叠；后续必须做 ablation，确认它提供的是额外结构信息，而不是换个更复杂的名字重复确认。

## 6. 来源
- Steinwealth. (2026). *EasyIchimoku: Ichimoku Cloud trend-following strategy for TradingView (Pine v5).*  
  - Venue / DOI：无（GitHub repo）  
  - Repo URL: <https://github.com/Steinwealth/EasyIchimoku>  
  - Readable URL: <https://github.com/Steinwealth/EasyIchimoku/blob/main/README.md>  
  - Raw README URL: <https://raw.githubusercontent.com/Steinwealth/EasyIchimoku/main/README.md>  
  - Key code URL: <https://raw.githubusercontent.com/Steinwealth/EasyIchimoku/main/easy_ichimoku_v14.pine>  
  - Repo metadata snapshot: created `2025-11-02`, pushed `2026-03-08`, `0` stars at fetch time.
- 代码侧关键条件（来自 `easy_ichimoku_v14.pine`）：`tk_cross_up/down`、`close > cloud_top / < cloud_bottom`、`chikou >/< close[displacement]`、`adx >= adx_threshold`、`RSI extremity veto`、`entry_window_ok`、`time_filters_ok`。