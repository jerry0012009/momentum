# 别把 triangular arbitrage 只读成“零风险三腿搬砖”：对 short-cycle crypto desk，更该先保留的是「closed-loop mispricing × fee/capacity veto」这条 execution-heavy raw alpha 壳

- 时间：2026-04-23 19:10 UTC
- 类型：2025 *Finance Research Letters* 论文全文摘要级 audit（OpenAlex abstract + Crossref metadata）+ Binance Spot live public bookTicker probe（`BTCUSDT/LTCBTC/LTCUSDT`，约 `60s × 2Hz`）
- 主题类型：raw alpha
- 基础 alpha：**同一交易所内，若三条兑换边（如 `USDT→BTC→LTC→USDT`）的即时盘口乘积偏离 1，理论上可以通过三腿闭环交易锁定价差；也就是做 closed-loop relative-value arbitrage，而不是押方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但对延迟、手续费、盘口容量极度敏感
- 主题标签：raw-alpha/relative-value/stat-arb/triangular-arbitrage/closed-loop-mispricing/single-venue/spot/orderbook/fee-aware/slippage/capacity/execution-veto/1m/3m/5m/paper/public-data/cost/risk
- 证据类型：paper metadata + abstract + public live quote probe

## 1) 这次看了什么
主线材料：
- **Matthias Mück, Thomas Schmidl, Julian Wolf (2025)**
- **Title：** *Wish or reality? On the exploitability of triangular arbitrage in cryptocurrency markets*
- **Venue：** *Finance Research Letters*
- **DOI：** `10.1016/j.frl.2024.106508`
- **Readable URL：** <https://doi.org/10.1016/j.frl.2024.106508>
- **Repo URL：** N/A

可复述的 OpenAlex abstract 关键信息：
> 作者用 Binance 高频数据、围绕 `Bitcoin / Litecoin / U.S. Dollar` 实做 triangular arbitrage 检验，发现**样本里有 4,879 次表面上的 arbitrage opportunity**；但一旦加入**交易成本、潜在滑点和盘口容量限制**，这些机会基本被吃光，因此文中结论偏向：**中心化 crypto 市场已经相当有效**，而且“机会次数多”本身并不能直接当成市场低效的证据。

先把 base alpha 说清楚：
> **这条线的 base alpha 不是“币价会涨/跌”，而是三条边的相对价格没有同时自洽。**

翻成人话：
- 如果 `BTCUSDT`、`LTCBTC`、`LTCUSDT` 三条边里，有一条暂时偏贵/偏便宜；
- 那么你可以沿着“买入低估边、卖出高估合成腿”的三腿闭环去赚回到一致价的那一小段；
- 它本质上是 **single-venue closed-loop relative-value arb**，不是 trend，不是 mean-reversion 单腿猜方向，也不是 funding carry。

这条线之所以仍值得进研究池，是因为：
- 它是非常“干净”的 `raw alpha`；
- entry / exit / sizing / cost / risk 都能写清楚；
- 即便最终不适合当前 `5m/15m` desk 直接做主策略，它也很适合沉淀成 **fee/capacity veto** 与 **microstructure sanity check** 模块，服务别的 relative-value / stat-arb 壳。

---

## 2) 从论文里，真正该保留什么
这篇 paper 最重要的结论不是“tri-arb 还能赚大钱”，而恰恰相反：

1. **看见价差，不等于能吃到价差**
   - 论文里已经能数出 `4,879` 次表面机会；
   - 但加上真实 frictions 后，机会并不等于利润。
2. **对 tri-arb 来说，成本与容量比方向判断更重要**
   - 这类策略不是输在信号定义不清，而是输在：
     - 三腿都要成交；
     - 任一腿滑点扩大，闭环利润立刻归零；
     - 可成交量不足时，理论 edge 不能按名义仓位兑现。
3. **“机会计数”不是好指标，`net executable edge` 才是**
   - 这点很适合当前 desk：
   - 与其统计有多少次 `gross edge > 0`，不如直接统计：
     - 扣费后剩多少；
     - 扣最差一腿 half-spread 后还剩多少；
     - 在最薄腿的可成交量约束下，容量还剩多少。

对我们真正有价值的，不是复读“市场很有效”，而是下面这句：

> **如果一条 alpha 的 edge 量级还没厚到能扛住三腿手续费 + 最薄腿滑点 + 容量约束，那它更像研究层的价格一致性检验，不像 production-ready 短周期主策略。**

---

## 3) 本轮最小 public-data live probe（Binance Spot）
### 3.1 数据口径
为了避免只停在摘要，这轮补了一个最小 live 盘口快检：

- 交易所：Binance Spot public API
- 三角：
  - `BTCUSDT`
  - `LTCBTC`
  - `LTCUSDT`
