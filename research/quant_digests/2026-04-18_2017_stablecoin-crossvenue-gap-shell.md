# 别把这份 stablecoin cross-exchange arbitrage repo 只读成“转账图论作业”：对 short-cycle desk，更该先保留的是「inventory-funded stablecoin cross-venue gap」这条 raw alpha 壳
- 时间：2026-04-18 20:17 UTC
- 类型：GitHub / live public-quote probe
- 主题类型：raw alpha
- 基础 alpha：同一稳定币对在不同交易所的买一卖一短暂失配；预布库存后，卖高买低，等价于做 cross-venue quote-gap convergence
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / stablecoin / cross-venue / inventory-funded / quote-gap / convergence / maker-first / 1m / 3m / 5m
- 证据类型：repo source audit + 公开实时报价快检

## 1. 这次看了什么
看的是 GitHub 仓 `kevinl03/Stablecoin-CrossExchange-Arbitrage`。repo 表面上在讲“多交易所稳定币转账图 + A* / Bellman-Ford 路径搜索”，但对我们 desk 更值钱的旁支不是慢吞吞的链上转账全路径，而是它先把问题写清楚了：**稳定币套利不是方向判断，而是同类现金替代物在不同 venue 上的短暂价格错位**。如果把“先转币”改成“先预布库存”，base alpha 会更贴近 short-cycle desk：`同一 stablecoin pair 在 A 所更贵、在 B 所更便宜 -> 先卖 rich venue、买 cheap venue，等 gap 回归或内部库存再平衡。`

## 2. 核心结论
- 这条线的 **base alpha 很清楚**：不是猜 BTC 涨跌，而是赌 **同一稳定币对的跨所报价会向更一致的 law-of-one-price 区间回归**。
- repo 给的策略壳其实挺完整：节点是 `(exchange, coin)`，边上显式放了 trading fee、withdraw fee、slippage、transfer time、chain risk，连“30 分钟 time budget”都写进了问题定义。也就是说，`entry / exit / risk / cost` 不是事后补丁，而是一开始就在壳里。
- 但若照 repo 原样理解成“看见 gap 就现转现搬”，对我们默认 `1m/3m/5m` desk 还是太慢。更适合先拆出来的，是 **inventory-funded same-pair cross-venue gap** 这条更短、更干净的 raw alpha 分支。
- 我做了一个 4 所公开 bookTicker 快检（Binance / MEXC / OKX / KuCoin，`USDCUSDT/FDUSDUSDT/FDUSDUSDC/TUSDUSDT`，8 次采样）：`USDC/FDUSD` 这几组几乎没有正向跨所 gap，但 `TUSDUSDT` 出现了 **16 次正 gap**，median 约 **3.50bps**，p90 / max 约 **4.00bps**，主要是 **MEXC 卖、KuCoin 买** 这组。说明 stablecoin cross-venue pocket 不是完全没有，但很挑标的。
- 这也直接给出 first verdict：**raw alpha 在，但更像 maker/VIP/inventory pocket**。如果两边都按普通 taker，`3~4bps` gross 很容易被手续费吃掉；只有在更低费率、maker rebate、或已有双边库存时，才像能进下一轮。

## 3. 为什么和当前项目有关
这条线补的是我们当前持续在补的 **relative-value / stat-arb raw alpha 素材池**，而且和今天已经写过的 options / OBI / funding 不同：
- 它不依赖方向判断；
- 不需要复杂论文私有数据；
- 公开 quote 就能先做最小实验；
- 可以天然落到 `1m` 甚至更快的事件驱动 execution。

更重要的是，repo 的高价值点不在“图搜索算法有多炫”，而在它把 **成本、时间、链风险、流动性** 全部提前写进了壳。对 short-cycle desk 来说，这比又抄一个只看 spread、不看执行的套利 demo 值钱。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：stablecoin same-pair cross-venue quote-gap convergence
- regime：稳定币本身偏离锚定、局部流动性不均、单 venue order book 变薄时更容易出现
- filter / veto：只做高流动性对；gap 必须大于双边 fee + 预估 slippage + inventory buffer；禁止在链拥堵 / 提现暂停 / 订单簿过薄时入场
- risk / sizing / execution overlay：预布库存优先；每腿独立 notional 上限；maker-first 或 VIP fee tier；超时未收敛则 inventory rebalance；按 venue / stablecoin 设置 hard cap

## 4. 可复刻的最小实验
- 研究假设：同一稳定币对在不同 CEX 的 top-of-book 偶尔会出现 `bid_A > ask_B` 的短暂失配；若已有双边库存，短时间内可兑现为 quote-gap 收敛收益。
- 可计算定义：每秒或每 `5s` 抓多所 `bookTicker`，对同一 pair 计算 `cross_gap_bps = (bid_rich - ask_cheap) / mid * 10000`；只有 `cross_gap_bps > fee_A + fee_B + slippage_buffer + inventory_buffer` 才算候选。
- 最小回测切口：先不做转账，只做 **inventory-funded** 版本；标的先从 `TUSDUSDT / USDCUSDT / FDUSDUSDT` 开始；母频率 `1s~5s` 采样，聚合成 `1m` 事件统计，先看 gap 持续时间和净正机会占比。
- 最该先看：`正净边机会占比`、`gap 持续秒数 / 分钟数`；其次才是跨 venue 再平衡频率和资本占用。

## 5. 风险与保留意见
- repo 的完整图搜索壳是有价值的，但**链上转账版天然更慢**，不该硬包装成 `1m/3m` 主信号。
- 当前公开快检里，绝大多数主流 stablecoin 对并不厚，只有 `TUSDUSDT` 显示出可见 pocket；这意味着机会可能是 **标的特异性**，不是普适到所有 stables。
- 看到 `positive gap` 不等于能成交：真实可做边还要扣双边 fee、冲击、排队、库存再平衡成本。
- 如果没有低费率 / maker / 预布库存，这条线很容易从“结构上成立”退化成“经济上不成立”。

## 6. 来源
- kevinl03. (2026). *Stablecoin-CrossExchange-Arbitrage*. GitHub.
  - Repo URL: `https://github.com/kevinl03/Stablecoin-CrossExchange-Arbitrage`
  - Read files: `README.md`, `docs/PROBLEM_FORMULATION.md`, `docs/ALL_FEES_BREAKDOWN.md`, `scripts/bellman_ford_arbitrage.py`, `scripts/weighted_astar.py`
- Binance Spot API docs.
  - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-order-book-ticker`
- OKX REST API docs.
  - Readable URL: `https://www.okx.com/docs-v5/en/#rest-api-market-data-get-tickers`
- KuCoin REST API docs.
  - Readable URL: `https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-all-tickers`
- MEXC Spot API docs.
  - Readable URL: `https://mexcdevelop.github.io/apidocs/spot_v3_en/#symbol-order-book-ticker`
- 本地快检 artifact：
  - `reports/artifacts/quant_digests/2026-04-18_stablecoin_crossvenue_gap_probe_summary.json`
  - `reports/artifacts/quant_digests/2026-04-18_stablecoin_crossvenue_gap_probe_rows.csv`
