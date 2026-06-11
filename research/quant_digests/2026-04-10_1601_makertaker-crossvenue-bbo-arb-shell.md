# maker/taker 跨所 BBO 价差 × fill-timeout 套利壳
- 时间：2026-04-10 16:01 UTC
- 类型：GitHub repo + 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：同一标的在不同 venue 的最优买一/卖一短暂失配，会给出 `long cheap venue + short rich venue` 的 market-neutral spread-capture 机会
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / relative-value / stat-arb / cross-venue / maker-taker / perp / bbo / execution / cost / 1m / 3m
- 证据类型：工程经验 + 公共数据快检

## 1. 这次看了什么
看的是 `your-quantguy/cross-exchange-arbitrage` 这个 2026 GitHub repo，主审计文件包括 `README.md`、`arbitrage.py`、`strategy/edgex_arb.py`、`strategy/order_manager.py`。这套壳不是泛泛说“跨所套利”，而是写成了很具体的 live 逻辑：当一边 venue 的 `best bid` 高过另一边 venue 的 `best ask` 到达阈值，就在 maker venue 先挂 `post-only`，成交后再去另一边 taker 对冲；同时带 `fill_timeout=5s`、`max_position` 和连续盘口监控。

## 2. 核心结论
- **一句话核心结论**：这类 alpha 不是“完全没有 edge”，但在 Binance/Bybit 这种顶级 venue 的 liquid majors 上，edge 小得更像费率/排队/延迟竞争，不像当前 desk 应优先走的 `5m/15m` 主线 raw alpha。
- **一句话证明方式**：先审 repo 里的 maker/taker 壳，再用 Binance USDⓈ-M + Bybit linear 公共 `bookTicker/BBO` 做 `180` 个 `1s` snapshot live probe，看 crossed-BBO 是否能稳定越过成本门槛。
- repo 里最值得复用的不是 `edgeX/Lighter` 这两个具体 venue，而是这套**maker-first + taker-hedge + fill-timeout + max-position** 的执行框架；它把 raw alpha、执行和风险边界拆得很清楚。
- 我用 `BTC/ETH/SOL/XRP/DOGE` 做了 `1s × 180` 次 live BBO portability probe。结果里 `BTC/ETH` 的 `best crossed edge` 中位数只有约 `0.92 / 0.81 bps`，`p90` 约 `1.52 / 1.62 bps`；全样本最大值里，`ETH` 约 `5.36 bps`、`DOGE` 约 `3.25 bps`、`SOL` 约 `2.88 bps`、`BTC` 约 `2.46 bps`、`XRP` 约 `1.53 bps`。
- 更关键的是：本次样本里 **没有任何一个 symbol 出现过 `>6 bps` 的 crossed-BBO**。这意味着若按更现实的双边 maker+taker round-trip 成本去看，顶级 venue 上这条路大概率不够肥；要么得去更小众/更碎片化 venue，要么得依赖高 VIP rebate、极低延迟和很强的 queue/fill 优势。

## 3. 为什么和当前项目有关
这条东西仍然值得进研究池，因为它属于很干净的 **relative-value / stat-arb raw alpha**：不是猜方向，而是抓同一标的跨 venue 的短暂定价不一致。但它给 desk 的高价值判断不是“立刻上”，而是一个很清楚的 **go / no-go**：如果连顶级 venue 的 BBO 交叉都很少越过 `6~10 bps`，那这条线就不该继续占用大量 `5m/15m` 研发预算。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral / stat-arb
- 基础 alpha：同一标的跨 venue 的 `best-bid vs best-ask` 短暂失配
- regime：venue fragmentation 高、局部盘口更新不同步、事件窗口或局部流动性抽空时更容易出现
- filter / veto：`crossed edge > full fee hurdle`、top-of-book size 足够、maker venue 未失联、hedge venue 可立即成交、资金费率/标记价偏移不过度
- risk / sizing / execution overlay：maker-first、`fill-timeout` 取消、`max_position` 上限、必要时加 `flatten-after-N-seconds` 或 `edge<=0` 平仓规则

## 4. 可复刻的最小实验
- 研究假设：在更碎片化的 venue 对，或在新闻/结算/资金费率边界窗口，`same-underlier crossed BBO` 越过 `8~10 bps` 的比例会显著高于平时，从而让 maker/taker 跨所套利变成可交易事件驱动 alpha。
- 一个可计算定义：
  - `edge_buy_A = bid_B / ask_A - 1`
  - `edge_buy_B = bid_A / ask_B - 1`
  - `edge_t = max(edge_buy_A, edge_buy_B) * 10000 (bps)`
  当 `edge_t > hurdle_bps` 才允许开仓，方向为 `long cheap venue / short rich venue`。
- 最小回测切口：先别做全历史，先抓 `Binance / Bybit / OKX` 的 `BTC/ETH/SOL` 公共 `1s` BBO，连续录 `3~7` 天；重点切出 `资金费率结算前后 ±10m`、`美盘数据/宏观事件`、`极端波动分钟` 三类窗口。
- 最该先看哪 1~2 个指标：
  1. `share(edge > hurdle)` —— 真正越过成本线的机会占比；
  2. maker fill 后 `5s/15s/30s` 的 `realized close-edge` —— 有没有被 adverse selection 反吃掉。

## 5. 风险与保留意见
- repo 给的是 live 交易壳，不是严格的历史统计论文；当前更像工程启发，不是“已被学术验证”的高置信 alpha。
- 我这次 portability probe 只有 `180s` live BBO，且只看 top-of-book，没有 depth、queue、latency、挂单成交率，所以这是 **first verdict**，不是最终否决。
- 但也正因为只看最乐观的 top-of-book，若这里已经很难越过成本，真实成交后通常只会更差。
- 因此当前更合理的定位是：**把它当 cross-venue arb 候选池里的 execution shell / viability gate**，而不是 desk 现在最优先推进的主策略。

## 6. 来源
- your-quantguy. (2026). *cross-exchange-arbitrage*.
  - Repo URL: `https://github.com/your-quantguy/cross-exchange-arbitrage`
  - Audited files: `README.md`, `arbitrage.py`, `strategy/edgex_arb.py`, `strategy/order_manager.py`
- Binance USDⓈ-M public BBO:
  - `https://fapi.binance.com/fapi/v1/ticker/bookTicker?symbol=BTCUSDT`
- Bybit linear public BBO:
  - `https://api.bybit.com/v5/market/tickers?category=linear&symbol=BTCUSDT`
- 本地快检产物：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_exchange_makertaker_probe_detail_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_exchange_makertaker_probe_summary_2026-04-10.csv`
