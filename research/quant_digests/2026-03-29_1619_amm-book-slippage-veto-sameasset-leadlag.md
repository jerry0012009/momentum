# 别把这篇 2025 arXiv 继续写成“又一篇 CEX 领先 DEX”：更该先落地的是「AMM 可执行价重建 × slippage/gas veto」same-asset lead-lag 共享 filter

- 时间：2026-03-29 16:19 UTC
- 类型：filter
- 主题标签：filter/shared-gate/execution-veto/relative-value/same-asset/lead-lag/price-discovery/cex-dex/spot-futures/amm/order-book-reconstruction/slippage/gas/eth/btc/uniswap/binance/cme/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2025 arXiv 全文 HTML + 本地 PDF + 论文表格级结果抽取
- 主题类型：filter
- 基础 alpha：same-asset cross-venue lead-lag / basis convergence（尤其是 CEX→DEX catch-up、futures→spot catch-up、跨 venue 同标的价差回归）
- 是否可独立复现：是（公开 CEX 行情 + Uniswap pool 状态 / swap 数据 + gas 数据即可复现）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（更适合作为 same-asset relative-value 家族的 shared execution / admission filter）

## 1. 这次看了什么

这次主看的是：

> **Juan Plazuelo Pascual, Carlos Tardón Rubio, Juan Toro Cebada, Ángel Hernando Veciana (2025)**  
> **Price Discovery in Cryptocurrency Markets**  
> *arXiv preprint*  
> DOI：未见正式 DOI（当前为 arXiv 预印本）  
> arXiv：`2506.08718`  
> Readable URL：<https://arxiv.org/abs/2506.08718>  
> Full HTML：<https://arxiv.org/html/2506.08718v1>  
> Repo URL：未见官方复现仓库

如果只看 headline，这篇东西很容易被读成：

- ETH 上 **Binance 领先 Uniswap**
- BTC 上 **CME futures 多数时候领先 Binance spot**

这些结论本身没错，但对我们这个已经积累了不少 same-asset lead-lag / basis / cross-venue relative-value 素材的 desk 来说，**这已经不是最稀缺的那层**。

这篇 paper 真正更值钱的分支是：

> **它认真处理了“DEX 没有传统 order book，仍然要先重建可执行价和滑点曲线，才知道 lead-lag alpha 到底能不能下单”这件事。**

这正好补的是我们当前素材池里更缺的一层：

- 不是再补一个“谁领先谁”的 raw alpha headline；
- 而是给已经存在的 same-asset relative-value alpha，补一个**shared execution veto / admission filter**。

## 2. 先回答用户要求的那句：这篇东西的 base alpha 是什么？

这篇东西的 **base alpha** 其实不该硬说成它自己发明了新方向。

更诚实的说法是：

- 它服务的 **base alpha** 是：
  - **same-asset lead-lag catch-up**
  - **same-asset basis convergence**
  - **cross-venue price-dislocation rollback**
- 典型落点包括：
  - `Binance → Uniswap` 的 ETH 迟滞补动
  - `futures → spot` 的 BTC catch-up
  - 其他“同一标的，不同 venue / 机制”的 spread 回归

所以本轮分类应当是：

- **主题类型：filter**
- **不是 standalone raw alpha**
- **而是 raw alpha 的执行可交易性过滤层**

一句话说白：

> **这篇 paper 最有用的，不是告诉你“有价差”；而是告诉你，DEX / AMM 上你必须先把“实际成交到手的价格”算出来，否则 paper alpha 只是中间价幻觉。**

## 3. 为什么这轮不继续写一个 raw alpha，而是写这个 filter

这个问题得正面回答。

过去几天，desk 已经连续积累了不少 raw alpha：

- CEX/DEX same-asset catch-up
- futures-lead-spot spread alpha
- cross-venue funding carry
- same-asset perp-perp basis pocket
- pairs / stat-arb / basket MR

反而当前更缺的是：

> **一层能同时服务这些 same-asset / cross-venue raw alpha 的“执行真实性过滤器”。**

