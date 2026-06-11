# 别把跨所价差只做常开扫描：这篇 FRL 2023 更该先测的是「高波动 × 链拥堵 pocket 下的 BTC 跨所 spread 收敛」完整 raw alpha
- 时间：2026-03-25 17:05 UTC
- 类型：2023 Finance Research Letters 论文 + 2025 GitHub 新仓库 + Binance / Coinbase 官方公开行情文档
- 主题类型：raw alpha
- 基础 alpha：同一资产在不同交易所的**可执行**买卖价差会向中枢收敛；高波动、低同步、链拥堵时更容易撑开到足够覆盖成本的 spread，可做成“maker 一腿 + taker 一腿”的跨所 relative-value 策略
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/cross-exchange/spread-reversion/maker-taker/volatility/network-congestion/coinbase/binance/bookticker/btc/1m/3m/5m/15m/repo/paper/execution
- 证据类型：FRL 论文摘要页 + 2025 开源执行仓库 README/参数 + 官方 websocket 行情文档

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是 filter，而是“同币种跨交易所可执行 spread 的短时收敛”这一条独立 raw alpha；高波动和链拥堵只是让它更容易出现、也更值得开机的 regime pocket。**

这次主看 Ladislav Kristoufek、Elie Bouri 发表于 *Finance Research Letters* 的 2023 论文 *Exploring sources of statistical arbitrage opportunities among Bitcoin exchanges*，再配一个 2025 年的开源仓库 `your-quantguy/cross-exchange-arbitrage`。一句话 desk 化结论：**别把 spatial arb 继续理解成“看见价差就无脑打”，真正值得先复现的是“只在高波动/低同步 pocket 做、并且用 maker-taker 结构把 fee 打薄”的 BTC 跨所 spread 收敛骨架。**

## 2. 核心结论
- **论文看的不是单一交易所，而是 5 个 BTC 交易所的相关性裂口。** 样本覆盖 `2017-10-20 ~ 2022-01-07`，交易所包括 `Binance / Bitfinex / Bitstamp / Coinbase / Kraken`。
- **统计套利机会更容易出现在“高波动 + 网络拥堵”时段。** 论文用 Grey correlation 度量 Binance 与另外四所的联动强度，核心发现是：**当 BTC 价格更波动、链更拥堵时，跨所同步性下降，套利机会更容易冒出来。**
- **成交越活跃、链上活动越强，反而越会压平机会。** 论文直接写到：**更高的交易所成交量与更强的 on-chain activity 会提高交易所间相关性，从而减少套利机会。**
- **作者自己就强调：这是 statistical arbitrage，不等于自动可赚。** 也就是说，真正能不能活下来，关键不只在 signal，而在费率、挂单成交率、库存预置、延迟预算。
- **2025 仓库把“怎么落地”讲得比论文更实。** `your-quantguy/cross-exchange-arbitrage` 的执行骨架是：
  - 在 `edgeX` 挂 `post-only` 限价单；
  - 在 `Lighter` 打市价单对冲；
  - 默认 `fill-timeout=5s`；
  - README 示例阈值给到 `long-threshold=10 / short-threshold=10`，以及更激进的 `1 / 20` BTC 配置示例；
  - 还有显式 `max-position` 风控。
- **所以这次最该偷的不是“有没有价差”，而是“什么时候价差值得打，以及怎么用 maker-taker 结构把它做成完整策略”。**

## 3. 为什么和当前项目有关
这条线和当前 desk 的关系很直接，因为它补的是 **raw alpha 素材池里的 cross-exchange / relative-value / stat-arb**，不是再写一个解释层：
- 它不是又一条“盘口/资金费确认”，而是**同一资产跨 venue 的独立价格收敛 alpha**。
- 它天然适合 `1m/3m/5m` 执行，`15m` 做 regime bucket：**短周期 quote 驱动，慢一点的 bar 只负责决定要不要开机、阈值开多大。**
- 它和已有的 `basis / perp premium / same-coin multiquote / pairs` 相关但不重合：这条线赌的是**venue 间同步修复**，不是期限结构、也不是跨币种协整。
- 它还能自然引入“库存预置 + maker 一腿 + taker 一腿 + 超时撤单”这类实盘组件，适合往 execution-ready 素材池里放。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / stat-arb / same-asset cross-venue mean reversion
- 基础 alpha：同一资产在 venue A 与 venue B 的**可执行** spread（`bid_A - ask_B` 或 `bid_B - ask_A`）偏离会在短时间内回补
- regime：优先交易 `15m` 高 realized vol、跨所短窗联动下降的 pocket；若能拿到外部数据，再把 BTC 链拥堵当额外 size-up 条件
- filter / veto：
  - 只做 top liquidity 资产（先从 BTC 开始）
  - 只在 `net spread > 双边手续费 + 预估滑点 + 安全 buffer` 时入场
  - 避开 funding 结算、系统维护、单所盘口明显失真、深度不足、quote 冻结
  - 若没有预置库存，不做需要链上转币才能闭环的版本