- 采样：约 `60s × 2Hz = 120` 个 snapshot
- 数据：best bid / best ask（`bookTicker`）
- 两个闭环方向：
  - **Cycle A**：`USDT -> BTC -> LTC -> USDT`
  - **Cycle B**：`USDT -> LTC -> BTC -> USDT`
- 无费 gross 定义：
  - `gross_a = (1 / ask_BTCUSDT) * (1 / ask_LTCBTC) * bid_LTCUSDT`
  - `gross_b = (1 / ask_LTCUSDT) * bid_LTCBTC * bid_BTCUSDT`
- 粗略 taker 成本口径：每腿 `10 bps`，三腿后乘 `(1 - 0.001)^3`

产物：
- `reports/artifacts/quant_digests/2026-04-23_1910_triangular_arb_probe_raw.csv`
- `reports/artifacts/quant_digests/2026-04-23_1910_triangular_arb_probe_summary.csv`

### 3.2 关键结果（4 个最有用的数据点）
1. **120 个 snapshot 里，连无费 gross edge 都没有转正**
   - `gross_a_pos_count = 0 / 120`
   - `gross_b_pos_count = 0 / 120`
2. **最佳 snapshot 也还是负的**
   - `max gross_a = -4.55 bps`
   - `max gross_b = -4.53 bps`
3. **平均闭环缺口本身就已经偏负**
   - `avg gross_a = -8.00 bps`
   - `avg gross_b = -7.83 bps`
4. **最薄的一腿是主要摩擦源**
   - `avg BTCUSDT spread = 0.0013 bps`
   - `avg LTCUSDT spread = 1.81 bps`
   - `avg LTCBTC spread = 14.04 bps`

翻成人话：
- 这轮 live 快检甚至还没走到“扣三腿手续费”那一步；
- **单看盘口最优买卖价拼起来，闭环已经是负数**；
- 真正把 tri-arb 打死的不是 BTCUSDT 这种深度腿，而是像 `LTCBTC` 这种相对薄、spread 明显更宽的桥接腿；
- 所以 paper 里“机会很多但不可赚”的结论，对今天的 Binance 现货盘口依然很有解释力。

---

## 4) 这条线对当前 desk 的真正价值
### 4.1 它是 raw alpha，但不是当前 `5m/15m` desk 的优先 deployment
因为它满足 raw alpha 的定义：
- 交易对象明确；
- long/short（或 buy/sell）路径明确；
- 平仓条件明确；
- 成本与容量决定是否可做。

但它对当前 desk 的问题也很明显：
- edge 持续时间通常比 `5m` 更短；
- 强依赖盘口级别撮合；
- `1m/3m/5m/15m` bar 只能拿来做 **事件桶统计 / veto / sanity check**，很难直接拿来当 parent signal。

所以这轮更诚实的定位是：
- **主题类型仍是 `raw alpha`**；
- **但当前 desk 一阶用途不是直接上 production tri-arb，而是把它当作“execution-heavy raw alpha 的边界案例”。**

### 4.2 更值得 desk 保留的，是它衍生出来的两个模块
#### 模块 A：`net executable edge` 审核器
任何 relative-value / cross-venue / basis / option quote-gap 策略，都该先过这道门：
- gross edge
- minus fee
- minus worst-leg half-spread
- minus depth cap
- minus stale-quote risk

如果这 5 步走完 edge 归零，就别再把它包装成 alpha。

#### 模块 B：最薄腿 veto
tri-arb 给的教训非常直接：
- 不是组合里每一腿都同等重要；
- 往往 **最薄、最宽、最容易滑的那一腿** 决定了整条策略的死活。

这个思想完全可以迁移到：
- cross-venue gap
- perp-vs-quarterly basis
- multi-leg options quote-gap
- pairs / basket 的 child execution

---

## 5) 若真要做，可直接落地的完整策略壳
### 5.1 Entry（入场）
按 snapshot/event-time 而不是按 bar：

1. 维护候选三角集合（优先高流动腿 + 少数桥接腿）
2. 实时计算两方向闭环：
   - `gross_edge_a = gross_a - 1`
   - `gross_edge_b = gross_b - 1`
3. 再算净边：
   - `net_edge = gross_edge - fees - slippage_buffer - stale_quote_buffer`
4. 仅当 `net_edge > theta_enter` 且最薄腿容量足够时才下单

建议第一版阈值不要太乐观：
- `theta_enter >= 3 ~ 5 bps`（扣完一切后的净边）
- 否则只是给交易所打工。

### 5.2 Exit（出场）
tri-arb 的 exit 不是传统 time-stop，而是：
- 三腿成交即完成闭环；
- 若任一腿未成交，立刻进入 **failure unwind mode**；
- 失败 unwind 比原始信号更重要，因为这时你已从“无方向”变成“裸露单腿或双腿风险”。

### 5.3 Sizing（仓位）
- 以 **最薄腿可成交量** 决定整组 notional，而不是以最深腿决定；
- 只做 `min(depth_i)` 能吃下的仓位；
- 同时按预估 fill ratio 做折扣（例如只取显示量的 `20%~50%`）。

