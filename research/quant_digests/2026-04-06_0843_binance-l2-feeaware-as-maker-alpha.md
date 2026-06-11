# 别把 A-S 继续只读成教科书：这份 2026 Binance L2 repo 更该先测的是「fee-aware reservation-price maker × latency / queue realism」这条完整 raw alpha
- 时间：2026-04-06 08:43 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `code/README.md` + `code/as_backtest.py` + `code/run_as_pipeline.py`）+ Binance Futures 官方公开文档 + 经典 inventory-based market making 文献 grounding
- 主题类型：raw alpha
- 基础 alpha：**在 Binance Futures `BTCUSDT` 上持续挂双边 maker quote，赚的是“可覆盖 maker fee 的 bid-ask spread capture”；`reservation price / inventory skew / fee floor / latency / queue` 这些不是 alpha 替身，而是把这条 spread alpha 从玩具回测拉回现实所必需的执行层。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/maker/market-making/spread-capture/avellaneda-stoikov/reservation-price/inventory-risk/fee-aware/latency/queue/binance-futures/btcusdt/orderbook-l2/aggtrade/1m/3m/5m/15m/repo/paper/public-data/cost/risk
- 证据类型：开源研究 repo + 经典 market making 论文 + Binance 官方公开 API 文档

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = 在高流动、持续有对手盘的 perpetual order book 上，双边提供流动性并吃 spread。**
> 不是方向预测，不是 filter，也不是 overlay；真正的赚钱假设仍然是 **spread capture**。只是这份 repo 的价值在于，它把「费率、延迟、排队」这些最容易把纸面 maker alpha 打回负数的现实约束，直接塞进了同一个可复现研究壳里。

## 1. 这次看了什么
**这轮更值得先收的，不是又一篇“maker 很赚钱”的截图，而是这份 2026 新 repo 对 `BTCUSDT` 真实 L2 的重建式 A-S 回测：它让我们第一次能把 maker raw alpha 本体，和 fee / latency / queue 这三层现实损耗拆开测清楚。**

这轮选它，主要有 4 个原因：

1. **不撞最近主题。** 最近 digest 已经连续补了不少 `pairs / carry / cross-sectional / LOB directional` 题；maker 虽然也出现过，但更多是宽价差 alt-perp 壳，**这次是 `BTCUSDT` + 真实 L2 + queue/latency realism**，不是同一件事。
2. **它是完整 raw alpha 壳，不是解释型综述。** repo 明确给了：
   - 数据采集；
   - order book 重建；
   - A-S 报价；
   - fee-aware quote floor；
   - latency / cancel-replace 生命周期；
   - inventory / cash / max-notional 约束；
   - JSON 与 HTML 输出。
3. **它正好补 desk 当前研究池里“maker alpha 现实校准版”的空缺。** 之前很多材料把 maker alpha 写成“spread 足够宽就能收”；这份 repo 最有价值的地方是告诉我们：
   > **gross edge 可能有，但净值常常先死在 fee，再死在 stale quote 和 queue 幻觉。**
4. **跟当前 short-cycle 研发链路能直接拼起来。** 最近 desk 已经累了很多 `OBI / OFI / liquidity veto / adverse selection overlay` 素材；这份东西不是和它们竞争，而是给这些组件找到了一个更自然的宿主：
   **maker raw alpha 本体 + toxicity/regime veto。**

## 2. 这条东西的 base alpha 到底是什么
要先把话说死，不然很容易把 A-S 读歪：

> **A-S 的 base alpha 不是“模型公式”，而是“被动挂单吃 spread”本身。**

说人话：
- 你在 bid 和 ask 两边都愿意提供流动性；
- 如果对手持续来打你，且你的双边价差能覆盖手续费与库存风险；
- 那么反复的小额 spread capture，理论上就能累积成正毛利。

所以这里：
- `reservation price` 负责把库存风险价格化；
- `half-spread` 负责决定你挂多宽；
- `fee floor` 负责避免“明明成交了，但每次 round-trip 都先亏给手续费”；
- `latency / queue` 负责告诉你：
  **纸面上触价 ≠ 真实世界里轮得到你成交。**

它们都重要，但它们服务的仍然是同一个 raw alpha：
**two-sided spread capture**。

