# 别把三角套利只读成“老掉牙搬砖”：对 short-cycle crypto desk，更该先测的是「同所同步报价里的 cross-rate inconsistency」这条 relative-value raw alpha
- 时间：2026-04-18 10:48 UTC
- 类型：GitHub repo source audit + Binance Spot `bookTicker` live public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`同一交易所、同一时点的多币对买一卖一若无法满足 cross-rate 一致性，存在可闭环执行的三腿汇率套利收益`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / triangular-arbitrage / cross-rate / law-of-one-price / spot / binance / usdt / usdc / fdusd / eth / 1m / 3m / 5m / repo / public-data / cost / risk
- 证据类型：repo audit + live top-of-book probe

## 1. 这次看了什么
这轮主看的是 GitHub 仓库 `Drakkar-Software/Triangular-Arbitrage`，核心文件包括：
- `README.md`
- `triangular_arbitrage/detector.py`
- `tests/test_detector.py`

它做的事情很直接：把交易对当成有向图上的边，遍历闭环路径，找出乘积大于 `1` 的 cycle。repo 默认用的是 `last/close` 价，**不含买卖价差、不含手续费、不含执行顺序约束**；所以它给的是一个 raw alpha 探测器，不是现成可上线的 execution engine。

但它的优点也正好在这里：**base alpha 非常清楚**，不是 overlay，不是 filter，就是最朴素的 Law-of-One-Price 偏离——同一撮同步报价之间，若 `A -> B -> C -> A` 的净兑换率大于 `1`，就有套利闭环。

## 2. 核心结论
- **一句话核心结论**：这份 repo 真正值得 desk 收进研究池的，不是“图搜索很酷”，而是它把一条**可独立复现的相对价值 raw alpha**讲得非常干净：`cross-rate inconsistency -> immediate mean reversion / closure`。
- **一句话 first verdict**：我把 repo 的“last-price 找环”改成了更严格的 Binance Spot `bookTicker` 版，用 `bid/ask` 和每腿费用去重算；结果很明确——**裸 gross 确实经常有正值，但一上现实费用，公开顶档盘口下几乎全灭**。

### 2.1 live probe 读出来的 3 个关键数
我对 Binance Spot `USDT / USDC / FDUSD / BTC / ETH / BNB / SOL / XRP / DOGE / ADA / LINK` 做了约 `90` 秒、每秒一次的 top-of-book 扫描，只保留从 `USDT` 出发的三腿闭环：

1. **零费用 gross 版**：`90/90` 个样本都能找到正的闭环，median 约 **`+1.50 bps`**，最好约 **`+4.68 bps`**。
2. **每腿 4 bps**（接近很优 taker / 普通 maker-taker 混合的乐观口径）后：`0/90` 个样本为正，best 也只有 **`-7.32 bps`**。
3. **每腿 10 bps**（更接近普通 taker 口径）后：同样 `0/90` 个样本为正，median 约 **`-28.47 bps`**。

最常出现的最佳闭环是：
- `USDT -> ETH -> USDC -> USDT`

这说明什么？说明 **edge 本体是存在的**，而且公开数据一眼就能复现；但 **它首先是 execution / fee / queue-priority 问题，不是信号是否存在的问题**。

## 3. 为什么这题仍然值得进研究池
虽然公开 top-of-book + taker 口径下 first verdict 偏负，但这题仍值得保留，原因有三个：

### 3.1 它是很干净的 raw alpha，不是伪命题
很多“结构类”主题其实只有 filter 意义；但三角套利不是。它的 base alpha 可以直接写成：

`净环收益 = Π(逐腿可成交汇率) - 1`

只要 `净环收益 > 全部费用 + 执行缓冲`，就能做；做完就平，没有方向暴露。这个定义足够干净，能独立存在。

