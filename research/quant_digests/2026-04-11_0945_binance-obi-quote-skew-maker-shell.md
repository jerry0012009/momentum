# Binance OBI quote skew × inventory-bounded maker shell（LIGHTER_Market_Making, 2026）
- 时间：2026-04-11 09:45 UTC
- 类型：GitHub / 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：`Binance Futures 深度 OBI（order-book imbalance）z-score 先给出未来数秒 mid-price 漂移方向，再把方向优势塞进 maker quote skew 里吃 spread + drift`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：maker / market-making / microstructure / order-book-imbalance / quote-skew / inventory / execution / Binance / Lighter / 1m / 3m
- 证据类型：工程经验 + repo source audit + 公开数据 portability probe

## 1. 这次看了什么
看的是 `djienne/LIGHTER_Market_Making` 这份 2026 GitHub repo。它表面上是给 Lighter perp 做双边做市，但真正值得 desk 拎出来的不是“零手续费 DEX 做市”，而是更底层的 **Binance 深度 OBI → maker skew**：先用 Binance `@depth@100ms` 维护本地 order book，算 `2.5%` 深度内的 `sum_bid_qty - sum_ask_qty`，再对滚动窗口做 z-score，把它当未来几秒方向偏置，最后只用来把 bid/ask 向一边轻推，而不是裸做 directional taker。

## 2. 核心结论
- 这份 repo 的 **base alpha 很清楚**：不是 inventory mean reversion，也不是 spread capture 本身，而是 `OBI extreme -> future short-horizon drift`。
- repo 给的是完整壳，不只是信号：`vol_obi` 负责半价差，`BinanceDiffDepthClient` 提供 alpha，`inventory skew` 控仓，`adaptive requote threshold / quota recovery / circuit breaker / stale-order poller` 负责执行与风控。
- 默认参数很 desk 化：`window_steps=6000`、`step_ns=100ms`（约 10 分钟滚动窗），`c1_ticks=20`，`min_half_spread=8bps`，`skew=3.0`，`alpha stale_seconds=5`。
- 我用 Binance USDⓈ-M 公共 `BTCUSDT` depth REST 做了一个 **180 秒、1 秒采样的缩尺 proxy probe**：`alpha_z` 与未来 `1s` 收益的相关约 `0.22`；按 top/bottom 20% bucket 看，最高 OBI 桶未来 `1s/3s/5s` 原始 mid return 约 `+0.04 / +0.08 / +0.12 bps`，最低桶约 `-0.07 / -0.21 / -0.35 bps`，`high-low 5s spread ≈ +0.47 bps`。这说明 OBI 更像 **maker skew admission**，而不是单独拿去做 5m 裸方向单。

## 3. 为什么和当前项目有关
这条线和当前 desk 直接相关，因为它补的不是又一个“15m 形态故事”，而是 **更快、更底层、可给多个 alpha 共用的 execution-aware raw alpha 组件**：
- 对 `1m/3m`：它本身就可以做 maker alpha；
- 对 `5m/15m`：它可以当 **entry veto / quote-side bias / child execution router**，决定顺着信号挂哪边、哪边缩量、哪边暂停；
- 对当前素材池：它把 `alpha / execution / inventory / safety` 四层拆得很清楚，适合后续单独迁移进我们自己的微观结构实验框架。

## 3.5 策略拆解（必填）
- 方向属性：微观结构顺势 + 做市价差捕获
- 基础 alpha：`depth imbalance z-score -> next-few-second signed drift`
- regime：高流动、价差稳定、书本更新连续时更可信
- filter / veto：alpha stale > 5s、book 不健康、quote quota 紧张、orderbook sanity fail 时停机
- risk / sizing / execution overlay：vol-based half spread、inventory skew、dynamic max position、POST_ONLY、adaptive requote threshold、circuit breaker

## 4. 可复刻的最小实验
**研究假设**：Binance 顶层到浅层深度的 OBI 极值，能在 `1s~10s` 内给出足够稳定的 drift，值得用来给 maker quote 做单边偏置。

**最小定义**：
1. 采 `BTC/ETH/SOL` 的 `depth@100ms` 或至少 `1s` depth snapshot；
2. 算 `imbalance_t = bid_qty(within 2.5%) - ask_qty(within 2.5%)`；
3. 用 `60s / 300s / 600s` 滚动窗算 `z_t`；
4. 当 `z_t > z*` 时，把 bid 抬高/ask 也抬高（偏多）；`z_t < -z*` 时反向；
5. 做一个最简 maker 仿真：`min_half_spread 1~4 ticks`、`inventory cap`、`5~30s timeout`。

**最该先看**：
- `fill-adjusted net bps`（扣 maker fee / rebate 后）
- `adverse selection`（成交后 `1s/3s/5s` markout）

如果这两项不过关，就说明 OBI 只够当 veto / skew，不够独立成策略。

## 5. 风险与保留意见
- 我这次 public probe 是 **REST 1s 缩尺代理**，不是 repo 原生的 `@depth@100ms + 本地簿`，所以只能说明“方向性没死”，不能说明 production edge 大小。
- maker alpha 最怕 **queue position / fill model / venue latency**；这些如果不进仿真，纸面 edge 很容易被高估。
- 这条 alpha 天生更像 `1m/3m`，硬拉到 `5m/15m` 做主方向会稀释信息密度。
- repo 跑在 Lighter、alpha 来自 Binance，本质是 **cross-venue transfer**；若两边微观结构脱钩，edge 会衰减。

## 6. 来源
- djienne. (2026). *LIGHTER_Market_Making*. GitHub.
  - Repo URL: `https://github.com/djienne/LIGHTER_Market_Making`
  - 关键文件：`README.md`、`market_maker_v2.py`、`binance_obi.py`、`vol_obi.py`、`config.json`
- Binance USDⓈ-M Futures REST depth endpoint（本地 portability probe 数据源）
  - Docs: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book`
- 本地快检产物：
  - `reports/artifacts/literature/lighter_obi_probe_detail_2026-04-11.csv`
  - `reports/artifacts/literature/lighter_obi_probe_summary_2026-04-11.csv`