如果没有这层，最容易犯的错是：

1. 用 mid-price 看到有 edge；
2. 实际一吃单，AMM 曲线滑点 + fee + gas 把 edge 吃光；
3. 回测还以为自己抓到了 alpha，实盘却只是“买到了论文图上的虚假价差”。

所以这轮虽然不是 raw alpha 本体，但它不是泛泛解释文。

它更像：

> **给现有 same-asset relative-value alpha 家族补一块现在更缺的实盘层：先过 executable-price veto，再谈入场。**

## 4. 论文里最值得 desk 拿走的不是“谁领先”，而是三组硬结果

### 4.1 ETH：中心化市场几乎每次都领先 DEX，但关键是这个结论必须建立在“可比价格”上

论文在 `ETH Binance vs Uniswap` 的 5 个事件日总结（Table 3.19）里给出：

- **Hasbrouck Centralized Share**：
  - March：`0.959`
  - April：`0.965`
  - May：`0.628`
  - August：`0.986`
  - September：`0.995`
- **Hayashi-Yoshida Lead-Lag Ratio** 也都是中心化市场领先：
  - March：`1.86`
  - April：`1.47`
  - May：`1.22`
  - August：`1.20`
  - September：`1.11`

而论文自己的总结是：

> centralized market consistently leads the decentralized one on every occasion.

但 desk 真该注意的不是“中心化领先”这句废话，而是：

> **作者为了得到这个结论，先把 Uniswap 的 liquidity pool 重建成一个可比较的 order-book / executable-price 结构。**

这一步对我们比“share=0.959”更重要，因为它决定了信号有没有成交意义。

### 4.2 BTC：futures 多数时候领先，但优势已经没想象中大，而且高波动会翻车

在 `BTC spot vs CME futures` 的 5 个事件日总结（Table 3.35）里：

- **Hasbrouck Futures Share**：
  - March：`0.563`
  - April：`0.552`
  - May：`0.521`
  - August：`0.158`
  - September：`0.539`
- **Hayashi-Yoshida lag（秒）**：
  - March：`0.055s`
  - April：`0.066s`
  - May：`0.063s`
  - August：`-0.571s`（spot 反而领先）
  - September：`0.15s`

论文总结得很清楚：

- futures **多数时候领先**；
- 但 **优势不大**；
- 高波动时会出现 **mixed results**；
- 市场效率比 4~5 年前更高，价差没以前肥。

对我们来说，这个结论其实是反向提醒：

> **别把“谁领先”直接抄成 1m/3m 可收钱 alpha。**

因为当 paper 里都只剩 `0.055s ~ 0.15s` 这种量级时，真正能迁移到 `1m/3m/5m` 的，不再是“秒级抢跑”本身，而是：

- 哪些情况下 lag 会扩到足以覆盖成本；
- 哪些情况下其实根本不该下单；
- 哪些 venue / pool / 时段的 executable edge 仍然没被成本吃掉。

### 4.3 论文把“交易性”问题写得很实：套利分析必须显式扣 gas / liquidity constraints

论文在执行层面反复强调：

- stressed liquidity conditions 下，**gas prices** 和 **liquidity constraints** 很重要；
- arbitrage opportunity estimation 不能只看 mispricing；
- 必须把 **transaction costs in the form of gas fees** 算进去；
- DEX 侧需要先构造 **liquidity snapshot**，再更新成 `t+1` 的可执行流动性状态。

这意味着 paper 给我们的不是一句“有价差就冲”，而是更接近下面这条实盘原则：

> **same-asset relative-value alpha 的 admission，必须基于 executable mispricing，而不是 observed mid mispricing。**

## 5. 这篇 paper 更适合 desk 的落地读法：把它做成 shared execution veto

### 5.1 它服务哪类 raw alpha

最直接服务这几类：

1. **CEX→DEX catch-up**
2. **futures→spot / spot→perp 的 same-asset spread 回归**
3. **cross-venue 同标的 basis pocket**
4. **带 AMM / 薄流动性 venue 腿的 relative-value / stat-arb**