## 3. 这份 2026 repo 到底给了什么
### 3.1 来源与定位
- **Repo**：Haoyu-tech, *An Avellaneda-Stoikov market-making research project built on real Binance Futures BTCUSDT L2 data* (GitHub, 2026)
- Repo URL：<https://github.com/Haoyu-tech/An-Avellaneda-Stoikov-market-making-research-project-built-on-real-Binance-Futures-BTCUSDT-L2-data.>
- 创建时间：`2026-03-20`
- 最近更新时间：`2026-03-28`
- GitHub stars：`16`

README 开宗明义写得很清楚：
这**不是 production trading system**，而是一个“把完整研究 workflow 复现出来”的项目。它的研究路径是：

1. 收集 Binance Futures `snapshot / diff depth / aggTrade`；
2. 用 `snapshot + diff depth` 重建 order book；
3. 跑带 inventory risk 的 Avellaneda–Stoikov backtest；
4. 显式加入 fees、cash constraints、inventory constraints、order latency、cancel latency；
5. 导出结构化 JSON 和 HTML 报告。

这点很关键：
> **它不是只给了一个公式，而是给了从 public data 到报告输出的完整研究闭环。**

### 3.2 当前 findings：最值钱的不是“能赚钱”，而是“知道先亏在哪”
repo README 自己总结的当前结论非常实：

- 策略在一些短样本上**有很薄的 gross edge**；
- 一旦加上真实手续费，**net PnL 经常转负**；
- latency 与 quote refresh 行为会明显影响 fills 和结果；
- 更大的 `order_size` 往往同时放大收益和回撤；
- 这比玩具回测更真实，但仍然**不是交易所级 matching engine**。

这几句其实就是这篇 digest 的核心：
**maker alpha 值得收，但必须先当“gross alpha + execution haircut”去测，而不是把 gross 误当净 alpha。**

### 3.3 它给的默认参数，已经足够拼成完整策略
README 列出的 `as_backtest.py` 默认参数：

- `order_size = 0.003`
- `max_order_notional = 300`
- `inventory_limit = 0.03`
- `maker_fee_rate = 0.0002`
- `dynamic_window_seconds = 10`
- `order_latency_ms = 150`
- `cancel_latency_ms = 100`
- `fee_spread_multiplier = 1.0`

这意味着它天然已经是一个完整策略壳：
- **entry**：双边挂 quote，等待 passive fill；
- **exit**：对手来打、库存回摆、或风控约束导致不再继续挂同向单；
- **sizing**：固定 `order_size`，但受 `cash / max_notional / inventory_limit / qty_step` 共同裁剪；
- **risk**：库存上限、现金上限、延迟、排队、手续费底线；
- **cost**：maker fee 直接进入 quote 宽度与净 PnL。

所以它不是单独一个 filter，也不是只会给一个“alpha 方向”；
它本身就是一条能落成完整策略的 raw alpha shell。

## 4. 这份源码里真正值得 desk 抄的 5 个东西
### 4.1 它不是用 K 线触发成交，而是先重建 book，再回放 trade
`as_backtest.py` 先读取：
- `snapshot.ndjson`
- `depth.ndjson`
- `aggtrade.ndjson`

然后：
- 用 snapshot 初始化 bids/asks；
- 用 diff-depth 增量更新盘口；
- 对每个事件重新计算 `best_bid / best_ask / mid / spread`；
- 再用 `aggTrade` 去检查 resting order 是否真的能被打到。

这是它相对很多 maker repo 最重要的升级：
> **不再是“bar high/low 碰到报价就算成交”，而是起码有了 book state + trade replay。**

这还不等于完美，但已经从“回测幻觉”往前走了一大步。

### 4.2 它把经典 A-S reservation price 真正落到了动态参数上
源码里最关键的一行是：

- `reservation = event.mid - account.position_btc * auto_gamma * (sigma_now**2) * quote_horizon`

然后 half-spread 取：
- 经典 A-S 风险补偿项；
- 当前真实盘口半价差 `0.5 * event.spread`；
- 手续费下限 `min_half_spread_from_fees`；
三者的最大值。

