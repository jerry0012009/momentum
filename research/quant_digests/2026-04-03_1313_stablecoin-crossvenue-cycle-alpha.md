# 别把这份 2025/2026 stablecoin repo 只读成图搜索作业：对 short-cycle desk，更该先测的是「cross-exchange stablecoin cycle mispricing × inventory-funded execution」这条完整 raw alpha
- 时间：2026-04-03 13:13 UTC
- 类型：GitHub / 课程研究报告
- 主题类型：raw alpha
- 基础 alpha：**同一组稳定币（`USDT / USDC / DAI / FDUSD` 等）在不同交易所与不同报价边之间会短暂形成“负对数为负”的套利环；只要净价差覆盖手续费、滑点和转账/库存成本，就能做成可执行的 cross-exchange cycle arbitrage。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**是**
- 主题标签：raw-alpha/relative-value/stat-arb/stablecoin/cycle-arbitrage/cross-exchange/graph-search/astar/inventory-funded/rebalance/transfer-penalty/usdt/usdc/dai/fdusd/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：2025/2026 GitHub repo source audit（README）+ SFU CMPT 827 research report PDF + 交易所公开行情接口口径

## 1. 这次看了什么
这轮补一个**和最近 OFI / pairs / funding 线不同、但同样能直接落成完整策略**的 raw alpha：Simon Fraser University 课程项目 **`Stablecoin-CrossExchange-Arbitrage`**。一句话核心结论：**真正值钱的不是“图搜索算法”本身，而是“稳定币跨所/跨边循环错价”这条可直接交易的相对价值 alpha。** 一句话证明方式：**作者把多交易所稳定币报价、手续费、转账成本和搜索耗时一起放进图模型里，比了 Dijkstra / A* / 两层启发式，并用 Monte Carlo 模拟比较利润与速度。**

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：**stablecoin cycle mispricing**，不是 filter，不是解释型综述。
- 报告里最有用的数不是“找到多少路径”，而是**净后仍有几十 bps 的 cycle pocket**：在作者设定的 common scenarios 下，Heuristic 4 的利润率大约 **32 / 39 / 42 bps**（对应 `$1k / $10k / $100k` 初始资金）。
- 纯追求最优利润不一定最适合 desk：Monte Carlo 里 **Heuristic 3** 在 100% 成功率时平均利润最高（约 **$203**），但 **Heuristic 4** 用约 **4.7 秒**就能给出结果，显著快于 H1/H2（约 **109~120 秒**）和 H3（约 **50 秒**），在 **80% 成功率**附近反而更均衡。
- 对 short-cycle desk，最值得抄的不是“每次都真转账闭环”，而是**把 graph search 当作路由器，把 alpha 本体定义成 inventory-funded 的跨所稳定币循环错价**；转账更适合作为再平衡/补库存层，而不是每笔都强绑定。
- 因为信号天然来自公开 bid/ask 与 fee schedule，它能直接映射到 `1m / 3m / 5m / 15m`：`1m/3m` 更适合做 entry 与可成交性检查，`5m/15m` 更适合做 pocket persistence 与库存回补节奏。

## 3. 为什么和当前项目有关
最近 digest 已经补了 OFI、pairs、funding carry、跨所 premium 等线；这轮继续优先 raw alpha，但换一条**更偏 stablecoin / relative-value / routing** 的素材，避免只在某一类 directional 或 pairs 上内循环。

它和当前 `momentum` 主线的关系不是“另一个抽象过滤器”，而是：
- 给 raw alpha 素材池补一个**完整可落地的 stat-arb/cycle** 方向；
- 给后续执行层提供一个很实用的工程骨架：**图建模、负对数权重、路径筛选、库存约束、成本门槛**；
- 给已有 stablecoin 主题（FDUSD/USDC、peer parity、depeg overlay）补一个更偏**跨 venue 可执行路由**的分支。

## 3.5 策略拆解（必填）
- 方向属性：**相对价值 / stat-arb / cycle arbitrage**
- 基础 alpha：**稳定币在多交易所、多报价边之间的净错价环会短暂存在，且足以覆盖摩擦时可做收敛。**
- regime：**高流动性、低链拥堵、主要稳定币报价稳定、库存充足时更适合开；极端 depeg / 风险事件时需切到保守模式。**
- filter / veto：**净 edge 必须同时覆盖 fee + slippage buffer + inventory imbalance penalty；禁止走慢链、禁止小深度边、禁止单跳后剩余容量不足的路径。**
- risk / sizing / execution overlay：**优先 inventory-funded 执行；按可用库存与盘口深度决定名义；设 venue exposure cap、单 stablecoin concentration cap、再平衡冷却时间与失败重试上限。**