它不负责决定方向；它负责决定：

- **这笔单能不能做**
- **做多大**
- **该用哪条腿做主动 / 被动执行**
- **预期 alpha 能不能扛得过滑点 + gas + fee**

### 5.2 最核心的 gate 变量不是 spread，而是“可执行 spread”

第一版最值得测的变量，不是：

- `mid_CEX - mid_DEX`

而是：

- `executable_spread = leader_ref_price - lagging_leg_executable_price_after_fee_gas`

其中 `lagging_leg_executable_price_after_fee_gas` 需要显式包含：

- AMM 曲线滑点
- LP / trading fee
- gas
- 估算失败 / confirmation buffer
- 可能的回补腿成本

只有当：

`expected_catchup > total_cost + safety_buffer`

这条 raw alpha 才允许入场。

### 5.3 这层 filter 不只服务 DEX

虽然 paper 一大亮点是 Uniswap order-book reconstruction，但它的思路不该只锁死在 DEX。

更广义地说，这是一条：

> **对任何“报价可见、但实际成交曲线并不线性”的 venue，都该先做 executable-price reconstruction。**

所以它其实也可以服务：

- 薄深度 perp venue
- 多 stablecoin quote 的同币多报价 MR
- 跨 venue maker pocket / rollback execution
- options 同 strike / 同 expiry 的相对价值

## 6. desk 最小可复现实验

### 6.1 数据源、公开性、更新频率

**主实验对象**：

- `ETH`：Binance vs Uniswap（优先 v3，若工程图省事先做 v2/v3 简化版）
- `BTC`：Binance spot / perp vs CME proxy 或先用 Binance spot-perp 替代做结构验证

**公开数据源**：

- CEX：Binance 公共 trade / kline / bookTicker / aggTrades
- DEX：Uniswap pool swap / mint / burn / slot0 / liquidity / tick state
- gas：Ethereum 公共 gas API / Etherscan gas tracker / on-chain block data
- 可选代理：GeckoTerminal / Dune 导出的 pool OHLCV + liquidity

**更新频率**：

- 底层最好 `1s~1m`
- 最小实验汇总到 `1m / 3m / 5m`
- 若只想快速出 first verdict，先做 `1m entry + 3m/5m exit`

### 6.2 最小实验定义

先别做复杂 VECM / 信息份额在线估计，第一版直接做可交易版本：

1. **leader impulse 定义**
   - 在 CEX 上定义 `1m` 冲击：
   - `abs(ret_1m) > rolling q90` 或 `> k * sigma_1m`
2. **lagging leg 可执行价重建**
   - 对 DEX / 薄深度腿，按给定 notional 计算：
   - `buy_exec_px(size)` / `sell_exec_px(size)`
   - 再扣 fee + gas
3. **可执行 edge**
   - `edge_exec = expected_reversion_target - current_exec_cost`
4. **filter**
   - 只在 `edge_exec > buffer` 时允许开仓
   - `buffer` 可取 `1.2x ~ 1.5x` 估算总成本
5. **exit**
   - `1m / 3m / 5m` 固定持有
   - 或当 spread 回到 rolling fair band 内即平

### 6.3 第一版就该做的对照

一定要做这两个版本的 A/B：

- **A：naive mid-price alpha**
- **B：executable-price veto alpha**

核心看三件事：

1. trade count 会不会大幅下降；
2. 成本后 pnl / hit-rate / avg trade 有没有明显改善；
3. 大亏损尾部是否明显收缩。

如果 B 版本只是把交易全砍掉，那这层 gate 没价值；
如果 B 版本能：

- 少做很多单，
- 但净值更平，
- 尾部更短，
- 每笔更厚，

那它就配进 shared execution layer。

## 7. 一个最适合当前 desk 的具体实现草图

### 7.1 先服务 `Binance impulse → Uniswap catch-up`

这是最直接的 paper 对应场景。