这件事的交易翻译很简单：
- 库存越偏，`reservation price` 越往减仓方向偏；
- 波动越大、成交衰减越快，理论 half-spread 越宽；
- 但不管模型怎么说，**如果连 fees 都覆盖不了，就不该挂太窄。**

这比很多“只背 A-S 公式”的实现强很多，因为它明确承认：
**真实 maker quote 的下界，常常不是理论最优，而是成本最优。**

### 4.3 它不是静态 sigma/k，而是滚动估计
源码里 `dynamic_window_seconds = 10`，会在滚动窗口里动态估计：
- `sigma`
- `intensity`
- `k`

并在 `gamma` 未手动指定时，先用库存风险预算推一个 base gamma，再在候选 gamma 网格上做小规模选择。

这让它更像 short-cycle desk 会真的去做的事情：
不是用一个永远不变的全局参数，而是承认**盘口毒性和 arrival intensity 是会随时间变的。**

### 4.4 它把 queue 与 latency 作为 alpha 生死线，而不是回测注脚
源码里专门做了两件多数 repo 会跳过的事：

1. **queue ahead**
   - resting buy order 若挂在 best bid，初始 `queue_ahead = best_bid_qty`
   - resting sell order 若挂在 best ask，初始 `queue_ahead = best_ask_qty`
   - 后续再根据盘口更新慢慢消耗 queue
2. **订单生命周期**
   - 新单不是立刻生效，而是 `order_latency_ms = 150`
   - cancel/replace 也不是瞬时，而是 `cancel_latency_ms = 100`
   - target quote 和 active quote 被分开处理

这两层现实性非常关键，因为 maker alpha 的大坑往往不是“公式不够优雅”，而是：
- 你以为自己挂在 best bid；
- 其实你在队尾；
- 你以为自己及时撤单了；
- 其实 stale quote 还在市场里裸奔。

### 4.5 它把 size 真正受现金与库存约束，而不是永远固定不变
源码里 buy size 会被裁成：
- `cash_usdt` 能负担的最大可买量；
- `inventory_limit - current_position` 允许的最大量；
- `max_order_notional / bid_quote` 的额度上限；
- 再做 `qty_step` 对齐。

sell side 也同样受库存边界控制。

这意味着它不是“理论上一直双边对称挂满”，而是会因为已有库存与现金状态，**动态缩一边、保另一边**。

对 desk 来说，这正是 maker raw alpha 该有的定义：
- alpha 本体是 spread；
- 但持仓/现金状态会决定你还能不能继续吃这份 spread。

## 5. 这份 repo 里最该记住的关键数字
### 5.1 5 分钟 baseline：gross 是正的，net 先被 fee 吃掉
README 给出的最新 5-minute full pipeline run：

- `events = 2925`
- `trades_seen = 5304`
- `fills = 5`
- `gross_pnl_before_fees = +0.0453 USDT`
- `fees_paid = 0.1690 USDT`
- `net_pnl = -0.1237 USDT`

这组数非常值钱，因为它告诉我们：

> **在真实 L2 + aggTrade 的短样本上，spread capture 毛利可以为正，但若 quote 不够宽、成交不够好、或 fill 数太稀，fee 很容易把净值直接吃穿。**

### 5.2 zero-fee size sweep：粗看不是“完全没有 alpha”，而是“alpha 先薄后死”
README 还给了一个信息点：

- 在 `zero fees` 假设下，`size = 0.005` 大约 `net_pnl ≈ +0.00625 USDT`

这不是为了鼓吹“去掉 fee 就稳赚”；
恰恰相反，它告诉我们最现实的一句话：

> **这条 alpha 更像“有一点点 gross edge，但边际很薄”，所以任何 fee、latency、queue 误判都会把它从正打成负。**

### 5.3 public data 的时间粒度足够给 1m/3m/5m/15m desk 做最小实验
Binance 官方公开文档写明：

- **Diff Book Depth Streams**：盘口增量可按 `100ms / 250ms / 500ms` 推送；
- **Aggregate Trade Streams**：`aggTrade` 以 `100ms` 聚合成交推送；
- **REST Order Book**：`GET /fapi/v1/depth` 可取 snapshot，支持公开查询。

这意味着这条研究不依赖私有撮合日志；
**最小实验所需数据是公开可拿、更新频率也足够高的。**