## 4. 可复刻的最小实验
**研究假设：** 如果把公开可得的稳定币 top-of-book、手续费和库存限制一起放进 cycle 图，`5m` 级别仍能找到一批成本后为正、且在 `1m~5m` 内可维持的 pocket。

**可计算定义：**
1. 节点：`(venue, coin)`，先只做 `Binance / Kraken / Coinbase` × `USDT / USDC / DAI / FDUSD`。
2. 边：
   - 同所币币兑换边：用最优 bid/ask 扣手续费；
   - 跨所同币库存边：最小实验先用 **inventory-funded** 假设，按再平衡罚分代替即时转账；
   - v2 再加入真实 withdrawal fee / chain latency。
3. 信号：若某闭环路径的 `net_return_bps >= {15, 25, 40}` 且容量覆盖下单名义，则触发。

**最小回测切口：**
- 频率：先存 `1m` snapshot，再聚合看 `3m / 5m / 15m`
- 样本：最近 `30~60` 天
- 资产：先只测稳定币主对，避免一开始混入 BTC/ETH 方向风险

**先看 2 个指标：**
- `post-cost positive cycle count / day`
- `inventory-funded net bps` 与 `full-transfer net bps` 的差距

**下一步怎么测：**
1. 先做 `inventory-funded` 版本，验证 pocket 数量与净 bps；
2. 再给每条路径加 `depth haircut` 和 `rebalance penalty`；
3. 最后再比较 `A* / H4` 与简单 greedy routing，确认 edge 来自错价本身，还是只来自搜索器更聪明。

## 5. 风险与保留意见
- 这份材料是**课程项目 + repo**，不是成熟实盘审计报告；关键数字更像工程原型证据，不是 live PnL。
- 报告中的“转账成功率 / 成本 / 场景参数”带有模拟设定；若链上确认变慢、出入金规则变化，edge 会明显变薄。
- README 与报告里的支持交易所口径并不完全一致（README 提到 Coinbase，报告正文主实验更多是 Binance/Kraken/KuCoin/Bybit），复现时应自己锁定一个小而干净的 venue set。
- 真正决定能不能活下来的，往往不是搜索算法，而是**库存管理、深度、费用、失败重试、再平衡频率**；如果这些不纳入，回测会明显乐观。
- 这条线和 `BTC/ETH` directional alpha 不同，更像一个**全天候扫描、机会稀疏但可重复**的 relative-value pocket；因此适合进素材池，但不该被误写成“大行情主线信号”。

## 6. 来源
1. **Kevin Li, Aryan Litvin, Pejman Katchooi, Prashant Singh. (2025). _Stable Coin Arbitrage_. Simon Fraser University, CMPT 827 project report.**
   - DOI: N/A
   - Readable URL: <https://github.com/kevinl03/Stablecoin-CrossExchange-Arbitrage/blob/integration/StableCoinArbitrage-ResearchReport.pdf>
   - Repo URL: <https://raw.githubusercontent.com/kevinl03/Stablecoin-CrossExchange-Arbitrage/integration/StableCoinArbitrage-ResearchReport.pdf>

2. **kevinl03 et al. (2025/2026). _Stablecoin-CrossExchange-Arbitrage_. GitHub Repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/kevinl03/Stablecoin-CrossExchange-Arbitrage>
   - Repo URL: <https://github.com/kevinl03/Stablecoin-CrossExchange-Arbitrage>

3. **CCXT Project. (2026 access). _CCXT: A cryptocurrency trading API with support for more than 100 bitcoin/altcoin exchanges_.**
   - Venue: GitHub / Docs
   - DOI: N/A
   - Readable URL: <https://docs.ccxt.com>
   - Repo URL: <https://github.com/ccxt/ccxt>

4. **Public exchange market-data docs (2026 access). Binance / Coinbase / Kraken spot order book & ticker endpoints.**
   - Venue: Official API Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints>
   - Readable URL: <https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductbook>
   - Readable URL: <https://docs.kraken.com/api/docs/rest-api/get-order-book>