**entry**：

- Binance `1m` 冲击超过阈值；
- Uniswap 池的同方向 `executable move` 仍明显落后；
- `net_edge_after_fee_gas > threshold`

**exit**：

- 3m / 5m 固定离场；或
- 当 `cex-dex executable spread` 回归到 `rolling z < z_close`

**sizing**：

- 按 pool depth / gas percentile 动态降杠杆；
- gas > rolling p80 直接 veto；
- pool depth < size floor 直接 veto

**risk / cost**：

- 只允许在 pool 价格 impact < `x bp` 时入场；
- gas 费用统一乘一个保守 buffer；
- 极端波动时扩大 cost haircut

### 7.2 再扩展到 `same-asset perp / spot / cross-venue`

第二阶段可以不碰链上，只把同样的思想搬去：

- 薄深度 venue 的 book-walk cost
- maker pocket 是否存在
- 一腿主动、一腿被动时的 net executable spread

也就是说：

> **这篇 paper 的最有用迁移，不是它那几个 share 数字，而是“别再拿中间价假装自己能成交”的执行哲学。**

## 8. 这轮最值得记住的 3 个关键数据点

1. **ETH：中心化市场在 5 个事件里 Hasbrouck share 分别为 `0.959 / 0.965 / 0.628 / 0.986 / 0.995`**，说明 CEX→DEX price discovery 优势非常稳定。  
2. **BTC：futures share 只有 `0.563 / 0.552 / 0.521 / 0.158 / 0.539`**，而且 August 甚至 spot 领先，说明“futures 一定碾压 spot”的旧叙事已经弱化。  
3. **论文明写了 gas / liquidity constraints / liquidity snapshot reconstruction**，这说明 real tradability 的关键不是观察到 spread，而是算出 **executable spread after cost**。

## 9. 下一步怎么测

### 最小下一步（本周内能做）

做一个 **ETH Binance ↔ Uniswap 1m executable-spread veto** 小实验：

1. 拉最近 `60~90` 天 Binance `ETHUSDT` `1m` / `aggTrades`
2. 取 1 个主流 Uniswap ETH 池，重建简化版 executable price（先不追求 tick-level 完美）
3. 用 `Binance 1m impulse` 触发候选信号
4. 比较：
   - **naive mid-gap catch-up**
   - **executable-gap > fee+gas+buffer 才入场**
5. 输出：
   - trade count
   - avg edge
   - gross/net pnl
   - p95 loss
   - 不同 gas 分位下的表现

### 如果第一版有边，再做第二步

把这层 gate 接到至少两类 alpha 上做 shared test：

- `CEX→DEX catch-up`
- `same-asset cross-venue basis pocket`

如果它能同时改善两类策略，而不是只对某一个 setup 有用，它就值得正式升级成 desk 的 shared execution filter。

## 10. 来源与可复现性清单

### 论文来源

- arXiv 摘要页：<https://arxiv.org/abs/2506.08718>
- arXiv 全文 HTML：<https://arxiv.org/html/2506.08718v1>
- 本地 PDF：`/root/clawd/jerry/momentum/tmp_price_discovery_2025.pdf`

### 公开数据口径

- Binance 公共市场数据（trade / aggTrades / kline / bookTicker）
- Uniswap pool 状态 / swap / liquidity / tick 数据（公开链上可得）
- Ethereum gas 数据（公开 API / 链上）

### 复现口径

- 频率：`1m / 3m / 5m` 为主，必要时底层 `1s`
- 标的：`ETH` 优先，`BTC` 作对照
- 角色：shared filter / execution veto
- 服务对象：same-asset relative-value / lead-lag / basis convergence

## 11. 一句话结论

> **这篇 2025 arXiv 对我们最值钱的，不是再证明一次“CEX 领先 DEX”，而是提醒：凡是 same-asset lead-lag / basis alpha，只要有 AMM 或薄深度腿，就必须先把 executable price、slippage、fee、gas 算清楚，再决定这笔单是不是值得做。**