### 3.2 它天然适合 `1m / 3m / 5m` 甚至更快的最小实验
这类信号不是日频/小时级宏观条件，而是**秒级到分钟级**的闭环偏离。对我们 desk 来说，很适合拿来做：
- 高频 relative-value 基线监控
- “低费率/返佣/内部撮合条件下是否能活”的 execution feasibility study
- 作为 stablecoin / quote-fragmentation 结构健康度指标

### 3.3 它能反过来当别的 raw alpha 的 execution veto
即便最后不单独上线 tri-arb，本题也能沉淀出一个很值钱的组件：
- 当某个 quote asset（如 `USDC` / `FDUSD`）相对 `USDT` 出现短时错位时，很多同 underlier 的跨报价 spread、pair residual、stablecoin spread fade 都会被一起污染。
- 所以 tri-arb 偏离本身，也可以反过来做 **execution veto / stale-quote veto / quote-health regime**。

也就是说：这题既可以被当 raw alpha 主体，也可以降级复用成其它 relative-value 策略的风控层。

## 3.5 策略拆解（必填）
- 方向属性：market-neutral / closed-loop / immediate relative-value arbitrage
- 基础 alpha：`同所同步报价中的三腿 cross-rate inconsistency 会被迅速修复`
- regime：多报价资产、稳定币 quote 碎片化、高波动或局部流动性不均时更容易出现
- filter / veto：
  - 必须用 `bid/ask` 而不是 `last`
  - 必须扣手续费、滑点、撤单失败、部分成交风险
  - 必须过滤 stale quote / 深度不足 / 最小成交额不足
- risk / sizing / execution overlay：
  - entry：`expected_net_bps > fee + slippage_buffer + latency_buffer`
  - exit：三腿闭环天然 exit；若某腿未成交，立即走 hedge/unwind 分支
  - sizing：按三腿最浅一腿的顶档容量或前 `k` 档累计可成交量确定
  - risk：挂单等待超时、残腿库存暴露、quote 突变、费率层级变化

## 4. repo 里真正有价值的部分
`triangular_arbitrage/detector.py` 的关键价值不是“能找到 cycle”本身，而是它把问题抽象成了：

1. 每个交易对是一条可兑换边；
2. 反向兑换边用倒数价格表示；
3. 找乘积最大的闭环；
4. 乘积大于 `1` 就是候选机会。

这让它天然可迁移到：
- 只扫 `3` 条腿，而不是所有闭环；
- 用 `bid/ask` 替代 `close`；
- 把边权从“价格”改成“价格 × (1-fee) × fill_prob × depth_penalty”；
- 把“最优环”改成“最优可执行环”。

所以 repo 本身虽然只是探测器，但它提供了一个很干净的 alpha skeleton。

## 5. 可复刻的最小实验
### 5.1 最小研究假设
同一所 spot 报价中，若某三腿循环在真实 `bid/ask` 与手续费后仍存在稳定正净值，则可形成可交易的短周期 stat-arb pocket。

### 5.2 最小可复现实验口径
- 交易所：Binance Spot
- 数据：公开 `GET /api/v3/ticker/bookTicker`
- 频率：`1s` 轮询先做 feasibility；若要更严谨，再上 websocket best bid/ask
- 资产池：先做 `USDT / USDC / FDUSD / BTC / ETH / BNB / SOL`
- 闭环：只看 `3` 条腿，从 `USDT` 出发回到 `USDT`
- 价格：
  - `base -> quote` 用 `bid`
  - `quote -> base` 用 `1/ask`
- 净收益：
  - `gross = Π(rate_i)`
  - `net = gross × Π(1-fee_i) - 1`
- 容量：取三腿中最紧那一腿对应的可成交起始名义

### 5.3 这轮已完成的 public-data probe
本地已生成：
- `reports/artifacts/quant_digests/2026-04-18_triangular_arb_bookticker_probe.csv`
- `reports/artifacts/quant_digests/2026-04-18_triangular_arb_bookticker_summary.json`