- risk / sizing / execution overlay：
  - maker 在更便宜的一侧挂单，taker 在更贵的一侧立刻对冲
  - 单腿 notional、净敞口、单所库存各自设上限
  - 未成交 `x` 秒强撤（repo 示例是 `5s`）
  - 价差压回阈值内、或达到超时、或净仓偏离过大则平仓/反向对冲

## 4. 可复刻的最小实验
### 4.1 最小研究假设
在 BTC 这种高流动性资产上，**跨所 top-of-book 可执行 spread 在高波动 pocket 更容易超过成本阈值，且在未来 `1m~15m` 内回补。**

### 4.2 公共可得数据
- **Binance USDⓈ-M Futures `bookTicker`**：实时推送 best bid/ask 与数量。
- **Coinbase Exchange websocket `ticker`**：提供 `best_bid / best_ask / size / time`。
- 这两类数据都是**公开可拿**，无需私有交易权限即可先做 signal 研究。

### 4.3 一个最小、诚实的实验口径
1. 选 `BTCUSDT perp (Binance)` 对 `BTC-USD spot (Coinbase)`，或直接改成两家 perp / 两家现货的更可比组合。  
2. 每 `1s~5s` 采样一次两边 best bid/ask，构造：  
   - `spread_longA = bid_B - ask_A - fees - slip_buffer`  
   - `spread_longB = bid_A - ask_B - fees - slip_buffer`  
3. 把事件流聚合到 `1m/3m/5m/15m`：每个 bucket 记录最大可执行净 spread、触发次数、触发后 `1/3/5/15` 分钟的回补幅度。  
4. `entry`：净 spread 超过阈值（先用固定 bps，再做 vol-scaled 阈值）。  
5. `exit`：
   - spread 回补到 entry 的 `25%~50%` 以内；或
   - 超过 `1m/3m/5m` 的 holding timeout；或
   - maker 腿迟迟不成交、taker 腿库存约束触发。  
6. `sizing`：先等额 notional；第二轮再改成按盘口深度、近 15m 波动、库存占用做 size throttle。  

### 4.4 最该先看什么
- `post-cost hit rate`
- `mean reversion half-life`
- `maker fill ratio`
- `timeout cancel ratio`
- `inventory drift`
- 高/低 `15m` realized vol 分层后的净收益差

## 5. 风险与保留意见
- **论文讲的是“机会何时出现”，不是直接给出可交易 PnL。** 所以从统计裂口到真钱 alpha，中间最大的坑还是 execution。
- **现货-现货、现货-perp、perp-perp 的可转移性不同。** 若标的、报价币、资金费和交易时段不一致，表面 spread 可能只是结构性基差，不会快速回补。
- **链拥堵是双刃剑。** 它能制造价差，但如果你的闭环依赖转币/充提，它也会直接把真实可赚性打掉；所以 desk 版默认应先做**库存预置**版本。
- **maker-taker 架构会暴露在单腿成交与 adverse selection 风险下。** 如果 maker 只在你“最不想成交”时成交，这条线会从 arb 变成裸方向。
- **这类 edge 很容易被 fee、rebate、VIP 等级改写。** 没有真实费率表和排队位置假设时，回测很容易过度乐观。

## 6. 来源
1. **Kristoufek, L., & Bouri, E. (2023). _Exploring sources of statistical arbitrage opportunities among Bitcoin exchanges_. Finance Research Letters, 51, 103332.**  
   - DOI: `https://doi.org/10.1016/j.frl.2022.103332`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1544612322005116`
2. **your-quantguy (2025). _cross-exchange-arbitrage_. GitHub repository.**  
   - Repo URL: `https://github.com/your-quantguy/cross-exchange-arbitrage`  
   - Readable README: `https://raw.githubusercontent.com/your-quantguy/cross-exchange-arbitrage/main/README.md`
3. **Binance Developers. _Individual Symbol Book Ticker Streams_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Individual-Symbol-Book-Ticker-Streams`
4. **Coinbase Exchange Docs. _WebSocket Channels_.**  
   - Readable URL: `https://docs.cdp.coinbase.com/exchange/websocket-feed/channels`

## 7. 下一步怎么测（必须）
1. **先做“纯公共 quote 版”回补统计**：别急着碰私有撮合，先验证 BTC 跨所净 spread 在 `1m/3m/5m/15m` 上到底有没有稳定的 post-cost 回补。  
2. **做 `spread × 15m realized vol` 双分层**：验证这条线是不是只在高波动 pocket 才值得开机，而不是全天候常开。  
3. **再加“短窗联动下降” gate**：用 rolling correlation / Grey-correlation proxy 看，只有当 venue 同步性暂时掉下去时，净边是否才明显抬升。  
4. **最后才接 maker fill 模型**：把 `fill-timeout`、maker 成交概率、撤单率、单所库存上限加进去，确认它是可执行 alpha，而不是纯看板价差。  
5. **若前四步成立，再补链拥堵数据**：把 mempool congestion 作为可选 size-up gate，验证它是增益项还是只是解释项。