## 6. 这条东西为什么必须归成 raw alpha，而不是 overlay / filter
这个分类很重要。

如果这篇东西的核心只是：
- 高波动时别做；
- 库存偏多时少买点；
- latency 高时谨慎点；
那它顶多算 overlay。

但这里不是。

这里真正被交易的对象是：
- 持续挂 bid/ask；
- 用对手盘成交把 spread 兑现；
- 通过反复的双边小额成交积累 PnL。

所以：
- **raw alpha = maker spread capture**；
- **filter / overlay = latency、queue、inventory、toxicity 只是在决定这份 raw alpha 能否活下来。**

换句话说：
> **它不是“maker 的风控研究”；它首先是一条 maker raw alpha，然后顺手把风控做对了。**

## 7. 它和 `1m / 3m / 5m / 15m` 的关系该怎么读
这条东西不是传统 K 线 directional signal，所以不能硬装成“每根 5m bar 预测未来 5m return”。

更诚实、也更适合 desk 的读法是：

### `1m / 3m`
拿来做：
- rolling sigma / spread / fill-rate / adverse-selection 监控；
- quote 开关；
- inventory skew 与 toxicity veto 的参数更新。

### `5m`
拿来做：
- gamma/k 或 fee floor 参数分桶；
- gross spread 与 net spread 的 rolling 健康度评估；
- 是否继续在这一段市场里挂双边。

### `15m`
拿来做：
- maker shell 是否开启；
- 是否切到更保守的 only-one-side / wider-spread / no-quote 模式；
- 跨标的选择时的 admission refresh。

也就是说：
> **事件时间是执行时钟，`1m/3m/5m/15m` 是管理时钟。**

这并不削弱它的价值，反而让策略定义更符合实盘。

## 8. 对当前 desk，最值得先测的不是“能不能赚”，而是 4 个 realism haircut 各砍掉多少
这是我认为这份材料最该带来的测试框架：

### 8.1 最小可复现实验口径
**数据源**
- Binance USDⓈ-M Futures 公开数据：
  - `/fapi/v1/depth` snapshot
  - WebSocket diff-depth
  - WebSocket aggTrade

**公开性**
- 官方公开 API / WebSocket，无需私有成交回报。

**更新频率**
- depth 增量：`100ms/250ms/500ms`
- aggTrade：`100ms`
- snapshot：按需拉取初始化。

**最小实验标的**
- 先只做 `BTCUSDT`。

**最小实验窗口**
- 先抓 `20` 个独立 `15m` session；
- 每个 session 内再切 `1m / 3m / 5m` 管理窗口看参数稳定性。

### 8.2 先不要直接调参暴力找正收益，先跑 4 组对照
A. **Toy A-S**：无 fee、无 latency、无 queue；
B. **+ Fee floor**：加 maker fee 下界；
C. **+ Latency**：加 `150ms/100ms` 订单生命周期；
D. **+ Queue**：加 queue-ahead 与 aggTrade fill 检查。

最该看的不是最终绝对收益，而是每加一层现实性时：
- fills 掉多少；
- gross spread capture 掉多少；
- fee 占 gross 的比例升多少；
- adverse selection 是否变重；
- inventory 偏离是否放大。

如果 A 正、B/C/D 全负，那就别再骗自己“alpha 还在”。
如果 A/B/C 还能活，只是 D 砍掉一半，那下一步就该去做 **queue / quote-priority 优化**，而不是盲目 widen spread。

### 8.3 这条 alpha 对 desk 最现实的升级方向
我会把下一步拆成 3 级：

1. **先复现 repo 原壳**
   - `BTCUSDT`
   - 60s / 300s / 900s 多窗口
   - 复核 README 的 gross / fee / net 关系是否稳定出现。
2. **再接 desk 已有的 microstructure veto 组件**
   - 把已有 `OBI / OFI / slippage / liquidity` 素材接成 maker veto；
   - 问的是：能不能少做“明知会被毒打”的时段，而不是靠更复杂公式挤收益。
3. **最后才考虑扩到 ETH / SOL 或更宽价差 alt-perp**
   - 先在 `BTCUSDT` 把 realism haircut 拆清楚；
   - 再去更宽价差标的上吃更厚 spread，否则很容易把标的差异误当模型进步。