结果摘要：
- `fee=0 bps/leg`：`positive_rate = 100%`，median `+1.50 bps`
- `fee=4 bps/leg`：`positive_rate = 0%`
- `fee=10 bps/leg`：`positive_rate = 0%`
- best cycle：`USDT>ETH>USDC>USDT`
- 正 gross 样本对应的顶档起始容量约在 **`9.5 ~ 37054 USDT`** 之间，但这只是顶档理论容量，不代表三腿都能无冲击完成

## 6. 对 short-cycle desk 的实际读法
### 6.1 不要把它理解成“普通账户直接 taker 三下就能赚”
公开盘口已经说明：**如果你只是普通 taker，edge 很大概率会被费用直接吃掉**。

### 6.2 真正更值钱的，是这三种 desk 级用法
1. **低费/返佣/做市权限账户**：重新评估是否能把 gross pocket 留住。  
2. **内部路由 / 多账户 / 自建撮合优先级研究**：验证 execution 是否比“公开顶档 + taker”更有优势。  
3. **作为 quote-health / stale-leg veto**：给 stablecoin spread、same-underlier multi-quote、跨 quote pair 策略做 admission filter。  

## 7. 风险与保留意见
- repo 原始实现用 `close/last`，会系统性高估机会；不能直接拿来下单。
- 三腿任何一腿失败，都会把 market-neutral 策略瞬间变成单腿库存风险。
- top-of-book 看上去有利润，不代表深度吃进去后仍有利润。
- 交易所内部撮合、延迟、费率等级、最小下单额、限价排队位置，都会决定这题是否能从“研究题”变成“生产题”。

## 8. 下一步怎么测
别再继续做 `last-price` 图搜索了，下一步应该是这 4 件事：

1. **把 `bookTicker` 升级成 websocket BBO 流**：看正净值机会的持续时间，而不是只看轮询快照。  
2. **把费用从常数改成真实账户费率场景**：普通 taker / VIP taker / maker-first / maker+taker 混合分开测。  
3. **把容量从顶档扩成前 `3~5` 档累计深度**：算真实可成交名义和冲击后净值。  
4. **只盯 `USDT/USDC/FDUSD + BTC/ETH/SOL` 的稳定币相关闭环**：因为这轮 live probe 里最佳环长期集中在 quote fragmentation 最强的位置。

如果这 4 步下来仍为负，就把 tri-arb 从“主策略候选”降级成：
- stablecoin quote stress monitor
- same-underlier multi-quote 策略的 veto / health metric

## 9. 数据源与公开性
- Repo：公开 GitHub 仓库，公开代码，可直接 clone
- 行情数据：Binance Spot `bookTicker` 公共 REST / websocket，公开可得
- 更新频率：近实时
- 最小可复现实验口径：用 BBO 数据重建三腿净环收益，扣费后统计 `positive_rate / best_bps / median_bps / capacity`

## 10. 来源
### Repo source
- Drakkar-Software. *Triangular-Arbitrage*. GitHub repository.
- Repo URL: `https://github.com/Drakkar-Software/Triangular-Arbitrage`
- Readable URL: `https://github.com/Drakkar-Software/Triangular-Arbitrage/blob/master/README.md`
- Key files:
  - `triangular_arbitrage/detector.py`
  - `tests/test_detector.py`

### Public market data
- Binance Spot bookTicker REST: `https://api.binance.com/api/v3/ticker/bookTicker`

### Local artifacts
- `reports/artifacts/quant_digests/2026-04-18_triangular_arb_bookticker_probe.csv`
- `reports/artifacts/quant_digests/2026-04-18_triangular_arb_bookticker_summary.json`

## 11. 最后一句话
这题的答案不是“有没有 alpha”——**有，而且公开数据很容易看到**；真正的问题是：**你的费用、延迟、排队权和执行兜底，够不够把这点 alpha 留在自己账上。**
