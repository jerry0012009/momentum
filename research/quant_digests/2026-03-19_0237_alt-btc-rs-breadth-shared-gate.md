# 别把“alt 强于 BTC”只当山寨追涨器：更值得先偷的是 `alt-vs-BTC RS breadth`，给 breakout-short / Fib / EMA 做 shared regime gate
- 时间：2026-03-19 02:37 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/relative-strength/breadth/regime/filter/repo/crypto/15m
- 证据类型：源码证据 + 工程迁移假设
- 证据强度提示：**中等偏弱**（规则清楚、公开可复现，但不是论文，也没有同口径 15m OOS 绩效）

## 1. 这次看了什么
这次看的是 **oranoap (2026), `rsb-trading-bot`**。repo headline 是“找出 **24h 相对 BTC 更强** 的 alt，再做 **1h Bollinger breakout**”，但对我们 desk 真正值钱的不是追山寨，而是它把 **市场广度筛选** 和 **单币触发** 分成了两层。

## 2. 核心结论
- **一句话核心结论：** 对当前三条收口线，更值得先测的不是“某个币是否强于 BTC”，而是 **有多少币在强于 / 弱于 BTC**，把它当 shared breadth gate。
- **一句话说明它怎么证明：** repo 源码把流程拆得很直白：`top 50 alt by volume` → `alt_24h_change - btc_24h_change > 5%` → `1h BB(20, 2)` 突破；说明作者自己也把 RS 放在 **trigger 之前**，而不是把 RS 当单独入场键。
- 可复用的硬参数有 3 个：**Top 50** 成交量宇宙、**RS > 5%** 的 BTC 相对强度门槛、以及 **1h Bollinger(20, 2)** 作为后续触发层。
- backtester 还显式放了 **0.1% slippage**、**0.6% round-trip fee**、**最多 3 个持仓**，提醒我们这类广度信号更适合作为 allow/deny 或 sizing，不要假装它是裸 alpha。

## 3. 为什么和当前项目有关
这轮值得优先写，因为最近几篇已经给三条线塞了不少“单币过滤器”，但还缺一个更上层的 **market breadth / crowd alignment** 共用层。
- 对 **`V3 final-verdict / breakout-short follow-up`**：如果多数 alt 仍显著跑赢 BTC，short follow-up 更像逆风单，优先 veto 或 half-size。
- 对 **`Fibonacci confirmation / retest_hold`**：若 `breadth_pos` 站高，long retest_hold 更值得放行；若 breadth 走弱，Fib 守住也别太早认。
- 对 **`EMA / PSAR raw alpha focus`**：可把 breadth 从“入场条件”降级为 **shared regime gate / sizing overlay**，比继续堆单币指标更像当前缺口。

## 4. 可复刻的最小实验
### 研究假设
`alt-vs-BTC breadth` 能提升 15m continuation / retest 的成本后质量，尤其适合当 shared allow/deny gate。

### 数据源（公开可得）
- 来源：交易所公开 ticker + OHLCV（Binance / Bybit / Coinbase，经 CCXT 可抓）
- 公开性：公开市场数据，无需私有成交回报
- 更新频率：ticker 近实时；15m / 1h K 线固定更新
- 最小复现实验口径：取 **Top 20~50** perp，滚动算 `rs_i = ret_24h(asset_i) - ret_24h(BTC)`

### 一个便宜定义
- `breadth_pos = share(rs_i > 0)`
- `breadth_neg = share(rs_i < 0)`
- 可加强版：`share(rs_i > 2%)` / `share(rs_i < -2%)`

### 15m 接法
1. `breakout-short`：仅当 `breadth_neg >= 0.55` 放行；`breadth_pos >= 0.55` 则 veto。  
2. `Fib retest_hold` / `EMA continuation long`：仅当 `breadth_pos >= 0.55` 放行；中性区 `0.45~0.55` half-size。  
3. 对照：baseline vs breadth gate vs breadth sizing。

### 第一轮最该看
- `post_cost_expectancy`
- `4~8 bar failure rate`
- `trade_retention`（别靠砍太多单伪改善）

## 5. 风险与保留意见
- repo 是 **1h 长侧 alt breakout**，不是 15m perp short；我们迁移的是 **层级结构**，不是原策略本身。
- `24h RS` 可能太慢，15m 上也许更该试 `8h / 4h RS breadth`。
- 宇宙会漂移：Top 50 alt 的成分每天都变，需先冻结一个可交易 perp 池，避免研究口径飘来飘去。

## 6. 来源
1. **oranoap (2026)**, *Relative Strength Breakout (RSB) Trading Bot*.
   - Readable URL: https://github.com/oranoap/rsb-trading-bot
   - Repo URL: https://github.com/oranoap/rsb-trading-bot
2. **关键源码文件**
   - `scanner.py`：`top 50 by volume` + `alt_24h_change - btc_24h_change > 5%`
   - `strategy.py`：`1h BB(20,2)` breakout
   - `backtester.py`：`0.1% slippage`、`0.6% round-trip fee`、`max 3 positions`