## 9. 我对这条东西的最终判断
### 结论一句话
**值得进研究池，而且优先级不低。**

但值得收的不是“Avellaneda–Stoikov”这个大名字本身，而是：

> **这份 2026 repo 终于把 maker raw alpha 最容易自欺的三件事——fee、latency、queue——一起摆上桌了。**

所以对当前 desk，它的最佳用法不是：
- 再做一篇教科书公式复述；
- 也不是把 README 当收益证明；

而是把它当作：
- **maker raw alpha 的现实基线**；
- 后续所有 `OBI / OFI / toxicity / volatility veto` 组件的主宿主。

## 10. 下一步怎么测
### 必做版（本周内可完成）
1. 用 Binance 公开 `snapshot + diff-depth + aggTrade` 抓 `BTCUSDT` 连续 `20` 个 `15m` session。
2. 复现 4 组对照：`Toy / +Fee / +Latency / +Queue`。
3. 统一报 6 个指标：
   - `gross_pnl_before_fees`
   - `fees_paid`
   - `net_pnl`
   - `fills`
   - `inventory_abs_mean`
   - `quote_refresh_events / replace_requests`
4. 只要 **D 组（全现实）仍在 20 个 session 里有稳定的 gross>0 且 fee 占 gross 比例可压缩**，才继续做下一层 veto；否则先停。

### 增量版（若必做版没死）
5. 把最近 desk 已积累的：
   - order-book imbalance
   - flow toxicity
   - slippage veto
   - short-horizon realized vol gate
   依次接到 maker 壳上，测它们各自对 `fills / gross / net / inventory tail` 的边际改善。
6. 最后再做一次跨标的 portability：
   - `BTCUSDT -> ETHUSDT -> SOLUSDT`
   - 看是“模型真的有效”，还是“只是 BTC 的微观结构刚好更友好”。

## 11. 来源
### 论文 / 理论地基
1. **Marco Avellaneda, Sasha Stoikov (2008). _High-frequency trading in a limit order book_. Quantitative Finance.**
   - DOI：`10.1080/14697680701381228`
   - Readable URL：<https://doi.org/10.1080/14697680701381228>
2. **Olivier Guéant, Charles-Albert Lehalle, Joaquin Fernandez-Tapia (2013). _Dealing with the inventory risk: a solution to the market making problem_. Mathematics and Financial Economics.**
   - DOI：`10.1007/s11579-012-0087-0`
   - Readable URL：<https://doi.org/10.1007/s11579-012-0087-0>
   - arXiv readable version：<https://arxiv.org/abs/1105.3115>

### 主体 repo
3. **Haoyu-tech (2026). _An Avellaneda-Stoikov market-making research project built on real Binance Futures BTCUSDT L2 data_. GitHub repository.**
   - Repo URL：<https://github.com/Haoyu-tech/An-Avellaneda-Stoikov-market-making-research-project-built-on-real-Binance-Futures-BTCUSDT-L2-data.>
   - README raw：<https://raw.githubusercontent.com/Haoyu-tech/An-Avellaneda-Stoikov-market-making-research-project-built-on-real-Binance-Futures-BTCUSDT-L2-data./main/README.md>
   - Code README raw：<https://raw.githubusercontent.com/Haoyu-tech/An-Avellaneda-Stoikov-market-making-research-project-built-on-real-Binance-Futures-BTCUSDT-L2-data./main/code/README.md>
   - Backtest core raw：<https://raw.githubusercontent.com/Haoyu-tech/An-Avellaneda-Stoikov-market-making-research-project-built-on-real-Binance-Futures-BTCUSDT-L2-data./main/code/as_backtest.py>
   - Pipeline raw：<https://raw.githubusercontent.com/Haoyu-tech/An-Avellaneda-Stoikov-market-making-research-project-built-on-real-Binance-Futures-BTCUSDT-L2-data./main/code/run_as_pipeline.py>

### 公开数据文档
4. **Binance Open Platform. USDⓈ-M Futures Market Data Docs.**
   - Diff Book Depth Streams：<https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Diff-Book-Depth-Streams>
   - Aggregate Trade Streams：<https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Aggregate-Trade-Streams>
   - REST Order Book：<https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book>