### 5.4 Risk（风控）
- stale quote 超时熔断
- 桥接腿 spread 突然放大熔断
- 任一腿超时未成 → 立刻撤/反向对冲
- 单三角 / 单桥接资产 / 单 venue notional cap
- 网络延迟或 API 抖动期间禁开新闭环

### 5.5 Cost（成本）
这条线最该做的是极端保守的 friction ladder：
- maker/maker/maker
- maker/taker/taker
- taker/taker/taker
- 再分别叠加最薄腿 `0.5x / 1.0x / 1.5x spread` 滑点缓冲

只要在 `taker/taker/taker + thin-leg slippage` 下过不了线，就不要把它写成生产级机会。

---

## 6) 对 `1m / 3m / 5m / 15m` 的映射
### `1m`
最勉强可接受的研究口径：
- 不是拿 1m OHLC 做 tri-arb；
- 而是把 1 秒 / event-time 的闭环机会聚合成 1m 统计：
  - `gross_pos_count`
  - `net_pos_count`
  - `max_net_edge`
  - `thin_leg_spread`
  - `depth_ratio`

### `3m / 5m`
更适合做 **环境监控 / veto**：
- 哪些时段三角失衡明显增多？
- 这些时段是否同时对应：
  - 薄腿 spread 异常拉大
  - 跨所 gap 变多
  - basis / funding / option quote-gap 机会增多

也就是把 tri-arb 当成 **microstructure stress thermometer**。

### `15m`
不适合作 tri-arb 主执行周期；
但适合作为：
- 市场质量面板
- 子策略的 execution veto
- “今天这种盘口环境到底值不值得跑 multi-leg stat-arb” 的 admission layer

---

## 7) 最小实验：下一步怎么测
这条线最值得做的不是“再写一篇摘要”，而是下面 3 个最小实验：

### 实验 1：三角宇宙扩展 + 事件桶统计
- 不只看 `BTC/LTC/USDT`；
- 扩到 `BTC/ETH/USDT`、`ETH/BNB/USDT`、`SOL/BTC/USDT` 等高流动三角；
- 记录：
  - `gross > 0` 次数
  - `net > 0` 次数
  - 最薄腿 spread
  - 最薄腿 depth
- 目标：先确认“有没有哪类三角比 `LTCBTC` 这种桥接腿更友好”。

### 实验 2：把 tri-arb 指标迁移成 shared veto
在已有的：
- cross-venue gap
- basis fade
- options quote-gap
- pairs child execution
上，加一个 5m gate：
- 若近 `5m` 的 thin-leg spread / stale-quote / tri-arb negative-gap 明显恶化，则降仓或停机。

这对当前 desk 反而比“真做 tri-arb”更可能马上有价值。

### 实验 3：maker-first 假设压力测试
如果仍想保留 production 幻想，就要直接测：
- maker-first fill ratio 假设是否现实；
- 一旦一腿吃不到被迫 taker 补腿，edge 会不会瞬间翻负；
- 这一步做完，通常就能知道它到底是策略，还是幻觉。

---

## 8) 本轮结论
### 结论一句话
> **triangular arbitrage 是一条定义非常干净的 raw alpha，但对当前 short-cycle crypto desk，它更像“execution-heavy 边界案例”而不是优先 deployment 主线；真正值得保留的，是它逼你把 `gross edge` 和 `net executable edge` 分开。**

### 当前 verdict
- **是否值得进素材池：值得**
- **是否值得作为当前 `5m/15m` 主策略优先复现：不值得**
- **更合适的角色：**
  - raw alpha 边界样本
  - multi-leg relative-value 的 cost/capacity 教材
  - shared execution veto / market-quality gate 的启发来源

### 对 Jerry 当前阶段的意义
最近 desk 已经堆了不少：
- pairs
- basis
- funding
- cross-venue outlier
- options quote-gap

这篇的价值不在于再贡献一条能直接上的主策略，而在于补上一个重要认知缺口：

> **不是所有 raw alpha 都输在“信号不够聪明”；很多 multi-leg alpha 是输在“edge 厚度不够穿过执行摩擦”。**

这条认识，对后面继续做 relative-value / stat-arb，反而很值钱。

---

## 9) 文件与链接
- Digest 路径：`research/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.md`
- 预计页面 URL：<https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-23_1910_triangular-arb-fee-capacity-reality-check.html>
- Probe raw：`reports/artifacts/quant_digests/2026-04-23_1910_triangular_arb_probe_raw.csv`
- Probe summary：`reports/artifacts/quant_digests/2026-04-23_1910_triangular_arb_probe_summary.csv`
- Source DOI：<https://doi.org/10.1016/j.frl.2024.106508>
- OpenAlex work：<https://openalex.org/W4405131149>
